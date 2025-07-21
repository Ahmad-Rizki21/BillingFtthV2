from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import date
from typing import List, Optional
from ..models.langganan import Langganan as LanggananModel
from ..schemas.langganan import Langganan as LanggananSchema, LanggananCreate, LanggananUpdate
from ..database import get_db

router = APIRouter(prefix="/langganan", tags=["Langganan"])

@router.post("/", response_model=LanggananSchema, status_code=status.HTTP_201_CREATED)
async def create_langganan(langganan: LanggananCreate, db: AsyncSession = Depends(get_db)):
    db_langganan = LanggananModel(**langganan.model_dump())
    db.add(db_langganan)
    await db.commit()
    await db.refresh(db_langganan)
    return db_langganan

# @router.get("/", response_model=List[LanggananSchema])
# async def get_all_langganan(db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(LanggananModel))
#     return result.scalars().all()

#Penyempurnaan
@router.get("/", response_model=List[LanggananSchema])
async def get_all_langganan(
    status: Optional[str] = None, 
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(LanggananModel)
        # 1. Tambahkan selectinload untuk mengambil detail paket
        .options(selectinload(LanggananModel.paket_layanan))
    )
    
    # 2. Tambahkan filter WHERE jika parameter status diberikan
    if status:
        query = query.where(LanggananModel.status == status)
        
    # Terapkan paginasi
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{langganan_id}", response_model=LanggananSchema)
async def get_langganan_by_id(langganan_id: int, db: AsyncSession = Depends(get_db)):
    langganan = await db.get(LanggananModel, langganan_id)
    if not langganan:
        raise HTTPException(status_code=404, detail="Langganan tidak ditemukan")
    return langganan

@router.patch("/{langganan_id}", response_model=LanggananSchema)
async def update_langganan(langganan_id: int, langganan_update: LanggananUpdate, db: AsyncSession = Depends(get_db)):
    db_langganan = await db.get(LanggananModel, langganan_id)
    if not db_langganan:
        raise HTTPException(status_code=404, detail="Langganan tidak ditemukan")

    update_data = langganan_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_langganan, key, value)
        
    db.add(db_langganan)
    await db.commit()
    await db.refresh(db_langganan)
    return db_langganan

@router.delete("/{langganan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_langganan(langganan_id: int, db: AsyncSession = Depends(get_db)):
    db_langganan = await db.get(LanggananModel, langganan_id)
    if not db_langganan:
        raise HTTPException(status_code=404, detail="Langganan tidak ditemukan")
        
    await db.delete(db_langganan)
    await db.commit()
    return None
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

# Impor model dan skema secara langsung dari filenya, bukan melalui paket
from ..models.pelanggan import Pelanggan as PelangganModel
from ..schemas.pelanggan import Pelanggan as PelangganSchema, PelangganCreate, PelangganUpdate
from ..database import get_db

router = APIRouter(
    prefix="/pelanggan",
    tags=["Pelanggan"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=PelangganSchema, status_code=status.HTTP_201_CREATED)
async def create_pelanggan(
    pelanggan: PelangganCreate, db: AsyncSession = Depends(get_db)
):
    """
    Membuat data pelanggan baru.
    """
    db_pelanggan = PelangganModel(**pelanggan.model_dump())
    db.add(db_pelanggan)
    await db.commit()
    await db.refresh(db_pelanggan)
    return db_pelanggan


@router.get("/", response_model=List[PelangganSchema])
async def read_all_pelanggan(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """
    Mengambil daftar semua pelanggan dengan paginasi.
    """
    query = select(PelangganModel).offset(skip).limit(limit).options(selectinload(PelangganModel.data_teknis))
    result = await db.execute(query)
    pelanggan_list = result.scalars().all()
    return pelanggan_list


@router.get("/{pelanggan_id}", response_model=PelangganSchema)
async def read_pelanggan_by_id(pelanggan_id: int, db: AsyncSession = Depends(get_db)):
    """
    Mengambil satu data pelanggan berdasarkan ID.
    """
    query = select(PelangganModel).where(PelangganModel.id == pelanggan_id).options(selectinload(PelangganModel.data_teknis))
    result = await db.execute(query)
    db_pelanggan = result.scalar_one_or_none()

    if db_pelanggan is None:
        raise HTTPException(status_code=404, detail="Pelanggan not found")
    return db_pelanggan


@router.patch("/{pelanggan_id}", response_model=PelangganSchema)
async def update_pelanggan(
    pelanggan_id: int,
    pelanggan_update: PelangganUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Memperbarui data pelanggan secara parsial (hanya field yang diisi).
    """
    db_pelanggan = await db.get(PelangganModel, pelanggan_id)
    if not db_pelanggan:
        raise HTTPException(status_code=404, detail="Pelanggan not found")

    update_data = pelanggan_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_pelanggan, key, value)

    db.add(db_pelanggan)
    await db.commit()
    await db.refresh(db_pelanggan)
    return db_pelanggan


@router.delete("/{pelanggan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pelanggan(pelanggan_id: int, db: AsyncSession = Depends(get_db)):
    """
    Menghapus data pelanggan berdasarkan ID.
    """
    db_pelanggan = await db.get(PelangganModel, pelanggan_id)
    if not db_pelanggan:
        raise HTTPException(status_code=404, detail="Pelanggan not found")

    await db.delete(db_pelanggan)
    await db.commit()
    return None

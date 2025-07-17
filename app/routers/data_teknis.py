from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

# Impor model dan skema secara langsung dari filenya
from ..models.data_teknis import DataTeknis as DataTeknisModel
from ..models.pelanggan import Pelanggan as PelangganModel
from ..schemas.data_teknis import DataTeknis as DataTeknisSchema, DataTeknisCreate, DataTeknisUpdate
from ..database import get_db

router = APIRouter(
    prefix="/data_teknis",
    tags=["Data Teknis"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=DataTeknisSchema, status_code=status.HTTP_201_CREATED)
async def create_data_teknis(
    data_teknis: DataTeknisCreate, db: AsyncSession = Depends(get_db)
):
    """
    Membuat data teknis baru untuk seorang pelanggan.
    """
    # Validasi: Pastikan pelanggan dengan ID yang diberikan ada
    pelanggan = await db.get(PelangganModel, data_teknis.pelanggan_id)
    if not pelanggan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pelanggan dengan id {data_teknis.pelanggan_id} tidak ditemukan.",
        )

    # Cek apakah pelanggan ini sudah punya data teknis
    existing_data_teknis_query = await db.execute(
        select(DataTeknisModel).where(DataTeknisModel.pelanggan_id == data_teknis.pelanggan_id)
    )
    if existing_data_teknis_query.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Data teknis untuk pelanggan dengan id {data_teknis.pelanggan_id} sudah ada.",
        )

    db_data_teknis = DataTeknisModel(**data_teknis.model_dump())
    db.add(db_data_teknis)
    await db.commit()
    await db.refresh(db_data_teknis)
    return db_data_teknis


@router.get("/", response_model=List[DataTeknisSchema])
async def read_all_data_teknis(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """
    Mengambil daftar semua data teknis dengan paginasi.
    """
    query = select(DataTeknisModel).offset(skip).limit(limit)
    result = await db.execute(query)
    data_teknis_list = result.scalars().all()
    return data_teknis_list


@router.get("/{data_teknis_id}", response_model=DataTeknisSchema)
async def read_data_teknis_by_id(data_teknis_id: int, db: AsyncSession = Depends(get_db)):
    """
    Mengambil satu data teknis berdasarkan ID.
    """
    db_data_teknis = await db.get(DataTeknisModel, data_teknis_id)
    if db_data_teknis is None:
        raise HTTPException(status_code=404, detail="Data Teknis not found")
    return db_data_teknis


@router.patch("/{data_teknis_id}", response_model=DataTeknisSchema)
async def update_data_teknis(
    data_teknis_id: int,
    data_teknis_update: DataTeknisUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Memperbarui data teknis secara parsial.
    """
    db_data_teknis = await db.get(DataTeknisModel, data_teknis_id)
    if not db_data_teknis:
        raise HTTPException(status_code=404, detail="Data Teknis not found")

    update_data = data_teknis_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_data_teknis, key, value)

    db.add(db_data_teknis)
    await db.commit()
    await db.refresh(db_data_teknis)
    return db_data_teknis


@router.delete("/{data_teknis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_data_teknis(data_teknis_id: int, db: AsyncSession = Depends(get_db)):
    """
    Menghapus data teknis berdasarkan ID.
    """
    db_data_teknis = await db.get(DataTeknisModel, data_teknis_id)
    if not db_data_teknis:
        raise HTTPException(status_code=404, detail="Data Teknis not found")

    await db.delete(db_data_teknis)
    await db.commit()
    return None

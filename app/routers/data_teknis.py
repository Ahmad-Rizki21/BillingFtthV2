from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import select, func 
from typing import List
import polars as pl
import logging
from io import BytesIO
from fastapi.responses import StreamingResponse

# --- PASTIKAN SEMUA IMPORT INI ADA DAN BENAR ---

# Impor model Pelanggan dengan nama asli 'Pelanggan', lalu kita beri alias 'PelangganModel'
from ..models.pelanggan import Pelanggan as PelangganModel 
from ..database import AsyncSessionLocal 

# Impor model DataTeknis
from ..models.data_teknis import DataTeknis as DataTeknisModel

# Impor semua skema yang dibutuhkan
from ..schemas.data_teknis import DataTeknis as DataTeknisSchema, DataTeknisCreate, DataTeknisUpdate, DataTeknisImport

# Impor database session
from ..database import get_db

router = APIRouter(
    prefix="/data_teknis",
    tags=["Data Teknis"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)

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


# routers/data_teknis.py

@router.get("/export/excel", response_class=StreamingResponse)
async def export_teknis_to_excel(db: AsyncSession = Depends(get_db)):
    """Mengekspor semua data teknis sebagai file Excel menggunakan Polars."""
    query = select(DataTeknisModel)
    result = await db.execute(query)
    data_list = result.scalars().all()

    if not data_list:
        raise HTTPException(status_code=404, detail="Tidak ada data teknis untuk diekspor.")

    # Persiapan data tetap sama
    data_for_df = [
        {
            "pelanggan_id": d.pelanggan_id,
            "id_vlan": d.id_vlan,
            "id_pelanggan": d.id_pelanggan,
            "password_pppoe": d.password_pppoe,
            "ip_pelanggan": d.ip_pelanggan,
            "profile_pppoe": d.profile_pppoe,
            "olt": d.olt,
            "olt_custom": d.olt_custom,
            "pon": d.pon,
            "otb": d.otb,
            "odc": d.odc,
            "odp": d.odp,
            "onu_power": d.onu_power,
            "mikrotik_server_id": d.mikrotik_server_id
        }
        for d in data_list
    ]
    
    # --- PERUBAHAN DARI PANDAS KE POLARS ---
    # Membuat DataFrame menggunakan Polars
    df = pl.DataFrame(data_for_df)
    
    output = BytesIO()
    # Menulis ke buffer menggunakan metode Polars
    df.write_excel(output, worksheet='Data Teknis')
    output.seek(0)
    # ----------------------------------------

    headers = {'Content-Disposition': 'attachment; filename="data_teknis.xlsx"'}
    return StreamingResponse(output, headers=headers, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# routers/data_teknis.py

@router.get("/import/template", response_class=StreamingResponse)
async def download_import_template():
    """Menyediakan file template Excel kosong menggunakan Polars."""
    headers = [
        "email_pelanggan",
        "id_vlan", "id_pelanggan", "password_pppoe", "ip_pelanggan", "profile_pppoe", "olt",
        "olt_custom", "pon", "otb", "odc", "odp", "onu_power", "mikrotik_server_id"
    ]
    
    # --- PERUBAHAN DARI PANDAS KE POLARS ---
    # Membuat DataFrame kosong dengan skema kolom yang ditentukan
    df = pl.DataFrame(schema=headers)

    output = BytesIO()
    # Menulis ke buffer menggunakan metode Polars
    df.write_excel(output, worksheet='Template Import Teknis')
    output.seek(0)
    # ----------------------------------------

    response_headers = {'Content-Disposition': 'attachment; filename="template_import_teknis.xlsx"'}
    return StreamingResponse(output, headers=response_headers, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@router.post("/import/excel")
async def import_teknis_from_excel(file: UploadFile = File(...)):
    """
    Mengimpor data teknis menggunakan Polars.
    """
    filename = file.filename.lower()
    
    # --- TAHAP 1: BACA FILE MENGGUNAKAN POLARS ---
    try:
        # Baca konten file ke dalam bytes agar bisa diproses Polars
        file_content = file.file.read()

        if filename.endswith('.xlsx'):
            # Polars membaca file Excel dari bytes, dan kita minta agar tidak menebak tipe data
            df = pl.read_excel(file_content, read_options={"infer_schema_length": 0})
        elif filename.endswith('.csv'):
            # Polars membaca file CSV, null_values='' akan mengubah sel kosong menjadi null
            df = pl.read_csv(file_content, infer_schema_length=0, null_values="")
        else:
            raise HTTPException(status_code=400, detail="Format file tidak valid. Harap unggah file .xlsx atau .csv")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gagal membaca file dengan Polars: {e}")

    errors = []
    data_to_create = []
    processed_pelanggan_ids = set()

    # Sesi DB sementara untuk validasi
    async with AsyncSessionLocal() as db:
        # --- TAHAP 2: ITERASI MENGGUNAKAN to_dicts() ---
        # Polars mengubah seluruh data menjadi list of dictionary, lebih efisien
        for row_dict in df.to_dicts():
            try:
                # Bersihkan spasi dari setiap value
                cleaned_row = {k: v.strip() if isinstance(v, str) else v for k, v in row_dict.items()}
                
                # Sisa logika validasi sama persis seperti sebelumnya
                data_import = DataTeknisImport(**cleaned_row)

                pelanggan = await db.execute(select(PelangganModel).where(func.lower(func.trim(PelangganModel.email)) == data_import.email_pelanggan.lower()))
                pelanggan = pelanggan.scalar_one_or_none()

                if not pelanggan:
                    errors.append(f"Baris data: {cleaned_row} -> Pelanggan '{data_import.email_pelanggan}' tidak ditemukan.")
                    continue

                if pelanggan.id in processed_pelanggan_ids:
                    errors.append(f"Baris data: {cleaned_row} -> Pelanggan '{pelanggan.nama}' muncul lebih dari sekali di file.")
                    continue

                existing_teknis = await db.execute(select(DataTeknisModel).where(DataTeknisModel.pelanggan_id == pelanggan.id))
                if existing_teknis.scalar_one_or_none():
                    errors.append(f"Baris data: {cleaned_row} -> Pelanggan '{pelanggan.nama}' sudah punya data teknis.")
                    continue
                
                teknis_data_dict = data_import.model_dump()
                teknis_data_dict['pelanggan_id'] = pelanggan.id
                del teknis_data_dict['email_pelanggan']
                data_to_create.append(teknis_data_dict)
                processed_pelanggan_ids.add(pelanggan.id)

            except Exception as e:
                errors.append(f"Baris data: {row_dict} -> Error: {e}")

    # ... (sisa kode untuk menyimpan ke database sama persis seperti sebelumnya) ...
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Ditemukan error, tidak ada data diimpor.", "errors": errors}
        )
    
    if not data_to_create:
        raise HTTPException(status_code=400, detail="Tidak ada data valid untuk diimpor.")

    async with AsyncSessionLocal() as db:
        async with db.begin():
            for data in data_to_create:
                db.add(DataTeknisModel(**data))
    
    return {"status": "Sukses", "message": f"Berhasil mengimpor {len(data_to_create)} data teknis baru."}

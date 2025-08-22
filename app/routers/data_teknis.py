from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import select, func, or_
from typing import List
import csv
import io
from datetime import datetime
import chardet
from pydantic import ValidationError
from sqlalchemy.orm import selectinload
import logging
from io import BytesIO
from fastapi.responses import StreamingResponse

from typing import Optional

# --- PASTIKAN SEMUA IMPORT INI ADA DAN BENAR ---

# Impor model Pelanggan dengan nama asli 'Pelanggan', lalu kita beri alias 'PelangganModel'
from ..models.pelanggan import Pelanggan as PelangganModel 
from ..database import AsyncSessionLocal
from ..models.mikrotik_server import MikrotikServer as MikrotikServerModel
from ..models.paket_layanan import PaketLayanan as PaketLayananModel

from ..services import mikrotik_service

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

    try:
        # Panggil fungsi trigger setelah data berhasil disimpan
        await mikrotik_service.trigger_mikrotik_create(db, db_data_teknis)
    except Exception as e:
        # Jika gagal membuat secret, jangan batalkan proses.
        # Cukup catat errornya. Data teknis tetap berhasil dibuat.
        logger.error(f"Data teknis ID {db_data_teknis.id} berhasil disimpan, "
                     f"namun gagal membuat secret di Mikrotik: {e}")

    return db_data_teknis


@router.get("/", response_model=List[DataTeknisSchema])
async def read_all_data_teknis(
    skip: int = 0, 
    limit: Optional[int] = None, # <-- 1. Diubah menjadi Optional[int] = None
    search: Optional[str] = None,
    olt: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Mengambil daftar semua data teknis dengan paginasi dan filter.
    """
    query = (
        select(DataTeknisModel)
        .join(DataTeknisModel.pelanggan)
        .options(selectinload(DataTeknisModel.pelanggan))
    )

    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                PelangganModel.nama.ilike(search_term),
                DataTeknisModel.id_pelanggan.ilike(search_term),
                DataTeknisModel.ip_pelanggan.ilike(search_term),
                DataTeknisModel.sn.ilike(search_term)
            )
        )

    if olt:
        query = query.where(DataTeknisModel.olt == olt)

    # <-- 2. Limit hanya diterapkan jika nilainya bukan None
    if limit is not None:
        query = query.offset(skip).limit(limit)

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

# ==========================================================
# FUNGSI DOWNLOAD DAN IMPORT, EXPORT CSV FILE
# ==========================================================

@router.get("/template/csv", response_class=StreamingResponse)
async def download_csv_template_teknis():
    """
    Men-download template CSV untuk import data teknis, lengkap dengan contoh.
    """
    output = io.StringIO()
    output.write('\ufeff') # BOM untuk kompatibilitas dengan Excel

    # Header disesuaikan untuk data teknis, dengan email sebagai kunci
    headers = [
        "email_pelanggan", "id_vlan", "id_pelanggan", "password_pppoe", "ip_pelanggan",
        "profile_pppoe", "olt", "olt_custom", "pon", "otb", "odc", "odp",
        "onu_power", "mikrotik_server_id"
    ]

    # Data contoh untuk mempermudah pengisian
    sample_data = [
        {
            "email_pelanggan": "budi.s@example.com", "id_vlan": "101", "id_pelanggan": "budi-santoso",
            "password_pppoe": "pass123", "ip_pelanggan": "10.10.1.25", "profile_pppoe": "50mbps-profile",
            "olt": "OLT-Utama-1", "olt_custom": "", "pon": 1, "otb": 1, "odc": 3, "odp": 5,
            "onu_power": -22, "mikrotik_server_id": 1
        }
    ]

    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    writer.writerows(sample_data)

    output.seek(0)
    
    response_headers = {'Content-Disposition': 'attachment; filename="template_import_teknis.csv"'}
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')), 
        headers=response_headers, 
        media_type='text/csv; charset=utf-8'
    )

@router.get("/export/csv", response_class=StreamingResponse)
async def export_to_csv_teknis(db: AsyncSession = Depends(get_db)):
    """
    Mengekspor semua data teknis ke dalam file CSV.
    """
    query = select(DataTeknisModel).options(selectinload(DataTeknisModel.pelanggan))
    result = await db.execute(query)
    data_list = result.scalars().unique().all()

    if not data_list:
        raise HTTPException(status_code=404, detail="Tidak ada data teknis untuk diekspor.")

    output = io.StringIO()
    output.write('\ufeff')

    # Siapkan data untuk ditulis ke CSV
    rows_to_write = []
    for d in data_list:
        rows_to_write.append({
            "Nama Pelanggan": d.pelanggan.nama if d.pelanggan else "N/A",
            "Email Pelanggan": d.pelanggan.email if d.pelanggan else "N/A",
            "ID Pelanggan (PPPoE)": d.id_pelanggan, "Password PPPoE": d.password_pppoe,
            "IP Pelanggan": d.ip_pelanggan, "Profile PPPoE": d.profile_pppoe, "VLAN": d.id_vlan,
            "OLT": d.olt, "OLT Custom": d.olt_custom, "PON": d.pon, "OTB": d.otb,
            "ODC": d.odc, "ODP": d.odp, "ONU Power (dBm)": d.onu_power,
            "ID Server Mikrotik": d.mikrotik_server_id
        })
    
    # Tulis ke CSV menggunakan DictWriter
    writer = csv.DictWriter(output, fieldnames=rows_to_write[0].keys())
    writer.writeheader()
    writer.writerows(rows_to_write)

    output.seek(0)
    
    filename = f"export_data_teknis_{datetime.now().strftime('%Y%m%d')}.csv"
    response_headers = {'Content-Disposition': f'attachment; filename="{filename}"'}
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')), 
        headers=response_headers, 
        media_type='text/csv; charset=utf-8'
    )

# Mengubah nama fungsi dan path dari /import/excel menjadi /import/csv
@router.post("/import/csv")
async def import_from_csv_teknis(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """
    Mengimpor data teknis dari file CSV dengan validasi mendalam.
    """
    if not file.filename or not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="File harus berformat .csv")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="File kosong.")

    try:
        encoding = chardet.detect(contents)['encoding'] or 'utf-8'
        content_str = contents.decode(encoding)
    except Exception:
        raise HTTPException(status_code=400, detail="Tidak dapat membaca file. Pastikan encoding adalah UTF-8.")

    reader = csv.DictReader(io.StringIO(content_str))
    
    errors = []
    data_to_create = []
    processed_emails = set()

    for row_num, row in enumerate(reader, start=2):
        try:
            # Validasi Pydantic menggunakan skema DataTeknisImport
            data_import = DataTeknisImport(**row)
            email = data_import.email_pelanggan.lower().strip()

            if not email:
                errors.append(f"Baris {row_num}: Kolom 'email_pelanggan' wajib diisi.")
                continue

            # Cek duplikat di dalam file
            if email in processed_emails:
                errors.append(f"Baris {row_num}: Email '{email}' muncul lebih dari sekali di file.")
                continue

            # Cari pelanggan berdasarkan email
            pelanggan_result = await db.execute(select(PelangganModel).where(func.lower(PelangganModel.email) == email))
            pelanggan = pelanggan_result.scalar_one_or_none()
            if not pelanggan:
                errors.append(f"Baris {row_num}: Pelanggan dengan email '{email}' tidak ditemukan.")
                continue

            # Cek apakah pelanggan sudah punya data teknis
            existing_teknis_result = await db.execute(select(DataTeknisModel).where(DataTeknisModel.pelanggan_id == pelanggan.id))
            if existing_teknis_result.scalar_one_or_none():
                errors.append(f"Baris {row_num}: Pelanggan '{pelanggan.nama}' sudah memiliki data teknis.")
                continue
            
            # Validasi mikrotik_server_id
            mikrotik_server_id = data_import.mikrotik_server_id
            mikrotik_server_result = await db.execute(select(MikrotikServerModel).where(MikrotikServerModel.id == mikrotik_server_id))
            if not mikrotik_server_result.scalar_one_or_none():
                errors.append(f"Baris {row_num}: Mikrotik Server ID '{mikrotik_server_id}' tidak ditemukan.")
                continue

            # Siapkan data untuk disimpan
            teknis_data_dict = data_import.model_dump()
            teknis_data_dict['pelanggan_id'] = pelanggan.id
            del teknis_data_dict['email_pelanggan']
            
            data_to_create.append(DataTeknisModel(**teknis_data_dict))
            processed_emails.add(email)
            logger.info(f"Valid data prepared for row {row_num}: Pelanggan {pelanggan.nama}, Mikrotik ID {mikrotik_server_id}")

        except ValidationError as e:
            error_details = "; ".join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors()])
            errors.append(f"Baris {row_num}: {error_details}")
            logger.error(f"Validation error at row {row_num}: {error_details}")
        except Exception as e:
            errors.append(f"Baris {row_num}: Terjadi error tidak terduga - {str(e)}")
            logger.error(f"Unexpected error at row {row_num}: {str(e)}")

    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": f"Ditemukan {len(errors)} kesalahan.", "errors": errors}
        )
    
    if not data_to_create:
        raise HTTPException(status_code=400, detail="Tidak ada data valid untuk diimpor.")

    try:
        db.add_all(data_to_create)
        await db.commit()
        logger.info(f"Successfully imported {len(data_to_create)} data teknis records")
    except Exception as e:
        await db.rollback()
        logger.error(f"Database save failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan ke database: {str(e)}")

    return {"message": f"Berhasil mengimpor {len(data_to_create)} data teknis baru."}

# ==========================================================
# FUNGSI DOWNLOAD DAN IMPORT, EXPORT CSV FILE
# ==========================================================



@router.get("/available-profiles/{paket_layanan_id}", response_model=List[str])
async def get_available_profiles(paket_layanan_id: int, db: AsyncSession = Depends(get_db)):
    """
    Menyediakan daftar PPPoE profile yang tersedia (kurang dari 5 pengguna)
    berdasarkan paket layanan yang dipilih.
    """
    # 1. Dapatkan info paket untuk mengetahui kecepatan
    paket = await db.get(PaketLayananModel, paket_layanan_id)
    if not paket:
        raise HTTPException(status_code=404, detail="Paket Layanan tidak ditemukan")
    
    # Asumsi kecepatan ada di nama paket, e.g., "Internet 30 Mbps" -> "30Mbps"
    # Anda mungkin perlu menyesuaikan logika ini jika format nama paket berbeda
    kecepatan_str = f"{paket.kecepatan}Mbps"

    # 2. Ambil SEMUA server Mikrotik yang aktif
    server_result = await db.execute(select(MikrotikServerModel).where(MikrotikServerModel.is_active == True))
    servers = server_result.scalars().all()
    if not servers:
        raise HTTPException(status_code=404, detail="Tidak ada server Mikrotik aktif")
        
    # Untuk saat ini kita asumsikan semua profile ada di server pertama,
    # atau Anda bisa sesuaikan logikanya untuk loop semua server.
    server_to_check = servers[0]
    
    api, connection = mikrotik_service.get_api_connection(server_to_check)
    if not api:
        raise HTTPException(status_code=503, detail=f"Tidak dapat terhubung ke server Mikrotik {server_to_check.name}")

    try:
        # 3. Ambil semua profile dari Mikrotik
        all_profiles = mikrotik_service.get_all_ppp_profiles(api)
        
        # Saring profile yang relevan berdasarkan kecepatan
        relevant_profiles = [p for p in all_profiles if kecepatan_str in p]
        
        if not relevant_profiles:
            return [] # Tidak ada profile yang cocok

        # 4. Hitung penggunaan setiap profile dari database
        usage_query = select(
            DataTeknisModel.profile_pppoe, 
            func.count(DataTeknisModel.id)
        ).where(
            DataTeknisModel.profile_pppoe.in_(relevant_profiles)
        ).group_by(
            DataTeknisModel.profile_pppoe
        )
        
        usage_result = await db.execute(usage_query)
        profile_usage = {profile: count for profile, count in usage_result.all()}

        # 5. Saring profile yang penggunanya masih di bawah 5
        available_profiles = []
        for profile in relevant_profiles:
            if profile_usage.get(profile, 0) < 5:
                available_profiles.append(profile)
        
        # Urutkan secara alfabetis agar lebih rapi (misal: 10Mbps-a, 10Mbps-b, dst.)
        available_profiles.sort()
        
        return available_profiles

    finally:
        if connection:
            connection.disconnect()
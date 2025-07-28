import pandas as pd
from typing import List
import openpyxl
from io import BytesIO
from typing import Optional
from datetime import datetime, timedelta
import io
import csv
import chardet  # Add this import for encoding detection

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from dateutil import parser

from sqlalchemy import func, or_
from ..models.user import User as UserModel
from ..models.role import Role as RoleModel
from ..websocket_manager import manager

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from pydantic import ValidationError
import logging

from ..models.pelanggan import Pelanggan as PelangganModel
from ..schemas.pelanggan import Pelanggan as PelangganSchema, PelangganCreate, PelangganUpdate
from ..database import get_db

router = APIRouter(
    prefix="/pelanggan",
    tags=["Pelanggan"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)

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

    try:
        # Cari semua user ID dengan role 'NOC' atau 'CS'
        target_roles = ['NOC', 'CS', 'Admin'] # Sesuaikan nama role jika perlu
        query = (
            select(UserModel.id)
            .join(RoleModel)
            .where(func.lower(RoleModel.name).in_([r.lower() for r in target_roles]))
        )
        result = await db.execute(query)
        target_user_ids = result.scalars().all()

        if target_user_ids:
            # Siapkan payload notifikasi
            notification_payload = {
                "type": "new_customer_for_noc",
                "data": {
                    "pelanggan_id": db_pelanggan.id,
                    "pelanggan_nama": db_pelanggan.nama,
                    "message": f"Pelanggan baru '{db_pelanggan.nama}' telah ditambahkan. Segera buatkan Data Teknis."
                }
            }
            # Kirim notifikasi ke user yang relevan
            await manager.broadcast_to_roles(notification_payload, target_user_ids)
            
    except Exception as e:
        # Jika pengiriman notifikasi gagal, jangan gagalkan proses utama
        logger.error(f"Gagal mengirim notifikasi pelanggan baru: {e}")

    return db_pelanggan


@router.get("/", response_model=List[PelangganSchema])
async def read_all_pelanggan(
    skip: int = 0, 
    limit: int = 100, 
    # Tambahkan parameter filter opsional di sini
    search: Optional[str] = None,
    alamat: Optional[str] = None,
    id_brand: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Mengambil daftar semua pelanggan dengan paginasi dan filter.
    """
    query = select(PelangganModel).options(selectinload(PelangganModel.data_teknis))

    # Terapkan filter pencarian umum (nama, email, no_telp)
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                PelangganModel.nama.ilike(search_term),
                PelangganModel.email.ilike(search_term),
                PelangganModel.no_telp.ilike(search_term)
            )
        )

    # Terapkan filter berdasarkan alamat
    if alamat:
        query = query.where(PelangganModel.alamat == alamat)

    # Terapkan filter berdasarkan ID Brand
    if id_brand:
        query = query.where(PelangganModel.id_brand == id_brand)

    # Terapkan paginasi setelah semua filter
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    pelanggan_list = result.scalars().all()
    return pelanggan_list


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

logger = logging.getLogger(__name__)



#========================================================== IMPORT DAN EXPORT ========================================================== 



@router.get("/template/csv", response_class=StreamingResponse)
async def download_csv_template():
    """
    Men-download template CSV sederhana untuk import pelanggan.
    """
    output = io.StringIO()
    
    # Menambahkan BOM (Byte Order Mark) agar file terbuka dengan benar di Excel
    output.write('\ufeff') 

    # Header yang lebih sederhana, sesuai gambar kedua
    headers = [
        "Nama", "No KTP", "Email", "No Telepon", "Layanan", "Alamat", "Alamat 2", 
        "Blok", "Unit", "Tanggal Instalasi (YYYY-MM-DD)", "ID Brand"
    ]

    # Data contoh yang lebih ringkas
    sample_data = [
        {
            "Nama": "John Doe", "No KTP": "1234567890123456", "Email": "john.doe@example.com",
            "No Telepon": "081234567890", "Layanan": "Internet 50 Mbps", "Alamat": "Jl. Contoh No 01", 
            "Alamat 2": "RT 01 RW A", "Blok": "A", "Unit": "12", 
            "Tanggal Instalasi (YYYY-MM-DD)": "2024-01-15", "ID Brand": "ajn-01"
        },
        {
            "Nama": "Jane Smith", "No KTP": "9876543210987654", "Email": "jane.smith@example.com",
            "No Telepon": "085987654321", "Layanan": "Internet 20 Mbps", "Alamat": "Jl. Sample Stn R7 01", 
            "Alamat 2": "RW B", "Blok": "B", "Unit": "25", 
            "Tanggal Instalasi (YYYY-MM-DD)": "2024-02-20", "ID Brand": "ajn-02"
        }
    ]

    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    writer.writerows(sample_data)

    output.seek(0)
    
    # Mengatur nama file saat di-download
    response_headers = {'Content-Disposition': 'attachment; filename="template_import_pelanggan.csv"'}
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')), 
        headers=response_headers, 
        media_type='text/csv; charset=utf-8'
    )


# --- FUNGSI BARU: EXPORT DATA KE CSV ---
@router.get("/export/csv", response_class=StreamingResponse)
async def export_to_csv(db: AsyncSession = Depends(get_db)):
    """
    Mengekspor semua data pelanggan ke dalam file CSV.
    """
    query = select(PelangganModel)
    result = await db.execute(query)
    pelanggan_list = result.scalars().all()

    if not pelanggan_list:
        raise HTTPException(status_code=404, detail="Tidak ada data pelanggan untuk diekspor.")

    output = io.StringIO()
    output.write('\ufeff') # BOM for Excel compatibility

    # Ambil header dari field model pertama
    headers = pelanggan_list[0].to_dict().keys()
    writer = csv.DictWriter(output, fieldnames=headers)
    
    writer.writeheader()
    for pelanggan in pelanggan_list:
        writer.writerow(pelanggan.to_dict())

    output.seek(0)
    
    filename = f"export_pelanggan_{datetime.now().strftime('%Y%m%d')}.csv"
    response_headers = {'Content-Disposition': f'attachment; filename="{filename}"'}
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')), 
        headers=response_headers, 
        media_type='text/csv; charset=utf-8'
    )


# --- FUNGSI BARU: IMPORT DATA DARI CSV (SANGAT ROBUST) ---
@router.post("/import")
async def import_from_csv(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """
    Mengimpor data pelanggan dari file CSV dengan validasi mendalam dan laporan error.
    """
    # DEBUG: Log informasi file yang diterima
    logger.info(f"Received file: {file.filename}, content_type: {file.content_type}")
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nama file tidak valid")
        
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="File harus berformat .csv")

    try:
        contents = await file.read()
        logger.info(f"File content size: {len(contents)} bytes")
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        raise HTTPException(status_code=400, detail=f"Gagal membaca file: {str(e)}")
    
    if not contents:
        raise HTTPException(status_code=400, detail="File kosong.")

    # Deteksi encoding
    try:
        encoding = chardet.detect(contents)['encoding'] or 'utf-8'
        logger.info(f"Detected encoding: {encoding}")
        content_str = contents.decode(encoding)
    except (UnicodeDecodeError, TypeError) as e:
        logger.error(f"Encoding error: {e}")
        raise HTTPException(status_code=400, detail="Tidak dapat membaca file. Pastikan encoding adalah UTF-8.")

    stream = io.StringIO(content_str)
    lines = content_str.strip().splitlines()

    # Cari header secara dinamis
    header_row_index = -1
    for i, line in enumerate(lines):
        if "Nama" in line and "No KTP" in line and "Email" in line:
            header_row_index = i
            break
    
    logger.info(f"Header found at row: {header_row_index}")
    
    if header_row_index == -1:
        raise HTTPException(status_code=400, detail="Header (Nama, No KTP, Email, dll.) tidak ditemukan dalam file CSV.")

    # Reset stream dan skip baris sebelum header
    stream.seek(0)
    for _ in range(header_row_index):
        next(stream)

    try:
        # Deteksi dialect
        sample_line = stream.readline()
        if sample_line:
            dialect = csv.Sniffer().sniff(sample_line, delimiters=',;')
        else:
            dialect = 'excel'
        
        stream.seek(0)
        for _ in range(header_row_index):
            next(stream)
    except csv.Error:
        dialect = 'excel'
        stream.seek(0)
        for _ in range(header_row_index):
            next(stream)

    reader = csv.DictReader(stream, dialect=dialect)
    
    # Mapping nama kolom di CSV ke field di Pydantic Schema
    column_mapping = {
        "Nama": "nama", "No KTP": "no_ktp", "Email": "email", "No Telepon": "no_telp",
        "Alamat": "alamat", "Alamat 2": "alamat_2", "Blok": "blok", "Unit": "unit",
        "Tanggal Instalasi (YYYY-MM-DD)": "tgl_instalasi", "Layanan": "layanan", "ID Brand": "id_brand"
    }

    new_customers = []
    errors = []
    required_fields = ["nama", "no_ktp", "email", "no_telp", "alamat", "blok", "unit"]

    processed_rows = 0
    for row_num, row in enumerate(reader, start=header_row_index + 2):
        processed_rows += 1
        logger.info(f"Processing row {row_num}: {list(row.keys())}")
        
        data = {}
        for csv_header, model_field in column_mapping.items():
            value = row.get(csv_header, "").strip() if row.get(csv_header) else ""
            if value and value.lower() not in ['null', 'none', 'n/a', '']:
                data[model_field] = value
        
        # Skip empty rows
        if not any(data.values()):
            logger.info(f"Skipping empty row {row_num}")
            continue

        try:
            # Check required fields
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                errors.append(f"Baris {row_num}: Field wajib kosong: {', '.join(missing_fields)}")
                continue

            # Parse date if exists
            if 'tgl_instalasi' in data and data['tgl_instalasi']:
                try:
                    data['tgl_instalasi'] = parser.parse(data['tgl_instalasi']).date()
                except (parser.ParserError, ValueError):
                    errors.append(f"Baris {row_num}: Format tanggal tidak valid untuk '{data['tgl_instalasi']}'. Gunakan YYYY-MM-DD.")
                    continue
            
            # Validate with Pydantic
            customer_schema = PelangganCreate(**data)
            new_customers.append(PelangganModel(**customer_schema.model_dump()))
            logger.info(f"Valid customer added from row {row_num}: {data.get('nama')}")

        except ValidationError as e:
            error_details = "; ".join([f"{err['loc'][0] if err['loc'] else 'unknown'}: {err['msg']}" for err in e.errors()])
            errors.append(f"Baris {row_num}: {error_details}")
            logger.error(f"Validation error at row {row_num}: {error_details}")
        except Exception as e:
            errors.append(f"Baris {row_num}: Terjadi error tidak terduga - {str(e)}")
            logger.error(f"Unexpected error at row {row_num}: {str(e)}")

    logger.info(f"Processing complete. Processed rows: {processed_rows}, Valid customers: {len(new_customers)}, Errors: {len(errors)}")

    # Return errors if any
    if errors:
        logger.warning(f"Import failed with {len(errors)} errors")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": f"Ditemukan {len(errors)} kesalahan dalam file.", "errors": errors}
        )

    if not new_customers:
        logger.warning("No valid customers to import")
        raise HTTPException(status_code=400, detail="Tidak ada data pelanggan yang valid untuk diimpor.")

    # Save to database
    try:
        db.add_all(new_customers)
        await db.commit()
        logger.info(f"Successfully saved {len(new_customers)} customers to database")
    except Exception as e:
        await db.rollback()
        logger.error(f"Database save failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan saat menyimpan ke database: {str(e)}")

    success_message = f"Sukses! Berhasil mengimpor {len(new_customers)} pelanggan baru."
    logger.info(success_message)
    
    # PERBAIKAN: Pastikan return response yang proper
    return {"message": success_message, "imported_count": len(new_customers)}

#========================================================== IMPORT DAN EXPORT ========================================================== 

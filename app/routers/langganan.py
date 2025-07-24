from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse # <-- Untuk download/export
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func # <-- Untuk fungsi database seperti lower()

from datetime import date, datetime, timedelta
from typing import List, Optional
import csv
import io
import chardet
from pydantic import ValidationError

# Impor semua model dan skema yang kita butuhkan
from ..models.langganan import Langganan as LanggananModel
from ..models.pelanggan import Pelanggan as PelangganModel
from ..models.paket_layanan import PaketLayanan as PaketLayananModel
from ..schemas.langganan import Langganan as LanggananSchema, LanggananCreate, LanggananUpdate, LanggananImport
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
        # --- KUNCI PERBAIKAN ADA DI SINI ---
        .options(selectinload(LanggananModel.paket_layanan))
    )
    
    if status:
        query = query.where(LanggananModel.status == status)
        
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

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
    
    # --- KUNCI PERBAIKAN ADA DI SINI ---
    # Setelah commit, kita ambil ulang datanya dengan eager loading
    # sebelum dikembalikan sebagai respons.
    query = (
        select(LanggananModel)
        .where(LanggananModel.id == langganan_id)
        .options(selectinload(LanggananModel.paket_layanan))
    )
    result = await db.execute(query)
    updated_langganan = result.scalar_one_or_none()
    
    return updated_langganan
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


#=============================================================================
# INI ADALAH CODE YANG MENANGANI LOGIC IMPORT, EXPORT, DAN DOWNLOAD TEMPLATE
#=============================================================================

@router.get("/template/csv", response_class=StreamingResponse)
async def download_csv_template_langganan():
    """Men-download template CSV untuk import langganan."""
    output = io.StringIO()
    output.write('\ufeff')

    # Tambahkan 'id_brand' ke header
    headers = ["email_pelanggan", "id_brand", "nama_paket_layanan", "status", "metode_pembayaran", "tgl_jatuh_tempo"]
    
    # Tambahkan 'id_brand' ke contoh data
    sample_data = [{
        "email_pelanggan": "budi.s@example.com",
        "id_brand": "ajn-01",  # <-- Contoh ID Brand
        "nama_paket_layanan": "Internet 50 Mbps",
        "status": "Aktif",
        "metode_pembayaran": "Otomatis",
        "tgl_jatuh_tempo": "2025-08-01"
    }]

    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    writer.writerows(sample_data)
    output.seek(0)
    
    response_headers = {'Content-Disposition': 'attachment; filename="template_import_langganan.csv"'}
    return StreamingResponse(io.BytesIO(output.getvalue().encode('utf-8')), headers=response_headers, media_type='text/csv; charset=utf-8')

@router.get("/export/csv", response_class=StreamingResponse)
async def export_to_csv_langganan(db: AsyncSession = Depends(get_db)):
    """Mengekspor semua data langganan ke dalam file CSV."""
    query = select(LanggananModel).options(
        selectinload(LanggananModel.pelanggan),
        selectinload(LanggananModel.paket_layanan)
    )
    result = await db.execute(query)
    langganan_list = result.scalars().unique().all()

    if not langganan_list:
        raise HTTPException(status_code=404, detail="Tidak ada data langganan untuk diekspor.")

    output = io.StringIO()
    output.write('\ufeff')

    rows_to_write = []
    for langganan in langganan_list:
        rows_to_write.append({
            "Nama Pelanggan": langganan.pelanggan.nama if langganan.pelanggan else "N/A",
            "Email Pelanggan": langganan.pelanggan.email if langganan.pelanggan else "N/A",
            "Paket Layanan": langganan.paket_layanan.nama_paket if langganan.paket_layanan else "N/A",
            "Status": langganan.status,
            "Metode Pembayaran": langganan.metode_pembayaran,
            "Harga": langganan.harga_awal,
            "Tgl Jatuh Tempo": langganan.tgl_jatuh_tempo,
            "Tgl Invoice Terakhir": langganan.tgl_invoice_terakhir
        })

    writer = csv.DictWriter(output, fieldnames=rows_to_write[0].keys())
    writer.writeheader()
    writer.writerows(rows_to_write)
    output.seek(0)
    
    filename = f"export_langganan_{datetime.now().strftime('%Y%m%d')}.csv"
    response_headers = {'Content-Disposition': f'attachment; filename="{filename}"'}
    return StreamingResponse(io.BytesIO(output.getvalue().encode('utf-8')), headers=response_headers, media_type='text/csv; charset=utf-8')

@router.post("/import/csv")
async def import_from_csv_langganan(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """Mengimpor data langganan dari file CSV."""
    # (Logika pembacaan file CSV sama persis seperti sebelumnya)
    if not file.filename or not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="File harus berformat .csv")
    contents = await file.read()
    try:
        content_str = contents.decode(chardet.detect(contents)['encoding'] or 'utf-8')
    except Exception:
        raise HTTPException(status_code=400, detail="Encoding file tidak dapat dibaca.")

    reader = csv.DictReader(io.StringIO(content_str))
    errors = []
    langganan_to_create = []

    for row_num, row in enumerate(reader, start=2):
        try:
            data_import = LanggananImport(**row)
            
            # 1. Cari Pelanggan berdasarkan Email (Tetap sama)
            pelanggan_q = await db.execute(select(PelangganModel).where(func.lower(PelangganModel.email) == data_import.email_pelanggan.lower()))
            pelanggan = pelanggan_q.scalar_one_or_none()
            if not pelanggan:
                errors.append(f"Baris {row_num}: Pelanggan dengan email '{data_import.email_pelanggan}' tidak ditemukan.")
                continue

            # 2. Cari Paket Layanan berdasarkan NAMA dan ID BRAND (Ini Perubahannya)
            paket_q = await db.execute(
                select(PaketLayananModel).where(
                    func.lower(PaketLayananModel.nama_paket) == data_import.nama_paket_layanan.lower(),
                    PaketLayananModel.id_brand == data_import.id_brand # <-- KONDISI BARU
                )
            )
            paket = paket_q.scalar_one_or_none()
            if not paket:
                errors.append(f"Baris {row_num}: Paket Layanan '{data_import.nama_paket_layanan}' untuk brand '{data_import.id_brand}' tidak ditemukan.")
                continue

            # 3. Cek apakah pelanggan sudah punya langganan
            existing_langganan_q = await db.execute(select(LanggananModel).where(LanggananModel.pelanggan_id == pelanggan.id))
            if existing_langganan_q.scalar_one_or_none():
                errors.append(f"Baris {row_num}: Pelanggan '{pelanggan.nama}' sudah memiliki langganan.")
                continue
            
            # 4. Siapkan data untuk dibuat
            new_langganan_data = {
                "pelanggan_id": pelanggan.id,
                "paket_layanan_id": paket.id,
                "status": data_import.status,
                "metode_pembayaran": data_import.metode_pembayaran,
                "harga_awal": paket.harga, # Ambil harga dari paket
                "tgl_jatuh_tempo": data_import.tgl_jatuh_tempo,
            }
            langganan_to_create.append(LanggananModel(**new_langganan_data))

        except ValidationError as e:
            errors.append(f"Baris {row_num}: " + "; ".join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]))
        except Exception as e:
            errors.append(f"Baris {row_num}: Terjadi error - {str(e)}")

    if errors:
        raise HTTPException(status_code=422, detail={"message": "Impor gagal, ditemukan error.", "errors": errors})
    
    if not langganan_to_create:
        raise HTTPException(status_code=400, detail="Tidak ada data valid untuk diimpor.")

    try:
        db.add_all(langganan_to_create)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan ke database: {e}")

    return {"message": f"Berhasil mengimpor {len(langganan_to_create)} langganan baru."}

#=============================================================================
# INI ADALAH CODE YANG MENANGANI LOGIC IMPORT, EXPORT, DAN DOWNLOAD TEMPLATE
#=============================================================================
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import text, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from datetime import date, timedelta, datetime
import uuid
from typing import List, Dict, Any
import pytz

# Impor semua model dan skema yang dibutuhkan
from ..models.invoice import Invoice as InvoiceModel
from ..models.langganan import Langganan as LanggananModel
from ..models.pelanggan import Pelanggan as PelangganModel
from ..models.paket_layanan import PaketLayanan as PaketLayananModel
from ..models.harga_layanan import HargaLayanan as HargaLayananModel
from ..schemas.invoice import Invoice as InvoiceSchema, InvoiceGenerate, InvoiceUpdate
from ..database import get_db
from ..services import xendit_service

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
    responses={404: {"description": "Not found"}},
)

@router.post("/generate", response_model=InvoiceSchema, status_code=status.HTTP_201_CREATED)
async def generate_invoice_for_subscription(
    invoice_data: InvoiceGenerate, db: AsyncSession = Depends(get_db)
):
    """
    Membuat invoice baru untuk satu langganan dan mendaftarkannya ke Xendit.
    """
    # 1. Ambil semua data terkait dalam satu query
    query = (
        select(LanggananModel)
        .where(LanggananModel.id == invoice_data.langganan_id)
        .options(
            selectinload(LanggananModel.pelanggan).selectinload(PelangganModel.harga_layanan),
            selectinload(LanggananModel.paket_layanan)
        )
    )
    langganan = (await db.execute(query)).scalar_one_or_none()
    
    if not langganan:
        raise HTTPException(status_code=404, detail="Langganan tidak ditemukan")

    pelanggan = langganan.pelanggan
    paket = langganan.paket_layanan
    brand = pelanggan.harga_layanan

    # 2. Hitung total harga
    total_harga = float(paket.harga) * (1 + (float(brand.pajak) / 100))

    # 3. Siapkan data untuk invoice baru
    new_invoice_data = {
        "invoice_number": f"INV-{date.today().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}",
        "pelanggan_id": pelanggan.id,
        "id_pelanggan": getattr(pelanggan, 'id_pelanggan_lama', f"CUST-{pelanggan.id}"),
        "brand": brand.brand,
        "total_harga": round(total_harga, 2),
        "no_telp": pelanggan.no_telp,
        "email": pelanggan.email,
        "tgl_invoice": date.today(),
        "tgl_jatuh_tempo": date.today() + timedelta(days=14)
    }
    
    db_invoice = InvoiceModel(**new_invoice_data)
    db.add(db_invoice)
    await db.commit()
    await db.refresh(db_invoice)

    # 4. Panggil Xendit untuk membuat payment link
    try:
        xendit_response = await xendit_service.create_xendit_invoice(db_invoice, pelanggan)
        
        # 5. Update record invoice dengan data dari Xendit
        db_invoice.payment_link = xendit_response.get("invoice_url")
        db_invoice.xendit_id = xendit_response.get("id")
        db_invoice.xendit_external_id = xendit_response.get("external_id")
        if xendit_response.get("expiry_date"):
            db_invoice.expiry_date = parse_xendit_datetime(xendit_response.get("expiry_date"))
        
        db.add(db_invoice)
        await db.commit()
        await db.refresh(db_invoice)

    except Exception as e:
        print(f"Gagal mengintegrasikan dengan Xendit: {e}")
        await db.rollback()  # Roll back sesi jika ada error
        raise HTTPException(status_code=500, detail=f"Gagal mengintegrasikan dengan Xendit: {str(e)}")

    return db_invoice

def parse_xendit_datetime(iso_datetime_str: str) -> str:
    """
    Fungsi untuk mengkonversi format datetime ISO 8601 dari Xendit ke format yang kompatibel dengan MySQL
    """
    try:
        # Parse string datetime ISO yang berformat: 2025-07-17T07:51:12.000Z
        if iso_datetime_str.endswith('Z'):
            iso_datetime_str = iso_datetime_str[:-1] + '+00:00'
        
        # Parse ke objek datetime
        dt = datetime.fromisoformat(iso_datetime_str)
        
        # Konversi ke zona waktu lokal (WIB/Jakarta)
        jakarta_tz = pytz.timezone('Asia/Jakarta')
        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)
        
        dt_jakarta = dt.astimezone(jakarta_tz)
        
        # Format ke string yang kompatibel dengan MySQL
        return dt_jakarta.strftime('%Y-%m-%d %H:%M:%S')
    
    except Exception as e:
        print(f"Error parsing datetime: {e}")
        return datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%Y-%m-%d %H:%M:%S')

@router.post("/xendit-callback", status_code=status.HTTP_200_OK)
async def handle_xendit_callback(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Endpoint untuk menangani callback dari Xendit ketika invoice dibayar
    """
    try:
        # Parse request body sebagai JSON
        payload = await request.json()
        
        # Log payload untuk debugging
        print(f"Xendit callback payload: {payload}")
        
        # Ambil data yang diperlukan dari payload
        external_id = payload.get("external_id")
        paid_amount = payload.get("paid_amount")
        paid_at = payload.get("paid_at")
        status = payload.get("status")
        
        if not external_id:
            raise HTTPException(
                status_code=400, 
                detail="External ID tidak ditemukan dalam payload"
            )
        
        # Cari invoice berdasarkan external_id (yang seharusnya sama dengan invoice_number)
        stmt = select(InvoiceModel).where(InvoiceModel.invoice_number == external_id)
        result = await db.execute(stmt)
        invoice = result.scalar_one_or_none()
        
        if not invoice:
            raise HTTPException(
                status_code=404, 
                detail=f"Invoice dengan external_id {external_id} tidak ditemukan"
            )
        
        # Update invoice berdasarkan status dari Xendit
        if status == "PAID":
            # Parse datetime dari format ISO 8601 ke format MySQL
            parsed_paid_at = None
            if paid_at:
                parsed_paid_at = parse_xendit_datetime(paid_at)
            
            # Update menggunakan SQLAlchemy ORM (lebih aman dari raw SQL)
            invoice.status_invoice = "Lunas"
            invoice.paid_amount = float(paid_amount) if paid_amount else None
            invoice.paid_at = parsed_paid_at
            invoice.updated_at = datetime.now(pytz.timezone('Asia/Jakarta'))
            
            # Commit changes
            await db.commit()
            await db.refresh(invoice)
            
            print(f"Invoice {external_id} berhasil diupdate menjadi Lunas")
            
        elif status == "EXPIRED":
            invoice.status_invoice = "Expired"
            invoice.updated_at = datetime.now(pytz.timezone('Asia/Jakarta'))
            await db.commit()
            await db.refresh(invoice)
            
            print(f"Invoice {external_id} berhasil diupdate menjadi Expired")
            
        else:
            print(f"Status {status} tidak dikenali untuk invoice {external_id}")
            
        return {
            "message": "Callback processed successfully",
            "invoice_number": external_id,
            "status": status
        }
        
    except Exception as e:
        print(f"Error processing Xendit callback: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing callback: {str(e)}"
        )

@router.get("/", response_model=List[InvoiceSchema])
async def get_all_invoices(db: AsyncSession = Depends(get_db)):
    """
    Mengambil semua data invoice.
    """
    result = await db.execute(select(InvoiceModel))
    return result.scalars().all()

@router.get("/{invoice_id}", response_model=InvoiceSchema)
async def get_invoice_by_id(invoice_id: int, db: AsyncSession = Depends(get_db)):
    """
    Mengambil detail satu invoice berdasarkan ID.
    """
    invoice = await db.get(InvoiceModel, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    return invoice

@router.put("/{invoice_id}", response_model=InvoiceSchema)
async def update_invoice(
    invoice_id: int, 
    invoice_update: InvoiceUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Update invoice manually (untuk testing atau admin purposes)
    """
    # Cari invoice
    invoice = await db.get(InvoiceModel, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    
    # Update field yang diberikan
    update_data = invoice_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(invoice, field, value)
    
    # Set updated_at
    invoice.updated_at = datetime.now(pytz.timezone('Asia/Jakarta'))
    
    await db.commit()
    await db.refresh(invoice)
    
    return invoice

@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)):
    """
    Menghapus invoice. Sebaiknya digunakan dengan hati-hati.
    """
    db_invoice = await db.get(InvoiceModel, invoice_id)
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
        
    await db.delete(db_invoice)
    await db.commit()
    return None

# Endpoint untuk testing callback secara manual
@router.post("/test-callback", status_code=status.HTTP_200_OK)
async def test_xendit_callback(payload: Dict[Any, Any], db: AsyncSession = Depends(get_db)):
    """
    Endpoint untuk testing callback Xendit secara manual
    """
    # Simulasikan callback dengan data yang diberikan
    external_id = payload.get("external_id")
    paid_amount = payload.get("paid_amount", 0)
    paid_at = payload.get("paid_at", datetime.now().isoformat() + "Z")
    status = payload.get("status", "PAID")
    
    # Panggil fungsi handle_xendit_callback
    fake_request = type('Request', (), {
        'json': lambda: payload
    })()
    
    try:
        result = await handle_xendit_callback(fake_request, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
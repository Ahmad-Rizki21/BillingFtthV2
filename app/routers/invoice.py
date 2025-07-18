# app/routers/invoice.py - Perbaikan untuk webhook callback

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
import uuid
from typing import List, Dict, Any, Optional
import pytz
import json
import logging

# Impor semua model dan skema yang dibutuhkan
from ..models.invoice import Invoice as InvoiceModel
from ..models.langganan import Langganan as LanggananModel
from ..models.pelanggan import Pelanggan as PelangganModel
from ..models.paket_layanan import PaketLayanan as PaketLayananModel
from ..schemas.invoice import Invoice as InvoiceSchema, InvoiceGenerate
from ..database import get_db
from ..config import settings
from ..services import xendit_service, mikrotik_service

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
    responses={404: {"description": "Not found"}},
)

def parse_xendit_datetime(iso_datetime_str: str) -> datetime:
    """Fungsi untuk mengkonversi format datetime ISO 8601 dari Xendit."""
    try:
        if not iso_datetime_str:
            return datetime.now(pytz.utc)
            
        # Menangani format 'Z' (UTC)
        if iso_datetime_str.endswith('Z'):
            iso_datetime_str = iso_datetime_str[:-1] + '+00:00'
        dt = datetime.fromisoformat(iso_datetime_str)
        return dt
    except (ValueError, TypeError) as e:
        logger.error(f"Error parsing datetime {iso_datetime_str}: {e}")
        # Fallback jika format tidak valid atau None
        return datetime.now(pytz.utc)

@router.post("/generate", response_model=InvoiceSchema, status_code=status.HTTP_201_CREATED)
async def generate_invoice_for_subscription(
    invoice_data: InvoiceGenerate, db: AsyncSession = Depends(get_db)
):
    """Membuat invoice baru untuk satu langganan dan mendaftarkannya ke Xendit."""
    try:
        query = (
            select(LanggananModel)
            .where(LanggananModel.id == invoice_data.langganan_id)
            .options(
                selectinload(LanggananModel.pelanggan).selectinload(PelangganModel.harga_layanan),
                selectinload(LanggananModel.pelanggan).selectinload(PelangganModel.data_teknis),
                selectinload(LanggananModel.paket_layanan)
            )
        )
        langganan = (await db.execute(query)).scalar_one_or_none()
        
        if not langganan:
            raise HTTPException(status_code=404, detail="Langganan tidak ditemukan")

        pelanggan = langganan.pelanggan
        paket = langganan.paket_layanan
        brand = pelanggan.harga_layanan

        total_harga = float(paket.harga) * (1 + (float(brand.pajak) / 100))

        new_invoice_data = {
            "invoice_number": f"INV-{date.today().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}",
            "pelanggan_id": pelanggan.id,
            "id_pelanggan": pelanggan.data_teknis.id_pelanggan,
            "brand": brand.brand,
            "total_harga": round(total_harga, 2),
            "no_telp": pelanggan.no_telp,
            "email": pelanggan.email,          
            "tgl_invoice": date.today(),
            "tgl_jatuh_tempo": langganan.tgl_jatuh_tempo
        }
        
        db_invoice = InvoiceModel(**new_invoice_data)
        db.add(db_invoice)
        await db.commit()
        await db.refresh(db_invoice)

        try:
            xendit_response = await xendit_service.create_xendit_invoice(db_invoice, pelanggan)
            
            db_invoice.payment_link = xendit_response.get("invoice_url")
            db_invoice.xendit_id = xendit_response.get("id")
            db_invoice.xendit_external_id = xendit_response.get("external_id")
            if xendit_response.get("expiry_date"):
                db_invoice.expiry_date = parse_xendit_datetime(xendit_response.get("expiry_date"))
            
            db.add(db_invoice)
            await db.commit()
            await db.refresh(db_invoice)

        except Exception as e:
            logger.error(f"Error integrating with Xendit: {str(e)}")
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Gagal mengintegrasikan dengan Xendit: {str(e)}")

        return db_invoice
    
    except Exception as e:
        logger.error(f"Error generating invoice: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error generating invoice: {str(e)}")

@router.post("/xendit-callback", status_code=status.HTTP_200_OK)
async def handle_xendit_callback(
    request: Request, 
    x_callback_token: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Endpoint untuk menangani callback dari Xendit ketika invoice dibayar atau kadaluarsa."""
    try:
        # Validasi callback token
        if x_callback_token != settings.XENDIT_CALLBACK_TOKEN:
            logger.warning(f"Invalid callback token received: {x_callback_token}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid callback token")

        # Cek apakah ini adalah ping request
        content_length = request.headers.get('content-length')
        if not content_length or int(content_length) == 0:
            logger.info("Received ping request from Xendit")
            return {"message": "Webhook URL successfully verified."}

        # Parse payload
        payload = await request.json()
        logger.info(f"Xendit callback payload: {json.dumps(payload, indent=2)}")
        
        external_id = payload.get("external_id")
        xendit_status = payload.get("status")
        
        if not external_id:
            logger.error("External ID not found in payload")
            raise HTTPException(status_code=400, detail="External ID tidak ditemukan")
        
        # Cari invoice berdasarkan external_id
        stmt = (
            select(InvoiceModel)
            .where(InvoiceModel.xendit_external_id == external_id)
            .options(
                selectinload(InvoiceModel.pelanggan).selectinload(PelangganModel.langganan),
                selectinload(InvoiceModel.pelanggan).selectinload(PelangganModel.data_teknis)
            )
        )
        invoice = (await db.execute(stmt)).scalar_one_or_none()
        
        if not invoice:
            logger.error(f"Invoice with external_id {external_id} not found")
            raise HTTPException(status_code=404, detail=f"Invoice dengan external_id {external_id} tidak ditemukan")
        
        # Pastikan ada langganan terkait
        if not invoice.pelanggan or not invoice.pelanggan.langganan:
            logger.error(f"No subscription found for invoice {external_id}")
            raise HTTPException(status_code=400, detail="Tidak ada langganan terkait dengan invoice ini")
        
        # Ambil langganan pertama (asumsi satu pelanggan satu langganan aktif)
        langganan_terkait = invoice.pelanggan.langganan[0] if invoice.pelanggan.langganan else None
        
        if not langganan_terkait:
            logger.error(f"No active subscription found for invoice {external_id}")
            raise HTTPException(status_code=400, detail="Tidak ada langganan aktif ditemukan")

        # Proses berdasarkan status
        if xendit_status == "PAID":
            logger.info(f"Processing PAID status for invoice {external_id}")
            
            # Update invoice status
            invoice.status_invoice = "Lunas"
            invoice.paid_amount = float(payload.get("paid_amount", 0))
            invoice.paid_at = parse_xendit_datetime(payload.get("paid_at"))
            
            # Update langganan status
            old_status = langganan_terkait.status
            langganan_terkait.status = "Aktif"
            
            # Update tanggal jatuh tempo
            current_due_date = langganan_terkait.tgl_jatuh_tempo
            next_due_date = current_due_date + relativedelta(months=1)
            langganan_terkait.tgl_jatuh_tempo = next_due_date
            
            # Simpan perubahan ke database
            db.add(invoice)
            db.add(langganan_terkait)
            await db.commit()
            
            logger.info(f"Payment processed successfully for invoice {external_id}")
            logger.info(f"Subscription status changed from {old_status} to {langganan_terkait.status}")
            
            # Trigger update Mikrotik untuk aktivasi layanan
            try:
                await mikrotik_service.trigger_mikrotik_update(db, langganan_terkait)
                logger.info(f"Mikrotik update triggered successfully for subscription {langganan_terkait.id}")
            except Exception as mikrotik_error:
                logger.error(f"Error updating Mikrotik for subscription {langganan_terkait.id}: {mikrotik_error}")
                # Jangan raise error di sini, karena pembayaran sudah diproses
                # Log error saja untuk monitoring

        elif xendit_status == "EXPIRED":
            logger.info(f"Processing EXPIRED status for invoice {external_id}")
            invoice.status_invoice = "Kadaluarsa"
            db.add(invoice)
            await db.commit()
            
            logger.info(f"Invoice {external_id} expired. Suspension will be handled by daily scheduler if overdue.")

        else:
            logger.warning(f"Unknown status received: {xendit_status} for invoice {external_id}")

        return {"message": "Callback processed successfully", "status": xendit_status}
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing Xendit callback: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing callback: {str(e)}")

# Endpoint tambahan untuk debugging
@router.get("/debug/{invoice_id}")
async def debug_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)):
    """Endpoint untuk debugging invoice dan langganan terkait."""
    try:
        stmt = (
            select(InvoiceModel)
            .where(InvoiceModel.id == invoice_id)
            .options(
                selectinload(InvoiceModel.pelanggan).selectinload(PelangganModel.langganan),
                selectinload(InvoiceModel.pelanggan).selectinload(PelangganModel.data_teknis)
            )
        )
        invoice = (await db.execute(stmt)).scalar_one_or_none()
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
        
        debug_info = {
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "xendit_external_id": invoice.xendit_external_id,
            "status_invoice": invoice.status_invoice,
            "pelanggan_id": invoice.pelanggan_id,
            "pelanggan_nama": invoice.pelanggan.nama if invoice.pelanggan else None,
            "langganan_count": len(invoice.pelanggan.langganan) if invoice.pelanggan else 0,
            "langganan_info": [
                {
                    "id": l.id,
                    "status": l.status,
                    "tgl_jatuh_tempo": l.tgl_jatuh_tempo
                } for l in invoice.pelanggan.langganan
            ] if invoice.pelanggan else [],
            "data_teknis": {
                "id_pelanggan": invoice.pelanggan.data_teknis.id_pelanggan if invoice.pelanggan and invoice.pelanggan.data_teknis else None,
                "profile_pppoe": invoice.pelanggan.data_teknis.profile_pppoe if invoice.pelanggan and invoice.pelanggan.data_teknis else None,
                "mikrotik_server_id": invoice.pelanggan.data_teknis.mikrotik_server_id if invoice.pelanggan and invoice.pelanggan.data_teknis else None
            } if invoice.pelanggan else None
        }
        
        return debug_info
        
    except Exception as e:
        logger.error(f"Error in debug endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Debug error: {str(e)}")
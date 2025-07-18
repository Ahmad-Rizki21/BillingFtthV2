# app/routers/invoice.py

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from datetime import date, timedelta, datetime, timezone
from dateutil.relativedelta import relativedelta
import uuid
from typing import List, Optional
import json
import logging
import pytz

# Impor semua model dan skema yang dibutuhkan
from ..models.invoice import Invoice as InvoiceModel
from ..models.langganan import Langganan as LanggananModel
from ..models.pelanggan import Pelanggan as PelangganModel
from ..schemas.invoice import Invoice as InvoiceSchema, InvoiceGenerate
from ..database import get_db
from ..config import settings
from ..services import xendit_service, mikrotik_service

logger = logging.getLogger('app.routers.invoice')

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
        if iso_datetime_str.endswith('Z'):
            iso_datetime_str = iso_datetime_str[:-1] + '+00:00'
        return datetime.fromisoformat(iso_datetime_str)
    except (ValueError, TypeError):
        return datetime.now(pytz.utc)

# Fungsi terpusat untuk memproses logika setelah pembayaran berhasil
async def _process_successful_payment(db: AsyncSession, invoice: InvoiceModel, payload: dict = None):
    """Fungsi terpusat untuk menangani logika setelah invoice lunas."""
    pelanggan = await db.get(
        PelangganModel, 
        invoice.pelanggan_id, 
        options=[selectinload(PelangganModel.langganan), selectinload(PelangganModel.data_teknis)]
    )
    if not pelanggan or not pelanggan.langganan:
        logger.error(f"Pelanggan atau langganan tidak ditemukan untuk invoice {invoice.invoice_number}")
        return

    langganan = pelanggan.langganan[0]
    old_status = langganan.status

    invoice.status_invoice = "Lunas"
    if payload:
        invoice.paid_amount = float(payload.get("paid_amount", invoice.total_harga))
        invoice.paid_at = parse_xendit_datetime(payload.get("paid_at"))
    else:
        invoice.paid_amount = invoice.total_harga
        invoice.paid_at = datetime.now(timezone.utc)

    langganan.status = "Aktif"
    current_due_date = langganan.tgl_jatuh_tempo or date.today()
    next_due_date = current_due_date + relativedelta(months=1)
    langganan.tgl_jatuh_tempo = next_due_date

    db.add(invoice)
    db.add(langganan)

    logger.info(f"Payment processed successfully for invoice {invoice.invoice_number}")

    if old_status == "Suspended":
        await mikrotik_service.trigger_mikrotik_update(db, langganan)
        logger.info(f"Mikrotik update triggered to re-activate subscription {langganan.id}")

@router.post("/xendit-callback", status_code=status.HTTP_200_OK)
async def handle_xendit_callback(request: Request, x_callback_token: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)):
    if x_callback_token != settings.XENDIT_CALLBACK_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid callback token")

    payload = await request.json()
    logger.info(f"Xendit callback payload: {json.dumps(payload, indent=2)}")
    
    external_id = payload.get("external_id")
    xendit_status = payload.get("status")

    if not external_id:
        raise HTTPException(status_code=400, detail="External ID tidak ditemukan")

    stmt = select(InvoiceModel).where(InvoiceModel.xendit_external_id == external_id)
    invoice = (await db.execute(stmt)).scalar_one_or_none()

    if not invoice:
        raise HTTPException(status_code=404, detail=f"Invoice {external_id} tidak ditemukan")

    if invoice.status_invoice == "Lunas":
        return {"message": "Invoice already processed"}

    try:
        if xendit_status == "PAID":
            await _process_successful_payment(db, invoice, payload)
        elif xendit_status == "EXPIRED":
            invoice.status_invoice = "Kadaluarsa"
            db.add(invoice)
        
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error processing Xendit callback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing callback: {str(e)}")

    return {"message": "Callback processed successfully"}
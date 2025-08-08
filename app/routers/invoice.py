from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from sqlalchemy import func, or_ # <-- TAMBAHAN: Impor func
from datetime import date, timedelta, datetime, timezone
from dateutil.relativedelta import relativedelta
import uuid
from typing import List, Optional
import json
import logging
import pytz
from ..websocket_manager import manager

from typing import Optional

# Impor semua model dan skema yang dibutuhkan
from ..models.invoice import Invoice as InvoiceModel
from ..models.langganan import Langganan as LanggananModel
from ..models.pelanggan import Pelanggan as PelangganModel
from ..models.user import User as UserModel # <-- TAMBAHAN: Impor UserModel
from ..models.role import Role as RoleModel # <-- TAMBAHAN: Impor RoleModel
from ..schemas.invoice import Invoice as InvoiceSchema, InvoiceGenerate, MarkAsPaidRequest
from ..database import get_db
from ..services import mikrotik_service
from ..config import settings
from ..services import xendit_service, mikrotik_service

logger = logging.getLogger('app.routers.invoice')

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[InvoiceSchema])
async def get_all_invoices(
    db: AsyncSession = Depends(get_db),
    # Tambahkan parameter filter
    search: Optional[str] = None,
    status_invoice: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    """Mengambil semua data invoice dengan filter."""
    query = (
        select(InvoiceModel)
        .join(InvoiceModel.pelanggan)
        .options(selectinload(InvoiceModel.pelanggan))
    )

    # Filter pencarian umum (No. Invoice, Nama Pelanggan, ID PPPoE)
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                InvoiceModel.invoice_number.ilike(search_term),
                PelangganModel.nama.ilike(search_term),
                InvoiceModel.id_pelanggan.ilike(search_term)
            )
        )

    # Filter berdasarkan status invoice
    if status_invoice:
        query = query.where(InvoiceModel.status_invoice == status_invoice)

    # Filter berdasarkan rentang tanggal jatuh tempo
    if start_date:
        query = query.where(InvoiceModel.tgl_jatuh_tempo >= start_date)
    if end_date:
        query = query.where(InvoiceModel.tgl_jatuh_tempo <= end_date)

    result = await db.execute(query)
    return result.scalars().all()


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
    
    # --- PERUBAHAN 1: Muat semua data yang diperlukan sekaligus ---
    pelanggan = await db.get(
        PelangganModel,
        invoice.pelanggan_id,
        options=[
            selectinload(PelangganModel.harga_layanan),
            selectinload(PelangganModel.langganan).selectinload(LanggananModel.paket_layanan),
            selectinload(PelangganModel.data_teknis) 
        ]
    )
    if not pelanggan or not pelanggan.langganan:
        logger.error(f"Pelanggan atau langganan tidak ditemukan untuk invoice {invoice.invoice_number}")
        return

    langganan = pelanggan.langganan[0]

    # Update status invoice (logika ini tetap sama)
    invoice.status_invoice = "Lunas"
    if payload:
        invoice.paid_amount = float(payload.get("paid_amount", invoice.total_harga))
        invoice.paid_at = parse_xendit_datetime(payload.get("paid_at"))
    else:
        invoice.paid_amount = invoice.total_harga
        invoice.paid_at = datetime.now(timezone.utc)
    
    db.add(invoice)

    # --- PERUBAHAN 2: Logika siklus penagihan dan pembaruan harga ---
    
    next_due_date = None

    if langganan.metode_pembayaran == 'Prorate':
        # --- TAMBAHAN: Ambil data paket dan brand ---
        paket = langganan.paket_layanan
        brand = pelanggan.harga_layanan
        
        # Ganti metode pembayaran
        langganan.metode_pembayaran = 'Otomatis'

        # Hitung jatuh tempo berikutnya
        current_due_date = invoice.tgl_jatuh_tempo 
        next_due_date = (current_due_date + relativedelta(days=1)).replace(day=1)
        
        # --- TAMBAHAN: Hitung ulang dan perbarui harga ke harga normal ---
        if paket and brand:
            harga_paket = float(paket.harga)
            pajak_persen = float(brand.pajak)
            harga_baru_otomatis = harga_paket * (1 + (pajak_persen / 100))
            
            # Perbarui harga_awal di langganan
            langganan.harga_awal = round(harga_baru_otomatis, 0)
            
            logger.info(f"Harga langganan ID {langganan.id} diupdate ke harga Otomatis: {langganan.harga_awal}")
        else:
            logger.error(f"Data paket atau brand tidak lengkap untuk langganan ID {langganan.id}. Harga tidak diupdate.")
        
        logger.info(f"Langganan ID {langganan.id} diubah ke Otomatis. Jatuh tempo berikutnya: {next_due_date}")

    else: # Jika sudah Otomatis
        current_due_date = langganan.tgl_jatuh_tempo or date.today()
        next_due_date = (current_due_date + relativedelta(months=1)).replace(day=1)

    # Update status langganan dan tanggal jatuh tempo berikutnya
    langganan.status = "Aktif"
    langganan.tgl_jatuh_tempo = next_due_date
    langganan.tgl_invoice_terakhir = date.today()

    db.add(langganan)

    try:
        await mikrotik_service.trigger_mikrotik_update(db, langganan)
        logger.info(f"Successfully triggered Mikrotik reactivation for subscription ID {langganan.id}")
    except Exception as e:
        logger.error(f"Failed to trigger Mikrotik reactivation for subscription ID {langganan.id}: {e}")
        # Tetap lanjutkan proses meskipun trigger gagal, tapi catat errornya.

    logger.info(f"Payment processed successfully for invoice {invoice.invoice_number}")


@router.post("/xendit-callback", status_code=status.HTTP_200_OK)
async def handle_xendit_callback(request: Request, x_callback_token: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)):
    # 1. Ambil payload dari request
    payload = await request.json()
    logger.info(f"Xendit callback received. Payload: {json.dumps(payload, indent=2)}")
    
    # 2. Ekstrak external_id untuk identifikasi
    external_id = payload.get("external_id")
    if not external_id:
        raise HTTPException(status_code=400, detail="External ID tidak ditemukan di payload")

    # 3. Tentukan brand berdasarkan awalan external_id
    try:
        brand_prefix = external_id.split('/')[0]
    except IndexError:
        raise HTTPException(status_code=400, detail="Format external_id tidak valid")

    # 4. Pilih token callback yang benar berdasarkan brand
    correct_token = None
    if brand_prefix.lower() in ["jakinet", "nagrak"]:
        # Ambil token dari property Settings yang sudah kita buat
        correct_token = settings.XENDIT_CALLBACK_TOKENS.get("ARTACOMINDO")
        logger.info("Validating with ARTACOMINDO callback token.")
    elif brand_prefix.lower() == "jelantik":
        correct_token = settings.XENDIT_CALLBACK_TOKENS.get("JELANTIK")
        logger.info("Validating with JELANTIK callback token.")
    
    # 5. Lakukan validasi
    if not correct_token or x_callback_token != correct_token:
        logger.warning(f"Invalid callback token received for brand '{brand_prefix}'.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid callback token")

    # --- Dari sini, logika pemrosesan invoice tetap sama ---
    
    xendit_status = payload.get("status")

    stmt = select(InvoiceModel).where(InvoiceModel.xendit_external_id == external_id)
    invoice = (await db.execute(stmt)).scalar_one_or_none()

    if not invoice:
        logger.warning(f"Invoice with external_id {external_id} not found, but callback is valid.")
        return {"message": "Callback valid, invoice not found."}

    if invoice.status_invoice == "Lunas":
        return {"message": "Invoice already processed"}

    try:
        if xendit_status == "PAID":
            await _process_successful_payment(db, invoice, payload)
            
            # (Logika notifikasi WebSocket Anda di sini)

        elif xendit_status == "EXPIRED":
            invoice.status_invoice = "Kadaluarsa"
            db.add(invoice)
        
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"Error processing Xendit callback for external_id {external_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while processing callback.")

    return {"message": "Callback processed successfully"}

@router.post("/generate", response_model=InvoiceSchema, status_code=status.HTTP_201_CREATED)
async def generate_manual_invoice(
    invoice_data: InvoiceGenerate,
    db: AsyncSession = Depends(get_db)
):
    """Membuat satu invoice secara manual berdasarkan langganan_id."""
    # 1. Ambil data langganan beserta relasi yang diperlukan
    langganan = await db.get(
        LanggananModel, 
        invoice_data.langganan_id,
        options=[
            selectinload(LanggananModel.pelanggan).selectinload(PelangganModel.harga_layanan),
            selectinload(LanggananModel.pelanggan).selectinload(PelangganModel.data_teknis),
            selectinload(LanggananModel.paket_layanan)
        ]
    )
    if not langganan:
        raise HTTPException(status_code=404, detail="Langganan tidak ditemukan")

    # 2. Validasi status langganan
    if langganan.status == "Berhenti":
        raise HTTPException(
            status_code=400,
            detail=f"Gagal membuat invoice. Status langganan untuk pelanggan '{langganan.pelanggan.nama}' adalah 'Berhenti'."
        )

    # 3. Pastikan semua data relasi ada
    pelanggan = langganan.pelanggan
    paket = langganan.paket_layanan
    if not pelanggan or not paket or not pelanggan.harga_layanan or not pelanggan.data_teknis:
        raise HTTPException(status_code=400, detail=f"Data pendukung (pelanggan, paket, brand, teknis) tidak lengkap untuk langganan ID {langganan.id}")
    
    brand = pelanggan.harga_layanan
    data_teknis = pelanggan.data_teknis

    # Validasi data numerik
    if not paket.harga or not brand.pajak:
        raise HTTPException(status_code=400, detail="Harga paket atau pajak tidak valid")

    # 4. Cek apakah invoice untuk periode ini sudah ada
    existing_invoice_stmt = select(InvoiceModel.id).where(
        InvoiceModel.pelanggan_id == langganan.pelanggan_id,
        InvoiceModel.tgl_jatuh_tempo == langganan.tgl_jatuh_tempo
    )
    if (await db.execute(existing_invoice_stmt)).scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Invoice untuk periode ini sudah ada.")

    # 5. Buat detail invoice
    jatuh_tempo_str = langganan.tgl_jatuh_tempo.strftime('%d/%m/%Y')
    nomor_invoice = f"INV-{pelanggan.nama.replace(' ', '')}-{langganan.tgl_jatuh_tempo.strftime('%Y%m')}-{uuid.uuid4().hex[:4].upper()}"

    # Hitung harga dasar dan pajak
    harga_dasar = float(paket.harga)
    pajak_persen = float(brand.pajak)
    pajak = round(harga_dasar * (pajak_persen / 100), 2)
    total_harga = round(harga_dasar + pajak, 2)

    new_invoice_data = {
        "invoice_number": nomor_invoice,
        "pelanggan_id": pelanggan.id,
        "id_pelanggan": data_teknis.id_pelanggan,
        "brand": brand.brand,
        "total_harga": total_harga,
        "no_telp": pelanggan.no_telp,
        "email": pelanggan.email,
        "tgl_invoice": date.today(),
        "tgl_jatuh_tempo": langganan.tgl_jatuh_tempo,
        "status_invoice": "Belum Dibayar",
    }

    db_invoice = InvoiceModel(**new_invoice_data)
    db.add(db_invoice)
    await db.flush()

    # 6. Kirim ke Xendit dengan detail pajak dan deskripsi
    try:
        periode = f"Periode Tgl {db_invoice.tgl_invoice.day}-{db_invoice.tgl_jatuh_tempo.day} {db_invoice.tgl_jatuh_tempo.strftime('%B %Y')}"
        deskripsi_xendit = f"Biaya berlangganan internet up to {paket.kecepatan} Mbps jatuh tempo pembayaran tanggal {jatuh_tempo_str}"
        # Format nomor telepon dengan kode negara
        no_telp_xendit = f"+62{pelanggan.no_telp.replace('0', '', 1)}" if pelanggan.no_telp.startswith('0') else pelanggan.no_telp
        xendit_response = await xendit_service.create_xendit_invoice(db_invoice, pelanggan, paket, deskripsi_xendit, pajak, no_telp_xendit)
        db_invoice.payment_link = xendit_response.get("short_url", xendit_response.get("invoice_url"))
        db_invoice.xendit_id = xendit_response.get("id")
        db_invoice.xendit_external_id = xendit_response.get("external_id")
        await db.commit()
        await db.refresh(db_invoice)
    except Exception as e:
        await db.rollback()
        logger.error(f"Gagal membuat invoice di Xendit: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Gagal membuat invoice di Xendit: {str(e)}")

    return db_invoice


@router.post("/{invoice_id}/mark-as-paid", response_model=InvoiceSchema)
async def mark_invoice_as_paid(
    invoice_id: int,
    payload: MarkAsPaidRequest,
    db: AsyncSession = Depends(get_db)
):
    """Menandai sebuah invoice sebagai lunas secara manual."""
    stmt = select(InvoiceModel).where(InvoiceModel.id == invoice_id)
    invoice = (await db.execute(stmt)).scalar_one_or_none()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")

    if invoice.status_invoice == "Lunas":
        raise HTTPException(status_code=400, detail="Invoice ini sudah lunas.")

    # Set metode pembayaran dari input
    invoice.metode_pembayaran = payload.metode_pembayaran
    
    # Panggil fungsi logika pembayaran yang sudah ada
    # Kita tidak mengirim payload Xendit, jadi fungsi akan menggunakan waktu saat ini
    await _process_successful_payment(db, invoice)
    
    await db.commit()
    await db.refresh(invoice)
    
    logger.info(f"Invoice {invoice.invoice_number} ditandai lunas secara manual via {payload.metode_pembayaran}")
    
    return invoice



@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)):
    """Menghapus satu invoice berdasarkan ID-nya."""
    
    # Cari invoice di database
    db_invoice = await db.get(InvoiceModel, invoice_id)
    
    # Jika tidak ditemukan, kirim error 404
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    
    # Jika ditemukan, hapus dari database
    await db.delete(db_invoice)
    await db.commit()
    
    return None
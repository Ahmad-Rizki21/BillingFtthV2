# app/jobs.py

import logging
from datetime import date, timedelta
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import uuid

# --- Impor komponen yang diperlukan ---
from .database import AsyncSessionLocal as SessionLocal
from .models.langganan import Langganan as LanggananModel
from .models.invoice import Invoice as InvoiceModel
from .models.pelanggan import Pelanggan as PelangganModel
from .models.data_teknis import DataTeknis as DataTeknisModel
from .services import mikrotik_service, xendit_service

# --- Impor helper log yang baru ---
from .logging_config import log_scheduler_event

# --- Atur logger khusus untuk modul ini ---
logger = logging.getLogger('app.jobs')


async def generate_single_invoice(db, langganan: LanggananModel):
    """Fungsi bantuan untuk membuat satu invoice. Direfaktor dari router."""
    try:
        pelanggan = langganan.pelanggan
        paket = langganan.paket_layanan
        brand = pelanggan.harga_layanan
        data_teknis = pelanggan.data_teknis

        if not all([pelanggan, paket, brand, data_teknis]):
            logger.error(f"Data tidak lengkap untuk langganan ID {langganan.id}. Skip.")
            return

        total_harga = float(paket.harga) * (1 + (float(brand.pajak) / 100))

        new_invoice_data = {
            "invoice_number": f"INV-{date.today().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}",
            "pelanggan_id": pelanggan.id,
            "id_pelanggan": data_teknis.id_pelanggan,
            "brand": brand.brand,
            "total_harga": round(total_harga, 2),
            "no_telp": pelanggan.no_telp,
            "email": pelanggan.email,
            "tgl_invoice": date.today(),
            "tgl_jatuh_tempo": langganan.tgl_jatuh_tempo,
            "status_invoice": "Belum Dibayar",
        }

        db_invoice = InvoiceModel(**new_invoice_data)
        db.add(db_invoice)
        await db.flush()  # Gunakan flush untuk mendapatkan ID sebelum commit

        xendit_response = await xendit_service.create_xendit_invoice(db_invoice, pelanggan)

        db_invoice.payment_link = xendit_response.get("invoice_url")
        db_invoice.xendit_id = xendit_response.get("id")
        db_invoice.xendit_external_id = xendit_response.get("external_id")

        db.add(db_invoice)
        logger.info(f"✅ Invoice {db_invoice.invoice_number} berhasil dibuat untuk Langganan ID {langganan.id}")

    except Exception as e:
        logger.error(f"❌ Gagal membuat invoice untuk Langganan ID {langganan.id}: {e}")
        # Jangan re-raise error agar job lain bisa lanjut


async def job_generate_invoices():
    """Tugas untuk membuat invoice bagi langganan yang akan jatuh tempo 5 hari lagi."""
    log_scheduler_event(logger, 'job_generate_invoices', 'started')
    target_due_date = date.today() + timedelta(days=5)
    invoices_created = 0

    async with SessionLocal() as db:
        try:
            stmt = (
                select(LanggananModel)
                .where(
                    LanggananModel.tgl_jatuh_tempo == target_due_date,
                    LanggananModel.status == "Aktif"
                ).options(
                    selectinload(LanggananModel.pelanggan).selectinload(PelangganModel.harga_layanan),
                    selectinload(LanggananModel.pelanggan).selectinload(PelangganModel.data_teknis),
                    selectinload(LanggananModel.paket_layanan)
                )
            )
            subscriptions_to_invoice = (await db.execute(stmt)).scalars().all()

            if not subscriptions_to_invoice:
                log_scheduler_event(logger, 'job_generate_invoices', 'completed', "Tidak ada invoice untuk dibuat hari ini.")
                return

            for langganan in subscriptions_to_invoice:
                existing_invoice_stmt = (
                    select(InvoiceModel.id).where(
                        InvoiceModel.pelanggan_id == langganan.pelanggan_id,
                        InvoiceModel.tgl_jatuh_tempo == langganan.tgl_jatuh_tempo
                    )
                )
                existing_invoice = (await db.execute(existing_invoice_stmt)).scalar_one_or_none()

                if not existing_invoice:
                    await generate_single_invoice(db, langganan)
                    invoices_created += 1
                else:
                    logger.debug(f"Invoice untuk langganan ID {langganan.id} sudah ada, dilewati.")

            await db.commit()
            log_scheduler_event(logger, 'job_generate_invoices', 'completed', f"Berhasil membuat {invoices_created} invoice baru.")
        except Exception as e:
            await db.rollback()
            log_scheduler_event(logger, 'job_generate_invoices', 'failed', str(e))


async def job_suspend_services():
    """Tugas untuk menonaktifkan layanan yang telah melewati jatuh tempo."""
    log_scheduler_event(logger, 'job_suspend_services', 'started')
    services_suspended = 0

    async with SessionLocal() as db:
        try:
            stmt = (
                select(LanggananModel)
                .where(
                    LanggananModel.tgl_jatuh_tempo < date.today(),
                    LanggananModel.status == "Aktif"
                ).options(
                    selectinload(LanggananModel.pelanggan).selectinload(PelangganModel.data_teknis)
                )
            )
            overdue_subscriptions = (await db.execute(stmt)).scalars().all()

            if not overdue_subscriptions:
                log_scheduler_event(logger, 'job_suspend_services', 'completed', "Tidak ada layanan untuk di-suspend.")
                return

            for langganan in overdue_subscriptions:
                logger.warning(f"Melakukan suspend layanan untuk Langganan ID: {langganan.id} karena terlambat.")

                langganan.status = "Suspended"
                db.add(langganan)

                # Panggil service Mikrotik untuk update status pelanggan
                await mikrotik_service.trigger_mikrotik_update(db, langganan)
                services_suspended += 1

            await db.commit()
            log_scheduler_event(logger, 'job_suspend_services', 'completed', f"Berhasil suspend {services_suspended} layanan.")
        except Exception as e:
            await db.rollback()
            log_scheduler_event(logger, 'job_suspend_services', 'failed', str(e))
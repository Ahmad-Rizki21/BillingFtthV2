# app/jobs.py

import logging
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy.future import select
from sqlalchemy import update
from sqlalchemy.orm import selectinload
import uuid
import traceback
import math

# Impor komponen
from .database import AsyncSessionLocal as SessionLocal
from .models import (
    Langganan as LanggananModel,
    Invoice as InvoiceModel,
    Pelanggan as PelangganModel,
)
from .services import mikrotik_service, xendit_service
from .logging_config import log_scheduler_event
from .routers.invoice import _process_successful_payment

logger = logging.getLogger("app.jobs")


# Fungsi generate_single_invoice tetap sama, tidak perlu diubah
async def generate_single_invoice(db, langganan: LanggananModel):
    try:
        pelanggan = langganan.pelanggan
        paket = langganan.paket_layanan
        brand = pelanggan.harga_layanan
        data_teknis = pelanggan.data_teknis

        if not all([pelanggan, paket, brand, data_teknis]):
            logger.error(f"Data tidak lengkap untuk langganan ID {langganan.id}. Skip.")
            return

        harga_dasar = float(paket.harga)
        pajak_persen = float(brand.pajak)
        pajak_mentah = harga_dasar * (pajak_persen / 100)
        pajak = math.floor(pajak_mentah + 0.5)
        total_harga = harga_dasar + pajak

        new_invoice_data = {
            "invoice_number": f"INV-{date.today().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}",
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

        deskripsi_xendit = ""
        jatuh_tempo_str_lengkap = db_invoice.tgl_jatuh_tempo.strftime('%d/%m/%Y')

        if langganan.metode_pembayaran == 'Prorate':
            # ▼▼▼ LOGIKA BARU DIMULAI DI SINI ▼▼▼

            # Hitung harga normal untuk perbandingan
            harga_normal_full = float(paket.harga) * (1 + (float(brand.pajak) / 100))

            # Cek apakah ini invoice gabungan
            if db_invoice.total_harga > (harga_normal_full + 1):
                 # INI TAGIHAN GABUNGAN
                start_day = db_invoice.tgl_invoice.day
                end_day = db_invoice.tgl_jatuh_tempo.day
                periode_prorate_str = db_invoice.tgl_jatuh_tempo.strftime("%B %Y")
                periode_berikutnya_str = (db_invoice.tgl_jatuh_tempo + relativedelta(months=1)).strftime("%B %Y")
                
                deskripsi_xendit = (
                    f"Biaya internet up to {paket.kecepatan} Mbps. "
                    f"Periode Prorate {start_day}-{end_day} {periode_prorate_str} + "
                    f"Periode {periode_berikutnya_str}"
                )
            else:
                # INI TAGIHAN PRORATE BIASA
                start_day = db_invoice.tgl_invoice.day
                end_day = db_invoice.tgl_jatuh_tempo.day 
                periode_str = db_invoice.tgl_jatuh_tempo.strftime('%B %Y')
                deskripsi_xendit = (
                    f"Biaya berlangganan internet up to {paket.kecepatan} Mbps, "
                    f"Periode Tgl {start_day}-{end_day} {periode_str}"
                )
            
        else: # Otomatis
            deskripsi_xendit = (
                f"Biaya berlangganan internet up to {paket.kecepatan} Mbps "
                f"jatuh tempo pembayaran tanggal {jatuh_tempo_str_lengkap}"
            )

        no_telp_xendit = (
            f"+62{pelanggan.no_telp.lstrip('0')}" if pelanggan.no_telp else None
        )

        xendit_response = await xendit_service.create_xendit_invoice(
            db_invoice, pelanggan, paket, deskripsi_xendit, pajak, no_telp_xendit
        )

        db_invoice.payment_link = xendit_response.get(
            "short_url", xendit_response.get("invoice_url")
        )
        db_invoice.xendit_id = xendit_response.get("id")
        db_invoice.xendit_external_id = xendit_response.get("external_id")

        db.add(db_invoice)
        logger.info(
            f"Invoice {db_invoice.invoice_number} berhasil dibuat untuk Langganan ID {langganan.id}"
        )

    except Exception as e:
        logger.error(
            f"Gagal membuat invoice untuk Langganan ID {langganan.id}: {e}\n{traceback.format_exc()}"
        )


# ==========================================================
# --- JOB SCHEDULER YANG SUDAH DIOPTIMALKAN ---
# ==========================================================


async def job_generate_invoices():
    log_scheduler_event(logger, "job_generate_invoices", "started")
    target_due_date = date.today() + timedelta(days=5)
    total_invoices_created = 0
    BATCH_SIZE = 100
    offset = 0

    async with SessionLocal() as db:
        while True:
            try:
                base_stmt = (
                    select(LanggananModel)
                    .where(
                        LanggananModel.tgl_jatuh_tempo == target_due_date,
                        LanggananModel.status == "Aktif",
                    )
                    .options(
                        selectinload(LanggananModel.pelanggan).selectinload(
                            PelangganModel.harga_layanan
                        ),
                        selectinload(LanggananModel.pelanggan).selectinload(
                            PelangganModel.data_teknis
                        ),
                        selectinload(LanggananModel.paket_layanan),
                    )
                )

                batch_stmt = base_stmt.offset(offset).limit(BATCH_SIZE)
                subscriptions_batch = (
                    (await db.execute(batch_stmt)).scalars().unique().all()
                )

                if not subscriptions_batch:
                    break

                for langganan in subscriptions_batch:
                    existing_invoice_stmt = (
                        select(InvoiceModel.id)
                        .where(
                            InvoiceModel.pelanggan_id == langganan.pelanggan_id,
                            InvoiceModel.tgl_jatuh_tempo == langganan.tgl_jatuh_tempo,
                        )
                        .limit(1)
                    )
                    if not (
                        await db.execute(existing_invoice_stmt)
                    ).scalar_one_or_none():
                        await generate_single_invoice(db, langganan)
                        total_invoices_created += 1

                await db.commit()
                offset += BATCH_SIZE

            except Exception as e:
                await db.rollback()
                error_details = traceback.format_exc()
                logger.error(
                    f"[FAIL] Scheduler 'job_generate_invoices' failed at offset {offset}. Details:\n{error_details}"
                )
                break

    if total_invoices_created > 0:
        log_scheduler_event(
            logger,
            "job_generate_invoices",
            "completed",
            f"Berhasil membuat {total_invoices_created} invoice baru.",
        )
    else:
        log_scheduler_event(
            logger,
            "job_generate_invoices",
            "completed",
            "Tidak ada invoice baru yang perlu dibuat.",
        )


async def job_suspend_services():
    log_scheduler_event(logger, "job_suspend_services", "started")
    total_services_suspended = 0
    current_date = date.today()
    BATCH_SIZE = 50
    offset = 0

    async with SessionLocal() as db:
        while True:
            try:
                base_stmt = (
                    select(LanggananModel)
                    .join(
                        InvoiceModel,
                        LanggananModel.pelanggan_id == InvoiceModel.pelanggan_id,
                    )
                    .where(
                        LanggananModel.tgl_jatuh_tempo
                        <= current_date - timedelta(days=4),
                        LanggananModel.status == "Aktif",
                        InvoiceModel.status_invoice == "Belum Dibayar",
                    )
                    .options(
                        selectinload(LanggananModel.pelanggan).selectinload(
                            PelangganModel.data_teknis
                        )
                    )
                )

                batch_stmt = base_stmt.offset(offset).limit(BATCH_SIZE)
                overdue_batch = (await db.execute(batch_stmt)).scalars().unique().all()

                if not overdue_batch:
                    break

                for langganan in overdue_batch:
                    logger.warning(
                        f"Melakukan suspend layanan untuk Langganan ID: {langganan.id}..."
                    )
                    langganan.status = "Suspended"
                    db.add(langganan)
                    await mikrotik_service.trigger_mikrotik_update(db, langganan)

                await db.commit()
                total_services_suspended += len(overdue_batch)
                offset += BATCH_SIZE

            except Exception as e:
                await db.rollback()
                logger.error(
                    f"[FAIL] Scheduler 'job_suspend_services' failed at offset {offset}. Details: {traceback.format_exc()}"
                )
                break

    if total_services_suspended > 0:
        log_scheduler_event(
            logger,
            "job_suspend_services",
            "completed",
            f"Berhasil suspend {total_services_suspended} layanan.",
        )
    else:
        log_scheduler_event(
            logger,
            "job_suspend_services",
            "completed",
            "Tidak ada layanan baru untuk di-suspend.",
        )


async def job_send_payment_reminders():
    log_scheduler_event(logger, "job_send_payment_reminders", "started")
    total_reminders_sent = 0
    target_due_date = date.today() + timedelta(days=3)
    BATCH_SIZE = 100
    offset = 0

    async with SessionLocal() as db:
        while True:
            try:
                base_stmt = (
                    select(LanggananModel)
                    .where(
                        LanggananModel.tgl_jatuh_tempo == target_due_date,
                        LanggananModel.status == "Aktif",
                    )
                    .options(selectinload(LanggananModel.pelanggan))
                )

                batch_stmt = base_stmt.offset(offset).limit(BATCH_SIZE)
                reminder_batch = (await db.execute(batch_stmt)).scalars().unique().all()

                if not reminder_batch:
                    break

                for langganan in reminder_batch:
                    pelanggan = langganan.pelanggan
                    logger.info(
                        f"Mengirim pengingat pembayaran untuk pelanggan ID: {pelanggan.id} ({pelanggan.nama})"
                    )
                    # Di sini Anda bisa menambahkan logika pengiriman notifikasi (WA, Email, dll)
                    total_reminders_sent += 1

                # Tidak ada db.commit() karena kita hanya membaca data
                offset += BATCH_SIZE

            except Exception as e:
                logger.error(
                    f"[FAIL] Scheduler 'job_send_payment_reminders' failed at offset {offset}. Details: {traceback.format_exc()}"
                )
                break

    if total_reminders_sent > 0:
        log_scheduler_event(
            logger,
            "job_send_payment_reminders",
            "completed",
            f"Berhasil mengirim {total_reminders_sent} pengingat pembayaran.",
        )
    else:
        log_scheduler_event(
            logger,
            "job_send_payment_reminders",
            "completed",
            "Tidak ada pelanggan untuk dikirim pengingat hari ini.",
        )


async def job_verify_payments():
    """Job untuk rekonsiliasi pembayaran dan menandai invoice kedaluwarsa."""
    log_scheduler_event(logger, "job_verify_payments", "started")

    async with SessionLocal() as db:
        try:
            # Bagian 1: Tandai Invoice Kedaluwarsa (Batch Update) - Ini sudah efisien
            expired_stmt = (
                update(InvoiceModel)
                .where(
                    InvoiceModel.status_invoice == "Belum Dibayar",
                    InvoiceModel.tgl_jatuh_tempo < date.today() - timedelta(days=1),
                )
                .values(status_invoice="Kadaluarsa")
            )
            result = await db.execute(expired_stmt)
            if result.rowcount > 0:
                logger.info(
                    f"[VERIFY] Menandai {result.rowcount} invoice sebagai kedaluwarsa."
                )

            # Bagian 2: Rekonsiliasi Pembayaran Terlewat - Ini sudah efisien
            paid_invoice_ids = await xendit_service.get_paid_invoice_ids_since(days=3)

            if not paid_invoice_ids:
                log_scheduler_event(
                    logger,
                    "job_verify_payments",
                    "completed",
                    "Tidak ada pembayaran baru di Xendit.",
                )
                await db.commit()
                return

            unprocessed_stmt = select(InvoiceModel).where(
                InvoiceModel.xendit_external_id.in_(paid_invoice_ids),
                InvoiceModel.status_invoice == "Belum Dibayar",
            )
            invoices_to_process = (await db.execute(unprocessed_stmt)).scalars().all()

            processed_count = 0
            if invoices_to_process:
                logger.warning(
                    f"[VERIFY] Menemukan {len(invoices_to_process)} pembayaran terlewat. Memproses..."
                )
                for invoice in invoices_to_process:
                    await _process_successful_payment(db, invoice)
                    processed_count += 1

            await db.commit()
            log_scheduler_event(
                logger,
                "job_verify_payments",
                "completed",
                f"Memproses {processed_count} pembayaran terlewat.",
            )

        except Exception as e:
            await db.rollback()
            error_details = traceback.format_exc()
            logger.error(
                f"[FAIL] Scheduler 'job_verify_payments' failed. Details:\n{error_details}"
            )

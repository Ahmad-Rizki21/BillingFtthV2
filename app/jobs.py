# app/jobs.py

import logging
from datetime import date, timedelta
from sqlalchemy.future import select
from sqlalchemy import update
from sqlalchemy.orm import selectinload
import uuid
import traceback
import math

# Impor komponen
from .database import AsyncSessionLocal as SessionLocal
from .models import Langganan as LanggananModel, Invoice as InvoiceModel, Pelanggan as PelangganModel
from .services import mikrotik_service, xendit_service
from .logging_config import log_scheduler_event
from .routers.invoice import _process_successful_payment # Impor fungsi refaktor

logger = logging.getLogger('app.jobs')

async def generate_single_invoice(db, langganan: LanggananModel):
    try:
        pelanggan = langganan.pelanggan
        paket = langganan.paket_layanan
        brand = pelanggan.harga_layanan
        data_teknis = pelanggan.data_teknis

        if not all([pelanggan, paket, brand, data_teknis]):
            logger.error(f"Data tidak lengkap untuk langganan ID {langganan.id}. Skip.")
            return

        # --- PERBAIKAN FINAL ---
        
        # 1. Hitung harga dan pajak
        harga_dasar = float(paket.harga)
        pajak_persen = float(brand.pajak)

        # Hitung nilai pajak mentah
        pajak_mentah = harga_dasar * (pajak_persen / 100)

        # Lakukan pembulatan matematis standar (round half up) sesuai aturan finance
        pajak = math.floor(pajak_mentah + 0.5)

        # Total harga adalah harga dasar ditambah pajak yang sudah dibulatkan.
        total_harga = harga_dasar + pajak
        
        # --- PERBAIKAN PADA new_invoice_data ---
        new_invoice_data = {
            "invoice_number": f"INV-{date.today().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}",
            "pelanggan_id": pelanggan.id,
            "id_pelanggan": data_teknis.id_pelanggan,
            "brand": brand.brand,
            "total_harga": total_harga, # Menggunakan total_harga yang sudah dihitung dengan benar
            "no_telp": pelanggan.no_telp,
            "email": pelanggan.email,
            "tgl_invoice": date.today(),
            "tgl_jatuh_tempo": langganan.tgl_jatuh_tempo,
            "status_invoice": "Belum Dibayar",
        }

        db_invoice = InvoiceModel(**new_invoice_data)
        db.add(db_invoice)
        await db.flush()

        # 2. Siapkan deskripsi dan format nomor telepon untuk Xendit
        jatuh_tempo_str = db_invoice.tgl_jatuh_tempo.strftime('%d/%m/%Y')
        deskripsi_xendit = f"Biaya berlangganan internet up to {paket.kecepatan} Mbps jatuh tempo pembayaran tanggal {jatuh_tempo_str}"
        no_telp_xendit = f"+62{pelanggan.no_telp.lstrip('0')}" if pelanggan.no_telp else None
        
        # 3. Panggil service Xendit dengan argumen yang lengkap
        xendit_response = await xendit_service.create_xendit_invoice(
            db_invoice, 
            pelanggan, 
            paket, 
            deskripsi_xendit,
            pajak,
            no_telp_xendit
        )

        db_invoice.payment_link = xendit_response.get("short_url", xendit_response.get("invoice_url"))
        db_invoice.xendit_id = xendit_response.get("id")
        db_invoice.xendit_external_id = xendit_response.get("external_id")

        db.add(db_invoice)
        logger.info(f"Invoice {db_invoice.invoice_number} berhasil dibuat untuk Langganan ID {langganan.id}")

    except Exception as e:
        import traceback
        logger.error(f"Gagal membuat invoice untuk Langganan ID {langganan.id}: {e}\n{traceback.format_exc()}")

async def job_suspend_services():
    log_scheduler_event(logger, 'job_suspend_services', 'started')
    services_suspended = 0
    current_date = date.today()

    async with SessionLocal() as db:
        try:
            stmt = (
                select(LanggananModel)
                .join(InvoiceModel, LanggananModel.pelanggan_id == InvoiceModel.pelanggan_id)
                .where(
                    # LanggananModel.tgl_jatuh_tempo < current_date, #ini Logic Suspend di tanggal 2
                    LanggananModel.tgl_jatuh_tempo <= current_date - timedelta(days=4), # ini Logic Suspend di tanggal 5
                    LanggananModel.status == "Aktif",
                    InvoiceModel.status_invoice == "Belum Dibayar"
                ).options(
                    selectinload(LanggananModel.pelanggan).selectinload(PelangganModel.data_teknis)
                )
            )
            overdue_subscriptions = (await db.execute(stmt)).scalars().all()

            if not overdue_subscriptions:
                log_scheduler_event(logger, 'job_suspend_services', 'completed', "Tidak ada layanan untuk di-suspend.")
                return

            for langganan in overdue_subscriptions:
                logger.info(f"LOOP SAAT INI UNTUK: Langganan ID {langganan.id}, User PPPoE: {langganan.pelanggan.data_teknis.id_pelanggan}")
                logger.warning(f"Melakukan suspend layanan untuk Langganan ID: {langganan.id} karena terlambat pada {current_date}.")
                langganan.status = "Suspended"
                db.add(langganan)
                await mikrotik_service.trigger_mikrotik_update(db, langganan)
                services_suspended += 1
            
            await db.commit()
            log_scheduler_event(logger, 'job_suspend_services', 'completed', f"Berhasil suspend {services_suspended} layanan.")
        except Exception as e:
            await db.rollback()
            log_scheduler_event(logger, 'job_suspend_services', 'failed', str(e))

async def job_verify_payments():
    """Job untuk rekonsiliasi pembayaran dan menandai invoice kedaluwarsa."""
    log_scheduler_event(logger, 'job_verify_payments', 'started')
    
    async with SessionLocal() as db:
        try:
            # Bagian 1: Tandai Invoice Kedaluwarsa (Batch Update)
            expired_stmt = (
                update(InvoiceModel)
                .where(
                    InvoiceModel.status_invoice == "Belum Dibayar",
                    InvoiceModel.tgl_jatuh_tempo < date.today() - timedelta(days=1)
                )
                .values(status_invoice="Kadaluarsa")
            )
            result = await db.execute(expired_stmt)
            if result.rowcount > 0:
                logger.info(f"[VERIFY] Menandai {result.rowcount} invoice sebagai kedaluwarsa.")

            # Bagian 2: Rekonsiliasi Pembayaran Terlewat (Batch API & SELECT)
            paid_invoice_ids = await xendit_service.get_paid_invoice_ids_since(days=3)

            if not paid_invoice_ids:
                log_scheduler_event(logger, 'job_verify_payments', 'completed', "Tidak ada pembayaran baru di Xendit.")
                await db.commit()
                return

            unprocessed_stmt = (
                select(InvoiceModel)
                .where(
                    InvoiceModel.xendit_external_id.in_(paid_invoice_ids),
                    InvoiceModel.status_invoice == "Belum Dibayar"
                )
            )
            invoices_to_process = (await db.execute(unprocessed_stmt)).scalars().all()

            processed_count = 0
            if invoices_to_process:
                logger.warning(f"[VERIFY] Menemukan {len(invoices_to_process)} pembayaran terlewat. Memproses...")
                for invoice in invoices_to_process:
                    await _process_successful_payment(db, invoice)
                    processed_count += 1
            
            await db.commit()
            log_scheduler_event(logger, 'job_verify_payments', 'completed', f"Memproses {processed_count} pembayaran terlewat.")
            
        except Exception as e:
            await db.rollback()
            error_details = traceback.format_exc()
            logger.error(f"[FAIL] Scheduler 'job_verify_payments' failed. Details:\n{error_details}")

async def job_generate_invoices():
    log_scheduler_event(logger, 'job_generate_invoices', 'started')
    # Penyesuaian: Job ini seharusnya berjalan setiap hari untuk H-5,
    # jadi kita gunakan tanggal hari ini untuk kalkulasi.
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
            subscriptions_to_invoice = (await db.execute(stmt)).scalars().unique().all()

            if not subscriptions_to_invoice:
                log_scheduler_event(logger, 'job_generate_invoices', 'completed', "Tidak ada invoice untuk dibuat hari ini.")
                return

            for langganan in subscriptions_to_invoice:
                # Cek apakah invoice untuk periode ini sudah ada
                existing_invoice_stmt = (
                    select(InvoiceModel.id).where(
                        InvoiceModel.pelanggan_id == langganan.pelanggan_id,
                        InvoiceModel.tgl_jatuh_tempo == langganan.tgl_jatuh_tempo
                    ).limit(1)
                )
                existing_invoice = (await db.execute(existing_invoice_stmt)).scalar_one_or_none()

                if not existing_invoice:
                    await generate_single_invoice(db, langganan)
                    invoices_created += 1
                else:
                    logger.debug(f"Invoice untuk langganan ID {langganan.id} dengan jatuh tempo {langganan.tgl_jatuh_tempo} sudah ada, dilewati.")
            
            await db.commit()
            if invoices_created > 0:
                log_scheduler_event(logger, 'job_generate_invoices', 'completed', f"Berhasil membuat {invoices_created} invoice baru.")
            else:
                log_scheduler_event(logger, 'job_generate_invoices', 'completed', "Tidak ada invoice baru yang perlu dibuat (semua sudah ada).")

        except Exception as e:
            await db.rollback()
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"[FAIL] Scheduler 'job_generate_invoices' failed. Details:\n{error_details}")

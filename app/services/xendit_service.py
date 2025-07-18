# app/services/xendit_service.py

import httpx
from ..config import settings
from ..models import Invoice, Pelanggan
import os
import base64
import logging
import urllib.parse
from datetime import datetime, timedelta, timezone

logger = logging.getLogger('app.services.xendit')

async def create_xendit_invoice(invoice: Invoice, pelanggan: Pelanggan) -> dict:
    """Mengirim request ke Xendit untuk membuat invoice baru."""
    target_key_name = pelanggan.harga_layanan.xendit_key_name
    api_key = settings.XENDIT_API_KEYS.get(target_key_name)
    if not api_key:
        raise ValueError(f"Kunci API Xendit untuk '{target_key_name}' tidak ditemukan.")

    encoded_key = base64.b64encode(f"{api_key}:".encode('utf-8')).decode('utf-8')
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {encoded_key}"
    }

    payload = {
        "external_id": invoice.invoice_number,
        "amount": float(invoice.total_harga),
        "description": f"Tagihan Internet untuk {pelanggan.nama} - Invoice {invoice.invoice_number}",
        "invoice_duration": 86400 * 7, # Durasi 7 hari
        "customer": {
            "given_names": pelanggan.nama,
            "email": pelanggan.email,
            "mobile_number": pelanggan.no_telp
        },
        "currency": "IDR",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(settings.XENDIT_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Error saat membuat invoice Xendit: {e.response.text}")
            raise

async def get_paid_invoice_ids_since(days: int) -> list[str]:
    """
    Mengambil daftar external_id dari semua invoice yang statusnya PAID
    sejak beberapa hari yang lalu dari Xendit (Batch API Call).
    """
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    
    api_key = settings.XENDIT_API_KEYS.get("JAKINET")
    if not api_key:
        logger.error("Kunci API Xendit default tidak ditemukan untuk verifikasi.")
        return []

    encoded_key = base64.b64encode(f"{api_key}:".encode('utf-8')).decode('utf-8')
    headers = {"Authorization": f"Basic {encoded_key}"}
    
    # ==========================================================
    # --- PERUBAHAN UTAMA ADA DI SINI ---
    # ==========================================================
    
    # Kita tidak lagi menggunakan dict 'params' untuk httpx,
    # karena formatting array-nya tidak sesuai harapan Xendit.
    # Kita akan membangun query string secara manual.
    
    base_url = "https://api.xendit.co/v2/invoices"
    query_params = {
        "statuses[]": "PAID", # Gunakan 'statuses[]' untuk menandakan array
        "paid_after": start_date,
        "limit": 1000
    }
    
    # Gunakan urllib untuk encode parameter dengan benar
    encoded_params = urllib.parse.urlencode(query_params)
    full_url = f"{base_url}?{encoded_params}"

    # ==========================================================

    async with httpx.AsyncClient() as client:
        try:
            # Panggil URL yang sudah diformat dengan benar
            response = await client.get(full_url, headers=headers)
            response.raise_for_status()
            invoices_data = response.json()
            return [inv.get("external_id") for inv in invoices_data if inv.get("external_id")]
        except httpx.HTTPStatusError as e:
            logger.error(f"Error saat mengambil data dari Xendit: {e.response.text}")
            return []

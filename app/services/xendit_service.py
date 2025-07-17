import httpx
from ..config import settings
from ..models import Invoice, Pelanggan
import os
import base64


async def create_xendit_invoice(invoice: Invoice, pelanggan: Pelanggan) -> dict:
    """
    Mengirim request ke Xendit untuk membuat invoice baru.
    """
    # Tentukan kunci API mana yang akan digunakan berdasarkan brand invoice
    api_key = settings.XENDIT_API_KEYS.get(invoice.brand)
    if not api_key:
        raise ValueError(f"Kunci API Xendit untuk brand '{invoice.brand}' tidak ditemukan.")

    # Siapkan header dengan autentikasi Basic Auth (username adalah kunci API, password kosong)
    headers = {
        "Content-Type": "application/json",
        "Authorization": api_key
    }

    # Siapkan data payload sesuai dokumentasi Xendit
    payload = {
        "external_id": invoice.invoice_number,
        "amount": float(invoice.total_harga),
        "description": f"Tagihan Internet untuk {pelanggan.nama} - Invoice {invoice.invoice_number}",
        "invoice_duration": 86400,  # Durasi invoice dalam detik (contoh: 1 hari)
        "customer": {
            "given_names": pelanggan.nama,
            "email": pelanggan.email,
            "mobile_number": pelanggan.no_telp
        },
        "currency": "IDR",
    }

    # Kirim request menggunakan httpx (library modern untuk http request)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(settings.XENDIT_API_URL, json=payload, headers=headers)
            response.raise_for_status()  # Ini akan raise error jika status code bukan 2xx
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error saat membuat invoice Xendit: {e.response.text}")
            raise  # Melempar kembali error untuk ditangani di router


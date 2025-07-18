import os
import base64
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Memuat variabel dari .env secara eksplisit
load_dotenv()

class Settings(BaseSettings):
    # --- TAMBAHKAN DUA BARIS INI ---
    DATABASE_URL: str
    XENDIT_CALLBACK_TOKEN: str
    # --------------------------------

    # Deklarasi yang sudah ada
    XENDIT_API_KEY_JAKINET: str
    XENDIT_API_KEY_JELANTIK: str
    XENDIT_API_URL: str = "https://api.xendit.co/v2/invoices"

    @property
    def XENDIT_API_KEYS(self) -> dict:
        return {
            "JAKINET": self.XENDIT_API_KEY_JAKINET,
            "JELANTIK": self.XENDIT_API_KEY_JELANTIK,
        }
    
    # Fungsi _encode_api_key tidak perlu diubah, karena sudah tidak digunakan di @property
    # Namun, jika Anda ingin tetap menggunakannya, pastikan memanggil self._encode_api_key()

    class Config:
        env_file = ".env"

settings = Settings()
# app/config.py
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import List

load_dotenv()


class Settings(BaseSettings):
    # --- PERPINDAHAN VARIABEL MENUS ---
    # Pindahkan MENUS ke sini
    MENUS: List[str] = [
        "Pelanggan",
        "Langganan",
        "Data Teknis",
        "Brand & Paket",
        "Invoices",
        "Mikrotik Servers",
        "Users",
        "Roles",
        "Permissions",
        "S&K",
        "Simulasi Harga",
        "Kelola S&K",
    ]
    # -----------------------------------

    DATABASE_URL: str
    XENDIT_CALLBACK_TOKEN_ARTACOMINDO: str
    XENDIT_CALLBACK_TOKEN_JELANTIK: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    XENDIT_API_KEY_JAKINET: str
    XENDIT_API_KEY_JELANTIK: str
    XENDIT_API_URL: str = "https://api.xendit.co/v2/invoices"

    @property
    def XENDIT_API_KEYS(self) -> dict:
        return {
            "JAKINET": self.XENDIT_API_KEY_JAKINET,
            "JELANTIK": self.XENDIT_API_KEY_JELANTIK,
        }

    @property
    def XENDIT_CALLBACK_TOKENS(self) -> dict:
        return {
            "ARTACOMINDO": self.XENDIT_CALLBACK_TOKEN_ARTACOMINDO,
            "JELANTIK": self.XENDIT_CALLBACK_TOKEN_JELANTIK,
        }

    class Config:
        env_file = ".env"


settings = Settings()

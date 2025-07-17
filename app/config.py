import os
import base64
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    XENDIT_API_URL: str = "https://api.xendit.co/v2/invoices"

    @property
    def XENDIT_API_KEYS(self) -> dict:
        return {
            "Jakinet": self._encode_api_key(os.getenv("XENDIT_API_KEY_JAKINET")),
            "Jelantik": self._encode_api_key(os.getenv("XENDIT_API_KEY_JELANTIK")),
        }

    def _encode_api_key(self, key: str) -> str:
        return "Basic " + base64.b64encode(f"{key}:".encode()).decode()

settings = Settings()

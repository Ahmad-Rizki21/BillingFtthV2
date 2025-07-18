# app/logging_config.py

import logging
import logging.config
import sys
from pathlib import Path

# --- Fungsi Bantuan untuk Logging Terstruktur ---

def log_scheduler_event(logger, job_name: str, status: str, details: str = ""):
    status_map = {"started": "[START]", "completed": "[DONE]", "failed": "[FAIL]"}
    message = f"{status_map.get(status, '[INFO]')} Scheduler '{job_name}' {status}. {details}".strip()
    if status == "failed":
        logger.error(message)
    else:
        logger.info(message)

def log_mikrotik_operation(logger, operation: str, customer_id: str, status: str):
    icon_map = {"success": "✅", "failed": "❌", "info": "🛜"}
    message = f"{icon_map.get(status, '⚙️')} Mikrotik | {operation} untuk '{customer_id}'"
    if status == "failed":
        logger.error(message)
    else:
        logger.info(message)

def log_payment_event(logger, event: str, invoice_id: str, details: str = ""):
    message = f"💳 Pembayaran {event} untuk Invoice ID: {invoice_id}. {details}".strip()
    logger.info(message)


# --- Konfigurasi Inti Logging ---

class ColoredFormatter(logging.Formatter):
    """Formatter khusus dengan warna untuk terminal."""
    COLORS = {
        'DEBUG': '\033[94m',    # Biru
        'INFO': '\033[92m',     # Hijau
        'WARNING': '\033[93m',  # Kuning
        'ERROR': '\033[91m',    # Merah
        'CRITICAL': '\033[95m', # Ungu
        'RESET': '\033[0m'
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        record.levelname = f"{color}{record.levelname:<8}{reset}"
        # Membuat nama modul lebih pendek dan mudah dibaca
        record.name = record.name.replace('app.', '').upper()
        return super().format(record)

def setup_logging():
    """Mengatur konfigurasi logging untuk seluruh aplikasi."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'colored': {
                '()': ColoredFormatter,
                'format': '%(asctime)s | %(name)-12s | %(levelname)s | %(message)s',
                'datefmt': '%H:%M:%S'
            },
            'detailed': {
                'format': '%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'colored',
                'stream': sys.stdout,
            },
            'file_app': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filename': log_dir / 'app.log',
                'maxBytes': 5 * 1024 * 1024, # 5 MB
                'backupCount': 3
            },
            'file_error': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': log_dir / 'errors.log',
                'maxBytes': 5 * 1024 * 1024, # 5 MB
                'backupCount': 3
            }
        },
        'loggers': {
            'app': {
                'handlers': ['console', 'file_app', 'file_error'],
                'level': 'INFO',
                'propagate': False
            },
            # --- Perubahan Kunci: Mengurangi log yang berisik ---
            'sqlalchemy.engine': {
                'handlers': ['console', 'file_app'],
                'level': 'WARNING', # Hanya tampilkan warning dan error
                'propagate': False
            },
            'apscheduler': {
                'handlers': ['console', 'file_app'],
                'level': 'WARNING', # Hanya tampilkan warning dan error
                'propagate': False
            },
            'uvicorn': {
                'handlers': ['console', 'file_app'],
                'level': 'INFO',
                'propagate': False,
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console', 'file_app', 'file_error']
        }
    }
    logging.config.dictConfig(logging_config)
    logger = logging.getLogger('app.main')
    logger.info("=" * 40)
    logger.info("🚀 Sistem logging berhasil diinisialisasi!")
    logger.info(f"File log disimpan di: {log_dir.absolute()}")
    logger.info("=" * 40)
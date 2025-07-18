# app/logging_config.py

import logging
import logging.config
import sys
from pathlib import Path

# --- Helper Functions for Structured Logging (NO EMOJIS) ---

def log_scheduler_event(logger, job_name: str, status: str, details: str = ""):
    status_map = {"started": "[START]", "completed": "[DONE]", "failed": "[FAIL]"}
    message = f"{status_map.get(status, '[INFO]')} Scheduler '{job_name}' {status}. {details}".strip()
    if status == "failed":
        logger.error(message)
    else:
        logger.info(message)

def log_mikrotik_operation(logger, operation: str, customer_id: str, status: str):
    status_map = {"success": "[OK]", "failed": "[FAIL]", "info": "[INFO]"}
    message = f"{status_map.get(status, '[OP]')} Mikrotik | {operation} for '{customer_id}'"
    if status == "failed":
        logger.error(message)
    else:
        logger.info(message)

def log_payment_event(logger, event: str, invoice_id: str, details: str = ""):
    message = f"[PAYMENT] {event} for Invoice ID: {invoice_id}. {details}".strip()
    logger.info(message)


# --- Core Logging Setup ---

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',
        'INFO': '\033[92m',
        'WARNING': '\033[93m',
        'ERROR': '\033[91m',
        'CRITICAL': '\033[95m',
        'RESET': '\033[0m'
    }
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        record.levelname = f"{color}{record.levelname:<8}{reset}"
        record.name = record.name.replace('app.', '').upper()
        return super().format(record)

def setup_logging():
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
                'maxBytes': 5 * 1024 * 1024,
                'backupCount': 3
            },
            'file_error': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': log_dir / 'errors.log',
                'maxBytes': 5 * 1024 * 1024,
                'backupCount': 3
            }
        },
        'loggers': {
            'app': {'handlers': ['console', 'file_app', 'file_error'], 'level': 'INFO', 'propagate': False},
            'sqlalchemy.engine': {'handlers': ['file_app'], 'level': 'ERROR', 'propagate': False},
            'apscheduler': {'handlers': ['console', 'file_app'], 'level': 'WARNING', 'propagate': False},
            'uvicorn': {'handlers': ['console', 'file_app'], 'level': 'INFO', 'propagate': False}
        },
        'root': {'level': 'INFO', 'handlers': ['console', 'file_app', 'file_error']}
    }
    logging.config.dictConfig(logging_config)
    logger = logging.getLogger('app.main')
    logger.info("========================================")
    logger.info("Sistem logging berhasil diinisialisasi!")
    logger.info(f"File log disimpan di: {log_dir.absolute()}")
    logger.info("========================================")
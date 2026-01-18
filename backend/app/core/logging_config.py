"""
Modulo: logging_config.py
Descrizione: Configurazione sistema di logging strutturato
Autore: Claude per Davide
Data: 2026-01-15
"""

import logging
import os
import sys
from pathlib import Path
from pythonjsonlogger import jsonlogger

from app.core.config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter per logging strutturato.
    Aggiunge campi custom ai log JSON.
    """

    def add_fields(self, log_record, record, message_dict):
        """Aggiunge campi custom al log record"""
        super().add_fields(log_record, record, message_dict)

        # Aggiungi timestamp sempre
        log_record["timestamp"] = self.formatTime(record, self.datefmt)

        # Aggiungi livello di log
        log_record["level"] = record.levelname

        # Aggiungi nome del logger
        log_record["logger"] = record.name

        # Aggiungi file e line number
        log_record["file"] = record.filename
        log_record["line"] = record.lineno

        # Aggiungi function name
        log_record["function"] = record.funcName

        # Aggiungi environment
        log_record["environment"] = settings.ENVIRONMENT


def setup_logging():
    """
    Configura il sistema di logging dell'applicazione.

    Features:
    - Logging strutturato JSON in production
    - Logging human-readable in development
    - File rotation per log files
    - Livelli di log configurabili
    - Console e file output

    Note: In CI environment, skippa file logging per evitare permission issues
    """

    # Check if running in CI environment (GitHub Actions, GitLab CI, etc.)
    is_ci = os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true"

    # In CI, usa solo console logging (no file logging)
    if is_ci:
        logging.basicConfig(
            level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            stream=sys.stdout,
        )
        logger = logging.getLogger(__name__)
        logger.info("Logging configured for CI environment (console only)")
        return

    # Crea directory log se non esiste (solo in non-CI environments)
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Determina formato log
    if settings.LOG_FORMAT == "json":
        # JSON formatter per production
        formatter = CustomJsonFormatter(
            fmt="%(timestamp)s %(level)s %(logger)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    else:
        # Text formatter per development (più leggibile)
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # Rimuovi handlers esistenti per evitare duplicati
    root_logger.handlers.clear()

    # Console handler (sempre attivo)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    root_logger.addHandler(console_handler)

    # File handler per log completi
    file_handler = logging.FileHandler(log_dir / "application.log")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)

    # File handler per errori (separato)
    error_handler = logging.FileHandler(log_dir / "errors.log")
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_handler)

    # Configura logging per librerie esterne (riduci verbosità)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("stripe").setLevel(logging.INFO)

    # Log configurazione completata
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured",
        extra={
            "log_level": settings.LOG_LEVEL,
            "log_format": settings.LOG_FORMAT,
            "log_dir": str(log_dir),
        },
    )


if __name__ == "__main__":
    # Test logging configuration
    setup_logging()

    logger = logging.getLogger(__name__)

    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    logger.critical("This is a CRITICAL message")

    # Test con extra fields
    logger.info(
        "User action",
        extra={
            "user_id": "123",
            "action": "login",
            "ip_address": "192.168.1.1",
        },
    )

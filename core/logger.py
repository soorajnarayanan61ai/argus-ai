"""
Enterprise Logging System for ARGUS AI Platform.
Features console logging, rotating file logging, and an in-memory buffer for UI display.
"""
import logging
import io
from logging.handlers import RotatingFileHandler
from pathlib import Path
from config.settings import settings


class UILogHandler(logging.Handler):
    """Custom log handler capturing logs into an in-memory string stream for UI display."""
    
    def __init__(self, capacity: int = 500):
        super().__init__()
        self.capacity = capacity
        self.log_records = []

    def emit(self, record):
        log_entry = self.format(record)
        self.log_records.append(log_entry)
        if len(self.log_records) > self.capacity:
            self.log_records.pop(0)

    def get_logs(self) -> str:
        return "\n".join(reversed(self.log_records))


class LoggerManager:
    """Singleton Logger Manager."""

    _logger = None
    _ui_handler = None

    @classmethod
    def get_logger(cls, name: str = "ARGUS_AI") -> logging.Logger:
        if cls._logger is None:
            cls._setup_logger(name)
        return cls._logger

    @classmethod
    def get_ui_logs(cls) -> str:
        if cls._ui_handler:
            return cls._ui_handler.get_logs()
        return "No logs captured yet."

    @classmethod
    def _setup_logger(cls, name: str) -> None:
        logger = logging.getLogger(name)
        log_level_str = settings.get("logging.level", "INFO").upper()
        log_level = getattr(logging, log_level_str, logging.INFO)
        logger.setLevel(log_level)

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s:%(filename)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # 1. Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        logger.addHandler(console_handler)

        # 2. Rotating File Handler
        log_dir = Path(settings.base_dir) / settings.get("logging.log_dir", "logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / settings.get("logging.file_name", "argus_app.log")
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=settings.get("logging.max_bytes", 10485760),
            backupCount=settings.get("logging.backup_count", 5),
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        logger.addHandler(file_handler)

        # 3. UI In-Memory Stream Handler
        cls._ui_handler = UILogHandler(capacity=300)
        cls._ui_handler.setFormatter(formatter)
        cls._ui_handler.setLevel(log_level)
        logger.addHandler(cls._ui_handler)

        cls._logger = logger
        logger.info("ARGUS AI Logger initialized successfully.")


# Convenience logger instance
logger = LoggerManager.get_logger()

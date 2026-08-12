"""
Enterprise Configuration Manager for ARGUS AI Platform.
Loads configuration from YAML file with environment variable override support.
"""
import os
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from pathlib import Path
from typing import Any, Dict


class Settings:
    """Singleton Configuration Manager."""
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        
        self.base_dir = Path(__file__).resolve().parent.parent
        self.config_path = self.base_dir / "config" / "config.yaml"
        self._config_data: Dict[str, Any] = {}
        self.load_config()
        self._ensure_directories()
        self._initialized = True

    def load_config(self) -> None:
        """Load configuration from config.yaml or set defaults."""
        if HAS_YAML and self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self._config_data = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"[Warning] Failed to read config.yaml: {e}. Using fallback defaults.")
                self._config_data = self._get_default_config()
        else:
            self._config_data = self._get_default_config()


    def _get_default_config(self) -> Dict[str, Any]:
        """Fallback default dictionary."""
        return {
            "app": {
                "name": "ARGUS AI",
                "tagline": "Enterprise AI Data Analyst Platform",
                "version": "1.0.0",
                "environment": "production",
                "debug": False,
            },
            "theme": {
                "default_theme": "dark",
                "primary_color": "#6366f1",
                "secondary_color": "#8b5cf6",
                "background_dark": "#0f172a",
                "card_bg_dark": "rgba(30, 41, 59, 0.7)",
                "text_dark": "#f8fafc",
            },
            "database": {
                "dialect": "sqlite",
                "database_path": "data/argus_enterprise.db",
                "echo": False,
                "pool_size": 10,
                "max_overflow": 20,
            },
            "logging": {
                "level": "INFO",
                "log_dir": "logs",
                "file_name": "argus_app.log",
                "max_bytes": 10485760,
                "backup_count": 5,
            },
            "session": {
                "max_file_size_mb": 200,
                "cache_timeout_seconds": 3600,
                "default_currency": "USD",
            },
            "storage": {
                "upload_dir": "data/uploads",
                "exports_dir": "data/exports",
                "cache_dir": "data/cache",
            },
        }

    def _ensure_directories(self) -> None:
        """Create storage, data, and log directories if they do not exist."""
        dirs_to_create = [
            self.base_dir / "data",
            self.base_dir / self.get("storage.upload_dir", "data/uploads"),
            self.base_dir / self.get("storage.exports_dir", "data/exports"),
            self.base_dir / self.get("storage.cache_dir", "data/cache"),
            self.base_dir / self.get("logging.log_dir", "logs"),
        ]
        for d in dirs_to_create:
            d.mkdir(parents=True, exist_ok=True)

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get config value using dot-notation (e.g., 'database.database_path').
        Checks environment variables first (e.g. ARGUS_DATABASE_DATABASE_PATH).
        """
        env_key = "ARGUS_" + key_path.upper().replace(".", "_")
        if env_key in os.environ:
            return os.environ[env_key]

        keys = key_path.split(".")
        val = self._config_data
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val

    @property
    def database_url(self) -> str:
        """Construct SQLAlchemy database connection URL."""
        db_path = self.get("database.database_path", "data/argus_enterprise.db")
        abs_db_path = (self.base_dir / db_path).resolve()
        return f"sqlite:///{abs_db_path}"


# Global settings singleton
settings = Settings()

"""
SQLAlchemy Database Connection Layer for ARGUS AI Platform.
Targeting SQLite with connection pooling, health diagnostics, and session management.
"""
from sqlalchemy import create_engine, text, MetaData, Column, Integer, String, DateTime, Float
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from config.settings import settings
from core.logger import logger
from core.exceptions import DatabaseException

Base = declarative_base()


class DatasetMetadataModel(Base):
    """System table tracking imported datasets."""
    __tablename__ = "argus_dataset_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    row_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    file_size_bytes = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class DatabaseManager:
    """Singleton Database Connection & Session Manager."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        db_url = settings.database_url
        logger.info(f"Initializing Database Engine targeting: {db_url}")
        
        try:
            self.engine = create_engine(
                db_url,
                echo=settings.get("database.echo", False),
                future=True
            )
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            self._create_tables()
            self._initialized = True
            logger.info("Database Manager initialized and tables created.")
        except Exception as e:
            logger.error(f"Failed to initialize Database engine: {e}")
            raise DatabaseException(f"Database Initialization Error: {str(e)}")

    def _create_tables(self) -> None:
        """Create all declarative tables if they do not exist."""
        try:
            Base.metadata.create_all(bind=self.engine)
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")

    def get_session(self):
        """Provide a transactional scope around a series of operations."""
        return self.SessionLocal()

    def check_health(self) -> dict:
        """Execute diagnostic query to verify SQLite database health."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1")).scalar()
                db_path = settings.get("database.database_path", "data/argus_enterprise.db")
                return {
                    "status": "Healthy" if result == 1 else "Degraded",
                    "dialect": self.engine.dialect.name,
                    "database_path": str(db_path),
                    "connected": True
                }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "Unhealthy",
                "error": str(e),
                "connected": False
            }


# Singleton database instance
db_manager = DatabaseManager()

"""
Modules package for ARGUS AI Platform.
"""
from modules.base_module import BaseModule
from modules.home.view import HomeModule
from modules.file_loader.view import FileLoaderModule
from modules.db_connectors.view import DBConnectorsModule
from modules.ocr.view import OCRModule
from modules.cleaning.view import DataCleaningModule
from modules.profiling.view import ProfilingModule
from modules.analytics.view import AnalyticsModule
from modules.visualization.view import VisualizationModule
from modules.settings.view import SettingsModule

__all__ = [
    "BaseModule",
    "HomeModule",
    "FileLoaderModule",
    "DBConnectorsModule",
    "OCRModule",
    "DataCleaningModule",
    "ProfilingModule",
    "AnalyticsModule",
    "VisualizationModule",
    "SettingsModule",
]

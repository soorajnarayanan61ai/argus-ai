"""
Automated Test Suite for ARGUS AI Platform Engines.
Tests config, database, logging, file loader, data cleaning, profiling, analytics, visualization, and plugin manager.
"""
import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Ensure root dir is in path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config.settings import settings
from core.database import db_manager
from core.logger import LoggerManager, logger
from core.plugin_manager import plugin_manager
from services.file_service import FileIngestionService
from services.db_service import DatabaseConnectorService
from services.cleaning_service import DataCleaningService
from services.profiling_service import DataProfilingService
from services.analytics_service import AnalyticsService
from services.visualization_service import VisualizationService
from modules.home import HomeModule


class TestArgusPlatformEngine(unittest.TestCase):

    def test_01_configuration_manager(self):
        self.assertEqual(settings.get("app.name"), "ARGUS AI")
        self.assertIsNotNone(settings.database_url)

    def test_02_database_connection(self):
        health = db_manager.check_health()
        self.assertTrue(health["connected"])
        self.assertEqual(health["status"], "Healthy")

    def test_03_logger_manager(self):
        logger.info("Test log line for verification")
        logs = LoggerManager.get_ui_logs()
        self.assertIn("Test log line for verification", logs)

    def test_04_file_loader_csv_json(self):
        csv_bytes = b"id,name,amount\n1,Alice,$100.00\n2,Bob,$200.00\n"
        df = FileIngestionService._parse_csv(csv_bytes)
        self.assertEqual(len(df), 2)
        self.assertIn("amount", df.columns)

    def test_05_data_cleaning_engine(self):
        raw_df = pd.DataFrame({
            "item": ["A", "A", "B", "C"],
            "val": [10, 10, None, 40],
            "price": ["$10.50", "$10.50", "$20.00", "$30.00"]
        })
        # Remove duplicates
        df_no_dup = DataCleaningService.remove_duplicates(raw_df)
        self.assertEqual(len(df_no_dup), 3)

        # Impute missing values
        df_imp = DataCleaningService.impute_missing_values(df_no_dup, column="val", strategy="mean")
        self.assertFalse(df_imp["val"].isnull().any())

        # Clean currency
        df_curr = DataCleaningService.clean_currency_column(df_imp, column="price")
        self.assertTrue(pd.api.types.is_numeric_dtype(df_curr["price"]))

    def test_06_data_profiling_engine(self):
        test_df = pd.DataFrame({
            "col_a": [1, 2, 3, 4, 5],
            "col_b": [10.0, 20.0, 30.0, 40.0, 50.0]
        })
        profile = DataProfilingService.generate_full_profile(test_df)
        self.assertEqual(profile["summary"]["quality_score"], 100.0)
        self.assertIn("col_a", profile["columns"])

    def test_07_analytics_engine(self):
        test_df = pd.DataFrame({
            "product": ["Widget A", "Widget B", "Widget C", "Widget D"],
            "revenue": [8000, 1500, 400, 100]
        })
        abc_res = AnalyticsService.run_abc_analysis(test_df, item_col="product", value_col="revenue")
        self.assertEqual(abc_res["total_value"], 10000.0)
        self.assertIn("data", abc_res)

    def test_08_visualization_engine(self):
        test_df = pd.DataFrame({"x": ["A", "B"], "y": [10, 20]})
        fig = VisualizationService.create_bar_chart(test_df, x_col="x", y_col="y", title="Test Bar")
        self.assertIsNotNone(fig)

    def test_09_plugin_manager(self):
        home_mod = HomeModule()
        plugin_manager.register_module(home_mod)
        retrieved = plugin_manager.get_module("home")
        self.assertEqual(retrieved.name, "Home Dashboard")


if __name__ == "__main__":
    unittest.main()

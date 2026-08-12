"""
Data Cleaning & Transformation Engine for ARGUS AI Platform.
Features automated cleaning rule generation, missing value imputation, outlier detection, currency fixes, and type coercion.
"""
import re
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from core.logger import logger
from core.exceptions import CleaningException


class DataCleaningService:
    """Enterprise Data Cleaning & Preparation Engine."""

    @classmethod
    def generate_cleaning_suggestions(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analyze DataFrame and suggest automated cleaning actions."""
        suggestions = []

        # 1. Check duplicate rows
        dup_count = df.duplicated().sum()
        if dup_count > 0:
            suggestions.append({
                "type": "remove_duplicates",
                "severity": "high",
                "message": f"Found {dup_count} exact duplicate rows ({round(dup_count/len(df)*100, 1)}% of dataset).",
                "action": "Remove Duplicates"
            })

        # 2. Check missing values
        null_counts = df.isnull().sum()
        for col, count in null_counts.items():
            if count > 0:
                pct = round(count / len(df) * 100, 1)
                suggestions.append({
                    "type": "missing_values",
                    "column": col,
                    "severity": "medium" if pct < 30 else "high",
                    "message": f"Column '{col}' has {count} missing values ({pct}%).",
                    "action": f"Impute or Drop '{col}'"
                })

        # 3. Check for leading/trailing whitespaces in string columns
        string_cols = df.select_dtypes(include=['object', 'string']).columns
        for col in string_cols:
            sample_vals = df[col].dropna().astype(str)
            whitespace_count = sample_vals.apply(lambda s: s != s.strip()).sum()
            if whitespace_count > 0:
                suggestions.append({
                    "type": "trim_whitespace",
                    "column": col,
                    "severity": "low",
                    "message": f"Column '{col}' contains {whitespace_count} values with unneeded whitespaces.",
                    "action": f"Trim Whitespaces in '{col}'"
                })

        # 4. Check for currency formatted strings
        for col in string_cols:
            sample_vals = df[col].dropna().astype(str)
            if sample_vals.str.contains(r"[\$\€\£\₹]", regex=True).any():
                suggestions.append({
                    "type": "clean_currency",
                    "column": col,
                    "severity": "medium",
                    "message": f"Column '{col}' appears to contain currency symbols.",
                    "action": f"Convert '{col}' to Numeric Float"
                })


        return suggestions

    @classmethod
    def remove_duplicates(cls, df: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
        """Remove duplicate rows from DataFrame."""
        return df.drop_duplicates(subset=subset, keep="first").reset_index(drop=True)

    @classmethod
    def impute_missing_values(
        cls, 
        df: pd.DataFrame, 
        column: str, 
        strategy: str = "mean", 
        fill_value: Any = None
    ) -> pd.DataFrame:
        """Impute missing values using mean, median, mode, constant, ffill, or bfill."""
        df_clean = df.copy()
        if column not in df_clean.columns:
            return df_clean

        if strategy == "mean" and pd.api.types.is_numeric_dtype(df_clean[column]):
            val = df_clean[column].mean()
            df_clean[column] = df_clean[column].fillna(val)
        elif strategy == "median" and pd.api.types.is_numeric_dtype(df_clean[column]):
            val = df_clean[column].median()
            df_clean[column] = df_clean[column].fillna(val)
        elif strategy == "mode":
            mode_series = df_clean[column].mode()
            val = mode_series[0] if not mode_series.empty else "Unknown"
            df_clean[column] = df_clean[column].fillna(val)
        elif strategy == "constant":
            df_clean[column] = df_clean[column].fillna(fill_value if fill_value is not None else "Missing")
        elif strategy == "ffill":
            df_clean[column] = df_clean[column].ffill()
        elif strategy == "bfill":
            df_clean[column] = df_clean[column].bfill()

        return df_clean

    @classmethod
    def clean_currency_column(cls, df: pd.DataFrame, column: str) -> pd.DataFrame:
        """Strip currency symbols ($, €, £, ₹), commas, and cast to float."""
        df_clean = df.copy()
        if column in df_clean.columns:
            cleaned_series = (
                df_clean[column]
                .astype(str)
                .str.replace(r"[^\d\.\-]", "", regex=True)
                .str.strip()
            )
            df_clean[column] = pd.to_numeric(cleaned_series, errors="coerce")
        return df_clean


    @classmethod
    def parse_datetime_column(cls, df: pd.DataFrame, column: str) -> pd.DataFrame:
        """Convert string column to pandas datetime."""
        df_clean = df.copy()
        if column in df_clean.columns:
            df_clean[column] = pd.to_datetime(df_clean[column], errors="coerce")
        return df_clean

    @classmethod
    def trim_whitespaces(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Trim leading and trailing whitespaces across all string columns."""
        df_clean = df.copy()
        for col in df_clean.select_dtypes(include=["object", "string"]).columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()
        return df_clean

    @classmethod
    def detect_outliers_iqr(cls, df: pd.DataFrame, column: str, factor: float = 1.5) -> Tuple[pd.DataFrame, int]:
        """Detect outliers using Interquartile Range (IQR) method."""
        if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
            return df, 0

        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - (factor * iqr)
        upper_bound = q3 + (factor * iqr)

        outlier_mask = (df[column] < lower_bound) | (df[column] > upper_bound)
        outlier_count = int(outlier_mask.sum())
        
        return df[~outlier_mask].reset_index(drop=True), outlier_count

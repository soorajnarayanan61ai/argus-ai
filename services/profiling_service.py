"""
Data Profiling & Quality Scoring Engine for ARGUS AI Platform.
Computes dataset metrics, column health statistics, correlation matrices, and Data Quality Score.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from core.logger import logger


class DataProfilingService:
    """Enterprise Data Profiling Engine."""

    @classmethod
    def generate_full_profile(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive profiling report for DataFrame."""
        total_rows = len(df)
        total_cols = len(df.columns)

        if total_rows == 0:
            return {"error": "DataFrame is empty."}

        # 1. High level statistics
        total_cells = total_rows * total_cols
        total_nulls = int(df.isnull().sum().sum())
        null_percentage = round((total_nulls / total_cells) * 100, 2) if total_cells > 0 else 0.0
        duplicate_rows = int(df.duplicated().sum())

        # 2. Column profiling
        column_profiles = {}
        for col in df.columns:
            col_series = df[col]
            null_count = int(col_series.isnull().sum())
            null_pct = round((null_count / total_rows) * 100, 2)
            unique_count = int(col_series.nunique())
            dtype_str = str(col_series.dtype)

            col_data: Dict[str, Any] = {
                "dtype": dtype_str,
                "null_count": null_count,
                "null_pct": null_pct,
                "unique_count": unique_count,
                "health": "Healthy"
            }

            if null_pct > 40:
                col_data["health"] = "Critical"
            elif null_pct > 10:
                col_data["health"] = "Warning"

            # Numeric specific stats
            if pd.api.types.is_numeric_dtype(col_series):
                non_null = col_series.dropna()
                if not non_null.empty:
                    col_data.update({
                        "mean": round(float(non_null.mean()), 4),
                        "std": round(float(non_null.std()), 4) if len(non_null) > 1 else 0.0,
                        "min": round(float(non_null.min()), 4),
                        "q25": round(float(non_null.quantile(0.25)), 4),
                        "median": round(float(non_null.median()), 4),
                        "q75": round(float(non_null.quantile(0.75)), 4),
                        "max": round(float(non_null.max()), 4),
                        "skewness": round(float(non_null.skew()), 4) if len(non_null) > 2 else 0.0,
                    })

            column_profiles[col] = col_data

        # 3. Correlation Matrix (Numeric Columns)
        numeric_df = df.select_dtypes(include=[np.number])
        corr_matrix = {}
        if numeric_df.shape[1] > 1:
            corr_df = numeric_df.corr(method="pearson").fillna(0.0)
            corr_matrix = corr_df.to_dict()

        # 4. Data Quality Score Calculation (0 - 100%)
        quality_score = cls._calculate_quality_score(
            total_rows=total_rows,
            null_pct=null_percentage,
            duplicate_pct=(duplicate_rows / total_rows * 100) if total_rows > 0 else 0.0,
            column_profiles=column_profiles
        )

        return {
            "summary": {
                "total_rows": total_rows,
                "total_columns": total_cols,
                "total_nulls": total_nulls,
                "null_percentage": null_percentage,
                "duplicate_rows": duplicate_rows,
                "quality_score": quality_score
            },
            "columns": column_profiles,
            "correlation_matrix": corr_matrix
        }

    @classmethod
    def _calculate_quality_score(
        cls, 
        total_rows: int, 
        null_pct: float, 
        duplicate_pct: float, 
        column_profiles: Dict[str, Any]
    ) -> float:
        """Compute composite Data Quality Score (0 to 100)."""
        score = 100.0
        
        # Deduct for missing values
        score -= (null_pct * 0.5)

        # Deduct for duplicates
        score -= (duplicate_pct * 0.5)

        # Deduct for critical columns
        critical_cols = sum(1 for c in column_profiles.values() if c.get("health") == "Critical")
        score -= (critical_cols * 5.0)

        return round(max(0.0, min(100.0, score)), 1)

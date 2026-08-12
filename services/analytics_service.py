"""
Analytics & Intelligence Engine for ARGUS AI Platform.
Features Predictive Forecasting, ABC Analysis, Pareto 80/20 Rule, RFM Customer Segmentation, and Financial Analysis.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from sklearn.linear_model import Ridge
from sklearn.cluster import KMeans
from core.logger import logger
from core.exceptions import AnalyticsException


class AnalyticsService:
    """Enterprise Analytics & Predictive Intelligence Engine."""

    @classmethod
    def run_descriptive_summary(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate high-level statistical summary for numeric fields."""
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            return {"message": "No numeric columns available for statistical summary."}

        summary = {}
        for col in numeric_df.columns:
            s = numeric_df[col].dropna()
            if not s.empty:
                summary[col] = {
                    "count": int(s.count()),
                    "sum": round(float(s.sum()), 2),
                    "mean": round(float(s.mean()), 2),
                    "std": round(float(s.std()), 2) if len(s) > 1 else 0.0,
                    "min": round(float(s.min()), 2),
                    "max": round(float(s.max()), 2),
                    "range": round(float(s.max() - s.min()), 2),
                }
        return summary

    @classmethod
    def run_time_series_forecast(
        cls, 
        df: pd.DataFrame, 
        date_col: str, 
        value_col: str, 
        periods: int = 6
    ) -> Dict[str, Any]:
        """
        Run Predictive Time-Series Forecasting using Ridge Trend Regression.
        Returns historical aggregated series, forecasted points, and upper/lower confidence bounds.
        """
        if date_col not in df.columns or value_col not in df.columns:
            raise AnalyticsException(f"Columns '{date_col}' or '{value_col}' not found.")

        # Ensure datetime format and sort
        temp_df = df[[date_col, value_col]].dropna().copy()
        temp_df[date_col] = pd.to_datetime(temp_df[date_col], errors="coerce")
        temp_df = temp_df.dropna().sort_values(date_col)

        if temp_df.empty or len(temp_df) < 3:
            raise AnalyticsException("Insufficient time-series data points for forecasting (minimum 3 required).")

        # Group by date period (e.g. Month or Day)
        grouped = temp_df.set_index(date_col).resample("M")[value_col].sum().reset_index()
        if len(grouped) < 3:
            grouped = temp_df.set_index(date_col).resample("D")[value_col].sum().reset_index()

        X = np.arange(len(grouped)).reshape(-1, 1)
        y = grouped[value_col].values

        model = Ridge(alpha=1.0)
        model.fit(X, y)

        future_X = np.arange(len(grouped), len(grouped) + periods).reshape(-1, 1)
        forecast_y = model.predict(future_X)

        # Standard error estimation
        residuals = y - model.predict(X)
        std_err = np.std(residuals) if len(residuals) > 1 else 1.0

        # Generate future dates
        last_date = grouped[date_col].max()
        future_dates = pd.date_range(start=last_date, periods=periods + 1, freq="M")[1:]

        forecast_records = []
        for d, val in zip(future_dates, forecast_y):
            pred_val = float(max(0.0, val))
            forecast_records.append({
                "date": d.strftime("%Y-%m-%d"),
                "forecast": round(pred_val, 2),
                "lower_bound": round(max(0.0, pred_val - 1.96 * std_err), 2),
                "upper_bound": round(pred_val + 1.96 * std_err, 2),
            })

        historical_records = [
            {"date": r[date_col].strftime("%Y-%m-%d"), "actual": round(float(r[value_col]), 2)}
            for _, r in grouped.iterrows()
        ]

        return {
            "historical": historical_records,
            "forecast": forecast_records,
            "model_r2": round(float(model.score(X, y)), 4) if len(X) > 2 else 0.0,
            "trend_slope": round(float(model.coef_[0]), 4)
        }

    @classmethod
    def run_abc_analysis(cls, df: pd.DataFrame, item_col: str, value_col: str) -> Dict[str, Any]:
        """
        ABC Inventory / Revenue Classification Analysis:
        Class A: Top 80% Revenue (usually top ~20% items)
        Class B: Next 15% Revenue (~30% items)
        Class C: Bottom 5% Revenue (~50% items)
        """
        if item_col not in df.columns or value_col not in df.columns:
            raise AnalyticsException("Invalid columns for ABC Analysis.")

        grouped = df.groupby(item_col)[value_col].sum().reset_index()
        grouped = grouped.sort_values(by=value_col, ascending=False).reset_index(drop=True)

        total_val = grouped[value_col].sum()
        if total_val == 0:
            raise AnalyticsException("Total value is zero.")

        grouped["revenue_pct"] = (grouped[value_col] / total_val) * 100
        grouped["cum_pct"] = grouped["revenue_pct"].cumsum()

        def classify(cum):
            if cum <= 80.0:
                return "Class A (Top 80%)"
            elif cum <= 95.0:
                return "Class B (Next 15%)"
            else:
                return "Class C (Bottom 5%)"

        grouped["abc_category"] = grouped["cum_pct"].apply(classify)
        summary = grouped["abc_category"].value_counts().to_dict()

        return {
            "data": grouped.to_dict(orient="records"),
            "summary": summary,
            "total_value": round(float(total_val), 2)
        }

    @classmethod
    def run_pareto_analysis(cls, df: pd.DataFrame, category_col: str, value_col: str) -> Dict[str, Any]:
        """Pareto 80/20 Rule Analysis."""
        if category_col not in df.columns or value_col not in df.columns:
            raise AnalyticsException("Columns missing for Pareto Analysis.")

        grouped = df.groupby(category_col)[value_col].sum().reset_index()
        grouped = grouped.sort_values(by=value_col, ascending=False).reset_index(drop=True)

        total = grouped[value_col].sum()
        if total == 0:
            return {"data": []}

        grouped["percentage"] = (grouped[value_col] / total) * 100
        grouped["cumulative_percentage"] = grouped["percentage"].cumsum()

        return {
            "data": grouped.to_dict(orient="records"),
            "top_80_count": int((grouped["cumulative_percentage"] <= 80.0).sum() + 1),
            "total_categories": len(grouped)
        }

    @classmethod
    def run_rfm_segmentation(
        cls, 
        df: pd.DataFrame, 
        customer_id_col: str, 
        date_col: str, 
        amount_col: str, 
        clusters: int = 4
    ) -> Dict[str, Any]:
        """RFM (Recency, Frequency, Monetary) Customer Segmentation using K-Means Clustering."""
        temp_df = df[[customer_id_col, date_col, amount_col]].dropna().copy()
        temp_df[date_col] = pd.to_datetime(temp_df[date_col], errors="coerce")
        temp_df = temp_df.dropna()

        max_date = temp_df[date_col].max()

        rfm = temp_df.groupby(customer_id_col).agg({
            date_col: lambda x: (max_date - x.max()).days,
            customer_id_col: "count",
            amount_col: "sum"
        }).rename(columns={
            date_col: "Recency",
            customer_id_col: "Frequency",
            amount_col: "Monetary"
        }).reset_index()

        if len(rfm) < clusters:
            clusters = max(1, len(rfm))

        X = rfm[["Recency", "Frequency", "Monetary"]]
        kmeans = KMeans(n_clusters=clusters, random_state=42, n_init=10)
        rfm["Cluster"] = kmeans.fit_predict(X)

        cluster_summary = rfm.groupby("Cluster").agg({
            "Recency": "mean",
            "Frequency": "mean",
            "Monetary": "mean",
            customer_id_col: "count"
        }).round(2).to_dict(orient="index")

        return {
            "rfm_data": rfm.to_dict(orient="records"),
            "cluster_summary": cluster_summary
        }

"""
Visualization Engine for ARGUS AI Platform.
Generates interactive Plotly figures (Bar, Line, Area, Pie, Donut, Scatter, Heatmap, Treemap, Sunburst, Waterfall, Gauge, KPI).
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, Optional, List
from core.logger import logger
from core.session import SessionManager
from config.settings import settings


class VisualizationService:
    """Enterprise Plotly Chart Generator Engine."""

    DARK_COLOR_SEQUENCE = ["#6366f1", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444", "#3b82f6", "#ec4899", "#14b8a6"]
    DARK_TEMPLATE = "plotly_dark"
    LIGHT_TEMPLATE = "plotly_white"

    @classmethod
    def _get_template(cls) -> str:
        current_theme = SessionManager.get(SessionManager.THEME, settings.get("theme.default_theme", "dark"))
        return cls.DARK_TEMPLATE if current_theme == "dark" else cls.LIGHT_TEMPLATE

    @classmethod
    def create_bar_chart(
        cls, 
        df: pd.DataFrame, 
        x_col: str, 
        y_col: str, 
        title: str = "Bar Chart", 
        orientation: str = "v"
    ) -> go.Figure:
        """Create responsive interactive Bar Chart."""
        if orientation == "h":
            fig = px.bar(df, x=y_col, y=x_col, title=title, orientation="h", color_discrete_sequence=cls.DARK_COLOR_SEQUENCE)
        else:
            fig = px.bar(df, x=x_col, y=y_col, title=title, color_discrete_sequence=cls.DARK_COLOR_SEQUENCE)
        
        fig.update_layout(template=cls._get_template(), margin=dict(l=20, r=20, t=40, b=20))
        return fig

    @classmethod
    def create_line_chart(cls, df: pd.DataFrame, x_col: str, y_col: str, title: str = "Line Trend") -> go.Figure:
        """Create responsive interactive Line Chart."""
        fig = px.line(df, x=x_col, y=y_col, title=title, markers=True, color_discrete_sequence=cls.DARK_COLOR_SEQUENCE)
        fig.update_layout(template=cls._get_template(), margin=dict(l=20, r=20, t=40, b=20))
        return fig

    @classmethod
    def create_area_chart(cls, df: pd.DataFrame, x_col: str, y_col: str, title: str = "Area Chart") -> go.Figure:
        """Create Area Chart."""
        fig = px.area(df, x=x_col, y=y_col, title=title, color_discrete_sequence=cls.DARK_COLOR_SEQUENCE)
        fig.update_layout(template=cls._get_template(), margin=dict(l=20, r=20, t=40, b=20))
        return fig

    @classmethod
    def create_pie_donut_chart(cls, df: pd.DataFrame, names_col: str, values_col: str, title: str = "Distribution", hole: float = 0.4) -> go.Figure:
        """Create Donut / Pie Chart."""
        fig = px.pie(df, names=names_col, values=values_col, title=title, hole=hole, color_discrete_sequence=cls.DARK_COLOR_SEQUENCE)
        fig.update_layout(template=cls._get_template(), margin=dict(l=20, r=20, t=40, b=20))
        return fig

    @classmethod
    def create_scatter_chart(cls, df: pd.DataFrame, x_col: str, y_col: str, color_col: Optional[str] = None, title: str = "Scatter Matrix") -> go.Figure:
        """Create Scatter plot."""
        fig = px.scatter(df, x=x_col, y=y_col, color=color_col, title=title, color_discrete_sequence=cls.DARK_COLOR_SEQUENCE)
        fig.update_layout(template=cls._get_template(), margin=dict(l=20, r=20, t=40, b=20))
        return fig

    @classmethod
    def create_heatmap(cls, corr_df: pd.DataFrame, title: str = "Correlation Heatmap") -> go.Figure:
        """Create Correlation Heatmap."""
        fig = px.imshow(corr_df, text_auto=True, aspect="auto", title=title, color_continuous_scale="Viridis")
        fig.update_layout(template=cls._get_template(), margin=dict(l=20, r=20, t=40, b=20))
        return fig

    @classmethod
    def create_histogram(cls, df: pd.DataFrame, x_col: str, title: str = "Distribution Histogram", bins: int = 30) -> go.Figure:
        """Create Histogram."""
        fig = px.histogram(df, x=x_col, nbins=bins, title=title, color_discrete_sequence=cls.DARK_COLOR_SEQUENCE)
        fig.update_layout(template=cls._get_template(), margin=dict(l=20, r=20, t=40, b=20))
        return fig

    @classmethod
    def create_treemap(cls, df: pd.DataFrame, path_cols: List[str], values_col: str, title: str = "Treemap Hierarchy") -> go.Figure:
        """Create Treemap Chart."""
        fig = px.treemap(df, path=path_cols, values=values_col, title=title, color_discrete_sequence=cls.DARK_COLOR_SEQUENCE)
        fig.update_layout(template=cls._get_template(), margin=dict(l=20, r=20, t=40, b=20))
        return fig

    @classmethod
    def create_sunburst(cls, df: pd.DataFrame, path_cols: List[str], values_col: str, title: str = "Sunburst Breakdown") -> go.Figure:
        """Create Sunburst Chart."""
        fig = px.sunburst(df, path=path_cols, values=values_col, title=title, color_discrete_sequence=cls.DARK_COLOR_SEQUENCE)
        fig.update_layout(template=cls._get_template(), margin=dict(l=20, r=20, t=40, b=20))
        return fig

    @classmethod
    def create_gauge_chart(cls, value: float, min_val: float = 0.0, max_val: float = 100.0, title: str = "Score Gauge") -> go.Figure:
        """Create KPI Gauge Chart."""
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title, 'font': {'size': 18}},
            gauge={
                'axis': {'range': [min_val, max_val]},
                'bar': {'color': "#6366f1"},
                'steps': [
                    {'range': [0, 40], 'color': "rgba(239, 68, 68, 0.3)"},
                    {'range': [40, 75], 'color': "rgba(245, 158, 11, 0.3)"},
                    {'range': [75, 100], 'color': "rgba(16, 185, 129, 0.3)"}
                ],
            }
        ))
        fig.update_layout(template=cls._get_template(), height=250, margin=dict(l=20, r=20, t=40, b=20))
        return fig

"""
Visualization Engine UI Module for ARGUS AI Platform.
Interactive Chart Builder supporting Bar, Line, Area, Pie, Donut, Scatter, Heatmap, Histogram, Treemap, Sunburst, and Gauge.
"""
import streamlit as st
import pandas as pd
from modules.base_module import BaseModule
from services.visualization_service import VisualizationService
from core.session import SessionManager
from core.exceptions import handle_errors


class VisualizationModule(BaseModule):
    @property
    def module_id(self) -> str:
        return "visualization_engine"

    @property
    def name(self) -> str:
        return "Visualization Engine"

    @property
    def icon(self) -> str:
        return "🎨"

    @property
    def category(self) -> str:
        return "Analytics"

    @property
    def order(self) -> int:
        return 70

    @handle_errors(show_traceback=True)
    def render(self) -> None:
        st.title("🎨 Interactive Visualization Engine & Dashboard Builder")

        df = SessionManager.get_active_df()
        if df is None:
            st.warning("⚠️ No active dataset loaded. Please ingest a dataset first using the File Loader or Database Connectors.")
            return

        cols = list(df.columns)
        num_cols = list(df.select_dtypes(include=['number']).columns)

        st.sidebar.markdown("### ⚙️ Chart Configuration")
        chart_type = st.sidebar.selectbox(
            "Select Chart Type",
            options=["Bar Chart", "Line Chart", "Area Chart", "Pie / Donut", "Scatter Plot", "Histogram", "Treemap", "Sunburst", "Gauge"]
        )

        title = st.sidebar.text_input("Chart Title", value=f"{chart_type} - Enterprise View")

        fig = None

        if chart_type in ["Bar Chart", "Line Chart", "Area Chart"]:
            x_col = st.sidebar.selectbox("X Axis (Category/Date)", options=cols, index=0)
            y_col = st.sidebar.selectbox("Y Axis (Numeric Value)", options=num_cols if num_cols else cols, index=0)

            if chart_type == "Bar Chart":
                orient = st.sidebar.radio("Orientation", options=["Vertical", "Horizontal"])
                fig = VisualizationService.create_bar_chart(df, x_col=x_col, y_col=y_col, title=title, orientation="h" if orient == "Horizontal" else "v")
            elif chart_type == "Line Chart":
                fig = VisualizationService.create_line_chart(df, x_col=x_col, y_col=y_col, title=title)
            elif chart_type == "Area Chart":
                fig = VisualizationService.create_area_chart(df, x_col=x_col, y_col=y_col, title=title)

        elif chart_type == "Pie / Donut":
            names_col = st.sidebar.selectbox("Categories (Names)", options=cols, index=0)
            values_col = st.sidebar.selectbox("Values Column", options=num_cols if num_cols else cols, index=0)
            is_donut = st.sidebar.checkbox("Render as Donut Chart", value=True)
            fig = VisualizationService.create_pie_donut_chart(df, names_col=names_col, values_col=values_col, title=title, hole=0.4 if is_donut else 0.0)

        elif chart_type == "Scatter Plot":
            x_col = st.sidebar.selectbox("X Axis Column", options=num_cols if num_cols else cols, index=0)
            y_col = st.sidebar.selectbox("Y Axis Column", options=num_cols if num_cols else cols, index=min(1, len(cols)-1))
            color_col = st.sidebar.selectbox("Color Segment (Optional)", options=["None"] + cols)
            color_arg = None if color_col == "None" else color_col
            fig = VisualizationService.create_scatter_chart(df, x_col=x_col, y_col=y_col, color_col=color_arg, title=title)

        elif chart_type == "Histogram":
            x_col = st.sidebar.selectbox("Numeric Feature", options=num_cols if num_cols else cols, index=0)
            bins = st.sidebar.slider("Number of Bins", min_value=5, max_value=100, value=30)
            fig = VisualizationService.create_histogram(df, x_col=x_col, title=title, bins=bins)

        elif chart_type in ["Treemap", "Sunburst"]:
            path_cols = st.sidebar.multiselect("Hierarchy Path Columns", options=cols, default=cols[:2] if len(cols)>=2 else cols)
            values_col = st.sidebar.selectbox("Values Column", options=num_cols if num_cols else cols, index=0)
            if path_cols:
                if chart_type == "Treemap":
                    fig = VisualizationService.create_treemap(df, path_cols=path_cols, values_col=values_col, title=title)
                else:
                    fig = VisualizationService.create_sunburst(df, path_cols=path_cols, values_col=values_col, title=title)

        elif chart_type == "Gauge":
            val_col = st.sidebar.selectbox("Select Target Value", options=num_cols if num_cols else cols, index=0)
            avg_val = float(df[val_col].mean()) if not df.empty and val_col in num_cols else 50.0
            max_val = float(df[val_col].max()) if not df.empty and val_col in num_cols else 100.0
            fig = VisualizationService.create_gauge_chart(value=avg_val, min_val=0.0, max_val=max_val, title=f"Mean {val_col}")

        # Render Chart
        if fig:
            st.plotly_chart(fig, use_container_width=True)

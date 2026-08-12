"""
Data Profiling UI Module for ARGUS AI Platform.
Displays overall Data Quality Score gauge, column health breakdown, correlation heatmap, and statistics.
"""
import streamlit as st
import pandas as pd
from modules.base_module import BaseModule
from services.profiling_service import DataProfilingService
from services.visualization_service import VisualizationService
from core.session import SessionManager
from core.exceptions import handle_errors


class ProfilingModule(BaseModule):
    @property
    def module_id(self) -> str:
        return "data_profiling"

    @property
    def name(self) -> str:
        return "Data Profiling Engine"

    @property
    def icon(self) -> str:
        return "📈"

    @property
    def category(self) -> str:
        return "Analytics"

    @property
    def order(self) -> int:
        return 50

    @handle_errors(show_traceback=True)
    def render(self) -> None:
        st.title("📈 Data Profiling & Quality Scoring Engine")

        df = SessionManager.get_active_df()
        if df is None:
            st.warning("⚠️ No active dataset loaded. Please ingest a dataset first using the File Loader or Database Connectors.")
            return

        with st.spinner("Calculating comprehensive dataset metrics and Data Quality Score..."):
            profile = DataProfilingService.generate_full_profile(df)

        summary = profile["summary"]

        # Score Gauge and Highlights
        col1, col2 = st.columns([1, 2])

        with col1:
            gauge_fig = VisualizationService.create_gauge_chart(
                value=summary["quality_score"],
                title="Data Quality Score"
            )
            st.plotly_chart(gauge_fig, use_container_width=True)

        with col2:
            st.markdown("### 📊 Dataset Health Overview")
            kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
            with kpi_col1:
                st.metric("Total Rows", f"{summary['total_rows']:,}")
                st.metric("Missing Cell Ratio", f"{summary['null_percentage']}%")
            with kpi_col2:
                st.metric("Total Columns", summary['total_columns'])
                st.metric("Duplicate Rows", summary['duplicate_rows'])
            with kpi_col3:
                st.metric("Total Cells", f"{summary['total_rows'] * summary['total_columns']:,}")
                st.metric("Quality Grade", "EXCELLENT" if summary["quality_score"] > 85 else ("GOOD" if summary["quality_score"] > 70 else "NEEDS ATTENTION"))

        st.markdown("---")
        st.subheader("📋 Column-by-Column Health Breakdown")

        cols_data = []
        for col_name, cinfo in profile["columns"].items():
            cols_data.append({
                "Column Name": col_name,
                "Data Type": cinfo["dtype"],
                "Null Count": cinfo["null_count"],
                "Null %": f"{cinfo['null_pct']}%",
                "Unique Count": cinfo["unique_count"],
                "Health Status": cinfo["health"],
                "Mean": cinfo.get("mean", "N/A"),
                "Median": cinfo.get("median", "N/A"),
                "Min": cinfo.get("min", "N/A"),
                "Max": cinfo.get("max", "N/A"),
            })

        df_cols_summary = pd.DataFrame(cols_data)
        st.dataframe(df_cols_summary, use_container_width=True)

# Correlation Matrix
        if profile.get("correlation_matrix"):
            st.markdown("---")
            st.subheader("🔥 Pearson Correlation Heatmap")
            st.markdown("---")
            corr_df = pd.DataFrame(profile["correlation_matrix"])
            heatmap_fig = VisualizationService.create_heatmap(corr_df)
            st.plotly_chart(heatmap_fig, use_container_width=True)

        st.markdown("---")
        st.subheader("🧠 ASK ARGUS AI")
        user_query = st.text_input("Ask a question about your dataset...", key="profiling_query_input")
        if st.button("Analyze", key="profiling_query_btn"):
            if user_query:
                from services.query_service import QueryService
                query_service = QueryService()
                response = query_service.process_query(df, user_query)
                st.write("### Answer")
                st.write(response.get("answer", ""))
                if response.get("evidence"):
                    st.info(f"**Evidence:** {response['evidence']}")
                if response.get("table") is not None:
                    st.dataframe(response["table"])
                if response.get("chart") is not None:
                    st.plotly_chart(response["chart"])
            else:
                st.warning("Please enter a question.")
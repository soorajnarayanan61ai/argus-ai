"""
Home Dashboard Module for ARGUS AI Platform.
Provides platform summary, architecture topology, system health, and quick actions.
"""
import streamlit as st
import pandas as pd
from modules.base_module import BaseModule
from core.session import SessionManager
from core.theme import ThemeManager
from utils.helpers import get_system_diagnostics, format_bytes


class HomeModule(BaseModule):
    @property
    def module_id(self) -> str:
        return "home"

    @property
    def name(self) -> str:
        return "Home Dashboard"

    @property
    def icon(self) -> str:
        return "🏠"

    @property
    def category(self) -> str:
        return "Core"

    @property
    def order(self) -> int:
        return 1

    def render(self) -> None:
        # Header Banner
        st.markdown(
            """
            <div class="argus-header-banner">
                <div>
                    <h1 class="argus-header-title">ARGUS AI PLATFORM</h1>
                    <div class="argus-header-sub">Enterprise AI Data Analyst Platform Engine</div>
                </div>
                <div>
                    <span class="argus-badge argus-badge-primary">v1.0.0 Enterprise</span>
                    <span class="argus-badge argus-badge-success">System Active</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Active Dataset Status Card
        df = SessionManager.get_active_df()
        meta = SessionManager.get(SessionManager.DATASET_METADATA, {})

        st.subheader("📊 Active Workspace Status")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                f"""
                <div class="argus-metric-card">
                    <div class="argus-metric-title">Active Dataset</div>
                    <div class="argus-metric-value">{meta.get('name', 'None Loaded')}</div>
                    <div class="argus-metric-subtitle">Ready for analysis</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""
                <div class="argus-metric-card">
                    <div class="argus-metric-title">Total Rows</div>
                    <div class="argus-metric-value">{meta.get('rows', 0):,}</div>
                    <div class="argus-metric-subtitle">Records in memory</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                f"""
                <div class="argus-metric-card">
                    <div class="argus-metric-title">Total Columns</div>
                    <div class="argus-metric-value">{meta.get('columns', 0)}</div>
                    <div class="argus-metric-subtitle">Variables mapped</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col4:
            st.markdown(
                f"""
                <div class="argus-metric-card">
                    <div class="argus-metric-title">RAM Allocation</div>
                    <div class="argus-metric-value">{meta.get('memory_usage_mb', 0.0)} MB</div>
                    <div class="argus-metric-subtitle">Memory footprint</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Preview Active DataFrame if present
        if df is not None:
            st.markdown("### 📋 Active Dataset Quick Preview")
            st.dataframe(df.head(10), use_container_width=True)
        else:
            st.info("💡 No dataset loaded yet. Use **Universal File Loader** or **Database Connectors** in the sidebar to ingest data.")

        # System Metrics & Topology Section
        st.markdown("---")
        st.subheader("💻 System Performance & Engine Architecture")

        diag = get_system_diagnostics()
        sys_col1, sys_col2, sys_col3 = st.columns(3)

        with sys_col1:
            st.metric("CPU Utilization", f"{diag['cpu_usage_pct']}%")
            st.progress(min(1.0, diag['cpu_usage_pct'] / 100.0))

        with sys_col2:
            st.metric("RAM Used (%)", f"{diag['ram_used_pct']}%")
            st.progress(min(1.0, diag['ram_used_pct'] / 100.0))

        with sys_col3:
            st.metric("Disk Free", f"{diag['disk_free']} / {diag['disk_total']}")
            st.progress(0.85)

        st.markdown(
            """
            #### 🛠️ Available Platform Engines
            - **Universal File Loader**: CSV, Excel, JSON, XML, PDF, Word, PPTX, ZIP, Images.
            - **Multi-Database Connectors**: SQLite, DuckDB, PostgreSQL, MySQL, SQL Server, Snowflake, BigQuery.
            - **OCR Engine**: Image & Invoice tabular extraction engine.
            - **Data Cleaning Engine**: Automated missing value imputation, outlier detection, currency normalization.
            - **Data Profiling Engine**: Automated Data Quality Scoring (0-100%), correlation matrices, distribution.
            - **Analytics Engine**: Time-Series Forecasting, ABC Inventory Analysis, Pareto 80/20, RFM Customer Segmentation.
            - **Visualization Engine**: Interactive Plotly suite (10+ chart types, Dark enterprise theme).
            """
        )

"""
Multi-Database Connector UI Module for ARGUS AI Platform.
Supports SQLite, DuckDB, PostgreSQL, MySQL, SQL Server, Oracle, Snowflake, BigQuery, and MongoDB.
"""
import streamlit as st
import pandas as pd
from modules.base_module import BaseModule
from services.db_service import DatabaseConnectorService
from core.session import SessionManager
from core.exceptions import handle_errors


class DBConnectorsModule(BaseModule):
    @property
    def module_id(self) -> str:
        return "db_connectors"

    @property
    def name(self) -> str:
        return "Database Connectors"

    @property
    def icon(self) -> str:
        return "🗄️"

    @property
    def category(self) -> str:
        return "Ingestion"

    @property
    def order(self) -> int:
        return 20

    @handle_errors(show_traceback=True)
    def render(self) -> None:
        st.title("🗄️ Multi-Database Connectors Engine")
        st.markdown("Connect to local or cloud relational & analytical databases.")

        dialect = st.selectbox(
            "Select Target Database Engine",
            options=DatabaseConnectorService.SUPPORTED_DIALECTS,
            index=0
        )

        config = {"dialect": dialect}

        if dialect in ["SQLite", "DuckDB"]:
            path = st.text_input("Database File Path (or :memory:)", value="data/argus_enterprise.db" if dialect == "SQLite" else "data/analytics.duckdb")
            config["database_path"] = path
        else:
            conn_str = st.text_input("Connection String (URI)", value=f"{dialect.lower()}://user:password@localhost:5432/dbname", type="password")
            config["connection_string"] = conn_str

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔌 Test Database Connection"):
                res = DatabaseConnectorService.test_connection(config)
                if res["success"]:
                    st.success(res["message"])
                else:
                    st.error(res["message"])

        with col2:
            if st.button("📋 Fetch Database Tables"):
                tables = DatabaseConnectorService.get_tables(config)
                if tables:
                    st.success(f"Found {len(tables)} table(s): {', '.join(tables)}")
                else:
                    st.info("No user tables found or connection pending.")

        st.markdown("---")
        st.subheader("⚡ Execute SQL Query to Load Data")
        default_query = "SELECT * FROM argus_dataset_metadata;" if dialect == "SQLite" else "SELECT 1 as id, 'Argus Test' as sample_col;"
        query_sql = st.text_area("SQL Query", value=default_query, height=120)

        if st.button("🚀 Run Query & Load into Workspace", type="primary"):
            with st.spinner("Executing SQL query..."):
                df = DatabaseConnectorService.execute_query(config, query_sql)
                if not df.empty:
                    SessionManager.set_active_df(df, name=f"DB_Query_{dialect}")
                    st.success(f"Query executed successfully! Loaded {len(df)} rows and {len(df.columns)} columns into workspace.")
                    st.dataframe(df.head(20), use_container_width=True)
                else:
                    st.warning("Query returned zero rows.")

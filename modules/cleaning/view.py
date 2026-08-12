"""
Data Cleaning UI Module for ARGUS AI Platform.
Features automated cleaning recommendations, duplicate removal, null imputation, currency fixes, and outlier filters.
"""
import streamlit as st
import pandas as pd
from modules.base_module import BaseModule
from services.cleaning_service import DataCleaningService
from core.session import SessionManager
from core.exceptions import handle_errors


class DataCleaningModule(BaseModule):
    @property
    def module_id(self) -> str:
        return "data_cleaning"

    @property
    def name(self) -> str:
        return "Data Cleaning Engine"

    @property
    def icon(self) -> str:
        return "🧹"

    @property
    def category(self) -> str:
        return "Processing"

    @property
    def order(self) -> int:
        return 40

    @handle_errors(show_traceback=True)
    def render(self) -> None:
        st.title("🧹 Enterprise Data Cleaning Engine")

        df = SessionManager.get_active_df()
        if df is None:
            st.warning("⚠️ No active dataset loaded. Please ingest a dataset first using the File Loader or Database Connectors.")
            return

        st.markdown(f"Working on Active Dataset: **{SessionManager.get(SessionManager.DATASET_METADATA, {}).get('name', 'Dataset')}** ({len(df)} rows, {len(df.columns)} columns)")

        # Auto Suggestions Section
        suggestions = DataCleaningService.generate_cleaning_suggestions(df)
        if suggestions:
            st.subheader("💡 Automated Cleaning Recommendations")
            for sug in suggestions:
                st.info(f"**[{sug['severity'].upper()}]** {sug['message']} → Suggested Action: `{sug['action']}`")

        # Interactive Tool Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Duplicates & Whitespace", 
            "Missing Values Imputation", 
            "Currency & Types", 
            "Outlier Filter (IQR)",
            "Active Data View"
        ])

        working_df = df.copy()

        with tab1:
            st.subheader("Remove Duplicates & Whitespaces")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Remove Duplicate Rows"):
                    cleaned = DataCleaningService.remove_duplicates(working_df)
                    removed = len(working_df) - len(cleaned)
                    SessionManager.set_active_df(cleaned, name=SessionManager.get(SessionManager.DATASET_METADATA, {}).get('name', 'Dataset'))
                    st.success(f"Removed {removed} duplicate row(s)!")
                    st.rerun()

            with col2:
                if st.button("✂️ Trim All String Whitespaces"):
                    cleaned = DataCleaningService.trim_whitespaces(working_df)
                    SessionManager.set_active_df(cleaned, name=SessionManager.get(SessionManager.DATASET_METADATA, {}).get('name', 'Dataset'))
                    st.success("Trimmed leading/trailing whitespaces across string columns!")
                    st.rerun()

        with tab2:
            st.subheader("Missing Value Imputation")
            col = st.selectbox("Select Column with Missing Values", options=df.columns)
            strategy = st.selectbox("Imputation Strategy", options=["mean", "median", "mode", "constant", "ffill", "bfill"])
            fill_val = None
            if strategy == "constant":
                fill_val = st.text_input("Custom Fill Value", value="Missing")

            if st.button("✨ Apply Imputation"):
                cleaned = DataCleaningService.impute_missing_values(working_df, column=col, strategy=strategy, fill_value=fill_val)
                SessionManager.set_active_df(cleaned, name=SessionManager.get(SessionManager.DATASET_METADATA, {}).get('name', 'Dataset'))
                st.success(f"Imputed missing values in '{col}' using strategy '{strategy}'!")
                st.rerun()

        with tab3:
            st.subheader("Currency & Date Normalization")
            col_curr = st.selectbox("Select Currency Column to Clean ($, €, ₹ -> Float)", options=df.columns)
            if st.button("💲 Clean Currency Column"):
                cleaned = DataCleaningService.clean_currency_column(working_df, column=col_curr)
                SessionManager.set_active_df(cleaned, name=SessionManager.get(SessionManager.DATASET_METADATA, {}).get('name', 'Dataset'))
                st.success(f"Converted '{col_curr}' to numeric float!")
                st.rerun()

            col_date = st.selectbox("Select Date Column to Parse (Datetime)", options=df.columns)
            if st.button("📅 Parse Datetime Column"):
                cleaned = DataCleaningService.parse_datetime_column(working_df, column=col_date)
                SessionManager.set_active_df(cleaned, name=SessionManager.get(SessionManager.DATASET_METADATA, {}).get('name', 'Dataset'))
                st.success(f"Parsed '{col_date}' as pandas datetime!")
                st.rerun()

        with tab4:
            st.subheader("Outlier Filtering (IQR Method)")
            num_cols = df.select_dtypes(include=['number']).columns
            if len(num_cols) > 0:
                col_outlier = st.selectbox("Select Numeric Column for Outlier Removal", options=num_cols)
                factor = st.slider("IQR Multiplier Factor", min_value=1.0, max_value=3.0, value=1.5, step=0.1)
                if st.button("🔍 Filter Outliers"):
                    cleaned, count = DataCleaningService.detect_outliers_iqr(working_df, column=col_outlier, factor=factor)
                    SessionManager.set_active_df(cleaned, name=SessionManager.get(SessionManager.DATASET_METADATA, {}).get('name', 'Dataset'))
                    st.success(f"Removed {count} outlier row(s) based on '{col_outlier}' IQR factor {factor}!")
                    st.rerun()
            else:
                st.info("No numeric columns available for outlier detection.")

        with tab5:
            st.subheader("Current Working DataFrame")
            st.dataframe(df, use_container_width=True)

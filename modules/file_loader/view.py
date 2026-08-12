"""
Universal File Loader UI Module for ARGUS AI Platform.
Supports drag & drop, folder upload, auto-detection, and file metadata display.
"""
import streamlit as st
import pandas as pd
from modules.base_module import BaseModule
from services.file_service import FileIngestionService
from core.session import SessionManager
from core.exceptions import handle_errors


class FileLoaderModule(BaseModule):
    @property
    def module_id(self) -> str:
        return "file_loader"

    @property
    def name(self) -> str:
        return "Universal File Loader"

    @property
    def icon(self) -> str:
        return "📁"

    @property
    def category(self) -> str:
        return "Ingestion"

    @property
    def order(self) -> int:
        return 10

    @handle_errors(show_traceback=True)
    def render(self) -> None:
        st.title("📁 Universal File Ingestion Engine")
        st.markdown(
            "Upload any data format (**CSV, Excel, JSON, XML, PDF, Word, PowerPoint, ZIP, Images**). "
            "The platform auto-detects encoding, delimiters, and structural schema."
        )

        uploaded_files = st.file_uploader(
            "Drag and drop files or folders here",
            accept_multiple_files=True,
            type=["csv", "xlsx", "xls", "json", "xml", "pdf", "docx", "pptx", "zip", "png", "jpg"]
        )

        if uploaded_files:
            st.success(f"Uploaded {len(uploaded_files)} file(s). Select one to ingest into active workspace:")
            
            selected_file = st.selectbox(
                "Select File to Inspect and Ingest",
                options=uploaded_files,
                format_func=lambda f: f.name
            )

            if selected_file:
                if st.button("🚀 Process & Load into Workspace", type="primary"):
                    with st.spinner(f"Ingesting '{selected_file.name}'..."):
                        df, metadata = FileIngestionService.process_uploaded_file(selected_file)

                        st.subheader("📌 File Ingestion Metadata")
                        st.json(metadata)

                        if df is not None and isinstance(df, pd.DataFrame):
                            SessionManager.set_active_df(df, name=selected_file.name)
                            st.success(f"Successfully loaded '{selected_file.name}' into active session workspace ({len(df)} rows, {len(df.columns)} columns)!")
                            st.dataframe(df.head(20), use_container_width=True)
                        elif metadata.get("text_content"):
                            st.markdown("### 📄 Document Text Preview")
                            st.text_area("Extracted Document Text", metadata["text_content"], height=300)
                        else:
                            st.warning("File ingested successfully, but no structured tabular data could be extracted.")

"""
OCR & Document Extraction UI Module for ARGUS AI Platform.
Extracts text and tabular data from scanned documents, invoices, bank statements, and images.
"""
import streamlit as st
import pandas as pd
from modules.base_module import BaseModule
from services.ocr_service import OCREngineService
from core.session import SessionManager
from core.exceptions import handle_errors


class OCRModule(BaseModule):
    @property
    def module_id(self) -> str:
        return "ocr_engine"

    @property
    def name(self) -> str:
        return "OCR & Document Extractor"

    @property
    def icon(self) -> str:
        return "🔍"

    @property
    def category(self) -> str:
        return "Ingestion"

    @property
    def order(self) -> int:
        return 30

    @handle_errors(show_traceback=True)
    def render(self) -> None:
        st.title("🔍 OCR & Invoice Extraction Engine")
        st.markdown("Extract structured text, key metadata fields, and tabular line items from scanned invoices, bank statements, and image files.")

        ocr_file = st.file_uploader(
            "Upload Image or Scanned Document (PNG, JPG, BMP, TIFF)",
            type=["png", "jpg", "jpeg", "bmp", "tiff"]
        )

        if ocr_file:
            st.image(ocr_file, caption=f"Uploaded Document: {ocr_file.name}", width=400)
            
            if st.button("🚀 Run OCR Engine Pipeline", type="primary"):
                with st.spinner("Processing document image through OCR pipeline..."):
                    bytes_data = ocr_file.getvalue()
                    results = OCREngineService.extract_from_image(bytes_data)

                    st.success("OCR Extraction Completed!")

                    # Key Value Fields
                    if results.get("extracted_fields"):
                        st.subheader("🔑 Extracted Key-Value Metadata")
                        st.json(results["extracted_fields"])

                    # Extracted Tables
                    tables = results.get("tables", [])
                    if tables:
                        st.subheader(f"📊 Extracted Tabular Items ({len(tables)} table found)")
                        for idx, df_table in enumerate(tables):
                            st.markdown(f"**Table #{idx+1}**")
                            st.dataframe(df_table, use_container_width=True)
                            
                            if st.button(f"📥 Load Table #{idx+1} into Session Workspace", key=f"btn_ocr_table_{idx}"):
                                SessionManager.set_active_df(df_table, name=f"OCR_Table_{ocr_file.name}")
                                st.success("Loaded OCR table into workspace!")

                    # Raw Text Area
                    with st.expander("📄 Raw OCR Text Output", expanded=False):
                        st.text_area("Full Extracted Text", results.get("raw_text", ""), height=250)

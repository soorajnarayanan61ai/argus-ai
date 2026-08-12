"""
ARGUS AI Enterprise Data Analyst Platform - Main Streamlit Entrypoint
"""
import streamlit as st
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.core.session import SessionManager
from src.core.database import init_db
from src.core.logger import logger
from src.ui.styles.theme import inject_theme
from src.ui.components.header import render_header
from src.ui.components.sidebar import render_sidebar
from src.ui.components.footer import render_footer

# Import Page Renderers
from src.ui.pages.home import render_home_page
from src.ui.pages.settings_page import render_settings_page
from src.plugins.registry import PluginRegistry
from src.plugins.engine_plugins import register_all_engines

# Configure Streamlit Page
st.set_page_config(
    page_title="ARGUS AI - Enterprise Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    try:
        # Initialize Core Systems & Plugin Extensions
        SessionManager.initialize()
        init_db()
        inject_theme()
        register_all_engines()

        # Render Core Layout Components
        render_header()
        selected_tab = render_sidebar()

        st.markdown("<br>", unsafe_allow_html=True)

        # Dynamic Engine Routing Pipeline
        if "Home" in selected_tab:
            render_home_page()
        elif "Settings" in selected_tab:
            render_settings_page()
        else:
            # Check registered dynamic plugin engines
            plugins = PluginRegistry.get_plugins()
            plugin_found = False
            for p in plugins:
                if p["name"] in selected_tab or selected_tab in p["name"]:
                    p["render"]()
                    plugin_found = True
                    break
            if not plugin_found:
                render_home_page()

        render_footer()

    except Exception as e:
        logger.error(f"Unhandled Streamlit Exception: {str(e)}")
        st.error(f"⚠️ Application Error: {str(e)}")

if __name__ == "__main__":
    main()

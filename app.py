"""
ARGUS AI - Enterprise AI Data Analyst Platform.
Main Streamlit Application Entrypoint.
"""
import streamlit as st
import sys
from pathlib import Path

# Add project root directory to python path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config.settings import settings
from core.logger import logger
from core.session import SessionManager
from core.theme import ThemeManager
from core.plugin_manager import plugin_manager
from core.exceptions import handle_errors

# Import and register modules
from modules.home import HomeModule
from modules.file_loader import FileLoaderModule
from modules.db_connectors import DBConnectorsModule
from modules.ocr import OCRModule
from modules.cleaning import DataCleaningModule
from modules.profiling import ProfilingModule
from modules.analytics import AnalyticsModule
from modules.visualization import VisualizationModule
from modules.settings import SettingsModule


# Configure Streamlit Page
st.set_page_config(
    page_title=f"{settings.get('app.name')} - Enterprise Data Analyst Platform",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)


def register_all_modules() -> None:
    """Register all platform pluggable modules into the PluginManager."""
    modules_to_register = [
        HomeModule(),
        FileLoaderModule(),
        DBConnectorsModule(),
        OCRModule(),
        DataCleaningModule(),
        ProfilingModule(),
        AnalyticsModule(),
        VisualizationModule(),
        SettingsModule(),
    ]
    for mod in modules_to_register:
        try:
            plugin_manager.register_module(mod)
        except Exception as e:
            logger.error(f"Error registering module {mod}: {e}")


def render_sidebar() -> str:
    """Render enterprise sidebar with logo, grouped module navigation, workspace status, and theme toggle."""
    st.sidebar.markdown(
        """
        <div style="text-align: center; padding: 10px 0;">
            <h2 style="margin: 0; background: linear-gradient(135deg, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">👁️ ARGUS AI</h2>
            <p style="font-size: 0.75rem; color: #94a3b8; margin: 0;">ENTERPRISE ANALYST</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.sidebar.markdown("---")

    modules = plugin_manager.list_modules()
    
    # Group by category
    categories = {}
    for mod in modules:
        cat = mod.category
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(mod)

    current_active = SessionManager.get(SessionManager.ACTIVE_MODULE, "home")

    st.sidebar.markdown("### 🧭 Navigation")
    for cat_name, cat_modules in categories.items():
        st.sidebar.markdown(f"**{cat_name.upper()}**")
        for m in cat_modules:
            btn_label = f"{m.icon} {m.name}"
            is_active = (m.module_id == current_active)
            if st.sidebar.button(
                btn_label, 
                key=f"nav_btn_{m.module_id}", 
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                SessionManager.set(SessionManager.ACTIVE_MODULE, m.module_id)
                st.rerun()

    st.sidebar.markdown("---")
    
    # Active Workspace Quick Indicator
    df = SessionManager.get_active_df()
    if df is not None:
        meta = SessionManager.get(SessionManager.DATASET_METADATA, {})
        st.sidebar.info(f"📊 **Loaded Dataset**: `{meta.get('name', 'DataFrame')}` ({len(df):,} rows)")
        if st.sidebar.button("❌ Unload Dataset", use_container_width=True):
            SessionManager.clear_dataset()
            st.rerun()

    # Theme Switcher Quick Toggle
    st.sidebar.markdown("---")
    curr_theme = SessionManager.get(SessionManager.THEME, "dark")
    if st.sidebar.button(f"🌓 Theme: {curr_theme.upper()}", use_container_width=True):
        new_theme = ThemeManager.toggle_theme()
        st.rerun()

    return SessionManager.get(SessionManager.ACTIVE_MODULE, "home")


@handle_errors(show_traceback=True)
def main():
    # Initialize Session & Theme
    SessionManager.initialize_session()
    ThemeManager.apply_theme()

    # Register Pluggable Modules
    register_all_modules()

    # Render Navigation
    active_module_id = render_sidebar()

    # Render Active Module View
    active_module = plugin_manager.get_module(active_module_id)
    active_module.render()


if __name__ == "__main__":
    main()

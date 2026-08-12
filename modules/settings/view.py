"""
Settings UI Module for ARGUS AI Platform.
Provides configuration inspection, theme switching, DB diagnostics, and live UI log streaming.
"""
import streamlit as st
from modules.base_module import BaseModule
from config.settings import settings
from core.database import db_manager
from core.logger import LoggerManager
from core.theme import ThemeManager
from core.exceptions import handle_errors



class SettingsModule(BaseModule):
    @property
    def module_id(self) -> str:
        return "settings"

    @property
    def name(self) -> str:
        return "Platform Settings"

    @property
    def icon(self) -> str:
        return "⚙️"

    @property
    def category(self) -> str:
        return "Core"

    @property
    def order(self) -> int:
        return 999

    @handle_errors(show_traceback=True)
    def render(self) -> None:
        st.title("⚙️ Platform Settings & System Diagnostics")

        tab1, tab2, tab3, tab4 = st.tabs([
            "🎨 Theme & Appearance",
            "🗄️ Database Diagnostics",
            "📜 Live Log Stream",
            "🧩 Module Registry"
        ])

        with tab1:
            st.subheader("Theme & Visual Styling")
            curr_theme = SessionManager.get(SessionManager.THEME, "dark")
            st.write(f"Current Active Theme Mode: **{curr_theme.upper()}**")

            if st.button("🌓 Toggle Light / Dark Theme"):
                new_theme = ThemeManager.toggle_theme()
                st.success(f"Switched theme to {new_theme.upper()}!")
                st.rerun()

        with tab2:
            st.subheader("SQLAlchemy Database Diagnostics")
            health = db_manager.check_health()
            st.json(health)

            if st.button("🔄 Re-Run Database Connection Health Check"):
                st.rerun()

        with tab3:
            st.subheader("Enterprise System Logs Stream")
            st.text_area("Live Application Log Output", value=LoggerManager.get_ui_logs(), height=400)
            if st.button("🔄 Refresh Logs"):
                st.rerun()

        with tab4:
            st.subheader("Registered Pluggable Modules")
            from core.plugin_manager import plugin_manager
            modules = plugin_manager.list_modules()

            mod_data = [
                {
                    "ID": m.module_id,
                    "Name": m.name,
                    "Icon": m.icon,
                    "Category": m.category,
                    "Order": m.order,
                    "Class": m.__class__.__name__
                }
                for m in modules
            ]
            st.table(mod_data)

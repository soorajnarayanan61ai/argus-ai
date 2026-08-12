"""
Theme & Global CSS Provider for ARGUS AI Platform.
Injects custom CSS variables, glassmorphism containers, and dark/light styling rules.
"""
import streamlit as st
from pathlib import Path
from config.settings import settings
from core.session import SessionManager


class ThemeManager:
    """Manages dynamic theme switching and global CSS injection."""

    @classmethod
    def apply_theme(cls) -> None:
        """Inject theme variables and style.css into Streamlit DOM."""
        current_theme = SessionManager.get(SessionManager.THEME, settings.get("theme.default_theme", "dark"))
        
        css_path = Path(settings.base_dir) / "assets" / "css" / "style.css"
        css_content = ""
        if css_path.exists():
            with open(css_path, "r", encoding="utf-8") as f:
                css_content = f.read()

        theme_variables = cls._get_theme_css_vars(current_theme)

        st.markdown(
            f"""
            <style>
            {theme_variables}
            {css_content}
            </style>
            """,
            unsafe_allow_html=True
        )

    @classmethod
    def _get_theme_css_vars(cls, theme_mode: str) -> str:
        if theme_mode == "light":
            return """
            :root {
                --bg-primary: #f8fafc;
                --bg-secondary: #ffffff;
                --card-bg: rgba(255, 255, 255, 0.85);
                --card-border: rgba(226, 232, 240, 0.8);
                --text-primary: #0f172a;
                --text-secondary: #475569;
                --accent-primary: #6366f1;
                --accent-secondary: #8b5cf6;
                --success-color: #10b981;
                --warning-color: #f59e0b;
                --danger-color: #ef4444;
                --shadow-color: rgba(0, 0, 0, 0.05);
            }
            """
        else:  # Dark mode
            return """
            :root {
                --bg-primary: #0f172a;
                --bg-secondary: #1e293b;
                --card-bg: rgba(30, 41, 59, 0.7);
                --card-border: rgba(51, 65, 85, 0.5);
                --text-primary: #f8fafc;
                --text-secondary: #94a3b8;
                --accent-primary: #6366f1;
                --accent-secondary: #8b5cf6;
                --success-color: #10b981;
                --warning-color: #f59e0b;
                --danger-color: #ef4444;
                --shadow-color: rgba(0, 0, 0, 0.3);
            }
            """

    @classmethod
    def toggle_theme(cls) -> str:
        current = SessionManager.get(SessionManager.THEME, "dark")
        new_theme = "light" if current == "dark" else "dark"
        SessionManager.set(SessionManager.THEME, new_theme)
        return new_theme

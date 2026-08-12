"""
Type-safe Streamlit Session State Manager for ARGUS AI Platform.
Ensures session keys are initialized safely and provides clean getter/setters.
"""
import streamlit as st
import pandas as pd
from typing import Any, Optional, Dict


class SessionManager:
    """Encapsulates st.session_state access with default fallbacks and reset abilities."""

    # Pre-defined state keys
    ACTIVE_MODULE = "active_module"
    THEME = "current_theme"
    ACTIVE_DATAFRAME = "active_dataframe"
    DATASET_METADATA = "active_dataset_metadata"
    CLEANED_DATAFRAME = "cleaned_dataframe"
    PROFILING_RESULTS = "profiling_results"
    ANALYTICS_CACHE = "analytics_cache"
    LOGS_STREAM = "logs_stream"
    NOTIFICATION = "system_notification"

    @classmethod
    def initialize_session(cls) -> None:
        """Initialize default values in st.session_state if not present."""
        defaults: Dict[str, Any] = {
            cls.ACTIVE_MODULE: "home",
            cls.THEME: "dark",
            cls.ACTIVE_DATAFRAME: None,
            cls.DATASET_METADATA: {},
            cls.CLEANED_DATAFRAME: None,
            cls.PROFILING_RESULTS: {},
            cls.ANALYTICS_CACHE: {},
            cls.NOTIFICATION: None,
        }

        for key, default_val in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_val

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        cls.initialize_session()
        return st.session_state.get(key, default)

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        st.session_state[key] = value

    @classmethod
    def get_active_df(cls) -> Optional[pd.DataFrame]:
        """Retrieve current working DataFrame."""
        return st.session_state.get(cls.ACTIVE_DATAFRAME, None)

    @classmethod
    def set_active_df(cls, df: pd.DataFrame, name: str = "Uploaded Dataset") -> None:
        """Set active working DataFrame and metadata."""
        st.session_state[cls.ACTIVE_DATAFRAME] = df
        st.session_state[cls.DATASET_METADATA] = {
            "name": name,
            "rows": len(df),
            "columns": len(df.columns),
            "col_names": list(df.columns),
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
        }

    @classmethod
    def clear_dataset(cls) -> None:
        """Reset dataset states."""
        st.session_state[cls.ACTIVE_DATAFRAME] = None
        st.session_state[cls.DATASET_METADATA] = {}
        st.session_state[cls.CLEANED_DATAFRAME] = None
        st.session_state[cls.PROFILING_RESULTS] = {}
        st.session_state[cls.ANALYTICS_CACHE] = {}

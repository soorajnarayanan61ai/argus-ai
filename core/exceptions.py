"""
Custom Exception Hierarchy and Error Boundary Wrapper for ARGUS AI Platform.
"""
import functools
import traceback
import streamlit as st
from typing import Callable, Any


class ArgusBaseException(Exception):
    """Base exception for all ARGUS AI platform errors."""
    def __init__(self, message: str, details: Any = None):
        super().__init__(message)
        self.message = message
        self.details = details


class ConfigurationException(ArgusBaseException):
    """Raised when configuration loading or validation fails."""
    pass


class DatabaseException(ArgusBaseException):
    """Raised during database connection or query execution errors."""
    pass


class FileProcessingException(ArgusBaseException):
    """Raised during file parsing or ingestion errors."""
    pass


class OCRException(ArgusBaseException):
    """Raised during OCR processing errors."""
    pass


class CleaningException(ArgusBaseException):
    """Raised during data cleaning errors."""
    pass


class AnalyticsException(ArgusBaseException):
    """Raised during analytical calculations or forecasting errors."""
    pass


class PluginException(ArgusBaseException):
    """Raised during module initialization or rendering errors."""
    pass


def handle_errors(show_traceback: bool = True):
    """
    Decorator for Streamlit view methods to catch exceptions cleanly and show UI error callouts.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ArgusBaseException as e:
                st.error(f"**[{e.__class__.__name__}]**: {e.message}")
                if e.details:
                    st.info(f"Details: {e.details}")
            except Exception as e:
                st.error(f"**Unexpected Error**: {str(e)}")
                if show_traceback:
                    with st.expander("🔍 Stack Trace Details", expanded=False):
                        st.code(traceback.format_exc(), language="python")
        return wrapper
    return decorator

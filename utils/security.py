"""
Security Utilities for ARGUS AI Platform.
Input sanitization, filename cleaning, and data masking.
"""
import re
from pathlib import Path


def sanitize_filename(filename: str) -> str:
    """Sanitize uploaded filenames to prevent path traversal vulnerabilities."""
    # Remove directory paths
    clean_name = Path(filename).name
    # Replace dangerous characters with underscores
    clean_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', clean_name)
    return clean_name


def mask_sensitive_string(val: str, show_last: int = 4) -> str:
    """Mask credentials or API keys for display."""
    if not val or len(val) <= show_last:
        return "****"
    return "*" * (len(val) - show_last) + val[-show_last:]

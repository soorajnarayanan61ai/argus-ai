"""
General Helper Utilities for ARGUS AI Platform.
"""
import psutil
import os
from typing import Union


def format_bytes(size: Union[int, float]) -> str:
    """Format byte counts into human-readable strings (KB, MB, GB)."""
    if not size or size < 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(size) < 1024.0:
            return f"{size:3.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def get_system_diagnostics() -> dict:
    """Retrieve local system metrics (CPU, RAM, Memory usage)."""
    cpu_usage = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(os.getcwd())
    
    return {
        "cpu_usage_pct": cpu_usage,
        "ram_total": format_bytes(memory.total),
        "ram_available": format_bytes(memory.available),
        "ram_used_pct": memory.percent,
        "disk_free": format_bytes(disk.free),
        "disk_total": format_bytes(disk.total),
    }

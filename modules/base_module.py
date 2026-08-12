"""
Abstract Base Class for ARGUS AI Pluggable Modules.
Every platform module MUST inherit from BaseModule.
"""
from abc import ABC, abstractmethod
import streamlit as st


class BaseModule(ABC):
    """Abstract Base Class for pluggable UI modules."""

    @property
    @abstractmethod
    def module_id(self) -> str:
        """Unique key identifier for the module (e.g. 'file_loader')."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable display name for the module."""
        pass

    @property
    @abstractmethod
    def icon(self) -> str:
        """Icon character or Lucide/Emoji code."""
        pass

    @property
    def category(self) -> str:
        """Category section in sidebar (e.g. 'Core', 'Ingestion', 'Analytics')."""
        return "Core"

    @property
    def order(self) -> int:
        """Sorting order in sidebar menu."""
        return 100

    def initialize(self) -> None:
        """Lifecycle hook executed when module is registered."""
        pass

    @abstractmethod
    def render(self) -> None:
        """Render module UI components in Streamlit."""
        pass

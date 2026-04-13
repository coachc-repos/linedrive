"""
Azure Search Integration Module

This module provides Azure AI Search functionality for the LineDrive tournament management system.

Components:
- AzureSearchTester: Main class for Azure AI Search operations and testing
"""

try:
    from .search_test import AzureSearchTester

    __all__ = ["AzureSearchTester"]
except ImportError:
    # Azure SDK not available - create placeholder
    __all__ = []

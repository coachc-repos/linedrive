"""
Azure Services Integration Module for LineDrive

This module provides Azure cloud services integration for the LineDrive tournament
management system, including:

- Azure Data Lake Storage for raw and processed tournament data
- Azure AI Search for intelligent tournament discovery and retrieval

Submodules:
- storage: Azure Data Lake Storage integration
- search: Azure AI Search integration with RAG capabilities
"""

from .storage import AzureDataLakeUploader

try:
    from .search import AzureSearchTester

    __all__ = ["AzureDataLakeUploader", "AzureSearchTester"]
except ImportError:
    __all__ = ["AzureDataLakeUploader"]

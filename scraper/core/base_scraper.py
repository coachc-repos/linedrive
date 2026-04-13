"""
Base scraper class that all scrapers should inherit from.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import time


class BaseScraper(ABC):
    """
    Abstract base class for all scrapers.
    Provides common functionality and enforces interface for specific scrapers.
    """

    def __init__(self, name: str):
        """
        Initialize the base scraper.

        Args:
            name: Name of the scraper (e.g., 'perfectgame', 'gamechanger')
        """
        self.name = name
        self.logger = logging.getLogger(f"scraper.{name}")
        self.start_time = None

    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the scraper.

        Returns:
            Dictionary containing scraper status information
        """
        return {
            "scraper_name": self.name,
            "status": "ready",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": time.time() - (self.start_time or time.time()),
        }

    @abstractmethod
    def search_tournaments(self, **filters) -> Dict[str, Any]:
        """
        Search for tournaments based on provided filters.

        Args:
            **filters: Search filters (age_group, location, distance, etc.)

        Returns:
            Dictionary containing search results and metadata
        """
        pass

    @abstractmethod
    def get_tournament_details(self, tournament_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific tournament.

        Args:
            tournament_id: Unique identifier for the tournament

        Returns:
            Dictionary containing detailed tournament information
        """
        pass

    def _log_search(self, filters: Dict[str, Any], result_count: int, duration: float):
        """
        Log search operation details.

        Args:
            filters: Search filters used
            result_count: Number of results found
            duration: Time taken for the search
        """
        self.logger.info(
            f"Search completed: {result_count} results in {duration:.2f}s "
            f"with filters: {filters}"
        )

    def _validate_filters(
        self, filters: Dict[str, Any], required_fields: List[str]
    ) -> bool:
        """
        Validate that required filters are present.

        Args:
            filters: Filters to validate
            required_fields: List of required field names

        Returns:
            True if all required fields are present, False otherwise
        """
        missing_fields = [field for field in required_fields if field not in filters]
        if missing_fields:
            self.logger.error(f"Missing required filters: {missing_fields}")
            return False
        return True

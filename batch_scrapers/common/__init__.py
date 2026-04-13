"""
Common Tournament Scraping Utilities

Shared utilities and base classes for all tournament scrapers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import json
import os
from datetime import datetime


class BaseTournamentScraper(ABC):
    """Abstract base class for tournament scrapers"""

    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url

    @abstractmethod
    def search_tournaments(self, filters: Dict) -> Dict:
        """Search for tournaments with given filters"""
        pass

    @abstractmethod
    def build_search_url(self, filters: Dict) -> str:
        """Build search URL from filters"""
        pass


class CommonUtils:
    """Common utility functions for all scrapers"""

    @staticmethod
    def ensure_output_directory():
        """Ensure output directory exists"""
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    @staticmethod
    def save_results(
        data: Dict, filename: str = None, prefix: str = "tournament_results"
    ) -> str:
        """Save tournament results to JSON file"""
        CommonUtils.ensure_output_directory()

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}_{timestamp}.json"

        if not filename.startswith("output/"):
            filepath = f"output/{filename}"
        else:
            filepath = filename

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return filepath
        except Exception:
            return ""

    @staticmethod
    def load_results(filepath: str) -> Dict:
        """Load tournament results from JSON file"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}


class TournamentValidator:
    """Validation utilities for tournament data"""

    REQUIRED_FIELDS = ["name", "location", "age_groups"]
    OPTIONAL_FIELDS = [
        "date_start",
        "date_end",
        "organizer",
        "tournament_type",
        "teams",
        "url",
    ]

    @staticmethod
    def validate_tournament(tournament: Dict) -> bool:
        """Validate tournament data structure"""
        for field in TournamentValidator.REQUIRED_FIELDS:
            if not tournament.get(field):
                return False
        return True

    @staticmethod
    def clean_tournament_data(tournament: Dict) -> Dict:
        """Clean and standardize tournament data"""
        cleaned = {}

        # Copy required fields
        for field in TournamentValidator.REQUIRED_FIELDS:
            cleaned[field] = tournament.get(field, "").strip()

        # Copy optional fields if they exist
        for field in TournamentValidator.OPTIONAL_FIELDS:
            if field in tournament and tournament[field]:
                cleaned[field] = str(tournament[field]).strip()

        # Add metadata
        cleaned["scraped_at"] = tournament.get("scraped_at", datetime.now().isoformat())
        cleaned["source"] = tournament.get("source", "unknown")

        return cleaned


class FilterValidator:
    """Common filter validation utilities"""

    @staticmethod
    def validate_state(state: str) -> bool:
        """Validate US state abbreviation"""
        us_states = {
            "AL",
            "AK",
            "AZ",
            "AR",
            "CA",
            "CO",
            "CT",
            "DE",
            "FL",
            "GA",
            "HI",
            "ID",
            "IL",
            "IN",
            "IA",
            "KS",
            "KY",
            "LA",
            "ME",
            "MD",
            "MA",
            "MI",
            "MN",
            "MS",
            "MO",
            "MT",
            "NE",
            "NV",
            "NH",
            "NJ",
            "NM",
            "NY",
            "NC",
            "ND",
            "OH",
            "OK",
            "OR",
            "PA",
            "RI",
            "SC",
            "SD",
            "TN",
            "TX",
            "UT",
            "VT",
            "VA",
            "WA",
            "WV",
            "WI",
            "WY",
        }
        return state.upper() in us_states

    @staticmethod
    def validate_age_group(age_group: str) -> bool:
        """Validate age group format"""
        import re

        # Match patterns like 10U, 12U, etc.
        pattern = r"^\d{1,2}U$"
        return bool(re.match(pattern, age_group.upper()))

    @staticmethod
    def validate_radius(radius: int) -> bool:
        """Validate search radius"""
        return 1 <= radius <= 500  # 1 to 500 miles

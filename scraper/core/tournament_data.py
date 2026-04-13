"""
Data structures and utilities for tournament data handling.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime
import json


@dataclass
class Tournament:
    """
    Data class representing a tournament.
    """

    id: str
    name: str
    age_group: str
    start_date: str
    end_date: str
    location: str
    city: str
    state: str
    distance_miles: Optional[float] = None
    entry_fee: Optional[str] = None
    team_count: Optional[int] = None
    contact_info: Optional[str] = None
    website_url: Optional[str] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert tournament to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "age_group": self.age_group,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "location": self.location,
            "city": self.city,
            "state": self.state,
            "distance_miles": self.distance_miles,
            "entry_fee": self.entry_fee,
            "team_count": self.team_count,
            "contact_info": self.contact_info,
            "website_url": self.website_url,
            "description": self.description,
        }


class TournamentData:
    """
    Utility class for handling tournament data operations.
    """

    @staticmethod
    def create_search_result(
        tournaments: List[Tournament],
        search_filters: Dict[str, Any],
        duration_seconds: float,
        total_found: int,
    ) -> Dict[str, Any]:
        """
        Create a standardized search result structure.

        Args:
            tournaments: List of Tournament objects
            search_filters: Filters used in the search
            duration_seconds: Time taken for the search
            total_found: Total number of tournaments found

        Returns:
            Standardized search result dictionary
        """
        return {
            "search_metadata": {
                "timestamp": datetime.now().isoformat(),
                "filters": search_filters,
                "duration_seconds": round(duration_seconds, 2),
                "total_found": total_found,
                "returned_count": len(tournaments),
            },
            "tournaments": [tournament.to_dict() for tournament in tournaments],
        }

    @staticmethod
    def validate_tournament_data(tournament_dict: Dict[str, Any]) -> bool:
        """
        Validate that tournament data has required fields.

        Args:
            tournament_dict: Tournament data as dictionary

        Returns:
            True if valid, False otherwise
        """
        required_fields = [
            "id",
            "name",
            "age_group",
            "start_date",
            "end_date",
            "location",
        ]
        return all(
            field in tournament_dict and tournament_dict[field]
            for field in required_fields
        )

    @staticmethod
    def filter_tournaments_by_distance(
        tournaments: List[Tournament], max_distance: float
    ) -> List[Tournament]:
        """
        Filter tournaments by maximum distance.

        Args:
            tournaments: List of tournaments to filter
            max_distance: Maximum distance in miles

        Returns:
            Filtered list of tournaments
        """
        return [
            tournament
            for tournament in tournaments
            if tournament.distance_miles is not None
            and tournament.distance_miles <= max_distance
        ]

    @staticmethod
    def sort_tournaments_by_date(tournaments: List[Tournament]) -> List[Tournament]:
        """
        Sort tournaments by start date.

        Args:
            tournaments: List of tournaments to sort

        Returns:
            Sorted list of tournaments
        """
        return sorted(tournaments, key=lambda t: t.start_date)

    @staticmethod
    def export_to_json(tournaments: List[Tournament], filepath: str) -> bool:
        """
        Export tournaments to JSON file.

        Args:
            tournaments: List of tournaments to export
            filepath: Path to save the JSON file

        Returns:
            True if successful, False otherwise
        """
        try:
            tournament_dicts = [tournament.to_dict() for tournament in tournaments]
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(tournament_dicts, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

"""
Perfect Game Filter Utilities

Helper classes and functions for managing Perfect Game tournament search filters.
"""

from datetime import datetime, timedelta
from typing import Dict, List


class PerfectGameFilters:
    """Utility class for managing Perfect Game search filters"""

    # City coordinates for location-based searches
    CITY_COORDS = {
        "houston": {"lat": 29.786, "lng": -95.3885},
        "dallas": {"lat": 32.7767, "lng": -96.7970},
        "austin": {"lat": 30.2672, "lng": -97.7431},
        "san antonio": {"lat": 29.4241, "lng": -98.4936},
        "fort worth": {"lat": 32.7555, "lng": -97.3308},
        "el paso": {"lat": 31.7619, "lng": -106.4850},
        "arlington": {"lat": 32.7357, "lng": -97.1081},
        "corpus christi": {"lat": 27.8006, "lng": -97.3964},
        "plano": {"lat": 33.0198, "lng": -96.6989},
        "lubbock": {"lat": 33.5779, "lng": -101.8552},
    }

    # Legacy Houston coordinates for backward compatibility
    HOUSTON_COORDS = CITY_COORDS["houston"]

    # Common age groups in Perfect Game
    AGE_GROUPS = [
        "6U",
        "7U",
        "8U",
        "9U",
        "10U",
        "11U",
        "12U",
        "13U",
        "14U",
        "15U",
        "16U",
        "17U",
        "18U",
    ]

    # Sport types
    SPORT_TYPES = ["Baseball", "Softball", "Fastpitch"]

    # US States with abbreviations
    STATES = {
        "TX": "Texas",
        "CA": "California",
        "FL": "Florida",
        "NY": "New York",
        "GA": "Georgia",
        "IL": "Illinois",
        "OH": "Ohio",
        "NC": "North Carolina",
        "VA": "Virginia",
        "AZ": "Arizona",  # Add more as needed
    }

    @classmethod
    def get_default_filters(cls) -> Dict:
        """Get default search filters for Houston, TX 10U Baseball"""
        end_date = datetime.now() + timedelta(days=35)

        return {
            "state": "TX",
            "city": "Houston",
            "lat": cls.HOUSTON_COORDS["lat"],
            "lng": cls.HOUSTON_COORDS["lng"],
            "radius": 25,
            "sport_type": "Baseball",
            "age_group": "10U",
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
        }

    @classmethod
    def create_filters(cls, **kwargs) -> Dict:
        """Create filter dictionary with defaults"""
        filters = cls.get_default_filters()

        # Update with provided values
        for key, value in kwargs.items():
            if key in ["state", "city", "sport_type", "age_group"]:
                filters[key] = value
            elif key == "radius":
                filters[key] = int(value)
            elif key in ["lat", "lng"]:
                filters[key] = float(value)
            elif key in ["start_date", "end_date"]:
                filters[key] = value

        return filters

    @classmethod
    def validate_filters(cls, filters: Dict) -> Dict:
        """Validate and clean filter values"""
        validated = {}

        # Required fields with defaults
        validated["state"] = filters.get("state", "TX")
        validated["city"] = filters.get("city", "Houston")
        validated["sport_type"] = filters.get("sport_type", "Baseball")
        validated["age_group"] = filters.get("age_group", "10U")

        # Location coordinates
        if "lat" in filters and "lng" in filters:
            validated["lat"] = float(filters["lat"])
            validated["lng"] = float(filters["lng"])
        else:
            validated.update(cls.HOUSTON_COORDS)

        # Search radius
        validated["radius"] = int(filters.get("radius", 25))

        # Date range
        if "start_date" in filters:
            validated["start_date"] = filters["start_date"]
        else:
            validated["start_date"] = datetime.now().strftime("%Y-%m-%d")

        if "end_date" in filters:
            validated["end_date"] = filters["end_date"]
        else:
            end_date = datetime.now() + timedelta(days=35)
            validated["end_date"] = end_date.strftime("%Y-%m-%d")

        return validated

    @classmethod
    def get_date_range_filters(cls, range_type: str) -> Dict:
        """Get pre-defined date range filters"""
        today = datetime.now()

        if range_type == "this_month":
            end_date = today + timedelta(days=35)
        elif range_type == "next_month":
            start_date = today + timedelta(days=30)
            end_date = start_date + timedelta(days=30)
            return {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
            }
        elif range_type == "this_year":
            end_date = datetime(today.year, 12, 31)
        else:  # Default to next 35 days
            end_date = today + timedelta(days=35)

        return {
            "start_date": today.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
        }

    @classmethod
    def format_filters_display(cls, filters: Dict) -> str:
        """Format filters for display in console"""
        lines = []
        lines.append(
            f"   📍 Location: {filters.get('city', 'Unknown')}, {filters.get('state', 'Unknown')}"
        )
        lines.append(f"   📏 Radius: {filters.get('radius', 25)} miles")
        lines.append(f"   👥 Age Group: {filters.get('age_group', 'Unknown')}")
        lines.append(f"   ⚾ Sport: {filters.get('sport_type', 'Unknown')}")

        if "start_date" in filters:
            lines.append(
                f"   📅 Date Range: {filters['start_date']} to {filters.get('end_date', 'Unknown')}"
            )

        return "\n".join(lines)


class FilterBuilder:
    """Interactive filter builder for console applications"""

    def __init__(self):
        self.filters = PerfectGameFilters.get_default_filters()

    def set_location(self, state: str, city: str, radius: int = 25):
        """Set location-based filters"""
        self.filters["state"] = state
        self.filters["city"] = city
        self.filters["radius"] = radius

        # Set coordinates based on known cities
        city_key = city.lower()
        if city_key in PerfectGameFilters.CITY_COORDS:
            self.filters.update(PerfectGameFilters.CITY_COORDS[city_key])
        else:
            # If city not found, keep current coordinates or use Houston as default
            if "lat" not in self.filters or "lng" not in self.filters:
                self.filters.update(PerfectGameFilters.HOUSTON_COORDS)

    def set_age_group(self, age_group: str):
        """Set age group filter"""
        if age_group in PerfectGameFilters.AGE_GROUPS:
            self.filters["age_group"] = age_group

    def set_sport(self, sport_type: str):
        """Set sport type filter"""
        if sport_type in PerfectGameFilters.SPORT_TYPES:
            self.filters["sport_type"] = sport_type

    def set_date_range(self, start_date: str, end_date: str):
        """Set custom date range"""
        self.filters["start_date"] = start_date
        self.filters["end_date"] = end_date

    def get_filters(self) -> Dict:
        """Get current filter configuration"""
        return self.filters.copy()

    def reset_to_defaults(self):
        """Reset filters to defaults"""
        self.filters = PerfectGameFilters.get_default_filters()

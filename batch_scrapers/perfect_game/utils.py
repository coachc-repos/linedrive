"""
Perfect Game Utilities

Helper functions and utilities for Perfect Game tournament scraping.
"""

import json
import os
from datetime import datetime
from typing import Dict, List


class PerfectGameUtils:
    """Utility functions for Perfect Game scraper"""

    @staticmethod
    def ensure_output_directory():
        """Ensure output directory exists"""
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    @staticmethod
    def save_json_results(data: Dict, filename: str = None) -> str:
        """Save results to JSON file with timestamp"""
        PerfectGameUtils.ensure_output_directory()

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"perfect_game_results_{timestamp}.json"

        if not filename.startswith("output/"):
            filepath = f"output/{filename}"
        else:
            filepath = filename

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return filepath
        except Exception as e:
            print(f"Error saving results: {e}")
            return ""

    @staticmethod
    def load_json_results(filepath: str) -> Dict:
        """Load results from JSON file"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading results: {e}")
            return {}

    @staticmethod
    def format_tournament_display(tournament: Dict) -> str:
        """Format single tournament for console display"""
        lines = []
        lines.append(f"🏆 {tournament.get('name', 'Unknown Tournament')}")
        lines.append(f"   📅 Date: {tournament.get('date_start', 'TBD')}")
        lines.append(f"   📍 Location: {tournament.get('location', 'TBD')}")
        lines.append(f"   👥 Ages: {tournament.get('age_groups', 'TBD')}")
        lines.append(f"   🏟️  Type: {tournament.get('tournament_type', 'Tournament')}")

        if tournament.get("teams"):
            lines.append(f"   👨‍👩‍👧‍👦 Teams: {tournament['teams']}")

        if tournament.get("url"):
            lines.append(f"   🔗 URL: {tournament['url']}")

        return "\n".join(lines)

    @staticmethod
    def format_results_summary(results: Dict) -> str:
        """Format search results summary for console"""
        lines = []
        lines.append("📊 SEARCH RESULTS SUMMARY")
        lines.append("=" * 50)

        if results.get("success"):
            count = results.get("tournament_count", 0)
            duration = results.get("search_duration", 0)
            lines.append(f"✅ Search completed successfully")
            lines.append(f"🏆 Found {count} tournaments")
            lines.append(f"⏱️  Search duration: {duration}s")

            if "filters_applied" in results:
                lines.append(f"🔍 Filters applied:")
                filters = results["filters_applied"]
                lines.append(
                    f"   📍 {filters.get('city', 'Unknown')}, {filters.get('state', 'Unknown')}"
                )
                lines.append(f"   👥 {filters.get('age_group', 'Unknown')}")
                lines.append(f"   ⚾ {filters.get('sport_type', 'Unknown')}")
        else:
            lines.append(f"❌ Search failed: {results.get('error', 'Unknown error')}")

        return "\n".join(lines)

    @staticmethod
    def print_tournament_list(tournaments: List[Dict], max_display: int = 10):
        """Print formatted tournament list to console"""
        if not tournaments:
            print("📭 No tournaments found")
            return

        print(f"🏆 Tournament Details:")
        print()

        for i, tournament in enumerate(tournaments[:max_display], 1):
            print(f"{i}. {tournament.get('name', 'Unknown Tournament')}")
            print(f"   📅 Date: {tournament.get('date_start', 'TBD')}")
            print(f"   📍 Location: {tournament.get('location', 'TBD')}")
            print(f"   👥 Ages: {tournament.get('age_groups', 'TBD')}")
            print(f"   🏟️  Type: {tournament.get('tournament_type', 'Tournament')}")
            print(f"   🔧 Source: {tournament.get('source', 'unknown')}")
            print()

        if len(tournaments) > max_display:
            remaining = len(tournaments) - max_display
            print(f"   ... and {remaining} more tournaments")
            print()

    @staticmethod
    def create_search_summary(filters: Dict, results: Dict) -> Dict:
        """Create comprehensive search summary"""
        return {
            "search_metadata": {
                "timestamp": datetime.now().isoformat(),
                "filters_used": filters,
                "search_duration": results.get("search_duration", 0),
                "success": results.get("success", False),
            },
            "results": {
                "tournament_count": results.get("tournament_count", 0),
                "tournaments": results.get("tournaments", []),
                "search_url": results.get("search_url", ""),
                "error": results.get("error", None),
            },
        }

    @staticmethod
    def validate_tournament_data(tournament: Dict) -> bool:
        """Validate tournament data structure"""
        required_fields = ["name", "location", "age_groups"]

        for field in required_fields:
            if not tournament.get(field):
                return False

        return True

    @staticmethod
    def clean_tournament_name(name: str) -> str:
        """Clean and normalize tournament name"""
        if not name:
            return ""

        # Remove extra whitespace
        cleaned = " ".join(name.split())

        # Limit length
        if len(cleaned) > 100:
            cleaned = cleaned[:97] + "..."

        return cleaned

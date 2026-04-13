"""
Tournament scraper module with support for multiple scraping platforms.
"""

# Core scraping functionality
from .core import BaseScraper, SeleniumUtils, TournamentData

# Platform-specific scrapers
from .perfectgame import PerfectGameScraper

# Legacy scraper for backward compatibility
from .legacy_scraper import TournamentScraper

__all__ = [
    "BaseScraper",
    "SeleniumUtils",
    "TournamentData",
    "PerfectGameScraper",
    "TournamentScraper",  # Legacy compatibility
]

#!/usr/bin/env python3
"""
Console UI Package

Centralized location for all console-based user interfaces and menus
for the LineDrive tournament system.

Organized by category:
- scrapers/: Data scraping interfaces
- social_media/: Social media management interfaces
- automation/: AI and automated workflow interfaces
"""

# Import from organized subdirectories
try:
    # Scraper UIs
    from .scrapers.batch_scraper_ui import main as batch_scraper_main
    from .scrapers.tournament_scraper_ui import main as tournament_scraper_main

    # Automation UIs
    from .automation.batch_job_runner import BatchJobRunner
    from .automation.autogen_tournament_ui import AutoGenTournamentUI

    # Social Media UIs
    from .social_media.ai_tweet_generator import AITweetGenerator

    ORGANIZED_IMPORTS_AVAILABLE = True
except ImportError:
    # Fallback for any missing dependencies
    ORGANIZED_IMPORTS_AVAILABLE = False

# Menu Classes (legacy support)
try:
    from .scrapers.url_scraper_menu import URLScraperMenu
    from .scrapers.youtube_transcript_menu import YouTubeTranscriptMenu
    from .scrapers.perfect_game_menu import TournamentSearchMenu
except ImportError:
    pass

__all__ = [
    "batch_scraper_main",
    "tournament_scraper_main",
    "BatchJobRunner",
    "URLScraperMenu",
    "YouTubeTranscriptMenu",
    "TournamentSearchMenu",
    "ORGANIZED_IMPORTS_AVAILABLE",
]

# Add components to exports if available
if ORGANIZED_IMPORTS_AVAILABLE:
    __all__.extend(["AutoGenTournamentUI", "AITweetGenerator"])

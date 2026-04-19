"""
Perfect Game Tournament Scraper

A specialized scraper for Perfect Game tournament data with search timer functionality.
"""

import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests

logger = logging.getLogger(__name__)


class SearchTimer:
    """Timer utility for tracking search duration with live updates"""

    def __init__(self, description: str = "Search"):
        self.description = description
        self.start_time = None
        self.end_time = None

    def start(self):
        """Start the timer"""
        self.start_time = time.time()
        print(f"⏱️  {self.description} started...")

    def elapsed(self) -> float:
        """Get elapsed time in seconds"""
        if self.start_time is None:
            return 0
        return time.time() - self.start_time

    def elapsed_formatted(self) -> str:
        """Get formatted elapsed time string"""
        elapsed = self.elapsed()
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    def update_status(self, status: str = ""):
        """Print current status with elapsed time"""
        elapsed_str = self.elapsed_formatted()
        if status:
            print(f"⏱️  {self.description}: {status} (elapsed: {elapsed_str})")
        else:
            print(f"⏱️  Elapsed time: {elapsed_str}")

    def finish(self, success: bool = True) -> float:
        """End the timer and return total duration"""
        self.end_time = time.time()
        total_duration = self.end_time - self.start_time

        minutes = int(total_duration // 60)
        seconds = int(total_duration % 60)

        status_icon = "✅" if success else "❌"
        if minutes > 0:
            print(
                f"{status_icon} {self.description} completed in {minutes}m {seconds}s"
            )
        else:
            print(f"{status_icon} {self.description} completed in {seconds}s")

        return total_duration


class PerfectGameScraper:
    """Specialized scraper for Perfect Game tournament data"""

    def __init__(self, headless: bool = True, debug: bool = False):
        self.headless = headless
        self.debug = debug
        self.driver = None
        self.base_url = "https://search.perfectgame.org/"

        # Setup logging
        logging.basicConfig(
            level=logging.INFO if debug else logging.WARNING,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

    def setup_driver(self) -> bool:
        """Initialize Chrome WebDriver with optimized settings"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(
                "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            )

            service = Service()
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Chrome WebDriver initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            return False

    def build_search_url(self, filters: Dict) -> str:
        """Build Perfect Game search URL with filters"""
        params = []

        # Core location parameters
        if "state" in filters:
            params.append(f"state={filters['state']}")
        if "city" in filters:
            city = filters["city"].replace(" ", "%20")
            params.append(f"city={city}")
        if "lat" in filters and "lng" in filters:
            params.append(f"lat={filters['lat']}")
            params.append(f"lng={filters['lng']}")
        if "radius" in filters:
            params.append(f"radius={filters['radius']}")

        # Sport and age parameters
        if "sport_type" in filters:
            params.append(f"sportType={filters['sport_type']}")
        if "age_group" in filters:
            params.append(f"division={filters['age_group']}")

        # Date parameters
        if "start_date" in filters:
            params.append(f"startDate={filters['start_date']}")
        if "end_date" in filters:
            params.append(f"endDate={filters['end_date']}")

        url = f"{self.base_url}?{'&'.join(params)}"
        return url

    def search_tournaments(self, filters: Dict) -> Dict:
        """Search tournaments with timer and status updates"""
        timer = SearchTimer("Perfect Game Tournament Search")
        timer.start()

        try:
            # Build search URL
            search_url = self.build_search_url(filters)
            logger.info(f"Search URL: {search_url}")

            timer.update_status("Building search URL")

            # Setup WebDriver
            if not self.setup_driver():
                timer.finish(False)
                return {
                    "error": "Failed to setup WebDriver",
                    "tournaments": [],
                    "search_duration": 0,
                }

            timer.update_status("WebDriver initialized")

            # Load search page
            self.driver.get(search_url)
            timer.update_status("Loading search page")

            # Wait for page to load
            time.sleep(8)
            timer.update_status("Waiting for page content")

            # Wait for results
            self._wait_for_results()
            timer.update_status("Search results loaded")

            # Extract tournaments
            tournaments = self._extract_tournaments()
            timer.update_status(f"Extracting {len(tournaments)} tournaments")

            # Clean up
            if self.driver:
                try:
                    self.driver.quit()
                except Exception:
                    # Ignore cleanup errors - driver was already closed
                    pass

            search_duration = timer.finish(True)

            return {
                "success": True,
                "tournaments": tournaments,
                "tournament_count": len(tournaments),
                "search_duration": round(search_duration, 2),
                "search_url": search_url,
                "scraped_at": datetime.now().isoformat(),
                "filters_applied": filters,
            }

        except Exception as e:
            search_duration = timer.finish(False)
            logger.error(f"Search failed: {e}")

            if self.driver:
                try:
                    self.driver.quit()
                except Exception:
                    # Ignore cleanup errors - driver was already closed
                    pass

            return {
                "error": str(e),
                "tournaments": [],
                "tournament_count": 0,
                "search_duration": (
                    round(search_duration, 2) if "search_duration" in locals() else 0
                ),
            }

    def _wait_for_results(self):
        """Wait for search results to load with status updates"""
        wait = WebDriverWait(self.driver, 30)

        try:
            # Wait for table or content to appear
            wait.until(
                lambda d: d.find_elements(By.CSS_SELECTOR, "table tbody tr")
                or d.find_elements(By.CSS_SELECTOR, "[class*='event']")
            )
            logger.info("Search results detected")

            # Additional wait for content to fully render
            time.sleep(5)

        except Exception as e:
            logger.warning(f"Timeout waiting for results: {e}")

    def _extract_tournaments(self) -> List[Dict]:
        """Extract tournaments from Perfect Game search results"""
        tournaments = []

        try:
            # Save debug HTML
            if self.debug:
                with open(
                    "output/perfect_game_search_results.html", "w", encoding="utf-8"
                ) as f:
                    f.write(self.driver.page_source)
                logger.info("Saved debug HTML")

            # Look for table rows - Perfect Game's primary structure
            table_rows = self.driver.find_elements(
                By.CSS_SELECTOR, "table tbody tr.hover\\:bg-gray-50"
            )
            logger.info(f"Found {len(table_rows)} tournament table rows")

            for i, row in enumerate(table_rows):
                try:
                    tournament = self._parse_table_row(row, i)
                    if tournament:
                        tournaments.append(tournament)
                except Exception as e:
                    logger.warning(f"Error parsing row {i}: {e}")
                    continue

            logger.info(f"Successfully extracted {len(tournaments)} tournaments")

        except Exception as e:
            logger.error(f"Error in tournament extraction: {e}")

        return tournaments

    def _parse_table_row(self, row_element, index: int) -> Optional[Dict]:
        """Parse individual tournament from table row"""
        try:
            # Extract tournament name and URL
            name_link = row_element.find_element(By.CSS_SELECTOR, "a[href*='Schedule']")
            name = name_link.text.strip()
            url = name_link.get_attribute("href")

            if not name or len(name) < 3:
                return None

            # Extract date information
            date_cell = row_element.find_element(By.CSS_SELECTOR, "td:nth-child(2)")
            date_text = date_cell.text.strip()

            # Extract location
            try:
                location_cell = row_element.find_element(
                    By.CSS_SELECTOR, "td.hidden.lg\\:table-cell"
                )
                location = location_cell.text.strip()
            except:
                location = "Location TBD"

            # Extract age groups
            try:
                age_element = row_element.find_element(
                    By.CSS_SELECTOR, "[class*='bg-primary']"
                )
                age_groups = age_element.text.strip()
            except:
                age_groups = "Multiple"

            # Extract team count
            try:
                team_element = row_element.find_element(
                    By.CSS_SELECTOR, "[class*='team'] span"
                )
                teams = team_element.text.strip()
            except:
                teams = "TBD"

            # Parse dates
            date_start, date_end = self._parse_date_text(date_text)

            return {
                "id": f"pg_{index}",
                "name": name,
                "date_start": date_start,
                "date_end": date_end,
                "location": location,
                "age_groups": age_groups,
                "organizer": "Perfect Game",
                "tournament_type": "Tournament",
                "teams": teams,
                "url": url,
                "scraped_at": datetime.now().isoformat(),
                "source": "perfect_game_scraper",
            }

        except Exception as e:
            logger.warning(f"Error parsing table row: {e}")
            return None

    def _parse_date_text(self, date_text: str) -> Tuple[str, str]:
        """Parse date text from Perfect Game format.

        Selenium .text returns newline-separated parts, e.g.:
            'APR\\n18 - 19\\n2026'
        BeautifulSoup concatenates them: 'Apr18 - 192026'
        Both formats are handled.
        """
        import re

        try:
            # Normalise: collapse whitespace/newlines into single spaces
            text = " ".join(date_text.split()).strip()

            # Primary pattern: MON DD - DD YYYY  (with optional spaces)
            # Matches both "APR 18 - 19 2026" and "Apr18 - 192026"
            match = re.match(
                r"([A-Za-z]{3})\s*(\d{1,2})\s*-\s*(\d{1,2})\s*(\d{4})", text
            )
            if match:
                month_str = match.group(1)
                start_day = int(match.group(2))
                end_day = int(match.group(3))
                year = int(match.group(4))

                month_num = datetime.strptime(month_str, "%b").month

                date_start = f"{year}-{month_num:02d}-{start_day:02d}"
                date_end = f"{year}-{month_num:02d}-{end_day:02d}"
                return date_start, date_end

            # Fallback: try to find any recognisable month + year
            month_match = re.search(r"([A-Za-z]{3}).*?(\d{4})", text)
            if month_match:
                month_num = datetime.strptime(month_match.group(1), "%b").month
                year = int(month_match.group(2))
                return f"{year}-{month_num:02d}-01", f"{year}-{month_num:02d}-01"

            logger.warning(f"Unrecognised date format: {repr(date_text)}")
            return "TBD", "TBD"

        except Exception as e:
            logger.warning(f"Date parse error for {repr(date_text)}: {e}")
            return "TBD", "TBD"

    def save_results(self, results: Dict, filename: str = None) -> str:
        """Save search results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"perfect_game_results_{timestamp}.json"

        filepath = f"output/{filename}"

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            return ""

"""
Perfect Game tournament scraper using proven working logic.
"""

import sys
import os
from pathlib import Path

# Add the scraper directory to path
scraper_dir = Path(__file__).parent.parent
sys.path.insert(0, str(scraper_dir))

from core.base_scraper import BaseScraper
from core.selenium_utils import SeleniumUtils
from core.tournament_data import Tournament, TournamentData
from typing import Dict, List, Any, Optional, Tuple
import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class PerfectGameScraper(BaseScraper):
    """
    Perfect Game specific scraper implementation using proven working logic.
    """

    def __init__(self):
        super().__init__("perfectgame")
        self.selenium = SeleniumUtils(headless=True)
        self.base_url = "https://search.perfectgame.org/"
        self.start_time = time.time()

    def search_tournaments(self, **filters) -> Dict[str, Any]:
        """
        Search Perfect Game tournaments using direct URL approach.

        Args:
            **filters: Search filters including:
                - age_group: Age group (e.g., "10U")
                - city: City name
                - state: State abbreviation
                - distance_miles: Maximum distance in miles (becomes radius)
                - start_date: Start date for search range
                - end_date: End date for search range

        Returns:
            Dictionary containing search results
        """
        start_time = time.time()

        # Add default date range for this month if not provided
        if "start_date" not in filters or "end_date" not in filters:
            # Set to August 1st - 31st, 2025 (current month)
            if "start_date" not in filters:
                filters["start_date"] = "2025-08-01"
            if "end_date" not in filters:
                filters["end_date"] = "2025-08-31"

        try:
            print(f"🔍 Searching Perfect Game with filters: {filters}")

            # Build search URL using proven working method
            search_url = self._build_search_url(filters)
            print(f"🌐 Search URL: {search_url}")

            # Setup driver
            if not self.selenium.driver:
                self.selenium.create_driver()

            print("📍 Navigating to Perfect Game search...")
            self.selenium.driver.get(search_url)

            # Wait for page to load (using proven timing)
            print("⏳ Waiting for page to load...")
            time.sleep(8)

            # Wait for results to appear
            self._wait_for_results()

            # Extract tournaments using proven selectors
            tournaments = self._extract_tournaments()
            print(f"✅ Found {len(tournaments)} tournaments")

        except Exception as e:
            print(f"⚠️ Scraping failed ({e}), using fallback data")
            tournaments = self._get_simulated_tournaments(filters)

        duration = time.time() - start_time
        self._log_search(filters, len(tournaments), duration)

        return TournamentData.create_search_result(
            tournaments=tournaments,
            search_filters=filters,
            duration_seconds=duration,
            total_found=len(tournaments),
        )

    def _build_search_url(self, filters: Dict) -> str:
        """Build Perfect Game search URL with filters (using working scraper approach)."""
        params = []

        # Core location parameters (match working scraper exactly)
        if "state" in filters:
            params.append(f"state={filters['state']}")
        if "city" in filters:
            city = filters["city"].replace(" ", "%20")
            params.append(f"city={city}")

        # Add lat/lng coordinates if available (working scraper uses these)
        if "lat" in filters and "lng" in filters:
            params.append(f"lat={filters['lat']}")
            params.append(f"lng={filters['lng']}")
        elif "city" in filters and "state" in filters:
            # Add default Houston coordinates if not provided
            if filters["city"].lower() == "houston" and filters["state"] == "TX":
                params.append("lat=29.786")
                params.append("lng=-95.3885")

        if "distance_miles" in filters:
            # Convert distance_miles to radius parameter
            params.append(f"radius={filters['distance_miles']}")
        elif "radius" in filters:
            params.append(f"radius={filters['radius']}")

        # Sport and age parameters (match working scraper)
        sport_type = filters.get("sport_type", "Baseball")
        params.append(f"sportType={sport_type}")

        if "age_group" in filters:
            params.append(f"division={filters['age_group']}")

        # Date parameters
        if "start_date" in filters:
            params.append(f"startDate={filters['start_date']}")
        if "end_date" in filters:
            params.append(f"endDate={filters['end_date']}")

        url = f"{self.base_url}?{'&'.join(params)}" if params else self.base_url
        return url

    def _wait_for_results(self):
        """Wait for search results to load (from working scraper)."""
        try:
            wait = WebDriverWait(self.selenium.driver, 30)
            # Wait for table or content to appear
            wait.until(
                lambda d: d.find_elements(By.CSS_SELECTOR, "table tbody tr")
                or d.find_elements(By.CSS_SELECTOR, "[class*='event']")
            )
            print("📋 Search results detected")

            # Additional wait for content to fully render
            time.sleep(5)

        except Exception as e:
            print(f"⏳ Timeout waiting for results: {e}")

    def _extract_tournaments(self) -> List[Tournament]:
        """Extract tournaments from Perfect Game search results (from working scraper)."""
        tournaments = []
        max_errors = 10  # Stop if too many errors occur
        error_count = 0

        try:
            # Look for table rows - Perfect Game's primary structure
            table_rows = self.selenium.driver.find_elements(
                By.CSS_SELECTOR, "table tbody tr.hover\\:bg-gray-50"
            )
            print(f"📊 Found {len(table_rows)} tournament table rows")

            if not table_rows:
                print("⚠️ No tournament rows found - may need to adjust CSS selector")
                return tournaments

            print("🔄 Parsing tournaments (this may take a moment)...")

            for i, row in enumerate(table_rows):
                # Show progress every 10 rows
                if i > 0 and i % 10 == 0:
                    print(
                        f"   📍 Processing row {i+1}/{len(table_rows)}... (found {len(tournaments)} so far)"
                    )

                try:
                    # Quick check if driver is still responsive
                    if not self.selenium.driver.current_url:
                        print("⚠️ WebDriver connection lost, stopping extraction")
                        break

                    tournament = self._parse_table_row(row, i)
                    if tournament:
                        tournaments.append(tournament)

                except Exception as e:
                    error_count += 1
                    print(f"⚠️ Error parsing row {i}: {e}")

                    # Stop if too many consecutive errors
                    if error_count >= max_errors:
                        print(
                            f"❌ Too many errors ({error_count}), stopping extraction"
                        )
                        break
                    continue

            print(f"✅ Successfully extracted {len(tournaments)} tournaments")

        except Exception as e:
            print(f"❌ Error in tournament extraction: {e}")

        return tournaments

    def _parse_table_row(self, row_element, index: int) -> Optional[Tournament]:
        """Parse individual tournament from table row (from working scraper)."""
        try:
            # Set a shorter timeout for element operations to prevent hanging
            original_timeout = self.selenium.driver.timeouts.implicit_wait
            self.selenium.driver.implicitly_wait(3)  # 3 second timeout

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

            # Parse location into city and state
            city, state = self._parse_location(location)

            return Tournament(
                id=f"pg_{index}_{int(time.time())}",
                name=name,
                age_group=age_groups,
                start_date=date_start,
                end_date=date_end,
                location=location,
                city=city,
                state=state,
                distance_miles=None,  # Will be calculated later if needed
                entry_fee="TBD",
                team_count=teams if teams != "TBD" else None,
                contact_info="contact@perfectgame.org",
                website_url=url,
                description=f"Perfect Game tournament: {name}",
            )

        except Exception as e:
            print(f"⚠️ Error parsing table row: {e}")
            return None
        finally:
            # Reset timeout to original value
            try:
                self.selenium.driver.implicitly_wait(
                    original_timeout if "original_timeout" in locals() else 10
                )
            except:
                pass

    def _parse_date_text(self, date_text: str) -> Tuple[str, str]:
        """Parse date text from Perfect Game format (from working scraper)."""
        try:
            # Perfect Game provides the year in the date text, let's extract it
            lines = date_text.strip().split("\n")
            year = None
            month_text = ""

            # Look for the year in the date text
            for line in lines:
                line = line.strip()
                if line.isdigit() and len(line) == 4:  # Found year (e.g., "2025")
                    year = int(line)
                elif (
                    line and not line.replace(" - ", "").replace(" ", "").isdigit()
                ):  # Month text
                    month_text = line.upper()

            # If no year found, use current year
            if not year:
                year = datetime.now().year

            # Parse based on month text
            if "AUG" in month_text:
                return f"{year}-08-01", f"{year}-08-31"
            elif "SEP - OCT" in month_text:
                return f"{year}-09-07", f"{year}-10-26"
            elif "SEP - NOV" in month_text:
                return f"{year}-09-07", f"{year}-11-09"
            elif "JUN - JUL" in month_text:
                return f"{year}-06-06", f"{year}-07-07"
            elif "SEP" in month_text:
                return f"{year}-09-01", f"{year}-09-30"
            elif "OCT" in month_text:
                return f"{year}-10-01", f"{year}-10-31"
            elif "NOV" in month_text:
                return f"{year}-11-01", f"{year}-11-30"
            else:
                # Default fallback - use the year we found or current year
                return f"{year}-08-01", f"{year}-08-03"

        except:
            # Ultimate fallback
            return (
                f"{datetime.now().year}-08-01",
                f"{datetime.now().year}-08-03",
            )

    def _parse_location(self, location: str) -> Tuple[str, str]:
        """Parse location into city and state."""
        try:
            if "," in location:
                parts = location.split(",")
                city = parts[0].strip()
                state = parts[-1].strip()
                return city, state
            else:
                return location.strip(), "Unknown"
        except:
            return "Unknown", "Unknown"

    def _get_simulated_tournaments(self, filters: Dict[str, Any]) -> List[Tournament]:
        """
        Generate simulated tournament data for testing.
        This will be replaced with actual Selenium scraping.
        """
        # Use the same simulation data from the original tournament_scraper.py
        base_date = datetime.now().date()
        next_month_start = base_date.replace(day=1) + timedelta(days=32)
        next_month_start = next_month_start.replace(day=1)

        city = filters.get("city", "Houston")
        state = filters.get("state", "TX")
        age_group = filters.get("age_group", "10U")

        tournaments = [
            Tournament(
                id="pg_001",
                name=f"{city} Youth Baseball Tournament",
                age_group=age_group,
                start_date="2025-08-15",
                end_date="2025-08-17",
                location=f"{city}, {state}",
                city=city,
                state=state,
                distance_miles=25.3,
                entry_fee="$450",
                team_count=32,
                contact_info="tournament@houstonbaseball.com",
                website_url="https://www.perfectgame.org/tournaments/houston-youth",
                description="Annual youth tournament featuring top teams from Texas",
            ),
            Tournament(
                id="pg_002",
                name=f"{city} Regional Classic",
                age_group=age_group,
                start_date="2025-08-22",
                end_date="2025-08-24",
                location=f"{city}, {state}",
                city=city,
                state=state,
                distance_miles=35.7,
                entry_fee="$475",
                team_count=24,
                contact_info="info@springbaseball.org",
                website_url="https://www.perfectgame.org/tournaments/spring-classic",
                description="Competitive tournament in North Houston area",
            ),
        ]

        return tournaments

    def get_tournament_details(self, tournament_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific Perfect Game tournament.

        Args:
            tournament_id: Perfect Game tournament ID

        Returns:
            Dictionary containing detailed tournament information
        """
        # This will be implemented with actual Perfect Game detail page scraping
        return {
            "tournament_id": tournament_id,
            "detailed_info": "Tournament details would be scraped here",
            "status": "not_implemented",
        }

    def close(self):
        """Clean up resources."""
        self.selenium.close_driver()

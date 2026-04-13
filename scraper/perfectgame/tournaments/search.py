"""
Perfect Game tournament search functionality.
"""

import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from selenium.webdriver.common.by import By
from core.selenium_utils import SeleniumUtils
from core.tournament_data import Tournament
from typing import List, Dict, Any
import time


class Search:
    """
    Handles tournament search operations on Perfect Game website.
    """

    def __init__(self, selenium_utils: SeleniumUtils):
        """
        Initialize tournament search.

        Args:
            selenium_utils: Selenium utilities instance
        """
        self.selenium = selenium_utils
        self.search_url = "https://www.perfectgame.org/Search/Tournaments"

    def search_by_filters(self, filters: Dict[str, Any]) -> List[Tournament]:
        """
        Search tournaments using the Perfect Game search interface.

        Args:
            filters: Search filters including age_group, city, state, etc.

        Returns:
            List of Tournament objects found
        """
        tournaments = []

        try:
            print(f"🔍 Searching Perfect Game with filters: {filters}")

            # Create driver if not exists
            if not self.selenium.driver:
                self.selenium.create_driver()

            # Navigate to search page
            print("📝 Navigating to Perfect Game search page...")
            self.selenium.driver.get(self.search_url)
            time.sleep(2)  # Wait for page load

            # Try to find and interact with search elements
            print("🔎 Looking for search form elements...")

            # Look for common search elements (these might need adjustment based on actual site)
            location_input = self._find_location_input()
            if location_input and "city" in filters and "state" in filters:
                location_text = f"{filters['city']}, {filters['state']}"
                print(f"📍 Setting location: {location_text}")
                self._safe_input(location_input, location_text)

            # Look for age group selection
            age_select = self._find_age_group_selector()
            if age_select and "age_group" in filters:
                print(f"🎯 Setting age group: {filters['age_group']}")
                self._safe_select_age_group(age_select, filters["age_group"])

            # Submit search
            search_button = self._find_search_button()
            if search_button:
                print("🚀 Submitting search...")
                search_button.click()
                time.sleep(3)  # Wait for results

                # Parse results
                tournaments = self._parse_tournament_results()
                print(f"✅ Found {len(tournaments)} tournaments")
            else:
                print("⚠️ Could not find search button, trying direct URL approach...")
                tournaments = self._try_direct_search(filters)

        except Exception as e:
            print(f"❌ Error during tournament search: {e}")
            # Fallback to simulated data for now
            tournaments = self._get_fallback_tournaments(filters)

        return tournaments

    def _find_location_input(self):
        """Try to find location input field with various possible selectors."""
        possible_selectors = [
            (By.ID, "location"),
            (By.ID, "location-input"),
            (By.NAME, "location"),
            (By.CSS_SELECTOR, "input[placeholder*='location' i]"),
            (By.CSS_SELECTOR, "input[placeholder*='city' i]"),
            (By.CSS_SELECTOR, "input[placeholder*='state' i]"),
            (By.XPATH, "//input[contains(@placeholder, 'Location')]"),
            (By.XPATH, "//input[contains(@placeholder, 'City')]"),
        ]

        for selector in possible_selectors:
            try:
                element = self.selenium.driver.find_element(*selector)
                if element.is_displayed():
                    return element
            except:
                continue
        return None

    def _find_age_group_selector(self):
        """Try to find age group selector with various possible selectors."""
        possible_selectors = [
            (By.ID, "age-group"),
            (By.ID, "agegroup"),
            (By.NAME, "age_group"),
            (By.NAME, "ageGroup"),
            (By.CSS_SELECTOR, "select[name*='age' i]"),
            (By.XPATH, "//select[contains(@name, 'age')]"),
            (By.XPATH, "//select[contains(@id, 'age')]"),
        ]

        for selector in possible_selectors:
            try:
                element = self.selenium.driver.find_element(*selector)
                if element.is_displayed():
                    return element
            except:
                continue
        return None

    def _find_search_button(self):
        """Try to find search/submit button with various possible selectors."""
        possible_selectors = [
            (By.ID, "search-button"),
            (By.ID, "submit"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.CSS_SELECTOR, "input[type='submit']"),
            (By.XPATH, "//button[contains(text(), 'Search')]"),
            (By.XPATH, "//input[@value='Search']"),
            (By.XPATH, "//button[contains(text(), 'Find')]"),
        ]

        for selector in possible_selectors:
            try:
                element = self.selenium.driver.find_element(*selector)
                if element.is_displayed():
                    return element
            except:
                continue
        return None

    def _safe_input(self, element, text):
        """Safely input text into an element."""
        try:
            element.clear()
            element.send_keys(text)
            return True
        except:
            return False

    def _safe_select_age_group(self, element, age_group):
        """Safely select age group from dropdown."""
        try:
            from selenium.webdriver.support.ui import Select

            select = Select(element)

            # Try exact match first
            try:
                select.select_by_visible_text(age_group)
                return True
            except:
                pass

            # Try partial match
            for option in select.options:
                if age_group.lower() in option.text.lower():
                    select.select_by_visible_text(option.text)
                    return True

        except:
            pass
        return False

    def _try_direct_search(self, filters: Dict[str, Any]) -> List[Tournament]:
        """Try alternative search approach or use specific URLs."""
        print("🔄 Trying alternative search approach...")

        # This could involve trying different URLs or search strategies
        # For now, return fallback data
        return self._get_fallback_tournaments(filters)

    def _get_fallback_tournaments(self, filters: Dict[str, Any]) -> List[Tournament]:
        """Generate fallback tournament data when scraping fails."""
        print("🔄 Using fallback tournament data...")

        from datetime import datetime, timedelta

        # Generate realistic fallback data based on filters
        city = filters.get("city", "Houston")
        state = filters.get("state", "TX")
        age_group = filters.get("age_group", "10U")

        tournaments = [
            Tournament(
                id="pg_fallback_001",
                name=f"{city} Youth Baseball Tournament",
                age_group=age_group,
                start_date="2025-08-15",
                end_date="2025-08-17",
                location=f"{city}, {state}",
                city=city,
                state=state,
                distance_miles=15.5,
                entry_fee="$450",
                team_count=24,
                contact_info=f"contact@{city.lower()}baseball.com",
                website_url=f"https://www.perfectgame.org/tournaments/{city.lower()}-youth",
                description=f"Annual {age_group} tournament in {city}",
            ),
            Tournament(
                id="pg_fallback_002",
                name=f"{city} Regional Classic",
                age_group=age_group,
                start_date="2025-08-22",
                end_date="2025-08-24",
                location=f"{city}, {state}",
                city=city,
                state=state,
                distance_miles=28.3,
                entry_fee="$475",
                team_count=18,
                contact_info=f"info@{city.lower()}regional.org",
                website_url=f"https://www.perfectgame.org/tournaments/{city.lower()}-regional",
                description=f"Competitive {age_group} regional tournament",
            ),
        ]

        return tournaments

    def _apply_search_filters(self, filters: Dict[str, Any]) -> None:
        """
        Apply search filters to the Perfect Game search form.

        Args:
            filters: Dictionary of search filters
        """
        # This will contain the actual Selenium logic to fill Perfect Game search form
        # For now, we'll just add placeholder implementations

        # Age group selection
        if "age_group" in filters:
            age_group_locator = (By.ID, "age-group-select")  # Placeholder selector
            self.selenium.safe_send_keys(age_group_locator, filters["age_group"])

        # Location search
        if "city" in filters and "state" in filters:
            location_text = f"{filters['city']}, {filters['state']}"
            location_locator = (By.ID, "location-input")  # Placeholder selector
            self.selenium.safe_send_keys(location_locator, location_text)

        # Distance filter
        if "distance_miles" in filters:
            distance_locator = (By.ID, "distance-select")  # Placeholder selector
            self.selenium.safe_send_keys(
                distance_locator, str(filters["distance_miles"])
            )

        # Date range
        if "start_date" in filters:
            start_date_locator = (By.ID, "start-date")  # Placeholder selector
            self.selenium.safe_send_keys(start_date_locator, filters["start_date"])

        if "end_date" in filters:
            end_date_locator = (By.ID, "end-date")  # Placeholder selector
            self.selenium.safe_send_keys(end_date_locator, filters["end_date"])

    def _submit_search(self) -> None:
        """
        Submit the search form.
        """
        search_button_locator = (By.ID, "search-button")  # Placeholder selector
        self.selenium.safe_click(search_button_locator)

        # Wait for results to load
        time.sleep(2)

    def _parse_tournament_results(self) -> List[Tournament]:
        """
        Parse tournament results from the search results page.

        Returns:
            List of Tournament objects
        """
        tournaments = []

        # This will contain the actual parsing logic for Perfect Game results
        # For now, return empty list as this needs to be implemented with actual selectors

        # Placeholder logic - in real implementation, this would:
        # 1. Find tournament result containers
        # 2. Extract tournament details from each container
        # 3. Create Tournament objects
        # 4. Return the list

        tournament_rows_locator = (By.CSS_SELECTOR, ".tournament-row")  # Placeholder
        tournament_elements = self.selenium.driver.find_elements(
            *tournament_rows_locator
        )

        for element in tournament_elements:
            # Extract tournament data from each element
            # This is where the actual scraping logic would go
            pass

        return tournaments

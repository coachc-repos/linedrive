"""
Selenium utilities for web scraping operations.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Dict, List, Any, Optional
import logging
import time


class SeleniumUtils:
    """
    Utility class for common Selenium operations.
    """

    def __init__(self, headless: bool = True, timeout: int = 30):
        """
        Initialize Selenium utilities.

        Args:
            headless: Whether to run browser in headless mode
            timeout: Default timeout for web operations
        """
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self.logger = logging.getLogger("scraper.selenium")

    def create_driver(self) -> webdriver.Chrome:
        """
        Create and configure Chrome WebDriver.

        Returns:
            Configured Chrome WebDriver instance
        """
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(self.timeout)
        return self.driver

    def wait_for_element(self, locator: tuple, timeout: Optional[int] = None) -> Any:
        """
        Wait for an element to be present and return it.

        Args:
            locator: Tuple of (By method, locator string)
            timeout: Custom timeout, uses default if None

        Returns:
            WebElement if found

        Raises:
            TimeoutException: If element not found within timeout
        """
        wait_time = timeout or self.timeout
        wait = WebDriverWait(self.driver, wait_time)
        return wait.until(EC.presence_of_element_located(locator))

    def wait_for_clickable(self, locator: tuple, timeout: Optional[int] = None) -> Any:
        """
        Wait for an element to be clickable and return it.

        Args:
            locator: Tuple of (By method, locator string)
            timeout: Custom timeout, uses default if None

        Returns:
            WebElement if clickable

        Raises:
            TimeoutException: If element not clickable within timeout
        """
        wait_time = timeout or self.timeout
        wait = WebDriverWait(self.driver, wait_time)
        return wait.until(EC.element_to_be_clickable(locator))

    def safe_click(self, locator: tuple, timeout: Optional[int] = None) -> bool:
        """
        Safely click an element with error handling.

        Args:
            locator: Tuple of (By method, locator string)
            timeout: Custom timeout, uses default if None

        Returns:
            True if click successful, False otherwise
        """
        try:
            element = self.wait_for_clickable(locator, timeout)
            element.click()
            return True
        except (TimeoutException, NoSuchElementException) as e:
            self.logger.warning("Click failed for locator %s: %s", locator, str(e))
            return False

    def safe_send_keys(
        self, locator: tuple, text: str, timeout: Optional[int] = None
    ) -> bool:
        """
        Safely send keys to an element with error handling.

        Args:
            locator: Tuple of (By method, locator string)
            text: Text to send to the element
            timeout: Custom timeout, uses default if None

        Returns:
            True if successful, False otherwise
        """
        try:
            element = self.wait_for_element(locator, timeout)
            element.clear()
            element.send_keys(text)
            return True
        except (TimeoutException, NoSuchElementException) as e:
            self.logger.warning("Send keys failed for locator %s: %s", locator, str(e))
            return False

    def get_elements_text(
        self, locator: tuple, timeout: Optional[int] = None
    ) -> List[str]:
        """
        Get text from multiple elements.

        Args:
            locator: Tuple of (By method, locator string)
            timeout: Custom timeout, uses default if None

        Returns:
            List of text content from elements
        """
        try:
            self.wait_for_element(locator, timeout)
            elements = self.driver.find_elements(*locator)
            return [element.text.strip() for element in elements]
        except (TimeoutException, NoSuchElementException) as e:
            self.logger.warning(
                "Get elements text failed for locator %s: %s", locator, str(e)
            )
            return []

    def scroll_to_element(self, element) -> None:
        """
        Scroll to an element to bring it into view.

        Args:
            element: WebElement to scroll to
        """
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)  # Brief pause after scroll

    def close_driver(self) -> None:
        """
        Close the WebDriver and clean up resources.
        """
        if self.driver:
            self.driver.quit()
            self.driver = None

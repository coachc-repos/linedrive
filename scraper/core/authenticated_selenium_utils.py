#!/usr/bin/env python3
"""
Enhanced Selenium utilities with authentication support for web scraping operations.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Dict, Any, Optional
import logging
import time
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scraper.core.selenium_utils import SeleniumUtils
from scraper.config.site_auth_config import SiteAuthConfig, get_site_config


class AuthenticatedSeleniumUtils(SeleniumUtils):
    """
    Enhanced Selenium utilities with authentication support
    """

    def __init__(self, headless: bool = True, timeout: int = 30):
        """
        Initialize authenticated Selenium utilities.

        Args:
            headless: Whether to run browser in headless mode
            timeout: Default timeout for web operations
        """
        super().__init__(headless, timeout)
        self.auth_config = SiteAuthConfig()
        self.is_authenticated = False
        self.current_site = None

    def authenticate_site(
        self, site_name: str, force_interactive: bool = False
    ) -> bool:
        """
        Authenticate with a specific site

        Args:
            site_name: Name of the site to authenticate with
            force_interactive: Force headless=False for interactive 2FA

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Get site configuration
            site_config = get_site_config(site_name)
            if not site_config:
                self.logger.error(f"Unsupported site for authentication: {site_name}")
                return False

            # Check if credentials exist
            if not self.auth_config.has_site_credentials(site_name):
                print(f"❌ No credentials found for {site_name}")
                print(f"💡 Run credential setup first")
                return False

            # Get credentials
            credentials = self.auth_config.get_site_credentials(site_name)

            # If site requires 2FA or force_interactive, run in visible mode
            if site_config.get("requires_2fa") or force_interactive:
                if self.headless:
                    print(
                        "🔐 Authentication requires interaction - switching to visible browser mode"
                    )
                    self.headless = False
                    if self.driver:
                        self.close_driver()
                    self.create_driver()

            # Navigate to login page
            print(f"🌐 Navigating to {site_config['name']} login page...")
            self.driver.get(site_config["login_url"])
            time.sleep(2)

            # Wait for and fill username field
            print("👤 Entering username...")
            if not self._safe_fill_field(
                site_config["username_selector"], credentials["username"]
            ):
                self.logger.error("Failed to enter username")
                return False

            # Wait for and fill password field
            print("🔑 Entering password...")
            if not self._safe_fill_field(
                site_config["password_selector"], credentials["password"]
            ):
                self.logger.error("Failed to enter password")
                return False

            # Click login button
            print("🚀 Clicking login button...")
            if not self.safe_click(
                (By.CSS_SELECTOR, site_config["login_button_selector"])
            ):
                self.logger.error("Failed to click login button")
                return False

            # Handle 2FA if required
            if site_config.get("requires_2fa"):
                print("\n🔒 2FA REQUIRED")
                print("=" * 40)
                print("Please complete 2FA verification in the browser window.")
                print("This may include:")
                print("  - Entering SMS/email code")
                print("  - Clicking verification email")
                print("  - Using authenticator app")
                print("  - Completing CAPTCHA")

                success = self._wait_for_2fa_completion(site_config)
                if not success:
                    print("❌ 2FA verification failed or timed out")
                    return False
                print("✅ 2FA verification completed!")

            # Wait for successful login indicator
            print("⏳ Verifying login success...")
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, site_config["success_indicator"])
                    )
                )
                print(f"✅ Successfully authenticated with {site_config['name']}!")
                self.is_authenticated = True
                self.current_site = site_name
                return True
            except TimeoutException:
                print(f"❌ Login verification failed - success indicator not found")
                return False

        except Exception as e:
            self.logger.error(f"Authentication failed for {site_name}: {e}")
            return False

    def _safe_fill_field(self, selector: str, value: str, timeout: int = 10) -> bool:
        """Safely fill a form field"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            element.clear()
            element.send_keys(value)
            return True
        except (TimeoutException, NoSuchElementException) as e:
            self.logger.warning(f"Failed to fill field {selector}: {e}")
            return False

    def _wait_for_2fa_completion(
        self, site_config: Dict[str, Any], max_wait_minutes: int = 5
    ) -> bool:
        """
        Wait for user to complete 2FA verification

        Args:
            site_config: Site configuration dict
            max_wait_minutes: Maximum time to wait for completion

        Returns:
            True if 2FA completed successfully, False otherwise
        """
        max_wait_seconds = max_wait_minutes * 60
        start_time = time.time()

        print(
            f"⏰ Waiting up to {max_wait_minutes} minutes for verification completion..."
        )

        while (time.time() - start_time) < max_wait_seconds:
            try:
                # Check if we've reached the success page/indicator
                success_element = self.driver.find_element(
                    By.CSS_SELECTOR, site_config["success_indicator"]
                )
                if success_element:
                    return True
            except NoSuchElementException:
                pass

            # Show countdown every 30 seconds
            elapsed = int(time.time() - start_time)
            if elapsed % 30 == 0 and elapsed > 0:
                remaining = max_wait_minutes - (elapsed // 60)
                print(f"⏱️  Still waiting... {remaining} minutes remaining")

            time.sleep(2)

        return False

    def is_site_authenticated(self, site_name: str) -> bool:
        """Check if currently authenticated with a site"""
        return self.is_authenticated and self.current_site == site_name

    def logout_site(self) -> bool:
        """Logout from current site (generic approach)"""
        try:
            if not self.is_authenticated:
                return True

            # Try common logout selectors
            logout_selectors = [
                'a[href*="logout"]',
                ".logout",
                '[data-action="logout"]',
                ".signout",
                'a[href*="signout"]',
            ]

            for selector in logout_selectors:
                try:
                    if self.safe_click((By.CSS_SELECTOR, selector)):
                        print("✅ Logged out successfully")
                        self.is_authenticated = False
                        self.current_site = None
                        return True
                except:
                    continue

            print("⚠️ Could not find logout button - session may still be active")
            return False

        except Exception as e:
            self.logger.warning(f"Logout attempt failed: {e}")
            return False

    def close_driver(self) -> None:
        """Close driver and reset authentication state"""
        self.is_authenticated = False
        self.current_site = None
        super().close_driver()


class TwoFactorHandler:
    """Helper class for handling 2FA interactions"""

    @staticmethod
    def pause_for_manual_verification(site_name: str, instructions: str = "") -> bool:
        """
        Pause execution for manual 2FA verification

        Args:
            site_name: Name of the site being authenticated
            instructions: Additional instructions for user

        Returns:
            True if user confirms completion, False if cancelled
        """
        print(f"\n🛑 MANUAL VERIFICATION REQUIRED - {site_name.upper()}")
        print("=" * 50)

        if instructions:
            print(f"📋 {instructions}")
            print()

        print("Please complete the following steps:")
        print("1. 🔍 Check your browser window")
        print("2. 📱 Complete any 2FA verification (SMS, email, app)")
        print("3. 🔐 Solve any CAPTCHA if present")
        print("4. ✅ Wait for successful login")
        print()

        while True:
            try:
                user_input = (
                    input(
                        "Press [ENTER] when verification is complete, or 'q' to quit: "
                    )
                    .strip()
                    .lower()
                )

                if user_input == "q":
                    print("❌ Verification cancelled by user")
                    return False
                elif user_input == "":
                    print("✅ Proceeding with verification...")
                    return True
                else:
                    print("💡 Press ENTER to continue or 'q' to quit")

            except KeyboardInterrupt:
                print("\n❌ Verification cancelled by user")
                return False

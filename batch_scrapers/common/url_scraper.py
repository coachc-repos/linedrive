#!/usr/bin/env python3
"""
Generic URL Scraper with Subpage Support

A flexible scraper that can scrape a given URL and its subpages,
with options to save to local files and Azure Data Lake.
"""

import time
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse, urldefrag
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests

logger = logging.getLogger(__name__)


class URLScraper:
    """Generic URL scraper with subpage crawling capabilities"""

    def __init__(self, headless: bool = True, debug: bool = False):
        """Initialize the URL scraper"""
        self.headless = headless
        self.debug = debug
        self.driver = None
        self.visited_urls: Set[str] = set()
        self.scraped_data: List[Dict] = []

        # Configure logging
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

    def _init_driver(self):
        """Initialize Chrome WebDriver"""
        if self.driver is not None:
            return

        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")

            # Add user agent to avoid bot detection
            chrome_options.add_argument(
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )

            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("✅ Chrome WebDriver initialized")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Chrome WebDriver: {e}")
            raise

    def login_to_site(
        self,
        login_url: str,
        username: str,
        password: str,
        username_field: str = "username",
        password_field: str = "password",
        submit_button_selector: str = None,
    ) -> bool:
        """
        Login to a website with authentication

        Args:
            login_url: URL of the login page
            username: Username/email for login
            password: Password for login
            username_field: Name/ID of username field (default: "username")
            password_field: Name/ID of password field (default: "password")
            submit_button_selector: CSS selector for submit button (optional)

        Returns:
            bool: True if login appears successful, False otherwise
        """
        try:
            self._init_driver()
            logger.info(f"🔐 Navigating to login page: {login_url}")
            self.driver.get(login_url)

            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Auto-detect login form if fields not found by name/id
            username_element = self._find_login_field(
                username_field, ["username", "email", "user", "login"]
            )
            password_element = self._find_login_field(
                password_field, ["password", "pass", "pwd"]
            )

            if not username_element or not password_element:
                logger.error("❌ Could not find username or password fields")
                return False

            # Fill in credentials
            logger.info("📝 Filling in credentials...")
            username_element.clear()
            username_element.send_keys(username)

            password_element.clear()
            password_element.send_keys(password)

            # Submit form
            if submit_button_selector:
                submit_button = self.driver.find_element(
                    By.CSS_SELECTOR, submit_button_selector
                )
                submit_button.click()
            else:
                # Try pressing Enter or finding submit button
                password_element.send_keys(Keys.RETURN)

            logger.info("🚀 Login form submitted")

            # Wait a moment for page to respond
            time.sleep(2)

            return True

        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
            return False

    def _find_login_field(self, preferred_name: str, fallback_names: List[str]):
        """Find login field by name, id, or common alternatives"""
        try:
            # Try preferred name first
            try:
                return self.driver.find_element(By.NAME, preferred_name)
            except:
                try:
                    return self.driver.find_element(By.ID, preferred_name)
                except:
                    pass

            # Try fallback names
            for name in fallback_names:
                try:
                    return self.driver.find_element(By.NAME, name)
                except:
                    try:
                        return self.driver.find_element(By.ID, name)
                    except:
                        continue

            # Try by input type
            if "password" in fallback_names:
                try:
                    return self.driver.find_element(
                        By.CSS_SELECTOR, "input[type='password']"
                    )
                except:
                    pass
            else:
                # Try email and text inputs
                for input_type in ["email", "text"]:
                    try:
                        return self.driver.find_element(
                            By.CSS_SELECTOR, f"input[type='{input_type}']"
                        )
                    except:
                        continue

            return None

        except Exception:
            return None

    def wait_for_mfa(
        self,
        instruction: str = "Please complete MFA authentication",
        mfa_field_selector: str = None,
    ) -> bool:
        """
        Handle MFA authentication with console code entry

        Args:
            instruction: Custom instruction to show user
            mfa_field_selector: CSS selector for MFA input field (optional)

        Returns:
            bool: True when MFA is complete
        """
        try:
            logger.info("⏸️ Starting MFA authentication...")
            print(f"\n🔐 MFA REQUIRED")
            print("=" * 60)
            print(instruction)
            print("📱 Please check your device for MFA code/notification")
            print("=" * 60)

            # Check if we can find an MFA input field on the page
            mfa_input = None
            if mfa_field_selector:
                try:
                    mfa_input = self.driver.find_element(
                        By.CSS_SELECTOR, mfa_field_selector
                    )
                except:
                    pass

            # Try common MFA field selectors if none specified
            if not mfa_input:
                common_selectors = [
                    "input[name*='mfa']",
                    "input[name*='2fa']",
                    "input[name*='code']",
                    "input[name*='verification']",
                    "input[name*='otp']",
                    "input[placeholder*='code']",
                    "input[placeholder*='MFA']",
                    "input[placeholder*='verification']",
                    "input[id*='mfa']",
                    "input[id*='2fa']",
                    "input[id*='code']",
                    "input[id*='verification']",
                    "input[id*='otp']",
                ]

                for selector in common_selectors:
                    try:
                        mfa_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                        logger.info(f"🎯 Found MFA input field: {selector}")
                        break
                    except:
                        continue

            if mfa_input:
                # Console-based MFA code entry
                print("🎯 MFA code input field detected!")
                print("📝 You can enter your MFA code below:")
                print("⚠️  Leave blank and press Enter to switch to manual browser mode")

                while True:
                    mfa_code = input("\n🔢 Enter MFA code: ").strip()

                    if not mfa_code:
                        print("🔄 Switching to manual browser mode...")
                        print("🔍 Complete the authentication in your browser")
                        print("⚠️ Do NOT close the browser window")
                        input("👆 Press Enter when MFA authentication is complete...")
                        break

                    # Validate code format (basic validation)
                    if len(mfa_code) < 4:
                        print("❌ MFA code seems too short. Please try again.")
                        continue

                    # Clear the field and enter the code
                    try:
                        mfa_input.clear()
                        mfa_input.send_keys(mfa_code)
                        logger.info(f"📝 Entered MFA code: {'*' * len(mfa_code)}")

                        # Try to find and click submit button
                        submit_found = False
                        submit_selectors = [
                            "button[type='submit']",
                            "input[type='submit']",
                            "button:contains('Submit')",
                            "button:contains('Verify')",
                            "button:contains('Continue')",
                            ".btn-submit",
                            ".verify-button",
                            ".submit-btn",
                        ]

                        for submit_selector in submit_selectors:
                            try:
                                submit_btn = self.driver.find_element(
                                    By.CSS_SELECTOR, submit_selector
                                )
                                submit_btn.click()
                                logger.info(
                                    f"🚀 Clicked submit button: {submit_selector}"
                                )
                                submit_found = True
                                break
                            except:
                                continue

                        if not submit_found:
                            # Try pressing Enter on the MFA field
                            mfa_input.send_keys(Keys.RETURN)
                            logger.info("🚀 Pressed Enter on MFA field")

                        # Wait for response
                        print("⏳ Submitting MFA code...")
                        time.sleep(3)

                        # Check if there's an error message
                        error_selectors = [
                            ".error",
                            ".alert-error",
                            ".invalid",
                            "[class*='error']",
                            "[class*='invalid']",
                            "div:contains('Invalid')",
                            "div:contains('incorrect')",
                            "span:contains('Invalid')",
                            "span:contains('incorrect')",
                        ]

                        error_found = False
                        for error_selector in error_selectors:
                            try:
                                error_element = self.driver.find_element(
                                    By.CSS_SELECTOR, error_selector
                                )
                                if error_element.is_displayed():
                                    error_text = error_element.text.lower()
                                    if any(
                                        word in error_text
                                        for word in [
                                            "invalid",
                                            "incorrect",
                                            "wrong",
                                            "expired",
                                        ]
                                    ):
                                        print(f"❌ Error: {error_element.text}")
                                        error_found = True
                                        break
                            except:
                                continue

                        if error_found:
                            print("🔄 Please try entering the MFA code again.")
                            continue
                        else:
                            print("✅ MFA code submitted successfully!")
                            break

                    except Exception as e:
                        print(f"❌ Error entering MFA code: {e}")
                        print(
                            "🔄 Please try again or press Enter without code for manual mode."
                        )
                        continue

            else:
                # No MFA field found, fall back to manual mode
                print("⚠️  No MFA input field detected on page")
                print("🔍 Complete the authentication in your browser")
                print("⚠️ Do NOT close the browser window")
                input("\n👆 Press Enter when MFA authentication is complete...")

            # Give a moment for any page redirects
            time.sleep(3)

            logger.info("✅ MFA authentication completed")
            return True

        except KeyboardInterrupt:
            logger.info("❌ MFA authentication cancelled by user")
            return False
        except Exception as e:
            logger.error(f"❌ Error during MFA authentication: {e}")
            return False

    def check_login_success(
        self, success_indicators: List[str] = None, failure_indicators: List[str] = None
    ) -> bool:
        """
        Check if login was successful by looking for indicators on the page

        Args:
            success_indicators: List of text/elements that indicate successful login
            failure_indicators: List of text/elements that indicate login failure

        Returns:
            bool: True if login appears successful
        """
        try:
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()

            # Default failure indicators
            default_failures = [
                "invalid username",
                "invalid password",
                "login failed",
                "incorrect credentials",
                "authentication failed",
                "login error",
                "wrong password",
                "user not found",
                "access denied",
            ]
            failure_indicators = failure_indicators or default_failures

            # Check for failure indicators first
            for indicator in failure_indicators:
                if indicator.lower() in page_source:
                    logger.error(f"❌ Login failed - found indicator: {indicator}")
                    return False

            # Default success indicators
            default_success = [
                "dashboard",
                "profile",
                "logout",
                "welcome",
                "account",
                "settings",
                "my account",
                "signed in",
                "logged in",
            ]
            success_indicators = success_indicators or default_success

            # Check for success indicators
            for indicator in success_indicators:
                if indicator.lower() in page_source:
                    logger.info(f"✅ Login successful - found indicator: {indicator}")
                    return True

            # If URL changed significantly, might indicate successful login
            if (
                "login" not in current_url.lower()
                and "signin" not in current_url.lower()
            ):
                logger.info(
                    "✅ Login likely successful - redirected away from login page"
                )
                return True

            # No clear indicators found
            logger.warning(
                "⚠️ Login status unclear - no clear success/failure indicators found"
            )
            return True  # Assume success and let user verify

        except Exception as e:
            logger.error(f"❌ Error checking login success: {e}")
            return False

    def _clean_url(self, url: str) -> str:
        """Clean URL by removing fragments and normalizing"""
        # Remove fragment (anchor) part
        clean_url, _ = urldefrag(url)
        return clean_url.strip()

    def _is_valid_subpage(self, url: str, base_domain: str) -> bool:
        """Check if URL is a valid subpage to scrape"""
        try:
            parsed = urlparse(url)
            base_parsed = urlparse(base_domain)

            # Must be same domain
            if parsed.netloc != base_parsed.netloc:
                return False

            # Skip file downloads, images, etc.
            skip_extensions = [
                ".pdf",
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".zip",
                ".doc",
                ".docx",
            ]
            if any(parsed.path.lower().endswith(ext) for ext in skip_extensions):
                return False

            return True

        except Exception:
            return False

    def _extract_links(self, base_url: str) -> List[str]:
        """Extract all links from current page"""
        links = []
        try:
            # Find all anchor tags
            anchor_elements = self.driver.find_elements(By.TAG_NAME, "a")

            for element in anchor_elements:
                href = element.get_attribute("href")
                if href:
                    # Convert relative URLs to absolute
                    absolute_url = urljoin(base_url, href)
                    clean_url = self._clean_url(absolute_url)

                    if self._is_valid_subpage(clean_url, base_url):
                        links.append(clean_url)

        except Exception as e:
            logger.warning(f"⚠️ Error extracting links: {e}")

        return list(set(links))  # Remove duplicates

    def _scrape_page_content(self, url: str) -> Dict:
        """Scrape content from a single page"""
        try:
            logger.info(f"🔍 Scraping: {url}")
            self.driver.get(url)

            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Get page content
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")

            # Extract basic information
            title = soup.find("title")
            title_text = title.get_text().strip() if title else "No Title"

            # Extract meta description
            meta_desc = soup.find("meta", attrs={"name": "description"})
            description = meta_desc.get("content", "") if meta_desc else ""

            # Extract main content (try different content selectors)
            content_selectors = [
                "main",
                "article",
                ".content",
                "#content",
                ".main-content",
                ".post-content",
                ".entry-content",
                "section",
            ]

            main_content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    main_content = content_elem.get_text(strip=True)
                    break

            # If no main content found, get body text
            if not main_content:
                body = soup.find("body")
                if body:
                    # Remove script and style elements
                    for script in body(["script", "style"]):
                        script.decompose()
                    main_content = body.get_text(strip=True)

            # Extract all text content
            all_text = soup.get_text(strip=True)

            scraped_data = {
                "url": url,
                "title": title_text,
                "description": description,
                "main_content": main_content[:5000],  # Limit content length
                "full_text": all_text[:10000],  # Limit full text length
                "scraped_at": datetime.now().isoformat(),
                "content_length": len(all_text),
                "links_found": len(self._extract_links(url)),
            }

            logger.info(f"✅ Successfully scraped: {title_text}")
            return scraped_data

        except Exception as e:
            logger.error(f"❌ Error scraping {url}: {e}")
            return {
                "url": url,
                "title": "Error",
                "description": "",
                "main_content": "",
                "full_text": "",
                "error": str(e),
                "scraped_at": datetime.now().isoformat(),
                "content_length": 0,
                "links_found": 0,
            }

    def scrape_url_with_subpages(
        self,
        start_url: str,
        max_pages: int = 10,
        max_depth: int = 2,
        delay: float = 1.0,
        login_url: str = None,
        username: str = None,
        password: str = None,
        username_field: str = "username",
        password_field: str = "password",
        require_mfa: bool = False,
        mfa_field_selector: str = None,
        success_indicators: List[str] = None,
        failure_indicators: List[str] = None,
    ) -> Dict:
        """
        Scrape a URL and its subpages with optional authentication

        Args:
            start_url: The starting URL to scrape
            max_pages: Maximum number of pages to scrape
            max_depth: Maximum depth to crawl (0 = only start URL)
            delay: Delay between requests in seconds
            login_url: URL of login page (if authentication required)
            username: Username/email for login
            password: Password for login
            username_field: Name/ID of username field (default: "username")
            password_field: Name/ID of password field (default: "password")
            require_mfa: Whether MFA is required after login
            mfa_field_selector: CSS selector for MFA input field (optional)
            success_indicators: List of text that indicates successful login
            failure_indicators: List of text that indicates failed login
        """
        try:
            self._init_driver()

            start_time = time.time()
            self.visited_urls.clear()
            self.scraped_data.clear()

            # Handle authentication if required
            if login_url and username and password:
                logger.info("🔐 Authentication required - logging in...")
                login_success = self.login_to_site(
                    login_url=login_url,
                    username=username,
                    password=password,
                    username_field=username_field,
                    password_field=password_field,
                )

                if not login_success:
                    logger.error("❌ Login failed - aborting scraping")
                    return {
                        "error": "Login failed",
                        "urls_scraped": 0,
                        "total_time": time.time() - start_time,
                        "timestamp": datetime.now().isoformat(),
                    }

                # Handle MFA if required
                if require_mfa:
                    logger.info("🔐 MFA required...")
                    mfa_success = self.wait_for_mfa(
                        "Please complete MFA to continue scraping", mfa_field_selector
                    )
                    if not mfa_success:
                        logger.error("❌ MFA authentication failed - aborting scraping")
                        return {
                            "error": "MFA authentication failed",
                            "urls_scraped": 0,
                            "total_time": time.time() - start_time,
                            "timestamp": datetime.now().isoformat(),
                        }

                # Verify login success
                if not self.check_login_success(success_indicators, failure_indicators):
                    logger.error("❌ Login verification failed - aborting scraping")
                    return {
                        "error": "Login verification failed",
                        "urls_scraped": 0,
                        "total_time": time.time() - start_time,
                        "timestamp": datetime.now().isoformat(),
                    }

                logger.info("✅ Authentication successful - proceeding with scraping")

            # Queue for URLs to visit: (url, depth)
            url_queue = [(start_url, 0)]

            logger.info(f"🚀 Starting URL scraping: {start_url}")
            logger.info(
                f"📊 Settings: max_pages={max_pages}, max_depth={max_depth}, delay={delay}s"
            )

            while url_queue and len(self.scraped_data) < max_pages:
                current_url, current_depth = url_queue.pop(0)
                clean_url = self._clean_url(current_url)

                # Skip if already visited
                if clean_url in self.visited_urls:
                    continue

                # Mark as visited
                self.visited_urls.add(clean_url)

                # Scrape current page
                page_data = self._scrape_page_content(clean_url)
                page_data["depth"] = current_depth
                self.scraped_data.append(page_data)

                # If we haven't reached max depth, find more links
                if current_depth < max_depth and len(self.scraped_data) < max_pages:
                    try:
                        links = self._extract_links(clean_url)
                        logger.info(f"🔗 Found {len(links)} links on {clean_url}")

                        # Add new links to queue
                        for link in links:
                            clean_link = self._clean_url(link)
                            if clean_link not in self.visited_urls:
                                url_queue.append((clean_link, current_depth + 1))

                    except Exception as e:
                        logger.warning(
                            f"⚠️ Error extracting links from {clean_url}: {e}"
                        )

                # Add delay between requests
                if delay > 0:
                    time.sleep(delay)

                # Progress update
                elapsed = time.time() - start_time
                logger.info(
                    f"⏱️ Progress: {len(self.scraped_data)}/{max_pages} pages scraped in {elapsed:.1f}s"
                )

            end_time = time.time()
            total_time = end_time - start_time

            # Compile results
            results = {
                "start_url": start_url,
                "pages_scraped": len(self.scraped_data),
                "total_time_seconds": total_time,
                "settings": {
                    "max_pages": max_pages,
                    "max_depth": max_depth,
                    "delay": delay,
                },
                "scraped_at": datetime.now().isoformat(),
                "data": self.scraped_data,
            }

            logger.info(
                f"✅ Scraping completed: {len(self.scraped_data)} pages in {total_time:.1f}s"
            )
            return results

        except Exception as e:
            logger.error(f"❌ Scraping failed: {e}")
            raise
        finally:
            self._cleanup()

    def save_results(self, results: Dict, output_path: str) -> str:
        """Save scraping results to JSON file"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Results saved to: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"❌ Error saving results: {e}")
            raise

    def _cleanup(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                logger.info("🧹 WebDriver cleaned up")
            except Exception as e:
                logger.warning(f"⚠️ Error cleaning up WebDriver: {e}")


def main():
    """Main function for testing"""
    if len(sys.argv) < 2:
        print("Usage: python url_scraper.py <URL> [max_pages] [max_depth]")
        sys.exit(1)

    url = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    max_depth = int(sys.argv[3]) if len(sys.argv) > 3 else 1

    scraper = URLScraper(headless=True, debug=True)

    try:
        results = scraper.scrape_url_with_subpages(url, max_pages, max_depth)

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"url_scraping_results_{timestamp}.json"
        scraper.save_results(results, output_file)

        print(f"\n✅ Scraping completed!")
        print(f"📊 Pages scraped: {results['pages_scraped']}")
        print(f"⏱️ Total time: {results['total_time_seconds']:.1f}s")
        print(f"💾 Results saved to: {output_file}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

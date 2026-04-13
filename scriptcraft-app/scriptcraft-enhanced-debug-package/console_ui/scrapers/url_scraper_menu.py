#!/usr/bin/env python3
"""
Generic URL Scraper Menu

Interactive menu system for scraping URLs and their subpages with Azure Data Lake support.
"""

from datetime import datetime
import os
import sys
import json
from typing import Dict, List, Optional

# Add the parent directory to the path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(
    os.path.dirname(current_dir)
)  # Go up two levels to reach project root
sys.path.insert(0, parent_dir)

# Import URL scraper
try:
    from batch_scrapers.common.url_scraper import URLScraper
except ImportError:
    # Fallback for direct execution
    sys.path.append(os.path.join(parent_dir, "batch_scrapers", "common"))
    from url_scraper import URLScraper

# Import Azure storage from linedrive_azure module
sys.path.append(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        "linedrive_azure",
        "storage",
    )
)

try:
    from azure_storage import AzureDataLakeUploader

    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False


class URLScraperMenu:
    """Interactive menu for URL scraping"""

    def __init__(self):
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)

        self.scraper = URLScraper(headless=True, debug=True)
        self.last_results = None
        self.azure_available = AZURE_AVAILABLE
        self.auto_upload = False

        # Default settings
        self.settings = {
            "max_pages": 10,
            "max_depth": 2,
            "delay": 1.0,
            "save_to_azure": False,
            # Authentication settings
            "use_authentication": False,
            "login_url": "",
            "username": "",
            "password": "",
            "username_field": "username",
            "password_field": "password",
            "require_mfa": False,
            "mfa_field_selector": "",
        }

    def display_header(self):
        """Display the menu header"""
        print("\n🌐 GENERIC URL SCRAPER")
        print("=" * 60)
        print("Scrape any website and its subpages with configurable settings")

    def display_current_settings(self):
        """Display current scraper settings"""
        print("\n⚙️ Current Settings:")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"   📄 Max Pages: {self.settings['max_pages']}")
        print(f"   🔗 Max Depth: {self.settings['max_depth']} (0 = only start URL)")
        print(f"   ⏱️ Delay: {self.settings['delay']}s between requests")

        # Authentication settings
        auth_status = "✅ ON" if self.settings["use_authentication"] else "❌ OFF"
        print(f"   🔐 Authentication: {auth_status}")

        if self.settings["use_authentication"]:
            print(f"   🌐 Login URL: {self.settings['login_url'] or 'Not set'}")
            print(f"   👤 Username: {self.settings['username'] or 'Not set'}")
            print(
                f"   🔑 Password: {'***' if self.settings['password'] else 'Not set'}"
            )
            mfa_status = "✅ YES" if self.settings["require_mfa"] else "❌ NO"
            print(f"   📱 MFA Required: {mfa_status}")
            if self.settings["require_mfa"]:
                mfa_selector = self.settings.get("mfa_field_selector", "")
                selector_display = mfa_selector if mfa_selector else "Auto-detect"
                print(f"   🎯 MFA Field: {selector_display}")

        if self.azure_available:
            azure_status = "✅ ON" if self.settings["save_to_azure"] else "❌ OFF"
            print(f"   ☁️ Azure Data Lake: {azure_status}")

    def display_menu_options(self):
        """Display menu options"""
        print("\n📋 Menu Options:")
        print("   1: 🌐 Enter URL to scrape")
        print("   2: 📄 Change max pages setting")
        print("   3: 🔗 Change max depth setting")
        print("   4: ⏱️ Change delay setting")
        print("   5: 🔐 Setup authentication")
        if self.azure_available:
            print("   6: ☁️ Toggle Azure Data Lake saving")
            print("   7: 📊 Show last scraping results")
            print("   8: 📤 Upload last results to Azure")
        else:
            print("   6: 📊 Show last scraping results")
        print("   0: ❌ Exit")

    def get_url_input(self) -> Optional[str]:
        """Get URL input from user with validation"""
        print("\n🌐 URL Scraping Setup")
        print("=" * 40)

        url = input("Enter the URL to scrape: ").strip()

        if not url:
            print("❌ URL cannot be empty")
            return None

        # Add http:// if no protocol specified
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
            print(f"🔗 Using: {url}")

        return url

    def change_max_pages(self):
        """Change max pages setting"""
        print(f"\n📄 Current max pages: {self.settings['max_pages']}")
        try:
            new_value = input("Enter new max pages (1-100): ").strip()
            if new_value:
                pages = int(new_value)
                if 1 <= pages <= 100:
                    self.settings["max_pages"] = pages
                    print(f"✅ Max pages set to: {pages}")
                else:
                    print("❌ Max pages must be between 1 and 100")
        except ValueError:
            print("❌ Please enter a valid number")

    def change_max_depth(self):
        """Change max depth setting"""
        print(f"\n🔗 Current max depth: {self.settings['max_depth']}")
        print("   0 = Only scrape the start URL")
        print("   1 = Scrape start URL + direct links")
        print("   2 = Scrape start URL + links + their links")
        print("   3+ = Even deeper crawling")

        try:
            new_value = input("Enter new max depth (0-5): ").strip()
            if new_value:
                depth = int(new_value)
                if 0 <= depth <= 5:
                    self.settings["max_depth"] = depth
                    print(f"✅ Max depth set to: {depth}")
                else:
                    print("❌ Max depth must be between 0 and 5")
        except ValueError:
            print("❌ Please enter a valid number")

    def change_delay(self):
        """Change delay setting"""
        print(f"\n⏱️ Current delay: {self.settings['delay']}s")
        print("   Delay between requests (to be respectful to servers)")

        try:
            new_value = input("Enter new delay in seconds (0.1-10.0): ").strip()
            if new_value:
                delay = float(new_value)
                if 0.1 <= delay <= 10.0:
                    self.settings["delay"] = delay
                    print(f"✅ Delay set to: {delay}s")
                else:
                    print("❌ Delay must be between 0.1 and 10.0 seconds")
        except ValueError:
            print("❌ Please enter a valid number")

    def setup_authentication(self):
        """Setup authentication for protected sites"""
        print("\n🔐 Authentication Setup")
        print("=" * 40)

        # Toggle authentication on/off
        current_status = "ON" if self.settings["use_authentication"] else "OFF"
        print(f"Authentication is currently: {current_status}")
        print("\n1: Enable/Configure authentication")
        print("2: Disable authentication")
        print("0: Back to main menu")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            self._configure_authentication()
        elif choice == "2":
            self.settings["use_authentication"] = False
            print("✅ Authentication disabled")
        elif choice == "0":
            return
        else:
            print("❌ Invalid choice")

    def _configure_authentication(self):
        """Configure authentication details"""
        print("\n🔧 Configure Authentication")
        print("=" * 30)

        # Get login URL
        login_url = input(
            "Enter login page URL (e.g., https://example.com/login): "
        ).strip()
        if not login_url:
            print("❌ Login URL is required")
            return

        if not login_url.startswith(("http://", "https://")):
            login_url = "https://" + login_url

        # Get credentials
        username = input("Enter username/email: ").strip()
        if not username:
            print("❌ Username is required")
            return

        password = input("Enter password: ").strip()
        if not password:
            print("❌ Password is required")
            return

        # Get field names (optional)
        print("\n🏷️ Field Names (press Enter for defaults):")
        username_field = (
            input("Username field name (default: 'username'): ").strip() or "username"
        )
        password_field = (
            input("Password field name (default: 'password'): ").strip() or "password"
        )

        # MFA setup
        print("\n📱 Multi-Factor Authentication (MFA):")
        print("Does this site require MFA/2FA after login?")
        print("1: Yes (console code entry mode)")
        print("2: No")

        mfa_choice = input("Enter choice (1/2): ").strip()
        require_mfa = mfa_choice == "1"

        mfa_field_selector = ""
        if require_mfa:
            print("\n🎯 MFA Field Configuration (optional):")
            print(
                "If you know the CSS selector for the MFA input field, enter it below."
            )
            print("Leave blank to use automatic field detection.")
            print("Examples: input[name='mfa_code'], #verification-code, .otp-input")
            mfa_field_selector = input("MFA field selector (optional): ").strip()

        # Save settings
        self.settings.update(
            {
                "use_authentication": True,
                "login_url": login_url,
                "username": username,
                "password": password,
                "username_field": username_field,
                "password_field": password_field,
                "require_mfa": require_mfa,
                "mfa_field_selector": mfa_field_selector,
            }
        )

        print("\n✅ Authentication configured successfully!")
        print(f"🌐 Login URL: {login_url}")
        print(f"👤 Username: {username}")
        print(f"🔑 Password: ***")
        print(f"📱 MFA Required: {'Yes' if require_mfa else 'No'}")
        if require_mfa and mfa_field_selector:
            print(f"🎯 MFA Field Selector: {mfa_field_selector}")
        elif require_mfa:
            print("🎯 MFA Field Selector: Auto-detect")

    def toggle_azure_saving(self):
        """Toggle Azure Data Lake saving"""
        if not self.azure_available:
            print("❌ Azure Data Lake is not available")
            return

        self.settings["save_to_azure"] = not self.settings["save_to_azure"]
        status = "✅ ENABLED" if self.settings["save_to_azure"] else "❌ DISABLED"
        print(f"\n☁️ Azure Data Lake saving: {status}")

    def run_url_scraping(self, url: str):
        """Run the URL scraping process"""
        print("\n🔍 Starting URL scraping...")
        print("=" * 50)
        print(f"🌐 Target URL: {url}")
        print(f"📄 Max pages: {self.settings['max_pages']}")
        print(f"🔗 Max depth: {self.settings['max_depth']}")
        print(f"⏱️ Delay: {self.settings['delay']}s")

        if self.settings["use_authentication"]:
            print(f"🔐 Authentication: ENABLED")
            print(f"🌐 Login URL: {self.settings['login_url']}")
            print(f"📱 MFA Required: {'Yes' if self.settings['require_mfa'] else 'No'}")

        print()

        try:
            # Prepare authentication parameters
            auth_params = {}
            if self.settings["use_authentication"]:
                auth_params = {
                    "login_url": self.settings["login_url"],
                    "username": self.settings["username"],
                    "password": self.settings["password"],
                    "username_field": self.settings["username_field"],
                    "password_field": self.settings["password_field"],
                    "require_mfa": self.settings["require_mfa"],
                    "mfa_field_selector": self.settings.get("mfa_field_selector", ""),
                }

            # Run the scraping
            results = self.scraper.scrape_url_with_subpages(
                start_url=url,
                max_pages=self.settings["max_pages"],
                max_depth=self.settings["max_depth"],
                delay=self.settings["delay"],
                **auth_params,
            )

            self.last_results = results

            # Save results locally
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"url_scraping_{timestamp}.json"
            output_path = os.path.join("output", filename)

            self.scraper.save_results(results, output_path)

            # Display summary
            print(f"\n✅ Scraping completed successfully!")
            print("=" * 50)
            print(f"📊 Pages scraped: {results['pages_scraped']}")
            print(f"⏱️ Total time: {results['total_time_seconds']:.1f}s")
            print(f"💾 Saved to: {output_path}")

            # Auto-upload to Azure if enabled
            if self.settings["save_to_azure"] and self.azure_available:
                print(f"\n☁️ Auto-uploading to Azure Data Lake...")
                self.upload_to_azure()

        except Exception as e:
            print(f"\n❌ Scraping failed: {e}")
            print("💡 Please check the URL and try again")

    def show_last_results(self):
        """Display summary of last scraping results"""
        if not self.last_results:
            print("\n❌ No scraping results available")
            print("💡 Run a URL scraping operation first")
            return

        results = self.last_results
        print(f"\n📊 Last Scraping Results")
        print("=" * 50)
        print(f"🌐 Start URL: {results['start_url']}")
        print(f"📄 Pages scraped: {results['pages_scraped']}")
        print(f"⏱️ Total time: {results['total_time_seconds']:.1f}s")
        print(f"📅 Scraped at: {results['scraped_at']}")
        print()

        # Show sample of scraped data
        if results["data"]:
            print("📋 Sample of scraped pages:")
            for i, page in enumerate(results["data"][:5]):
                status = "✅" if "error" not in page else "❌"
                print(f"   {i+1}. {status} {page['title'][:50]}...")
                print(f"      URL: {page['url']}")
                if "error" in page:
                    print(f"      Error: {page['error']}")
                print()

            if len(results["data"]) > 5:
                print(f"   ... and {len(results['data']) - 5} more pages")

    def upload_to_azure(self):
        """Upload last results to Azure Data Lake"""
        if not self.azure_available:
            print("❌ Azure Data Lake is not available")
            print("💡 Please check your Azure configuration")
            return

        if not self.last_results:
            print("❌ No results to upload")
            print("💡 Run a scraping operation first")
            return

        try:
            print("☁️ Uploading to Azure Data Lake...")

            uploader = AzureDataLakeUploader()

            # Convert scraped data to tournament-like format for upload
            upload_data = []
            scraped_pages = self.last_results.get("data", [])

            for result in scraped_pages:
                upload_data.append(
                    {
                        "url": result.get("url", ""),
                        "title": result.get("title", ""),
                        "content": result.get("content", "")[:500],  # Truncate content
                        "links_found": len(result.get("links", [])),
                        "scrape_timestamp": result.get("timestamp", ""),
                        "source": "url_scraper",
                    }
                )

            # Add metadata about the scraping session
            metadata = {
                "start_url": self.last_results.get("start_url", ""),
                "pages_scraped": self.last_results.get("pages_scraped", 0),
                "total_time_seconds": self.last_results.get("total_time_seconds", 0),
                "scraped_at": self.last_results.get("scraped_at", ""),
                "settings": self.last_results.get("settings", {}),
                "source": "url_scraper_session",
            }

            # Add metadata as first item
            upload_data.insert(0, metadata)

            # Upload using the raw data method
            result = uploader.upload_raw_data(upload_data, "url_scraping")

            if result:
                print("✅ Upload successful!")
                print(f"📊 Data uploaded to: {result}")
                print(f"📄 Uploaded {len(scraped_pages)} pages + metadata")
            else:
                print("❌ Upload failed")
                print("💡 Check Azure connection and permissions")

        except Exception as e:
            print(f"❌ Upload error: {e}")
            print("💡 Please check your Azure connection")

    def run(self):
        """Main menu loop"""
        print("🚀 Starting Generic URL Scraper...")

        while True:
            self.display_header()
            self.display_current_settings()
            self.display_menu_options()
            print("=" * 60)

            try:
                max_option = "8" if self.azure_available else "6"
                choice = input(f"👆 Select an option (0-{max_option}): ").strip()

                if choice == "0":
                    print("👋 Goodbye! Happy scraping!")
                    break
                elif choice == "1":
                    url = self.get_url_input()
                    if url:
                        self.run_url_scraping(url)
                elif choice == "2":
                    self.change_max_pages()
                elif choice == "3":
                    self.change_max_depth()
                elif choice == "4":
                    self.change_delay()
                elif choice == "5":
                    self.setup_authentication()
                elif choice == "6":
                    if self.azure_available:
                        self.toggle_azure_saving()
                    else:
                        self.show_last_results()
                elif choice == "7" and self.azure_available:
                    self.show_last_results()
                elif choice == "8" and self.azure_available:
                    self.upload_to_azure()
                else:
                    print(f"❌ Invalid option. Please select 0-{max_option}.")

                if choice != "0":
                    input("\n⏎ Press Enter to continue...")

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted by user. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("⏎ Press Enter to continue...")


def main():
    """Main entry point for direct execution"""
    menu = URLScraperMenu()
    menu.run()


if __name__ == "__main__":
    main()

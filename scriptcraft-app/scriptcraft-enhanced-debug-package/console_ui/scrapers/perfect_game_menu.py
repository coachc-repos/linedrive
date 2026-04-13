#!/usr/bin/env python3
"""
Perfect Game Tournament Search Menu

Interactive menu system for searching Perfect Game tournaments with timer display.
"""

from datetime import datetime, timedelta
import os
import sys

# Add the parent directory to the path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(
    os.path.dirname(current_dir)
)  # Go up two levels to reach project root
sys.path.insert(0, parent_dir)

# Import from batch_scrapers package - now that we're in console_ui
try:
    from batch_scrapers.perfect_game.perfect_game_scraper import PerfectGameScraper
    from batch_scrapers.perfect_game.filters import PerfectGameFilters, FilterBuilder
    from batch_scrapers.perfect_game.utils import PerfectGameUtils
except ImportError:
    # Fallback for direct execution
    sys.path.append(os.path.join(parent_dir, "batch_scrapers", "perfect_game"))
    from perfect_game_scraper import PerfectGameScraper
    from filters import PerfectGameFilters, FilterBuilder
    from utils import PerfectGameUtils

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
from azure_storage import AzureDataLakeUploader


class TournamentSearchMenu:
    """Interactive menu for Perfect Game tournament searching"""

    def __init__(self):
        # Ensure output directory exists (for direct execution)
        os.makedirs("output", exist_ok=True)

        self.scraper = PerfectGameScraper(headless=True, debug=True)
        self.filter_builder = FilterBuilder()
        self.last_results = None
        self.auto_upload = False  # Make Azure upload optional, not automatic by default

        # Initialize Azure Data Lake uploader
        try:
            self.azure_uploader = AzureDataLakeUploader()
            self.azure_available = True
            print("✅ Azure Data Lake integration available (optional)")
        except Exception as e:
            print(f"⚠️  Azure Data Lake not available: {e}")
            self.azure_uploader = None
            self.azure_available = False

    def display_header(self):
        """Display the menu header"""
        print("\n" + "=" * 60)
        print("🏆 PERFECT GAME TOURNAMENT SEARCH")
        print("=" * 60)

    def display_current_filters(self):
        """Display current filter settings"""
        filters = self.filter_builder.get_filters()
        print("📍 Current Filter Settings:")
        print(f"   1. State: {filters['state']}")
        print(f"   2. City: {filters['city']}")
        print(f"   3. Search Radius: {filters['radius']} miles")
        print(f"   4. Age Group: {filters['age_group']}")
        print(f"   5. Sport Type: {filters['sport_type']}")

        # Show date range
        start_date = datetime.strptime(filters["start_date"], "%Y-%m-%d")
        end_date = datetime.strptime(filters["end_date"], "%Y-%m-%d")
        days_range = (end_date - start_date).days
        print(f"   6. Date Range: Next {days_range} days")

    def display_menu_options(self):
        """Display menu options"""
        print("\n📋 Menu Options:")
        print("   1-6: Change filter settings")
        print("   7: 🔍 Search tournaments with current filters")
        print("   8: 📊 Test default filters (recommended)")
        print("   9: 💾 Save current filters")
        print("   10: 📈 Show last search results")
        if self.azure_available:
            print("   11: ☁️  Upload last results to Azure Data Lake")
            auto_status = "✅ ON" if self.auto_upload else "❌ OFF"
            print(f"   12: 🔄 Toggle auto-upload to Azure ({auto_status})")
        print("   0: ❌ Exit")

    def run_search_with_timer(self, test_mode: bool = False):
        """Run tournament search with live timer display"""
        filters = self.filter_builder.get_filters()

        print("\n🔍 Searching tournaments with filters:")
        print(PerfectGameFilters.format_filters_display(filters))
        print()

        if test_mode:
            print("🧪 RUNNING TEST SEARCH")
            print("⏳ Please wait, testing Perfect Game connection...")
        else:
            print("⏳ Please wait, searching Perfect Game database...")
        print()

        # Run the search (timer is handled within the scraper)
        results = self.scraper.search_tournaments(filters)
        self.last_results = results

        print()  # Add space after timer output

        # Display results
        self.display_search_results(results)

        return results

    def display_search_results(self, results):
        """Display search results with formatting"""
        if results.get("success"):
            tournaments = results.get("tournaments", [])
            count = len(tournaments)
            duration = results.get("search_duration", 0)

            print("📊 SEARCH RESULTS:")
            print(f"Found {count} tournaments matching your criteria")
            print(f"⏱️  Search completed in {duration}s")
            print()

            if tournaments:
                PerfectGameUtils.print_tournament_list(tournaments, max_display=5)

                # Save results
                filepath = PerfectGameUtils.save_json_results(results)
                if filepath:
                    print(f"💾 Results saved to: {filepath}")

                # Auto-upload to Azure Data Lake if available and enabled
                if self.azure_available and self.auto_upload and tournaments:
                    print("\n☁️ Auto-uploading to Azure Data Lake...")
                    try:
                        result = self.azure_uploader.upload_both_formats(
                            tournaments, run_type="automated"
                        )
                        # Check if both formats uploaded successfully
                        if result.get("raw_url") and result.get("processed_url"):
                            print("✅ Auto-upload successful!")
                            print("📁 Data uploaded to Azure Data Lake")
                            print(f"📊 Uploaded {result.get('count', 0)} tournaments")
                        elif result.get("raw_url") or result.get("processed_url"):
                            print(
                                "⚠️ Auto-upload partially successful - use option 11 to retry manually"
                            )
                        else:
                            print(
                                "⚠️ Auto-upload had issues - use option 11 to retry manually"
                            )
                    except Exception as e:
                        print(f"⚠️ Auto-upload failed: {e}")
                        print("💡 Use option 11 to upload manually")
            else:
                print("📭 No tournaments found matching your criteria")
                print("💡 Try adjusting your filters for broader results")
        else:
            error = results.get("error", "Unknown error")
            duration = results.get("search_duration", 0)
            print(f"❌ Search failed after {duration}s: {error}")

    def change_filter(self, filter_number: int):
        """Change a specific filter"""
        filters = self.filter_builder.get_filters()

        if filter_number == 1:  # State
            print("\n📍 Change State:")
            new_state = (
                input("Enter state abbreviation (e.g., TX, CA, FL): ").upper().strip()
            )
            if len(new_state) == 2:
                self.filter_builder.set_location(
                    new_state, filters["city"], filters["radius"]
                )
                print(f"✅ State updated to: {new_state}")
            else:
                print("❌ Invalid state abbreviation")

        elif filter_number == 2:  # City
            print("\n🏙️  Change City:")
            new_city = input("Enter city name: ").strip()
            if new_city:
                self.filter_builder.set_location(
                    filters["state"], new_city, filters["radius"]
                )
                print(f"✅ City updated to: {new_city}")
            else:
                print("❌ City name cannot be empty")

        elif filter_number == 3:  # Radius
            print("\n📏 Change Search Radius:")
            try:
                new_radius = int(input("Enter search radius in miles (10-100): "))
                if 10 <= new_radius <= 100:
                    self.filter_builder.set_location(
                        filters["state"], filters["city"], new_radius
                    )
                    print(f"✅ Search radius updated to: {new_radius} miles")
                else:
                    print("❌ Radius must be between 10 and 100 miles")
            except ValueError:
                print("❌ Please enter a valid number")

        elif filter_number == 4:  # Age Group
            print("\n👥 Change Age Group:")
            print("Available age groups:", ", ".join(PerfectGameFilters.AGE_GROUPS))
            new_age = input("Enter age group (e.g., 10U, 12U): ").upper().strip()
            if new_age in PerfectGameFilters.AGE_GROUPS:
                self.filter_builder.set_age_group(new_age)
                print(f"✅ Age group updated to: {new_age}")
            else:
                print(
                    f"❌ Invalid age group. Choose from: {', '.join(PerfectGameFilters.AGE_GROUPS)}"
                )

        elif filter_number == 5:  # Sport Type
            print("\n⚾ Change Sport Type:")
            print("Available sports:", ", ".join(PerfectGameFilters.SPORT_TYPES))
            new_sport = input("Enter sport type: ").strip().title()
            if new_sport in PerfectGameFilters.SPORT_TYPES:
                self.filter_builder.set_sport(new_sport)
                print(f"✅ Sport type updated to: {new_sport}")
            else:
                print(
                    f"❌ Invalid sport type. Choose from: {', '.join(PerfectGameFilters.SPORT_TYPES)}"
                )

        elif filter_number == 6:  # Date Range
            print("\n📅 Change Date Range:")
            print("1. Next 30 days")
            print("2. Next 60 days")
            print("3. Custom range")

            choice = input("Select option (1-3): ").strip()
            today = datetime.now()

            if choice == "1":
                end_date = today + timedelta(days=30)
                self.filter_builder.set_date_range(
                    today.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
                )
                print("✅ Date range updated to: Next 30 days")
            elif choice == "2":
                end_date = today + timedelta(days=60)
                self.filter_builder.set_date_range(
                    today.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
                )
                print("✅ Date range updated to: Next 60 days")
            elif choice == "3":
                try:
                    start_str = input("Enter start date (YYYY-MM-DD): ")
                    end_str = input("Enter end date (YYYY-MM-DD): ")
                    # Validate dates
                    datetime.strptime(start_str, "%Y-%m-%d")
                    datetime.strptime(end_str, "%Y-%m-%d")
                    self.filter_builder.set_date_range(start_str, end_str)
                    print(f"✅ Date range updated: {start_str} to {end_str}")
                except ValueError:
                    print("❌ Invalid date format. Use YYYY-MM-DD")
            else:
                print("❌ Invalid option")

    def save_current_filters(self):
        """Save current filter configuration"""
        filters = self.filter_builder.get_filters()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"perfect_game_filters_{timestamp}.json"

        filepath = PerfectGameUtils.save_json_results(
            {
                "filters": filters,
                "created_at": datetime.now().isoformat(),
                "description": "Perfect Game search filters",
            },
            filename,
        )

        if filepath:
            print(f"💾 Filters saved to: {filepath}")
        else:
            print("❌ Failed to save filters")

    def show_last_results(self):
        """Display last search results"""
        if self.last_results is None:
            print("📭 No previous search results available")
            return

        print("\n📈 LAST SEARCH RESULTS")
        print("=" * 30)
        self.display_search_results(self.last_results)

    def upload_to_azure(self):
        """Upload last search results to Azure Data Lake"""
        if not self.azure_available:
            print("❌ Azure Data Lake not available")
            print("💡 Please check your Azure configuration")
            return

        if self.last_results is None:
            print("📭 No search results to upload")
            print("💡 Run a search first (option 7 or 8)")
            return

        if not self.last_results.get("success", False):
            print("❌ Cannot upload failed search results")
            return

        tournaments = self.last_results.get("tournaments", [])
        if not tournaments:
            print("📭 No tournament data to upload")
            return

        print("\n☁️  UPLOADING TO AZURE DATA LAKE")
        print("=" * 40)

        try:
            # Upload both JSON and CSV formats
            print("⏳ Uploading tournament data...")

            result = self.azure_uploader.upload_both_formats(
                tournaments=tournaments, run_type="manual"
            )

            if result["raw_url"] and result["processed_url"]:
                print("✅ Upload successful!")
                print(f"📁 JSON file uploaded: {result['raw_url']}")
                print(f"📊 CSV file uploaded: {result['processed_url']}")
                print(f"📈 Uploaded {len(tournaments)} tournaments")
            elif result["raw_url"] or result["processed_url"]:
                print("⚠️ Partial upload success:")
                if result["raw_url"]:
                    print(f"📁 JSON file uploaded: {result['raw_url']}")
                if result["processed_url"]:
                    print(f"📊 CSV file uploaded: {result['processed_url']}")
            else:
                print("❌ Upload failed for both formats")
                print("💡 Check Azure connection and permissions")

        except Exception as e:
            print(f"❌ Upload error: {e}")
            print("💡 Please check your Azure connection")

    def run(self):
        """Main menu loop"""
        print("🚀 Starting Perfect Game Tournament Search...")

        while True:
            self.display_header()
            self.display_current_filters()
            self.display_menu_options()
            print("=" * 60)

            try:
                choice = input("\n👆 Select an option (0-11): ").strip()

                if choice == "0":
                    print("👋 Goodbye! Happy tournament searching!")
                    break
                elif choice in ["1", "2", "3", "4", "5", "6"]:
                    self.change_filter(int(choice))
                elif choice == "7":
                    self.run_search_with_timer(test_mode=False)
                elif choice == "8":
                    print("\n🧪 TESTING DEFAULT FILTERS")
                    print("=" * 50)
                    print("Testing with default settings:")
                    filters = self.filter_builder.get_filters()
                    print(
                        f"   📍 {filters['city']}, {filters['state']} ({filters['radius']} miles)"
                    )
                    print(f"   👥 {filters['age_group']} {filters['sport_type']}")
                    print()
                    print("⏳ Running test search...")
                    print()

                    self.run_search_with_timer(test_mode=True)
                elif choice == "9":
                    self.save_current_filters()
                elif choice == "10":
                    self.show_last_results()
                elif choice == "11":
                    self.upload_to_azure()
                elif choice == "12" and self.azure_available:
                    self.toggle_auto_upload()
                else:
                    max_option = "12" if self.azure_available else "10"
                    print(f"❌ Invalid option. Please select 0-{max_option}.")

                if choice != "0":
                    input("\n⏎ Press Enter to continue...")

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted by user. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("⏎ Press Enter to continue...")

    def toggle_auto_upload(self):
        """Toggle automatic Azure Data Lake upload on/off"""
        self.auto_upload = not self.auto_upload
        status = "✅ ENABLED" if self.auto_upload else "❌ DISABLED"
        print(f"\n🔄 Auto-upload to Azure Data Lake: {status}")

        if self.auto_upload:
            print("💡 Tournament data will be automatically uploaded after searches")
        else:
            print("💡 Use option 11 to manually upload tournament data")


if __name__ == "__main__":
    menu = TournamentSearchMenu()
    menu.run()

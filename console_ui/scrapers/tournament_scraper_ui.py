#!/usr/bin/env python3
"""
Terminal UI for testing Perfect Game tournament scraper.
"""

import sys
import os
from pathlib import Path

# Direct import approach to avoid circular dependency
scraper_path = Path(__file__).parent / "scraper"
sys.path.insert(0, str(scraper_path))
sys.path.insert(0, str(scraper_path / "perfectgame"))

from scraper import PerfectGameScraper
import json
from datetime import datetime
import signal


def print_banner():
    """Print a nice banner."""
    print("\n" + "=" * 60)
    print("🏆 PERFECT GAME TOURNAMENT SCRAPER TEST UI")
    print("=" * 60)


def get_user_input():
    """Get search parameters from user."""
    print("\n📝 Enter search parameters (or press Enter for defaults):")

    age_group = input("Age Group [10U]: ").strip() or "10U"
    city = input("City [Houston]: ").strip() or "Houston"
    state = input("State [TX]: ").strip() or "TX"

    try:
        distance = int(input("Distance in miles [50]: ").strip() or "50")
    except ValueError:
        distance = 50

    # Add date range options
    print("\n📅 Date Range Options:")
    print("1. Current month (August 2025) [default]")
    print("2. Next 30 days")
    print("3. Next 60 days") 
    print("4. Custom date range")
    
    date_choice = input("Choose date range (1-4) [1]: ").strip() or "1"
    
    # Set date range based on choice
    from datetime import datetime, timedelta
    today = datetime.now().date()
    
    if date_choice == "2":
        start_date = today.strftime("%Y-%m-%d")
        end_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")
        print(f"📅 Selected: Next 30 days ({start_date} to {end_date})")
    elif date_choice == "3":
        start_date = today.strftime("%Y-%m-%d")
        end_date = (today + timedelta(days=60)).strftime("%Y-%m-%d")
        print(f"📅 Selected: Next 60 days ({start_date} to {end_date})")
    elif date_choice == "4":
        print("📅 Custom date range:")
        start_date = input("Start date (YYYY-MM-DD) [2025-08-01]: ").strip() or "2025-08-01"
        end_date = input("End date (YYYY-MM-DD) [2025-08-31]: ").strip() or "2025-08-31"
        print(f"📅 Selected: Custom range ({start_date} to {end_date})")
    else:
        # Default: Current month (August 2025)
        start_date = "2025-08-01"
        end_date = "2025-08-31"
        print(f"📅 Selected: Current month ({start_date} to {end_date})")

    headless = input("\nRun browser headless? (y/n) [y]: ").strip().lower()
    headless = headless != "n"

    params = {
        "age_group": age_group,
        "city": city,
        "state": state,
        "distance_miles": distance,
        "start_date": start_date,
        "end_date": end_date,
    }

    return params, headless


def display_results(results):
    """Display search results in a nice format."""
    print("\n" + "=" * 60)
    print("🎯 SEARCH RESULTS")
    print("=" * 60)

    metadata = results.get("search_metadata", {})
    tournaments = results.get("tournaments", [])

    print(f"📊 Search took: {metadata.get('duration_seconds', 0):.2f} seconds")
    print(f"🏆 Tournaments found: {metadata.get('total_found', 0)}")
    print(f"� Search timestamp: {metadata.get('timestamp', 'Unknown')}")

    if tournaments:
        print(f"\n🎯 FILTERS USED:")
        filters = metadata.get("filters", {})
        for key, value in filters.items():
            print(f"  {key}: {value}")

        print(f"\n🏆 TOURNAMENT DETAILS:")
        print("-" * 60)

        for i, tournament in enumerate(tournaments, 1):
            print(f"\n{i}. {tournament.get('name', 'Unknown Tournament')}")
            print(f"   📍 Location: {tournament.get('location', 'N/A')}")
            print(
                f"   📅 Dates: {tournament.get('start_date', 'N/A')} to {tournament.get('end_date', 'N/A')}"
            )
            print(f"   🎯 Age Group: {tournament.get('age_group', 'N/A')}")
            print(f"   📏 Distance: {tournament.get('distance_miles', 'N/A')} miles")
            print(f"   💰 Entry Fee: {tournament.get('entry_fee', 'N/A')}")
            print(f"   👥 Teams: {tournament.get('team_count', 'N/A')}")
            if tournament.get("description"):
                print(f"   📝 Description: {tournament.get('description', '')}")
    else:
        print("\n❌ No tournaments found with the specified criteria.")


def save_results(results):
    """Save results to a JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"tournament_search_results_{timestamp}.json"

    try:
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to: {filename}")
    except Exception as e:
        print(f"\n❌ Failed to save results: {e}")


def main():
    """Main function."""
    print_banner()

    scraper = None

    while True:
        try:
            # Get search parameters
            params, headless = get_user_input()

            print(f"\n🚀 Starting search with parameters: {params}")
            print(f"🖥️  Browser mode: {'Headless' if headless else 'Visible'}")

            # Initialize scraper with proper cleanup
            print("\n🔧 Initializing scraper...")
            scraper = PerfectGameScraper()
            scraper.selenium.headless = headless

            print("⏳ Searching for tournaments... (this may take 15-30 seconds)")
            print("💡 Press Ctrl+C to cancel search")

            # Perform search with timeout
            results = scraper.search_tournaments(**params)

            # Display results
            display_results(results)

            # Clean up scraper
            print("\n🧹 Cleaning up browser...")
            scraper.close()
            scraper = None

            # Ask if user wants to save results
            save_choice = input("\n💾 Save results to file? (y/n): ").strip().lower()
            if save_choice == "y":
                save_results(results)

            # Ask if user wants to search again
            again = input("\n🔄 Search again? (y/n): ").strip().lower()
            if again != "y":
                print("\n👋 Thanks for testing the scraper!")
                break

        except KeyboardInterrupt:
            print("\n\n⚠️  Search cancelled by user!")
            if scraper:
                print("🧹 Cleaning up browser...")
                try:
                    scraper.close()
                except:
                    pass
                scraper = None

            again = input("\n🔄 Try again? (y/n): ").strip().lower()
            if again != "y":
                print("\n👋 Goodbye!")
                break

        except Exception as e:
            print(f"\n❌ Error occurred: {e}")
            if scraper:
                print("🧹 Cleaning up browser...")
                try:
                    scraper.close()
                except:
                    pass
                scraper = None

            again = input("\n🔄 Try again? (y/n): ").strip().lower()
            if again != "y":
                print("\n👋 Goodbye!")
                break

    # Final cleanup
    if scraper:
        try:
            scraper.close()
        except:
            pass

    print("\n✅ Tournament scraper test completed!")


if __name__ == "__main__":
    main()

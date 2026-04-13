#!/usr/bin/env python3
"""
Tournament Scraper Main Entry Point

Central entry point for all tournament scrapers with clean interface.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def show_welcome():
    """Display welcome message and available scrapers"""
    print("🏆 LINEDRIVE TOURNAMENT SCRAPERS")
    print("=" * 50)
    print("Available tournament scrapers:")
    print()
    print("1. 🔵 Perfect Game Tournaments")
    print("   - Professional baseball tournaments")
    print("   - Location-based search")
    print("   - Age group filtering")
    print("   - Live timer display")
    print()
    print("2. 🌐 Generic URL Scraper")
    print("   - Scrape any URL and its subpages")
    print("   - Configurable depth and page limits")
    print("   - Azure Data Lake storage option")
    print()
    print("3. 🎬 YouTube Transcript Grabber")
    print("   - Extract transcripts from YouTube videos")
    print("   - Multiple language support")
    print("   - Azure Data Lake storage option")
    print()
    print("4. 🔴 USSSA Tournaments (Coming Soon)")
    print("5. 🟡 Triple Crown Sports (Coming Soon)")
    print("6. 🟢 GameChanger (Coming Soon)")
    print()


def run_url_scraper():
    """Launch Generic URL scraper menu"""
    try:
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)

        # Import and run URL scraper menu
        from console_ui.scrapers.url_scraper_menu import URLScraperMenu

        menu = URLScraperMenu()
        menu.run()
    except ImportError as e:
        print(f"❌ Error importing URL scraper: {e}")
        print("💡 Make sure you're in the correct directory")
    except Exception as e:
        print(f"❌ Error running URL scraper: {e}")


def run_youtube_transcript():
    """Launch YouTube Transcript Grabber menu"""
    try:
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)

        # Import and run YouTube transcript menu
        from console_ui.scrapers.youtube_transcript_menu import YouTubeTranscriptMenu

        menu = YouTubeTranscriptMenu()
        menu.run()
    except ImportError as e:
        print(f"❌ Error importing YouTube transcript grabber: {e}")
        print("💡 Make sure you're in the correct directory")
    except Exception as e:
        print(f"❌ Error running YouTube transcript grabber: {e}")


def run_perfect_game():
    """Launch Perfect Game scraper menu"""
    try:
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)

        # Import and run Perfect Game menu
        from console_ui.scrapers.perfect_game_menu import TournamentSearchMenu

        menu = TournamentSearchMenu()
        menu.run()
    except ImportError as e:
        print(f"❌ Error importing Perfect Game scraper: {e}")
        print("💡 Make sure you're in the correct directory")
    except Exception as e:
        print(f"❌ Error running Perfect Game scraper: {e}")


def main():
    """Main entry point"""
    while True:
        show_welcome()

        print("📋 Options:")
        print("1. Launch Perfect Game scraper")
        print("2. Launch Generic URL scraper")
        print("3. Launch YouTube Transcript Grabber")
        print("4. View documentation")
        print("5. Run tests")
        print("0. Exit")
        print("=" * 50)

        try:
            choice = input("\n👆 Select an option (0-5): ").strip()

            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                print("\n🚀 Launching Perfect Game Tournament Scraper...")
                run_perfect_game()
            elif choice == "2":
                print("\n🚀 Launching Generic URL Scraper...")
                run_url_scraper()
            elif choice == "3":
                print("\n🚀 Launching YouTube Transcript Grabber...")
                run_youtube_transcript()
            elif choice == "4":
                print("\n📖 Opening documentation...")
                print("See README.md for detailed documentation")
            elif choice == "5":
                print("\n🧪 Running tests...")
                print("Test functionality coming soon")
            else:
                print("❌ Invalid option. Please select 0-5.")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("⏎ Press Enter to continue...")


if __name__ == "__main__":
    main()

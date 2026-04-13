#!/usr/bin/env python3
"""
Menu handlers for LineDrive Console
Contains all menu display and navigation logic
"""

import subprocess
import sys
from pathlib import Path

# Get the project root directory (parent of console_ui)
PROJECT_ROOT = Path(__file__).parent.parent


def show_main_menu():
    """Display the main menu options"""
    print("\n🏆 LINEDRIVE CONSOLE UI")
    print("=" * 50)
    print("Select a category:")
    print()
    print("1. 🔍 Scrapers")
    print("   - Perfect Game tournaments")
    print("   - URL scraping")
    print("   - YouTube transcripts")
    print()
    print("2. 🤖 Automation")
    print("   - 4-Agent script creation & review")
    print("   - Demo package generation")
    print("   - AutoGen tournament planning")
    print("   - Batch job runner")
    print("   - Thumbnail generator")
    print("   - B-Roll video downloader")
    print()
    print("3. 📱 Social Media")
    print("   - AI tweet generator")
    print("   - Social media verification")
    print("   - Manual posting")
    print()
    print("4. 🧪 Agent Testing")
    print("   - Demo Script Creator")
    print("   - Azure OpenAI demo generation")
    print("   - Developer + Everyday viewer demos")
    print()
    print("0. Exit")
    print("=" * 50)


def run_scrapers_menu():
    """Handle scrapers menu selection"""
    while True:
        print("\n🔍 SCRAPERS MENU")
        print("=" * 30)
        print("1. Perfect Game Tournament Scraper")
        print("2. URL Scraping")
        print("3. YouTube Transcript Scraper")
        print("4. Batch Scraper")
        print("0. Back to main menu")
        print("=" * 30)

        try:
            choice = input("👆 Select scraper (0-4): ").strip()
        except EOFError:
            choice = "0"
            print(f"   Using default (EOF): {choice}")

        if choice == "0":
            break
        elif choice == "1":
            subprocess.run(
                [sys.executable, "console_ui/scrapers/perfect_game_menu.py"], cwd=PROJECT_ROOT)
        elif choice == "2":
            subprocess.run(
                [sys.executable, "console_ui/scrapers/url_scraper_menu.py"], cwd=PROJECT_ROOT)
        elif choice == "3":
            subprocess.run(
                [sys.executable, "console_ui/scrapers/youtube_transcript_menu.py"], cwd=PROJECT_ROOT
            )
        elif choice == "4":
            subprocess.run(
                [sys.executable, "console_ui/scrapers/batch_scraper_ui.py"], cwd=PROJECT_ROOT)
        else:
            print("❌ Invalid selection. Please choose 0-4.")


def run_automation_menu():
    """Handle automation menu selection"""
    while True:
        print("\n🤖 AUTOMATION MENU")
        print("=" * 30)
        print("1. AutoGen Tournament UI")
        print("2. Batch Job Runner")
        print("3. 🎬 Complete 4-Agent Script → Demo Workflow")
        print("4. 🪄 Script Polisher → Demo Workflow")
        print("5. 🎥 Demo Script Creator")
        print("6. 🖼️ Thumbnail Generator")
        print("7. 🎬 B-Roll Video Downloader")
        print("0. Back to main menu")
        print("=" * 30)

        try:
            choice = input("👆 Select automation tool (0-7): ").strip()
        except EOFError:
            choice = "0"
            print(f"   Using default (EOF): {choice}")

        if choice == "0":
            break
        elif choice == "1":
            subprocess.run(
                [sys.executable, "console_ui/automation/autogen_tournament_ui.py"], cwd=PROJECT_ROOT
            )
        elif choice == "2":
            subprocess.run(
                [sys.executable, "console_ui/automation/batch_job_runner.py"], cwd=PROJECT_ROOT
            )
        elif choice == "3":
            # Import here to avoid circular imports
            import asyncio
            from workflows import run_script_to_demo_workflow

            asyncio.run(run_script_to_demo_workflow())
        elif choice == "4":
            import asyncio
            from workflows import run_script_polisher_workflow

            asyncio.run(run_script_polisher_workflow())
        elif choice == "5":
            import asyncio
            from workflows import run_demo_script_creator

            asyncio.run(run_demo_script_creator())
        elif choice == "6":
            # Launch thumbnail generator
            subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "from tools.media.branded_thumbnail_generator import main; main()",
                ]
            )
        elif choice == "7":
            # B-Roll Video Downloader
            import asyncio
            from workflows import run_broll_downloader_workflow

            asyncio.run(run_broll_downloader_workflow())
        else:
            print("❌ Invalid selection. Please choose 0-7.")


def run_social_media_menu():
    """Handle social media menu selection"""
    while True:
        print("\n📱 SOCIAL MEDIA MENU")
        print("=" * 30)
        print("1. AI Tweet Generator")
        print("2. Social Media Verification")
        print("3. Quick Tweet UI")
        print("0. Back to main menu")
        print("=" * 30)

        try:
            choice = input("👆 Select social media tool (0-3): ").strip()
        except EOFError:
            choice = "0"
            print(f"   Using default (EOF): {choice}")

        if choice == "0":
            break
        elif choice == "1":
            subprocess.run(
                [sys.executable, "console_ui/social_media/ai_tweet_generator.py"], cwd=PROJECT_ROOT
            )
        elif choice == "2":
            subprocess.run(
                [sys.executable, "console_ui/social_media/verify_social_media_ui.py"], cwd=PROJECT_ROOT
            )
        elif choice == "3":
            subprocess.run(
                [sys.executable, "console_ui/social_media/quick_tweet_ui.py"], cwd=PROJECT_ROOT
            )
        else:
            print("❌ Invalid selection. Please choose 0-3.")


def run_agent_testing_menu():
    """Handle agent testing menu selection"""
    while True:
        print("\n🧪 AGENT TESTING MENU")
        print("=" * 30)
        print("1. Demo Script Creator")
        print("2. Azure OpenAI Demo Generation")
        print("0. Back to main menu")
        print("=" * 30)

        try:
            choice = input("👆 Select testing tool (0-2): ").strip()
        except EOFError:
            choice = "0"
            print(f"   Using default (EOF): {choice}")

        if choice == "0":
            break
        elif choice == "1":
            import asyncio
            from workflows import run_demo_script_creator

            asyncio.run(run_demo_script_creator())
        elif choice == "2":
            print("🚧 Azure OpenAI Demo Generation - Coming Soon!")
        else:
            print("❌ Invalid selection. Please choose 0-2.")

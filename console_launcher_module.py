#!/usr/bin/env python3
"""
LineDrive Console Launcher - Modular Version

Simple launcher for all console-based interfaces organized by category.
This version uses modular components from the console_ui package.
"""

import sys
import os
from pathlib import Path

# Add current directory and console_ui to path for imports
# This ensures imports work after macOS updates that change path behavior
project_root = Path(__file__).parent
console_ui_path = project_root / "console_ui"

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(console_ui_path))

print(f"🔧 Added to Python path: {project_root}")
print(f"🔧 Added to Python path: {console_ui_path}")

try:
    from console_ui.menu_handlers import show_main_menu
    from console_ui.utils import sanitize_filename, extract_script_title
    from console_ui.text_processing import extract_teleprompter_text
    from console_ui.word_processing import convert_markdown_to_word

    MODULAR_IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Modular imports not available: {e}")
    print(f"🔍 Current working directory: {os.getcwd()}")
    print(f"🔍 Python path: {sys.path[:5]}")
    MODULAR_IMPORTS_AVAILABLE = False


def main():
    """Main console launcher"""
    # Set up Python environment
    print("🚀 Starting LineDrive Console...")

    # Virtual environment check
    if hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        print("✅ Virtual environment activated")
    else:
        print("⚠️ Not running in virtual environment")

    print(f"🔧 Python path: {sys.executable}")

    # Check if console UI is available
    if not MODULAR_IMPORTS_AVAILABLE:
        print("❌ Console UI modules not available. Using fallback mode.")
        print("🔧 Please ensure console_ui package is properly set up.")
        return

    print("🚀 Starting LineDrive Console UI...")
    print(f"📍 Current directory: {os.getcwd()}")
    print(f"🐍 Python version: {sys.version.split()[0]}")
    print()

    # Main menu loop
    while True:
        if MODULAR_IMPORTS_AVAILABLE:
            show_main_menu()
        else:
            # Fallback simple menu
            print("\n🏆 LINEDRIVE CONSOLE UI (FALLBACK)")
            print("=" * 50)
            print("1. 🔍 Scrapers (Limited)")
            print("2. 🤖 Automation (Limited)")
            print("3. 📱 Social Media (Limited)")
            print("0. Exit")
            print("=" * 50)

        try:
            choice = input("👆 Select category (0-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            choice = "0"
            print(f"\\n   Exiting...")

        if choice == "0":
            print("\\n👋 Goodbye!")
            print("👋 LineDrive Console session ended")
            break
        elif choice == "1":
            if MODULAR_IMPORTS_AVAILABLE:
                from console_ui.menu_handlers import run_scrapers_menu

                run_scrapers_menu()
            else:
                print("🔍 Scrapers functionality requires full console_ui setup")
        elif choice == "2":
            if MODULAR_IMPORTS_AVAILABLE:
                from console_ui.menu_handlers import run_automation_menu

                run_automation_menu()
            else:
                print("🤖 Automation functionality requires full console_ui setup")
        elif choice == "3":
            if MODULAR_IMPORTS_AVAILABLE:
                from console_ui.menu_handlers import run_social_media_menu

                run_social_media_menu()
            else:
                print("📱 Social Media functionality requires full console_ui setup")
        elif choice == "4":
            if MODULAR_IMPORTS_AVAILABLE:
                from console_ui.menu_handlers import run_agent_testing_menu

                run_agent_testing_menu()
            else:
                print("🧪 Agent Testing functionality requires full console_ui setup")
        else:
            print("❌ Invalid selection. Please choose 0-4.")


if __name__ == "__main__":
    main()

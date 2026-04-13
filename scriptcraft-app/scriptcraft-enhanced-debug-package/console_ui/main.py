#!/usr/bin/env python3
"""
Main entry point for LineDrive Console UI
Modular system with organized menu structure
"""

import sys
from pathlib import Path

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from menu_handlers import (
    show_main_menu,
    run_scrapers_menu,
    run_automation_menu,
    run_social_media_menu,
    run_agent_testing_menu,
)


def main():
    """Main console UI entry point"""
    print("🚀 Starting LineDrive Modular Console UI...")

    while True:
        try:
            show_main_menu()
            choice = input("👆 Select category (0-4): ").strip()
        except EOFError:
            choice = "0"
            print(f"   Using default (EOF): {choice}")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            sys.exit(0)

        if choice == "0":
            print("👋 Goodbye!")
            break
        elif choice == "1":
            run_scrapers_menu()
        elif choice == "2":
            run_automation_menu()
        elif choice == "3":
            run_social_media_menu()
        elif choice == "4":
            run_agent_testing_menu()
        else:
            print("❌ Invalid selection. Please choose 0-4.")


if __name__ == "__main__":
    main()

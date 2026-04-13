#!/usr/bin/env python3
"""
Social Media Launcher - Main entry point for social media posting tools
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def display_main_menu():
    """Display the main social media platform menu"""
    print("\n🚀 LINEDRIVE SOCIAL MEDIA TOOLS")
    print("=" * 60)
    print("Welcome to the Social Media Posting Interface")
    print("Choose a platform to get started:")
    print()
    print("Available Platforms:")
    print("1. 🐦 X (Twitter) - Post tweets and manage X account")
    print("2. 📘 Facebook - Coming Soon!")
    print("3. 📷 Instagram - Coming Soon!")
    print("4. 💼 LinkedIn - Coming Soon!")
    print("5. 🎵 TikTok - Coming Soon!")
    print()
    print("Other Options:")
    print("8. 🧪 Test All Connections")
    print("9. ⚙️  Configuration Settings")
    print("0. 🚪 Exit")
    print("=" * 60)


def launch_x_interface():
    """Launch the X (Twitter) posting interface"""
    try:
        from console_ui.x_posting_ui import XPostingUI

        print("\n🐦 Launching X (Twitter) Interface...")
        ui = XPostingUI()
        ui.run()

    except ImportError as e:
        print(f"❌ Error importing X interface: {e}")
        print("Make sure the social_media package is properly installed.")
    except Exception as e:
        print(f"❌ Error launching X interface: {e}")


def test_all_connections():
    """Test connections to all available platforms"""
    print("\n🧪 TESTING ALL PLATFORM CONNECTIONS")
    print("=" * 50)

    # Test X (Twitter)
    try:
        from social_media.platforms.x_platform import XPlatformHandler

        print("🐦 Testing X (Twitter)...")
        handler = XPlatformHandler()

        if handler.test_connection():
            user_info = handler.get_user_info()
            if user_info.get("success"):
                print(
                    f"   ✅ Connected as @{user_info['username']} ({user_info['name']})"
                )
                print(f"   👥 Followers: {user_info.get('followers_count', 0):,}")
            else:
                print("   ⚠️  Connection OK but couldn't get user info")
        else:
            print("   ❌ Connection failed")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Other platforms (coming soon)
    print("📘 Facebook: 🔜 Coming Soon")
    print("📷 Instagram: 🔜 Coming Soon")
    print("💼 LinkedIn: 🔜 Coming Soon")
    print("🎵 TikTok: 🔜 Coming Soon")


def show_configuration():
    """Show configuration options"""
    print("\n⚙️  CONFIGURATION SETTINGS")
    print("=" * 40)

    # Check X credentials
    try:
        from social_media.config.x_config import XConfig

        config = XConfig()

        if config.has_credentials():
            print("🐦 X (Twitter): ✅ Credentials configured")
        else:
            print("🐦 X (Twitter): ❌ No credentials found")
            print("   Run: python3 social_media/platforms/setup_x_credentials.py")
    except Exception as e:
        print(f"🐦 X (Twitter): ❌ Error checking config: {e}")

    print("📘 Facebook: 🔜 Not configured")
    print("📷 Instagram: 🔜 Not configured")
    print("💼 LinkedIn: 🔜 Not configured")
    print("🎵 TikTok: 🔜 Not configured")


def main():
    """Main application loop"""
    print("🚀 Starting LineDrive Social Media Tools...")

    while True:
        try:
            display_main_menu()
            choice = input("\n👆 Select an option (0-9): ").strip()

            if choice == "0":
                print("\n👋 Thanks for using LineDrive Social Media Tools!")
                break
            elif choice == "1":
                launch_x_interface()
            elif choice in ["2", "3", "4", "5"]:
                platform_names = {
                    "2": "Facebook",
                    "3": "Instagram",
                    "4": "LinkedIn",
                    "5": "TikTok",
                }
                print(f"\n🔜 {platform_names[choice]} integration coming soon!")
                print("Stay tuned for updates!")
            elif choice == "8":
                test_all_connections()
            elif choice == "9":
                show_configuration()
            else:
                print("❌ Invalid option. Please try again.")

            # Pause before showing menu again
            if choice != "0":
                input("\nPress Enter to continue...")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
X (Twitter) Posting UI - Simple console interface for posting to X
"""

import sys
from pathlib import Path
import asyncio

# Add project root to path for social media imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from social_media.platforms.x_platform import XPlatformHandler
from social_media.config.x_config import XConfig
from console_ui.ai_tweet_generator import AITweetGenerator
from console_ui.ai_tweet_generator import AITweetGenerator


class XPostingUI:
    """Console UI for posting to X (Twitter)"""

    def __init__(self):
        self.handler = XPlatformHandler()
        self.config = XConfig()
        # Cache user info to avoid excessive API calls
        self._user_info_cache = None

    def get_cached_user_info(self):
        """Get user info with caching to avoid rate limits"""
        if self._user_info_cache is None:
            self._user_info_cache = self.handler.get_user_info()
        return self._user_info_cache

    def display_menu(self):
        """Display the main menu"""
        print("\n🐦 X (TWITTER) POSTING INTERFACE")
        print("=" * 60)

        user_info = self.get_cached_user_info()
        if user_info.get("success"):
            print(f"📱 Connected as: @{user_info['username']} ({user_info['name']})")
            print(f"👥 Followers: {user_info.get('followers_count', 'N/A'):,}")

        print("\nMenu Options:")
        print("1. 📝 Post Text Tweet")
        print("2. 🤖 AI-Powered Tweet Generator")
        print("3. 👤 View Account Information")
        print("4. 🧪 Test X API Connection")
        print("0. 🚪 Exit")
        print("=" * 60)

    def post_text_tweet(self):
        """Handle text tweet posting"""
        print("\n📝 POST TEXT TWEET")
        print("=" * 40)

        print("Enter your tweet text (max 280 characters):")
        print("(Type your message and press Enter)")

        try:
            tweet_text = input("Tweet: ").strip()
        except KeyboardInterrupt:
            print("\n❌ Tweet cancelled.")
            return

        if not tweet_text:
            print("❌ Tweet cannot be empty.")
            return

        # Show character count
        char_count = len(tweet_text)
        print(f"\n📊 Character count: {char_count}/280")

        if char_count > 280:
            print("❌ Tweet is too long. Please shorten it.")
            return

        # Preview tweet
        print(f"\n�� Preview:")
        print("-" * 40)
        print(tweet_text)
        print("-" * 40)

        # Confirm posting
        confirm = input("\n�� Post this tweet? (y/N): ").strip().lower()
        if confirm not in ["y", "yes"]:
            print("❌ Tweet cancelled.")
            return

        # Post the tweet
        print("\n📤 Posting tweet...")
        result = self.handler.post_text(tweet_text)

        if result.get("success"):
            print(f"\n🎉 Tweet posted successfully!")
            print(f"🔗 URL: {result.get('url', 'N/A')}")
        else:
            print(f"\n❌ Failed to post tweet: {result.get('error', 'Unknown error')}")

    def launch_ai_tweet_generator(self):
        """Launch the AI-powered tweet generator"""
        print("\n🤖 Launching AI Tweet Generator...")
        print("=" * 40)

        try:
            ai_generator = AITweetGenerator()
            asyncio.run(ai_generator.main())
        except Exception as e:
            print(f"❌ Error launching AI Tweet Generator: {e}")
            print("💡 Make sure Azure AI credentials are configured")

    def view_account_info(self):
        """Display account information"""
        print("\n👤 ACCOUNT INFORMATION")
        print("=" * 40)

        user_info = self.handler.get_user_info()

        if user_info.get("success"):
            print(f"Username: @{user_info['username']}")
            print(f"Display Name: {user_info['name']}")
            print(f"User ID: {user_info['id']}")
            print(f"Description: {user_info.get('description', 'None')}")
            print(f"Followers: {user_info.get('followers_count', 0):,}")
            print(f"Following: {user_info.get('following_count', 0):,}")
            print(f"Total Tweets: {user_info.get('tweet_count', 0):,}")
            print(f"Verified: {'Yes' if user_info.get('verified') else 'No'}")
        else:
            print(
                f"❌ Failed to get account info: {user_info.get('error', 'Unknown error')}"
            )

    def test_connection(self):
        """Test the X API connection"""
        print("\n🧪 TESTING X API CONNECTION")
        print("=" * 40)

        print("Testing X API connection...")
        if self.handler.test_connection():
            print("✅ X API connection successful!")
        else:
            print("❌ X API connection failed!")

    def run(self):
        """Main UI loop"""
        print("🚀 Starting X Posting Interface...")

        # Test connection first
        if not self.handler.test_connection():
            print("❌ Cannot connect to X API. Please check your credentials.")
            return

        # Main menu loop
        while True:
            try:
                self.display_menu()
                choice = input("\n👆 Select an option (0-4): ").strip()

                if choice == "0":
                    print("\n👋 Thanks for using X Posting Interface!")
                    break
                elif choice == "1":
                    self.post_text_tweet()
                elif choice == "2":
                    self.launch_ai_tweet_generator()
                elif choice == "3":
                    self.view_account_info()
                elif choice == "4":
                    self.test_connection()
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
    ui = XPostingUI()
    ui.run()

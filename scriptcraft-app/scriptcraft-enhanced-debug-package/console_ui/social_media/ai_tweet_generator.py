#!/usr/bin/env python3
"""
AI-Powered Tweet Generator
Generate tweets using Azure AI Foundry and post to X (Twitter)
"""

import sys
import os
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(
    __file__
).parent.parent.parent  # Go up three levels to reach project root
sys.path.insert(0, str(project_root))

# Also add social_media directory for config imports
social_media_path = project_root / "social_media"
sys.path.insert(0, str(social_media_path))

from social_media.platforms.x_platform import XPlatformHandler
from linedrive_azure.functions.ai_tip_agent_client import AITipAgentClient


class FoundryAIContentGenerator:
    """Minimal async wrapper around the Linedrive AI Foundry agent client.

    Provides the async methods used by the UI: generate_ai_tip,
    generate_tech_insight, and generate_custom_tweet. Internally runs the
    synchronous agent client in a thread to avoid blocking the event loop.
    """

    def __init__(self):
        self.client = AITipAgentClient()

    async def _run_prompt(self, prompt: str):

        def sync_call():
            try:
                thread = self.client.create_thread()
                thread_id = getattr(thread, "id", None) or thread
                return self.client.send_message(thread_id, prompt, show_sources=False)
            except Exception as e:
                return {"success": False, "error": str(e), "response": None}

        # Run blocking client in thread and normalize response to UI format
        run_result = await asyncio.to_thread(sync_call)

        if not run_result or not run_result.get("success"):
            return {
                "success": False,
                "error": (
                    run_result.get("error")
                    if isinstance(run_result, dict)
                    else "Unknown error"
                ),
                "content": (
                    run_result.get("response") if isinstance(run_result, dict) else None
                ),
            }

        # Successful run - normalize fields expected by the UI
        content = run_result.get("response") or ""
        return {
            "success": True,
            "content": content,
            "character_count": len(content),
            "model": "AI Foundry",
            "raw": run_result,
        }

    async def generate_ai_tip(self, topic: str = "AI and machine learning"):
        prompt = (
            f"Write a short, engaging X (Twitter) tip about '{topic}'. "
            "Keep it under 240 characters, friendly and actionable. Include no hashtags."
        )
        return await self._run_prompt(prompt)

    async def generate_tech_insight(self):
        prompt = (
            "Provide a concise technical insight suitable for posting on X. "
            "Keep it under 240 characters, include one clear takeaway and a brief actionable step."
        )
        return await self._run_prompt(prompt)

    async def generate_custom_tweet(self, user_request: str):
        prompt = (
            f"Generate a single X (Twitter) post based on this request: {user_request}. "
            "Keep it under 240 characters, one clear message, friendly tone."
        )
        return await self._run_prompt(prompt)


class AITweetGenerator:
    """AI-powered tweet generator and poster"""

    def __init__(self):
        self.ai_generator = FoundryAIContentGenerator()
        self.x_handler = XPlatformHandler()

    def display_main_menu(self):
        """Display the main menu"""
        print("\n🤖 AI TWEET GENERATOR & MANUAL POSTING")
        print("=" * 55)
        print("Generate AI-powered tweets OR post manual tweets to X")
        print()
        print("📝 Manual Options:")
        print("1. ✍️  Post Manual Tweet (Type your own)")
        print()
        print("🤖 AI Generation Options:")
        print("2. 💡 Generate AI Tip of the Day")
        print("3. 🚀 Generate Tech Insight")
        print("4. ✨ Generate Custom Tweet")
        print("5. 🐦 Generate & Post AI Tip")
        print("6. 🎯 Generate & Post Tech Insight")
        print()
        print("ℹ️  Other:")
        print("7. 📊 View X Account Status")
        print("0. ← Back to Main Menu")
        print("=" * 55)

    async def post_manual_tweet(self):
        """Handle manual tweet posting"""
        print("\n📝 POST MANUAL TWEET")
        print("=" * 35)

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
        print(f"\n📋 Preview:")
        print("-" * 40)
        print(tweet_text)
        print("-" * 40)

        # Post the tweet directly
        await self.post_tweet(tweet_text)

    async def generate_and_show_ai_tip(self):
        """Generate and display an AI tip"""
        print("\n🎯 AI Tip Generator")
        print("-" * 30)

        topic = input("Enter topic (or press Enter for default): ").strip()
        if not topic:
            topic = "AI and machine learning"

        print(f"\n🤖 Generating AI tip about '{topic}' using AI Foundry Agent...")
        result = await self.ai_generator.generate_ai_tip(topic)

        if result["success"]:
            print(f"\n✅ Generated AI Tip ({result['character_count']} characters):")
            print(f"📱 {result['content']}")
            print(f"🤖 Model: {result['model']}")

            # Ask if user wants to post it
            post_now = input("\n📤 Post this to X now? (y/n): ").strip().lower()
            if post_now == "y":
                await self.post_tweet(result["content"])
        else:
            print(f"\n❌ Generation failed: {result['error']}")
            print(f"📱 Fallback content: {result['content']}")

    async def generate_and_show_tech_insight(self):
        """Generate and display a tech insight"""
        print("\n💡 Tech Insight Generator")
        print("-" * 30)

        print("🤖 Generating tech insight using AI Foundry Agent...")
        result = await self.ai_generator.generate_tech_insight()

        if result["success"]:
            print(
                f"\n✅ Generated Tech Insight ({result['character_count']} characters):"
            )
            print(f"📱 {result['content']}")
            print(f"🤖 Model: {result['model']}")

            # Ask if user wants to post it
            post_now = input("\n📤 Post this to X now? (y/n): ").strip().lower()
            if post_now == "y":
                await self.post_tweet(result["content"])
        else:
            print(f"\n❌ Generation failed: {result['error']}")
            print(f"📱 Fallback content: {result['content']}")

    async def generate_custom_tweet(self):
        """Generate custom tweet based on user input"""
        print("\n✍️ Custom Tweet Generator")
        print("-" * 30)

        user_request = input("What kind of tweet would you like? ").strip()
        if not user_request:
            print("❌ Please enter a request")
            return

        print("\n🤖 Generating custom tweet using AI Foundry Agent...")
        result = await self.ai_generator.generate_custom_tweet(user_request)

        if result.get("success"):
            print(
                f"\n✅ Generated Tweet ({result.get('character_count', 0)} characters):"
            )
            print(f"📱 {result.get('content')}")
            print(f"🤖 Model: {result.get('model')}")

            post_now = input("\n📤 Post this to X now? (y/n): ").strip().lower()
            if post_now == "y":
                await self.post_tweet(result.get("content"))
        else:
            print(f"\n❌ Generation failed: {result.get('error')}")
            if result.get("content"):
                print(f"📱 Fallback content: {result.get('content')}")

    async def generate_and_post_ai_tip(self):
        """Generate and immediately post an AI tip"""
        print("\n🚀 Generate & Post AI Tip")
        print("-" * 30)

        print("🤖 Generating AI tip using AI Foundry Agent...")
        result = await self.ai_generator.generate_ai_tip()

        if result.get("success"):
            print(
                f"\n✅ Generated AI Tip ({result.get('character_count', 0)} characters):"
            )
            print(f"📱 {result.get('content')}")

            await self.post_tweet(result.get("content"))
        else:
            print(f"\n❌ Generation failed: {result.get('error')}")
            print("Not posting fallback content automatically.")

    async def generate_and_post_tech_insight(self):
        """Generate and immediately post a tech insight"""
        print("\n🎯 Generate & Post Tech Insight")
        print("-" * 30)

        print("🤖 Generating tech insight using AI Foundry Agent...")
        result = await self.ai_generator.generate_tech_insight()

        if result.get("success"):
            print(
                f"\n✅ Generated Tech Insight ({result.get('character_count', 0)} characters):"
            )
            print(f"📱 {result.get('content')}")

            await self.post_tweet(result.get("content"))
        else:
            print(f"\n❌ Generation failed: {result.get('error')}")
            print("Not posting fallback content automatically.")

    async def post_tweet(self, content: str):
        """Post content to X"""
        print("\n📤 Posting to X...")

        confirm = input("Final confirmation - post this tweet? (y/n): ").strip().lower()
        if confirm != "y":
            print("❌ Tweet cancelled")
            return

        result = self.x_handler.post_text(content)

        if result.get("success"):
            print("✅ Tweet posted successfully!")
            if result.get("tweet_id"):
                print(f"🔗 Tweet ID: {result['tweet_id']}")
                print(
                    f"🌐 View at: https://twitter.com/i/web/status/{result['tweet_id']}"
                )
        else:
            print(f"❌ Tweet posting failed: {result.get('error', 'Unknown error')}")

    def view_account_status(self):
        """View X account status"""
        print("\n📊 X Account Status")
        print("-" * 25)

        user_info = self.x_handler.get_user_info()

        if user_info:
            print(f"👤 Username: @{user_info.get('username', 'Unknown')}")
            print(f"📊 Followers: {user_info.get('followers_count', 'Unknown'):,}")
            print(f"📝 Tweets: {user_info.get('tweet_count', 'Unknown'):,}")
            print("✅ Connection Status: Active")
        else:
            print("❌ Could not retrieve account information")
            print("💡 Check your X API credentials")

    async def main(self):
        """Main UI loop"""
        print("🚀 Starting AI Tweet Generator with AI Foundry Agent...")

        while True:
            try:
                self.display_main_menu()
                choice = input("\n👆 Select an option (0-7): ").strip()

                if choice == "0":
                    print("👋 Returning to main menu...")
                    break
                elif choice == "1":
                    await self.post_manual_tweet()
                elif choice == "2":
                    await self.generate_and_show_ai_tip()
                elif choice == "3":
                    await self.generate_and_show_tech_insight()
                elif choice == "4":
                    await self.generate_custom_tweet()
                elif choice == "5":
                    await self.generate_and_post_ai_tip()
                elif choice == "6":
                    await self.generate_and_post_tech_insight()
                elif choice == "7":
                    self.view_account_status()
                else:
                    print("❌ Invalid choice. Please select 0-7.")

                # Pause between operations
                if choice != "0":
                    input("\n🔄 Press Enter to continue...")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print("💡 Try selecting a different option")


def main():
    """Entry point"""
    app = AITweetGenerator()
    asyncio.run(app.main())


if __name__ == "__main__":
    main()

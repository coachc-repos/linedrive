#!/usr/bin/env python3
"""
Quick X posting interface - direct launch
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from social_media.platforms.x_platform import XPlatformHandler

def main():
    print("🐦 QUICK X POSTING TOOL")
    print("=" * 40)
    
    # Initialize handler
    handler = XPlatformHandler()
    
    # Test connection
    if not handler.test_connection():
        print("❌ Cannot connect to X API. Please check credentials.")
        return
    
    # Get user info
    user_info = handler.get_user_info()
    if user_info.get('success'):
        print(f"�� Connected as: @{user_info['username']} ({user_info['name']})")
        print(f"👥 Followers: {user_info.get('followers_count', 0):,}")
    
    print("\n📝 Enter your tweet (or 'quit' to exit):")
    
    try:
        tweet_text = input("Tweet: ").strip()
        
        if tweet_text.lower() == 'quit':
            print("👋 Goodbye!")
            return
        
        if not tweet_text:
            print("❌ Tweet cannot be empty.")
            return
        
        # Check length
        if len(tweet_text) > 280:
            print(f"❌ Tweet too long ({len(tweet_text)}/280 characters)")
            return
        
        print(f"\n📊 Length: {len(tweet_text)}/280 characters")
        print(f"📋 Preview: {tweet_text}")
        
        confirm = input("\n🤔 Post this tweet? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ Tweet cancelled.")
            return
        
        print("\n📤 Posting...")
        result = handler.post_text(tweet_text)
        
        if result.get('success'):
            print("🎉 Tweet posted successfully!")
            if result.get('url'):
                print(f"🔗 URL: {result['url']}")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")

if __name__ == "__main__":
    main()

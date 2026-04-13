#!/usr/bin/env python3
"""
Verification script - Check that all social media components are working
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(
    __file__
).parent.parent.parent  # Go up three levels to reach project root
sys.path.insert(0, str(project_root))


def check_file_structure():
    """Check that all required files exist"""
    print("�� CHECKING FILE STRUCTURE...")

    required_files = [
        "social_media/__init__.py",
        "social_media/config/__init__.py",
        "social_media/config/x_config.py",
        "social_media/platforms/__init__.py",
        "social_media/platforms/x_platform.py",
        "console_ui/social_media/x_posting_ui.py",
        "console_ui/social_media/social_media_ui.py",
        "console_ui/social_media/quick_tweet_ui.py",
        "social_media/platforms/setup_x_credentials.py",
    ]

    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"   ✅ {file_path}")

    if missing_files:
        print("\n❌ Missing files:")
        for file_path in missing_files:
            print(f"   ❌ {file_path}")
        return False
    else:
        print("   ✅ All files present!")
        return True


def check_imports():
    """Check that all modules can be imported"""
    print("\n🐍 CHECKING PYTHON IMPORTS...")

    try:
        from social_media.config.x_config import XConfig

        print("   ✅ social_media.config.x_config")
    except Exception as e:
        print(f"   ❌ social_media.config.x_config: {e}")
        return False

    try:
        from social_media.platforms.x_platform import XPlatformHandler

        print("   ✅ social_media.platforms.x_platform")
    except Exception as e:
        print(f"   ❌ social_media.platforms.x_platform: {e}")
        return False

    try:
        from console_ui.social_media.x_posting_ui import XPostingUI

        print("   ✅ console_ui.social_media.x_posting_ui")
    except Exception as e:
        print(f"   ❌ console_ui.social_media.x_posting_ui: {e}")
        return False

    print("   ✅ All imports successful!")
    return True


def check_credentials():
    """Check that credentials are properly configured"""
    print("\n🔐 CHECKING X API CREDENTIALS...")

    try:
        from social_media.config.x_config import XConfig

        config = XConfig()

        # Use the proper method to check credentials
        if config.has_credentials() and config.test_credentials():
            print("   ✅ All X API credentials found and valid")
            return True
        else:
            print("   ❌ Missing or invalid X API credentials")
            print("   💡 Run: python3 social_media/platforms/setup_x_credentials.py")
            return False
    except Exception as e:
        print(f"   ❌ Error loading X credentials: {e}")
        print("   💡 Run: python3 social_media/platforms/setup_x_credentials.py")
        return False


def check_api_connection():
    """Test actual API connection"""
    print("\n🌐 TESTING X API CONNECTION...")

    try:
        from social_media.platforms.x_platform import XPlatformHandler

        x_handler = XPlatformHandler()

        # Test connection by getting user info
        user_info = x_handler.get_user_info()
        if user_info:
            print(f"   ✅ Connected to X as: @{user_info.get('username', 'Unknown')}")
            print(f"   📊 Followers: {user_info.get('followers_count', 'Unknown')}")
            return True
        else:
            print("   ❌ Failed to connect to X API")
            return False
    except Exception as e:
        print(f"   ❌ X API connection failed: {e}")
        print("   💡 Check your credentials and internet connection")
        return False


def main():
    """Run all verification checks"""
    print("🔍 LINEDRIVE SOCIAL MEDIA VERIFICATION")
    print("=" * 60)

    # Run all checks
    file_check = check_file_structure()
    import_check = check_imports() if file_check else False
    cred_check = check_credentials() if import_check else False
    api_check = check_api_connection() if cred_check else False

    # Summary
    print("\n📊 VERIFICATION RESULTS")
    print("=" * 30)
    print(f"File Structure: {'✅' if file_check else '❌'}")
    print(f"Python Imports: {'✅' if import_check else '❌'}")
    print(f"Credentials: {'✅' if cred_check else '❌'}")
    print(f"API Connection: {'✅' if api_check else '❌'}")

    if all([file_check, import_check, cred_check, api_check]):
        print("\n🎉 ALL SYSTEMS GO! Your social media tools are ready!")
        print("\n🚀 To get started:")
        print("   • Quick tweet: python3 console_ui/quick_tweet_ui.py")
        print("   • Full interface: python3 console_ui/social_media_ui.py")
    else:
        print("\n⚠️  Some issues found. Please fix them before using the tools.")


if __name__ == "__main__":
    main()

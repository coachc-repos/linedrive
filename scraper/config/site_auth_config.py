#!/usr/bin/env python3
"""
Site Authentication Configuration
Manages login credentials for scraping sites that require authentication
"""

import os
from typing import Dict, Optional, List
from pathlib import Path
import json
import getpass


class SiteAuthConfig:
    """Site authentication configuration manager"""

    def __init__(self):
        self.config_dir = Path(__file__).parent
        self.credentials_file = self.config_dir / ".site_credentials.json"

    def save_site_credentials(
        self, site_name: str, credentials: Dict[str, str]
    ) -> bool:
        """
        Save site credentials to secure config file

        Args:
            site_name: Name of the site (e.g., 'perfectgame', 'gamechanger')
            credentials: Dictionary of credentials (username, password, etc.)

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Load existing credentials
            all_credentials = {}
            if self.credentials_file.exists():
                with open(self.credentials_file, "r", encoding="utf-8") as f:
                    all_credentials = json.load(f)

            # Add/update site credentials
            all_credentials[site_name] = credentials

            # Save back to file
            with open(self.credentials_file, "w", encoding="utf-8") as f:
                json.dump(all_credentials, f, indent=2)

            # Set secure file permissions
            os.chmod(self.credentials_file, 0o600)
            print(f"✅ Credentials saved for {site_name}: {self.credentials_file}")
            return True
        except Exception as e:
            print(f"❌ Error saving credentials for {site_name}: {e}")
            return False

    def has_site_credentials(self, site_name: str) -> bool:
        """Check if credentials exist for a specific site"""
        try:
            if not self.credentials_file.exists():
                return False

            with open(self.credentials_file, "r", encoding="utf-8") as f:
                all_credentials = json.load(f)

            return site_name in all_credentials and all_credentials[site_name]
        except Exception:
            return False

    def get_site_credentials(self, site_name: str) -> Dict[str, str]:
        """
        Get credentials for a specific site

        Args:
            site_name: Name of the site

        Returns:
            Dictionary of credentials

        Raises:
            ValueError: If credentials not found
        """
        try:
            if not self.credentials_file.exists():
                raise ValueError(f"No credentials file found")

            with open(self.credentials_file, "r", encoding="utf-8") as f:
                all_credentials = json.load(f)

            if site_name not in all_credentials:
                raise ValueError(f"No credentials found for site: {site_name}")

            return all_credentials[site_name]
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid credentials file format: {e}")

    def list_configured_sites(self) -> List[str]:
        """Get list of sites with configured credentials"""
        try:
            if not self.credentials_file.exists():
                return []

            with open(self.credentials_file, "r", encoding="utf-8") as f:
                all_credentials = json.load(f)

            return list(all_credentials.keys())
        except Exception:
            return []

    def remove_site_credentials(self, site_name: str) -> bool:
        """Remove credentials for a specific site"""
        try:
            if not self.credentials_file.exists():
                return False

            with open(self.credentials_file, "r", encoding="utf-8") as f:
                all_credentials = json.load(f)

            if site_name in all_credentials:
                del all_credentials[site_name]

                with open(self.credentials_file, "w", encoding="utf-8") as f:
                    json.dump(all_credentials, f, indent=2)

                print(f"✅ Removed credentials for {site_name}")
                return True
            else:
                print(f"❌ No credentials found for {site_name}")
                return False
        except Exception as e:
            print(f"❌ Error removing credentials for {site_name}: {e}")
            return False

    def test_site_credentials(self, site_name: str) -> bool:
        """Test if credentials exist and have required fields"""
        try:
            credentials = self.get_site_credentials(site_name)

            # Check for required fields
            required_fields = ["username", "password"]
            return all(
                field in credentials
                and credentials[field]
                and len(credentials[field].strip()) > 0
                for field in required_fields
            )
        except Exception:
            return False

    def interactive_setup(self, site_name: str) -> bool:
        """Interactive setup for site credentials"""
        print(f"\n🔐 Setting up credentials for {site_name.upper()}")
        print("=" * 50)

        try:
            username = input("Username: ").strip()
            if not username:
                print("❌ Username cannot be empty")
                return False

            password = getpass.getpass("Password: ").strip()
            if not password:
                print("❌ Password cannot be empty")
                return False

            # Optional fields
            email = input("Email (optional): ").strip()
            notes = input("Notes (optional): ").strip()

            credentials = {"username": username, "password": password}

            if email:
                credentials["email"] = email
            if notes:
                credentials["notes"] = notes

            # Save credentials
            if self.save_site_credentials(site_name, credentials):
                print(f"✅ Credentials saved successfully for {site_name}!")
                return True
            else:
                print(f"❌ Failed to save credentials for {site_name}")
                return False

        except KeyboardInterrupt:
            print("\n❌ Setup cancelled by user")
            return False
        except Exception as e:
            print(f"❌ Error during setup: {e}")
            return False


# Site-specific configurations
SUPPORTED_SITES = {
    "perfectgame": {
        "name": "Perfect Game",
        "login_url": "https://www.perfectgame.org/Login",
        "username_selector": 'input[name="username"]',
        "password_selector": 'input[name="password"]',
        "login_button_selector": 'button[type="submit"]',
        "success_indicator": ".user-menu",
        "requires_2fa": False,
    },
    "gamechanger": {
        "name": "GameChanger",
        "login_url": "https://gc.com/login",
        "username_selector": 'input[name="email"]',
        "password_selector": 'input[name="password"]',
        "login_button_selector": 'button[type="submit"]',
        "success_indicator": ".profile-dropdown",
        "requires_2fa": True,
    },
    "usabaseball": {
        "name": "USA Baseball",
        "login_url": "https://www.usabaseball.com/login",
        "username_selector": 'input[name="username"]',
        "password_selector": 'input[name="password"]',
        "login_button_selector": ".login-button",
        "success_indicator": ".user-profile",
        "requires_2fa": False,
    },
}


def get_site_config(site_name: str) -> Optional[Dict]:
    """Get configuration for a specific site"""
    return SUPPORTED_SITES.get(site_name.lower())


def list_supported_sites() -> List[str]:
    """Get list of supported sites for authentication"""
    return list(SUPPORTED_SITES.keys())

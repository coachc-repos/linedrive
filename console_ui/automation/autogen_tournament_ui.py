#!/usr/bin/env python3
"""
AutoGen Tournament Test UI - Interactive Terminal Interface for 3-Agent System

This provides a user-friendly terminal interface to test the 3-agent AutoGen
tournament search system with customizable filters.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from linedrive_azure.agents.agent_framework import TournamentAutoGenSystem


class AutoGenTournamentUI:
    """Interactive terminal UI for testing the 3-agent AutoGen tournament system"""

    def __init__(self):
        self.system = TournamentAutoGenSystem()

        # Default search filters
        self.filters = {
            "age_group": "10U",
            "location": "Houston, TX",
            "time_range": "This month (August 2025)",
            "event_type": "Baseball",
            "bracket": "Perfect Game",
            "additional_notes": "",
        }

        # Available options for quick selection
        self.age_groups = [
            "8U",
            "9U",
            "10U",
            "11U",
            "12U",
            "13U",
            "14U",
            "15U",
            "16U",
            "17U",
            "18U",
        ]
        self.event_types = ["Baseball", "Softball", "Both"]
        self.brackets = [
            "Perfect Game",
            "USSSA",
            "Travel Ball",
            "Recreation",
            "All Star",
            "Any",
        ]
        self.time_ranges = [
            "This week",
            "This month (August 2025)",
            "Next month (September 2025)",
            "This weekend",
            "Next weekend",
            "Next 30 days",
            "Summer 2025",
        ]

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system("clear" if os.name == "posix" else "cls")

    def print_header(self):
        """Print the application header"""
        print("🤖" + "=" * 78 + "🤖")
        print("🤖" + " " * 25 + "AUTOGEN TOURNAMENT TEST UI" + " " * 25 + "🤖")
        print("🤖" + " " * 20 + "3-Agent AutoGen Tournament System" + " " * 20 + "🤖")
        print(
            "🤖"
            + " " * 15
            + "TournamentFinder → TournamentPlanner → TournamentAdvisor"
            + " " * 15
            + "🤖"
        )
        print("🤖" + "=" * 78 + "🤖")
        print()

    def print_current_filters(self):
        """Display current search filters"""
        print("📝 Current Search Filters:")
        print("━" * 50)
        print(f"🎯 Age Group:    {self.filters['age_group']}")
        print(f"📍 Location:     {self.filters['location']}")
        print(f"📅 Time Range:   {self.filters['time_range']}")
        print(f"⚾ Event Type:   {self.filters['event_type']}")
        print(f"🏆 Bracket:      {self.filters['bracket']}")
        if self.filters["additional_notes"]:
            print(f"📝 Notes:        {self.filters['additional_notes']}")
        print("━" * 50)
        print()

    def print_menu(self):
        """Display the main menu"""
        print("🎮 Menu Options:")
        print("━" * 30)
        print("1️⃣  Change Age Group")
        print("2️⃣  Change Location")
        print("3️⃣  Change Time Range")
        print("4️⃣  Change Event Type")
        print("5️⃣  Change Bracket")
        print("6️⃣  Add/Edit Notes")
        print("7️⃣  Reset to Defaults")
        print("8️⃣  Run AutoGen Tournament Search")
        print("9️⃣  Quick Test (Default Settings)")
        print("0️⃣  Exit")
        print("━" * 30)
        print()

    def select_from_list(
        self, title: str, options: List[str], current_value: str = ""
    ) -> Optional[str]:
        """Helper to select from a list of options"""
        print(f"\n📋 {title}")
        print("━" * 40)

        for i, option in enumerate(options, 1):
            marker = "✅" if option == current_value else "  "
            print(f"{marker} {i:2}. {option}")

        print(f"   0. Custom (enter your own)")
        print(f"   x. Cancel")
        print("━" * 40)

        while True:
            choice = input("Select option: ").strip().lower()

            if choice == "x":
                return None
            elif choice == "0":
                custom = input("Enter custom value: ").strip()
                return custom if custom else None
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(options):
                        return options[idx]
                except ValueError:
                    pass
                print("❌ Invalid choice. Try again.")

    def edit_age_group(self):
        """Edit age group filter"""
        result = self.select_from_list(
            "Select Age Group", self.age_groups, self.filters["age_group"]
        )
        if result:
            self.filters["age_group"] = result
            print(f"✅ Age group updated to: {result}")

    def edit_location(self):
        """Edit location filter"""
        print("\n📍 Enter Location:")
        print("Examples: Houston, TX | Dallas, TX | Austin, TX | San Antonio, TX")
        location = input("Location: ").strip()
        if location:
            self.filters["location"] = location
            print(f"✅ Location updated to: {location}")

    def edit_time_range(self):
        """Edit time range filter"""
        result = self.select_from_list(
            "Select Time Range", self.time_ranges, self.filters["time_range"]
        )
        if result:
            self.filters["time_range"] = result
            print(f"✅ Time range updated to: {result}")

    def edit_event_type(self):
        """Edit event type filter"""
        result = self.select_from_list(
            "Select Event Type", self.event_types, self.filters["event_type"]
        )
        if result:
            self.filters["event_type"] = result
            print(f"✅ Event type updated to: {result}")

    def edit_bracket(self):
        """Edit bracket filter"""
        result = self.select_from_list(
            "Select Bracket", self.brackets, self.filters["bracket"]
        )
        if result:
            self.filters["bracket"] = result
            print(f"✅ Bracket updated to: {result}")

    def edit_notes(self):
        """Edit additional notes"""
        print("\n📝 Additional Notes/Requirements:")
        print("(e.g., 'Looking for wood bat only', 'Need weekend tournaments', etc.)")
        notes = input("Notes: ").strip()
        self.filters["additional_notes"] = notes
        print(f"✅ Notes updated: {notes if notes else '(cleared)'}")

    def reset_filters(self):
        """Reset filters to defaults"""
        self.filters = {
            "age_group": "10U",
            "location": "Houston, TX",
            "time_range": "This month (August 2025)",
            "event_type": "Baseball",
            "bracket": "Perfect Game",
            "additional_notes": "",
        }
        print("✅ Filters reset to defaults")

    def build_query(self) -> str:
        """Build the query string from current filters"""
        query_parts = [
            "I need help finding baseball tournaments. Here are my search criteria:"
        ]

        query_parts.append(f"- Age group: {self.filters['age_group']}")
        query_parts.append(f"- Location: {self.filters['location']}")
        query_parts.append(f"- Time range: {self.filters['time_range']}")
        query_parts.append(f"- Event type: {self.filters['event_type']}")
        query_parts.append(f"- Bracket: {self.filters['bracket']}")

        if self.filters["additional_notes"]:
            query_parts.append(
                f"- Additional requirements: {self.filters['additional_notes']}"
            )

        query_parts.append("")
        query_parts.append(
            "Please help me find tournaments and provide planning advice."
        )

        return "\n".join(query_parts)

    async def run_tournament_search(self, quick_test: bool = False):
        """Run the 3-agent tournament search"""
        query = self.build_query()

        if quick_test:
            print("⚡ QUICK TEST MODE - Using Default Settings")
        else:
            print("🚀 RUNNING 3-AGENT AUTOGEN TOURNAMENT SEARCH")

        print("=" * 80)
        print("📝 Search Query:")
        print("-" * 40)
        print(query)
        print("=" * 80)

        start_time = datetime.now()
        print(f"⏰ Started at: {start_time.strftime('%H:%M:%S')}")
        print(
            "🤖 Agents: TournamentFinder (LineDrive) → TournamentPlanner (Grok) → TournamentAdvisor (Grok)"
        )
        print()

        try:
            response = await self.system.run_tournament_workflow(query)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            print("\n" + "=" * 80)
            print("✅ AUTOGEN SEARCH COMPLETED")
            print(f"⏱️  Duration: {duration:.2f} seconds")
            print(f"🕐 Completed at: {end_time.strftime('%H:%M:%S')}")
            print("=" * 80)
            print()
            print("📊 TOURNAMENT SEARCH RESULTS:")
            print("━" * 80)
            print(response)
            print("━" * 80)

            return True

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            print("\n" + "=" * 80)
            print("❌ AUTOGEN SEARCH FAILED")
            print(f"⏱️  Duration: {duration:.2f} seconds")
            print(f"🕐 Failed at: {end_time.strftime('%H:%M:%S')}")
            print(f"🔍 Error: {e}")
            print("=" * 80)

            return False

    async def main_loop(self):
        """Main application loop"""
        while True:
            self.clear_screen()
            self.print_header()
            self.print_current_filters()
            self.print_menu()

            choice = input("Enter your choice: ").strip()

            if choice == "1":
                self.edit_age_group()
            elif choice == "2":
                self.edit_location()
            elif choice == "3":
                self.edit_time_range()
            elif choice == "4":
                self.edit_event_type()
            elif choice == "5":
                self.edit_bracket()
            elif choice == "6":
                self.edit_notes()
            elif choice == "7":
                self.reset_filters()
            elif choice == "8":
                await self.run_tournament_search(quick_test=False)
            elif choice == "9":
                self.reset_filters()
                await self.run_tournament_search(quick_test=True)
            elif choice == "0":
                print("\n👋 Thanks for using AutoGen Tournament Test UI!")
                break
            else:
                print("❌ Invalid choice. Please try again.")

            if choice in ["1", "2", "3", "4", "5", "6", "7"]:
                input("\nPress Enter to continue...")
            elif choice in ["8", "9"]:
                print("\n" + "=" * 80)
                input("Press Enter to return to menu...")


async def main():
    """Main entry point"""
    try:
        ui = AutoGenTournamentUI()
        await ui.main_loop()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Application error: {e}")


if __name__ == "__main__":
    print("🚀 Starting AutoGen Tournament Test UI...")
    asyncio.run(main())

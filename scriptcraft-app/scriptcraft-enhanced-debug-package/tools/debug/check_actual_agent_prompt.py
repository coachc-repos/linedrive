#!/usr/bin/env python3
"""
Check the actual current prompt configured for the Review Agent in Azure
"""

import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Load environment
load_dotenv("/Users/christhi/Dev/Github/linedrive/linedrive_azure/agents/.env")

# Configuration
project_connection_string = os.getenv("AIPROJECT_CONNECTION_STRING")
review_agent_id = "asst_MeeUTGVUBItaslmikiJ1qhd9"


def check_agent_prompt():
    """Check the actual current agent configuration"""
    try:
        print("🔍 Connecting to Azure AI Foundry...")
        project_client = AIProjectClient(
            credential=DefaultAzureCredential(),
            api_key=os.getenv("AI_PROJECT_API_KEY"),
            endpoint="https://linedrive-ai-foundry.services.ai.azure.com/api/projects/linedriveAgents",
        )

        print(f"📋 Retrieving agent configuration for: {review_agent_id}")
        agent = project_client.agents.get_agent(review_agent_id)

        print(f"\n✅ Agent Found: {agent.name}")
        print(f"   Model: {agent.model}")
        print(f"   Created: {agent.created_at}")

        print(f"\n📝 CURRENT INSTRUCTIONS (first 500 chars):")
        print("="*80)
        instructions = agent.instructions or "No instructions set"
        print(instructions[:500])
        print("="*80)

        print(f"\n📏 Full instructions length: {len(instructions)} characters")

        # Check for problematic phrases
        print(f"\n🔍 Checking for interactive phrases:")
        problematic_phrases = [
            "what would you like",
            "tell me",
            "drop the script",
            "which script",
            "what kind of review"
        ]

        for phrase in problematic_phrases:
            if phrase.lower() in instructions.lower():
                print(f"   ⚠️  Found: '{phrase}'")
            else:
                print(f"   ✅ Not found: '{phrase}'")

        # Check for direct processing indicators
        print(f"\n✅ Checking for direct-processing indicators:")
        good_phrases = [
            "when you receive a script",
            "automatically",
            "directly process",
            "immediately review"
        ]

        for phrase in good_phrases:
            if phrase.lower() in instructions.lower():
                print(f"   ✅ Found: '{phrase}'")
            else:
                print(f"   ⚠️  Not found: '{phrase}'")

        print(f"\n💾 Saving full instructions to file...")
        with open("/tmp/review_agent_current_prompt.txt", "w") as f:
            f.write(instructions)
        print(f"   Saved to: /tmp/review_agent_current_prompt.txt")

        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("="*80)
    print("Review Agent Prompt Checker")
    print("="*80)
    check_agent_prompt()

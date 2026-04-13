#!/usr/bin/env python3
"""
Check Agent Tools Configuration
================================
Verifies what tools are actually configured on each agent.
This helps diagnose tool-related issues with GPT-5-mini.
"""

from dotenv import load_dotenv
from linedrive_azure.agents.script_review_agent_client import (
    ScriptReviewAgentClient
)
from linedrive_azure.agents.script_writer_agent_client import (
    ScriptWriterAgentClient
)
from linedrive_azure.agents.script_topic_assistant_agent_client import (
    ScriptTopicAssistantAgentClient
)
import sys
import os

# Add project root to path
project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)
sys.path.insert(0, project_root)


# Load environment variables
env_path = os.path.join(project_root, "linedrive_azure", "agents", ".env")
load_dotenv(env_path)


def check_agent_tools(client, name):
    """Check what tools an agent has configured."""
    print(f"\n{'=' * 60}")
    print(f"🔍 {name}")
    print(f"{'=' * 60}")
    print(f"Agent ID: {client.agent.id}")
    print(f"Model: {client.agent.model}")

    # Check tools
    if hasattr(client.agent, 'tools') and client.agent.tools:
        print(f"\n⚠️  TOOLS CONFIGURED ({len(client.agent.tools)}):")
        for i, tool in enumerate(client.agent.tools, 1):
            if hasattr(tool, 'type'):
                print(f"   {i}. {tool.type}")
            else:
                print(f"   {i}. {tool}")

        # Check for problematic tools
        tool_types = [
            getattr(t, 'type', str(t)) for t in client.agent.tools
        ]
        problematic = []
        if 'azure_ai_search' in tool_types:
            problematic.append('azure_ai_search')
        if 'bing_grounding' in tool_types:
            problematic.append('bing_grounding')

        if problematic:
            print(f"\n   ❌ INCOMPATIBLE WITH GPT-5-mini: {problematic}")
            print(f"   ⚠️  These tools will cause the agent to hang!")
        else:
            print(f"\n   ✅ No known incompatible tools")
    else:
        print(f"\n✅ NO TOOLS CONFIGURED (Safe for GPT-5-mini)")


def main():
    print("\n" + "=" * 60)
    print("🔧 AGENT TOOLS CONFIGURATION CHECK")
    print("=" * 60)
    print("\nChecking what tools are configured on each agent...")
    print("This helps diagnose GPT-5-mini compatibility issues.")

    try:
        # Check Topic Enhancement Agent
        topic_client = ScriptTopicAssistantAgentClient()
        check_agent_tools(topic_client, "Script Topic Enhancement Agent")

        # Check Script Writer Agent
        writer_client = ScriptWriterAgentClient()
        check_agent_tools(writer_client, "Script Writer Agent")

        # Check Script Review Agent
        review_client = ScriptReviewAgentClient()
        check_agent_tools(review_client, "Script Review Agent")

        print("\n" + "=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)
        print("""
If any agent shows 'azure_ai_search' or 'bing_grounding':
1. Go to https://ai.azure.com
2. Navigate to your project → Agents
3. Open each agent
4. Remove the incompatible tools
5. Save changes

GPT-5-mini only supports:
- code_interpreter
- file_search
- function (custom functions)

NOT supported:
- azure_ai_search (use Python code instead)
- bing_grounding (use Python code instead)
""")

    except Exception as e:
        print(f"\n❌ Error checking agents: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

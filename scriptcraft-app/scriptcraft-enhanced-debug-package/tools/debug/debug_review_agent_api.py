#!/usr/bin/env python3
"""
Debug Review Agent API Response
================================
Captures the raw HTTP response to see what's actually being returned.
"""

import logging
from dotenv import load_dotenv
from linedrive_azure.agents.script_review_agent_client import (
    ScriptReviewAgentClient
)
import sys
import os

# Add project root to path
project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)
sys.path.insert(0, project_root)


# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables
env_path = os.path.join(project_root, "linedrive_azure", "agents", ".env")
load_dotenv(env_path)


def main():
    print("\n" + "=" * 70)
    print("🔬 REVIEW AGENT RAW API DEBUG")
    print("=" * 70)

    try:
        # Initialize client
        print("\n1. Initializing Review Agent...")
        client = ScriptReviewAgentClient()
        print(f"   Agent ID: {client.agent.id}")
        print(f"   Model: {client.agent.model}")

        # Get agent details to see if prompt updated
        print("\n2. Fetching agent configuration...")
        agent = client.agent

        print(f"   Name: {agent.name if hasattr(agent, 'name') else 'N/A'}")
        print(f"   Model: {agent.model}")
        print(
            f"   Created: {agent.created_at if hasattr(agent, 'created_at') else 'N/A'}")

        # Check if we can see the instructions/prompt
        if hasattr(agent, 'instructions') and agent.instructions:
            instructions = agent.instructions
            print(f"\n   System Prompt Preview (first 200 chars):")
            print(f"   {'-' * 66}")
            preview = instructions[:200].replace("\n", "\n   ")
            print(f"   {preview}")
            if len(instructions) > 200:
                print(f"   ... [{len(instructions)} total chars]")
            print(f"   {'-' * 66}")

            # Check for key phrases
            if "Tell me which" in instructions or "Drop the script" in instructions:
                print("\n   ⚠️  OLD PROMPT DETECTED!")
                print("   The agent still has the interactive prompt.")
                print("   Prompt update may not have propagated yet.")
            elif "When you receive a script review request" in instructions:
                print("\n   ✅ NEW PROMPT DETECTED!")
                print("   The agent has the updated direct-processing prompt.")
            else:
                print("\n   ❓ Unknown prompt format")
        else:
            print("\n   ⚠️  Cannot access agent instructions")

        # Try to create a thread
        print("\n3. Testing thread creation...")
        try:
            thread_result = client.project.agents.threads.create()
            thread_id = thread_result.id
            print(f"   ✅ Thread created: {thread_id}")

            # Try to create a simple message
            print("\n4. Testing message creation...")
            try:
                message = client.project.agents.messages.create(
                    thread_id=thread_id,
                    role="user",
                    content="Hello, can you help me?"
                )
                print(f"   ✅ Message created: {message.id}")
                print("\n✅ API is working - thread and message creation successful")

            except Exception as msg_error:
                print(f"\n   ❌ Message creation failed:")
                print(f"      Error type: {type(msg_error).__name__}")
                print(f"      Error: {msg_error}")

                # This is the actual problem
                print("\n   🔍 This is where it's failing!")
                print("      The agent configuration might be corrupted.")
                print("      Try recreating the agent in Azure AI Foundry.")

        except Exception as thread_error:
            print(f"   ❌ Thread creation failed: {thread_error}")

    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
ScriptCraft Diagnostics Script
Run this to check Azure authentication and agent connectivity
"""

import os
import sys
from pathlib import Path


def check_environment():
    """Check environment variables"""
    print("🔍 Environment Variables:")
    api_key = os.environ.get("AI_PROJECT_API_KEY")
    if api_key:
        print(f"  ✅ AI_PROJECT_API_KEY: {api_key[:10]}...{api_key[-10:]}")
    else:
        print("  ❌ AI_PROJECT_API_KEY: Not found")

    print(f"  📁 PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    print()


def check_azure_packages():
    """Check if Azure packages are available"""
    print("📦 Azure Package Check:")
    try:
        from azure.ai.projects import AIProjectClient

        print("  ✅ azure-ai-projects: Available")
    except ImportError as e:
        print(f"  ❌ azure-ai-projects: {e}")

    try:
        from azure.identity import DefaultAzureCredential

        print("  ✅ azure-identity: Available")
    except ImportError as e:
        print(f"  ❌ azure-identity: {e}")

    try:
        from azure.core.credentials import AzureKeyCredential

        print("  ✅ azure-core: Available")
    except ImportError as e:
        print(f"  ❌ azure-core: {e}")
    print()


def test_azure_connection():
    """Test Azure AI Foundry connection"""
    print("🔗 Azure AI Connection Test:")
    try:
        from azure.ai.projects import AIProjectClient
        from azure.identity import DefaultAzureCredential
        from azure.core.credentials import AzureKeyCredential

        # Try API key first
        api_key = os.environ.get("AI_PROJECT_API_KEY")
        if api_key:
            print("  🔑 Using API key authentication")
            credential = AzureKeyCredential(api_key)
        else:
            print("  🔑 Using DefaultAzureCredential")
            credential = DefaultAzureCredential()

        project = AIProjectClient(
            credential=credential,
            endpoint="https://linedrive-ai-foundry.services.ai.azure.com/api/projects/linedriveAgents",
        )

        print("  ✅ Project client created successfully")

        # Try to list agents
        agents = list(project.agents.list_agents())
        print(f"  ✅ Found {len(agents)} agents")

        if agents:
            agent = agents[0]
            print(f"  📝 First agent: {agent.id}")
            print(f"     Name: {getattr(agent, 'name', 'Unknown')}")

        return True

    except Exception as e:
        print(f"  ❌ Connection failed: {e}")
        return False


def test_agent_interaction():
    """Test creating a thread and sending a message"""
    print("🤖 Agent Interaction Test:")
    try:
        from linedrive_azure.agents.script_writer_agent_client import (
            ScriptWriterAgentClient,
        )

        # Use the known agent ID
        agent_id = "asst_AaDCevqoB0tpjyKNqzLR0Wxx"
        client = ScriptWriterAgentClient(agent_id)

        print(f"  ✅ Agent client created: {client.agent_name}")

        # Create a thread
        thread = client.create_thread()
        print(f"  ✅ Thread created: {thread.id}")

        # Send a simple test message
        result = client.send_message(
            thread_id=thread.id,
            message_content="Write a 30-second script about coffee.",
            timeout=60,
        )

        if result["success"]:
            print("  ✅ Message sent and response received")
            print(f"     Response length: {len(result['response'])} characters")
        else:
            print(f"  ❌ Message failed: {result['error']}")

        return result["success"]

    except Exception as e:
        print(f"  ❌ Agent test failed: {e}")
        return False


def main():
    """Run all diagnostics"""
    print("🏥 ScriptCraft Diagnostics")
    print("=" * 50)

    # Add current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))

    check_environment()
    check_azure_packages()

    connection_ok = test_azure_connection()
    if connection_ok:
        test_agent_interaction()

    print("=" * 50)
    print("🏁 Diagnostics complete")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import os

os.environ["AI_PROJECT_API_KEY"] = "c1edf7ed70c84b049de84fc7bfc4bf42"

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

print("Testing agent listing...")
try:
    credential = DefaultAzureCredential()
    project = AIProjectClient(
        credential=credential,
        api_key=os.environ["AI_PROJECT_API_KEY"],
        endpoint="https://linedrive-ai-foundry.services.ai.azure.com/api/projects/linedriveAgents",
    )

    print("Listing all agents...")
    agents = list(project.agents.list_agents())
    print(f"Found {len(agents)} agents:")

    for agent in agents:
        print(f"  - ID: {agent.id}")
        print(f"    Name: {getattr(agent, 'name', 'Unknown')}")
        print(f"    Instructions: {getattr(agent, 'instructions', 'None')[:100]}...")
        print()

except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback

    traceback.print_exc()

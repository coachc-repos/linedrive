#!/usr/bin/env python3
"""
Check for stuck/running threads and cancel them
"""

import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Load environment
load_dotenv("/Users/christhi/Dev/Github/linedrive/linedrive_azure/agents/.env")

# Configuration
review_agent_id = "asst_MeeUTGVUBItaslmikiJ1qhd9"
stuck_thread_id = "thread_8p4GAn3aTIuFPwUdb2WawjHJ"
stuck_run_id = "run_0KiJIvZ1mZI3kagPsxMyiKab"


def cancel_stuck_run():
    """Cancel the stuck run"""
    try:
        print("🔍 Connecting to Azure AI Foundry...")
        project_client = AIProjectClient(
            credential=DefaultAzureCredential(),
            api_key=os.getenv("AI_PROJECT_API_KEY"),
            endpoint="https://linedrive-ai-foundry.services.ai.azure.com/api/projects/linedriveAgents",
        )

        print(f"📋 Checking run status...")
        print(f"   Thread: {stuck_thread_id}")
        print(f"   Run: {stuck_run_id}")

        # Get run status
        run = project_client.agents.runs.get_run(
            thread_id=stuck_thread_id,
            run_id=stuck_run_id
        )

        print(f"\n📊 Current Run Status: {run.status}")

        if run.status in ["in_progress", "queued", "requires_action"]:
            print(f"\n🛑 Cancelling stuck run...")
            cancelled = project_client.agents.runs.cancel_run(
                thread_id=stuck_thread_id,
                run_id=stuck_run_id
            )
            print(f"✅ Run cancelled: {cancelled.status}")
        else:
            print(f"ℹ️  Run is not active, status: {run.status}")

        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("="*80)
    print("Cancel Stuck Run")
    print("="*80)
    cancel_stuck_run()

#!/usr/bin/env python3
"""
QUICK CHECK: Verify AI Foundry agent system prompts are set correctly.
Takes ~10 seconds instead of 3-4 minutes.

Usage:
    python tools/quick_prompt_check.py
"""

from linedrive_azure.agents.script_review_agent_client import (
    ScriptReviewAgentClient,
)
from linedrive_azure.agents.script_writer_agent_client import (
    ScriptWriterAgentClient,
)
from linedrive_azure.agents.script_topic_assistant_agent_client import (
    ScriptTopicAssistantAgentClient,
)
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def quick_check_agent(agent_client, agent_name: str):
    """Quick check of agent system prompt"""
    print(f"\n🔍 {agent_name}")
    print("-" * 60)

    try:
        agent = agent_client.project.agents.get_agent(agent_client.agent_id)
        instructions = agent.instructions if hasattr(
            agent, "instructions") else ""

        if not instructions:
            print("❌ NO SYSTEM INSTRUCTIONS FOUND!")
            return False

        # Quick checks
        checks = {
            "Has content": len(instructions) > 500,
            "YouTube refs": "Chris Williamson" in instructions
            or "AI Explained" in instructions,
            "Level 200": "level 200" in instructions.lower(),
            "Sensationalized": "sensationalized" in instructions.lower()
            or "provocative" in instructions.lower(),
            "Audience types": "beginners" in instructions.lower()
            and "developers" in instructions.lower(),
        }

        # Agent-specific checks
        if "Topic" in agent_name:
            checks["Storytelling"] = (
                "story" in instructions.lower() or "scenario" in instructions.lower()
            )
        elif "Writer" in agent_name:
            checks["Strong hook"] = "hook" in instructions.lower()
            checks["Visual cues"] = "visual cue" in instructions.lower()
        elif "Review" in agent_name:
            checks["Quality check"] = "quality" in instructions.lower()

        passed = sum(checks.values())
        total = len(checks)

        for name, result in checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {name}")

        print(f"\nScore: {passed}/{total} ({100*passed//total}%)")
        print(f"Length: {len(instructions):,} characters")

        return passed == total

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False


def main():
    print("=" * 60)
    print("🚀 QUICK AGENT PROMPT VERIFICATION (~10 seconds)")
    print("=" * 60)

    agents = [
        (ScriptTopicAssistantAgentClient(), "Topic Enhancement Agent"),
        (ScriptWriterAgentClient(), "Script Writer Agent"),
        (ScriptReviewAgentClient(), "Chapter Review Agent"),
    ]

    results = {}
    for agent_client, agent_name in agents:
        results[agent_name] = quick_check_agent(agent_client, agent_name)

    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)

    for agent_name, passed in results.items():
        status = "✅" if passed else "⚠️"
        print(f"{status} {agent_name}")

    if all(results.values()):
        print("\n✅ All prompts look good! Ready to generate scripts.")
    else:
        print("\n⚠️  Some prompts may need updating in AI Foundry portal.")
        print(
            "\nUpdate at: https://ai.azure.com → linedriveAgents → Agents → Instructions"
        )

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Quick verification script to check AI Foundry agent system prompts
WITHOUT running the full 3-4 minute pipeline.

This script:
1. Connects to each AI Foundry agent
2. Retrieves their system instructions/prompts
3. Displays key indicators to verify they're set correctly
"""

from linedrive_azure.agents.script_review_agent_client import ScriptReviewAgentClient
from linedrive_azure.agents.script_writer_agent_client import ScriptWriterAgentClient
from linedrive_azure.agents.script_topic_assistant_agent_client import (
    ScriptTopicAssistantAgentClient,
)
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_prompt_keywords(prompt_text: str, agent_name: str) -> dict:
    """Check for key indicators in the system prompt"""

    # Common keywords across all agents
    common_keywords = {
        "YouTube channels": any(
            channel in prompt_text
            for channel in [
                "Chris Williamson",
                "AI Explained",
                "Wes Roth",
                "Matthew Berman",
            ]
        ),
        "Level 200": "level 200" in prompt_text.lower() or "level200" in prompt_text.lower(),
        "Sensationalized": "sensationalized" in prompt_text.lower() or "provocative" in prompt_text.lower(),
        "Audience adaptation": "beginners" in prompt_text.lower() and "developers" in prompt_text.lower(),
        "Anti-patterns": "❌" in prompt_text or "never use" in prompt_text.lower(),
    }

    # Agent-specific keywords
    specific_keywords = {}

    if "Topic" in agent_name:
        specific_keywords = {
            "Storytelling": "story" in prompt_text.lower() or "scenario" in prompt_text.lower(),
            "Chapter breakdown": "chapter" in prompt_text.lower(),
            "No TensorFlow for beginners": "tensorflow" in prompt_text.lower(),
        }
    elif "Writer" in agent_name:
        specific_keywords = {
            "Strong hook": "hook" in prompt_text.lower() and "chapter 1" in prompt_text.lower(),
            "Conversational": "conversational" in prompt_text.lower(),
            "No formal language": "formal" in prompt_text.lower(),
            "Visual cues": "visual cue" in prompt_text.lower(),
        }
    elif "Review" in agent_name:
        specific_keywords = {
            "Quality assessment": "quality" in prompt_text.lower() or "assessment" in prompt_text.lower(),
            "Audience mismatch check": "mismatch" in prompt_text.lower(),
            "Complete revised chapter": "complete" in prompt_text.lower() and "revised" in prompt_text.lower(),
        }

    return {**common_keywords, **specific_keywords}


def verify_agent_prompt(agent_client, agent_name: str):
    """Verify a single agent's system prompt"""

    print(f"\n{'='*80}")
    print(f"🔍 VERIFYING: {agent_name}")
    print(f"{'='*80}")

    try:
        # Get agent details from AI Foundry
        agent = agent_client.project.agents.get_agent(agent_client.agent_id)

        print(f"✅ Agent ID: {agent_client.agent_id}")
        print(f"✅ Agent Name: {agent.name}")
        print(f"✅ Model: {agent.model}")

        # Get system instructions (the system prompt)
        instructions = agent.instructions if hasattr(
            agent, "instructions") else ""

        if not instructions:
            print(f"⚠️  WARNING: No system instructions found!")
            return False

        print(
            f"\n📝 System Instructions Length: {len(instructions)} characters")
        print(f"📝 System Instructions Preview (first 500 chars):")
        print("-" * 80)
        print(instructions[:500])
        print("..." if len(instructions) > 500 else "")
        print("-" * 80)

        # Check for key indicators
        print(f"\n🔍 KEY INDICATOR CHECKS:")
        print("-" * 80)

        checks = check_prompt_keywords(instructions, agent_name)

        passed = 0
        failed = 0

        for check_name, check_result in checks.items():
            status = "✅" if check_result else "❌"
            print(f"{status} {check_name}")
            if check_result:
                passed += 1
            else:
                failed += 1

        print("-" * 80)
        print(f"SCORE: {passed}/{passed+failed} checks passed")

        if failed > 0:
            print(
                f"\n⚠️  WARNING: {failed} checks failed - prompt may need updating!")
        else:
            print(f"\n✅ All checks passed!")

        return failed == 0

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main verification function"""

    print("=" * 80)
    print("🔍 AI FOUNDRY AGENT SYSTEM PROMPT VERIFICATION")
    print("=" * 80)
    print("\nThis script verifies that AI Foundry agent system prompts are set correctly")
    print("WITHOUT running the full 3-4 minute pipeline.\n")

    agents_to_check = [
        (ScriptTopicAssistantAgentClient(), "Topic Enhancement Agent"),
        (ScriptWriterAgentClient(), "Script Writer Agent"),
        (ScriptReviewAgentClient(), "Chapter Review Agent"),
    ]

    results = {}

    for agent_client, agent_name in agents_to_check:
        result = verify_agent_prompt(agent_client, agent_name)
        results[agent_name] = result

    # Summary
    print("\n" + "=" * 80)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 80)

    for agent_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ NEEDS UPDATE"
        print(f"{status}: {agent_name}")

    all_passed = all(results.values())

    if all_passed:
        print("\n✅ All agents have proper system prompts configured!")
        print("✅ Ready to run script generation workflow.")
    else:
        print("\n⚠️  Some agents need system prompt updates in AI Foundry portal!")
        print("\nTo update:")
        print("1. Go to Azure AI Foundry portal")
        print("2. Navigate to linedriveAgents project")
        print("3. Open each agent and update 'Instructions' field")
        print("4. Use the system prompts provided earlier in the conversation")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

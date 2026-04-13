#!/usr/bin/env python3
"""
Standalone Script Review Tool
===============================
Reviews an existing script without re-running the full workflow.
Use this when Step 3 (review) fails but Steps 1-2 (topic + writing) succeeded.

Usage:
    python tools/debug/standalone_review.py
    
Then paste your combined script when prompted.
"""

from dotenv import load_dotenv
from linedrive_azure.agents.script_writer_agent_client import ScriptWriterAgentClient
import sys
import os

# Add project root to path
project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)


# Load environment variables
env_path = os.path.join(project_root, "linedrive_azure", "agents", ".env")
load_dotenv(env_path)


def main():
    print("\n" + "=" * 60)
    print("🔍 STANDALONE SCRIPT REVIEW TOOL")
    print("=" * 60)
    print("\nThis tool will review your script WITHOUT the Review Agent.")
    print("It uses the Script Writer Agent to do a quick quality check.\n")

    # Get script input
    print("📋 PASTE YOUR COMBINED SCRIPT BELOW")
    print("(Ctrl+D when done, or type '---END---' on a new line)")
    print("-" * 60)

    lines = []
    try:
        while True:
            line = input()
            if line.strip() == "---END---":
                break
            lines.append(line)
    except EOFError:
        pass

    combined_script = "\n".join(lines)

    if not combined_script.strip():
        print("❌ No script provided. Exiting.")
        return

    print(f"\n✅ Received script ({len(combined_script)} chars)")

    # Get metadata
    topic = input("\n📋 Enter script topic: ").strip() or "AI Starters Guide"
    audience = input("👥 Enter target audience: ").strip() or "beginners"
    tone = input(
        "💬 Enter tone/style: ").strip() or "educational and conversational"

    print(f"\n🚀 Reviewing script...")
    print(f"   Topic: {topic}")
    print(f"   Audience: {audience}")
    print(f"   Tone: {tone}\n")

    # Initialize Script Writer client (we'll use it for review)
    try:
        writer_client = ScriptWriterAgentClient()

        # Create review request (simpler version)
        review_request = f"""
SCRIPT REVIEW REQUEST:

Please review this video script and provide:

1. **Overall Quality Assessment** (1-5 stars)
2. **What Works Well** (3-5 specific strengths)
3. **What Needs Improvement** (3-5 specific issues)
4. **Specific Suggestions** (actionable changes)
5. **Revised Script** (COMPLETE version with improvements)

**Context:**
- Topic: {topic}
- Target Audience: {audience}
- Tone: {tone}

**FULL SCRIPT TO REVIEW:**

{combined_script}

**FORMAT YOUR RESPONSE AS:**

=== REVIEW FEEDBACK ===
[Your detailed assessment]

=== REVISED SCRIPT ===
[COMPLETE revised script with all chapters and full dialogue]
"""

        # Create thread and send message
        thread_id = writer_client.create_thread()
        print(f"   ✅ Created review thread: {thread_id}")

        print(f"   🔍 Sending review request...")
        result = writer_client.send_message(
            thread_id=thread_id,
            message_content=review_request,
            show_sources=False,
            timeout=600  # 10 minutes
        )

        if result["success"]:
            review_response = result["response"]
            print(f"\n✅ Review completed ({len(review_response)} chars)\n")

            # Save to file
            output_file = os.path.join(
                project_root, "output", "standalone_review_result.txt")
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            with open(output_file, "w") as f:
                f.write("=" * 80 + "\n")
                f.write("SCRIPT REVIEW RESULT\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Topic: {topic}\n")
                f.write(f"Audience: {audience}\n")
                f.write(f"Tone: {tone}\n\n")
                f.write("=" * 80 + "\n\n")
                f.write(review_response)

            print(f"💾 Full review saved to: {output_file}\n")

            # Try to extract revised script
            if "REVISED SCRIPT" in review_response:
                revised_section = review_response.split(
                    "REVISED SCRIPT")[-1].strip()

                revised_file = os.path.join(
                    project_root, "output", "standalone_revised_script.txt")
                with open(revised_file, "w") as f:
                    f.write(revised_section)

                print(f"📝 Revised script saved to: {revised_file}\n")

            # Print summary
            print("=" * 60)
            print("📊 REVIEW SUMMARY")
            print("=" * 60)

            # Show first 1000 chars of review
            preview = review_response[:1000]
            if len(review_response) > 1000:
                preview += "\n\n... (truncated, see full output in file)"

            print(preview)
            print("\n✅ Review complete!")

        else:
            print(f"\n❌ Review failed: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"\n❌ Error during review: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

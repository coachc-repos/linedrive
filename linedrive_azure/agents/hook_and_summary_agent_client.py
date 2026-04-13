#!/usr/bin/env python3
"""
Hook and Summary Agent Client - Specialized client for generating video hooks and summaries

This agent handles creation of engaging video hooks and summaries:
- Opening Hook (8-10 seconds) with pattern interrupt at 5-7s
- Closing Summary (30-45 seconds) with recap + wrap-up + CTA
- Optimized for YouTube retention and engagement
"""

from typing import Dict, Any, Optional
from .base_agent_client import BaseAgentClient


class HookAndSummaryAgentClient(BaseAgentClient):
    """Specialized client for generating engaging hooks and summaries"""

    def __init__(self):
        """Initialize the Hook and Summary Agent"""
        super().__init__(
            agent_id="asst_IaM5FTf3cVZ33TjIatXwloWE",
            agent_name="Hook-and-Summary-Agent",
        )

    def get_specialized_info(self) -> Dict[str, Any]:
        """Get specialized information about the hook and summary agent"""
        return {
            "agent_type": "engagement_optimization",
            "capabilities": [
                "Opening hook generation (8-10 seconds)",
                "Pattern interrupt creation (5-7 second mark)",
                "Closing summary generation (30-45 seconds)",
                "Call-to-action (CTA) crafting",
                "Retention optimization",
                "Audience engagement maximization",
            ],
            "hook_requirements": {
                "duration": "8-10 seconds",
                "pattern_interrupt_timing": "5-7 seconds",
                "retention_goal": "70% in first 3 seconds",
                "structure": "0-3s: Hook, 3-5s: Intrigue, 5-7s: Interrupt, 7-10s: Promise",
            },
            "summary_requirements": {
                "duration": "30-45 seconds",
                "structure": "Recap + Wrap-up + CTA",
                "cta_focus": "Engagement-driven (like, subscribe, comment)",
            },
            "optimization_focus": [
                "First 3-second retention",
                "Pattern interrupt effectiveness",
                "Satisfying conclusion",
                "Call-to-action clarity",
                "Tone consistency with script",
                "Alignment with YouTube strategy",
            ],
            "hook_patterns": [
                "Question + Shock",
                "Bold Statement + Challenge",
                "Problem + Urgency",
                "Story Hook + Cliffhanger",
                "Statistic + Surprise",
            ],
            "cta_patterns": [
                "Value-based CTA",
                "Community-building CTA",
                "Next-video CTA",
                "Engagement CTA",
                "Educational CTA",
            ],
        }

    def generate_hook_and_summary(
        self,
        script_content: str,
        youtube_details: str = None,
        script_title: str = None,
        target_audience: str = "general",
        tone: str = "conversational",
        timeout: int = 240,
    ) -> Dict[str, Any]:
        """
        Generate engaging hook and summary for video script

        Args:
            script_content: Complete video script content
            youtube_details: YouTube metadata (title, description, tags) for context
            script_title: Title of the script/video
            target_audience: Target audience level (general, hobbyist, professional, expert)
            tone: Desired tone (conversational, educational, technical, entertaining)
            timeout: Maximum time to wait for response (seconds)

        Returns:
            Dictionary with:
            - success: Boolean indicating if generation was successful
            - hook: Opening hook text (8-10 seconds)
            - pattern_interrupt: Specific pattern interrupt text (5-7s mark)
            - summary: Closing summary text (30-45 seconds)
            - cta: Specific call-to-action
            - raw_response: Full agent response
            - error: Error message if generation failed
        """
        # Create detailed prompt for the agent
        prompt = f"""Generate an engaging HOOK and SUMMARY for the following video script.

**SCRIPT TITLE:** {script_title or "YouTube Educational Video"}
**TARGET AUDIENCE:** {target_audience}
**TONE:** {tone}

**SCRIPT CONTENT:**
{script_content}
"""

        # Add YouTube details context if available
        if youtube_details:
            prompt += f"""

**YOUTUBE METADATA (For Context):**
{youtube_details}

⚠️ IMPORTANT: Use this metadata to align the hook and summary with the video's SEO strategy and thumbnail text.
"""

        prompt += """

**TASK:**
Following your system instructions, generate:
1. THREE HOOK OPTIONS (8-10 seconds each) using DIFFERENT opening patterns
2. ONE OPENING STATEMENT (15-20 seconds) that teases ALL chapters
3. ONE SUMMARY/CONCLUSION (30-45 seconds) with recap + wrap-up + CTA

Use the EXACT OUTPUT FORMAT specified in your system instructions, including:
- HOOK OPTION 1 (8-10 SECONDS)
- HOOK OPTION 2 (8-10 SECONDS)
- HOOK OPTION 3 (8-10 SECONDS)
- OPENING STATEMENT (15-20 SECONDS)
- SUMMARY/CONCLUSION (30-45 SECONDS)
- YOUTUBE STRATEGY ALIGNMENT

Analyze the script and return all sections with their ANALYSIS subsections as specified.
"""

        # Create thread and send message
        thread = self.create_thread()
        if not thread:
            return {
                "success": False,
                "error": "Failed to create conversation thread",
                "hook": None,
                "pattern_interrupt": None,
                "summary": None,
                "cta": None,
                "raw_response": None,
            }

        print(f"🎯 Generating hook and summary with {self.agent_name}...")
        print(f"   Script length: {len(script_content)} chars")
        print(f"   Target audience: {target_audience}")
        print(f"   Tone: {tone}")

        result = self.send_message(
            thread_id=thread.id, message_content=prompt, timeout=timeout
        )

        if result["success"]:
            raw_response = result["response"]

            # Extract hook sections (3 options), opening statement, and summary
            hook1_text = ""
            hook2_text = ""
            hook3_text = ""
            opening_statement = ""
            summary_text = ""
            hook1_analysis = ""
            hook2_analysis = ""
            hook3_analysis = ""
            opening_analysis = ""
            summary_analysis = ""
            flow_analysis = ""

            # Try new format first (3 hooks + opening statement)
            if "HOOK OPTION 1 (8-10 SECONDS)" in raw_response:
                try:
                    # Extract Hook Option 1
                    parts = raw_response.split("HOOK OPTION 1 (8-10 SECONDS)")
                    if len(parts) > 1:
                        hook1_section = parts[1].split("HOOK OPTION 2")[0]
                        hook1_parts = hook1_section.split("ANALYSIS:")
                        if len(hook1_parts) > 1:
                            hook1_text = hook1_parts[0].strip()
                            hook1_analysis = "ANALYSIS:" + \
                                hook1_parts[1].strip()
                        else:
                            hook1_text = hook1_section.strip()

                    # Extract Hook Option 2
                    parts = raw_response.split("HOOK OPTION 2 (8-10 SECONDS)")
                    if len(parts) > 1:
                        hook2_section = parts[1].split("HOOK OPTION 3")[0]
                        hook2_parts = hook2_section.split("ANALYSIS:")
                        if len(hook2_parts) > 1:
                            hook2_text = hook2_parts[0].strip()
                            hook2_analysis = "ANALYSIS:" + \
                                hook2_parts[1].strip()
                        else:
                            hook2_text = hook2_section.strip()

                    # Extract Hook Option 3
                    parts = raw_response.split("HOOK OPTION 3 (8-10 SECONDS)")
                    if len(parts) > 1:
                        hook3_section = parts[1].split("OPENING STATEMENT")[0]
                        hook3_parts = hook3_section.split("ANALYSIS:")
                        if len(hook3_parts) > 1:
                            hook3_text = hook3_parts[0].strip()
                            hook3_analysis = "ANALYSIS:" + \
                                hook3_parts[1].strip()
                        else:
                            hook3_text = hook3_section.strip()

                    # Extract Opening Statement
                    opening_parts = raw_response.split(
                        "OPENING STATEMENT (15-20 SECONDS)")
                    if len(opening_parts) > 1:
                        opening_section = opening_parts[1].split(
                            "SUMMARY/CONCLUSION")[0]
                        opening_subparts = opening_section.split("ANALYSIS:")
                        if len(opening_subparts) > 1:
                            opening_statement = opening_subparts[0].strip()
                            opening_analysis = (
                                "ANALYSIS:" + opening_subparts[1].strip())
                        else:
                            opening_statement = opening_section.strip()

                    # Extract summary section
                    summary_parts = raw_response.split(
                        "SUMMARY/CONCLUSION (30-45 SECONDS)")
                    if len(summary_parts) > 1:
                        summary_section = summary_parts[1].split(
                            "YOUTUBE STRATEGY")[0]
                        summary_subparts = summary_section.split("ANALYSIS:")
                        if len(summary_subparts) > 1:
                            summary_text = summary_subparts[0].strip()
                            summary_analysis = (
                                "ANALYSIS:" + summary_subparts[1].strip())
                        else:
                            summary_text = summary_section.strip()

                    print(f"✅ Hook 1: {len(hook1_text)} chars")
                    print(f"✅ Hook 2: {len(hook2_text)} chars")
                    print(f"✅ Hook 3: {len(hook3_text)} chars")
                    print(f"✅ Opening: {len(opening_statement)} chars")
                    print(f"✅ Summary: {len(summary_text)} chars")

                except Exception as parse_error:
                    print(f"⚠️ Error parsing new format: {parse_error}")
                    # Fall back to returning what we have
                    pass

            return {
                "success": True,
                "hook": hook1_text,
                "hook1": hook1_text,
                "hook2": hook2_text,
                "hook3": hook3_text,
                "opening_statement": opening_statement,
                "summary": summary_text,
                "hook1_analysis": hook1_analysis,
                "hook2_analysis": hook2_analysis,
                "hook3_analysis": hook3_analysis,
                "opening_analysis": opening_analysis,
                "summary_analysis": summary_analysis,
                "flow_analysis": flow_analysis,
                "raw_response": raw_response,
                "error": None,
            }
        else:
            print(f"❌ Hook and summary generation failed: {result['error']}")
            return {
                "success": False,
                "error": result["error"],
                "hook": None,
                "pattern_interrupt": None,
                "summary": None,
                "cta": None,
                "raw_response": None,
            }

    def validate_hook(
        self, hook_text: str, max_seconds: int = 10, words_per_second: float = 2.5
    ) -> Dict[str, Any]:
        """
        Validate hook duration and structure

        Args:
            hook_text: Hook text to validate
            max_seconds: Maximum duration in seconds
            words_per_second: Average speaking rate

        Returns:
            Dictionary with validation results
        """
        word_count = len(hook_text.split())
        estimated_duration = word_count / words_per_second

        return {
            "valid": estimated_duration <= max_seconds,
            "word_count": word_count,
            "estimated_duration": estimated_duration,
            "max_duration": max_seconds,
            "within_limit": estimated_duration <= max_seconds,
            "recommendation": (
                "✅ Duration is good"
                if estimated_duration <= max_seconds
                else f"⚠️ Hook is {estimated_duration - max_seconds:.1f}s too long, consider shortening"
            ),
        }

    def validate_summary(
        self,
        summary_text: str,
        min_seconds: int = 30,
        max_seconds: int = 45,
        words_per_second: float = 2.5,
    ) -> Dict[str, Any]:
        """
        Validate summary duration and structure

        Args:
            summary_text: Summary text to validate
            min_seconds: Minimum duration in seconds
            max_seconds: Maximum duration in seconds
            words_per_second: Average speaking rate

        Returns:
            Dictionary with validation results
        """
        word_count = len(summary_text.split())
        estimated_duration = word_count / words_per_second

        return {
            "valid": min_seconds <= estimated_duration <= max_seconds,
            "word_count": word_count,
            "estimated_duration": estimated_duration,
            "min_duration": min_seconds,
            "max_duration": max_seconds,
            "within_range": min_seconds <= estimated_duration <= max_seconds,
            "recommendation": (
                "✅ Duration is perfect"
                if min_seconds <= estimated_duration <= max_seconds
                else (
                    f"⚠️ Summary is {min_seconds - estimated_duration:.1f}s too short"
                    if estimated_duration < min_seconds
                    else f"⚠️ Summary is {estimated_duration - max_seconds:.1f}s too long"
                )
            ),
        }


# Example usage and testing
if __name__ == "__main__":
    import asyncio

    async def test_agent():
        """Test the Hook and Summary Agent"""
        print("🧪 Testing Hook and Summary Agent")
        print("=" * 60)

        # Initialize agent
        agent = HookAndSummaryAgentClient()
        print(f"✅ Agent initialized: {agent.agent_name}")

        # Get agent info
        info = agent.get_specialized_info()
        print(f"\n📋 Agent Capabilities:")
        for cap in info["capabilities"]:
            print(f"   • {cap}")

        # Test with sample script
        sample_script = """
# The Future of AI in Healthcare

## Chapter 1: Introduction
Artificial Intelligence is revolutionizing healthcare...

## Chapter 2: Current Applications
From diagnosis to treatment planning...

## Chapter 3: Future Implications
The potential for AI to transform healthcare is immense...
"""

        sample_youtube_details = """
**Title:** AI in Healthcare: The Future is Now
**Description:** Discover how artificial intelligence is transforming modern medicine...
**Tags:** AI, healthcare, medical technology, machine learning
**Thumbnail Text:** "AI SAVES LIVES"
"""

        result = agent.generate_hook_and_summary(
            script_content=sample_script,
            youtube_details=sample_youtube_details,
            script_title="The Future of AI in Healthcare",
            target_audience="general",
            tone="conversational",
            timeout=240,
        )

        if result["success"]:
            print("\n✅ Hook and Summary Generated!")
            print("\n🎣 HOOK:")
            print(result["hook"])
            print("\n📝 SUMMARY:")
            print(result["summary"])

            # Validate durations
            if result["hook"]:
                hook_validation = agent.validate_hook(result["hook"])
                print(
                    f"\n⏱️ Hook Validation: {hook_validation['recommendation']}")

            if result["summary"]:
                summary_validation = agent.validate_summary(result["summary"])
                print(
                    f"⏱️ Summary Validation: {summary_validation['recommendation']}")
        else:
            print(f"\n❌ Generation failed: {result['error']}")

    # Run the test
    asyncio.run(test_agent())

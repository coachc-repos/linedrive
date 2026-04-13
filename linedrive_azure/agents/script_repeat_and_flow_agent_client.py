#!/usr/bin/env python3
"""
Script Repeat and Flow Agent Client - Specialized client for eliminating repetition and improving flow

This agent handles complete script analysis for:
- Identifying and eliminating repetitive content
- Ensuring smooth chapter-to-chapter transitions
- Maintaining consistent narrative progression
- Preserving intentional repetition (callbacks, key messages)
- Voice-friendly punctuation enforcement
"""

from typing import Dict, Any, Optional
from .base_agent_client import BaseAgentClient


class ScriptRepeatAndFlowAgentClient(BaseAgentClient):
    """Specialized client for script repetition elimination and flow analysis"""

    def __init__(self):
        """Initialize the Script Repeat and Flow Agent"""
        super().__init__(
            agent_id="asst_pjVIL7vZnKQzK6x7DfEsa2Ai",
            agent_name="Script-Repeat-and-Flow-Agent",
        )

    def get_specialized_info(self) -> Dict[str, Any]:
        """Get specialized information about the script repeat and flow agent"""
        return {
            "agent_type": "script_flow_optimization",
            "capabilities": [
                "Repetitive content detection and elimination",
                "Chapter-to-chapter flow analysis",
                "Narrative progression optimization",
                "Transition smoothing",
                "Voice-friendly punctuation enforcement",
                "Pacing balance across chapters",
            ],
            "analysis_areas": [
                "Duplicate tips and advice",
                "Redundant examples and analogies",
                "Repeated definitions and explanations",
                "Overlapping content between chapters",
                "Chapter transition quality",
                "Pacing and information density",
            ],
            "preservation_rules": [
                "Intentional callbacks and references",
                "Strategic key message repetition",
                "Rhetorical repetition for emphasis",
                "Framework building across chapters",
            ],
            "flow_improvements": [
                "Add transitional bridges",
                "Smooth tonal shifts",
                "Balance information density",
                "Strengthen narrative arc",
                "Improve chapter conclusions",
            ],
            "voice_compatibility": [
                "Remove em-dashes (—)",
                "Remove arrows (→)",
                "Remove en-dashes (–)",
                "Use commas and periods for pauses",
                "Spell out ranges (not 1–5)",
            ],
        }

    def analyze_and_improve_flow(
        self,
        script_content: str,
        script_title: str = None,
        target_audience: str = "general",
        timeout: int = 300,
    ) -> Dict[str, Any]:
        """
        Analyze complete script for repetition and flow, return improved version

        Args:
            script_content: Complete assembled video script
            script_title: Title of the script/video
            target_audience: Target audience level (general, hobbyist, professional, expert)
            timeout: Maximum time to wait for response (seconds)

        Returns:
            Dictionary with:
            - success: Boolean indicating if analysis was successful
            - improved_script: Complete revised script with repetitions removed and flow improved
            - repetition_analysis: Detailed analysis of repetitions found and removed
            - flow_analysis: Analysis of flow improvements made
            - raw_response: Full agent response
            - error: Error message if analysis failed
        """
        # Create detailed prompt for the agent
        prompt = f"""Analyze this COMPLETE VIDEO SCRIPT for repetitive content and flow issues.

**SCRIPT TITLE:** {script_title or "YouTube Educational Video"}
**TARGET AUDIENCE:** {target_audience}

**COMPLETE SCRIPT TO ANALYZE:**
{script_content}

**YOUR TASK:**

1. **Read the ENTIRE script** and identify ALL repetitive content:
   - Duplicate tips/advice appearing in multiple chapters
   - Redundant examples or analogies
   - Repeated definitions or explanations
   - Overlapping "how it works" sections
   - Rehashed statistics or facts

2. **Analyze flow between ALL chapters**:
   - Chapter-to-chapter transitions (smooth or jarring?)
   - Pacing issues (too dense, dragging, uneven?)
   - Narrative arc problems (weak conclusions, confusing structure?)

3. **Create detailed analysis report** showing:
   - What repetitions were found and where
   - What was removed vs. preserved (and why)
   - What flow issues were identified
   - What improvements were made

4. **Deliver COMPLETE REVISED SCRIPT** with:
   - All problematic repetitions removed
   - All flow issues corrected
   - ALL chapters with FULL dialogue (no summaries or condensing)
   - Smooth transitions between chapters
   - Voice-friendly punctuation (no em-dashes, arrows, en-dashes)

**CRITICAL RULES:**
- Remove ONLY problematic repetition (preserve intentional callbacks)
- Keep ALL chapters at FULL length
- Maintain engaging, conversational tone
- Ensure voice-friendly punctuation throughout
- Make script feel like one cohesive narrative

**OUTPUT FORMAT:**

=== REPETITION ANALYSIS ===

**Duplicate Content Found:**
1. [Description] - Found in Chapters X, Y, Z
   - ACTION: Removed from [locations], kept in [best location]
   - REASON: [why this location is best]

[Continue for all repetitions found]

**Flow Issues Identified:**
1. [Issue description between Chapters X and Y]
   - FIX: [what was done]

[Continue for all flow issues]

=== REVISED COMPLETE SCRIPT ===

[FULL SCRIPT with all chapters, complete dialogue, repetitions removed, flow improved]

## Chapter 1: [Title] (X:XX)

[Visual Cue: Description]

**Host:**
[Complete dialogue with improvements]

[Continue for ALL chapters]
"""

        try:
            # Create a thread and send message
            thread = self.create_thread()

            # Send message and get response
            result = self.send_message(
                thread_id=thread.id,
                message_content=prompt,
                timeout=timeout
            )

            if not result or not result.get("messages"):
                return {
                    "success": False,
                    "error": "No response from Script Repeat and Flow Agent",
                    "raw_response": result,
                }

            # Get the agent's response text
            messages = result.get("messages", [])
            agent_response = ""
            for msg in messages:
                if msg.get("role") == "assistant":
                    content = msg.get("content", "")
                    if isinstance(content, list):
                        agent_response = " ".join(
                            [
                                item.get("text", {}).get("value", "")
                                for item in content
                                if item.get("type") == "text"
                            ]
                        )
                    else:
                        agent_response = content

            if not agent_response:
                return {
                    "success": False,
                    "error": "Empty response from agent",
                    "raw_response": result,
                }

            # Parse the response to extract sections
            improved_script = ""
            repetition_analysis = ""
            flow_analysis = ""

            # Try to extract the revised script section
            if "=== REVISED COMPLETE SCRIPT ===" in agent_response:
                parts = agent_response.split("=== REVISED COMPLETE SCRIPT ===")
                if len(parts) > 1:
                    improved_script = parts[1].strip()

                # Extract analysis section
                if "=== REPETITION ANALYSIS ===" in parts[0]:
                    analysis_parts = parts[0].split(
                        "=== REPETITION ANALYSIS ===")
                    if len(analysis_parts) > 1:
                        analysis_text = analysis_parts[1].strip()

                        # Try to split into repetition and flow analysis
                        if "**Flow Issues Identified:**" in analysis_text:
                            rep_flow = analysis_text.split(
                                "**Flow Issues Identified:**")
                            repetition_analysis = rep_flow[0].strip()
                            flow_analysis = "**Flow Issues Identified:**\n" + \
                                rep_flow[1].strip()
                        else:
                            repetition_analysis = analysis_text

            # If extraction failed, use the entire response as improved script
            if not improved_script:
                improved_script = agent_response

            return {
                "success": True,
                "improved_script": improved_script,
                "repetition_analysis": repetition_analysis,
                "flow_analysis": flow_analysis,
                "raw_response": agent_response,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Exception during script flow analysis: {str(e)}",
                "raw_response": None,
            }


# For backwards compatibility and ease of import
if __name__ == "__main__":
    print("Script Repeat and Flow Agent Client")
    print("=" * 50)
    client = ScriptRepeatAndFlowAgentClient()
    print(f"Agent ID: {client.agent_id}")
    print(f"Agent Name: {client.agent_name}")
    print("\nCapabilities:")
    info = client.get_specialized_info()
    for capability in info["capabilities"]:
        print(f"  • {capability}")

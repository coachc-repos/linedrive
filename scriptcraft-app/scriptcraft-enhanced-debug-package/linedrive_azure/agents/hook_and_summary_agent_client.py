"""
Hook-and-Summary Agent Client for YouTube Script Optimization

This agent generates attention-grabbing hooks (8-10s) and compelling summaries (30-45s)
for completed video scripts to maximize viewer retention and engagement.
"""

from linedrive_azure.agents.base_agent_client import BaseAgentClient


class HookAndSummaryAgentClient(BaseAgentClient):
    """Client for Hook-and-Summary Agent on Azure AI Foundry"""

    def __init__(self):
        super().__init__(
            agent_name="Hook-and-Summary-Agent",
            agent_id="asst_IaM5FTf3cVZ33TjIatXwloWE"
        )

    def get_specialized_info(self) -> dict:
        """Get specialized information about this agent"""
        return {
            "purpose": "Generate hooks and summaries for video scripts",
            "hook_duration": "8-10 seconds",
            "summary_duration": "30-45 seconds",
            "capabilities": [
                "Attention-grabbing hooks with pattern interrupts",
                "Comprehensive summaries with CTAs",
                "YouTube retention optimization"
            ]
        }

    def generate_hook_and_summary(
        self,
        script_content: str,
        script_title: str,
        target_audience: str = "general audience",
        tone: str = "conversational and educational",
        video_length: str = "10 minutes",
        timeout: int = 120
    ) -> dict:
        """
        Generate hook and summary for a completed script.

        Args:
            script_content: The full reviewed script content
            script_title: The video title
            target_audience: Target audience level (beginners, hobbyists, professionals, experts)
            tone: Desired tone (conversational, educational, technical, entertaining)
            video_length: Approximate video length
            timeout: Maximum time to wait for response (default: 120 seconds)

        Returns:
            dict with success status, hook text, summary text, and analysis
        """
        print(f"\n🎯 Generating Hook and Summary for: {script_title}")
        print(f"   Audience: {target_audience}")
        print(f"   Tone: {tone}")
        print(f"   Script length: {len(script_content)} characters")

        # Create the request message
        request_message = f"""
HOOK AND SUMMARY GENERATION REQUEST

SCRIPT DETAILS:
- Title: {script_title}
- Target Audience: {target_audience}
- Tone: {tone}
- Video Length: {video_length}

COMPLETE SCRIPT TO ANALYZE:
{script_content}

TASK:
Generate THREE different hook options (8-10 seconds each), ONE summary/conclusion (30-45 seconds), AND analyze the flow between chapters.

HOOK REQUIREMENTS (GENERATE 3 VARIATIONS):
- Create 3 DIFFERENT hooks using DIFFERENT opening patterns (shocking statement, bold question, personal confession, etc.)
- Each hook should be unique but equally effective
- First 3 seconds must stop the scroll using one of the proven patterns
- Include pattern interrupt at 5-7 seconds
- End with commitment statement (7-10 seconds)
- Total: 25-35 words spoken naturally
- Reference specific elements from the script
- Match the video's tone and audience level

SUMMARY REQUIREMENTS:
- Quick recap of key takeaways (10-15 seconds)
- Satisfying wrap-up with closure (10-15 seconds)
- ONE clear call-to-action (10-15 seconds)
- Total: 90-135 words spoken naturally
- Reference specific tools/concepts from the script
- Create emotional closure and encourage engagement

FLOW ANALYSIS REQUIREMENTS:
- Identify chapter transitions (look for "---" separators or chapter markers)
- Check if each chapter ending flows naturally into the next chapter opening
- Note any jarring transitions or disconnects
- Identify chapters that feel isolated vs well-connected
- Rate overall script flow (1-5, where 5 is seamless)
- Suggest 1-2 specific transition improvements if needed

OUTPUT FORMAT (follow exactly):

HOOK OPTION 1 (8-10 SECONDS)
[Complete hook dialogue for option 1]

ANALYSIS:
- 0-3 sec pattern used: [Pattern name]
- 5-7 sec pattern interrupt: [Interrupt technique]
- Aligns with script tone: [Yes/No + note]
- References script content: [Specific elements]

HOOK OPTION 2 (8-10 SECONDS)
[Complete hook dialogue for option 2]

ANALYSIS:
- 0-3 sec pattern used: [Pattern name]
- 5-7 sec pattern interrupt: [Interrupt technique]
- Aligns with script tone: [Yes/No + note]
- References script content: [Specific elements]

HOOK OPTION 3 (8-10 SECONDS)
[Complete hook dialogue for option 3]

ANALYSIS:
- 0-3 sec pattern used: [Pattern name]
- 5-7 sec pattern interrupt: [Interrupt technique]
- Aligns with script tone: [Yes/No + note]
- References script content: [Specific elements]

SUMMARY/CONCLUSION (30-45 SECONDS)
[Complete summary dialogue]

ANALYSIS:
- Recap format used: [Format A/B/C]
- Wrap-up approach: [Closure type]
- CTA pattern used: [CTA Pattern number]
- Key elements reinforced: [List 2-3 takeaways]

FLOW ANALYSIS:
- Number of chapters detected: [Count]
- Overall flow rating: [1-5] - [Brief justification]
- Smooth transitions: [List chapter numbers with good flow]
- Jarring transitions: [List chapter numbers with problems, if any]
- Disconnected sections: [Identify isolated chapters, if any]
- Improvement suggestions: [1-2 specific fixes, or "None needed"]

YOUTUBE STRATEGY ALIGNMENT:
- Hook complements thumbnail text: [How they work together]
- Summary encourages [specific engagement action]
- Overall tone: [Match description]
"""

        # Create a new thread for this request
        thread = self.project.agents.threads.create()
        thread_id = thread.id

        # Send the message and get response
        result = self.send_message(
            thread_id=thread_id,
            message_content=request_message,
            show_sources=False,
            timeout=timeout
        )

        if not result["success"]:
            return {
                "success": False,
                "error": f"Hook-and-Summary generation failed: {result.get('error')}",
                "hook": None,
                "summary": None
            }

        # Parse the response
        response_text = result["response"]

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

        try:
            # Extract Hook Option 1
            parts = response_text.split("HOOK OPTION 1 (8-10 SECONDS)")
            if len(parts) > 1:
                hook1_section = parts[1].split("HOOK OPTION 2")[0]
                hook1_parts = hook1_section.split("ANALYSIS:")
                if len(hook1_parts) > 1:
                    hook1_text = hook1_parts[0].strip()
                    hook1_analysis = "ANALYSIS:" + hook1_parts[1].strip()
                else:
                    hook1_text = hook1_section.strip()

            # Extract Hook Option 2
            parts = response_text.split("HOOK OPTION 2 (8-10 SECONDS)")
            if len(parts) > 1:
                hook2_section = parts[1].split("HOOK OPTION 3")[0]
                hook2_parts = hook2_section.split("ANALYSIS:")
                if len(hook2_parts) > 1:
                    hook2_text = hook2_parts[0].strip()
                    hook2_analysis = "ANALYSIS:" + hook2_parts[1].strip()
                else:
                    hook2_text = hook2_section.strip()

            # Extract Hook Option 3
            parts = response_text.split("HOOK OPTION 3 (8-10 SECONDS)")
            if len(parts) > 1:
                hook3_section = parts[1].split("OPENING STATEMENT")[0]
                hook3_parts = hook3_section.split("ANALYSIS:")
                if len(hook3_parts) > 1:
                    hook3_text = hook3_parts[0].strip()
                    hook3_analysis = "ANALYSIS:" + hook3_parts[1].strip()
                else:
                    hook3_text = hook3_section.strip()

            # Extract Opening Statement
            opening_parts = response_text.split("OPENING STATEMENT (15-20 SECONDS)")
            if len(opening_parts) > 1:
                opening_section = opening_parts[1].split("SUMMARY/CONCLUSION")[0]
                opening_subparts = opening_section.split("ANALYSIS:")
                if len(opening_subparts) > 1:
                    opening_statement = opening_subparts[0].strip()
                    opening_analysis = "ANALYSIS:" + opening_subparts[1].strip()
                else:
                    opening_statement = opening_section.strip()

            # Extract summary section
            summary_parts = response_text.split(
                "SUMMARY/CONCLUSION (30-45 SECONDS)")
            if len(summary_parts) > 1:
                summary_section = summary_parts[1].split("FLOW ANALYSIS:")[0]
                summary_subparts = summary_section.split("ANALYSIS:")
                if len(summary_subparts) > 1:
                    summary_text = summary_subparts[0].strip()
                    summary_analysis = "ANALYSIS:" + \
                        summary_subparts[1].strip()
                else:
                    summary_text = summary_section.strip()

            # Extract flow analysis section
            flow_parts = response_text.split("FLOW ANALYSIS:")
            if len(flow_parts) > 1:
                flow_section = flow_parts[1].split("YOUTUBE STRATEGY")[0]
                flow_analysis = flow_section.strip()

            print(f"✅ Hook 1 generated: {len(hook1_text)} characters")
            print(f"✅ Hook 2 generated: {len(hook2_text)} characters")
            print(f"✅ Hook 3 generated: {len(hook3_text)} characters")
            print(f"✅ Opening statement generated: {len(opening_statement)} characters")
            print(f"✅ Summary generated: {len(summary_text)} characters")
            if flow_analysis:
                print(
                    f"✅ Flow analysis generated: {len(flow_analysis)} characters")

        except Exception as parse_error:
            print(f"⚠️ Parsing warning: {parse_error}")
            # Fallback: use entire response
            hook1_text = "Could not extract hooks - see full response"
            hook2_text = ""
            hook3_text = ""
            summary_text = "Could not extract summary - see full response"

        return {
            "success": True,
            "hook": hook1_text,  # Keep for backward compatibility
            "hook1": hook1_text,
            "hook2": hook2_text,
            "hook3": hook3_text,
            "summary": summary_text,
            "hook1_analysis": hook1_analysis,
            "hook2_analysis": hook2_analysis,
            "hook3_analysis": hook3_analysis,
            "summary_analysis": summary_analysis,
            "flow_analysis": flow_analysis,
            "full_response": response_text,
            "script_title": script_title,
            "audience": target_audience,
            "tone": tone
        }

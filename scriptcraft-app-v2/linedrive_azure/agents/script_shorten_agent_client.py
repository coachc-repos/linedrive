#!/usr/bin/env python3
"""
Script Shorten Agent Client - Smart shortening of finalized scripts.

Targets the new Foundry agent "Script-Shorten-Agent" (v2-only).
The v1 `agent_id` is a placeholder; v2 mode resolves by name via
V1_TO_V2_AGENT_NAME in base_agent_client.py.
"""

from typing import Any, Dict, Optional

from .base_agent_client import BaseAgentClient


class ScriptShortenAgentClient(BaseAgentClient):
    """Calls the Script-Shorten-Agent to condense Host: dialogue."""

    def __init__(self):
        super().__init__(
            # v2-only agent — placeholder id; resolution happens by name.
            agent_id="asst_script_shorten_v2_only",
            agent_name="Script-Shorten-Agent",
        )

    def shorten_to_target(
        self,
        script_content: str,
        target_minutes: float,
        wpm: int = 150,
        timeout: int = 600,
        target_words_override: Optional[int] = None,
        reduction_percent: Optional[int] = None,
        current_host_words: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Smart-shorten the script. The system prompt lives on the Foundry
        agent itself (script_shorten_agent_instructions.md), so this prompt
        just carries the per-call targets and the script payload.
        """
        if target_words_override is not None and target_words_override > 0:
            target_words = int(target_words_override)
        else:
            target_words = int(round(target_minutes * wpm))

        current_words = len(script_content.split())
        cur_host = (
            current_host_words
            if current_host_words is not None
            else "(not provided)"
        )
        pct_note = (
            f"- Requested reduction: ~{reduction_percent}% of current Host: words"
            if reduction_percent
            else "- Reduction implied by target Host: word count below"
        )

        query = f"""TARGET LENGTH:
- Target video length: {target_minutes:.1f} minutes at {wpm} wpm
- Target Host: word count: ~{target_words} words (total across all Host blocks)
- Current Host: word count: {cur_host}
- Current total word count (entire script): ~{current_words} words
{pct_note}

Apply your smart-cut rules and return ONLY the rewritten script text — no
preamble, no commentary, no code fences.

SCRIPT CONTENT TO SHORTEN:
{script_content}
"""

        thread = self.create_thread()
        if not thread:
            return {"success": False, "error": "Failed to create shorten thread"}

        return self.send_message(
            thread_id=thread.id, message_content=query, timeout=timeout
        )

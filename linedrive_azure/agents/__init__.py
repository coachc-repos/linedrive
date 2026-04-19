"""
LineDrive Azure AI Agents

This module provides access to all LineDrive AI agents and orchestration systems.
"""

try:
    from .base_agent_client import BaseAgentClient
    from .tournament_agent_client import TournamentAgentClient
    from .ai_tips_agent_client import AITipsAgentClient
    from .script_writer_agent_client import ScriptWriterAgentClient
    from .script_review_agent_client import ScriptReviewAgentClient
    from .youtube_upload_details_agent_client import YouTubeUploadDetailsAgentClient
    from .script_broll_agent_client import ScriptBRollAgentClient
    from .hook_and_summary_agent_client import HookAndSummaryAgentClient
    from .script_repeat_and_flow_agent_client import ScriptRepeatAndFlowAgentClient
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Azure SDK not available, agent clients disabled: {e}")

# Temporarily disabled until AutoGen dependencies are available
# from .enhanced_autogen_system import EnhancedAutoGenSystem

# Legacy imports for backwards compatibility
try:
    from .agent_client import LinedriveAgentClient
    from .agent_framework import TournamentAutoGenSystem
except ImportError:
    pass

__all__ = [
    "BaseAgentClient",
    "TournamentAgentClient",
    "AITipsAgentClient",
    "ScriptWriterAgentClient",
    "ScriptReviewAgentClient",
    "YouTubeUploadDetailsAgentClient",
    "ScriptBRollAgentClient",
    "HookAndSummaryAgentClient",
    "ScriptRepeatAndFlowAgentClient",
    # Temporarily disabled until AutoGen dependencies are available
    # "EnhancedAutoGenSystem",
    # Legacy
    "LinedriveAgentClient",
    "TournamentAutoGenSystem",
]

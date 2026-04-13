#!/usr/bin/env python3
"""
Text processing functions for LineDrive Console
Handles script content manipulation and teleprompter text extraction
"""

import re
from pathlib import Path


def extract_teleprompter_text(script_content: str) -> str:
    """Extract only host-readable text from script, removing visual cues,
    production notes, and technical directions"""
    print("📺 Extracting teleprompter-friendly text from script...")

    lines = script_content.split("\n")
    teleprompter_lines = []

    skip_patterns = [
        # Visual cues
        r"^\s*\[Visual Cue:",
        r"^\s*\[visual cue:",
        r"^\s*\[VISUAL CUE:",
        r"^\s*Visual Cue:",
        # Production notes
        r"^\s*\[Production Note:",
        r"^\s*\[production note:",
        r"^\s*\[PRODUCTION NOTE:",
        r"^\s*Production Note:",
        # Technical directions
        r"^\s*\[Technical:",
        r"^\s*\[TECHNICAL:",
        r"^\s*Technical:",
        # Camera directions
        r"^\s*\[Camera:",
        r"^\s*\[CAMERA:",
        r"^\s*Camera:",
    ]

    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue

        # Check if line should be skipped
        should_skip = False
        for pattern in skip_patterns:
            if re.match(pattern, line):
                should_skip = True
                break

        if not should_skip:
            teleprompter_lines.append(line)

    return "\n".join(teleprompter_lines)


def enhance_script_with_bold_tools(script_content: str) -> str:
    """Enhance script content by making tools, headings, and visual cues bold"""

    # Check if this looks like demo packages content
    if "DEMO PACKAGE" in script_content.upper() and (
        "TOOL 1" in script_content.upper()
        or "EVERYDAY-VIEWER" in script_content.upper()
    ):
        return enhance_demo_packages_formatting(script_content)

    print("✨ Enhancing script with bold tool formatting...")

    lines = script_content.split("\n")
    enhanced_lines = []

    # Common tools and services that should be bold
    tool_names = [
        # AI and productivity tools
        "Notion",
        "ChatGPT",
        "Claude",
        "Gemini",
        "OpenAI",
        "Zapier",
        "Grammarly",
        "Loom",
        "Calendly",
        "Slack",
        "Trello",
        "Asana",
        # Design and creative tools
        "Figma",
        "Canva",
        "Photoshop",
        "Illustrator",
        # Communication tools
        "Zoom",
        "Microsoft Teams",
        "Discord",
        "Telegram",
        # Development tools
        "GitHub",
        "GitLab",
        "VS Code",
        "Visual Studio Code",
        "Copilot",
        # Media and entertainment
        "YouTube",
        "Netflix",
        "TikTok",
        "Instagram",
        "Twitter",
        "LinkedIn",
    ]

    for line in lines:
        enhanced_line = line

        # Handle visual cue sections with special formatting
        if enhanced_line.strip().startswith(
            "**Visual Cue:**"
        ) or enhanced_line.strip().startswith("Visual Cue:"):
            # Make visual cues larger and colorized
            visual_text = (
                enhanced_line.strip()
                .replace("**Visual Cue:**", "")
                .replace("Visual Cue:", "")
                .strip()
            )
            enhanced_line = f"## 🎬 **VISUAL CUE:** {visual_text}"
            enhanced_lines.append(enhanced_line)
            continue

        # Make known tools bold
        for tool in tool_names:
            # Only make it bold if it's not already bold
            if tool in enhanced_line and f"**{tool}**" not in enhanced_line:
                # Use word boundaries to avoid partial matches
                pattern = r"\b" + re.escape(tool) + r"\b"
                enhanced_line = re.sub(pattern, f"**{tool}**", enhanced_line)

        enhanced_lines.append(enhanced_line)

    return "\n".join(enhanced_lines)


def enhance_demo_packages_formatting(demo_content: str) -> str:
    """Enhance demo package content with proper formatting for headings"""
    print("✨ Applying demo-specific formatting enhancements...")

    lines = demo_content.split("\n")
    enhanced_lines = []

    for line in lines:
        enhanced_line = line
        stripped = line.strip()

        # Main demo package headers
        demo_starts = ["EVERYDAY-VIEWER DEMO PACKAGE", "DEVELOPER DEMO PACKAGE"]
        if any(stripped.startswith(start) for start in demo_starts):
            enhanced_line = f"## {stripped}"

        # Tool headers (TOOL 1 — ChatGPT format)
        elif stripped.startswith("TOOL ") and "—" in stripped:
            enhanced_line = f"### {stripped}"

        # Make tool names bold in sentences
        tool_names = ["ChatGPT", "Canva", "Notion", "YouTube", "Google"]
        for tool in tool_names:
            if tool in enhanced_line and f"**{tool}**" not in enhanced_line:
                enhanced_line = enhanced_line.replace(tool, f"**{tool}**")

        enhanced_lines.append(enhanced_line)

    return "\n".join(enhanced_lines)


def extract_tool_links_and_info(script_content: str) -> str:
    """Extract tool links and information for YouTube description"""
    print("🔍 Extracting tool links and information...")

    lines = script_content.split("\n")
    extracted_urls = []

    # Enhanced patterns for tool identification and URLs
    url_pattern = r"(https?://[^\s\)>,]+)"

    for line in lines:
        line = line.strip()
        if "**URL**:" in line or "URL:" in line:
            # Direct URL extraction from **URL**: format
            urls = re.findall(url_pattern, line)
            for url in urls:
                # Clean URL and normalize format
                url = url.rstrip(".,!?;:")
                # Add https:// if it's a domain without protocol
                if not url.startswith("http"):
                    url = f"https://{url}"
                if url not in extracted_urls:
                    extracted_urls.append(url)

    # Map URLs to tool names based on domain
    url_to_tool = {
        "chat.openai.com": "ChatGPT",
        "claude.ai": "Claude",
        "perplexity.ai": "Perplexity",
        "canva.com": "Canva",
        "grammarly.com": "Grammarly",
        "notion.so": "Notion",
        "github.com": "GitHub",
    }

    # Create tool info from extracted URLs
    tool_info = []
    for url in extracted_urls:
        # Try to match domain to known tool
        tool_found = False
        for domain, tool_name in url_to_tool.items():
            if domain in url:
                tool_info.append(f"• {tool_name}: {url}")
                tool_found = True
                break

        if not tool_found:
            # Extract domain name as tool name
            try:
                domain = url.split("//")[1].split("/")[0]
                if domain.startswith("www."):
                    domain = domain[4:]
                tool_name = domain.replace(".com", "").replace(".ai", "").capitalize()
                tool_info.append(f"• {tool_name}: {url}")
            except Exception:
                tool_info.append(f"• Tool: {url}")

    if tool_info:
        youtube_description = "\n🛠️ TOOLS & RESOURCES MENTIONED:\n"
        youtube_description += "\n".join(tool_info)
        youtube_description += (
            "\n\n📝 This description contains affiliate links where applicable."
        )
        youtube_description += (
            "\nUsing these links helps support the channel at no extra cost to you."
        )
        youtube_description += (
            "\n\n🔗 Want more productivity tips? Check out our other videos!"
        )
        return youtube_description
    else:
        return "\n🛠️ No specific tools or resources were mentioned in this content."

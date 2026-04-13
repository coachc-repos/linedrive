#!/usr/bin/env python3
"""
Utility functions for LineDrive Console
Contains helper functions for file operations, text processing, etc.
"""

import re
from pathlib import Path
from typing import Optional


def sanitize_filename(text: str) -> str:
    """Convert text to safe filename by removing/replacing problematic characters"""
    # Remove or replace problematic characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "", text)  # Remove invalid filename chars
    sanitized = re.sub(
        r"[^\w\s-]", "", sanitized
    )  # Keep only alphanumeric, spaces, hyphens
    sanitized = re.sub(r"\s+", "_", sanitized)  # Replace spaces with underscores
    sanitized = sanitized.strip("_")  # Remove leading/trailing underscores

    # Limit length to avoid filesystem issues
    if len(sanitized) > 50:
        sanitized = sanitized[:50].rstrip("_")

    return sanitized if sanitized else "untitled_script"


def extract_script_title(script_content: str) -> str:
    """Extract the title from script content, looking for common title patterns"""
    if not script_content.strip():
        return "Untitled Script"

    lines = script_content.strip().split("\n")

    # Look for markdown h1 headers (# Title)
    for line in lines[:10]:  # Check first 10 lines
        line = line.strip()
        if line.startswith("# ") and len(line) > 2:
            title = line[2:].strip()
            # Clean up common prefixes
            title = re.sub(
                r"^(PODCAST SCRIPT:|SCRIPT:|VIDEO SCRIPT:)\s*",
                "",
                title,
                flags=re.IGNORECASE,
            )
            title = re.sub(r"^(Episode \d+:?\s*-?\s*)", "", title, flags=re.IGNORECASE)
            return title.strip() if title.strip() else "Untitled Script"

    # Look for lines that might be titles (all caps, etc.)
    for line in lines[:5]:  # Check first 5 lines
        line = line.strip()
        if not line:
            continue

        # Skip metadata lines
        if any(
            marker in line.lower()
            for marker in ["date:", "author:", "version:", "---", "```"]
        ):
            continue

        # If it's a substantial line that looks like a title
        if len(line) > 10 and (
            line.isupper()  # All caps
            or line.count(":") == 1  # Has single colon
            or "SCRIPT" in line.upper()  # Contains SCRIPT
            or "EPISODE" in line.upper()
        ):  # Contains EPISODE

            # Clean up the line
            title = re.sub(
                r"^(PODCAST SCRIPT:|SCRIPT:|VIDEO SCRIPT:)\s*",
                "",
                line,
                flags=re.IGNORECASE,
            )
            title = re.sub(r"^(Episode \d+:?\s*-?\s*)", "", title, flags=re.IGNORECASE)
            return title.strip() if title.strip() else "Untitled Script"

    # Fallback: use first substantial line
    for line in lines[:3]:
        line = line.strip()
        if line and len(line) > 5:
            return line[:100]  # Limit length

    return "Untitled Script"


def get_word_template_path() -> Optional[Path]:
    """Get the Word template path if available"""
    # Check for template in templates directory (prefer DOCX over DOTX for compatibility)
    template_paths = [
        Path(__file__).parent / "templates" / "linedrive_template_docx.docx",
        Path(__file__).parent.parent / "templates" / "linedrive_template_docx.docx",
        Path(__file__).parent / "templates" / "linedrive_template.dotx",
        Path(__file__).parent.parent / "templates" / "linedrive_template.dotx",
    ]

    for template_path in template_paths:
        if template_path.exists():
            return template_path

    return None

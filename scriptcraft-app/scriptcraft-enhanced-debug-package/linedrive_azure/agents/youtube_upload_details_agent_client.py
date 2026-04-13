#!/usr/bin/env python3
"""
YouTube Upload Details Agent Client - Specialized client for generating YouTube upload metadata

This agent handles creation of comprehensive YouTube upload details including:
- Video filename generation
- SEO-optimized titles
- Complete video descriptions with timestamps
- Tags for discoverability
- Thumbnail text suggestions
- Category recommendations
- Playlist suggestions
"""

from typing import Dict, Any, List
from .base_agent_client import BaseAgentClient


class YouTubeUploadDetailsAgentClient(BaseAgentClient):
    """Specialized client for generating YouTube upload metadata and details"""

    def __init__(self):
        """Initialize the YouTube Upload Details Agent"""
        super().__init__(
            agent_id="asst_3SXXgX7WbQmrgg2tGDgkynKV",
            agent_name="YouTube-Upload-Details-Agent",
        )

    def get_specialized_info(self) -> Dict[str, Any]:
        """Get specialized information about the YouTube upload details agent"""
        return {
            "agent_type": "youtube_metadata_generation",
            "capabilities": [
                "Video filename generation",
                "SEO-optimized title creation",
                "Comprehensive description writing",
                "Tag generation for discoverability",
                "Thumbnail text suggestions",
                "Category recommendations",
                "Playlist organization suggestions",
                "End screen content recommendations",
            ],
            "metadata_components": [
                "Clean, SEO-friendly file names",
                "Click-worthy titles (60 char limit)",
                "Structured descriptions (2000-3000 chars)",
                "15-30 relevant tags",
                "Thumbnail text (3-7 words)",
                "Category selection with justification",
                "Playlist suggestions",
                "End screen recommendations",
            ],
            "optimization_focus": [
                "Search engine optimization (SEO)",
                "Click-through rate (CTR) optimization",
                "Discoverability enhancement",
                "Engagement maximization",
                "Algorithm-friendly formatting",
                "Accessibility considerations",
            ],
            "seo_strategies": [
                "Primary keyword integration",
                "Long-tail keyword inclusion",
                "Question-based keywords",
                "Trending topic integration",
                "Competitor analysis insights",
                "YouTube autocomplete optimization",
            ],
        }

    def generate_upload_details(
        self,
        script_content: str,
        script_title: str = None,
        target_audience: str = "general",
        video_length: str = None,
        primary_keywords: List[str] = None,
        channel_focus: str = None,
        timeout: int = 300,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive YouTube upload details from script content

        Args:
            script_content: The complete script content to analyze
            script_title: Title of the script (extracted if not provided)
            target_audience: Target audience for the content (e.g., "beginners", "professionals")
            video_length: Approximate video length (e.g., "10 minutes", "5-7 minutes")
            primary_keywords: List of primary keywords to focus on (optional)
            channel_focus: Channel focus/niche (e.g., "productivity", "tech reviews")
            timeout: Maximum time to wait for response

        Returns:
            Dictionary containing all YouTube upload details
        """

        # Extract title if not provided
        if not script_title:
            lines = script_content.split("\n")
            for line in lines[:10]:  # Check first 10 lines for title
                if line.strip() and not line.startswith("#"):
                    script_title = line.strip()
                    break
            if not script_title:
                script_title = "Untitled Video"

        # Build keyword context
        keyword_context = ""
        if primary_keywords:
            keyword_context = f"\n        Primary Keywords to emphasize: {', '.join(primary_keywords)}"

        # Build channel context
        channel_context = ""
        if channel_focus:
            channel_context = (
                f"\n        Channel Focus/Niche: {channel_focus}"
            )

        # Calculate expected video duration for VALIDATION (not passed to agent)
        # Agent will do its own calculation - we use this to validate the result
        word_count = len(script_content.split())
        # Average speaking pace: 150 words per minute
        estimated_minutes = word_count / 150
        estimated_seconds = int(estimated_minutes * 60)

        # Format as minutes:seconds for validation
        duration_mins = estimated_seconds // 60
        duration_secs = estimated_seconds % 60
        calculated_duration = f"{duration_mins}:{duration_secs:02d}"
        
        print(f"📊 Client-side validation: {word_count} words = {calculated_duration} estimated duration")

        # Build video length context (only user-provided target, not our calculation)
        length_context = ""
        if video_length:
            length_context = f"\n        Target Video Length: {video_length}"

        query = f"""
        MANDATORY INSTRUCTION: You are a YouTube Upload Details Specialist. 
        You must IMMEDIATELY generate comprehensive YouTube upload metadata based on the provided script.
        DO NOT ask clarifying questions. DO NOT request additional information. 
        ANALYZE THE SCRIPT AND CREATE ALL UPLOAD DETAILS NOW.

        IMMEDIATE ACTION REQUIRED: Generate complete YouTube upload details for this video:

        SCRIPT CONTENT TO ANALYZE:
        {script_content}

        SCRIPT CONTEXT:
        - Script Title: {script_title}
        - Target Audience: {target_audience}{keyword_context}{channel_context}{length_context}

        REQUIRED OUTPUT SECTIONS (Use exact markdown format):

        ## 📁 FILE NAME
        Generate a clean, SEO-friendly filename:
        - Lowercase, hyphen-separated words
        - Include primary keyword
        - No special characters
        - Maximum 60 characters
        - Example format: "best-ai-tools-productivity-2025"

        ## 🎬 VIDEO TITLE
        Create an engaging, optimized title:
        - Include primary keywords naturally
        - Maximum 60 characters (avoid truncation)
        - Use power words and numbers when appropriate
        - Create curiosity and promise value
        - Examples: "10 AI Tools That Will 10X Your Productivity in 2025"

        ## 📝 DESCRIPTION
        Write a comprehensive 2000-3000 character description with these sections:

        **HOOK (First 150 chars - appears in search):**
        Front-load keywords and create interest

        **OVERVIEW:**
        What viewers will learn (use bullet points)

        **TIMESTAMPS:**
        📌 Create chapter markers based on script structure
        📌 CRITICAL: If script already has timestamps, USE THEM EXACTLY
        📌 If no timestamps exist, calculate them to match the estimated video duration
        📌 DO NOT create timestamps that exceed the video length
        📌 Distribute timestamps evenly across the video
        Format: 0:00 Introduction
                2:15 Chapter Title
                5:30 Next Section
                (etc.)

        **TOOLS & RESOURCES:**
        🔗 List all tools mentioned with full URLs
        Include any resources referenced in the script

        **CONNECT WITH US:**
        📱 [Your Social Media Placeholders]
        
        **HASHTAGS:**
        Include 3-5 relevant hashtags at the end

        **CALL TO ACTION:**
        Encourage likes, subscribes, and comments

        ## 🏷️ TAGS
        Generate 15-30 relevant tags (comma-separated):
        - Primary keyword variations
        - Related topics and subtopics
        - Tool names from the script
        - Year/date tags (e.g., "2025")
        - Audience tags (e.g., "for beginners")
        - Format tags (e.g., "tutorial", "guide")
        - Mix of broad and specific tags

        ## 🖼️ THUMBNAIL TEXT
        Suggest bold thumbnail text (3-7 words max):
        - Attention-grabbing phrases
        - High contrast text recommendations
        - Examples: "10 AI TOOLS", "GAME CHANGER"

        ## 📂 CATEGORY
        Recommend the best YouTube category:
        - Select from: Education, Science & Technology, Howto & Style, Entertainment, etc.
        - Provide brief justification

        ## 📚 PLAYLIST SUGGESTIONS
        Suggest 2-3 relevant playlist names:
        - Think about series potential
        - Consider content organization
        - Help with channel structure

        ## 🎯 END SCREEN RECOMMENDATIONS
        Suggest end screen content:
        - Related videos to promote
        - Playlists to link
        - Subscribe button placement

        ## 💡 ADDITIONAL NOTES
        Provide upload tips:
        - Best posting times
        - Community post ideas
        - Pinned comment suggestions
        - Engagement strategies

        CRITICAL REQUIREMENTS:
        1. Extract ALL tools/resources mentioned in the script with accurate URLs
        2. Create timestamps based on actual chapter structure in the script
        3. Ensure all keywords are relevant to the actual content
        4. Make the description scannable with clear sections
        5. Optimize for both YouTube search and suggested videos
        6. Balance SEO optimization with natural, engaging language
        7. Include specific details from the script (tool names, features, etc.)
        8. Make the title and thumbnail text work together for CTR
        9. Consider the target audience in all recommendations
        10. Ensure accessibility in formatting and structure

        SEO OPTIMIZATION PRIORITIES:
        - Front-load keywords in title and description
        - Use long-tail keywords naturally
        - Include question-based keywords
        - Reference trending topics when relevant
        - Use tool/brand names for search traffic
        - Balance broad and niche tags

        ENGAGEMENT OPTIMIZATION:
        - Create curiosity gaps
        - Use emotional triggers
        - Include specific numbers and timeframes
        - Promise clear value/outcomes
        - Use action verbs
        - Create urgency when appropriate

        Generate all sections now using the exact markdown format specified.
        """

        # Create thread and send message to agent
        thread = self.create_thread()
        if not thread:
            return {
                "success": False,
                "error": "Failed to create thread",
                "upload_details": "",
            }

        # Send the query and get response
        result = self.send_message(
            thread_id=thread.id,
            message_content=query,
            show_sources=False,
            timeout=timeout,
        )

        # Parse the response to extract structured data
        response_text = result.get("response", "")
        
        # VALIDATION: Check if agent's timestamps exceed our calculated duration
        self._validate_timestamps(response_text, estimated_seconds, calculated_duration)

        return {
            "success": result.get("success", False),
            "upload_details": response_text,
            "raw_response": result,
            "script_title": script_title,
            "metadata": {
                "target_audience": target_audience,
                "video_length": video_length,
                "primary_keywords": primary_keywords,
                "channel_focus": channel_focus,
                "calculated_duration": calculated_duration,
                "word_count": word_count,
            },
        }

    def extract_filename(self, upload_details: str) -> str:
        """Extract the suggested filename from the upload details"""
        import re

        match = re.search(r"## 📁 FILE NAME\s+(.+?)(?:\n\n|##)",
                          upload_details, re.DOTALL)
        if match:
            # Get the filename and clean it
            filename = match.group(1).strip().split("\n")[0].strip()
            # Remove any markdown formatting or extra text
            filename = re.sub(r"[`*_]", "", filename)
            return filename
        return "video-upload"

    def extract_title(self, upload_details: str) -> str:
        """Extract the suggested video title from the upload details"""
        import re

        match = re.search(r"## 🎬 VIDEO TITLE\s+(.+?)(?:\n\n|##)",
                          upload_details, re.DOTALL)
        if match:
            title = match.group(1).strip().split("\n")[0].strip()
            # Remove markdown formatting
            title = re.sub(r"[`*_]", "", title)
            return title
        return "Untitled Video"

    def extract_tags(self, upload_details: str) -> List[str]:
        """Extract the suggested tags as a list from the upload details"""
        import re

        match = re.search(r"## 🏷️ TAGS\s+(.+?)(?:\n\n|##)",
                          upload_details, re.DOTALL)
        if match:
            tags_text = match.group(1).strip()
            # Split by commas and clean each tag
            tags = [tag.strip() for tag in tags_text.split(",")]
            # Remove empty tags
            tags = [tag for tag in tags if tag]
            return tags
        return []

    def extract_description(self, upload_details: str) -> str:
        """Extract the video description from the upload details"""
        import re

        match = re.search(r"## 📝 DESCRIPTION\s+(.+?)(?:\n\n##)",
                          upload_details, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    def format_for_console_display(self, upload_details: str) -> str:
        """Format the upload details for clean console display"""
        # Add some visual separation and formatting
        separator = "=" * 80
        return f"\n{separator}\n{upload_details}\n{separator}\n"

    def get_quick_summary(self, upload_details: str) -> Dict[str, str]:
        """Get a quick summary of key upload details"""
        return {
            "filename": self.extract_filename(upload_details),
            "title": self.extract_title(upload_details),
            "tags_count": len(self.extract_tags(upload_details)),
            "description_length": len(self.extract_description(upload_details)),
        }
    
    def _validate_timestamps(self, upload_details: str, max_seconds: int, duration_str: str) -> None:
        """Validate that agent's timestamps don't exceed calculated duration"""
        import re
        
        # Extract all timestamps from the response (format: MM:SS or M:SS or H:MM:SS)
        timestamp_pattern = r'(?:^|\s)(\d{1,2}):([0-5]\d)(?::([0-5]\d))?'
        matches = re.findall(timestamp_pattern, upload_details)
        
        if not matches:
            print("⚠️ No timestamps found in agent response")
            return
        
        max_timestamp = 0
        max_timestamp_str = "0:00"
        invalid_count = 0
        
        for match in matches:
            hours = 0
            minutes = int(match[0])
            seconds = int(match[1])
            
            # Check if H:MM:SS format (match[2] would be seconds, match[1] would be minutes)
            if match[2]:  # H:MM:SS format
                hours = minutes
                minutes = seconds
                seconds = int(match[2])
            
            # Convert to total seconds
            total_seconds = (hours * 3600) + (minutes * 60) + seconds
            
            if total_seconds > max_timestamp:
                max_timestamp = total_seconds
                if hours > 0:
                    max_timestamp_str = f"{hours}:{minutes:02d}:{seconds:02d}"
                else:
                    max_timestamp_str = f"{minutes}:{seconds:02d}"
            
            # Check if exceeds calculated duration
            if total_seconds > max_seconds:
                invalid_count += 1
        
        # Report validation results
        if invalid_count > 0:
            print(f"❌ VALIDATION FAILED: {invalid_count} timestamp(s) exceed calculated duration")
            print(f"   Max timestamp in response: {max_timestamp_str}")
            print(f"   Calculated duration limit: {duration_str}")
            print(f"   Agent should calculate duration from word count!")
        else:
            print(f"✅ VALIDATION PASSED: All timestamps within {duration_str} limit")
            print(f"   Max timestamp found: {max_timestamp_str}")

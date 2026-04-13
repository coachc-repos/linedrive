#!/usr/bin/env python3
"""
YouTube Transcript Storage Module
Stores YouTube transcripts in Azure Data Lake with proper schema for search indexing
"""

import json
import logging
from datetime import datetime, timezone
from azure.storage.filedatalake import DataLakeServiceClient
from azure.identity import DefaultAzureCredential
import os
from typing import Dict, List, Optional


class YouTubeTranscriptStorage:
    def __init__(
        self,
        storage_account_name: str = "linedrivestorage",
        container_name: str = "youtube-transcripts",
    ):
        """Initialize the YouTube transcript storage client"""
        self.storage_account_name = storage_account_name
        self.container_name = container_name
        self.account_url = f"https://{storage_account_name}.dfs.core.windows.net"

        # Use managed identity or Azure CLI credentials
        self.credential = DefaultAzureCredential()
        self.service_client = DataLakeServiceClient(
            account_url=self.account_url, credential=self.credential
        )

        # Get or create the container
        self.file_system_client = self.service_client.get_file_system_client(
            file_system=container_name
        )

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def create_transcript_document(
        self,
        video_id: str,
        video_title: str,
        channel_name: str,
        transcript_text: str,
        channel_url: str = None,
        host: str = None,
        video_description: str = None,
        video_tags: List[str] = None,
        video_duration: int = None,
        publish_date: str = None,
        transcript_segments: List[Dict] = None,
        language: str = "en",
        transcript_source: str = "auto-generated",
        metadata: Dict = None,
    ) -> Dict:
        """
        Create a properly formatted transcript document for storage and indexing

        Args:
            video_id: YouTube video ID (e.g., 'dQw4w9WgXcQ')
            video_title: Title of the video
            channel_name: Name of the YouTube channel
            transcript_text: Full transcript text
            channel_url: URL of the YouTube channel
            host: Host or main speaker (if identifiable)
            video_description: YouTube video description
            video_tags: List of tags/categories
            video_duration: Duration in seconds
            publish_date: When video was published (ISO format)
            transcript_segments: List of transcript segments with timestamps
            language: Language code (ISO 639-1)
            transcript_source: Source of transcript
            metadata: Additional metadata dictionary

        Returns:
            Dict: Properly formatted transcript document
        """

        # Generate video URL from video_id
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # Generate channel URL if not provided
        if not channel_url:
            # This would need to be extracted from YouTube API in real implementation
            channel_url = f"https://www.youtube.com/channel/UNKNOWN"

        # Current timestamp
        created_at = datetime.now(timezone.utc).isoformat()

        document = {
            "video_id": video_id,
            "video_title": video_title,
            "channel_name": channel_name,
            "channel_url": channel_url,
            "video_url": video_url,
            "transcript_text": transcript_text,
            "created_at": created_at,
            "language": language,
            "transcript_source": transcript_source,
        }

        # Add optional fields
        if host:
            document["host"] = host
        if video_description:
            document["video_description"] = video_description
        if video_tags:
            document["video_tags"] = video_tags
        if video_duration:
            document["video_duration"] = video_duration
        if publish_date:
            document["publish_date"] = publish_date
        if transcript_segments:
            document["transcript_segments"] = transcript_segments
        if metadata:
            document["metadata"] = metadata

        return document

    def store_transcript(self, transcript_document: Dict) -> str:
        """
        Store a transcript document in Azure Data Lake

        Args:
            transcript_document: Formatted transcript document

        Returns:
            str: Path where the document was stored
        """
        video_id = transcript_document["video_id"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create filename: videoId_timestamp.json
        filename = f"{video_id}_{timestamp}.json"

        try:
            # Convert document to JSON
            json_content = json.dumps(transcript_document, indent=2, ensure_ascii=False)

            # Upload to Data Lake
            file_client = self.file_system_client.get_file_client(filename)
            file_client.upload_data(json_content.encode("utf-8"), overwrite=True)

            self.logger.info(
                f"Successfully stored transcript for video {video_id} at {filename}"
            )
            return filename

        except Exception as e:
            self.logger.error(
                f"Failed to store transcript for video {video_id}: {str(e)}"
            )
            raise

    def store_transcript_from_scraper_output(
        self, scraper_output_path: str
    ) -> List[str]:
        """
        Convert existing scraper output to proper transcript format and store

        Args:
            scraper_output_path: Path to existing scraper output JSON file

        Returns:
            List[str]: List of filenames where documents were stored
        """
        stored_files = []

        try:
            with open(scraper_output_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle different formats from your scraper
            if isinstance(data, dict):
                # Single video format
                if "video_id" in data or "id" in data:
                    document = self._convert_scraper_format(data)
                    filename = self.store_transcript(document)
                    stored_files.append(filename)
                else:
                    # Multiple videos in dict format
                    for key, video_data in data.items():
                        if isinstance(video_data, dict):
                            document = self._convert_scraper_format(video_data)
                            filename = self.store_transcript(document)
                            stored_files.append(filename)

            elif isinstance(data, list):
                # List of videos
                for video_data in data:
                    if isinstance(video_data, dict):
                        document = self._convert_scraper_format(video_data)
                        filename = self.store_transcript(document)
                        stored_files.append(filename)

            self.logger.info(
                f"Successfully converted and stored {len(stored_files)} transcripts"
            )
            return stored_files

        except Exception as e:
            self.logger.error(f"Failed to convert scraper output: {str(e)}")
            raise

    def _convert_scraper_format(self, scraper_data: Dict) -> Dict:
        """
        Convert scraper output format to standard transcript format

        Args:
            scraper_data: Raw data from YouTube scraper

        Returns:
            Dict: Standardized transcript document
        """
        # Extract video_id from various possible formats
        video_id = scraper_data.get("video_id") or scraper_data.get("id")

        # Extract other fields, adapting to your scraper's output format
        video_title = scraper_data.get("title") or scraper_data.get(
            "video_title", "Unknown Title"
        )
        channel_name = (
            scraper_data.get("channel")
            or scraper_data.get("uploader")
            or scraper_data.get("channel_name", "Unknown Channel")
        )

        # Handle transcript text from different possible keys
        transcript_text = (
            scraper_data.get("transcript")
            or scraper_data.get("transcript_text")
            or scraper_data.get("subtitles")
            or scraper_data.get("enhanced_transcript")
            or ""
        )

        # Handle transcript segments if available
        transcript_segments = scraper_data.get("transcript_segments")

        # Other optional fields
        host = scraper_data.get("host")
        video_description = scraper_data.get("description")
        video_tags = scraper_data.get("tags") or scraper_data.get("categories")
        video_duration = scraper_data.get("duration")

        # Handle publish date
        publish_date = scraper_data.get("upload_date") or scraper_data.get(
            "publish_date"
        )
        if publish_date and isinstance(publish_date, str) and len(publish_date) == 8:
            # Convert YYYYMMDD to ISO format
            try:
                pub_date = datetime.strptime(publish_date, "%Y%m%d")
                publish_date = pub_date.isoformat() + "Z"
            except:
                publish_date = None

        return self.create_transcript_document(
            video_id=video_id,
            video_title=video_title,
            channel_name=channel_name,
            transcript_text=transcript_text,
            host=host,
            video_description=video_description,
            video_tags=video_tags,
            video_duration=video_duration,
            publish_date=publish_date,
            transcript_segments=transcript_segments,
            metadata=scraper_data.get("metadata", {}),
        )


def main():
    """Example usage"""
    storage = YouTubeTranscriptStorage()

    # Example 1: Store a single transcript
    sample_document = storage.create_transcript_document(
        video_id="dQw4w9WgXcQ",
        video_title="Rick Astley - Never Gonna Give You Up (Official Music Video)",
        channel_name="Rick Astley",
        transcript_text="Never gonna give you up, never gonna let you down...",
        channel_url="https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw",
        host="Rick Astley",
        video_description="The official video for Rick Astley's hit song",
        video_tags=["music", "80s", "pop", "rick astley"],
        video_duration=213,
        language="en",
        transcript_source="auto-generated",
    )

    filename = storage.store_transcript(sample_document)
    print(f"Stored sample transcript at: {filename}")

    # Example 2: Convert existing scraper output
    # storage.store_transcript_from_scraper_output("/path/to/your/scraper/output.json")


if __name__ == "__main__":
    main()

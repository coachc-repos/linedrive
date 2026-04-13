#!/usr/bin/env python3
"""
YouTube Transcript Grabber

A utility to fetch transcripts from YouTube videos using the youtube-transcript-api.
Handles various error cases and saves results to JSON format.
"""

from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    CouldNotRetrieveTranscript,
)
import json
import os
from datetime import datetime
from typing import List, Dict, Optional


def fetch_youtube_transcript(
    video_id: str, languages: List[str] = None
) -> Optional[List[Dict]]:
    """
    Fetch transcript for a YouTube video

    Args:
        video_id: YouTube video ID (e.g., 'dQw4w9WgXcQ')
        languages: List of language codes to try (default: ['en'])

    Returns:
        List of transcript entries with 'text', 'start', and 'duration' keys
        None if transcript cannot be retrieved
    """
    if languages is None:
        languages = ["en"]

    try:
        api = YouTubeTranscriptApi()

        # Fetch transcript with specified languages
        transcript = api.fetch(video_id, languages=languages)

        # Convert FetchedTranscriptSnippet objects to dictionaries
        transcript_data = []
        for snippet in transcript:
            if hasattr(snippet, "text") and hasattr(snippet, "start"):
                # FetchedTranscriptSnippet object
                entry = {
                    "text": snippet.text,
                    "start": snippet.start,
                    "duration": getattr(snippet, "duration", 0),
                }
            else:
                # Already a dictionary
                entry = snippet
            transcript_data.append(entry)

        return transcript_data if transcript_data else None

    except TranscriptsDisabled:
        print(f"❌ Transcripts are disabled for video ID: {video_id}")
        return None
    except NoTranscriptFound:
        print(f"❌ No transcript found for video ID: {video_id}")
        return None
    except VideoUnavailable:
        print(f"❌ Video is unavailable: {video_id}")
        return None
    except CouldNotRetrieveTranscript as e:
        print(f"❌ Could not retrieve transcript: {e}")
        return None
    except ValueError as e:
        print(f"❌ Invalid video ID or parameters: {e}")
        return None
    except ConnectionError as e:
        print(f"❌ Network connection error: {e}")
        return None


def save_transcript_to_json(transcript: List[Dict], output_path: str) -> bool:
    """
    Save transcript data to JSON file

    Args:
        transcript: List of transcript entries
        output_path: Path to save the JSON file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Create full readable text from transcript entries
        # Process each entry to ensure we capture all text content
        text_parts = []
        for entry in transcript:
            text_content = entry.get("text", "")
            if isinstance(text_content, str) and text_content.strip():
                # Clean up the text but preserve content
                clean_text = text_content.strip()
                # Remove any potential duplicate spaces but keep the text intact
                clean_text = " ".join(clean_text.split())
                text_parts.append(clean_text)

        # Join all text parts into one continuous string
        full_text = " ".join(text_parts)

        # Debug info
        print(f"📝 Processed {len(text_parts)} text segments into full_text")
        print(f"📏 Full text length: {len(full_text)} characters")

        # Prepare data with metadata
        output_data = {
            "metadata": {
                "fetched_at": datetime.now().isoformat(),
                "total_entries": len(transcript),
                "total_duration": (
                    transcript[-1]["start"] + transcript[-1].get("duration", 0)
                    if transcript
                    else 0
                ),
            },
            "full_text": full_text,
            "transcript": transcript,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)

        print(f"✅ Transcript saved to: {output_path}")
        return True

    except (OSError, IOError) as e:
        print(f"❌ File system error: {e}")
        return False
    except (ValueError, TypeError) as e:
        print(f"❌ JSON encoding error: {e}")
        return False


def print_transcript_summary(transcript: List[Dict], max_entries: int = 5) -> None:
    """Print a summary of the transcript"""
    if not transcript:
        print("❌ No transcript data to display")
        return

    print("\n📊 Transcript Summary:")
    print(f"   Total entries: {len(transcript)}")

    if transcript:
        total_duration = transcript[-1]["start"] + transcript[-1].get("duration", 0)
        print(f"   Total duration: {total_duration:.1f} seconds")

        print(f"\n📋 First {min(max_entries, len(transcript))} entries:")
        for entry in transcript[:max_entries]:
            start_time = entry.get("start", 0)
            text = entry.get("text", "").strip()
            print(f"   {start_time:7.2f}s: {text}")


def main():
    """Main function to demonstrate the transcript grabber"""
    # Example video ID - using a short video that should have transcripts
    video_id = "NgF2G9VItKY"  # A popular video with transcripts enabled

    print(f"🎬 Fetching transcript for video: {video_id}")

    # Fetch transcript
    transcript = fetch_youtube_transcript(video_id, languages=["en", "en-US"])

    if transcript:
        # Print summary
        print_transcript_summary(
            transcript, max_entries=3
        )  # Show only 3 entries for testing

        # Save to file
        output_path = "output/transcript.json"
        if save_transcript_to_json(transcript, output_path):
            print(
                f"\n🎉 Successfully processed transcript with {len(transcript)} entries"
            )
        else:
            print("\n❌ Failed to save transcript")
    else:
        print("\n❌ Could not fetch transcript")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
YouTube Transcript Grabber Menu

Interactive menu interface for fetching YouTube video transcripts
with Azure Data Lake storage integration.
"""

import os
import re
from datetime import datetime
from typing import Optional
from batch_scrapers.common.youtube_transcript_grabber import (
    fetch_youtube_transcript,
    save_transcript_to_json,
)

# Try to import Azure Data Lake uploader
try:
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
    from linedrive_azure.storage.youtube_transcript_storage import (
        YouTubeTranscriptStorage,
    )

    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False


class YouTubeTranscriptMenu:
    """Interactive menu for YouTube transcript operations"""

    def __init__(self):
        """Initialize the YouTube transcript menu"""
        self.settings = {
            "languages": ["en", "en-US"],
            "save_to_azure": False,
        }
        self.azure_available = AZURE_AVAILABLE
        self.last_transcript = None
        self.last_video_id = None

        # Create output directory
        os.makedirs("output", exist_ok=True)

    def show_menu(self):
        """Display the main menu"""
        azure_status = "✅ ON" if self.settings["save_to_azure"] else "❌ OFF"
        languages_str = ", ".join(self.settings["languages"])

        print("\n🎬 YOUTUBE TRANSCRIPT GRABBER")
        print("=" * 60)
        print("Fetch transcripts from YouTube videos with configurable settings")
        print()
        print("⚙️ Current Settings:")
        print("━" * 50)
        print(f"   🌍 Languages: {languages_str}")
        print(f"   ☁️ Azure Data Lake: {azure_status}")
        print()
        print("📋 Menu Options:")
        print("   1: 🎬 Enter YouTube video URL or ID")
        print("   2: 🌍 Change language preferences")
        print("   3: ☁️ Toggle Azure Data Lake saving")
        print("   4: 📊 Show last transcript results")
        print("   5: � View full transcript text")
        print("   6: �📤 Upload last transcript to Azure")
        print("   7: 📁 View saved transcripts")
        print("   0: ❌ Exit")
        print("=" * 60)

    def extract_video_id(self, url_or_id: str) -> Optional[str]:
        """Extract video ID from YouTube URL or validate direct ID"""
        # Remove whitespace
        url_or_id = url_or_id.strip()

        # If it's already a video ID (11 characters, alphanumeric + underscores/hyphens)
        if re.match(r"^[a-zA-Z0-9_-]{11}$", url_or_id):
            return url_or_id

        # Extract from various YouTube URL formats
        patterns = [
            r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})",
            r"(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})",
            r"(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})",
            r"(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})",
        ]

        for pattern in patterns:
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)

        return None

    def change_languages(self):
        """Change language preferences for transcript fetching"""
        print("\n🌍 Language Preferences")
        print("=" * 40)
        print("Current languages:", ", ".join(self.settings["languages"]))
        print()
        print("Common language codes:")
        print("  en, en-US  - English")
        print("  es, es-ES  - Spanish")
        print("  fr, fr-FR  - French")
        print("  de, de-DE  - German")
        print("  it, it-IT  - Italian")
        print("  pt, pt-BR  - Portuguese")
        print("  ja, ja-JP  - Japanese")
        print("  ko, ko-KR  - Korean")
        print("  zh, zh-CN  - Chinese")
        print()

        try:
            new_languages = input(
                "Enter language codes (comma-separated, e.g., 'en,es,fr'): "
            ).strip()
            if new_languages:
                # Parse and clean language codes
                languages = [lang.strip() for lang in new_languages.split(",")]
                languages = [lang for lang in languages if lang]  # Remove empty strings

                if languages:
                    self.settings["languages"] = languages
                    print(f"✅ Languages updated to: {', '.join(languages)}")
                else:
                    print("❌ No valid languages provided")
            else:
                print("💡 Language preferences unchanged")

        except KeyboardInterrupt:
            print("\n💡 Language preferences unchanged")

    def toggle_azure_saving(self):
        """Toggle Azure Data Lake saving on/off"""
        if not self.azure_available:
            print("❌ Azure Data Lake is not available")
            print("💡 Make sure Azure credentials are configured")
            return

        self.settings["save_to_azure"] = not self.settings["save_to_azure"]
        status = "✅ ENABLED" if self.settings["save_to_azure"] else "❌ DISABLED"
        print(f"\n☁️ Azure Data Lake saving: {status}")

    def fetch_transcript(self, video_url_or_id: str):
        """Fetch transcript for a YouTube video"""
        video_id = self.extract_video_id(video_url_or_id)

        if not video_id:
            print("❌ Invalid YouTube URL or video ID")
            print("💡 Please provide a valid YouTube URL or 11-character video ID")
            return

        print(f"\n🔍 Fetching transcript...")
        print("=" * 40)
        print(f"🎬 Video ID: {video_id}")
        print(f"🌍 Languages: {', '.join(self.settings['languages'])}")
        print()

        try:
            # Fetch transcript
            transcript = fetch_youtube_transcript(video_id, self.settings["languages"])

            if transcript:
                self.last_transcript = transcript
                self.last_video_id = video_id

                # Display summary
                total_entries = len(transcript)
                total_duration = (
                    transcript[-1]["start"] + transcript[-1].get("duration", 0)
                    if transcript
                    else 0
                )

                print(f"✅ Transcript fetched successfully!")
                print("=" * 40)
                print(f"📊 Total entries: {total_entries}")
                print(f"⏱️ Total duration: {total_duration:.1f} seconds")

                # Show first few entries
                print(f"\n📋 First {min(3, total_entries)} entries:")
                for entry in transcript[:3]:
                    start_time = entry.get("start", 0)
                    text = entry.get("text", "").strip().replace("\n", " ")
                    print(f"   {start_time:7.2f}s: {text}")

                # Save to local file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"youtube_transcript_{video_id}_{timestamp}.json"
                output_path = os.path.join("output", filename)

                if save_transcript_to_json(transcript, output_path):
                    print(f"\n💾 Saved to: {output_path}")

                # Auto-upload to Azure if enabled
                if self.settings["save_to_azure"] and self.azure_available:
                    print(f"\n☁️ Auto-uploading to Azure Data Lake...")
                    self.upload_to_azure()

            else:
                print("❌ Could not fetch transcript")
                print("💡 The video may not have transcripts available")

        except Exception as e:
            print(f"❌ Error fetching transcript: {e}")
            print("💡 Please check the video ID and try again")

    def upload_to_azure(self):
        """Upload last transcript to Azure Data Lake with proper YouTube transcript schema"""
        if not self.last_transcript:
            print("❌ No transcript to upload")
            print("💡 Fetch a transcript first")
            return

        try:
            print("☁️ Uploading to Azure Data Lake...")

            # Use dedicated YouTube transcript storage
            storage = YouTubeTranscriptStorage()

            # Build full continuous text
            text_parts = []
            for entry in self.last_transcript:
                text_content = entry.get("text", "")
                if isinstance(text_content, str) and text_content.strip():
                    clean_text = text_content.strip()
                    clean_text = " ".join(clean_text.split())
                    text_parts.append(clean_text)

            full_text = " ".join(text_parts)

            # Calculate video duration
            total_duration = (
                self.last_transcript[-1]["start"]
                + self.last_transcript[-1].get("duration", 0)
                if self.last_transcript
                else 0
            )

            # Create the proper transcript document using the helper method
            transcript_document = storage.create_transcript_document(
                video_id=self.last_video_id,
                video_title=f"Video {self.last_video_id}",  # We don't have title from the grabber
                channel_name="Unknown Channel",  # We don't have channel from the grabber
                transcript_text=full_text,
                video_description=f"YouTube video transcript for {self.last_video_id}",
                video_duration=int(total_duration),
                transcript_segments=self.last_transcript,
                language=(
                    self.settings["languages"][0]
                    if self.settings["languages"]
                    else "en"
                ),
            )

            # Store the transcript document
            result_path = storage.store_transcript(transcript_document)

            if result_path:
                print("✅ Upload successful!")
                print("📊 Data uploaded to youtube-transcripts container")
                print(f"📁 Stored at: {result_path}")
                print(f"📄 Full transcript with {len(self.last_transcript)} entries")
                print(f"📝 Continuous text: {len(full_text)} characters")
                print(f"🎬 Video ID: {self.last_video_id}")
                print(f"⏱️ Duration: {total_duration:.1f} seconds")
            else:
                print("❌ Upload failed")
                print("💡 Check Azure connection and permissions")

        except Exception as e:
            print(f"❌ Upload error: {e}")
            print("💡 Please check your Azure connection")

    def show_last_results(self):
        """Display summary of last transcript results"""
        if not self.last_transcript:
            print("\n❌ No transcript results available")
            print("💡 Fetch a transcript first")
            return

        print(f"\n📊 Last Transcript Results")
        print("=" * 40)
        print(f"🎬 Video ID: {self.last_video_id}")
        print(f"📄 Total entries: {len(self.last_transcript)}")

        if self.last_transcript:
            total_duration = self.last_transcript[-1]["start"] + self.last_transcript[
                -1
            ].get("duration", 0)
            print(f"⏱️ Total duration: {total_duration:.1f} seconds")

        print(f"🌍 Languages: {', '.join(self.settings['languages'])}")
        print()

        # Show sample entries
        print("📋 Sample entries:")
        for i, entry in enumerate(self.last_transcript[:5]):
            start_time = entry.get("start", 0)
            text = entry.get("text", "").strip().replace("\n", " ")[:60]
            print(f"   {i+1}. {start_time:7.2f}s: {text}...")

    def view_full_transcript(self):
        """Display the complete transcript in a readable format"""
        if not self.last_transcript:
            print("\n❌ No transcript available")
            print("💡 Fetch a transcript first")
            return

        print(f"\n📜 FULL TRANSCRIPT - Video ID: {self.last_video_id}")
        print("=" * 60)

        total_duration = self.last_transcript[-1]["start"] + self.last_transcript[
            -1
        ].get("duration", 0)
        print(
            f"📊 {len(self.last_transcript)} entries | ⏱️ {total_duration:.1f} seconds total"
        )
        print()

        # Display options
        print("Choose display format:")
        print("1. Timestamped entries (shows each segment with timestamp)")
        print("2. Continuous text (combines all text into paragraphs)")
        print("3. Export to text file")
        print("0. Back to main menu")

        try:
            choice = input("\n👆 Select format (0-3): ").strip()

            if choice == "1":
                self._display_timestamped_transcript()
            elif choice == "2":
                self._display_continuous_transcript()
            elif choice == "3":
                self._export_transcript_to_text()
            elif choice == "0":
                return
            else:
                print("❌ Invalid option")

        except KeyboardInterrupt:
            print("\n💡 Returning to main menu")

    def _display_timestamped_transcript(self):
        """Display transcript with timestamps in pages"""
        entries_per_page = 20
        total_entries = len(self.last_transcript)
        current_page = 0

        while True:
            start_idx = current_page * entries_per_page
            end_idx = min(start_idx + entries_per_page, total_entries)

            print(
                f"\n📝 Timestamped Transcript (Page {current_page + 1}/{(total_entries - 1) // entries_per_page + 1})"
            )
            print("=" * 60)

            for i in range(start_idx, end_idx):
                entry = self.last_transcript[i]
                start_time = entry.get("start", 0)
                duration = entry.get("duration", 0)
                text = entry.get("text", "").strip()

                # Format timestamp as MM:SS
                minutes = int(start_time // 60)
                seconds = int(start_time % 60)
                time_str = f"{minutes:02d}:{seconds:02d}"

                print(f"[{time_str}] {text}")

            # Navigation options
            print("\n" + "=" * 60)
            nav_options = []
            if current_page > 0:
                nav_options.append("p) Previous page")
            if end_idx < total_entries:
                nav_options.append("n) Next page")
            nav_options.append("q) Quit to menu")

            print(" | ".join(nav_options))

            try:
                nav = input("\n👆 Navigate: ").strip().lower()
                if nav == "q":
                    break
                elif nav == "n" and end_idx < total_entries:
                    current_page += 1
                elif nav == "p" and current_page > 0:
                    current_page -= 1
                else:
                    print("❌ Invalid navigation option")
            except KeyboardInterrupt:
                break

    def _display_continuous_transcript(self):
        """Display transcript as continuous text"""
        print(f"\n📖 Continuous Transcript - Video ID: {self.last_video_id}")
        print("=" * 60)

        # Combine all text entries
        full_text = ""
        current_sentence = ""

        for entry in self.last_transcript:
            text = entry.get("text", "").strip()
            current_sentence += " " + text

            # Check if this seems like end of sentence
            if text.endswith((".", "!", "?")) or len(current_sentence) > 200:
                full_text += current_sentence.strip() + "\n\n"
                current_sentence = ""

        # Add any remaining text
        if current_sentence.strip():
            full_text += current_sentence.strip()

        # Display in chunks to avoid overwhelming output
        lines = full_text.split("\n\n")
        lines_per_page = 10
        current_page = 0

        while True:
            start_idx = current_page * lines_per_page
            end_idx = min(start_idx + lines_per_page, len(lines))

            print(f"\nPage {current_page + 1}/{(len(lines) - 1) // lines_per_page + 1}")
            print("-" * 40)

            for i in range(start_idx, end_idx):
                if lines[i].strip():
                    print(lines[i])
                    print()

            # Navigation
            nav_options = []
            if current_page > 0:
                nav_options.append("p) Previous")
            if end_idx < len(lines):
                nav_options.append("n) Next")
            nav_options.append("q) Quit")

            print("-" * 40)
            print(" | ".join(nav_options))

            try:
                nav = input("\n👆 Navigate: ").strip().lower()
                if nav == "q":
                    break
                elif nav == "n" and end_idx < len(lines):
                    current_page += 1
                elif nav == "p" and current_page > 0:
                    current_page -= 1
                else:
                    print("❌ Invalid option")
            except KeyboardInterrupt:
                break

    def _export_transcript_to_text(self):
        """Export transcript to a text file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create both formats
        formats = {
            "timestamped": f"youtube_transcript_{self.last_video_id}_timestamped_{timestamp}.txt",
            "continuous": f"youtube_transcript_{self.last_video_id}_continuous_{timestamp}.txt",
        }

        try:
            for format_type, filename in formats.items():
                output_path = os.path.join("output", filename)

                with open(output_path, "w", encoding="utf-8") as f:
                    if format_type == "timestamped":
                        f.write(
                            f"YouTube Transcript - Video ID: {self.last_video_id}\n"
                        )
                        f.write(f"Generated: {datetime.now().isoformat()}\n")
                        f.write("=" * 60 + "\n\n")

                        for entry in self.last_transcript:
                            start_time = entry.get("start", 0)
                            text = entry.get("text", "").strip()
                            minutes = int(start_time // 60)
                            seconds = int(start_time % 60)
                            f.write(f"[{minutes:02d}:{seconds:02d}] {text}\n")

                    else:  # continuous
                        f.write(
                            f"YouTube Transcript - Video ID: {self.last_video_id}\n"
                        )
                        f.write(f"Generated: {datetime.now().isoformat()}\n")
                        f.write("=" * 60 + "\n\n")

                        current_paragraph = ""
                        for entry in self.last_transcript:
                            text = entry.get("text", "").strip()
                            current_paragraph += " " + text

                            if (
                                text.endswith((".", "!", "?"))
                                or len(current_paragraph) > 200
                            ):
                                f.write(current_paragraph.strip() + "\n\n")
                                current_paragraph = ""

                        if current_paragraph.strip():
                            f.write(current_paragraph.strip() + "\n")

                print(f"✅ Exported {format_type} format: {output_path}")

        except Exception as e:
            print(f"❌ Export failed: {e}")

    def view_saved_transcripts(self):
        """View list of saved transcript files"""
        output_dir = "output"

        if not os.path.exists(output_dir):
            print("\n❌ No output directory found")
            return

        # Find transcript files
        transcript_files = [
            f
            for f in os.listdir(output_dir)
            if f.startswith("youtube_transcript_") and f.endswith(".json")
        ]

        if not transcript_files:
            print("\n❌ No saved transcripts found")
            print(f"💡 Transcripts will be saved in: {output_dir}/")
            return

        print(f"\n📁 Saved Transcripts ({len(transcript_files)} files)")
        print("=" * 50)

        # Sort by modification time (newest first)
        transcript_files.sort(
            key=lambda f: os.path.getmtime(os.path.join(output_dir, f)), reverse=True
        )

        for i, filename in enumerate(transcript_files[:10]):  # Show last 10
            filepath = os.path.join(output_dir, filename)
            try:
                mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                file_size = os.path.getsize(filepath)

                # Extract video ID from filename
                parts = (
                    filename.replace("youtube_transcript_", "")
                    .replace(".json", "")
                    .split("_")
                )
                video_id = parts[0] if parts else "unknown"

                print(
                    f"   {i+1:2d}. {video_id} - {mod_time.strftime('%Y-%m-%d %H:%M')} ({file_size:,} bytes)"
                )

            except Exception as e:
                print(f"   {i+1:2d}. {filename} - Error reading file info: {e}")

    def run(self):
        """Run the YouTube transcript menu"""
        print("🚀 Starting YouTube Transcript Grabber...")

        while True:
            try:
                self.show_menu()
                choice = input("\n👆 Select an option (0-7): ").strip()

                if choice == "0":
                    print("👋 Goodbye! Happy transcript grabbing!")
                    break
                elif choice == "1":
                    video_input = input("\n🎬 Enter YouTube URL or video ID: ").strip()
                    if video_input:
                        self.fetch_transcript(video_input)
                    else:
                        print("💡 No URL or video ID provided")
                elif choice == "2":
                    self.change_languages()
                elif choice == "3":
                    self.toggle_azure_saving()
                elif choice == "4":
                    self.show_last_results()
                elif choice == "5":
                    self.view_full_transcript()
                elif choice == "6":
                    self.upload_to_azure()
                elif choice == "7":
                    self.view_saved_transcripts()
                else:
                    print("❌ Invalid option. Please select 0-7.")

                # Pause for user to read output
                if choice != "0":
                    input("\n⏎ Press Enter to continue...")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("💡 Please try again")
                input("\n⏎ Press Enter to continue...")


if __name__ == "__main__":
    menu = YouTubeTranscriptMenu()
    menu.run()

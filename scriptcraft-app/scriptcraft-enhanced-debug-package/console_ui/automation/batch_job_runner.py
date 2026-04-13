#!/usr/bin/env python3
"""
Batch Job Runner for LineDrive

Runs multiple scraping jobs with lists of parameters for each tool:
- Tournament scraper: Multiple search parameter sets
- URL scraper: Multiple URLs
- YouTube grabber: Multiple video URLs
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class BatchJobRunner:
    """Manages batch processing of multiple scraping jobs"""

    def __init__(self):
        """Initialize the batch job runner"""
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

        # Job results tracking
        self.job_results = {
            "tournament_jobs": [],
            "url_jobs": [],
            "youtube_jobs": [],
            "summary": {
                "start_time": None,
                "end_time": None,
                "total_jobs": 0,
                "successful_jobs": 0,
                "failed_jobs": 0,
            },
        }

    def run_tournament_batch(
        self, parameter_sets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Run multiple tournament searches with different parameter sets

        Args:
            parameter_sets: List of parameter dictionaries for tournament searches
            Example: [
                {"location": "Houston, TX", "age_group": "10U", "radius": 25},
                {"location": "Dallas, TX", "age_group": "12U", "radius": 50}
            ]
        """
        print(f"\n🏆 Starting Tournament Batch Job - {len(parameter_sets)} searches")
        print("=" * 60)

        results = []

        try:
            # Import tournament scraper components
            from batch_scrapers.perfect_game.perfect_game_scraper import (
                PerfectGameScraper,
            )
            from batch_scrapers.perfect_game.filters import FilterBuilder

            scraper = PerfectGameScraper(headless=True, debug=False)

            for i, params in enumerate(parameter_sets, 1):
                print(
                    f"\n📍 Job {i}/{len(parameter_sets)}: {params.get('location', 'Unknown location')}"
                )

                try:
                    # Build filters from parameters
                    filter_builder = FilterBuilder()

                    if "location" in params:
                        # Parse location string "City, State"
                        location = params["location"]
                        if "," in location:
                            city, state = [part.strip() for part in location.split(",")]
                            radius = params.get("radius", 25)
                            filter_builder.set_location(state, city, radius)
                        else:
                            # Default to Texas if only city provided
                            filter_builder.set_location(
                                "TX", location, params.get("radius", 25)
                            )

                    if "age_group" in params:
                        filter_builder.set_age_group(params["age_group"])
                    if "start_date" in params and "end_date" in params:
                        filter_builder.set_date_range(
                            params["start_date"], params["end_date"]
                        )

                    filters = filter_builder.get_filters()

                    # Run search
                    tournaments = scraper.search_tournaments(filters)

                    # Also upload to Azure if enabled in config
                    azure_uploaded = False
                    if params.get("upload_to_azure", False):
                        azure_uploaded = self._upload_tournament_to_azure(
                            tournaments, params
                        )

                    job_result = {
                        "job_number": i,
                        "parameters": params,
                        "success": True,
                        "tournament_count": len(tournaments),
                        "tournaments": tournaments,
                        "azure_uploaded": azure_uploaded,
                        "timestamp": datetime.now().isoformat(),
                    }

                    results.append(job_result)
                    print(f"   ✅ Found {len(tournaments)} tournaments")
                    if azure_uploaded:
                        print("   ☁️ Uploaded to Azure Data Lake")

                except Exception as e:
                    job_result = {
                        "job_number": i,
                        "parameters": params,
                        "success": False,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                    results.append(job_result)
                    print(f"   ❌ Error: {e}")

            # Clean up scraper resources
            if hasattr(scraper, "driver") and scraper.driver:
                scraper.driver.quit()

        except Exception as e:
            print(f"❌ Fatal error in tournament batch: {e}")

        return results

    def run_url_batch(self, url_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Run URL scraping on multiple URLs with different configurations

        Args:
            url_configs: List of URL configuration dictionaries
            Example: [
                {"url": "https://example1.com", "max_depth": 2, "max_pages": 10},
                {"url": "https://example2.com", "max_depth": 1, "max_pages": 5}
            ]
        """
        print(f"\n🌐 Starting URL Batch Job - {len(url_configs)} URLs")
        print("=" * 60)

        results = []

        try:
            # Import URL scraper
            from batch_scrapers.common.url_scraper import URLScraper

            for i, config in enumerate(url_configs, 1):
                url = config.get("url", "")
                print(f"\n🔗 Job {i}/{len(url_configs)}: {url}")

                try:
                    scraper = URLScraper(headless=True, debug=False)

                    # Configure scraping parameters
                    max_depth = config.get("max_depth", 1)
                    max_pages = config.get("max_pages", 10)
                    delay = config.get("delay", 1)

                    # Run scraping
                    scraped_data = scraper.scrape_url_with_subpages(
                        start_url=url,
                        max_depth=max_depth,
                        max_pages=max_pages,
                        delay=delay,
                    )

                    # Also upload to Azure if enabled in config
                    azure_uploaded = False
                    if config.get("upload_to_azure", False):
                        azure_uploaded = self._upload_url_data_to_azure(
                            scraped_data, config
                        )

                    job_result = {
                        "job_number": i,
                        "url": url,
                        "config": config,
                        "success": True,
                        "pages_scraped": len(scraped_data),
                        "data": scraped_data,
                        "azure_uploaded": azure_uploaded,
                        "timestamp": datetime.now().isoformat(),
                    }

                    results.append(job_result)
                    print(f"   ✅ Scraped {len(scraped_data)} pages")
                    if azure_uploaded:
                        print("   ☁️ Uploaded to Azure Data Lake")

                except Exception as e:
                    job_result = {
                        "job_number": i,
                        "url": url,
                        "config": config,
                        "success": False,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                    results.append(job_result)
                    print(f"   ❌ Error: {e}")

        except Exception as e:
            print(f"❌ Fatal error in URL batch: {e}")

        return results

    def run_youtube_batch(
        self, video_configs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Run YouTube transcript grabbing on multiple videos

        Args:
            video_configs: List of video configuration dictionaries
            Example: [
                {"url": "https://youtube.com/watch?v=abc123", "languages": ["en"]},
                {"video_id": "def456", "languages": ["en", "es"]}
            ]
        """
        print(f"\n🎬 Starting YouTube Batch Job - {len(video_configs)} videos")
        print("=" * 60)

        results = []

        try:
            # Import YouTube transcript functions
            from batch_scrapers.common.youtube_transcript_grabber import (
                fetch_youtube_transcript,
                save_transcript_to_json,
            )

            for i, config in enumerate(video_configs, 1):
                video_id = self._extract_video_id(config)
                print(f"\n📺 Job {i}/{len(video_configs)}: {video_id}")

                try:
                    languages = config.get("languages", ["en", "en-US"])

                    # Fetch transcript
                    transcript = fetch_youtube_transcript(video_id, languages)

                    if transcript:
                        # Save transcript to JSON (creates enhanced structure with full_text)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        output_path = (
                            self.output_dir
                            / f"youtube_transcript_{video_id}_{timestamp}.json"
                        )

                        save_transcript_to_json(transcript, str(output_path))

                        # Also upload to Azure if enabled in config
                        azure_uploaded = False
                        if config.get("upload_to_azure", False):
                            azure_uploaded = self._upload_youtube_to_azure(
                                video_id, transcript, config
                            )

                        job_result = {
                            "job_number": i,
                            "video_id": video_id,
                            "config": config,
                            "success": True,
                            "transcript_entries": len(transcript),
                            "output_file": str(output_path),
                            "azure_uploaded": azure_uploaded,
                            "timestamp": datetime.now().isoformat(),
                        }

                        print(f"   ✅ Transcript saved: {len(transcript)} entries")
                        if azure_uploaded:
                            print(f"   ☁️ Uploaded to Azure Data Lake")
                    else:
                        job_result = {
                            "job_number": i,
                            "video_id": video_id,
                            "config": config,
                            "success": False,
                            "error": "No transcript available",
                            "timestamp": datetime.now().isoformat(),
                        }
                        print(f"   ❌ No transcript available")

                    results.append(job_result)

                except Exception as e:
                    job_result = {
                        "job_number": i,
                        "video_id": video_id or "unknown",
                        "config": config,
                        "success": False,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                    results.append(job_result)
                    print(f"   ❌ Error: {e}")

        except Exception as e:
            print(f"❌ Fatal error in YouTube batch: {e}")

        return results

    def _extract_video_id(self, config: Dict[str, Any]) -> Optional[str]:
        """Extract video ID from URL or return direct video_id"""
        if "video_id" in config:
            return config["video_id"]

        if "url" in config:
            url = config["url"]
            # Extract video ID from various YouTube URL formats
            if "youtube.com/watch?v=" in url:
                return url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in url:
                return url.split("youtu.be/")[1].split("?")[0]

        return None

    def _upload_youtube_to_azure(
        self, video_id: str, transcript: List[Dict], config: Dict
    ) -> bool:
        """
        Upload YouTube transcript to Azure Data Lake with enhanced structure

        Args:
            video_id: YouTube video ID
            transcript: Transcript data
            config: Configuration settings

        Returns:
            True if upload successful, False otherwise
        """
        try:
            # Try to import Azure uploader
            sys.path.append(
                os.path.join(
                    os.path.dirname(__file__), "..", "linedrive_azure", "storage"
                )
            )
            from azure_storage import AzureDataLakeUploader

            uploader = AzureDataLakeUploader()

            # Create the same enhanced structure as save_transcript_to_json
            # Build full continuous text
            text_parts = []
            for entry in transcript:
                text_content = entry.get("text", "")
                if isinstance(text_content, str) and text_content.strip():
                    clean_text = text_content.strip()
                    clean_text = " ".join(clean_text.split())
                    text_parts.append(clean_text)

            full_text = " ".join(text_parts)

            # Create enhanced transcript data structure for upload
            transcript_data = {
                "video_id": video_id,
                "metadata": {
                    "fetched_at": datetime.now().isoformat(),
                    "total_entries": len(transcript),
                    "total_duration": (
                        transcript[-1]["start"] + transcript[-1].get("duration", 0)
                        if transcript
                        else 0
                    ),
                    "languages": config.get("languages", ["en"]),
                    "source": "youtube_transcript_batch",
                    "full_text_length": len(full_text),
                    "batch_config": config,
                },
                "full_text": full_text,
                "transcript": transcript,
            }

            # Upload using the raw data method
            result = uploader.upload_raw_data([transcript_data], "youtube_transcripts")

            return bool(result)

        except Exception:
            return False

    def _upload_tournament_to_azure(
        self, tournaments: List[Dict], params: Dict
    ) -> bool:
        """
        Upload tournament data to Azure Data Lake

        Args:
            tournaments: List of tournament dictionaries
            params: Configuration parameters

        Returns:
            bool: True if upload successful, False otherwise
        """
        try:
            # Try to import Azure uploader
            from linedrive_azure.storage import AzureDataLakeUploader

            uploader = AzureDataLakeUploader()

            # Upload using the upload_both_formats method which handles both JSON and CSV
            result = uploader.upload_both_formats(tournaments, run_type="batch")

            return bool(result)

        except Exception:
            return False

    def _upload_url_data_to_azure(self, scraped_data: List[Dict], config: Dict) -> bool:
        """
        Upload URL scraped data to Azure Data Lake

        Args:
            scraped_data: List of scraped page data
            config: Configuration parameters

        Returns:
            bool: True if upload successful, False otherwise
        """
        try:
            # Try to import Azure uploader
            from linedrive_azure.storage import AzureDataLakeUploader

            uploader = AzureDataLakeUploader()

            # Upload using the raw data method for URL scraped content
            result = uploader.upload_raw_data(scraped_data, "url_scraped_data")

            return bool(result)

        except Exception:
            return False

    def save_batch_results(self, job_type: str, results: List[Dict[str, Any]]) -> str:
        """Save batch job results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"batch_{job_type}_results_{timestamp}.json"
        output_path = self.output_dir / filename

        # Update job results
        self.job_results[f"{job_type}_jobs"] = results
        self.job_results["summary"]["total_jobs"] += len(results)
        self.job_results["summary"]["successful_jobs"] += sum(
            1 for r in results if r.get("success", False)
        )
        self.job_results["summary"]["failed_jobs"] += sum(
            1 for r in results if not r.get("success", True)
        )

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "job_type": job_type,
                    "timestamp": timestamp,
                    "total_jobs": len(results),
                    "results": results,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        print(f"\n📄 Results saved to: {output_path}")
        return str(output_path)

    def run_complete_batch(self, batch_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a complete batch job with multiple job types

        Args:
            batch_config: Configuration for all job types
            Example: {
                "tournament_searches": [list of parameter sets],
                "url_scraping": [list of URL configs],
                "youtube_videos": [list of video configs]
            }
        """
        print("\n🚀 STARTING COMPLETE BATCH JOB")
        print("=" * 70)

        self.job_results["summary"]["start_time"] = datetime.now().isoformat()

        # Run tournament searches
        if "tournament_searches" in batch_config:
            tournament_results = self.run_tournament_batch(
                batch_config["tournament_searches"]
            )
            self.job_results["tournament_jobs"] = tournament_results
            if tournament_results:
                self.save_batch_results("tournament", tournament_results)

        # Run URL scraping
        if "url_scraping" in batch_config:
            url_results = self.run_url_batch(batch_config["url_scraping"])
            self.job_results["url_jobs"] = url_results
            if url_results:
                self.save_batch_results("url", url_results)

        # Run YouTube transcript grabbing
        if "youtube_videos" in batch_config:
            youtube_results = self.run_youtube_batch(batch_config["youtube_videos"])
            self.job_results["youtube_jobs"] = youtube_results
            if youtube_results:
                self.save_batch_results("youtube", youtube_results)

        self.job_results["summary"]["end_time"] = datetime.now().isoformat()

        # Save complete batch summary
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_path = self.output_dir / f"batch_complete_summary_{timestamp}.json"

        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(self.job_results, f, indent=2, ensure_ascii=False)

        print(f"\n📊 BATCH JOB COMPLETE")
        print(f"📄 Summary saved to: {summary_path}")
        print(f"✅ Successful jobs: {self.job_results['summary']['successful_jobs']}")
        print(f"❌ Failed jobs: {self.job_results['summary']['failed_jobs']}")
        print(f"📈 Total jobs: {self.job_results['summary']['total_jobs']}")

        return self.job_results


def main():
    """Interactive batch job runner"""
    print("🎯 LineDrive Batch Job Runner")
    print("=" * 50)
    print("Run multiple scraping jobs in batch mode")
    print()
    print("1. Tournament Batch (multiple search parameters)")
    print("2. URL Batch (multiple URLs to scrape)")
    print("3. YouTube Batch (multiple video transcripts)")
    print("4. Complete Batch (all job types from config file)")
    print("5. Load example configurations")
    print("0. Exit")
    print("=" * 50)

    runner = BatchJobRunner()

    while True:
        try:
            choice = input("\n👆 Select batch job type (0-5): ").strip()

            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                run_tournament_batch_interactive(runner)
            elif choice == "2":
                run_url_batch_interactive(runner)
            elif choice == "3":
                run_youtube_batch_interactive(runner)
            elif choice == "4":
                run_complete_batch_interactive(runner)
            elif choice == "5":
                create_example_configs()
            else:
                print("❌ Invalid choice. Please select 0-5.")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def run_tournament_batch_interactive(runner: BatchJobRunner):
    """Interactive tournament batch job setup"""
    print("\n🏆 Tournament Batch Job Setup")
    print("=" * 40)

    # Example parameter sets
    parameter_sets = [
        {"location": "Houston, TX", "age_group": "10U", "radius": 25},
        {"location": "Dallas, TX", "age_group": "12U", "radius": 50},
        {"location": "Austin, TX", "age_group": "14U", "radius": 30},
    ]

    print("Example parameter sets:")
    for i, params in enumerate(parameter_sets, 1):
        print(f"{i}. {params}")

    use_example = input("\nUse example parameter sets? (y/n): ").strip().lower()

    if use_example == "y":
        results = runner.run_tournament_batch(parameter_sets)
        runner.save_batch_results("tournament", results)
    else:
        print("Please create a JSON file with your parameter sets and run again.")


def run_url_batch_interactive(runner: BatchJobRunner):
    """Interactive URL batch job setup"""
    print("\n🌐 URL Batch Job Setup")
    print("=" * 40)

    # Example URL configs
    url_configs = [
        {
            "url": "https://www.perfectgame.org/tournaments",
            "max_depth": 1,
            "max_pages": 5,
        },
        {
            "url": "https://www.usssabaseball.com/tournaments",
            "max_depth": 1,
            "max_pages": 3,
        },
    ]

    print("Example URL configurations:")
    for i, config in enumerate(url_configs, 1):
        print(f"{i}. {config}")

    use_example = input("\nUse example URL configs? (y/n): ").strip().lower()

    if use_example == "y":
        results = runner.run_url_batch(url_configs)
        runner.save_batch_results("url", results)
    else:
        print("Please create a JSON file with your URL configs and run again.")


def run_youtube_batch_interactive(runner: BatchJobRunner):
    """Interactive YouTube batch job setup"""
    print("\n🎬 YouTube Batch Job Setup")
    print("=" * 40)

    # Example video configs
    video_configs = [
        {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "languages": ["en"]},
        {"video_id": "E1rHbyZ03T0", "languages": ["en", "en-US"]},
    ]

    print("Example video configurations:")
    for i, config in enumerate(video_configs, 1):
        print(f"{i}. {config}")

    use_example = input("\nUse example video configs? (y/n): ").strip().lower()

    if use_example == "y":
        results = runner.run_youtube_batch(video_configs)
        runner.save_batch_results("youtube", results)
    else:
        print("Please create a JSON file with your video configs and run again.")


def run_complete_batch_interactive(runner: BatchJobRunner):
    """Interactive complete batch job setup"""
    print("\n🚀 Complete Batch Job Setup")
    print("=" * 40)

    config_file = input("Enter path to batch config JSON file: ").strip()

    # Handle relative paths by making them relative to the project root
    if not os.path.isabs(config_file):
        # Try relative to current directory first
        if not os.path.exists(config_file):
            # Try relative to project root
            project_root = Path(__file__).parent.parent
            config_file = project_root / config_file

    print(f"🔍 Looking for config file: {config_file}")
    print(f"📂 Current working directory: {os.getcwd()}")

    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                batch_config = json.load(f)

            print(f"✅ Config loaded successfully from: {config_file}")
            runner.run_complete_batch(batch_config)
        except Exception as e:
            print(f"❌ Error loading config file: {e}")
    else:
        print("❌ Config file not found. Use option 5 to create examples.")
        print(f"💡 Tried looking in: {config_file}")
        print(
            "💡 Try using the full path or just the filename: batch_config_example.json"
        )


def create_example_configs():
    """Create example configuration files"""
    print("\n📄 Creating Example Configuration Files")
    print("=" * 40)

    # Complete batch config example
    complete_config = {
        "tournament_searches": [
            {"location": "Houston, TX", "age_group": "10U", "radius": 25},
            {"location": "Dallas, TX", "age_group": "12U", "radius": 50},
        ],
        "url_scraping": [
            {
                "url": "https://www.perfectgame.org/tournaments",
                "max_depth": 1,
                "max_pages": 5,
            }
        ],
        "youtube_videos": [{"video_id": "E1rHbyZ03T0", "languages": ["en"]}],
    }

    config_path = "batch_config_example.json"
    with open(config_path, "w") as f:
        json.dump(complete_config, f, indent=2)

    print(f"✅ Example config created: {config_path}")
    print("Edit this file with your actual parameters and run option 4.")


if __name__ == "__main__":
    main()

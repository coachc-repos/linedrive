#!/usr/bin/env python3
"""
DaVinci Resolve API Integration
Automates project creation, timeline setup, and bin organization
"""
import re
import sys
import os
from pathlib import Path


def sanitize_project_name(title):
    """Create a condensed, filesystem-safe project name from script title"""
    # Remove special characters, keep alphanumeric and spaces
    clean = re.sub(r'[^\w\s-]', '', title)
    # Replace spaces with underscores, limit length
    condensed = clean.replace(' ', '_')[:50]
    return condensed if condensed else "AI_Video_Project"


def create_resolve_project(script_title, edl_filename=None):
    """
    Create a new DaVinci Resolve project with automated setup

    Args:
        script_title: Full script title
        edl_filename: Optional EDL file to import

    Returns:
        dict with success status, project details, or error message
    """
    try:
        # Set required environment variables for DaVinci Resolve API
        resolve_script_api = (
            "/Library/Application Support/Blackmagic Design/"
            "DaVinci Resolve/Developer/Scripting"
        )
        resolve_script_lib = (
            "/Applications/DaVinci Resolve/DaVinci Resolve.app/"
            "Contents/Libraries/Fusion/fusionscript.so"
        )

        os.environ["RESOLVE_SCRIPT_API"] = resolve_script_api
        os.environ["RESOLVE_SCRIPT_LIB"] = resolve_script_lib

        # Add modules to Python path
        modules_path = os.path.join(resolve_script_api, "Modules")
        if modules_path not in sys.path:
            sys.path.append(modules_path)

        # Import DaVinci Resolve Python API
        import DaVinciResolveScript as dvr_script

        resolve = dvr_script.scriptapp("Resolve")
        if not resolve:
            return {
                "success": False,
                "error": "DaVinci Resolve is not running. Please start Resolve first."
            }

        project_manager = resolve.GetProjectManager()
        if not project_manager:
            return {
                "success": False,
                "error": "Failed to get Project Manager from Resolve"
            }

        # Create condensed project name
        project_name = sanitize_project_name(script_title)

        # Check if project already exists
        existing_project = project_manager.LoadProject(project_name)
        if existing_project:
            return {
                "success": False,
                "error": f"A project named '{project_name}' already exists. Please delete it from DaVinci Resolve or use a different script title."
            }

        # Create new project
        project = project_manager.CreateProject(project_name)
        if not project:
            return {
                "success": False,
                "error": f"Failed to create project '{project_name}'"
            }

        # Get media pool for bin creation
        media_pool = project.GetMediaPool()
        if not media_pool:
            return {
                "success": False,
                "error": "Failed to get Media Pool from project"
            }

        # Create master bins structure matching template directory
        bins_created = []
        bin_structure = [
            "heygen",
            "intro",
            "aroll",
            "broll",
            "raw",
            "animations",
            "timelines",
            "audio",
            "images"
        ]

        root_folder = media_pool.GetRootFolder()
        bin_mapping = {}  # Store bin objects for media import

        for bin_name in bin_structure:
            new_bin = media_pool.AddSubFolder(root_folder, bin_name)
            if new_bin:
                bins_created.append(bin_name)
                bin_mapping[bin_name] = new_bin

        # Import template media files into corresponding bins
        template_path = Path.home() / "Dev" / "Davinci" / "Template"
        media_imported = {}
        intro_clip = None  # Store AI with Roz v2.mov clip

        if template_path.exists():
            for bin_name in bin_structure:
                bin_folder = template_path / bin_name
                if bin_folder.exists() and bin_folder.is_dir():
                    # Get all media files directly in this bin folder
                    media_files = []
                    for ext in ['*.mp4', '*.mov', '*.avi', '*.mkv',
                                '*.mp3', '*.wav', '*.aac',
                                '*.jpg', '*.png', '*.tiff']:
                        media_files.extend(bin_folder.glob(ext))

                    if media_files and bin_name in bin_mapping:
                        # Convert paths to strings
                        file_paths = [str(f) for f in media_files]

                        # Import into corresponding bin
                        imported = media_pool.ImportMedia(file_paths)
                        if imported:
                            # Move imported clips to correct bin
                            target_bin = bin_mapping[bin_name]
                            for clip in imported:
                                media_pool.MoveClips([clip], target_bin)

                                # Check if this is the intro clip we need for timeline
                                if bin_name == "intro" and "AI with Roz v2.mov" in str(file_paths):
                                    clip_name = clip.GetName()
                                    if "AI with Roz v2" in clip_name:
                                        intro_clip = clip

                            media_imported[bin_name] = len(imported)

                    # Handle subdirectories for heygen bin
                    if bin_name == "heygen":
                        subdirs = [d for d in bin_folder.iterdir()
                                   if d.is_dir()]
                        for subdir in subdirs:
                            # Create sub-bin
                            sub_bin_name = subdir.name
                            sub_bin = media_pool.AddSubFolder(
                                bin_mapping[bin_name], sub_bin_name)

                            if sub_bin:
                                bins_created.append(
                                    f"{bin_name}/{sub_bin_name}")

                                # Get all media files in subdirectory
                                sub_media_files = []
                                for ext in ['*.mp4', '*.mov', '*.avi', '*.mkv',
                                            '*.mp3', '*.wav', '*.aac',
                                            '*.jpg', '*.png', '*.tiff']:
                                    sub_media_files.extend(subdir.glob(ext))

                                if sub_media_files:
                                    sub_file_paths = [str(f)
                                                      for f in sub_media_files]

                                    # Import into sub-bin
                                    sub_imported = media_pool.ImportMedia(
                                        sub_file_paths)
                                    if sub_imported:
                                        # Move imported clips to sub-bin
                                        for clip in sub_imported:
                                            media_pool.MoveClips(
                                                [clip], sub_bin)

                                        # Track imported media count
                                        sub_key = f"{bin_name}/{sub_bin_name}"
                                        media_imported[sub_key] = len(
                                            sub_imported)

        # Set current folder to timelines bin before creating timeline
        if "timelines" in bin_mapping:
            media_pool.SetCurrentFolder(bin_mapping["timelines"])

        # Create timeline named after script title
        timeline_name = script_title
        timeline = media_pool.CreateEmptyTimeline(timeline_name)
        if not timeline:
            return {
                "success": False,
                "error": f"Failed to create timeline '{timeline_name}'"
            }

        # Add intro clip to timeline if found
        if intro_clip:
            media_pool.AppendToTimeline([intro_clip])

        # Set the timeline as current
        project.SetCurrentTimeline(timeline)

        # Import EDL file if provided
        edl_timeline = None
        if edl_filename:
            edl_path = Path(edl_filename)
            print(f"🎬 Attempting to import EDL from: {edl_path}")
            print(f"📁 EDL file exists: {edl_path.exists()}")

            if edl_path.exists():
                try:
                    # Set current folder to timelines bin before importing
                    if "timelines" in bin_mapping:
                        print(f"📁 Setting current folder to timelines bin")
                        media_pool.SetCurrentFolder(bin_mapping["timelines"])

                    print(f"�📥 Importing EDL timeline...")
                    # Try ImportTimelineFromFile method
                    edl_timeline = media_pool.ImportTimelineFromFile(
                        str(edl_path)
                    )

                    if edl_timeline:
                        print(
                            f"✅ EDL timeline imported: {edl_timeline.GetName()}")
                        bins_created.append("EDL Timeline Imported")
                    else:
                        # If ImportTimelineFromFile doesn't work, try CreateTimelineFromClips
                        print(
                            f"⚠️ ImportTimelineFromFile returned None, trying alternative...")
                        print(
                            f"⚠️ EDL import via API not supported - markers must be added manually")

                except Exception as edl_error:
                    # Don't fail the whole operation if EDL import fails
                    print(f"⚠️ Warning: Failed to import EDL: {edl_error}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"❌ EDL file not found at path: {edl_path}")

        result_data = {
            "success": True,
            "project_name": project_name,
            "timeline_name": timeline_name,
            "bins_created": bins_created,
            "media_imported": media_imported,
            "message": "Project created successfully!"
        }

        # Add EDL import status if attempted
        if edl_filename:
            if edl_timeline:
                result_data["edl_imported"] = True
                result_data["edl_timeline_name"] = edl_timeline.GetName()
                result_data["edl_message"] = "EDL timeline imported successfully"
            else:
                result_data["edl_imported"] = False
                result_data["edl_message"] = (
                    "EDL created but not imported automatically. "
                    "DaVinci Resolve API doesn't support marker-only EDL import. "
                    "You can manually add markers by importing the EDL file "
                    "or copying markers from the EDL tab."
                )

        return result_data

    except ImportError:
        return {
            "success": False,
            "error": "DaVinci Resolve Python API not found. Please ensure Resolve is installed and Python API is configured."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }


def create_resolve_project_with_videos(
    script_title,
    edl_filename=None,
    aroll_folder=None,
    sorted_video_files=None
):
    """
    Create a new DaVinci Resolve project with aRoll videos added to timeline

    Args:
        script_title: Full script title
        edl_filename: Optional EDL file to import
        aroll_folder: Path to folder containing aRoll videos
        sorted_video_files: List of video filenames in desired timeline order

    Returns:
        dict with success status, project details, videos added, or error
    """
    print("\n" + "="*80)
    print("🎬 CREATE DAVINCI PROJECT WITH VIDEOS")
    print("="*80)
    print(f"📝 Script title: {script_title}")
    print(f"📁 aRoll folder: {aroll_folder}")
    print(
        f"🎥 Videos to add: {len(sorted_video_files) if sorted_video_files else 0}")
    if sorted_video_files:
        for i, v in enumerate(sorted_video_files, 1):
            print(f"   {i}. {v}")

    try:
        # First create the base project
        print("\n📦 Creating base project...")
        base_result = create_resolve_project(script_title, edl_filename)

        if not base_result.get("success"):
            print("❌ Base project creation failed")
            return base_result

        print("✅ Base project created")

        # If no videos to add, return base result
        if not aroll_folder or not sorted_video_files:
            print("⚠️ No videos to add - returning base result")
            return base_result

        print(f"\n🎥 Processing {len(sorted_video_files)} videos...")

        # Import DaVinci Resolve Python API
        resolve_script_api = (
            "/Library/Application Support/Blackmagic Design/"
            "DaVinci Resolve/Developer/Scripting"
        )
        modules_path = os.path.join(resolve_script_api, "Modules")
        if modules_path not in sys.path:
            sys.path.append(modules_path)

        import DaVinciResolveScript as dvr_script

        print("🔌 Connecting to DaVinci Resolve...")
        resolve = dvr_script.scriptapp("Resolve")
        if not resolve:
            print("❌ Could not connect to Resolve")
            base_result["warning"] = "Could not add videos - Resolve not accessible"
            return base_result

        print("✅ Connected to Resolve")

        project_manager = resolve.GetProjectManager()
        project_name = sanitize_project_name(script_title)

        print(f"📂 Loading project: {project_name}")
        project = project_manager.LoadProject(project_name)

        if not project:
            print(f"❌ Could not load project: {project_name}")
            base_result["warning"] = "Could not load project to add videos"
            return base_result

        print(f"✅ Project loaded: {project_name}")

        print("🎬 Getting media pool...")
        media_pool = project.GetMediaPool()
        if not media_pool:
            print("❌ Could not get media pool")
            base_result["warning"] = "Could not get media pool to add videos"
            return base_result

        print("✅ Media pool ready")

        # Import video files to aRoll bin
        root_folder = media_pool.GetRootFolder()
        aroll_bin = None

        print("📁 Looking for aroll bin...")
        # Find aroll bin
        for subfolder in root_folder.GetSubFolders().values():
            print(f"   Found bin: {subfolder.GetName()}")
            if subfolder.GetName() == "aroll":
                aroll_bin = subfolder
                break

        if not aroll_bin:
            print("❌ Could not find aroll bin")
            base_result["warning"] = "Could not find aroll bin"
            return base_result

        print("✅ Found aroll bin")

        # Set current folder to aRoll bin
        media_pool.SetCurrentFolder(aroll_bin)
        print("✅ Set current folder to aRoll bin")

        # Import all videos
        print(
            f"📦 Building video paths from {len(sorted_video_files)} files...")
        video_paths = [
            os.path.join(aroll_folder, filename)
            for filename in sorted_video_files
        ]

        # Filter to only existing files
        existing_paths = [p for p in video_paths if os.path.exists(p)]
        print(f"✅ Found {len(existing_paths)} existing video files")

        if not existing_paths:
            print("❌ No video files found to import")
            base_result["warning"] = "No video files found to import"
            return base_result

        # Import video files
        print("📥 Importing videos to media pool...")
        storage = resolve.GetMediaStorage()
        imported_clips = storage.AddItemsToMediaPool(existing_paths)

        if not imported_clips:
            print("❌ Failed to import video files to media pool")
            base_result["warning"] = "Failed to import video files to media pool"
            return base_result

        print(
            f"✅ Imported {len(imported_clips) if imported_clips else 0} clips")

        # Get the main timeline
        # Use the original script title (not sanitized) since timeline was created with it
        timeline_name = script_title  # NOT sanitize_project_name(script_title)
        print(f"🔍 Looking for timeline: {timeline_name}")
        print(f"📊 Project has {project.GetTimelineCount()} timeline(s)")
        timeline = None

        # Find timeline by name
        for i in range(project.GetTimelineCount()):
            tl = project.GetTimelineByIndex(i + 1)
            if tl:
                tl_name = tl.GetName()
                print(f"   Timeline {i+1}: {tl_name}")
                if tl_name == timeline_name:
                    timeline = tl
                    print(f"✅ Found matching timeline: {timeline_name}")
                    break

        if not timeline:
            print(f"❌ Could not find timeline matching: {timeline_name}")
            base_result["warning"] = "Could not find main timeline"
            return base_result

        # Set timeline as current
        project.SetCurrentTimeline(timeline)

        # WORKAROUND: AppendToTimeline doesn't work with existing content
        # We need to clear the timeline first, then add all videos in order
        print(f"\n🔧 Clearing existing timeline content...")

        # Get all items in all tracks
        video_track_items = timeline.GetItemListInTrack("video", 1)
        audio_track_items = timeline.GetItemListInTrack("audio", 1)

        total_items = len(video_track_items) + len(audio_track_items)
        print(
            f"   Found {len(video_track_items)} video items, {len(audio_track_items)} audio items")

        # Delete all existing items from both tracks
        if video_track_items:
            print(f"   Removing {len(video_track_items)} video items...")
            timeline.DeleteClips(video_track_items)

        if audio_track_items:
            print(f"   Removing {len(audio_track_items)} audio items...")
            timeline.DeleteClips(audio_track_items)

        if total_items > 0:
            print(f"   ✅ Cleared timeline (removed {total_items} items)")

        # Get clips from aRoll bin
        # Note: GetClipList() returns a list of MediaPoolItem objects
        aroll_clips = aroll_bin.GetClipList()

        if not aroll_clips:
            base_result["warning"] = "No clips found in aRoll bin after import"
            return base_result

        print(f"\n🔍 DEBUG: Found {len(aroll_clips)} clips in aRoll bin")
        print("🔍 DEBUG: Clip names in bin:")
        for clip in aroll_clips:
            clip_name = clip.GetName()
            print(f"   - {clip_name}")

        # Get intro video from Intro bin
        intro_bin = None
        for subfolder in root_folder.GetSubFolders().values():
            if subfolder.GetName() == "intro":
                intro_bin = subfolder
                break

        intro_clip = None
        if intro_bin:
            intro_clips = intro_bin.GetClipList()
            print(f"\n🔍 Looking for intro video in intro bin...")
            print(f"   Found {len(intro_clips)} clips in Intro bin")

            # Look for "AI with Roz v2.mov"
            for clip in intro_clips:
                clip_name = clip.GetName()
                print(f"   - {clip_name}")
                if "AI with Roz v2" in clip_name or "AI_with_Roz_v2" in clip_name:
                    intro_clip = clip
                    print(f"   ✅ Found intro video: {clip_name}")
                    break

            if not intro_clip:
                print(f"   ⚠️ Intro video 'AI with Roz v2.mov' not found in Intro bin")

        # Create a mapping of clip name to clip object
        clip_map = {}
        for clip in aroll_clips:
            clip_name = clip.GetName()
            clip_map[clip_name] = clip

        # Build list of clips in sorted order (intro first, then aRoll videos)
        clips_to_add = []

        # Add intro video first if found
        if intro_clip:
            clips_to_add.append(intro_clip)
            print(f"\n📺 Intro video will be added first")

        for filename in sorted_video_files:
            print(f"\n🔍 DEBUG: Matching: {filename}")

            # Try to match clip by filename (without extension)
            clip_name_base = os.path.splitext(filename)[0]
            print(f"   Base name: {clip_name_base}")

            # Try exact match first
            clip = None
            if filename in clip_map:
                print(f"   ✅ Found exact match: {filename}")
                clip = clip_map[filename]
            elif clip_name_base in clip_map:
                print(f"   ✅ Found base name match: {clip_name_base}")
                clip = clip_map[clip_name_base]
            else:
                # Try partial match
                for name, clip_obj in clip_map.items():
                    if clip_name_base in name or name in clip_name_base:
                        print(f"   ✅ Found partial match: {name}")
                        clip = clip_obj
                        break

                if not clip:
                    print(f"   ❌ No match found for {filename}")

            if clip:
                clips_to_add.append(clip)

        print(f"\n� Prepared {len(clips_to_add)} clips to add to timeline")

        # Verify timeline is empty
        current_items = timeline.GetItemListInTrack("video", 1)
        print(f"🔍 Current timeline items: {len(current_items)}")

        if clips_to_add:
            # Skip Method 1 (AppendToTimeline) and go directly to Method 2
            # Method 1 consistently fails with [None] results on empty timelines
            print(f"\n🎬 Creating new timeline from clips...")
            print(f"   (Skipping AppendToTimeline - known to fail on cleared timelines)")

            # Delete the current empty timeline
            media_pool.DeleteTimelines([timeline])

            # Create a new timeline from the clips
            timeline_name = sanitize_project_name(script_title)
            new_timeline = media_pool.CreateTimelineFromClips(
                timeline_name,
                clips_to_add
            )

            if new_timeline:
                print(
                    f"   ✅ Created new timeline with {len(clips_to_add)} clips!")
                videos_added = sorted_video_files
                timeline = new_timeline
                project.SetCurrentTimeline(timeline)
            else:
                print(f"   ❌ CreateTimelineFromClips failed")
                print(f"\n⚠️ DaVinci Resolve API limitation detected")
                print(f"   Possible causes:")
                print(f"   1. 'External scripting using' not enabled in Preferences")
                print(f"   2. Timeline is locked or has restrictions")
                print(f"   3. Clips are in unsupported format")
                print(f"\n📝 Manual workaround:")
                print(f"   1. Open DaVinci Resolve")
                print(
                    f"   2. Go to project '{sanitize_project_name(script_title)}'")
                print(f"   3. Drag clips from aRoll bin to timeline manually")

        # Final verification
        final_items = timeline.GetItemListInTrack("video", 1)
        print(f"\n🔍 Final timeline items: {len(final_items)}")

        # Build list of what was added
        videos_list = []
        if intro_clip and len(final_items) > 0:
            videos_list.append("AI with Roz v2.mov (intro)")

        if len(final_items) > (1 if intro_clip else 0):
            videos_list.extend(sorted_video_files)

        videos_added = videos_list if len(final_items) > 0 else []

        # Update result with video info
        base_result["videos_added"] = videos_added
        base_result["videos_count"] = len(videos_added)

        if intro_clip:
            base_result["message"] = (
                f"Project created with intro + {len(sorted_video_files)} "
                f"aRoll videos in timeline"
            )
        else:
            base_result["message"] = (
                f"Project created with {len(videos_added)} videos in timeline"
            )

        return base_result

    except Exception as e:
        # Return base result with warning if video addition fails
        if 'base_result' in locals():
            base_result["warning"] = f"Videos not added: {str(e)}"
            return base_result
        return {
            "success": False,
            "error": f"Failed to create project with videos: {str(e)}"
        }


if __name__ == "__main__":
    # Test the API
    print("🎬 Testing DaVinci Resolve API...")
    result = create_resolve_project("Test AI Video Project", None)
    print(f"Result: {result}")

#!/usr/bin/env python3
"""
DaVinci Resolve API Integration
Automates project creation, timeline setup, and bin organization
"""
import re
import sys
import os
import logging
from pathlib import Path

logger = logging.getLogger("davinci_resolve_api")
if not logger.handlers and not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger.setLevel(logging.INFO)


def _log(msg):
    """Log to both logger (Flask captures) and stdout (flushed)."""
    try:
        logger.info(msg)
    except Exception:
        pass
    try:
        print(msg, flush=True)
    except Exception:
        pass


def sanitize_project_name(title):
    """Create a condensed, filesystem-safe project name from script title"""
    # Remove special characters, keep alphanumeric and spaces
    clean = re.sub(r'[^\w\s-]', '', title)
    # Replace spaces with underscores, limit length
    condensed = clean.replace(' ', '_')[:50]
    return condensed if condensed else "AI_Video_Project"


def _collect_media_paths(folder, extensions):
    """Return sorted existing media paths under folder for given extensions."""
    if not folder:
        return []
    try:
        root = Path(folder)
        if not root.exists() or not root.is_dir():
            return []
        exts = {e.lower() for e in extensions}
        files = [p for p in root.rglob('*') if p.is_file() and p.suffix.lower() in exts]
        files.sort(key=lambda p: p.name.lower())
        return [str(p) for p in files]
    except Exception:
        return []


def _import_media_to_bin(resolve, media_pool, bin_mapping, bin_name, file_paths):
    """Import files directly into a target bin."""
    if not file_paths:
        return 0
    target_bin = bin_mapping.get(bin_name)
    if not target_bin:
        return 0

    # Critical: set current folder first so imported media lands in the intended bin,
    # rather than whatever folder was active previously (e.g. heygen/Transition_Clips).
    try:
        media_pool.SetCurrentFolder(target_bin)
    except Exception:
        pass

    imported = media_pool.ImportMedia(file_paths)
    if imported:
        return len(imported)

    # Fallback path for environments where ImportMedia may be flaky.
    storage = resolve.GetMediaStorage()
    if not storage:
        return 0
    imported = storage.AddItemsToMediaPool(file_paths)
    if not imported:
        return 0
    return len(imported)


def _generate_subtitles_from_audio(timeline):
    """Try to generate subtitles from timeline audio via Resolve scripting API."""
    if not timeline:
        return {
            "attempted": True,
            "success": False,
            "message": "No active timeline available for subtitle generation",
        }

    # Try multiple known/possible API signatures for compatibility across versions.
    attempts = [
        ("CreateSubtitlesFromAudio({})", lambda: timeline.CreateSubtitlesFromAudio({})),
        ("CreateSubtitlesFromAudio()", lambda: timeline.CreateSubtitlesFromAudio()),
        ("GenerateSubtitlesFromAudio({})", lambda: timeline.GenerateSubtitlesFromAudio({})),
        ("GenerateSubtitlesFromAudio()", lambda: timeline.GenerateSubtitlesFromAudio()),
    ]

    for label, fn in attempts:
        try:
            result = fn()
            if result is None:
                continue
            if isinstance(result, bool):
                if result:
                    return {
                        "attempted": True,
                        "success": True,
                        "message": f"Subtitles generated via {label}",
                    }
                continue
            return {
                "attempted": True,
                "success": True,
                "message": f"Subtitles generated via {label}",
            }
        except Exception:
            continue

    return {
        "attempted": True,
        "success": False,
        "message": (
            "Could not auto-generate subtitles via scripting API. "
            "Your Resolve version may require manual Timeline > AI Tools > Create Subtitles from Audio."
        ),
    }


def _try_set_track_color(timeline, track_type, track_index, color):
    """Try several method names / color casings to set a track's color.
    Returns True if any attempt succeeds."""
    if not timeline:
        return False
    method_names = ("SetTrackColor", "SetTrackColour")
    color_variants = (color, color.lower(), color.upper(), color.capitalize())
    seen = set()
    color_variants = tuple(c for c in color_variants if not (c in seen or seen.add(c)))
    last_err = None
    for mname in method_names:
        fn = getattr(timeline, mname, None)
        if not callable(fn):
            continue
        for cval in color_variants:
            try:
                res = fn(track_type, track_index, cval)
                if res:
                    _log(f"      \u21b3 {mname}('{track_type}', {track_index}, '{cval}') → True")
                    return True
                else:
                    _log(f"      \u21b3 {mname}('{track_type}', {track_index}, '{cval}') → False")
            except Exception as err:
                last_err = err
    if last_err:
        _log(f"      \u21b3 last error: {last_err}")
    return False


def _setup_video_tracks(timeline):
    """
    Configure the project's video track layout:
        V1 = aroll       (Yellow)
        V2 = adjustment  (Lime)
        V3 = broll       (Teal)
        V4 = animations  (Pink)
    Adds tracks if missing, renames and colors each one.
    Returns a dict {track_index: track_name} for what was set.
    """
    desired = [
        (1, "aroll", "Yellow"),
        (2, "adjustment", "Lime"),
        (3, "broll", "Teal"),
        (4, "animations", "Pink"),
    ]
    if not timeline:
        return {}

    # Diagnostic: log which track-related methods are exposed (one-time per call)
    try:
        methods = [m for m in dir(timeline) if "track" in m.lower() or "color" in m.lower()]
        _log(f"   🔬 Timeline track/color methods: {methods}")
    except Exception:
        pass

    try:
        current_count = int(timeline.GetTrackCount("video") or 1)
    except Exception:
        current_count = 1

    # Add any missing tracks up to V4.
    while current_count < 4:
        try:
            timeline.AddTrack("video")
            current_count += 1
            _log(f"   ➕ Added video track V{current_count}")
        except Exception as add_err:
            _log(f"   ⚠️ Could not add video track V{current_count + 1}: {add_err}")
            break

    applied = {}
    for idx, name, color in desired:
        if idx > current_count:
            continue
        try:
            ok = timeline.SetTrackName("video", idx, name)
            if ok:
                applied[idx] = name
                _log(f"   🏷️  V{idx} → '{name}'")
            else:
                _log(f"   ⚠️ SetTrackName returned False for V{idx} → '{name}'")
        except Exception as name_err:
            _log(f"   ⚠️ SetTrackName failed for V{idx} → '{name}': {name_err}")
        ok_c = _try_set_track_color(timeline, "video", idx, color)
        if ok_c:
            _log(f"   🎨 V{idx} color → {color}")
        else:
            _log(f"   ⚠️ Could not set V{idx} color → {color} (API may not support it)")
    return applied


def _setup_audio_tracks(timeline):
    """
    Configure the project's audio track layout:
        A1 = aroll sound       (Orange)
        A2 = background sound  (Green)
        A3 = sound effects     (Purple)
    Adds tracks if missing, renames and colors each one.
    Returns a dict {track_index: track_name} for what was set.
    """
    desired = [
        (1, "aroll sound", "Orange"),
        (2, "background sound", "Green"),
        (3, "sound effects", "Purple"),
    ]
    if not timeline:
        return {}

    try:
        current_count = int(timeline.GetTrackCount("audio") or 1)
    except Exception:
        current_count = 1

    while current_count < 3:
        try:
            timeline.AddTrack("audio")
            current_count += 1
            _log(f"   ➕ Added audio track A{current_count}")
        except Exception as add_err:
            _log(f"   ⚠️ Could not add audio track A{current_count + 1}: {add_err}")
            break

    applied = {}
    for idx, name, color in desired:
        if idx > current_count:
            continue
        try:
            ok = timeline.SetTrackName("audio", idx, name)
            if ok:
                applied[idx] = name
                _log(f"   🏷️  A{idx} → '{name}'")
            else:
                _log(f"   ⚠️ SetTrackName returned False for A{idx} → '{name}'")
        except Exception as name_err:
            _log(f"   ⚠️ SetTrackName failed for A{idx} → '{name}': {name_err}")
        ok_c = _try_set_track_color(timeline, "audio", idx, color)
        if ok_c:
            _log(f"   🎨 A{idx} color → {color}")
        else:
            _log(f"   ⚠️ Could not set A{idx} color → {color} (API may not support it)")
    return applied


def _add_adjustment_clips_to_v2(media_pool, timeline, source_bin, count=3):
    """
    Place `count` adjustment-layer-style clips onto video track V2
    ('adjustment'), evenly spaced across the timeline duration.

    Why this approach:
      - Resolve's scripting API has NO method to set the destination track
        for `Insert*IntoTimeline()` calls. Locking V1 only makes the call
        refuse silently — it never redirects to V2.
      - The ONLY reliable per-track placement is `MediaPool.AppendToTimeline()`
        with `clip_info["trackIndex"]`. This is what we use here, mirroring
        the proven pattern used by `_add_broll_clips_above_aroll` (V3) and
        `_add_background_audio_clips` (A2).

    We append a short slice of an existing media-pool clip (typically the
    first aRoll video) onto V2 at each target frame, then convert each
    placed timeline item into a Fusion clip via `CreateFusionClip([item])`
    so it behaves like an empty adjustment / Fusion composition over the
    tracks below it.

    Returns: {attempted, success, count, message, clips}
    """
    if not timeline:
        return {"attempted": False, "success": False, "count": 0,
                "message": "No timeline", "clips": []}
    if not media_pool:
        return {"attempted": False, "success": False, "count": 0,
                "message": "No media pool", "clips": []}

    # ------------------------------------------------------------------
    # Find a usable media-pool item to anchor the V2 clip onto.
    # Prefer the supplied source_bin (typically the aRoll bin); fall back
    # to scanning all subfolders for any video clip.
    # ------------------------------------------------------------------
    anchor_clip = None
    try:
        if source_bin:
            for c in (source_bin.GetClipList() or []):
                anchor_clip = c
                break
    except Exception:
        anchor_clip = None
    if anchor_clip is None:
        try:
            root = media_pool.GetRootFolder()
            for sub in (root.GetSubFolders() or {}).values():
                for c in (sub.GetClipList() or []):
                    anchor_clip = c
                    break
                if anchor_clip:
                    break
        except Exception:
            pass
    if anchor_clip is None:
        return {"attempted": True, "success": False, "count": 0,
                "message": "No media-pool clip available to anchor V2 adjustment",
                "clips": []}

    # Compute timeline span.
    try:
        start_frame = int(timeline.GetStartFrame())
    except Exception:
        start_frame = 0
    try:
        end_frame = int(timeline.GetEndFrame())
    except Exception:
        end_frame = 0
    if end_frame <= start_frame:
        try:
            v1_items = timeline.GetItemListInTrack("video", 1) or []
            for item in v1_items:
                try:
                    e = int(item.GetEnd())
                    if e > end_frame:
                        end_frame = e
                except Exception:
                    continue
        except Exception:
            pass

    span = max(0, end_frame - start_frame)
    if span <= 0 or count <= 0:
        return {"attempted": True, "success": False, "count": 0,
                "message": f"Empty timeline span ({start_frame}..{end_frame})",
                "clips": []}

    fps = 24
    try:
        fps_val = timeline.GetSetting("timelineFrameRate")
        if fps_val:
            fps = int(round(float(fps_val)))
    except Exception:
        pass

    # Ensure V2 exists.
    try:
        vc = int(timeline.GetTrackCount("video") or 1)
    except Exception:
        vc = 1
    while vc < 2:
        try:
            timeline.AddTrack("video")
            vc += 1
        except Exception:
            break

    # Each adjustment clip spans its full segment (so V2 is fully covered
    # by adjustment clips back-to-back, which is what an "adjustment
    # layer" pattern looks like in a timeline).
    segment = max(1, span // count)

    # Source-clip duration (for clamping).
    src_dur = 0
    try:
        src_dur = int(anchor_clip.GetClipProperty("Frames") or 0)
    except Exception:
        src_dur = 0
    if src_dur <= 0:
        src_dur = segment  # assume long enough

    _log(f"\n✨ Placing {count} adjustment clip(s) on V2 via AppendToTimeline "
         f"(span {start_frame}..{end_frame} @ {fps}fps, segment {segment}f, "
         f"anchor={anchor_clip.GetName()})")

    appended = []
    placed_items = []
    for i in range(count):
        record_frame = start_frame + i * segment
        clip_len = min(segment, src_dur)
        clip_info = {
            "mediaPoolItem": anchor_clip,
            "trackIndex": 2,        # V2 = adjustment
            "mediaType": 1,         # 1 = video
            "startFrame": 0,
            "endFrame": max(1, clip_len - 1),
            "recordFrame": record_frame,
        }
        try:
            v2_before = {id(it) for it in (timeline.GetItemListInTrack("video", 2) or [])}
            result = media_pool.AppendToTimeline([clip_info])
        except Exception as ap_err:
            _log(f"   ❌ AppendToTimeline V2 #{i+1} raised: {ap_err}")
            continue
        if not result:
            _log(f"   ⚠️ AppendToTimeline V2 #{i+1} @ frame {record_frame} returned empty")
            continue

        # Identify the newly-placed item on V2 so we can convert it to a
        # Fusion clip (adjustment-layer behaviour).
        try:
            v2_after = timeline.GetItemListInTrack("video", 2) or []
            new_items = [it for it in v2_after if id(it) not in v2_before]
        except Exception:
            new_items = []

        new_item = new_items[0] if new_items else None
        if new_item:
            placed_items.append(new_item)
            try:
                new_item.SetClipColor("Teal")
            except Exception:
                pass
            try:
                new_item.SetName(f"Adjustment {i+1}")
            except Exception:
                pass

        appended.append(f"adjustment_{i+1}")
        _log(f"   ✅ V2 #{i+1} placed @ frame {record_frame} (+{clip_len}f)")

    # Convert all placed V2 items to a single Fusion clip so they act
    # like an adjustment layer (empty Fusion comp = transparent passthrough
    # that effects below propagate through). Best-effort.
    if placed_items:
        for it in placed_items:
            try:
                fusion_clip = timeline.CreateFusionClip([it])
                if fusion_clip:
                    _log(f"   🎬 Converted V2 item to Fusion clip")
            except Exception as fc_err:
                _log(f"   ⚠️ CreateFusionClip skipped: {fc_err}")

    if appended:
        return {"attempted": True, "success": True, "count": len(appended),
                "message": f"Placed {len(appended)} adjustment clip(s) on V2",
                "clips": appended}
    return {"attempted": True, "success": False, "count": 0,
            "message": "AppendToTimeline did not place any adjustment clips on V2",
            "clips": []}


def _add_background_audio_clips(media_pool, timeline, audio_bin):
    """
    Place background music clips on audio track A2 ('background sound') in
    a fixed order:
        1. AI with Roz Build Up.wav
        2. AI with Roz Main Background.wav (repeated once per aRoll clip on V1)
    Sequenced back-to-back starting at the timeline start frame.
    """
    build_up_name = "AI with Roz Build Up.wav"
    main_bg_name = "AI with Roz Main Background.wav"

    if not audio_bin:
        return {
            "attempted": False,
            "success": False,
            "count": 0,
            "message": "No audio bin available",
            "clips": [],
        }
    if not timeline or not media_pool:
        return {
            "attempted": True,
            "success": False,
            "count": 0,
            "message": "Timeline or media pool unavailable",
            "clips": [],
        }

    try:
        audio_clips = audio_bin.GetClipList() or []
    except Exception as list_err:
        return {
            "attempted": True,
            "success": False,
            "count": 0,
            "message": f"Could not list audio clips: {list_err}",
            "clips": [],
        }

    # Build name -> clip map (case-insensitive, also try basename).
    by_name = {}
    for c in audio_clips:
        try:
            n = c.GetName() or ""
        except Exception:
            continue
        by_name[n.lower()] = c

    # Ensure A2 exists.
    try:
        audio_track_count = int(timeline.GetTrackCount("audio") or 1)
    except Exception:
        audio_track_count = 1
    while audio_track_count < 2:
        try:
            timeline.AddTrack("audio")
            audio_track_count += 1
            print(f"   ➕ Added audio track A{audio_track_count} (fallback)")
        except Exception as add_err:
            print(f"   ⚠️ Could not add audio track A{audio_track_count + 1}: {add_err}")
            break

    try:
        start_frame = int(timeline.GetStartFrame())
    except Exception:
        start_frame = 0

    def _audio_duration_frames(mp_item):
        for prop in ("Frames", "Duration"):
            try:
                val = mp_item.GetClipProperty(prop)
            except Exception:
                val = None
            if not val:
                continue
            try:
                if str(val).isdigit():
                    return int(val)
            except Exception:
                pass
            try:
                parts = str(val).split(":")
                if len(parts) == 4:
                    h, m, s, f = (int(p) for p in parts)
                    fps = 24
                    try:
                        fps_val = mp_item.GetClipProperty("FPS")
                        if fps_val:
                            fps = int(round(float(fps_val)))
                    except Exception:
                        pass
                    return ((h * 3600) + (m * 60) + s) * fps + f
            except Exception:
                continue
        return 0

    appended = []
    missing = []
    cursor = start_frame

    # Count aRoll clips on V1 so we can repeat Main Background that many times.
    try:
        aroll_items = timeline.GetItemListInTrack("video", 1) or []
        aroll_count = len(aroll_items)
    except Exception:
        aroll_count = 0
    if aroll_count <= 0:
        aroll_count = 1
    print(f"   🔁 Repeating '{main_bg_name}' {aroll_count}x (one per aRoll clip on V1)")

    desired_order = [build_up_name] + [main_bg_name] * aroll_count

    for target in desired_order:
        clip = by_name.get(target.lower())
        if not clip:
            # Try without extension match.
            base = target.rsplit(".", 1)[0].lower()
            for k, v in by_name.items():
                if k.rsplit(".", 1)[0] == base:
                    clip = v
                    break
        if not clip:
            print(f"   ⚠️ Background audio not found in audio bin: {target}")
            if target not in missing:
                missing.append(target)
            continue

        duration = _audio_duration_frames(clip)
        clip_info = {
            "mediaPoolItem": clip,
            "trackIndex": 2,
            "mediaType": 2,        # 2 = audio
            "recordFrame": cursor,
        }
        try:
            result = media_pool.AppendToTimeline([clip_info])
        except Exception as ap_err:
            print(f"   ❌ AppendToTimeline failed for {target}: {ap_err}")
            continue
        if result:
            appended.append(target)
            print(f"   ✅ A2 @ frame {cursor} (+{duration}f): {target}")
            cursor += duration if duration > 0 else 24
        else:
            print(f"   ⚠️ AppendToTimeline returned empty for {target} @ frame {cursor}")

    if appended:
        return {
            "attempted": True,
            "success": True,
            "count": len(appended),
            "message": f"Added {len(appended)} background audio clip(s) to A2",
            "clips": appended,
            "missing": missing,
        }
    return {
        "attempted": True,
        "success": False,
        "count": 0,
        "message": "AppendToTimeline did not place any background audio clips on A2",
        "clips": [],
        "missing": missing,
    }


def _extract_magic_zoom_setting():
    """Extract MagicZoomPro.setting from the installed .drfx (zip) to a
    temp path and return its absolute path. Cached after first call."""
    import tempfile, zipfile
    cache_dir = Path(tempfile.gettempdir()) / "scriptcraft_fusion_settings"
    cache_dir.mkdir(parents=True, exist_ok=True)
    out_path = cache_dir / "MagicZoomPro.setting"
    if out_path.exists() and out_path.stat().st_size > 0:
        return str(out_path)

    drfx = Path.home() / "Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Templates/MagicZoomPro.drfx"
    if not drfx.exists():
        return None
    try:
        with zipfile.ZipFile(drfx, "r") as z:
            for member in z.namelist():
                if member.endswith("/MagicZoomPro.setting") and "1. MagicZoom/" in member:
                    with z.open(member) as src, open(out_path, "wb") as dst:
                        dst.write(src.read())
                    return str(out_path)
    except Exception:
        return None
    return None


def _apply_effect_to_aroll_clips(timeline, effect_name="MagicZoomPro"):
    """
    Apply a Resolve FX / OpenFX video effect to every clip on the aRoll
    track (V1). Tries a few API method variants for compatibility across
    Resolve versions.

    Returns a result dict: {attempted, success, count, message, applied_to}
    """
    if not timeline:
        return {
            "attempted": False,
            "success": False,
            "count": 0,
            "message": "Timeline unavailable",
            "applied_to": [],
        }

    try:
        items = timeline.GetItemListInTrack("video", 1) or []
    except Exception as list_err:
        return {
            "attempted": True,
            "success": False,
            "count": 0,
            "message": f"Could not list V1 items: {list_err}",
            "applied_to": [],
        }

    if not items:
        return {
            "attempted": True,
            "success": False,
            "count": 0,
            "message": "No clips on V1 (aroll) to apply effect to",
            "applied_to": [],
        }

    # Effect name candidates. MagicZoomPro is a Fusion .drfx template (not
    # OFX), so AddVideoEffect should accept its display name as it appears
    # in the Effects Library. We also try a few path-style variants in case
    # Resolve namespaces it under its toolkit folder.
    name_candidates = [
        effect_name,
        effect_name.replace(" ", ""),
        "Magic Zoom Pro",
        "MagicZoom Pro",
        "MagicToolkit/MagicZoom/MagicZoomPro",
        "MagicZoom/MagicZoomPro",
        "Effects/MagicToolkit/MagicZoom/MagicZoomPro",
    ]
    # De-dup while preserving order.
    seen = set()
    name_candidates = [n for n in name_candidates if not (n in seen or seen.add(n))]

    print(f"\n✨ Applying '{effect_name}' to {len(items)} aRoll clip(s) on V1...")

    applied_to = []
    failures = []
    for idx, item in enumerate(items, 1):
        try:
            clip_name = item.GetName()
        except Exception:
            clip_name = f"V1 item #{idx}"

        success = False
        last_err = None
        for cand in name_candidates:
            # Try AddVideoEffect (Resolve 19.1+) — works for Resolve FX and
            # Fusion-template .drfx effects when called with display name.
            try:
                fn = getattr(item, "AddVideoEffect", None)
                if callable(fn):
                    res = fn(cand)
                    if res:
                        success = True
                        print(f"   \u21b3 matched name candidate: '{cand}'")
                        break
            except Exception as err:
                last_err = err
            # Older / alternate methods on some Resolve builds.
            for alt_method in ("AddPlugin", "AddOFXPlugin", "AddEffect"):
                try:
                    fn = getattr(item, alt_method, None)
                    if callable(fn):
                        res = fn(cand)
                        if res:
                            success = True
                            print(f"   \u21b3 matched via {alt_method}('{cand}')")
                            break
                except Exception as err:
                    last_err = err
            if success:
                break

        # Fusion-comp fallback: import the extracted .setting file directly
        # onto the clip. Works for Fusion-template based .drfx effects.
        if not success:
            setting_path = _extract_magic_zoom_setting()
            if setting_path:
                for fusion_method in ("ImportFusionCompFromFile", "LoadFusionCompFromFile"):
                    try:
                        fn = getattr(item, fusion_method, None)
                        if callable(fn):
                            res = fn(setting_path)
                            if res:
                                success = True
                                print(f"   \u21b3 matched via {fusion_method}('{setting_path}')")
                                # If imported, also try to activate by name.
                                if fusion_method == "ImportFusionCompFromFile":
                                    try:
                                        load_fn = getattr(item, "LoadFusionCompByName", None)
                                        if callable(load_fn):
                                            load_fn("MagicZoomPro")
                                    except Exception:
                                        pass
                                break
                    except Exception as err:
                        last_err = err

        if success:
            applied_to.append(clip_name)
            print(f"   ✅ {clip_name}")
        else:
            failures.append(clip_name)
            err_txt = f" ({last_err})" if last_err else ""
            print(f"   ⚠️ Could not apply '{effect_name}' to {clip_name}{err_txt}")

    if applied_to:
        return {
            "attempted": True,
            "success": True,
            "count": len(applied_to),
            "message": f"Applied '{effect_name}' to {len(applied_to)}/{len(items)} aRoll clip(s)",
            "applied_to": applied_to,
            "failures": failures,
        }
    return {
        "attempted": True,
        "success": False,
        "count": 0,
        "message": (
            f"Could not apply '{effect_name}' via scripting API. Your Resolve "
            "version may not expose AddVideoEffect for this OFX plugin — apply "
            "manually from the Effects panel."
        ),
        "applied_to": [],
        "failures": failures,
    }


def _broll_sort_key(clip_name: str):
    """
    Order broll clips by the index baked into Grok-generated filenames.

    Filenames look like: ``grok_<timestamp>_<index>_<safe_term>.mp4``
    Lower index == earlier row in the broll table.
    Non-Grok / unrecognized names sort to the end (alphabetically).
    """
    import re
    name = clip_name or ""
    m = re.match(r"grok_(\d+)_(\d+)_", name)
    if m:
        ts = int(m.group(1))
        idx = int(m.group(2))
        # Primary key: index in table; secondary: timestamp; tertiary: name
        return (0, idx, ts, name.lower())
    return (1, 0, 0, name.lower())


def _add_broll_clips_above_aroll(media_pool, timeline, broll_bin):
    """
    Append all clips from the broll bin onto video track V3 (above the
    aRoll on V1), in the order they appear in the broll table.

    Returns a result dict: {attempted, success, count, message, clips}
    """
    if not broll_bin:
        return {
            "attempted": False,
            "success": False,
            "count": 0,
            "message": "No bRoll bin available",
            "clips": [],
        }

    if not timeline or not media_pool:
        return {
            "attempted": True,
            "success": False,
            "count": 0,
            "message": "Timeline or media pool unavailable",
            "clips": [],
        }

    try:
        broll_clips = broll_bin.GetClipList() or []
    except Exception as list_err:
        return {
            "attempted": True,
            "success": False,
            "count": 0,
            "message": f"Could not list bRoll clips: {list_err}",
            "clips": [],
        }

    if not broll_clips:
        return {
            "attempted": True,
            "success": False,
            "count": 0,
            "message": "bRoll bin is empty",
            "clips": [],
        }

    # Sort by index in the Grok filename so timeline order == broll table order.
    sorted_clips = sorted(broll_clips, key=lambda c: _broll_sort_key(c.GetName()))
    ordered_names = [c.GetName() for c in sorted_clips]
    print(f"\n🎞️  bRoll order on V3 ({len(sorted_clips)} clips):")
    for i, n in enumerate(ordered_names, 1):
        print(f"   {i}. {n}")

    # Ensure at least V3 exists (track setup helper normally handles this,
    # but keep a defensive add here in case the helper wasn't run).
    try:
        video_track_count = timeline.GetTrackCount("video")
    except Exception:
        video_track_count = 1
    if video_track_count is None:
        video_track_count = 1
    while video_track_count < 3:
        try:
            timeline.AddTrack("video")
            video_track_count += 1
            print(f"   ➕ Added video track V{video_track_count} (fallback)")
        except Exception as add_err:
            print(f"   ⚠️ Could not add V{video_track_count + 1} track: {add_err}")
            break

    # Make this timeline current so AppendToTimeline targets it.
    try:
        project = media_pool.GetCurrentFolder() and None  # no-op safe access
    except Exception:
        pass

    # Compute the timeline start frame so the first broll clip lines up with
    # the very beginning of V1 (above the first aRoll clip).
    try:
        start_frame = int(timeline.GetStartFrame())
    except Exception:
        start_frame = 0

    def _clip_duration_frames(mp_item):
        """Return the clip's duration in frames (best-effort)."""
        for prop in ("Frames", "Duration"):
            try:
                val = mp_item.GetClipProperty(prop)
            except Exception:
                val = None
            if not val:
                continue
            # "Frames" is usually an integer string; "Duration" is HH:MM:SS:FF.
            try:
                if str(val).isdigit():
                    return int(val)
            except Exception:
                pass
            # Parse timecode HH:MM:SS:FF assuming 24fps fallback.
            try:
                parts = str(val).split(":")
                if len(parts) == 4:
                    h, m, s, f = (int(p) for p in parts)
                    fps = 24
                    try:
                        fps_val = mp_item.GetClipProperty("FPS")
                        if fps_val:
                            fps = int(round(float(fps_val)))
                    except Exception:
                        pass
                    return ((h * 3600) + (m * 60) + s) * fps + f
            except Exception:
                continue
        return 0

    # Append clips one at a time on V3 starting at the timeline start frame.
    appended = []
    cursor = start_frame
    for clip in sorted_clips:
        duration = _clip_duration_frames(clip)
        clip_info = {
            "mediaPoolItem": clip,
            "trackIndex": 3,
            "mediaType": 1,        # 1 = video
            "recordFrame": cursor, # absolute timeline frame to drop onto V3
        }
        try:
            result = media_pool.AppendToTimeline([clip_info])
        except Exception as ap_err:
            print(f"   ❌ AppendToTimeline failed for {clip.GetName()}: {ap_err}")
            continue
        if result:
            appended.append(clip.GetName())
            print(f"   ✅ V3 @ frame {cursor} (+{duration}f): {clip.GetName()}")
            if duration > 0:
                cursor += duration
            else:
                # Fallback: bump cursor by 1 second @ 24fps so next clip doesn't overlap.
                cursor += 24
        else:
            print(f"   ⚠️ AppendToTimeline returned empty for {clip.GetName()} @ frame {cursor}")

    if appended:
        return {
            "attempted": True,
            "success": True,
            "count": len(appended),
            "message": f"Added {len(appended)} bRoll clip(s) to V3",
            "clips": appended,
        }
    return {
        "attempted": True,
        "success": False,
        "count": 0,
        "message": "AppendToTimeline did not place any bRoll clips on V3",
        "clips": [],
    }


def create_resolve_project(script_title, edl_filename=None, broll_folder=None, images_folder=None):
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

        # Import additional project-generated media (e.g., prior Grok b-roll and generated images).
        supplemental_imported = {}
        broll_paths = _collect_media_paths(
            broll_folder,
            extensions={'.mp4', '.mov', '.m4v', '.avi', '.mkv'}
        )
        images_paths = _collect_media_paths(
            images_folder,
            extensions={'.png', '.jpg', '.jpeg', '.webp', '.tif', '.tiff'}
        )

        broll_count = _import_media_to_bin(resolve, media_pool, bin_mapping, 'broll', broll_paths)
        images_count = _import_media_to_bin(resolve, media_pool, bin_mapping, 'images', images_paths)
        if broll_count > 0:
            supplemental_imported['broll'] = broll_count
        if images_count > 0:
            supplemental_imported['images'] = images_count

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
            "supplemental_media_imported": supplemental_imported,
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
    sorted_video_files=None,
    broll_folder=None,
    images_folder=None,
    generate_subtitles=True,
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
        base_result = create_resolve_project(
            script_title,
            edl_filename,
            broll_folder=broll_folder,
            images_folder=images_folder,
        )

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

                # Configure track layout: V1=aroll, V2=adjustment, V3=broll, V4=animations
                print("\n🛤️  Configuring video track layout...")
                track_layout = _setup_video_tracks(timeline)
                base_result["video_track_layout"] = track_layout
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

        # ------------------------------------------------------------------
        # (Adjustment-clip insertion on V2 disabled — Resolve scripting
        # API has no reliable way to create empty adjustment clips.)
        # ------------------------------------------------------------------

        # ------------------------------------------------------------------
        # Place bRoll (Grok-generated) clips on V2 above the aRoll on V1.
        # Order matches the broll table (encoded in filename: grok_<ts>_<i>_*).
        # ------------------------------------------------------------------
        broll_bin = None
        try:
            for subfolder in root_folder.GetSubFolders().values():
                if subfolder.GetName() == "broll":
                    broll_bin = subfolder
                    break
        except Exception as bin_err:
            print(f"⚠️ Could not locate broll bin: {bin_err}")

        broll_v2_result = _add_broll_clips_above_aroll(media_pool, timeline, broll_bin)
        print(
            f"   {'✅' if broll_v2_result.get('success') else '⚠️'} "
            f"{broll_v2_result.get('message')}"
        )

        # ------------------------------------------------------------------
        # Configure audio tracks (A1='aroll sound', A2='background sound')
        # and place background music clips on A2 in fixed order.
        # ------------------------------------------------------------------
        print("\n🎵 Configuring audio track layout...")
        audio_track_layout = _setup_audio_tracks(timeline)
        base_result["audio_track_layout"] = audio_track_layout

        audio_bin = None
        try:
            for subfolder in root_folder.GetSubFolders().values():
                if subfolder.GetName() == "audio":
                    audio_bin = subfolder
                    break
        except Exception as bin_err:
            print(f"⚠️ Could not locate audio bin: {bin_err}")

        background_audio_result = _add_background_audio_clips(
            media_pool, timeline, audio_bin
        )
        print(
            f"   {'✅' if background_audio_result.get('success') else '⚠️'} "
            f"{background_audio_result.get('message')}"
        )
        base_result["background_audio"] = background_audio_result

        # Apply MagicZoomPro Resolve FX to every aRoll clip on V1.
        magic_zoom_result = _apply_effect_to_aroll_clips(timeline, "MagicZoomPro")
        print(
            f"   {'✅' if magic_zoom_result.get('success') else '⚠️'} "
            f"{magic_zoom_result.get('message')}"
        )
        base_result["magic_zoom_pro"] = magic_zoom_result

        # Build list of what was added
        videos_list = []
        if intro_clip and len(final_items) > 0:
            videos_list.append("AI with Roz v2.mov (intro)")

        if len(final_items) > (1 if intro_clip else 0):
            videos_list.extend(sorted_video_files)

        videos_added = videos_list if len(final_items) > 0 else []

        subtitle_result = {
            "attempted": False,
            "success": False,
            "message": "Subtitle generation skipped",
        }
        if generate_subtitles and len(final_items) > 0:
            print("\n📝 Attempting subtitle generation from timeline audio...")
            subtitle_result = _generate_subtitles_from_audio(timeline)
            print(f"   {'✅' if subtitle_result.get('success') else '⚠️'} {subtitle_result.get('message')}")

        # Update result with video info
        base_result["videos_added"] = videos_added
        base_result["videos_count"] = len(videos_added)
        base_result["subtitle_generation"] = subtitle_result
        base_result["broll_v2"] = broll_v2_result

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

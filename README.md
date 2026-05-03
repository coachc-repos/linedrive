# 📚 LineDrive — AI-Powered Content Creation, Video Production & Baseball Data Platform

**Version 2.1.x** (May 2026)

A multi-module platform combining:
- **ScriptCraft v2** — AI-powered YouTube script writing + DaVinci Resolve / Fusion video production automation + HeyGen avatar videos
- **Emotional thumbnail generator** — 6 AI-powered thumbnail variations (Gemini Flash Image)
- **Baseball tournament data** — Perfect Game / Little League / USA Baseball scrapers with Azure Data Lake storage
- **Social media** — X/Twitter content distribution

---

## 🚀 Quick Start

### ScriptCraft v2 — active web GUI (recommended)
```bash
cd scriptcraft-app-v2
source ../venv314/bin/activate
python web_gui.py
# Open http://localhost:8080
```
Provides the full pipeline: topic → 4-agent script writing → review → polish → YouTube upload details → emotional thumbnails → B-roll image generation → DaVinci Resolve timeline build with V3 B-roll + Fusion blur effects → EDL marker export → HeyGen avatar video.

### Console UI (baseline)
```bash
python console_launcher_module.py
# Select: Full Script Creation Workflow
```

### Baseball scrapers
```bash
# Web GUI
python scraper_web_gui.py

# Console batch UI
cd batch_scrapers && python batch_scraper_ui.py
```

### Emotional thumbnails (standalone)
```bash
python tools/test_emotional_thumbnails.py
```
or programmatically:
```python
from tools.media.emotional_thumbnail_generator import EmotionalThumbnailGenerator
gen = EmotionalThumbnailGenerator()
results = gen.generate_all_thumbnails(
    script_title="Your Title",
    script_content="Your script...",
    youtube_upload_details="## 🖼️ THUMBNAIL TEXT\nYour text...",
)
```

---

## 🎯 Core Capabilities

| Feature | Description | Entry Point |
|---|---|---|
| 🎬 Script Creation | 4-agent AI workflow (topic → write → review → polish) | [scriptcraft-app-v2/web_gui.py](scriptcraft-app-v2/web_gui.py) |
| 🎞 DaVinci Resolve | Programmatic timeline build, B-roll on V3, EDL marker export, Fusion comp automation | [scriptcraft-app-v2/davinci_resolve_api.py](scriptcraft-app-v2/davinci_resolve_api.py) |
| 🌫 Fusion FX | Programmatic Blur w/ BezierSpline keyframes per V3 clip + editor cache refresh | same as above |
| 🎭 HeyGen Avatars | v2 API integration with template management + curl test | [generate_heygen_curls.py](generate_heygen_curls.py), [tools/heygen/](tools/heygen/) |
| 🎨 Thumbnails | 6 emotional variations with Gemini Flash Image | [tools/media/emotional_thumbnail_generator.py](tools/media/emotional_thumbnail_generator.py) |
| 🖼 B-roll Images | Per-chapter prompts → Shutterstock + AI images | [tools/media/broll_image_generator.py](tools/media/broll_image_generator.py) |
| ⚾ Baseball Data | Multi-league scraping + Azure Data Lake | [scraper_web_gui.py](scraper_web_gui.py), [batch_scrapers/](batch_scrapers/) |
| 📱 Social Media | X/Twitter posting | [social_media/](social_media/) |
| ☁️ Azure Deploy | Container Apps + Static Web Apps | [scriptcraft-app/](scriptcraft-app/) (legacy deploy) |

---

## 🗂️ Project Structure

```
linedrive/
├── scriptcraft-app-v2/                  # 🎬 ACTIVE web GUI + Resolve/Fusion/HeyGen
│   ├── web_gui.py                       #   Flask + SSE on :8080
│   ├── davinci_resolve_api.py           #   Resolve/Fusion automation
│   ├── console_ui/                      #   workflows, text/word processing
│   ├── linedrive_azure/agents/          #   AI agent clients
│   ├── fusion_presets/                  #   Fusion .setting / .comp templates
│   └── templates/                       #   HTML
│
├── scriptcraft-app/                     # 🕰 Legacy web GUI (still present)
│
├── console_ui/                          # Console workflows + text/word processing
├── console_launcher_module.py           # Console UI entry
│
├── linedrive_azure/                     # Azure agents + storage + search (root copy)
│   ├── agents/
│   ├── storage/
│   └── search/
│
├── tools/
│   ├── media/
│   │   ├── emotional_thumbnail_generator.py   # 6 variations (Gemini)
│   │   └── broll_image_generator.py           # Per-chapter B-roll
│   ├── heygen/
│   ├── debug/, demos/, diagnostics/, samples/, setup/
│   └── cloud-cost-assistant/
│
├── batch_scrapers/                      # ⚾ Tournament scrapers (PG/LL/USA)
│   ├── common/, perfect_game/
├── scraper/                             # Multi-league scraping framework
├── scraper_web_gui.py                   # Scraper web UI
│
├── social_media/                        # X/Twitter platforms + UI
├── cloud-cost-assistant/                # Standalone cost assistant Flask app
├── gpt-oss/                             # OSS GPT helper Flask app
├── web/                                 # Static web assets
│
├── templates/                           # Word .dotx + scraper templates
├── output/                              # Generated artifacts
├── backups/                             # Snapshot backups
├── tests/, docs/                        # Tests + docs (where present)
│
├── azure.yaml                           # azd config
├── exec-craft.sh, run_console.sh, run_script_creator.sh, start_scraper_gui.sh
├── README.md                            # This file
└── AI-ASSISTANT-PROMPT.md               # Context prompt for AI assistants
```

---

## 🆕 What's New (last 3 weeks, ending May 2026)

### ScriptCraft v2 launched
- New active web GUI at [scriptcraft-app-v2/](scriptcraft-app-v2/) supersedes the original `scriptcraft-app/`. The v2 app has the full agent pipeline plus DaVinci Resolve / Fusion / HeyGen integration.

### DaVinci Resolve automation ([davinci_resolve_api.py](scriptcraft-app-v2/davinci_resolve_api.py))
- External-Python bridge via `DaVinciResolveScript.scriptapp("Resolve" / "Fusion")`.
- Timeline construction with B-roll automatically placed on **V3**.
- Per-clip **EDL marker export** for B-roll cues.
- **Fusion comp automation** with a Blur node + BezierSpline-driven keyframes (clear → blurry over each clip's lifetime).
- **Editor preview cache refresh**: per-clip `comp.SetCurrentTime` + `comp.Render` followed by an Edit↔Fusion page bounce that scrubs each V3 clip's mid-timecode so the Edit page reflects the new comp without manual interaction.
- Script-title parsing now recognizes a `Title:` line.
- Adjustment-clip insertion temporarily disabled.

### HeyGen v2
- Avatar video generation via the v2 API with template management and a curl-based test mode ([generate_heygen_curls.py](generate_heygen_curls.py), [tools/heygen/](tools/heygen/)).

### Grok integration
- Workflow for selecting Grok as a backend, including persistent API key storage.

### UI / UX
- Shutterstock tab now opens links in new browser tabs.
- Thumbnail generation has cancel controls; stop-button UI aligned across panels.
- Various B-roll error reporting and f-string compatibility fixes; thumbnail template path corrected.

### Scraper Web GUI
- Standalone Flask UI at [scraper_web_gui.py](scraper_web_gui.py) for the baseball scrapers.

---

## 🔧 Prerequisites

```bash
# Python 3.14 (project venv: venv314)
python --version

# Activate the project venv
source venv314/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### DaVinci Resolve scripting (for video pipeline)
- DaVinci Resolve Studio installed and running locally.
- `RESOLVE_SCRIPT_API`, `RESOLVE_SCRIPT_LIB`, and `PYTHONPATH` environment variables configured per Resolve's external scripting docs.
- The Resolve preference **System → General → External scripting using** must be set to **Local**.

### Azure (for data lake + agents)
```bash
az login
# Storage account: linedrivestorage  / container: tournament-data
```

### HeyGen
- HeyGen API key configured (used by the curl generator).

### Gemini (for thumbnails / B-roll images)
- `GOOGLE_API_KEY` (or equivalent) configured.
```bash
pip install google-generativeai
```

---

## 📝 Example Workflows

### Full ScriptCraft v2 pipeline (web)
1. `cd scriptcraft-app-v2 && python web_gui.py`
2. Open http://localhost:8080
3. Enter topic → audience → tone → length.
4. Watch the SSE-streamed pipeline: topic enhancement → script writing → review → polish → YouTube upload details → 6 emotional thumbnails → per-chapter B-roll images → DaVinci Resolve timeline build (V3 B-roll + Fusion blur) → EDL markers → HeyGen avatar (optional).

### DaVinci Resolve / Fusion smoke test
The current Fusion smoke test (`_apply_blur_to_v3_clips` in [davinci_resolve_api.py](scriptcraft-app-v2/davinci_resolve_api.py)) adds a Blur to every V3 broll clip with two BezierSpline keyframes (0 → max_blur over the clip's COMP-LOCAL range) and forces the Edit page preview to refresh.

### Baseball tournament scraping
```bash
python scraper_web_gui.py
# or
cd batch_scrapers && python batch_scraper_ui.py
```
Data lands in Azure Data Lake under `tournament-data/raw/year=YYYY/month=MM/day=DD/`.

---

## 🗃 Azure Data Lake Storage

- **Storage account**: `linedrivestorage`
- **Container**: `tournament-data`
- **Path**: `raw/year=YYYY/month=MM/day=DD/<run>.json`, `processed/...`
- **Auth**: `ChainedTokenCredential` with Azure CLI priority

---

## 🐛 Troubleshooting

### DaVinci Resolve: Blur only visible after manual Fusion-page scrub
Ensure each clip's comp is evaluated inside the Fusion page (`comp.SetCurrentTime` + `comp.Render({"Tool": tool, "Quality": 1})`) and that the post-loop page bounce scrubs each V3 clip's mid-timecode. Add a small `time.sleep(0.1)` per clip if the editor still shows stale thumbnails.

### Fusion: keyframes don't take effect
On this Resolve build, `tool.SetInput(name, value, frame)` does not create a BezierSpline modifier. Explicitly add one:
```python
spline = comp.AddTool("BezierSpline", -32768, -32768)
blur.ConnectInput("XBlurSize", spline)
spline.SetKeyFrames({f_start: {1: 0.0}, f_end: {1: max_blur}})
```

### Fusion: blur applied only to first 2 clips
You're using timeline-absolute frames inside per-clip comps. Use COMP-LOCAL frames from `comp.GetAttrs()['COMPN_GlobalStart' / 'COMPN_GlobalEnd']`.

### Web GUI hangs at completion
SSE completion bug. Use the `while True:` "drain queue, then check done" pattern (see [AI-ASSISTANT-PROMPT.md](AI-ASSISTANT-PROMPT.md)).

### Progress bar jumps to 50% or backward
`send_update()` must early-return on `progress is None`; filter chapter "Writing/Reviewing X/Y" START messages.

### "Thread already has an active run"
Cancel existing runs and `time.sleep(5)` before retrying.

### Import error: `google.generativeai`
```bash
venv314/bin/pip install google-generativeai
```

### Wrong Python / venv
```bash
source venv314/bin/activate
which python
```

---

## 🏷️ Version History

- **v2.1.x** (May 2026) — DaVinci Resolve + Fusion automation in `scriptcraft-app-v2`; HeyGen v2; Grok workflow; scraper web GUI; thumbnail cancel controls; `Title:` parsing.
- **v2.0.x** (Oct 2025) — Emotional thumbnails + Gemini Flash Image integration.
- **v1.5.x** (Oct 2025) — Tone selector + technical levels.
- **v1.0** — Working web GUI baseline.

---

## 📞 Support

- **AI assistant context**: [AI-ASSISTANT-PROMPT.md](AI-ASSISTANT-PROMPT.md)
- **Issues**: GitHub Issues
- **Maintainer**: Christian Thilmany

---

© 2026 LineDrive Project

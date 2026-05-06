# ScriptCraft v2 — Container Build

Headless cloud variant of `scriptcraft-app-v2/`, intended for **Azure Container Apps**.

## Relationship to `scriptcraft-app-v2/`

This folder is a **separate, self-contained copy** of the v2 app. The local
desktop variant (`scriptcraft-app-v2/`) is unaffected by anything here.
`web_gui.py` is intentionally **not** modified — `container_app.py` is a thin
overlay that:

* Stubs out `davinci_resolve_api`, `resolve_inspector`, and
  `DaVinciResolveScript` so imports don't crash without DaVinci installed.
* Replaces local-only Flask view functions with a `503
  feature_disabled_in_container` response.
* Adds a `/healthz` probe endpoint and a gunicorn entrypoint.

When you update `scriptcraft-app-v2/`, you can resync this folder by copying
`web_gui.py`, `templates/`, `console_ui/`, and `linedrive_azure/` from there —
nothing in `web_gui.py` itself is patched.

## What's enabled

* Script creation & processing (`/create`, `/process-script`)
* YouTube upload-details agent (titles, descriptions, tags, **chapters**)
* Hook agent
* Thumbnail generation (Google Imagen)
* Flow analysis
* B-roll table extraction & b-roll search
* Grok video generation (returns URL/job ref — no local download)
* HeyGen cURL generation (returns the cURL string — no upload, no download)
* Markdown / DOCX export endpoints that stream the file in the response
  (`/export_markdown`, `/export_heygen_curl`, `/download_comparison`)

## What's disabled (returns HTTP 503)

| Group | Examples |
|---|---|
| DaVinci Resolve | `/api/resolve/*`, `/create_resolve_project`, `/create_resolve_with_videos`, `/check_aroll_videos`, `/setup_project`, `/execute_curl`, `/check_video_status` |
| Local Whisper transcription | `/api/transcribe-audio`, `/api/transcribe-audio/progress/<id>` |
| Local file system browsers / output dirs | `/api/browse-dirs`, `/api/create-dir`, `/api/save-outputs`, `/api/output-dir` |
| Local-disk video/audio downloads | `/download_heygen_video`, `/api/download-media-zip` |
| Word doc export to local disk | `/export_word`, `/test_word` |
| Local debug | `/debug/stdout`, `/test-capture`, `/test_create` |

The full disabled set is enumerated in `container_app.py::_DISABLED_VIEWS`.

## Required environment variables

Set these in Container Apps secrets / env:

* `AI_PROJECT_API_KEY` (or use managed identity for Azure AI Projects)
* `AI_PROJECT_ENDPOINT`
* `GOOGLE_API_KEY` (Imagen / thumbnails)
* `GROK_API_KEY` (optional, for grok video routes)
* `HEYGEN_API_KEY` (optional, only needed if you call the HeyGen API
  routes — not needed for pure cURL generation)
* `PORT` (defaults to 8080)

## Local build & run

```bash
cd scriptcraft-app-v2-container

# Build
docker build -t scriptcraft-v2-container:dev .

# Run (mount a .env if you have one)
docker run --rm -p 8080:8080 \
  -e AI_PROJECT_ENDPOINT=$AI_PROJECT_ENDPOINT \
  -e AI_PROJECT_API_KEY=$AI_PROJECT_API_KEY \
  -e GOOGLE_API_KEY=$GOOGLE_API_KEY \
  scriptcraft-v2-container:dev

# Verify
curl http://localhost:8080/healthz
```

## Deploy to Azure Container Apps

Easiest path is `az containerapp up` with this folder as context:

```bash
RG=linedrive-rg
LOC=eastus2
ENV=linedrive-env
APP=scriptcraft-v2

az containerapp up \
  --name $APP \
  --resource-group $RG \
  --location $LOC \
  --environment $ENV \
  --source . \
  --ingress external \
  --target-port 8080 \
  --env-vars \
    AI_PROJECT_ENDPOINT=$AI_PROJECT_ENDPOINT \
    AI_PROJECT_API_KEY=secretref:ai-project-key \
    GOOGLE_API_KEY=secretref:google-api-key
```

(Set the secrets first with `az containerapp secret set`.)

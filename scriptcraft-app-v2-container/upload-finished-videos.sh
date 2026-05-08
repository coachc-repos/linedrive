#!/usr/bin/env bash
#
# Upload (or re-sync) the local Finished Videos folder to the
# 'finished-videos' blob container in the linedrivestorage account.
#
# Mirrors the on-disk layout: top-level subfolders become blob "folders"
# (one card each in the gallery); loose root-level videos become loose blobs.
#
# Defaults match what the container app reads at runtime via the env vars
# FINISHED_VIDEOS_BLOB_ACCOUNT and FINISHED_VIDEOS_BLOB_CONTAINER.
#
# Usage:
#   ./upload-finished-videos.sh                # default source = iCloud Final
#   SRC="/path/to/local/Final" ./upload-finished-videos.sh
set -euo pipefail

ACCOUNT="${FINISHED_VIDEOS_BLOB_ACCOUNT:-linedrivestorage}"
CONTAINER="${FINISHED_VIDEOS_BLOB_CONTAINER:-finished-videos}"
SRC="${SRC:-$HOME/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Podcast/Videos/Final}"

if [ ! -d "$SRC" ]; then
    echo "❌ Source folder not found: $SRC"
    exit 1
fi

echo "📦 Source     : $SRC"
echo "☁️  Account    : $ACCOUNT"
echo "📁 Container  : $CONTAINER"
echo "🎬 Pattern    : *.mp4 *.mov *.m4v *.webm *.mkv (case-insensitive)"
echo

# upload-batch keeps the relative folder structure; --pattern can only take one
# pattern at a time, so we run it once per extension.
for ext in mp4 MP4 mov MOV m4v M4V webm WEBM mkv MKV; do
    echo "→ uploading *.$ext ..."
    az storage blob upload-batch \
        --account-name "$ACCOUNT" \
        --auth-mode login \
        --destination "$CONTAINER" \
        --source "$SRC" \
        --pattern "*.$ext" \
        --overwrite false \
        --output none 2>/dev/null || true
done

echo
echo "✅ Done. Blobs in container:"
az storage blob list \
    --account-name "$ACCOUNT" \
    --auth-mode login \
    --container-name "$CONTAINER" \
    --query "[].{name:name, size:properties.contentLength}" \
    -o table

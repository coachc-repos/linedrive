#!/usr/bin/env bash
#
# Transcode ProRes (or other browser-incompatible) source videos to H.264 MP4
# in a temp directory and upload them to the 'finished-videos' blob container.
# The local source files are NOT modified.
#
# Usage:
#   ./transcode-and-upload.sh [pair ...]
#
# Each "pair" is "<blob_name>|<source_path>" where blob_name is the name to
# write into the container (use a forward-slash path to nest under a folder
# card; the gallery cards group by the first path segment).
#
# If no pairs are provided, defaults to the four ProRes 'AI with Roz' clips.
set -euo pipefail

ACCOUNT="${FINISHED_VIDEOS_BLOB_ACCOUNT:-linedrivestorage}"
CONTAINER="${FINISHED_VIDEOS_BLOB_CONTAINER:-finished-videos}"
SRC_ROOT="${SRC:-$HOME/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Podcast/Videos/Final}"

if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "ffmpeg not found on PATH" >&2
    exit 1
fi

if [ "$#" -eq 0 ]; then
    set -- \
      "AI with Roz Exit Clip.mp4|$SRC_ROOT/AI with Roz Exit Clip.mov" \
      "AI with Roz Intro Clip.mp4|$SRC_ROOT/AI with Roz Intro Clip.mov" \
      "AI with Roz Intro.mp4|$SRC_ROOT/AI with Roz Intro.mov"
fi

TMPDIR=$(mktemp -d -t scriptcraft-transcode-XXXXXX)
trap 'rm -rf "$TMPDIR"' EXIT
echo "Temp dir: $TMPDIR"

for entry in "$@"; do
    blob_name="${entry%%|*}"
    src_file="${entry##*|}"

    if [ ! -f "$src_file" ]; then
        echo "SKIP (missing source): $src_file"
        continue
    fi

    out="$TMPDIR/$(basename "$blob_name")"
    echo
    echo "=== Transcoding ==="
    echo "  src : $src_file"
    echo "  blob: $blob_name"

    ffmpeg -hide_banner -loglevel error -stats -y \
        -i "$src_file" \
        -vf "scale='min(1920,iw)':'-2'" \
        -c:v libx264 -preset veryfast -crf 22 -pix_fmt yuv420p \
        -c:a aac -b:a 192k \
        -movflags +faststart \
        "$out"

    if [ ! -s "$out" ]; then
        echo "  FAILED: ffmpeg produced no output"
        continue
    fi
    sz=$(stat -f%z "$out")
    echo "  output size: $sz bytes"

    # Delete the corresponding .mov blob (best effort) so the gallery shows
    # only the new MP4. Same blob name with .mov extension at the same path.
    if [[ "$blob_name" == *.mp4 ]]; then
        old_mov="${blob_name%.mp4}.mov"
        echo "  removing old blob (if present): $old_mov"
        az storage blob delete \
            --account-name "$ACCOUNT" --auth-mode login \
            --container-name "$CONTAINER" \
            --name "$old_mov" --output none 2>/dev/null || true
    fi

    echo "  uploading to blob: $blob_name"
    az storage blob upload \
        --account-name "$ACCOUNT" --auth-mode login \
        --container-name "$CONTAINER" \
        --name "$blob_name" \
        --file "$out" \
        --overwrite \
        --max-connections 4 \
        --output none

    rm -f "$out"
    echo "  done"
done

echo
echo "All requested files processed."
echo
echo "Final .mp4 blob list:"
az storage blob list \
    --account-name "$ACCOUNT" --auth-mode login \
    --container-name "$CONTAINER" \
    --query "[?ends_with(name,'.mp4')].{name:name,size:properties.contentLength}" \
    -o table

#!/usr/bin/env bash
# Generate JPG poster thumbnails for every MP4/MOV/M4V in finished-videos blob container.
# Compatible with macOS default bash 3.2 (no mapfile / no assoc arrays).
set -euo pipefail

ACCOUNT="${FINISHED_VIDEOS_BLOB_ACCOUNT:-linedrivestorage}"
CONTAINER="${FINISHED_VIDEOS_BLOB_CONTAINER:-finished-videos}"
FFMPEG="${FFMPEG:-/opt/homebrew/bin/ffmpeg}"
SEEK="${POSTER_SEEK:-00:00:02}"

echo "Account:   $ACCOUNT"
echo "Container: $CONTAINER"
echo "ffmpeg:    $FFMPEG"
echo "seek:      $SEEK"
echo

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

ALL_LIST="$TMP/all.txt"
POSTER_STEMS="$TMP/posters.txt"

az storage blob list \
    --account-name "$ACCOUNT" \
    --container-name "$CONTAINER" \
    --auth-mode login \
    --query "[].name" -o tsv > "$ALL_LIST"

grep -iE '\.jpg$' "$ALL_LIST" | sed -E 's/\.[Jj][Pp][Gg]$//' | sort -u > "$POSTER_STEMS" || true

count=0
skipped=0
fail=0

while IFS= read -r blob; do
    [ -z "$blob" ] && continue
    case "$blob" in
        *.mp4|*.MP4|*.mov|*.MOV|*.m4v|*.M4V) ;;
        *) continue ;;
    esac
    stem="${blob%.*}"
    if grep -Fxq "$stem" "$POSTER_STEMS"; then
        echo "skip (poster exists): $blob"
        skipped=$((skipped+1))
        continue
    fi

    echo
    echo "-> $blob"

    safe_name="$(echo "$blob" | tr '/ ' '__')"
    src="$TMP/src_$safe_name"
    out="$TMP/out_${safe_name%.*}.jpg"

    az storage blob download \
        --account-name "$ACCOUNT" \
        --container-name "$CONTAINER" \
        --name "$blob" \
        --file "$src" \
        --auth-mode login \
        --no-progress \
        --max-connections 4 >/dev/null

    "$FFMPEG" -hide_banner -loglevel error -y \
        -ss "$SEEK" -i "$src" \
        -frames:v 1 -vf "scale=320:-2" -q:v 4 \
        "$out" 2>/dev/null || true

    if [ ! -s "$out" ]; then
        "$FFMPEG" -hide_banner -loglevel error -y \
            -ss "00:00:00" -i "$src" \
            -frames:v 1 -vf "scale=320:-2" -q:v 4 \
            "$out" 2>/dev/null || true
    fi

    if [ ! -s "$out" ]; then
        echo "  X ffmpeg produced no frame for $blob"
        rm -f "$src" "$out"
        fail=$((fail+1))
        continue
    fi

    az storage blob upload \
        --account-name "$ACCOUNT" \
        --container-name "$CONTAINER" \
        --name "${stem}.jpg" \
        --file "$out" \
        --content-type "image/jpeg" \
        --overwrite true \
        --auth-mode login \
        --no-progress >/dev/null

    rm -f "$src" "$out"
    echo "  OK uploaded ${stem}.jpg"
    count=$((count+1))
done < "$ALL_LIST"

echo
echo "Done. Generated $count poster(s), skipped $skipped, failed $fail."

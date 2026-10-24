#!/usr/bin/env bash
# Start a video: number it, claim it, copy the stage template, and save the script.
#   scripts/new-video.sh <topic or brand> <<'SCRIPT'
#   <the approved script>
#   SCRIPT
# Prints the video's name (NN-name-MM-DD). The number is claimed atomically, so runs
# sharing this root at the same time each get their own. Run it from the root.
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
slug="$(printf '%s' "${1:?usage: scripts/new-video.sh <topic> <<< script}" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g')"
last=$(ls editable/materials 2>/dev/null | sed -nE 's/^([0-9]{2})-.*/\1/p' | sort -n | tail -1)
n=$((10#${last:-0} + 1))
while :; do
  name="$(printf '%02d' "$n")-$slug-$(date +%m-%d)"
  mkdir "editable/materials/$name" 2>/dev/null && break   # taken by another run: next number
  n=$((n + 1))
done
m="editable/materials/$name"
mkdir -p "$m/deletable" "$m/jobs" "$m/sfx"
sed "s/EDITABLE-NAME/$name/g" "$here/assets/stage/stage-9x16.html" > "editable/$name.html"
[ -t 0 ] || cat > "$m/script.txt"
echo "$name"

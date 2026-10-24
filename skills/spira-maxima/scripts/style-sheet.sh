#!/usr/bin/env bash
# One contact sheet of a style-reference video's distinct looks, for visual styling only.
#   scripts/style-sheet.sh <url or local path> <materials>/<name>/deletable
# Downloads a URL with yt-dlp into the folder (a local file is read in place), takes
# the opening frame plus a frame at every hard cut, keeps up to 20 spread evenly over
# the whole video, and writes <folder>/contact-sheet.jpg, four across. Open only the
# sheet: the reference is for how the video looks, never for what it says.
set -euo pipefail
src="$1"; dir="$2"; keep=20
mkdir -p "$dir/frames"
if [[ "$src" =~ ^https?:// ]]; then
  yt-dlp -q -f "bv*+ba/b" -o "$dir/reference.%(ext)s" "$src"
  src="$(ls "$dir"/reference.* | head -1)"
fi
rm -f "$dir"/frames/*.jpg
ffmpeg -v error -y -i "$src" -vf "select='eq(n\,0)+gt(scene\,0.4)',scale=360:-1" -fps_mode vfr "$dir/frames/f%04d.jpg"
n=$(ls "$dir"/frames/*.jpg | wc -l | tr -d ' ')
if [ "$n" -lt 8 ]; then   # few hard cuts: one frame every two seconds instead
  rm -f "$dir"/frames/*.jpg
  ffmpeg -v error -y -i "$src" -vf "fps=0.5,scale=360:-1" "$dir/frames/f%04d.jpg"
  n=$(ls "$dir"/frames/*.jpg | wc -l | tr -d ' ')
fi
if [ "$n" -gt "$keep" ]; then   # spread the kept frames over the whole video
  ls "$dir"/frames/*.jpg | awk -v n="$n" -v k="$keep" '{ if (int((NR - 1) * k / n) == int(NR * k / n)) print }' | xargs rm -f
  n=$(ls "$dir"/frames/*.jpg | wc -l | tr -d ' ')
fi
rows=$(( (n + 3) / 4 ))
ffmpeg -v error -y -pattern_type glob -i "$dir/frames/*.jpg" -vf "tile=4x${rows}" -frames:v 1 "$dir/contact-sheet.jpg"
echo "$dir/contact-sheet.jpg ($n frames)"

#!/usr/bin/env python3
"""Word timings for a VO: Whisper word timestamps written as timings.json beside it.

  python3 scripts/make-timings.py <materials>/<name>/vo.mp3
  python3 scripts/make-timings.py <materials>/<name>/vo.mp3 --from th-01.mp4 th-02.mp4 th-03.mp4
  python3 scripts/make-timings.py <materials>/<name>/vo.mp3 --recording <url or path>

With --from, the VO is first built from the talking-head clips: their audio
tracks joined in the order given (paths relative to the VO's folder, or
absolute), written to vo.mp3.

With --recording, the VO is the user's own recording (any audio or video
file, a URL or a path), converted to vo.mp3 as it is: nothing cut or retimed.
The recording is the script, so its transcript is written to script.txt
when the video has no script yet. Needs openai-whisper and ffmpeg.
"""
import json, shutil, subprocess, sys, pathlib, tempfile

args = sys.argv[1:]
if not args:
    sys.exit(__doc__)
src = pathlib.Path(args[0]).resolve(); out_dir = src.parent
if "--from" in args:
    clips = [(out_dir / c).resolve() for c in args[args.index("--from") + 1:]]
    missing = [str(c) for c in clips if not c.exists()]
    if not clips or missing:
        sys.exit(f"make-timings: clips not found: {missing or 'none given'}")
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as lst:
        lst.write("".join(f"file '{c}'\n" for c in clips))  # absolute paths: concat resolves relative ones against the list
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst.name, "-vn",
                    "-ac", "2", "-c:a", "libmp3lame", "-q:a", "2", str(src)], check=True)
    pathlib.Path(lst.name).unlink()
    print(f"vo.mp3 built from {len(clips)} clips")
recording = None
if "--recording" in args:
    rest = args[args.index("--recording") + 1:]
    if not rest:
        sys.exit("make-timings: --recording needs a URL or a path")
    recording = rest[0]
    tmp = None
    if recording.startswith(("http://", "https://")):
        # curl, not urllib: the media CDN answers Python's user agent with 403.
        tmp = tempfile.NamedTemporaryFile(suffix=pathlib.Path(recording.split("?")[0]).suffix, delete=False)
        tmp.close()
        subprocess.run(["curl", "-fsSL", "--retry", "2", "-o", tmp.name, recording], check=True)
        path = tmp.name
    else:
        path = str(pathlib.Path(recording).resolve())
        if not pathlib.Path(path).exists():
            sys.exit(f"make-timings: recording not found: {recording}")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path, "-vn",
                    "-ac", "2", "-c:a", "libmp3lame", "-q:a", "2", str(src)], check=True)
    if tmp:
        pathlib.Path(tmp.name).unlink()
    print(f"vo.mp3 built from the recording {recording}")
whisper = shutil.which("whisper")
cmd = [whisper] if whisper else [sys.executable, "-m", "whisper"]
try:
    subprocess.run(cmd + [str(src), "--model", "small",
                          "--word_timestamps", "True", "--output_format", "json",
                          "--output_dir", str(out_dir), "--verbose", "False"], check=True)
except (FileNotFoundError, subprocess.CalledProcessError) as e:
    sys.exit(f"whisper not available ({e}). Install with: pip install openai-whisper")

d = json.load(open(out_dir / (src.stem + ".json")))
words, segs = [], []
for s in d["segments"]:
    segs.append({"start": round(s["start"], 2), "end": round(s["end"], 2), "text": s["text"].strip()})
    for w in s.get("words", []):
        words.append({"w": w["word"].strip(), "s": round(w["start"], 2), "e": round(w["end"], 2)})
json.dump({"source": src.name, "duration": round(words[-1]["e"], 2), "segments": segs, "words": words},
          open(out_dir / "timings.json", "w"), indent=1)
script = out_dir / "script.txt"
if recording and not (script.exists() and script.read_text().strip()):
    script.write_text(" ".join(s["text"] for s in segs) + "\n")
    print(f"script.txt written from the recording's transcript")
(out_dir / (src.stem + ".json")).unlink()
print(f"{len(words)} words, {len(segs)} segments -> {out_dir/'timings.json'}")
print(f"last word ends {words[-1]['e']:.2f}s: data-duration = {int(round(words[-1]['e'] * 1000)) + 1000}")
for s in segs: print(f"  {s['start']:6.2f}-{s['end']:6.2f}  {s['text']}")

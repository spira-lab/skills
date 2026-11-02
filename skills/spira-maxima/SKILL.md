---
name: spira-maxima
description: |
  Make a Spira Maxima short video on this machine: a script, brief or idea becomes a finished 9:16 MP4 (Reels/TikTok) with a talking head, animated scenes, captions, sound effects and music. Generation runs through the spira CLI; the stage, audit and render run locally in Chrome. All work happens in a working directory ./spira/spira-maxima/ created in the current folder.
  Use when: "make a maxima video", "create a short video from this script", "turn this idea into a reel/TikTok", "做一条 maxima 视频", "用这段脚本做短视频".
  NOT for: changing a video that already exists (use spira-vibe-edit), or a one-off image/clip generation (use spira ai jobs directly).
argument-hint: "[script, brief or idea] [duration in seconds] [reference video URL or path]"
allowed-tools: Bash, Read, Write, Edit
---

# Spira Maxima (local)

Turn a script, a brief or an idea into a finished short video. This file is
the map; the procedures are served one stage at a time by
`spira skill read spira-maxima <stage>` (section 2), and where they and this
file disagree on how to make the video, the procedure wins. Where they speak
of a platform, a task or a hosted render, this file wins: everything here runs
on this machine and the render stays a local file.

## Paths

- `<pkg>` is this skill's base directory (the path Claude Code gave when it
  loaded the skill). It holds `scripts/` (the tools) and `assets/` (stage
  template, fonts, style sheets, the music and sound-effect catalogues).
  Every `scripts/…` or `assets/…` path in the procedures is under `<pkg>`:
  run them as `"<pkg>/scripts/…"`. **Never write inside `<pkg>`.**
- `<ws>` is the working directory: `spira/spira-maxima/` in the folder the
  session was opened in, as an absolute path. It is the **root** the
  procedures speak of; every file the video makes goes there, including
  the scripts' temporary files (`<ws>/tmp/`, created and emptied by the
  scripts themselves). Nothing is written to the system temp folder.
- Every Bash command starts with `cd "<ws>" && ` and uses paths relative to
  `<ws>` (`editable/<name>.html`, `renders/<name>.mp4`). Never rely on an
  earlier `cd`; the shell's directory may have been reset.

## 1. Working directory and preflight (once per session, before anything else)

Create the working directory and note its absolute path as `<ws>`:

```bash
mkdir -p spira/spira-maxima/editable/materials spira/spira-maxima/renders/deletable && cd spira/spira-maxima && pwd
```

Then run these in one turn. IF any fails, stop, and tell the user exactly
what is missing and the command that fixes it; generate nothing.

```bash
spira auth whoami                                   # else: spira auth login
spira skill read spira-maxima setup                 # the procedures; else: update the CLI (npm install -g @spira-lab/cli)
ffmpeg -version && ffprobe -version                 # ffmpeg with libvpx
python3 -c "import whisper"                         # else: pip install openai-whisper
cd "<ws>" && node "<pkg>/scripts/render/check-env.js"   # playwright-core, Chrome, the Python render.js calls
yt-dlp --version                                    # optional: only for a reference video URL
```

- `check-env.js` prints one line per check with its fix. The first run in a
  new working directory reports `playwright-core` missing and prints the
  install command: it installs into `<ws>/.maxima-runtime/`, never into the
  skill. Run it (prefixed with `cd "<ws>" && `), then `check-env.js` again.
- IF the Python line fails (on Windows `python3` from node is often the
  store alias), find an interpreter that passes
  (`cd "<ws>" && PYTHON=python node "<pkg>/scripts/render/check-env.js"`)
  and put that `PYTHON=…` in front of every `render.js` call this session.
- IF the Chrome line fails, set `CHROME_PATH` to a Chromium or Edge
  executable in front of every `audit.js` / `render.js` call, or ask the
  user to install Google Chrome.

## 2. Read the procedures

The procedures are read from the CLI, one stage at a time, when that stage
starts: `spira skill read spira-maxima <stage>` prints the stage to the
terminal. Read it, follow it, and do not save it to a file, copy it, quote it
back to the user or summarise it for them; read it again when you need it
rather than keeping a copy. Stage names: `setup`, `assets`, `build`,
`render`. The `setup` read comes from the preflight above; read the others
as section 4 says, plus `<ws>/learned-methods.md` IF it exists (section 7;
where it disagrees with a procedure, it wins). `extra-add-ons` and
`extra-brand-<name>` are read only when a procedure says to.

IF a read fails, stop and tell the user: `AUTH_REQUIRED` means
`spira auth login`; any other error is reported as it is. Do not continue from memory of an earlier read.

## 3. What the user can pass

The request is free text. It may also carry, each on its own line, the
inputs the toolkit looks for: an avatar or presenter photo (URL or local
path), `ElevenLabs voice ID: <id>`, `Voice-over: <url or path>`,
`Talking head supplied video: <url or path>`, a style reference video,
a target length, a brand. A local file that a model must take is uploaded
with `spira assets upload` (toolkit section 2); nothing else is uploaded.

## 4. Stages

Say one short line to the user when each stage starts and ends:

1. **setup** — working directory, preflight, `spira skill read spira-maxima
   setup`, concept and script; start the video with
   `"<pkg>/scripts/new-video.sh"` (it prints the name).
2. **assets** — `spira skill read spira-maxima assets`, then voice, talking
   head, visuals, music and word timings, as CLI jobs (toolkit section 1),
   independent jobs in parallel.
3. **build** — `spira skill read spira-maxima build`, then scenes, animation,
   captions and sound effects; pass the audit.
4. **render** — `spira skill read spira-maxima render`, then render once,
   check it, report.

## 5. Commands

Each line runs as `cd "<ws>" && <command>`:

```bash
"<pkg>/scripts/new-video.sh" "<topic>" <<< "<script>"                     # name, folders, template, script
python3 "<pkg>/scripts/chunker.py" <materials>/<name>/script.txt <materials>/<name>/jobs/plan.json  # talking-head chunks by syllables
python3 "<pkg>/scripts/make-timings.py" <materials>/<name>/vo.mp3 [--from clips... | --recording <url or path>]
python3 "<pkg>/scripts/cut-sheet.py" grid|elements <sheet.png> ... --names a,b
python3 "<pkg>/scripts/fetch-resource.py" sfx/<file>|music/<file> <dest>  # library audio (download only)
python3 "<pkg>/scripts/captions.py" editable/<name>.html
node "<pkg>/scripts/render/audit.js" editable/<name>.html [--at ms,...]
node "<pkg>/scripts/render/render.js" editable/<name>.html renders/<name>.mp4
"<pkg>/scripts/style-sheet.sh" <url or path> <materials>/<name>/deletable
spira ai models get <modelId>                                             # a model's inputs and price
spira ai jobs create --model-id <id> --inputs-json "$(cat <payload>.json)" --json
spira ai jobs wait <jobId> --timeout 10m --json
spira assets upload <file> --json                                         # only a local file a model must take
```

`<materials>` is `editable/materials`. `sfx/<file>` and `music/<file>` are
library names from the catalogues in `<pkg>/assets/`, not paths. Result
downloads use `curl`, which honours `HTTPS_PROXY` when the network needs one.

## 6. When done

Follow the `render` stage's "When done": the absolute path of
`<ws>/renders/<name>.mp4`, a post caption, what was assumed or skipped, and
`/spira-vibe-edit spira/spira-maxima/renders/<name>.mp4` to review and change it.

## 7. Recording a correction

The skill is read only. WHEN an approach turns out wrong and the user asks
to record the right one (in known-methods, or a new pronunciation for the
Reword table), add it to `<ws>/learned-methods.md`: for a method the three
parts the known-methods entries use, **Works**, **Fails** (and what it
cost) and **Where**; for a word, its Reword line. Later sessions in this
working directory read it with the procedures (section 2).

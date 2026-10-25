---
name: spira-vibe-edit
description: |
  Review and change a spira-maxima video on this machine: opens the Spira local editor (spira editor --agent) on the video, the user comments in the browser and presses Send to agent, and you make each comment real in the video's HTML editable, re-render it locally and hand the new version back, round after round.
  Use when: "edit this maxima video", "open the editor on renders/…mp4", "I want to comment on the video and have you fix it", "修改这条 maxima 视频", "打开编辑器改视频".
  NOT for: making a new video (use spira-maxima); a plain video file with no spira-maxima editable beside it (use spira-video-editor).
argument-hint: "[spira/spira-maxima/renders/<video>.mp4 or the video name]"
allowed-tools: Bash, Read, Write, Edit
---

# Spira Vibe Edit

The user comments on a video in a local browser page; you change the
video's editable, render it again here and hand the new version back to
the page. Nothing is sent to Spira except the generation jobs a comment
needs. The page is only the interface: nothing edits the video but you.

## 0. Names

- `<cm>`: the spira-maxima skill, `<this skill's base directory>/../spira-maxima`.
  IF `<cm>/scripts/render/render.js` does not exist, stop: spira-maxima must
  be installed beside this skill. Never write inside `<cm>` or this skill.
- `<root>`, `<video>`: from the argument. A path `…/renders/<video>.mp4`
  gives `<root>` = the folder above `renders/`; a bare name, or no
  argument, gives `<root>` = `spira/spira-maxima/` in the current folder (the
  working directory spira-maxima creates). IF that folder does not exist,
  stop: there is no spira-maxima video here yet, make one with `/spira-maxima`.
  Use `<root>` as an absolute path; every Bash command starts with
  `cd "<root>" && ` and uses root-relative paths.
- `<ve>`: this skill's own folder, `spira/spira-vibe-edit/` in the folder the
  session was opened in, as an absolute path (created in section 2). The
  editor keeps everything it writes there (comments, frames, versions,
  batches, its `work/` folder), never in the user's home; every
  `spira editor` command gets `--dir "<ve>"`, the same value each time.

## 1. Find the video

`renders/<video>.mp4`, `editable/<video>.html` and
`editable/materials/<video>/` must all exist under `<root>`. IF any is
missing, stop and name what was looked for. Never pick a video by guessing
(newest, only one, similar name); with no video named, list the
`renders/*.mp4` that have an editable and ask which.

Run the spira-maxima preflight once (`<cm>/SKILL.md` section 1, with
`<ws>` = `<root>`; its render dependency lives in `<root>/.maxima-runtime/`)
and keep any `PYTHON=…` / `CHROME_PATH=…` it needed for every audit and render.
Then `spira help editor` must list `--agent` and `--dir`; IF it says
`Unknown command reference: editor`, or `--dir` is missing, the installed
CLI predates this skill: stop and ask the user to update it
(`npm install -g @spira-lab/cli`).

## 2. Open the editor (once)

Create `<ve>` from the folder the session was opened in (the one holding
`spira/`) and note the absolute path it prints:

```bash
mkdir -p spira/spira-vibe-edit && cd spira/spira-vibe-edit && pwd
```

The editor's version 1 is the file it is opened on, read in place, so it
is opened on a review base that never changes:

```bash
cd "<root>" && mkdir -p renders/review && (test -f renders/review/<video>.mp4 || cp renders/<video>.mp4 renders/review/<video>.mp4)
spira editor --video "<root>/renders/review/<video>.mp4" --agent --dir "<ve>" --json
```

Run the last line with the Bash tool **in the background**
(`run_in_background: true`); it keeps running. Read its output file for
the JSON: `data.studioId`, `data.url` (already opened in the browser),
`data.workDir`, `data.notesPath` (all under `<ve>/<studioId>/`). Reopening
the same base with the same `--dir` reopens the same comments and versions.

IF it fails with "already open in another studio", the editor is already
running (from an earlier session): its studioId is the folder name of
`ls -d "<ve>"/local-<video>-*` (the one holding `server.json`), and the
URL is in the message. Go on with that studioId.

Tell the user the URL, and that they add comments on the video, tick the
ones to do, and press **Send to agent**.

## 3. Wait for a batch

In the background again, then end your turn; you are notified when it
finishes:

```bash
spira editor wait <studioId> --dir "<ve>" --json
```

Its JSON `data` is the batch (`batchId`, `video`, `workDir`, `notes[]`).
If the user wants to stop, stop the background editor task and start no
other wait.

## 4. Make the changes

Read `references/edit-rules.md` (in this skill) and follow it from
section 1: read spira-maxima's procedures, map every note, audit at the
notes' moments, write the fix table, edit, audit again, render to
`renders/<video>.mp4`, and write `<workDir>/results.json` with one
outcome per note. Every change a batch needs goes into **one** render.

Tell the user in one line when the edit starts, and before any
generation a note needs (what will be generated).

## 5. Deliver, then wait again

```bash
spira editor deliver <studioId> --dir "<ve>" --batch <batchId> --video "<root>/renders/<video>.mp4" --results "<workDir>/results.json" --json
spira editor deliver <studioId> --dir "<ve>" --batch <batchId> --failed "<reason>" --json   # nothing could be done
```

`--video` is needed whenever any note is `fixed` or `partly`. The page
switches to the new version and shows each outcome. Tell the user the
outcome lines, then go back to section 3 and start the next wait in the
background.

- A lost batch (a restart) comes back from `wait` until it is delivered.
- IF `wait` or `deliver` says no studio is running, the user closed it:
  open it again (section 2); comments and versions are kept.

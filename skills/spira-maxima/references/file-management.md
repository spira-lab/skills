---
name: file-management
description: Where every file of a video session lives, how it is named, what happens to it when it is replaced or rejected, and how a finished render is handed over. Fixed procedure. Apply to every file created, moved, or replaced in a video session.
---

# File Management

This is a fixed procedure. Other skills say what a file is for; this
skill says where it goes, what it is called, and what happens to it when
it is superseded.

## 1. The root

The **root** is the working directory `spira-maxima/` that SKILL.md
creates in the folder the session was opened in (`<ws>`). Every file the
session creates goes inside it, and every path here is relative to it.
The skill's own folders (`references/`, `scripts/`, `assets/`) live in
the skill directory, `<pkg>` (SKILL.md); they are read from and never
written to, and nothing is built inside them.

```
<root>/
  .maxima-runtime/              the render's npm dependency (SKILL.md preflight)
  learned-methods.md            corrections recorded in this workspace (SKILL.md)
  editable/ …                   section 2
  renders/ …
```

## 2. Layout

```
<root>/
  editable/
    NN-name-MM-DD.html          one editable per video (a copy of the stage template)
    materials/
      NN-name-MM-DD/            everything that editable references
        script.txt              the approved script, verbatim (a recording's transcript)
        vo.mp3                  voice-over (dry: no effects mixed in)
        bgm.mp3                 background music
        timings.json            word timestamps for the VO
        sfx/                    the sound effects the editable uses
        <images, clips, cut-outs, fonts>
        jobs/                   generation payloads; never referenced
        deletable/              rejected, replaced, unused and working files
  renders/
    NN-name-MM-DD.mp4           the current render of each editable
    deletable/                  replaced renders
```

## 3. Naming

Every video has one name, `NN-name-MM-DD`, shared by its editable, its
materials folder, and its render: a sequence number, the brand if one is
named (otherwise the topic), and the day it was started. The tool in
section 4 assigns it; it never changes afterwards, through edits,
re-renders, and later sessions.

## 4. The editable

One command starts the video: it numbers and claims it, copies the stage
template to `editable/<name>.html`, makes its materials folder (with
`deletable/`, `jobs/`, and `sfx/`), saves the script, and prints the name.
The root's own folders already exist.

```bash
scripts/new-video.sh "<brand or topic>" <<'SCRIPT'
<the approved script>
SCRIPT
```

An edit to a video is made to the same editable; never create a second
html for the same video. IF an editable is rebuilt from scratch, move the
old one to its materials `deletable/` first.

Other editables in the root belong to other videos, and may be another
run working right now: never open, reuse, resume, or take files from
them. The one exception is this same task being continued after an
interruption (the message says to continue): then the editable this
session created is yours, with its paid assets; check what exists and
carry on from there, and generate nothing that is already in.

## 5. Materials

- Everything the editable references lives in its materials folder and
  is referenced as `materials/NN-name-MM-DD/<file>`. Nothing in
  `deletable/` or `jobs/` may be referenced.
- Only material in use stays in the folder proper. The moment a file is
  rejected, replaced, or turns out to be unused (the second take of a
  music job, a Soul base image once the edit is in, a contact sheet),
  `mv` it to `deletable/` under the same name (adding `_2`, `_3` on a
  collision). The generation's payload stays in `jobs/`, so the asset can
  be made again.
- Never delete, and never free space: no step needs room made, and no
  failure is fixed by removing files. On a size or resource error, `mv`
  a file the error names that the video does not use to `deletable/`;
  otherwise retry once, then stop and tell the user. The only `rm` is a saved
  `.pending` record (toolkit section 1). The `deletable/` folders are
  the user's to empty.
- Tool working files (audit sheets, a reference video and its frames,) are written straight to `deletable/`
  by the tools.

## 6. Renders

- `scripts/render/render.js` writes `renders/NN-name-MM-DD.mp4`, moving a
  previous render to `renders/deletable/NN-name-MM-DD_<YYYYMMDD-HHMM>.mp4`
  first, so `renders/` holds exactly the current render of each editable.
- A finished render (rendered and checked) stays where it is and is
  handed over by its absolute path. It is never uploaded.

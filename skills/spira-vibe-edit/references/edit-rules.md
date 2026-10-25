# Edit rules for a spira-maxima video

The video is a spira-maxima **editable** (HTML stage) rendered to MP4.
Edit that same editable with spira-maxima's tools and procedures. Nothing
is rebuilt and no new video is started.

Names used below (SKILL.md sets them):

- `<cm>`: the spira-maxima skill directory (`references/`, `scripts/`, `assets/`).
- `<root>`: the working directory holding `editable/` and `renders/` for
  this video (by default `spira/spira-maxima/` in the session's folder).
- `<ve>`: this skill's folder `spira/spira-vibe-edit/`, where the editor
  keeps its data; the batch's `workDir` is inside it.
- `<video>`: the video's name, `NN-name-MM-DD`.

## 1. Rules of the directory

- Run every command as `cd "<root>" && …` with root-relative paths:
  `cd "<root>" && node "<cm>/scripts/render/audit.js" editable/<video>.html --at 4200`.
- `<cm>` and this skill are read only.
- Touch only `editable/<video>.html`, `editable/materials/<video>/`,
  `renders/<video>.mp4`, what the renderer moves to `renders/deletable/`,
  and the review base `renders/review/<video>.mp4` (created once by
  SKILL.md, never overwritten). The scripts keep their scratch files in
  `<root>/tmp/` and remove them; nothing goes to the system temp folder
  or the user's home. Other editables in `<root>` may belong to
  another run: never open or take from them.
- No `new-video.sh`, new html, materials folder, name, concept, script,
  style, music or persona roll, unless a comment asks for that change.

Read in one turn before the first edit (they win where they apply; this
file replaces what they say about making a new video):
`<cm>/references/stage-canvas-html.md`, `<cm>/references/file-management.md`,
`<cm>/references/known-methods.md`, `<cm>/references/creative-video-production.md`
sections 1, 7, 9, and `<root>/learned-methods.md` IF it exists;
`<cm>/references/toolkit.md` and `prompting.md` only WHEN a comment needs
new material. Wherever they name `references/…`, `scripts/…` or
`assets/…`, that is under `<cm>`.

## 2. A batch

`spira editor wait` gives a batch:

| Field | Meaning |
|---|---|
| `batchId` | answered by `spira editor deliver` |
| `video.path`, `video.version` | the version the comments were written on; never edit or overwrite this file |
| `video.width`, `.height`, `.duration` | that version's size and length (seconds) |
| `workDir` | scratch folder for this batch; `results.json` goes here |
| `notes[]` | the comments, in the order to report them |

Each note:

| Field | Meaning |
|---|---|
| `id` | the `noteId` its outcome is reported under |
| `scope` | `video` = the whole video (ignore time); `frame` = the frame at `timeSeconds`; `region` = `region` at `timeSeconds` |
| `timeSeconds` | seconds from the start; `null` for `video` |
| `region` | `{x, y, width, height}` 0 to 1 of the frame, top-left; `null` = whole frame |
| `text` | what to change |
| `frameImage` | absolute path of the frame the reviewer looked at, when present: read it before deciding what the comment means |

## 3. Map comments onto the stage

Comments were written on the whole render placed from 0 s, so comment
time is stage time.

- Moment: `ms = round(timeSeconds * 1000)`; never a frame number (the
  render is 24 fps).
- Region: `null` = whole frame; else `x*W, y*H, width*W, height*H`, with
  `W x H` the `#stage` size (1080 x 1920 unless made at another ratio,
  stage-canvas-html section 9).

Check: `video.duration` within 0.1 s of `data-duration`/1000, and
`video.width / video.height` the aspect of `#stage`. IF not, scale times by
`data-duration / (video.duration*1000)` and regions by aspect, confirm on
the audit sheet, and say so in the outcome. A moment past the end is
skipped and reported `not_fixed`.

**A comment on an older version.** IF `video.version` is lower than the
latest version in the editor (the highest `vN` file in the `versions/`
folder beside the editor's `notesPath`, or 1 when there is none), the
editable has changed since the reviewer watched. Edit the current
editable, but confirm each comment on the first audit sheet (section 4);
one whose moment no longer shows what it describes is `not_fixed`, "the
video changed after this comment". Never restore the old version.

## 4. Look before editing

One audit with every comment's moment:
`cd "<root>" && node "<cm>/scripts/render/audit.js" editable/<video>.html --at <ms>,<ms>,...`
It writes `editable/materials/<video>/deletable/audit-sheet.jpg`, what
the reviewer saw. Compare it with each `frameImage`. Then find in the
editable:

- the scene: `#s1`, `#s2`... stacked, later above; a scene ends at the
  delay of its exit animation on `#sN`;
- the element under the region, by absolute px position and size
  (stage-canvas-html section 4, rule 1) and `animation-delay`; a clip's own
  time is `ms - data-start`, an effect plays from `data-at`.

Decide every fix first, as one table, then build from it without
re-deciding:

| note | ms | scene | element | meaning | change | needs generation |
|------|----|-------|---------|---------|--------|------------------|

## 5. By kind of change

Sort each row into one kind; section 6 rules apply to all.

- **Stage** (animation, timing, text, captions, layout, effects): html
  only, stage-canvas-html sections 3 to 6. No generation.
- **Visual material** (background, b-roll, element): generate per
  toolkit 3d or 3c and prompting, in the video's look, and swap it in.
  A comment that gives an image URL or a local file uses that file
  exactly as given: copy or download it into the materials, place it
  with `object-fit: contain` in the box the comment's region marks, no
  filter, recolour, crop or restyle.
- **Presenter**: appearance is 3b on the base, then redo the clips that
  show it (3e, or 3j when the voice is given) and their cut-out (3f); a
  new presenter is 3a and every clip; a gesture redoes those clips (3e
  prompt, or 3h from a reference video); placement is html only.
- **Sound**: a new track per creative-video-production section 1; a
  volume or a lowered moment per stage-canvas-html section 5's
  attributes; new words or voice remake the speech by its source (3e,
  3j, 3i), then timings, captions and the scenes they move.
- **Whole video** (script, length, style, hook, ratio): still this
  editable; redo the scene table first, keep what the comment leaves.
- **Brand**: colours and type from `<cm>/references/brands/<brand>.md` when
  the comment names that brand; a logo only from an image the comment
  gives or that file names, fetched into materials. Never draw one;
  without it the brand is its name in text.
- **Out of scope** (post caption, cover): skip, report `not_fixed` with
  the reason.

## 6. Fix rules

- Change only what a comment asks: no restyling, reordering, new colours,
  effects or music unless named. One scene's comment never "improves"
  another.
- Edit the html by hand in several small edits, never a rewriting script
  or one whole-file write (stage-canvas-html section 3).
- Timing lives in `animation-delay`, `data-start`, `data-at`, a scene's
  exit delay and `data-duration`; stage-canvas-html section 4 rules hold,
  rule 10 above all (exit on the scene or a wrapper, never beside the entry).
- Speech is word for word (creative-video-production section 1). WHEN a
  comment changes what is said: remake the voice by the route toolkit
  section 3 names, rerun `make-timings.py` and `captions.py`, reset
  `data-duration` (stage-canvas-html section 2), retime affected scenes,
  and say in the outcome that it was the costliest fix.
- Captions: restyle via `.cc-phrase` CSS after the marker block and
  regenerate with `captions.py`; never edit inside the markers
  (stage-canvas-html section 6). A misspelt word follows the script.
- Hard rules beat comments (creative-video-production section 9: safe
  zone, grid, nothing over the face, levels): make the nearest allowed
  change and report it `partly`.
- Levels change only through stage-canvas-html section 5's attributes
  (`#vo`/sfx `data-gain-db`, `#bgm` `data-gain-offset-db`, `data-duck`),
  never a volume filter or re-encode; the bed's `data-gain-db` stays as
  copied and the voice stays loudest. Replace the bed only WHEN a comment
  asks for other music, chosen per creative-video-production section 1,
  its `gain_db` copied exactly.
- New material only WHEN a comment needs it, generated per toolkit
  section 1 with its models and prompting formats, matching the video's
  look. Payload and `.pending` go in `editable/materials/<video>/jobs/`;
  the result is downloaded into `editable/materials/<video>/`. IF
  interrupted, wait on the ids in existing `.pending` records before
  creating any job. The replaced file goes to that video's `deletable/`.
- A job input is a URL (toolkit section 2): a job's output by its
  `resultUrls[0]`; a file made or changed on disk uploaded with
  `spira assets upload`. The render is never uploaded.
- A vague comment: take its most likely meaning from the frame, the
  region and `frameImage`, do it, and state the reading in the outcome.
  One that cannot be done (contradicts another, impossible, past the end)
  is `not_fixed` with the reason; it never stops the rest.

## 7. Verify and render

1. Rerun the same `--at` audit; each asked change is visible at its moment
   and nothing else moved. Fix any miss before going on.
2. Whole-video audit per stage-canvas-html section 7, fix, run again.
3. Render once per stage-canvas-html section 8:
   `cd "<root>" && node "<cm>/scripts/render/render.js" editable/<video>.html renders/<video>.mp4`
   (prefix `PYTHON=…` / `CHROME_PATH=…` when the preflight needed them).
   The previous render moves to `renders/deletable/`; the editor keeps its
   own copy of every delivered version, and its version 1 is the review
   base, which is never touched.

## 8. Outcomes

One entry per note, in batch order, into `<workDir>/results.json`:

```json
[
  { "noteId": "<id>", "outcome": "fixed", "note": "headline moved up to y 420, clear of the face" },
  { "noteId": "<id>", "outcome": "partly", "note": "logo placed top right; moved 40 px left to stay in the safe zone" },
  { "noteId": "<id>", "outcome": "not_fixed", "note": "past the end of the video (0:31.0 of 0:28.4)" }
]
```

`outcome` is `fixed`, `partly` or `not_fixed`. `note` is one line the
reviewer reads: what changed, or why not; WHEN something was generated,
what and roughly its credits.

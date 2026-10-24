---
name: stage-canvas-html
description: Set up the HTML stage canvas for a video animation, the rules for animating inside it, the audit, the sound effects, and the render to MP4. Fixed procedure. Use before building any video.
---

# Stage Canvas HTML

This is a fixed procedure. Follow it exactly. Do not improvise the harness;
creative decisions are not made here.

## 1. Start from the template

Every video is a copy of `assets/stage/stage-9x16.html`, made by
`scripts/new-video.sh` (file-management section 4). Never edit the template
itself, and never build a video from a blank file. The copy gives you:

- A **9:16 canvas**, `<div id="stage">`, at a fixed **1080 x 1920 px**.
- A **voice-over slot**, `<audio id="vo">`, and a **music slot**,
  `<audio id="bgm">`. Delete a tag the video does not use.
- **Video clip support**: every `<video>` inside `#stage` follows the
  stage clock (rule 11).
- **Sound-effect support**: `<audio class="sfx">` tags play at their time
  in the preview and are mixed by the renderer (section 5).
- A **timeline object**, `window.STAGE`, with `play()`, `pause()`,
  `restart()`, `seek(ms)`, `onFrame(fn)`, `time`, `playing`, `timings`,
  `duration`, `width`, `height`. `onFrame(fn)` calls `fn(t)`, `t` being the
  stage time in milliseconds, on every frame while playing, on every
  `seek`, and on `restart`; the renderer seeks every frame it captures, so
  a JS-driven element that derives its state from `t` alone renders
  exactly as it previews (rule 6).
- Preview controls, guide overlays, and a word readout for the operator;
  `?render` hides them and places the canvas at 1:1. Do not edit them.
  The guides are the stage grid every layout is placed on
  (creative-video-production section 9): `TikTok UI` and `Reels UI` draw
  the app UI and the one safe zone, `Centre` the X and Y axes through
  x 540, y 960 with a tick every 5% (54 px across, 96 px down), and
  `Thirds` the 3 x 3 lines at x 360 and 720, y 640 and 1280.

## 2. Voice-over timings (as soon as the VO file exists)

Every timed element is placed against the spoken words:

```bash
python3 scripts/make-timings.py <materials>/<name>/vo.mp3
```

(`--from <clip> <clip> ...` builds `vo.mp3` from talking-head clips first:
toolkit 3e. `--recording <url or path>` builds it from the user's own
recording: toolkit 3j.)

This runs Whisper (`small`, multilingual, the language detected from the audio, word timestamps) and writes `timings.json`
next to the audio, where the harness loads it from:

```json
{ "source": "vo.mp3", "duration": 39.14,
  "segments": [ { "start": 0.0, "end": 2.12, "text": "…" } ],
  "words":    [ { "w": "If", "s": 0.0, "e": 0.16 } ] }
```

Use `words[].s` as the `animation-delay` of anything that appears as a
word is said, and `segments` to find sentence boundaries for scene
changes. Whisper timestamps are accurate to roughly 50 ms. Re-run it
whenever the VO file changes.

**Set the video length.** The video ends one second after the last
spoken word: `data-duration` on `#stage`, in milliseconds, is the last
word's `e` plus 1000. The harness holds the last frame there and the
renderer uses it as the MP4 length. The last scene holds on that frame;
it has no exit.

## 3. Where things go

- Video CSS goes in the `<style>` block **below** the comment
  `Video content styles go below`. Do not touch the harness CSS above it.
- Video markup goes **inside** `<div id="stage">`. Anything outside the
  stage is not part of the video.
- Video JavaScript goes in a **new** `<script>` tag after the harness
  script. Do not edit the harness script.
- Each scene is a container with the class `scene` and an id (`#s1`,
  `#s2`, ...); the audit finds scenes by it. Kinetic-type words are
  elements with the class `w` (a key word also `k`), each phrase in its
  own parent; the audit checks phrases by it. Captions are not written by
  hand: section 6.
- **Plan the scenes once, then build in a few edits.** A scene is one
  look that holds for a few seconds; the changes inside it (cards, words,
  zooms) carry the pace. A 30-second video has at most 6 or 7 scenes,
  about one per sentence; more scenes are more to write and check, not
  a better video. Decide them all before the first edit, as one scene
  table (time window, what it shows, which assets), and build from it
  without re-deciding each scene as you reach it. Then write the
  skeleton (scene containers, the audio and sfx tags, `data-duration`),
  then the scenes two or three per edit. Never the whole file in one
  write: a very large write takes minutes with nothing on disk.
- **Write the editable by hand. Never build a helper that writes it.** No
  build script, generator, or template filler that takes timings and
  emits the html. You are the generator: read `timings.json`, write the
  CSS and markup with the numbers in them. A helper costs the time to
  write it, run it, and debug it, and can stall at each step. The one
  exception is the captions, which the skill's own tool writes
  (section 6).
- **Do not read the stage template.** Section 1 is its interface; the
  copy is your editable, and reading 23 KB of harness only fills the
  context.
- **Type comes from the skill's `assets/fonts/` library.** Read
  `assets/fonts/fonts.md` (the table of families, what each looks like, and the
  `@font-face` to write), pick the families the style calls for, copy
  their files into `materials/<name>/fonts/`, and declare them at the
  top of the video CSS. Nothing is fetched from the web (rule 8). The
  installed system fonts (`Noto Sans`, `DejaVu Sans`, ...) are fallbacks
  only, never the video's type; `Noto Color Emoji` is the emoji font. Do
  not list or inspect the system fonts. The audit flags a font that
  failed to load and a video whose text is all in system fonts.

## 4. Rules for animating inside the stage

These rules exist so Play, Pause, Play from start, and frame-by-frame
rendering all behave. Break them and playback or the MP4 will be wrong.

1. **All layout is in absolute pixels for a 1080 x 1920 canvas.** Position
   with `position: absolute` and px values. Never use `vw`, `vh`, `%` of the
   viewport, or media queries. The canvas is scaled as a whole; you design at 1:1.
2. **Use CSS animations (`@keyframes` + `animation`) for motion.** They are
   what the controls and the renderer drive.
3. **Every animation has `animation-fill-mode: both`.** Without it, elements
   snap to their base style before the delay starts and after the animation
   ends, and finished animations drop out of seeking.
4. **Sequence with `animation-delay`.** Time the whole video from t = 0 of
   the stage timeline. Do not chain animations with JavaScript timers.
5. **Do not use `transition` for timed motion.** Transitions cannot be paused,
   restarted, or seeked. Use `@keyframes`.
6. **Do not use `setTimeout`, `setInterval`, or `requestAnimationFrame` for
   timing.** If JavaScript must drive something (a counter, a canvas element),
   register it with `STAGE.onFrame(t => ...)` and derive its state from `t`
   in milliseconds. The state must be a pure function of `t`.
7. **No autoplay.** The stage loads paused on the first frame.
8. **No external network requests.** Fonts, images, and video files are
   local files referenced by relative path. The renderer runs offline.
9. **Do not use `animation-play-state` or `animation: none` in video CSS.**
   The harness owns those properties.
10. **Never put an entry and an exit animation of the same property on one
    element.** With `fill-mode: both`, the exit's backwards fill (for
    example `opacity: 1`) applies from t = 0 and wins over the entry's
    `opacity: 0`, so the element is visible before it should be. Put every
    exit on the scene's container (`#sN`) or a wrapper, and every entry on
    the thing that enters. The audit catches a violation as a leak.
11. **Video clips go in as `<video>` elements, never as frame sequences.**
    A talking-head cut-out (alpha WebM), footage, or any other clip is a
    `<video>` inside `#stage` with `muted playsinline preload="auto"` and
    `data-start="<ms>"`, the stage time at which the clip's own time is 0.
    The harness and the renderer drive it; write no sync script and
    extract no frames. Before its start the clip holds its first frame and
    after its end its last, so put its entry and exit on a wrapper with
    CSS animations, as for any element. An alpha WebM keeps its
    transparency on the stage and in the render.

## 5. Sound effects

Each cue is one tag inside `#stage`, next to the audio slots:

```html
<audio class="sfx" src="materials/<name>/sfx/03_whoosh.mp3" data-at="1600"></audio>
```

`data-at` is the stage millisecond the sound starts; put a whoosh's peak
on the cut it serves, not after it. Fetch each sound you use into
`materials/<name>/sfx/` first: `python3 scripts/fetch-resource.py
sfx/<file> editable/materials/<name>/sfx/<file>` (the audio is hosted,
not in the package).

Every effect plays at the volume stored in its file. The library is
already levelled, one sound at a time, against a voice at −16 LUFS, the
level the renderer sets every voice-over to; the renderer adds no gain
to an effect. WHEN a sound feels too loud or too soft for a moment,
choose a different sound. A library
music bed is set 10 dB under the voice by the gain on its tag,
`data-gain-db`, which is the chosen entry's `gain_db`
(creative-video-production section 1): the renderer applies it as a
fixed gain and stops before the capture when it is missing or is not
that track's value. Never estimate, round, or change it, and never
scale or re-encode the bed. Generated music, which has no stored gain,
carries no `data-gain-db` and is levelled to -26 LUFS. Do not
pre-mix effects into
`vo.mp3`; the VO file stays the dry voice that the timings came from.

**Level adjustments, only when the request or a review comment asks for
one.** These optional attributes are the only way to change a level;
never a gain filter or a re-encoded file. The voice stays the loudest
sound.

| Attribute | On | Effect |
|---|---|---|
| `data-gain-db="-3"` | `#vo` | voice after its −16 LUFS levelling, −12 to +6 |
| `data-gain-db="-6"` | an `audio.sfx` | that effect, −20 to +6 |
| `data-gain-offset-db="-4"` | `#bgm` | on top of its `data-gain-db` (kept as copied), −20 to +6 |
| `data-duck="1200-3400:-8,9000-12000:-6"` | `#bgm` | music lowered by dB in each ms range, 300 ms ramps, 0 to −30, no overlaps |

The renderer stops before the capture on a value out of range.

## 6. Captions

Word-per-word captions are mechanical, so a tool writes them:

```bash
python3 scripts/captions.py <root>/editable/<name>.html [--style highlight|appear] [--top 1390] [--size 66] [--color #fff] [--hl #ffcf33]
```

It aligns the script with the timings, so every word carries the
script's spelling and Whisper's timing; splits the words into one-line
phrases where the sentence reads best; shrinks a phrase that is wider
than the 700 px caption block; and writes the markup and CSS between
`captions:start` / `captions:end` markers, centred on x 540. `highlight`
lights each word as it is spoken; `appear` brings each word in as it is
spoken (creative-video-production section 7 decides which). Run it once
the timings exist, and again whenever the VO or script changes.

Restyle with CSS after the marker block: `#captions` (the layer),
`.cc-phrase` (position, size, colour, font), `.cc-phrase .w` (a word), and
the `ccHl` keyframes (the highlight). The captions come out in no font of
their own: set `.cc-phrase` to the caption face of the video's type
system (creative-video-production section 5). Never edit inside the markers, never
write caption words by hand, and do not reuse the `cc-` names.

## 7. Audit

Run the whole-video audit twice: once when every scene is written, and
once after fixing what it found. Not after each scene: problems are
cheaper to fix together.

```bash
node scripts/render/audit.js <root>/editable/<name>.html
```

To look at a stretch while building, add `--at` with the moments to see:
only those frames are shot, and only that stretch is checked, so it takes
seconds instead of a full pass. Use it instead of writing a script to
screenshot or inspect the page.

The audit is the measurement of the layout, so the layout is written
before it is measured. Where a cut-out, a headline or a layer lands on
the stage is checked by writing the scenes and running `--at` on them,
never worked out beforehand by probing the materials with ffmpeg or
Python, or by reading the audit's code: what it relies on is section 3,
and each line it prints says what is wrong and where.

```bash
node scripts/render/audit.js <root>/editable/<name>.html --at 7400,8100,9000
```

It seeks the stage in the renderer's own view and prints `audit clean` or
one line per problem:

- `leak @t`: an element whose entry has not started is already visible
  (rule 10, a `stroke-dasharray` shorter than its path, a second
  animation without its own delay). Checked on the first frame and 0.4 s
  before each scene.
- `text @t`: a phrase or any other text (a headline, a pill, card copy)
  outside the safe zone, a caption over two lines, or a line holding a
  single short non-key word.
- `edge @t`: a frame-filling layer (a clip, a still, a painted
  background) that stops a sliver short of the canvas edge, or a cut-out
  whose cropped side ends inside the canvas.
- `font:` a font that failed to load, or text set only in system fonts.
- `cut-out:` talking-head clips on the stage with none of their cut-outs.
- `file:` a referenced file that is missing, or sits in `deletable/` or
  `jobs/`.
- `console:` a page error.
- `N video seeks timed out`: the browser was slow to decode a clip. It is
  not a problem in the editable: run the audit once more, and never
  remove, swap, or re-cut a clip because of it. IF it is still there,
  render anyway and say so in the final message.

The first audit of a video also prepares the all-keyframe copies of its
clips that the render uses (`intra: N encoded`), so it takes longer;
later audits and the render reuse them.

Each line says how to fix it; fix them all in as few edits as you can,
then run it the second time. It also writes
`materials/<name>/deletable/audit-sheet.jpg`: the first frame, each scene
0.6 s in, and the last frame, or the `--at` moments. Look at it on the
first run; it is the check a render would otherwise be spent on. The
tool's output is the whole interface: do not read its source.

## 8. Render

```bash
node scripts/render/render.js <root>/editable/<name>.html <root>/renders/<name>.mp4
```

Arguments are the editable and the output; there is no frame-rate
argument. The renderer reads `data-duration`, `#vo` and `#bgm` (with its
`data-gain-db`), and the
`.sfx` tags from the editable; there is nothing else to configure. It
moves an existing render to `renders/deletable/` first, captures every
frame in local Chrome in parallel chunks, mixes the audio (voice at -16
LUFS, effects under it, bed 10 dB under it, faded in 1 s and out 1.5 s), checks
the file (duration, frame count, stereo). Output is 1080 x 1920 H.264
with stereo AAC at 24 fps, the rate of Seedance clips, so each output
frame is one clip frame. A clip at any other rate repeats or drops
frames on the stage, which shows as the presenter juddering; the
renderer names such a clip in a warning (toolkit section 3, Frame rate).
The render is final as it comes out, with no cover or other step after
it.

Expect a few minutes for a video up to two minutes long; the capture
runs on this machine (`CM_RENDER_CONCURRENCY` browsers at once). IF it prints `check FAILED` or `video seeks
timed out`, fix the cause before anything else. Render once, after the
audit is clean and the sound effects are placed: every re-render is
another few minutes of capture.

## 9. Other aspect ratios

Default is 9:16. For another ratio change only `#stage { width; height }`
in CSS, `STAGE_W`, `STAGE_H` in the harness JS, and the `<title>`,
keeping the shorter side at 1080 px: 16:9 is 1920 x 1080, 1:1 is
1080 x 1080, 4:5 is 1080 x 1350. The safe zone and caption rules are
9:16 rules; place key elements by eye for other ratios.

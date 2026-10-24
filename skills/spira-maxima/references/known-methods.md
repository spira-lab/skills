---
name: known-methods
description: Methods proven to work and methods proven to fail in this package, each with the reason and a pointer to where the working way is written. Read before building; never re-pay for a failure recorded here.
---

# Known Methods

Each entry is a failure that has already cost time or credits, and the
method that replaced it. The instruction itself lives in the skill or
tool the entry points to; this file holds the why.

## Talking head on the stage

- **Works:** the alpha WebM cut-out placed as a `<video>` inside `#stage`
  with `data-start`. The harness drives it, and the renderer and the
  audit both swap in an all-keyframe copy so each frame costs one decode.
- **Fails:** extracting the clip to a frame sequence and stepping it
  with CSS: 775 frames, minutes of conversion, and a hand-written
  converter that hung for ten minutes. Also slow: the renderer seeking
  the original clip, which decodes from the last keyframe on every
  frame and took 120 s for a 29 s video against 48 s now. The audit
  seeking the original clips reported "video seeks timed out" on every
  run, and sessions cut clips out of scenes to silence it; it is a
  decoder hiccup now, fixed by running the audit again, never by
  changing the scenes.
- **Where:** stage-canvas-html, rule 11; `scripts/render/intra.js`.

## Writing the editable

- **Works:** 6 or 7 scenes planned up front, a skeleton, then two or
  three scenes per edit, written by hand from `timings.json`.
- **Fails:** the whole editable in one write (an 80 KB file takes minutes
  with nothing visible), a generator script that emits the html (paid for
  three times: writing, running, fixing), and ten scenes written one per
  edit with an audit after each: twenty minutes of round trips on staging
  for a 30-second video.
- **Where:** stage-canvas-html, section 3.

## Captions

- **Works:** `scripts/captions.py`: the script aligned to the timings,
  one-line phrases, restyled with CSS after its markers.
- **Fails:** captions written by hand inside every scene: 90 timed word
  spans per video, most of the audit's text problems (lonely words,
  third lines), and a round of fixes for each.
- **Where:** stage-canvas-html, section 6.

## Sound effects and the number of renders

- **Works:** `<audio class="sfx" data-at>` tags placed before the first
  render; the renderer mixes them. One render per video.
- **Fails:** rendering first, then mixing effects with a hand-written
  ffmpeg command and rendering again: two or three renders per video,
  two to four minutes each.
- **Where:** stage-canvas-html, section 5.

## Checking the stage

- **Works:** `scripts/render/audit.js` twice on the whole video, once with
  every scene written and once after the fixes, and `--at` for a quick
  look at a stretch while building (seconds, not a full pass).
- **Fails:** writing a Playwright screenshot or probe script in every
  session, and a full audit after every scene: on staging each full run
  grew from 1 s to 38 s as the file grew, sixteen times over.
- **Where:** stage-canvas-html, section 7.

## Waiting on a background batch

- **Works:** submit the clip batch, write the scene plan and timing-free
  CSS meanwhile, then one `spira ai jobs wait` per clip, each a
  background Bash command, all started in one turn.
- **Fails:** waiting with a `pgrep -f` loop (it matches itself and never
  ends: 10 minutes to the tool timeout on staging) or a guessed `sleep 150`.
- **Where:** toolkit, section 3e.

## Other runs in the same root

- **Works:** `scripts/new-video.sh`, which claims the video's number
  atomically, and touching only the editable this session created.
- **Fails:** adopting an editable found in the root as "a previous run
  interrupted": it was another run working at the same time, and the two
  overwrote each other's voice-over and html.
- **Where:** file-management, section 4.

## Music style

- **Works:** a `style` of genre, mood, tempo, and instruments only.
- **Fails:** a style naming the subject ("motorsport"): Suno rejects it
  as a producer tag, the CLI shows only `provider_error`, and blind
  retries fail the same way, minutes each.
- **Where:** toolkit, section 3g.

## Persona cut-outs

- **Works:** every talking-head clip cut out in one Bria batch, and the
  cut-out layered over most talking-head scenes: over an animated
  background or b-roll, in front of a headline, the room faded away.
- **Fails:** cutting out only the clips the scene plan showed as a
  cut-out: sessions planned none, and every video was the clip in its
  own room from start to end (content team review, 2026-09-29).
- **Where:** toolkit, section 3f; creative-video-production, section 5.

## Type

- **Works:** the families the style calls for from `assets/fonts/`, copied into
  the materials and declared with `@font-face`, with the reference's
  treatment (weight contrast, italic serif accent, key-word colour).
- **Fails:** setting everything in the installed Noto and DejaVu fonts:
  one plain sans in every video, whatever the style reference showed
  (content team review, 2026-09-29).
- **Where:** stage-canvas-html, section 3; `assets/fonts/fonts.md`.

## Layout on the stage

- **Works:** key elements on the stage grid (centre, thirds, 5% ticks),
  every text checked against the safe zone, and frame-filling layers
  run past all four edges; the audit checks all three.
- **Fails:** checking only the caption phrases: a headline ran past
  x 1005 into the icon column, and a talking-head clip stopped 60 px
  short of the right edge, both unflagged (content team review,
  2026-09-29).
- **Where:** creative-video-production, section 9; `scripts/render/inspect.js`.

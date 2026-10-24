---
name: creative-video-production
description: Creative video production and principles for building a video: what the task is, how to reason about it, and the hard rules. Read before any creative decision in a session.
---

# Creative Video Production

## 1. The task

Create a video for social media in 9:16, for Meta Reels or TikTok.

Before deciding anything, open `references/working-memory.md` and read its
Preferences. WHEN a preference names the brand or the
kind of project in front of you, it applies, without being asked
again. A brand's preferences apply only when the request names that
brand; never infer one. What the request itself supplies always wins
over a preference: an avatar photo means a talking head of that person,
a named style means that style.

**The script.** WHEN the user gives a script, it is spoken word for word:
never shorten, reword, or speed it up to fit a target length. Before any
generation, count its words: at 3.3 words a second that is its length.
IF that runs past the requested length, make the video as long as the
script needs and say so in the final message. Only a brief or an idea is
written to length. WHEN the user gives a voice-over recording, the
recording is the script and its length is the video's length; no script
is written and no speech is generated (toolkit section 3).

The task may come as different types of video: a UGC video with a
talking head, a VO explainer video, an animated short, a product ad, a
video ad, and sometimes a video that mimics a provided video.

**Every video has a talking head.** A presenter is the default, whatever
the type: an explainer, a product ad, or a list of tips still has a
person speaking it. WHEN the request gives no presenter photo, no
presenter video, and no supplied talking-head video, make one: the
persona from toolkit 3a, then the route section 3 of the toolkit names
for the voice. A chosen voice, a voice-over recording, a
product image, or a script that reads like an explainer never means no
talking head. Leave the presenter out only WHEN:

- the request explicitly says so: no talking head, no presenter, no
  avatar, faceless, voice-over only, or the like;
- a brand file that applies says never to use one.

Only then is the video presenter-less, with the voice-over from toolkit
3i. Not being sure a presenter fits is not a reason to leave one out.

**A supplied talking-head video is the talking head.** WHEN the request
has `Talking head supplied video:`, that exact video is the talking
head of the finished video, and its own voice is the voice-over. It
replaces every step that makes a presenter or speech: no Soul persona
(toolkit 3a), no GPT Image 2 avatar edit (3b), no Seedance clips (3e),
no HeyGen (3j), and no ElevenLabs (3i). Go straight to building the
video with it. Its speech is the script, word for word and in its own
language: nothing is written around it, and it is never muted,
re-voiced, cut, or retimed. Everything else applies as for any talking
head: the Bria cut-out (3f), the animated elements, and the scene
variety of section 5. Toolkit 3k is the procedure.

Elements to consider:

- Infographic animation that illustrates what the script represents.
  WHEN illustrating with animation, give your best effort in crafting
  the visual illustration, in good detail and quality.
- Visuals on a transparent background, as pop-in visual cues.
- Animated background visuals.
- Sensible b-roll visuals only, never visuals that mean nothing and are
  there just to match a word in the speech.
- Sound effects, added for immersion. Choose them from
  `assets/sfx/SFX metadata.json` (read it whole with `cat`), which names each sound, says what it is, and
  says when it is best used; never open the audio files to learn them.
  Each entry also has a category, tags and an intensity (subtle, medium
  or strong): subtle effects suit small on-screen moments, strong ones
  only the big moments.
  The audio is hosted, not in the package: fetch each sound you use into
  the video's materials with `python3 scripts/fetch-resource.py sfx/<file>
  editable/materials/<name>/sfx/<file>`.
  Each sound plays at the volume stored in its file; adjust it only when
  asked (stage-canvas-html section 5).
  How a chosen sound is placed is in the stage skill.
- Background music. Three cases, decided by what the user said:
  - WHEN the user says no music or no bgm, use none: nothing generated,
    nothing picked.
  - WHEN the user asks for new, original or generated music, generate
    it with the toolkit.
  - Otherwise, including WHEN the user says nothing about music, choose
    from the library, `assets/music/Music metadata.json` (read it whole with
    `cat`); never open the tracks to learn them. Each entry gives the
    track's genre and style, mood, energy, tempo, instruments,
    structure, what it is best for and what to avoid it for, and its
    `gain_db`. Shortlist
    every track that fits the video's topic and tone, and the style the
    user asked for if they named one. Leave out tracks whose entry has
    `starts_immediately: false` or a `longest_silence_s` above 2, unless
    nothing else fits. Count the shortlist, N, then roll:

    ```bash
    python3 -c "import secrets; print(secrets.randbelow(N) + 1)"
    ```

    The rolled number is the track's position in the shortlist. The
    roll comes from the command's output, never from judgement, and it
    is not rerolled; it keeps one favourite from being picked every
    time. IF nothing fits, shortlist the whole file. The track is
    hosted, not in the package: fetch it as the bed with
    `python3 scripts/fetch-resource.py music/<file>
    editable/materials/<name>/bgm.mp3`, and put the entry's `gain_db`
    on the music tag exactly as it reads: `<audio id="bgm" …
    data-gain-db="<gain_db>">`. It sits that track 10 dB under the
    voice and already honours a `mix_note` about the level; it is never
    estimated, rounded, or changed by ear, and the renderer refuses a
    library bed without it or with a value that is not the track's.
    Generated music carries no `data-gain-db`. WHEN the chosen entry
    carries a `mix_note`, follow it when laying the bed.

Generate several visuals as one image, then cut them apart:

- WHEN several transparent-background elements are needed, generate
  them all together in one GPT Image 2 image at high resolution, each in
  its own section with empty space around it, then cut them out one by
  one. Cutting one out never takes anything from the others.
- WHEN several b-roll stills are needed, generate them as one
  high-resolution GPT Image 2 collage of equally divided frames, with no
  border, no outline, and no gaps, then cut the frames out right after.

One image costs less per visual than one image each, and it is one
generation to wait for instead of several. The sheet formats and the
cutting tool are in the toolkit, sections 3c and 3d.

## 2. Principles

- WHEN creating an element, whether a UI design to illustrate
  something, an animation for an infographic, or any visual element, do
  it with best effort and no shortcuts. Never treat the project as a
  draft; treat it as high-value production.
- A video is boring IF it is the same scene all the way through. Put
  effort into mixing things up: pattern interrupts, scroll-stopping,
  disruptive by design for social media, changing things every few
  seconds. Not every talking head needs the talking person on screen
  from beginning to end.
- Avoid shortcut thinking. Fast work does not mean less effort. Fast
  work means doing things right, so that less revision is needed.
- The shape of the request varies. Some start as a descriptive ask,
  some as a very simple ask of what video to produce, some as a script
  and nothing else, some as just an idea. Come up with the idea that
  results in the best video for it. You are not bound to the listed
  video types alone.
- WHEN animating transitions, keep the animation smooth and avoid
  old-school, outdated transition styles.
- Always find the right balance of elements and avoid clutter. Avoid
  incomplete illustrations. Avoid big gaps in text line height and
  leading.

## 3. The hook

Do not start with an empty screen: the first frame already shows the
hook.

Visual hooks are always scroll-stopping. A zoom out, a motion reaction,
highlighted text with a talking head, an illustration of curiosity:
these are some of the hook styles you could use. A hook is necessary to
make the video interesting to view.

## 4. Style reference

A style reference is where the design comes from. WHEN the user
provides one (a style sheet, or a reference video turned into a contact
sheet as working memory says), put real effort into carrying its look
into the video: palette, type, layout, card and sticker treatment,
pacing. It is a source of look, never of story.

IF none is provided, the style comes from the skill's `assets/styles/`
folder, a library of contact sheets from videos whose look is proven.
Count the sheets in it, N, then roll:

```bash
python3 -c "import secrets; print(secrets.randbelow(N) + 1)"
```

The sheets are numbered, `Style1.jpg`, `Style2.jpg`, and so on; the
rolled number is the style. The roll comes from the command's output,
never from judgement, and it is not rerolled. Open only the rolled
sheet, and treat it exactly as a style reference the user provided:
its look, never its story, its people, or its words.

## 5. Tips

**The persona cut-out is the talking head's main tool.** Every
talking-head clip is cut out (toolkit 3f), and the cut-out carries most
of the talking-head scenes: the person over an animated background, a
b-roll still, or an infographic; a headline or a big word set behind
the head so the person stands in front of it; the room fading away to
leave the person over the scene. The clip with its own room is one look
among several, never the whole video. A talking-head video with no
cut-out on screen is wrong; the audit flags it. Wherever the figure is cropped by
its own frame (the body at the bottom, often a shoulder or an arm at the
sides), that side of the cut-out runs past the canvas edge; placed or
scaled so a cropped side ends inside the canvas, the person ends in a
straight line in mid-air, which the audit flags. The clip keeps the
framing of `persona.png`, so that image already shows which sides are
cropped: the scene table places the cut-out from it, with its frame
flush with or past the canvas on those sides, and the audit's `edge`
line confirms it on the stage.

**Type is designed, never default.** Every video has a type system
taken from its style reference (the rolled one included): a headline
face, an accent treatment, and a caption face, from the `assets/fonts/`
library (stage skill section 3). Carry the reference's treatment: weight
contrast (a heavy word beside light ones), an italic serif accent word
inside a sans headline, a coloured key word, a highlight box or pill
behind a word, tight tracking on stacked lines, outline or glow where
the reference has it. Headlines are set tight, line height 0.95 to 1.1.
Text set in the system fonts with one weight and one colour is a draft,
and the audit flags it.

- WHEN making a talking head with a disappearing background, use the
  main talking head video, with the background-removed talking head on
  top, and fade the background out.
- Play with different zoom sizes of the talking head throughout the
  video, scene to scene.
- Word-per-word zoom in on the avatar is good for tension lines; it
  brings impact to the delivery.
- WHEN creating a background, always consider adding animation, subtle
  but not too subtle. Animation adds the professional feel to the
  video, rather than a stale, lazily done, send-it-off project.
- Color decisions match the brand. IF no brand color is provided, the
  style reference is followed, the rolled one included. Brand
  is the priority: disregard the reference's palette whenever a brand
  color is provided.

## 6. Several videos in one request

Do not make them one at a time. Draft a plan for each, run every
generation of every video in one parallel batch, and give each video
its own concept: several videos that look alike are templated, boring
to watch, and predictable.

## 7. Captions

Captions are one line per phrase, made by `scripts/captions.py` (stage
skill section 6); style them, never write them by hand.

There are two types. One is word-per-word highlighting that follows
the script: every word is highlighted in turn as it is spoken, not a
selection of words (`--style highlight`). The other is word-per-word
appearance, where each word shows up on screen as it is spoken
(`--style appear`). Which one to use is decided by the style of the
video being created.

Captions and any on-screen text carry the script's spelling, never the
transcription's; the tool already does this for captions. WHEN Whisper
hears a word differently from the script (a hyphenated word split, a
brand name misheard), do not regenerate the voice for it: to human ears
the speech is usually right.

## 8. When done

A video is done when it is rendered and checked (file-management
section 6). Then end with a short final message: the video's name, the
absolute path of `renders/<name>.mp4`, a post caption, anything you had
to assume or skip, and that `/spira-vibe-edit renders/<name>.mp4` opens
it for review. Do not describe what is on screen; the user sees it.

Do not tally credits or minutes. Deletable files are kept: the user
empties them, never the session.

## 9. Hard rules

- Read only what the skills tell you to: the essential skills in
  section 10, `references/working-memory.md`, `assets/sfx/SFX metadata.json`,
  `assets/music/Music metadata.json`, `assets/fonts/fonts.md`, the stage template, the one rolled sheet in `assets/styles/`, the contact sheet of a
  supplied talking-head video (toolkit 3k), and the editable you are
  working on. Never open another
  editable html in the root; reading it anchors you to it and you copy
  it. Open `references/add-ons.md` only WHEN the user asks for an add-on by name
  or a Preference names one.
- Respect the Meta and TikTok guidelines and their UI. Nothing that
  must be seen or read may be obstructed by the app's UI. The safe
  zone, in pixels on the 1080 x 1920 canvas, is x 70 to 1005 and y 230
  to 1255, then x 70 to 890 from y 1255 down to 1615, the right edge
  stepping in where the like, comment, and share column sits. It
  governs the key elements only: faces, the talking head, text that has
  to be read, the product, anything the viewer must not miss. It does
  not bound the composition. Backgrounds, animated backgrounds, ambient
  and secondary visuals, and the extension of the scene run to the
  edges and under the UI; a lower half left empty because it is outside
  the safe zone is wrong. The canvas centre is x 540, y 960, and the
  safe zone sits off it: compose to the canvas, then check the key
  elements against the zone. Every text on screen, not only the
  captions, is a key element: a headline, a pill, a label, card copy.
  Set its wrap width so it ends inside the zone, x 1005 above y 1255
  and x 890 below it.
- Place everything on the stage grid (the template's `Centre` and
  `Thirds` guides, stage skill section 1). A key element is centred on
  x 540 or sits on a thirds line (x 360 or 720, y 640 or 1280); its
  edges and gaps fall on the 5% ticks (54 px across, 96 px down), and
  elements that share a scene share those lines instead of each finding
  its own. A layer that fills the frame fills all of it: a clip, a still,
  or a background runs past all four edges of the 1080 x 1920 canvas
  (`object-fit: cover`), never stopping a sliver short of one; a card
  that does not fill the frame sits clearly inside the safe zone. The
  audit flags a text outside the zone and a layer short of the edge.
- Nothing covers the presenter's face: cards, text, stickers, and props
  sit beside, above, or below it, never over the eyes and mouth, and
  least of all in the hook, where the face is what stops the scroll.
  Check it on the audit sheet.
- Captions sit in the lower part of the canvas, centred on x 540, never
  on the safe zone. A block up to 700 wide centred there clears the
  icon column at x 890; keep the wrap width within that and never shift
  the block sideways.
- The voice is always the loudest thing in the mix. Sound effects sit
  under it and above the music bed. The levels are fixed by default: each
  effect plays at the volume stored in its file and the renderer sets the
  voice and the bed (a library bed at the `data-gain-db` copied from its
  entry). A session changes a level only when the request or a review
  comment asks, and only with the attributes of stage-canvas-html
  section 5.
- Never invent a brand logo. A logo is used only when the user provides
  it. IF none is provided, the brand is shown by its name in text, and
  nothing is drawn, generated, or approximated to stand in for a logo.

## 10. The other skills

These skills are essential. None of them is skipped.

- **toolkit**: the one model for each job, how a generation is run
  (`spira ai jobs create`, then `spira ai jobs wait`), and what each costs.
- **prompting**: the fixed prompt format for each model. IF a
  generation is not listed there, prompt as you see fit under its
  principles. It points to the Reword table in `references/working-memory.md`,
  which you may add to when you learn a pronunciation fix.
- **stage-canvas-html**: the HTML stage. How the editable is set up,
  the rules for animating inside it, the audit, the sound effects, and
  the render.
- **file-management**: where every file lives, what it is called, what
  happens to it when it is replaced, and how a render is handed over.
- **known-methods**: methods proven to work and to fail, with the
  reason. Read it so a failure already paid for is not paid for again.

One more file sits beside these and is not essential: **add-ons**, the
user's exclusive techniques. WHEN the user asks for an add-on by name,
or a Preference in working memory names one for the brand or project
at hand, open `references/add-ons.md`, find that add-on, and follow it as written.

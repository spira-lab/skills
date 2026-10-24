# Add-ons

The user's exclusive skills. Each one is a named technique or procedure
that is used only when the user asks for it by name, or when a
Preference in working memory names it. Nothing here is applied on your
own judgement, and nothing here is read until one of those two happens.

WHEN an add-on is called for, find its section below and follow it as
written. IF the name is not here, do not improvise a version of it:
make the video without it and say so in the final message.

Each add-on is one section:

```
## <add-on name>

What it is for, in a line.

How it is done.
```

## Style ref contact sheet

For a video the user provides as a style reference, by URL or local
path. Produces one contact sheet of the frames that carry the video's
look, and nothing else.

```bash
scripts/style-sheet.sh "<url or local path>" editable/materials/<name>/deletable
```

It downloads a URL with yt-dlp into that folder (a local file is read in
place, never moved or copied), takes the opening frame and a frame at
every hard cut, keeps up to 20 spread over the whole video, and writes
`contact-sheet.jpg` there, four across.

IF yt-dlp cannot fetch a social post (TikTok, Instagram, YouTube), resolve
it with the CLI instead: `spira media video "<url>" --json` returns the
original file's direct URL; download it with
`curl -fsSL "<direct url>" -o editable/materials/<name>/deletable/reference.mp4`
and run the tool on that local file.

Hard rules:

- Open only `contact-sheet.jpg`. Never watch the video, read its other
  frames, or read its transcript: from then on you build its story
  instead of your own. The reference is for visual styling only, never
  for what the video is about.
- Take from it the look: palette, type, layout, card and sticker
  treatment, framing of the talking head, pacing of the cuts.

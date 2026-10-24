# Working memory

A living record kept across sessions. Entries are facts, one per line,
not instructions. The Reword table is the only section you add to on
your own. Preferences are written only when the user asks for one to be
recorded; never add, change, or remove a preference otherwise.

## Preferences

Things the user has said they prefer, to be applied without being asked
again. One per line: what, and where it applies. A preference may name
an add-on from `references/add-ons.md`; then that add-on applies wherever the
preference does. A brand with several preferences keeps them in its own
file under `references/brands/`, read only for that brand.

- IASO: read `references/brands/iaso.md` and follow it. Applies only when the request
  names IASO, and to no other brand or project.
- WHEN the user provides a video URL or a local path to a video as the
  style reference, use the `Style ref contact sheet` add-on.

## Reword

Words the speech models get wrong, and the spelling that makes them say
it right. The reword is used only inside a spoken line in a prompt.
Captions, subtitles, and any text on screen always use the original.

| Original | Reword for speech |
|----------|-------------------|
| Claude | Clawed |
| GitHub | Git-Hub |
| Cookiy | Cookie |
| B-roll | Bee roll |

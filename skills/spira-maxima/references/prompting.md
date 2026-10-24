---
name: prompting
description: How to write prompts for the generation models in the toolkit, and the fixed prompt format for each model. Use every time a prompt is written for Higgsfield Soul, GPT Image 2, or Seedance 1.5 Pro.
---

# Prompting

Prompts are written the same way every time so the output is steady.
The principles apply to every prompt; the formats below are filled in,
not rewritten.

## 1. Principles

1. **The simpler the prompt, the better.** Detail past what the shot
   needs causes drift: the model is forced into a scene or a pose it
   cannot resolve and hallucinates to satisfy the words. Describe the
   state, not the mechanics. Let the model decide how a body sits, how a
   hand rests, how light falls, and it produces the natural version.
2. **Be decisive. Never write "or".** A model cannot choose between two
   ideas. It leans on the first, or merges both, and the merge is a
   hallucination. One subject, one outfit, one setting, one action.
3. **UGC shots use no professional photography or cinematography
   language.** No lens, no focal length, no bokeh, no golden hour, no
   rule of thirds, no dolly, no rack focus, no colour grade. Those words
   force a professional look into the image and the motion and pull it
   away from a casual UGC shot. Casual does not mean candid: the person
   knows the phone is there and looks at it.
4. **No examples in a prompt.** A model anchors on an example and
   reproduces it instead of the thing asked for. State what is wanted
   directly.

## 2. Higgsfield Soul (`ai-influencer-image`)

Fill the slots. Drop a slot only where the format says it may be
dropped.

```
UGC Casually taken shot of one [age] [gender], alone in the frame, [pretty/handsome/cute good looking], [beautiful and attractive with a natural easy smile, or the description that fits], [hair style] in a [outfit style], [what it is not, when needed; remove if unnecessary]. [He/She] is wearing a [outfit detail]. [Framed from the legs up if standing, waist up if sitting], [standing/sitting] relaxed in [setting location] [daylight/night time], looking at the camera, no posing, no filters, no text
```

## 3. GPT Image 2, persona edit

The Soul output, or the user's photo on Auto voice (toolkit 3a), is the
reference. The prompt keeps everything and
changes only what is named.

```
Edit this photo. Keep the same person with the exact same face, hair, expression, skin, body, outfit, pose, room and lighting. Only change [the part that needs replacing]: replace it [replacement instruction]. Also reframe slightly so there is clear empty space above [his/her] head, roughly a head height of room between the top of [his/her] hair and the top of the frame, still framed from the [legs up/waist up]. Keep the casual quick phone snapshot look, no filters, no text
```

- The "Only change" sentence is included only when something must be
  edited or fixed. With nothing to change, omit it and the prompt is
  keep, reframe, keep the look.
- Whatever is being replaced comes out of the keep list. If the outfit
  changes, the first sentence no longer says "outfit"; if the hair
  changes, it no longer says "hair". Keeping and changing the same thing
  in one prompt is a contradiction the model resolves by drifting.
- When the persona holds or wears a product, the product image is the
  second reference and the holding or wearing lines from the toolkit go
  in the "Only change" sentence.

## 4. GPT Image 2, transparent background

Keep it very simple: say what the visual is, then instruct a
transparent background. Nothing else.

```
[the visual], on a transparent background, PNG with alpha, no backdrop, no shadow on the ground, no frame
```

## 5. Seedance 1.5 Pro, talking head

The cleaned persona image is the reference. The line is the script
chunk for this clip, sized per the toolkit.

```
The person says: “[line]”
The camera remain static and steady on position.
No camera movements, No sound effects, No special effects, No text on screen.
```

The line goes in without quotation marks of its own: take out any “ ” or
" " around words in the script (`The word “Ferrari”` becomes `The word
Ferrari`), or the presenter reads the quote marks as pauses and words.
Captions and on-screen text keep them.

## 6. Speech

WHEN a prompt carries words to be spoken, the Seedance line or a VO
script, the model will get some of them wrong: brand names, product
names, acronyms, unusual spellings, words borrowed from another
language. Before writing the prompt, open `references/working-memory.md`
and check its Reword section. Any word listed there goes into the
spoken line in its reword spelling, not its original.

IF you hear a word mispronounced in the output and it is not in the
list, find a spelling that makes the model say it right and add the
pair to the Reword table, so the next session does not repeat the
search.

The reword lives in the spoken line only. In the subtitle, the caption,
and any text on screen where the word appears, use the original word,
spelled as the user or the brand spells it. The viewer reads the real
word and hears it said right.

## 7. Edge case

Any generation that has no format above is prompted freely, as you see
fit, under the principles in section 1.

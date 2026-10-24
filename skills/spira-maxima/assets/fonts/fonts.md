# Fonts

The type library. Every font here is under the SIL Open Font License
(`licenses/`), free to embed in a video. Pick by what the style
reference's type looks like, not by name.

| Family | File | Weights | Looks like, use for |
|--------|------|---------|---------------------|
| Inter | `Inter.ttf`, `Inter-Italic.ttf` | 100-900, italic | Clean neutral grotesk: UI mockups, cards, labels, captions |
| Inter Tight | `InterTight.ttf` | 100-900 | Tightly set grotesk: bold stacked headlines, the modern creator look |
| Montserrat | `Montserrat.ttf`, `Montserrat-Italic.ttf` | 100-900, italic | Geometric, wide: loud captions, punchy headlines |
| Poppins | `Poppins-Bold.ttf`, `Poppins-ExtraBold.ttf`, `Poppins-Black.ttf` | 700, 800, 900 | Round geometric: friendly, UGC captions |
| Space Grotesk | `SpaceGrotesk.ttf` | 300-700 | Techy grotesk: AI, product, startup |
| Archivo Black | `ArchivoBlack.ttf` | 400 (heavy) | Heavy grotesk: one-word slams, highlight boxes |
| Anton | `Anton.ttf` | 400 (condensed heavy) | Tall condensed impact: hooks, big numbers |
| Bebas Neue | `BebasNeue.ttf` | 400 (caps only) | Condensed caps: labels, kickers, titles |
| Oswald | `Oswald.ttf` | 200-700 | Condensed grotesk: news, sport, data |
| Instrument Serif | `InstrumentSerif.ttf`, `InstrumentSerif-Italic.ttf` | 400, italic | Editorial serif: the italic accent word inside a sans headline |
| DM Serif Display | `DMSerifDisplay.ttf`, `DMSerifDisplay-Italic.ttf` | 400, italic | High-contrast display serif: elegant titles, quotes |
| Playfair Display | `PlayfairDisplay.ttf`, `PlayfairDisplay-Italic.ttf` | 400-900, italic | Classic display serif: luxury, storytelling |
| Caveat | `Caveat.ttf` | 400-700 | Handwriting: annotations, arrows' labels, notes |

Text in another script falls back on its own: the renderer has Noto Sans
for Cyrillic, Greek, Arabic, Hebrew, Devanagari, Tamil and Thai, and Noto
Sans CJK for Chinese, Japanese and Korean. Keep the library face for the
style; any character it lacks is drawn in the matching Noto face.

## Using one

Copy each file the video uses into `materials/<name>/fonts/`, then declare
it in the video CSS, one `@font-face` per file:

```css
@font-face { font-family: 'Inter Tight'; src: url('materials/<name>/fonts/InterTight.ttf'); font-weight: 100 900; }
@font-face { font-family: 'Instrument Serif'; src: url('materials/<name>/fonts/InstrumentSerif-Italic.ttf'); font-style: italic; }
```

A variable file (a weight range in the table) declares its range as
`font-weight: <min> <max>`; a file with one weight declares that weight.
An italic file is declared with `font-style: italic` under the same
family as its upright.

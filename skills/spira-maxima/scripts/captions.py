#!/usr/bin/env python3
"""Word-per-word captions for an editable, from its timings and its script.

  python3 scripts/captions.py <root>/editable/<name>.html [--style highlight|appear]
      [--top 1390] [--size 66] [--color #fff] [--hl #ffcf33] [--max-chars N per line]

Reads materials/<name>/timings.json (Whisper) and materials/<name>/script.txt.
Each caption word carries the script's spelling and Whisper's timing: the two
are aligned word by word, so a word Whisper heard differently ("precision in
your" for "precision-engineered") is written as the script has it, timed over
what Whisper heard there. Each phrase is one line of two to four words, split
where the sentence reads best (commas and pauses, never ending on "the" or
"and"), and scaled down if it is wider than the 700 px block. Any language works:
a script written without spaces (Chinese, Japanese, Thai) is captioned character by
character, preferring breaks where Whisper heard a word end, and a right-to-left
phrase (Arabic, Hebrew) runs right to left. A phrase shows
from its first word until the next phrase starts; the last one holds to the end.

  highlight  every word lights up in turn as it is spoken (default)
  appear     each word appears as it is spoken and stays

The markup and CSS go between `captions:start` / `captions:end` markers in the
editable, replaced on every run, so re-run it after the VO or the script
changes. Restyle captions with CSS after the marker block: #captions (the
layer), .cc-phrase (one phrase: position, size, colour), .cc-phrase .w (a
word), and the ccHl keyframes for the highlight. Do not edit inside the
markers, and do not reuse the cc- names for anything else.
"""
import argparse, difflib, html, json, pathlib, re, sys, unicodedata

# Scripts written without spaces between words (Chinese, Japanese, Thai, Lao, Khmer, Myanmar): each
# character, with its combining marks, is a caption unit of its own, set with no space around it.
TIGHT = re.compile("[\u0e00-\u0eff\u1000-\u109f\u1780-\u17ff\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
RTL = re.compile("[\u0590-\u08ff\ufb1d-\ufdff\ufe70-\ufeff]")


def norm(tok):
    """Letters, digits and marks of any script, case- and width-folded."""
    return "".join(c for c in unicodedata.normalize("NFKC", tok).lower() if unicodedata.category(c)[0] in "LNM")


def units(chunk):
    """Split one whitespace-free chunk into caption units: a run of spaced-script characters stays
    whole, a tight-script character stands alone, and punctuation and marks join the unit before."""
    out = []
    for c in chunk:
        cat = unicodedata.category(c)[0]
        tight = bool(TIGHT.match(c))
        if out and (cat in "MPS" or (not tight and not out[-1]["tight"] and cat not in "Z")):
            out[-1]["w"] += c
        elif out and cat not in "LN" and not tight:
            out[-1]["w"] += c
        else:
            out.append({"w": c, "tight": tight})
    return out


def script_words(text):
    """Script words as written, each with the sub-tokens Whisper would hear."""
    words = []
    for chunk in text.split():
        for k, u in enumerate(units(chunk)):
            subs = [norm(p) for p in re.split(r"[-‐-―/]", u["w"])]
            subs = [s for s in subs if s]
            if subs:  # sp: the script has a space before it
                words.append({"w": u["w"], "tight": u["tight"], "sp": k == 0 and bool(words), "subs": subs})
            elif words:  # a lone mark such as "—": keep it on the word before
                words[-1]["w"] += (" " if k == 0 else "") + u["w"]
    return words


def heard_subs(tok):
    """Whisper's word, split the way the script is, so a tight-script word matches character by character."""
    return [s for u in units(tok) for s in (norm(p) for p in re.split(r"[-‐-―/]", u["w"])) if s]


def join(ws):
    """The words of a phrase as one line of text, spaced where the script is."""
    return "".join((" " if i and w["sp"] else "") + w["w"] for i, w in enumerate(ws))


def width(text):
    """Line length in half-width characters: a wide (CJK, Hangul) character counts twice."""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in text)


def align(words, timed):
    """Give each script word a start and end from the Whisper words."""
    subs, owner = [], []
    for i, w in enumerate(words):
        for s in w["subs"]:
            subs.append(s)
            owner.append(i)
    heard = []
    for t in timed:
        subs_t = heard_subs(t["w"])
        for k, s in enumerate(subs_t):  # a word heard as several units shares its time between them
            d = (t["e"] - t["s"]) / len(subs_t)
            heard.append((s, t["s"] + d * k, t["s"] + d * (k + 1), k == len(subs_t) - 1))
    sm = difflib.SequenceMatcher(a=subs, b=[h[0] for h in heard], autojunk=False)
    span = [None] * len(subs)
    ends = [True] * len(subs)  # the unit ends a word Whisper heard: in a tight script, the best place to break
    for op, a0, a1, b0, b1 in sm.get_opcodes():
        if op == "equal":
            for k in range(a1 - a0):
                span[a0 + k] = (heard[b0 + k][1], heard[b0 + k][2])
                ends[a0 + k] = heard[b0 + k][3]
        elif op == "replace" or (op == "delete" and b0 > 0):
            # Spread the stretch Whisper heard differently over the script's words.
            s0 = heard[b0][1] if b0 < len(heard) else heard[-1][2]
            s1 = heard[b1 - 1][2] if b1 > b0 else s0
            n = a1 - a0
            for k in range(n):
                span[a0 + k] = (s0 + (s1 - s0) * k / n, s0 + (s1 - s0) * (k + 1) / n)
        elif op == "delete":
            for k in range(a1 - a0):
                span[a0 + k] = (heard[0][1], heard[0][1])
    out = []
    for i, w in enumerate(words):
        own = [span[j] for j in range(len(subs)) if owner[j] == i and span[j]]
        s = min(x[0] for x in own) if own else (out[-1]["e"] if out else 0.0)
        e = max(x[1] for x in own) if own else s
        last = max((j for j in range(len(subs)) if owner[j] == i), default=None)
        out.append({"w": w["w"], "tight": w["tight"], "sp": w["sp"], "wend": last is None or ends[last],
                    "s": round(s, 2), "e": round(max(e, s + 0.05), 2)})
    for a, b in zip(out, out[1:]):  # keep time moving forward
        if b["s"] < a["s"]:
            b["s"] = a["s"]
    return out


# A phrase never ends on one of these: it leaves the reader hanging.
FUNCTION_WORDS = {"a", "an", "the", "and", "or", "but", "of", "to", "in", "on", "at", "for", "with",
                  "by", "from", "as", "is", "are", "was", "that", "which", "its", "their", "our", "your", "my"}
END = re.compile(r"[.!?。！？؟।॥]['\"”’」』）)]?$")
SOFT = re.compile(r"[,;:，、；：،؛]['\"”’」』）)]?$")


def phrase_cost(ws, line, last_in_sentence):
    """How bad a one-line phrase is on screen; None when it is far too long for the line."""
    text = join(ws)
    n, length = len(ws), width(text)
    if length > 1.4 * line:
        return None
    cost = max(0.0, length - line) * 0.4  # over the line it gets scaled down to fit
    if n == 1 and not (last_in_sentence and width(ws[0]["w"]) > 6):
        cost += 4
    if norm(ws[-1]["w"]) in FUNCTION_WORDS and not last_in_sentence:
        cost += 5
    if not last_in_sentence:
        cost += 0 if SOFT.search(ws[-1]["w"]) else 1.5
        if ws[-1]["tight"] and not ws[-1]["wend"]:  # inside a word of a tight script
            cost += 4
    if ws[-1]["e"] - ws[0]["s"] < 0.5:  # gone before it can be read
        cost += 2
    return cost + 0.6  # each phrase costs a little, so they do not get too short


def phrases(words, line):
    """Split each sentence into the cheapest run of one-line phrases."""
    sentences, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        # A space in a tight script separates clauses, as a full stop does.
        clause = nxt is not None and nxt["sp"] and w["tight"] and nxt["tight"]
        if nxt is None or END.search(w["w"]) or nxt["s"] - w["e"] > 0.6 or clause:
            sentences.append(cur)
            cur = []
    groups = []
    for sent in sentences:
        n = len(sent)
        best = [0.0] + [float("inf")] * n
        back = [0] * (n + 1)
        for j in range(1, n + 1):
            # Up to 8 spaced words, or as many tight characters as fit the line.
            for i in range(max(0, j - (24 if sent[j - 1]["tight"] else 8)), j):
                c = phrase_cost(sent[i:j], line, j == n)
                if c is not None and best[i] + c < best[j]:
                    best[j], back[j] = best[i] + c, i
        cuts, j = [], n
        while j > 0:
            cuts.append((back[j], j))
            j = back[j]
        groups += [sent[a:b] for a, b in reversed(cuts)]
    return groups


def build(groups, style, top, size, color, hl):
    rows = []
    for gi, g in enumerate(groups):
        start = g[0]["s"]
        stop = groups[gi + 1][0]["s"] if gi + 1 < len(groups) else None
        ws = []
        for i, w in enumerate(g):
            dur = max(w["e"] - w["s"], 0.08)
            cls = "w t" if w["tight"] else "w"
            gap = " " if i and w["sp"] else ""
            ws.append(f'{gap}<i class="{cls}" style="animation-delay:{w["s"]:.2f}s;animation-duration:{dur:.2f}s">{html.escape(w["w"])}</i>')
        # entry on the phrase, exit on its inner span (stage rule 10); the last phrase has no exit
        body = f'<span class="cc-body out" style="animation-delay:{max(stop - 0.04, start):.2f}s">' if stop is not None \
            else '<span class="cc-body">'
        rtl = ' dir="rtl"' if any(RTL.search(w["w"]) for w in g) else ""  # right-to-left words run right to left
        rows.append(f'    <div class="cc-phrase"{rtl} style="animation-delay:{start:.2f}s">{body}<span class="cc-fit">{"".join(ws)}</span></span></div>')
    # One line each: a phrase wider than the block overflows to the right, so it is pulled
    # back to the centre and scaled down to fit once fonts are in.
    # Layout, not timing, so it runs once and never on the clock.
    fit = ("  <script>document.fonts.ready.then(function () { document.querySelectorAll('#captions .cc-fit')"
           ".forEach(function (el) { var w = el.offsetWidth; if (w > 680) el.style.transform ="
           " 'translateX(' + (350 - w / 2) + 'px) scale(' + (680 / w) + ')'; }); });</script>\n")
    markup = "  <!-- captions:start (scripts/captions.py; restyle with CSS after the marker, never edit inside) -->\n" \
             "  <div id=\"captions\">\n" + "\n".join(rows) + "\n  </div>\n" + fit + "  <!-- captions:end -->\n"
    word_anim = "ccHl" if style == "highlight" else "ccAppear"
    css = f"""  /* captions:start (scripts/captions.py) */
  #captions {{ position: absolute; inset: 0; z-index: 900; pointer-events: none; }}
  #captions .cc-phrase {{ position: absolute; left: 190px; width: 700px; top: {top}px; text-align: center;
    font-weight: 900; font-size: {size}px; line-height: 1.1; color: {color}; white-space: nowrap;
    -webkit-text-stroke: 5px rgba(0,0,0,.55); paint-order: stroke fill;
    text-shadow: 0 0 3px rgba(0,0,0,.9), 0 3px 14px rgba(0,0,0,.75); animation: ccIn .16s ease-out both; }}
  #captions .cc-body {{ display: block; }}
  #captions .cc-fit {{ display: inline-block; transform-origin: 50% 50%; }}
  #captions .cc-body.out {{ animation: ccOut .04s linear both; }}
  #captions .w {{ font-style: normal; display: inline-block; margin: 0 .09em; animation-name: {word_anim}; animation-timing-function: linear; animation-fill-mode: both; }}
  #captions .w.t {{ margin: 0; }}
  @keyframes ccIn {{ from {{ opacity: 0; transform: translateY(20px) scale(.95); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes ccOut {{ from {{ opacity: 1; }} to {{ opacity: 0; }} }}
  /* colour only: a scaled word would grow into the space beside it (a transform does not move its neighbours) */
  @keyframes ccHl {{ 0% {{ color: {color}; }} 1%, 99% {{ color: {hl}; }} 100% {{ color: {color}; }} }}
  @keyframes ccAppear {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: none; }} }}
  /* captions:end */
"""
    return markup, css


def replace_block(text, start, end, block, anchor, before=True):
    pat = re.compile(re.escape(start) + r".*?" + re.escape(end) + r"[^\n]*\n?", re.S)
    if pat.search(text):
        return pat.sub(lambda _: block, text, count=1)
    i = text.find(anchor)
    if i < 0:
        sys.exit(f"captions: cannot find {anchor!r} in the editable")
    if not before:
        i = text.index("\n", i) + 1
    return text[:i] + block + text[i:]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("editable")
    ap.add_argument("--style", choices=["highlight", "appear"], default="highlight")
    ap.add_argument("--top", type=int, default=1390)
    ap.add_argument("--size", type=int, default=66)
    ap.add_argument("--color", default="#fff")
    ap.add_argument("--hl", default="#ffcf33")
    ap.add_argument("--max-chars", type=int, default=0,
                    help="characters per caption line; default fits the 700 px block at --size")
    a = ap.parse_args()
    ed = pathlib.Path(a.editable).resolve()
    name = ed.stem
    mat = ed.parent / "materials" / name
    timed = json.loads((mat / "timings.json").read_text())["words"]
    script = (mat / "script.txt").read_text()
    words = align(script_words(script), timed)
    # A heavy caption face runs about 0.55 em per half-width character across the 700 px block.
    line = a.max_chars or int(700 / (a.size * 0.55))
    groups = phrases(words, line)
    markup, css = build(groups, a.style, a.top, a.size, a.color, a.hl)
    text = ed.read_text()
    text = replace_block(text, "/* captions:start", "/* captions:end */", css, "/* ---------- Video content styles go below ---------- */", before=False)
    text = replace_block(text, "<!-- captions:start", "<!-- captions:end -->", markup, "<!-- ---------- Guide layers")
    ed.write_text(text)
    print(f"{len(words)} words in {len(groups)} phrases, {a.style}, top {a.top}px")
    for g in groups:
        print(f"  {g[0]['s']:6.2f}s  {join(g)}")


if __name__ == "__main__":
    main()

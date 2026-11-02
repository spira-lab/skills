# Syllables-per-second chunker for the talking-head clips (toolkit 3e). The script is
# never changed; only clip lengths adapt. Split at sentence ends, group sentences into
# chunks, and give each chunk a clip length so its syllables per second land in the band.
# WHEN no grouping of whole sentences lands in the target, a chunk may also end at a
# comma, colon, semicolon or dash: the fewest such breaks that reach the target.
#   target   4.7-5.0 SPS  (natural pace, ends on time, smooth joins)
#   fallback 4.0-5.2 SPS  (only when no grouping lands in the target)
#   ceiling  5.2 SPS      (never exceeded; above this Omni cuts lines off or rewrites them)
# Chunks under 4.0 are allowed only as a last resort and are flagged (silence risk).
#   --model omni      gemini-omni-flash-1.1 clips of 4/6/8/10 s (the default and only model)
#
# Syllables are counted by rules built into this file: no dictionary, no installs,
# plain Python 3. Copy this one file anywhere. Numbers and % are read out as words,
# capital abbreviations are spelled (AI = 2), and compounds split (ChatGPT = chat + G P T).
#   python3 scripts/chunker.py <script.txt|script.json> [plan.json]
# A .json script may add {"syllables": {"word": n}} to override any count.
# Checked against the CMU dictionary: 98% of everyday words exact, scripts within 3%.
import json, re, sys
from functools import lru_cache

TARGET = (4.7, 5.0)
FALLBACK = (4.0, 5.2)
CEILING = 5.2
# Listed Spira credits per clip at 1080p (spira ai models get <id>, 2026-10-20).
MODELS = {
    'omni': {4: 41, 6: 54, 8: 68, 10: 81},                  # gemini-omni-flash-1.1
}
CLIPS = MODELS['omni']
MID = sum(TARGET) / 2

ONES = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()
TENS = 'twenty thirty forty fifty sixty seventy eighty ninety'.split()

def number_words(n):
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10 - 2] + ('' if n % 10 == 0 else ' ' + ONES[n % 10])
    if n < 1000:
        return ONES[n // 100] + ' hundred' + ('' if n % 100 == 0 else ' ' + number_words(n % 100))
    if n < 1000000:
        return number_words(n // 1000) + ' thousand' + ('' if n % 1000 == 0 else ' ' + number_words(n % 1000))
    return ' '.join(ONES[int(d)] for d in str(n))

def spoken(text):
    """Write numbers and symbols the way they are said."""
    text = re.sub(r'(?<=\d),(?=\d{3}\b)', '', text)  # 3,000 is three thousand, not three zero
    text = re.sub(r'(\d+)%', lambda m: m.group(1) + ' percent', text)
    text = re.sub(r'\$(\d+)', lambda m: m.group(1) + ' dollars', text)
    text = text.replace('&', ' and ')
    return re.sub(r'\d+', lambda m: number_words(int(m.group())), text)

def sentences(text):
    found = re.findall(r'[^.!?]+[.!?]+', text)
    rest = text[sum(len(f) for f in found):].strip()  # a last sentence with no full stop
    return [s.strip() for s in found + ([rest] if rest else []) if s.strip()]

def units(text):
    """(piece, ends_sentence): each sentence, split again after , ; : and dashes."""
    out = []
    for sent in sentences(text):
        parts = [x for x in re.split(r'(?<=[,;:\u2014])\s+|\s+(?=[\u2014-]\s)', sent) if x.strip()]
        for k, part in enumerate(parts):
            out.append((part.strip(), k == len(parts) - 1))
    return out

def words(s):
    return re.findall(r"[A-Za-z0-9'’]+", spoken(s).replace('-', ' '))

# Words the rules get wrong. Add brand names and odd words here as they come up.
EXCEPTIONS = {
    'nike': 2, 'facebook': 2, 'youtube': 2, 'ok': 2, 'okay': 2, 'hours': 2, 'hour': 2,
    'our': 2, 'fire': 2, 'every': 2, 'everything': 3, 'everyone': 3, 'business': 2,
    'different': 3, 'pipeline': 2, 'files': 1, 'vs': 2, 'creators': 3, 'create': 2,
    'created': 3, 'idea': 3, 'ideas': 3, 'real': 1, 'really': 2, 'area': 3, 'video': 3,
    'videos': 3, 'people': 2, 'little': 2, 'gonna': 2, 'wanna': 2, 'gotta': 2,
    'actually': 4, 'usually': 4, 'intuitive': 4, 'spira': 2, 'maxima': 3,
}
SUB = re.compile(r'cial|tia|cius|cious|giu|ion|iou|sia$|ely$|[^aeiouytd]ed$|[^aeiouylsxzh]es$|[^aeiouy]e$|^ye|ue$')
ADD = re.compile(r'ia|riet|dien|iu|io|ii|[aeiouym]bl$|[aeiou]{3}|^mc|ism$|([^aeiouy])\1l$|[^l]lien|^coa[dglx].|[^gq]ua[^auieo]|dnt$|uity$|ie(r|st)$|[aeiouy]ing$|eo|[^aeiou]y[aeiou]|[cg]es$')

def rule_syllables(word):
    w = re.sub(r'[^a-z]', '', word.lower())
    if not w:
        return 0
    if w in EXCEPTIONS:
        return EXCEPTIONS[w]
    if len(w) <= 3:
        return 1
    n = len([g for g in re.split(r'[^aeiouy]+', w) if g])
    n -= len(SUB.findall(w))
    n += len(ADD.findall(w))
    if re.search(r'[^aeiouyl]le[sd]?$', w):
        n += 1  # bottle, single, angle, garbled: the -le is its own syllable
    return max(1, n)

def syllables(word, overrides):
    w = word.lower().replace('’', "'")
    if w in overrides:
        return overrides[w]
    if word.isupper() and len(word) > 1:  # AI, UGC: said letter by letter
        return sum(3 if c == 'W' else 1 for c in word)
    # CapCut -> Cap + Cut, ChatGPT -> Chat + G P T; capital runs are spelled out.
    # Apostrophes are dropped first so contractions (that's, you're) stay one word.
    parts = re.findall(r'[A-Z]{2,}(?![a-z])|[A-Z]?[a-z]+|[A-Z]', re.sub(r"['’]", '', word))
    if len(parts) > 1:
        return sum(sum(3 if c == 'W' else 1 for c in p) if p.isupper() else rule_syllables(p) for p in parts)
    return rule_syllables(w)

def band(sps):
    if TARGET[0] <= sps <= TARGET[1]:
        return 'target'
    if FALLBACK[0] <= sps <= FALLBACK[1]:
        return 'fallback'
    return 'slow'  # under 4.0; over the ceiling is never chosen

PENALTY = {'target': 0, 'fallback': 1, 'slow': 5}

def plan(text, overrides=None):
    """overrides: optional dict word(lowercase) -> syllables."""
    overrides = {k.lower(): v for k, v in (overrides or {}).items()}
    pieces = units(text)
    sents = [u for u, _ in pieces]
    ends = [e for _, e in pieces]
    n_syl = [sum(syllables(w, overrides) for w in words(s)) for s in sents]

    def options(total):
        # every clip that keeps the chunk at or under the ceiling
        return [d for d in sorted(CLIPS) if total / d <= CEILING]

    @lru_cache(None)
    def best(i):
        # score = (band penalties, mid-sentence breaks, listed cost, distance from target middle)
        if i == len(sents):
            return ((0, 0, 0.0, 0.0), ())
        out = None
        for j in range(i + 1, len(sents) + 1):
            total = sum(n_syl[i:j])
            opts = options(total)
            if not opts:
                break  # adding more sentences only makes it denser
            rest_score, rest = best(j)
            for d in opts:
                sps = total / d
                score = (rest_score[0] + PENALTY[band(sps)],
                         rest_score[1] + (0 if ends[j - 1] else 1),
                         rest_score[2] + CLIPS[d],
                         rest_score[3] + abs(sps - MID))
                cand = (score, ((i, j, d),) + rest)
                if out is None or cand[0] < out[0]:
                    out = cand
        if out is None:
            raise SystemExit(f'"{sents[i][:60]}" alone is over {CEILING * max(CLIPS):.0f} syllables with no comma to break at; split it')
        return out

    (_, _, cost, _), chunks = best(0)
    res = []
    for i, j, d in chunks:
        t = ' '.join(sents[i:j]); s = sum(n_syl[i:j]); w = len(words(t))
        res.append({'text': t, 'duration': d, 'syllables': s, 'sps': round(s / d, 2),
                    'band': band(s / d), 'words': w, 'wps': round(w / d, 2)})
    return cost, res

if __name__ == '__main__':
    args = sys.argv[1:]
    if '--model' in args:
        k = args.index('--model'); model = args[k + 1] if k + 1 < len(args) else ''
        if model not in MODELS:
            sys.exit(f'--model is one of {", ".join(MODELS)}')
        CLIPS = MODELS[model]; del args[k:k + 2]
    if not args:
        sys.exit(__doc__ or 'usage: python3 scripts/chunker.py <script.txt|script.json> [plan.json]')
    sys.argv = [sys.argv[0]] + args
    src = sys.argv[1]
    if src.endswith('.json'):
        cfg = json.load(open(src))
        cost, res = plan(cfg['text'], cfg.get('syllables'))
    else:
        cost, res = plan(open(src).read())
    for k, c in enumerate(res, 1):
        flag = {'target': '', 'fallback': '  [fallback]', 'slow': '  [UNDER 4.0: silence risk]'}[c['band']]
        print(f"chunk {k}: {c['duration']} s | {c['syllables']} syl ({c['sps']}/s){flag} | {c['words']} words ({c['wps']}/s) | {c['text']}")
    print(f'total {sum(c["duration"] for c in res)} s, {cost} credits (listed)')
    if len(sys.argv) > 2:
        json.dump(res, open(sys.argv[2], 'w'), indent=1)

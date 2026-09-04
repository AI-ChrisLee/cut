#!/usr/bin/env python3
"""Re-cut a caption file into one short line per cue.

Descript decides where its own captions break and exposes no control over it,
so a whole paragraph can land on screen as a three-line block. This takes its
SRT and breaks it again on meaning: after a comma or a full stop, before a
conjunction, and never past 40 characters.

Time inside a cue is split by character count. That is an approximation of
where each word falls, and it is close enough because the cues being split are
short to begin with; the alternative is word timings Descript does not give.
"""
import re, sys

MAXC   = 40     # characters on the one line
MINDUR = 0.60   # a cue shorter than this is a flash, so it merges
BREAK  = re.compile(r"(?<=[.!?])\s+|(?<=,)\s+|\s+(?=(?:and|but|so|or|then|because|when|if)\b)", re.I)

def parse(path):
    out = []
    for block in re.split(r"\n\s*\n", open(path).read().strip()):
        L = block.strip().split("\n")
        if len(L) < 3: continue
        m = re.match(r"([\d:,]+)\s*-->\s*([\d:,]+)", L[1])
        if not m: continue
        out.append([ts(m.group(1)), ts(m.group(2)), " ".join(L[2:]).strip()])
    return out

def ts(s):
    h, m, rest = s.split(":"); sec, ms = rest.split(",")
    return int(h)*3600 + int(m)*60 + int(sec) + int(ms)/1000

def fmt(t):
    h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:06.3f}".replace(".", ",")

DANGLE = {"a","an","the","my","your","our","and","or","but","of","to","in","on",
          "at","it","is","was","for","with","that","this","so","as","by","from"}
SLACK  = 5      # a line may run this far over rather than orphan one word

def widen(p):
    """split one over-long piece, preferring punctuation, then a clean word"""
    out = []
    while len(p) > MAXC + SLACK + 4:
        window = p[:MAXC + 1]
        cut = max(window.rfind(". "), window.rfind(", "), window.rfind("? "),
                  window.rfind("! "), window.rfind(": "))
        if cut > MAXC * 0.45:
            cut += 1                       # keep the mark on the line it ends
        else:
            cut = p.rfind(" ", 0, MAXC + 1)
            if cut <= 0:
                cut = MAXC
            else:
                head = p[:cut].split()     # never end a line on a hanging word
                while len(head) > 2 and head[-1].lower().strip(",.") in DANGLE:
                    head.pop()
                    cut = len(" ".join(head))
        out.append(p[:cut].strip())
        p = p[cut:].strip()
    if p:
        out.append(p)
    return out

SENT = re.compile(r"(?<=[.!?])\s+")

def chunks(text):
    """One caption never spans two sentences.

    Sentences split first, and nothing is ever recombined across that boundary.
    Inside a sentence the break goes to meaning, then to width, and a line
    never ends on a hanging function word.
    """
    out = []
    for sentence in SENT.split(text):
        sentence = sentence.strip()
        if not sentence:
            continue
        parts, buf = [], ""
        for piece in BREAK.split(sentence):
            piece = piece.strip()
            if not piece:
                continue
            cand = f"{buf} {piece}".strip()
            if len(cand) <= MAXC + SLACK:
                buf = cand
            else:
                if buf:
                    parts.append(buf)
                buf = piece
        if buf:
            parts.append(buf)
        out += [c for p in parts for c in widen(p)]
    return out

cues = []
for t0, t1, text in parse(sys.argv[1]):
    text = re.sub(r'\s+([,.!?])', r'\1', re.sub(r'"\s+', '"', text))
    ps = chunks(text)
    if not ps: continue
    total = sum(len(p) for p in ps)
    at = t0
    for p in ps:
        share = (t1 - t0) * len(p) / total
        cues.append([at, at + share, p])
        at += share

# a flash-length cue folds into its neighbour rather than blinking
merged = []
for c in cues:
    if merged and (c[1] - c[0] < MINDUR or len(c[2]) <= 3) \
       and not merged[-1][2].rstrip().endswith((".", "!", "?")) \
       and len(merged[-1][2]) + len(c[2]) + 1 <= MAXC + SLACK:
        merged[-1][1] = c[1]
        merged[-1][2] = f"{merged[-1][2]} {c[2]}"
    else:
        merged.append(c)

# a stub that could not join the cue before it joins the one after instead,
# which is what rescues the two words left at the head of a new sentence
fwd = []
for c in reversed(merged):
    if fwd and (len(c[2]) <= 14 or c[1] - c[0] < MINDUR) \
       and not c[2].rstrip().endswith((".", "!", "?")) \
       and len(c[2]) + len(fwd[-1][2]) + 1 <= MAXC + SLACK:
        fwd[-1][0] = c[0]
        fwd[-1][2] = f"{c[2]} {fwd[-1][2]}"
    else:
        fwd.append(c)
merged = list(reversed(fwd))

# a cue that still sits under the flash threshold borrows from the gap ahead
for i, c in enumerate(merged):
    if c[1] - c[0] < MINDUR:
        room = (merged[i+1][0] - c[1]) if i + 1 < len(merged) else 0.4
        c[1] += min(room, MINDUR - (c[1] - c[0]))

with open(sys.argv[2], "w") as f:
    for i, (a, b, t) in enumerate(merged, 1):
        f.write(f"{i}\n{fmt(a)} --> {fmt(b)}\n{t}\n\n")

lens = [len(t) for _, _, t in merged]
durs = [b - a for a, b, _ in merged]
print(f"{len(cues)} -> {len(merged)} cues after merging flashes")
print(f"longest line {max(lens)} chars · average {sum(lens)/len(lens):.0f}")
print(f"shortest cue {min(durs):.2f}s · average {sum(durs)/len(durs):.2f}s")
print(f"over {MAXC} chars: {sum(1 for l in lens if l > MAXC)}")

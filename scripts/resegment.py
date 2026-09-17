#!/usr/bin/env python3
"""Re-cut a caption file into one short line per cue.

Descript decides where its own captions break and exposes no control over it,
so a whole paragraph can land on screen as a three-line block. This takes its
SRT and breaks it again on meaning: after a comma or a full stop, before a
conjunction, near the middle of a long piece, never after a hanging word, and
never past 45 characters.

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

HANG = DANGLE | {"be","been","are","were","am","will","can","could","would","should","may","might",
                 "have","has","had","not","never","even","just","very","how","what","who","when","where",
                 "their","his","her","its","new","every","each","no","more","most","into","about","than",
                 "own","many","much","few"}
HANG |= {"i","we","they","he","she"}   # "what they / said"
PARTICLE = {"up","down","back","away","it","them","him","me","us"}   # never the first word of a line: "pick / up", "call / it"
AFTER_IT = {"a","an","the","to","for","with","and","but","or","so"}   # "call it / the call rate"
AFTER_IN = {"are","is","was","were","will","can","and","but","or","so","to"}   # "coming in / are", never "coming / in are"

def widen(p):
    """split one over-long piece near its middle, never after a hanging word"""
    if len(p) <= MAXC + SLACK:
        return [p]
    spaces = [i for i, ch in enumerate(p) if ch == " "]
    def ok(i):
        head, tail = p[:i].split(), p[i+1:].split()
        if len(head) < 2 or len(tail) < 2: return False
        h, t0, t1 = head[-1].lower().strip(",.:;"), tail[0].lower().strip(",.:;?!"), tail[1].lower().strip(",.:;?!")
        if h in HANG and not (h in {"it","them"} and t0 in AFTER_IT) and not (h in {"in","out","off"} and t0 in AFTER_IN): return False
        if (t0 in PARTICLE and tail[0][:1].islower()) or (t0 in {"in","out","off"} and t1 in AFTER_IN): return False
        return not re.fullmatch(r"[$]?[\d,.%]+", head[-1])
    good = [i for i in spaces if ok(i)] or spaces
    if not good:
        return [p]
    punct = [i for i in good if p[i-1] in ",.:;?!" and abs(i - len(p) / 2) <= len(p) / 4]
    cut = min(punct or good, key=lambda i: abs(i - len(p) / 2))
    return widen(p[:cut].strip()) + widen(p[cut+1:].strip())

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
        pieces = [x.strip() for x in BREAK.split(sentence) if x and x.strip()]
        carry = ""
        for piece in pieces:
            piece = f"{carry} {piece}".strip()
            carry = ""
            if len(piece.split()) == 1 and not piece.endswith((",", ".", "!", "?")) and piece is not pieces[-1]:
                carry = piece           # a lone word ("even") goes with what follows it
                continue
            cand = f"{buf} {piece}".strip()
            if len(cand) <= MAXC + SLACK or len(buf) < 10:
                buf = cand
            else:
                if buf:
                    parts.append(buf)
                buf = piece
        if carry:
            buf = f"{buf} {carry}".strip()
        if buf:
            parts.append(buf)
        out += [c for p in parts for c in widen(p)]
    return out

GHOST = {"you", "thank you", "thanks", "bye", "okay", "uh", "um"}

# Descript breaks sentences across cues, so join every cue into 1 stream
# first (ghost cues dropped), with a time on every character, then cut the
# stream into sentences and lines.
stream, times = "", []
for t0, t1, text in parse(sys.argv[1]):
    text = re.sub(r'\s+([,.!?])', r'\1', re.sub(r'"\s+', '"', " ".join(text.split())))
    if text.strip().lower().strip(".,!?") in GHOST:
        continue
    if stream:
        stream += " "
        times.append(t0)
    n = max(len(text), 1)
    times += [t0 + (t1 - t0) * i / n for i in range(len(text))]
    stream += text
times.append(times[-1] if times else 0)

cues, at = [], 0
for p in chunks(stream):
    start = stream.index(p, at)
    end = start + len(p)
    cues.append([times[start], times[min(end, len(times) - 1)], p])
    at = end

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

for i, c in enumerate(merged):   # a deleted "Um," leaves "in this video" starting a sentence lowercase
    if i == 0 or merged[i-1][2].rstrip().endswith((".", "!", "?")):
        c[2] = c[2][:1].upper() + c[2][1:]

with open(sys.argv[2], "w") as f:
    for i, (a, b, t) in enumerate(merged, 1):
        f.write(f"{i}\n{fmt(a)} --> {fmt(b)}\n{t}\n\n")

lens = [len(t) for _, _, t in merged]
durs = [b - a for a, b, _ in merged]
print(f"{len(cues)} -> {len(merged)} cues after merging flashes")
print(f"longest line {max(lens)} chars · average {sum(lens)/len(lens):.0f}")
print(f"shortest cue {min(durs):.2f}s · average {sum(durs)/len(durs):.2f}s")
print(f"over {MAXC} chars: {sum(1 for l in lens if l > MAXC)}")

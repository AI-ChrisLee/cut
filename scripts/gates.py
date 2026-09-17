#!/usr/bin/env python3
"""Run the cut rubric's gates and print what a person has to read.

    python3 gates.py <script.md> <cut.srt> [terms.tsv]

Five of the gates are searches. Written as prose they get re-improvised on every
run, and a search improvised at 11pm is a search that misses things; that is how
one review round turns into five paid calls. Here they run the same way twice.

terms.tsv is optional, one line per brand term:  correct<TAB>wrong,wrong,wrong
The wrong forms come from reading the transcript before the paid call.

Judgment stays with the person. This prints candidates, never decisions.
"""
import re, sys, collections, difflib

GHOST = {"you", "thank you", "thanks", "bye", "okay", "uh", "um"}
GAP   = 0.30

def ts(s):
    h, m, rest = s.split(":"); sec, ms = rest.split(",")
    return int(h)*3600 + int(m)*60 + int(sec) + int(ms)/1000

def read_srt(path):
    out = []
    for block in re.split(r"\n\s*\n", open(path).read().strip()):
        L = block.strip().split("\n")
        if len(L) < 3: continue
        m = re.match(r"([\d:,]+)\s*-->\s*([\d:,]+)", L[1])
        if m: out.append((ts(m.group(1)), ts(m.group(2)), " ".join(L[2:]).strip()))
    return out

NUMS = {"zero":"0","one":"1","two":"2","three":"3","four":"4","five":"5","six":"6","seven":"7","eight":"8","nine":"9","ten":"10","eleven":"11","twelve":"12"}
def words(t):
    return [NUMS.get(w, w) for w in re.findall(r"[a-z0-9']+", t.lower().replace(",", ""))]

def script_sentences(path):
    text = open(path).read()
    h = [m.start() for m in re.finditer(r"^##", text, re.M)]
    if h: text = text[h[0]:]
    text = re.sub(r"```.*?```", "\n\n", text, flags=re.S)
    text = re.sub(r"`[^`]*`", " ", text, flags=re.S)
    text = re.sub(r"\[[A-Z][^\]]*\]", " ", text, flags=re.S)
    keep = []
    for ln in text.splitlines():
        if "|" in ln or ln.lstrip().startswith("#") or re.match(r"^\s*[-*]?\s*\*\*(I type|Claude|DECK|DEMO|FACE|BOARD)", ln, re.I):
            keep.append("")
        else:
            keep.append(ln)
    out = []
    for para in re.split(r"\n\s*\n", "\n".join(keep)):
        para = re.sub(r"\*\*|__|\*|_", "", " ".join(para.split()))
        for s in re.split(r"(?<=[.!?])\s+", para):
            if len(words(s)) >= 3:
                out.append(s.strip())
    return out

def marked_starts(path):
    """first 3 words of every spoken line that comes right after [SCREEN:], [HOLD] or (pause)"""
    text = open(path).read()
    h = [m.start() for m in re.finditer(r"^##", text, re.M)]
    if h: text = text[h[0]:]
    out, mark = {}, None
    for ln in text.splitlines():
        t = ln.strip()
        if not t or t.startswith("#"): continue
        m = re.match(r"^\[(SCREEN|HOLD)|^\((pause)\)", t)
        if m: mark = m.group(1) or m.group(2); continue
        if t.startswith("["): continue
        if mark: out[tuple(words(t)[:3])] = mark
        mark = None
    return out

def section(n, title):
    print(f"\n{'='*66}\n{n}. {title}\n{'='*66}")

def main():
    script_p, cut_p = sys.argv[1], sys.argv[2]
    terms_p = sys.argv[3] if len(sys.argv) > 3 else None

    cues = read_srt(cut_p)
    cut_text = " ".join(c[2] for c in cues)
    cut_words = words(cut_text)
    sents = script_sentences(script_p)

    section("G1", "Lines that may have been lost  (READ ALL OF THESE)")
    # walk the script in order: a sentence is in the cut when most of its
    # 4-word runs sit a little past the last sentence found; a 3-word
    # sentence is in the cut when its exact 3 words sit close past it
    word_t = [c[0] + (c[1] - c[0]) * i / max(len(words(c[2])), 1) for c in cues for i in range(len(words(c[2])))]
    pos, pos3 = collections.defaultdict(list), collections.defaultdict(list)
    for i in range(len(cut_words) - 2):
        pos3[tuple(cut_words[i:i+3])].append(i)
        if i < len(cut_words) - 3:
            pos[tuple(cut_words[i:i+4])].append(i)
    cursor, marks, at = 0, [], []
    for s in sents:
        w = words(s)
        at.append(cursor)
        if len(w) == 3:
            marks.append(any(cursor <= p <= cursor + 60 for p in pos3[tuple(w)]))
            continue
        grams = [tuple(w[i:i+4]) for i in range(len(w) - 3)]
        hit = [min(p for p in pos[g] if cursor <= p <= cursor + 400)
               for g in grams if any(cursor <= p <= cursor + 400 for p in pos[g])]
        found = len(hit) * 2 >= len(grams)
        if found:
            cursor = max(hit)
        marks.append(found)
    last = max((k for k, f in enumerate(marks) if f and len(words(sents[k])) > 3), default=-1)
    missing, misheard = [], []
    for k, s in enumerate(sents):
        if k > last or (marks[k] and len(words(s)) <= 3): continue
        w = words(s)
        best = (0, None, None)
        for j in range(at[k], min(at[k] + len(w) + 40, len(cut_words))):
            for L in (len(w) - 1, len(w), len(w) + 1):
                sm = difflib.SequenceMatcher(None, w, cut_words[j:j+L], autojunk=False)
                if sm.ratio() > best[0]: best = (sm.ratio(), j, sm)
        ratio, j, sm = best
        # a misheard first or last word reads as dropped when the window stops short of it; widen the
        # window, and keep the wider read only when the words just past it start the next sentence
        # (or end the one before), so a word that was really dropped is never called misheard
        nxt = words(sents[k + 1])[:1] if k + 1 < len(sents) else []
        prv = words(sents[k - 1])[-1:] if k else []
        if sm and sm.get_opcodes()[-1][0] == "delete" and nxt:
            for e in (0, 1, 2):
                sm2 = difflib.SequenceMatcher(None, w, cut_words[j:j + len(w) + e], autojunk=False)
                op, a, b, c, d = sm2.get_opcodes()[-1]
                if op == "replace" and b == len(w) and cut_words[j + d:j + d + 1] == nxt:
                    sm = sm2
                    break
        if sm and sm.get_opcodes()[0][0] == "delete" and prv:
            for e in (1, 2):
                if j - e < 1: break
                sm2 = difflib.SequenceMatcher(None, w, cut_words[j - e:j + len(w) - 1], autojunk=False)
                op, a, b, c, d = sm2.get_opcodes()[0]
                if op == "replace" and a == 0 and c == 0 and cut_words[j - e - 1:j - e] == prv:
                    sm, j = sm2, j - e
                    break
        diff = [(" ".join(w[a:b]), " ".join(cut_words[j+c:j+d]))
                for op, a, b, c, d in (sm.get_opcodes() if sm else []) if op != "equal"]
        if len(w) > 3 and ratio >= 0.7 and diff and sum(len(x.split()) for x, _ in diff) <= 3:
            for op, a, b, c, d in sm.get_opcodes():
                x, y = " ".join(w[a:b]), " ".join(cut_words[j+c:j+d])
                base = lambda t: re.sub(r"\b(a|an|the)\b|'s\b|(?<=\w)(s|ed)\b|\s", "", t)
                if op != "replace" or re.search(r"\d", x + y) or base(x) == base(y):
                    continue              # a dropped word, a number written 2 ways, or the founder's own grammar
                if b - a <= 1 and len(x) < 4:   # a lone short word: show the word after it too
                    b, d = b + 1, d + 1
                    x, y = " ".join(w[a:b]), " ".join(cut_words[j+c:j+d])
                close = difflib.SequenceMatcher(None, x.replace(" ", ""), y.replace(" ", "")).ratio() >= 0.6
                misheard.append((word_t[min(j + c, len(word_t) - 1)], x, y, s, close))
        elif not marks[k]:
            missing.append(s)
    if not missing:
        print("  none inside the take.")
    for s in missing:
        print(f"  {s[:88]}")
    after = sum(1 for k in range(last + 1, len(sents)))
    if after:
        print(f"\n  The take ends at: {sents[last][:70]}")
        print(f"  {after} script sentences come after it. Never reached, so not listed.")
    print(f"\n  {len(missing)} of {len(sents)} script sentences to check by hand.")
    print("  Present in the RAW transcript and absent here means a line died.")
    print("  Absent from both means he never said it, which is not a defect.")

    section("G2", "Filler words the button left")
    said = set(words(" ".join(sents)))
    fill = [(word_t[i], " ".join(cut_words[max(0, i - 3):i + 4])) for i, x in enumerate(cut_words)
            if x in ("um", "uh", "uhm", "erm") and x not in said]
    for t0, ctx in fill:
        print(f"  {t0:7.1f}s  ...{ctx}...")
    if not fill: print("  none.")

    section("G3", "Doubled phrases still in the cut")
    dup = []
    i = 0
    while i < len(cut_words):
        for n in range(12, 2, -1):
            if len(cut_words) >= i + 2*n and cut_words[i:i+n] == cut_words[i+n:i+2*n]:
                dup.append(" ".join(cut_words[i:i+n]) + "  (said 2 times)")
                i += n
                break
        i += 1
    for d in dict.fromkeys(dup):
        print(f"  {d}")
    if not dup: print("  none.")

    section("G4", "Orphan fragments")
    # Descript runs a sentence across cues, so a lowercase start is normal inside
    # speech. A fragment is what sits alone: a pause before it, and under 4 words
    # or starting mid-sentence.
    orph = []
    live = [c for c in cues if c[2].strip().lower().strip(".,!?") not in GHOST]
    starts = {tuple(words(s)[:3]) for s in sents}   # a script sentence that starts lowercase (a quote) is not mid-sentence
    for k, (t0, t1, t) in enumerate(live):
        w = words(t)
        if not w: continue
        before = t0 - live[k-1][1] if k else 9
        after = live[k+1][0] - t1 if k + 1 < len(live) else 9
        if (len(w) < 4 and before > GAP and after > GAP) or (t[:1].islower() and before > GAP and tuple(w[:3]) not in starts):
            orph.append((t0, t))
    for t0, t in orph[:40]:
        print(f"  {t0:7.1f}s  {t[:70]}")
    print(f"  {len(orph)} cues that sit alone after a pause. Read each for a stranded word.")

    section("G5", "Dead air over 0.30s, ghosts removed first")
    real = [c for c in cues if c[2].strip().lower().strip(".,!?") not in GHOST]
    dropped = len(cues) - len(real)
    planned = marked_starts(script_p)
    gaps = [(a[1], b[0] - a[1], planned.get(tuple(words(b[2])[:3]))) for a, b in zip(real, real[1:]) if b[0] - a[1] > GAP]
    print(f"  {dropped} ghost cues ignored before measuring.")
    for at_, g, why in sorted(gaps, key=lambda x: (x[2] is not None, -x[1])):
        print(f"  {at_:7.1f}s   {g:.2f}s" + (f"   planned: the script's {why} is here, stays" if why else ""))
    print(f"  {sum(1 for x in gaps if not x[2])} gaps over {GAP}s to delete, {sum(1 for x in gaps if x[2])} planned by the script.")

    section("G6", "Words spelled wrong")
    for t0, x, y, s, close in misheard:
        if close:
            print(f"  {t0:7.1f}s  says \"{y}\", should say \"{x}\"   in: {s[:60]}")
    other = [m for m in misheard if not m[4]]
    if not any(m[4] for m in misheard): print("  none found by the walk.")
    if other:
        print("\n  Said with different words. A brand word heard as noise, or the founder's own words, which stay:")
        for t0, x, y, s, _ in other:
            print(f"  {t0:7.1f}s  says \"{y}\", the script says \"{x}\"")
    if not terms_p:
        print("  no terms.tsv given. Write one: correct<TAB>wrong,wrong")
    else:
        for line in open(terms_p):
            if not line.strip() or line.startswith("#"): continue
            parts = line.rstrip("\n").split("\t")
            good = parts[0].strip()
            bad  = [b.strip() for b in (parts[1].split(",") if len(parts) > 1 else []) if b.strip()]
            n_script = len(re.findall(re.escape(good), " ".join(sents[:last+1]), re.I))
            n_cut    = len(re.findall(re.escape(good), cut_text, re.I))
            hits     = [(b, len(re.findall(re.escape(b), cut_text, re.I))) for b in bad]
            flag = "FAIL" if any(h for _, h in hits) else ("short" if n_cut < n_script else "ok")
            print(f"  [{flag:5}] {good:24} script {n_script:3}  cut {n_cut:3}"
                  + ("   wrong forms still present: " + ", ".join(f"{b}({h})" for b, h in hits if h) if any(h for _,h in hits) else ""))
        print("\n  Brand words, from terms.tsv.  FAIL: a wrong form survived. short: fewer than the script has, so an")
        print("  instance was misheard into something not yet named. Read that passage.")

    section("REC", "Recorded, not judged")
    dur = cues[-1][1] if cues else 0
    print(f"  cut length {dur/60:.2f} min · {len(cues)} cues · "
          f"script {len(sents)} sentences / {sum(len(words(s)) for s in sents)} words")

if __name__ == "__main__":
    main()

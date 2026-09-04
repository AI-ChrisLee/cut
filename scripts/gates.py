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
import re, sys, collections

COMMON = set("""the be to of and a in that have i it for not on with he as you do at this but his
by from they we say her she or an will my one all would there their what so up out if about who
get which go me when make can like time no just him know take people into year your good some
could them see other than then now look only come its over also back after use two how our work
first well way even new want because any these give day most us is are was were been has had did
does am not don't it's i'm that's here where why while very much many more much such own same
too can't won't let put keep run made off down again still every last next thing things got""".split())

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

def words(t):
    return re.findall(r"[a-z']+", t.lower())

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

def section(n, title):
    print(f"\n{'='*66}\n{n}. {title}\n{'='*66}")

def main():
    script_p, cut_p = sys.argv[1], sys.argv[2]
    terms_p = sys.argv[3] if len(sys.argv) > 3 else None

    cues = read_srt(cut_p)
    cut_text = " ".join(c[2] for c in cues)
    cut_words = words(cut_text)
    cut_set = set(cut_words)
    sents = script_sentences(script_p)

    section("G1", "Lines that may have been lost  (READ ALL OF THESE)")
    freq = collections.Counter(w for s in sents for w in words(s))
    missing = []
    for s in sents:
        rare = sorted(set(words(s)) - COMMON, key=lambda w: (freq[w], -len(w)))[:2]
        if rare and not any(r in cut_set for r in rare):
            missing.append((rare, s))
    if not missing:
        print("  none. every script sentence has a rare word present in the cut.")
    for rare, s in missing:
        print(f"  [{'/'.join(rare)}]  {s[:88]}")
    print(f"\n  {len(missing)} of {len(sents)} script sentences to check by hand.")
    print("  Present in the RAW transcript and absent here means a line died.")
    print("  Absent from both means he never said it, which is not a defect.")

    section("G3", "Doubled phrases still in the cut")
    dup = []
    for i in range(len(cut_words) - 5):
        if cut_words[i:i+3] == cut_words[i+3:i+6]:
            dup.append(" ".join(cut_words[i:i+6]))
    for d in dict.fromkeys(dup):
        print(f"  {d}")
    if not dup: print("  none.")

    section("G4", "Orphan fragments")
    orph = []
    for t0, _, t in cues:
        w = words(t)
        if not w: continue
        if len(w) < 4 or (t[:1].islower() and not t[:1].isdigit()):
            orph.append((t0, t))
    for t0, t in orph[:40]:
        print(f"  {t0:7.1f}s  {t[:70]}")
    print(f"  {len(orph)} short or lowercase-start cues. Most are fine; read for a stranded word.")

    section("G5", "Dead air over 0.30s, ghosts removed first")
    real = [c for c in cues if c[2].strip().lower().strip(".,!?") not in GHOST]
    dropped = len(cues) - len(real)
    gaps = [(a[1], b[0] - a[1]) for a, b in zip(real, real[1:]) if b[0] - a[1] > GAP]
    print(f"  {dropped} ghost cues ignored before measuring.")
    for at, g in sorted(gaps, key=lambda x: -x[1])[:15]:
        print(f"  {at:7.1f}s   {g:.2f}s")
    print(f"  {len(gaps)} gaps over {GAP}s, {sum(g for _, g in gaps):.0f}s total.")
    print("  A gap where the screen is moving is demo footage and stays.")

    section("G6", "Brand words")
    if not terms_p:
        print("  no terms.tsv given. Write one: correct<TAB>wrong,wrong")
    else:
        for line in open(terms_p):
            if not line.strip() or line.startswith("#"): continue
            parts = line.rstrip("\n").split("\t")
            good = parts[0].strip()
            bad  = [b.strip() for b in (parts[1].split(",") if len(parts) > 1 else []) if b.strip()]
            n_script = len(re.findall(re.escape(good), open(script_p).read(), re.I))
            n_cut    = len(re.findall(re.escape(good), cut_text, re.I))
            hits     = [(b, len(re.findall(re.escape(b), cut_text, re.I))) for b in bad]
            flag = "FAIL" if any(h for _, h in hits) else ("short" if n_cut < n_script else "ok")
            print(f"  [{flag:5}] {good:24} script {n_script:3}  cut {n_cut:3}"
                  + ("   wrong forms still present: " + ", ".join(f"{b}({h})" for b, h in hits if h) if any(h for _,h in hits) else ""))
        print("\n  FAIL: a wrong form survived. short: fewer than the script has, so an")
        print("  instance was misheard into something not yet named. Read that passage.")

    section("REC", "Recorded, not judged")
    dur = cues[-1][1] if cues else 0
    print(f"  cut length {dur/60:.2f} min · {len(cues)} cues · "
          f"script {len(sents)} sentences / {sum(len(words(s)) for s in sents)} words")

if __name__ == "__main__":
    main()

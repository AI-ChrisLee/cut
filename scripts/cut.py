#!/usr/bin/env python3
"""Cut a one-take recording against its script. Keeps the LAST take.

    python cut.py recording.mp4 03_SCRIPT.md

Writes <recording>-cut.xml (a Premiere sequence), <recording>-captions.srt,
and cut.json (the keep ranges, if you want to render with ffmpeg).

Two dependencies: faster-whisper and ffmpeg. Nothing else, no account, no
upload. Every commercial tool either takes a script and picks the "best" take,
or keeps the last take and ignores your script. This does both, because a
retake is defined by the script: the same line, said again.

The one rule that keeps it honest: a line the matcher cannot place stays in the
video. Silence gets removed, retakes get removed, and anything uncertain
survives. A cut that quietly drops a sentence is worse than a loose cut.
"""
import json, os, re, subprocess, sys, urllib.parse, uuid
from collections import defaultdict

def probe_fps(path):
    """Read the real frame rate. Hard-coding 30 silently drifts a 23.976 cut
    away from its audio across a long sequence, and nothing reports it."""
    out = subprocess.run(["ffprobe","-v","error","-select_streams","v:0",
                          "-show_entries","stream=r_frame_rate","-of",
                          "default=nw=1:nk=1", path],
                         capture_output=True, text=True).stdout.strip()
    try:
        n, d = out.split("/")
        return int(n) / int(d)
    except Exception:
        return 30.0

FPS = 30            # replaced per-run in main()

# ---------------------------------------------------------------- script

def parse_script(path):
    """Spoken narration only: no headers, no markers, no screen content.

    Scripts carry a lot he never says out loud: a header block of format and
    runtime notes, a legend table for the shot markers, direction in backticks,
    screen text under "I type". Every one of those left in becomes a line the
    matcher hunts for and never finds.

    Lines are joined into paragraphs before sentences are split out, because a
    script hard-wraps mid-sentence and a half sentence matches nothing.
    """
    text = open(path).read()
    heads = [m.start() for m in re.finditer(r"^##", text, re.M)]
    if heads:
        text = text[heads[0]:]                       # drop the header block
    text = re.sub(r"```.*?```", "\n\n", text, flags=re.S)      # fenced blocks
    text = re.sub(r"`[^`]*`", " ", text, flags=re.S)            # direction notes
    text = re.sub(r"\[[A-Z][^\]]*\]", " ", text, flags=re.S)   # [DECK: ...]

    keep = []
    for ln in text.splitlines():
        if "|" in ln or ln.lstrip().startswith("#"):
            keep.append("")                          # a table row breaks the flow
        elif re.match(r"^\s*\*\*(I type|Claude asks|Claude outputs|DECK|DEMO|FACE|BOARD)",
                      ln, re.I) or re.match(r"^\s*[-*]\s*\*\*", ln):
            keep.append("")
        else:
            keep.append(ln)

    lines = []
    for para in re.split(r"\n\s*\n", "\n".join(keep)):
        para = re.sub(r"\*\*|__|\*|_", "", " ".join(para.split()))
        if len(para.split()) < 2:
            continue
        for sent in re.split(r"(?<=[.!?])\s+", para):
            w = [x for x in re.sub(r"[^a-z' ]", " ", sent.lower()).split() if x]
            if w:
                lines.append({"text": sent.strip(), "words": [x.upper() for x in w]})
    return lines

# ---------------------------------------------------------------- audio

ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = {20:"twenty",30:"thirty",40:"forty",50:"fifty",60:"sixty",70:"seventy",80:"eighty",90:"ninety"}

def num_words(n):
    if n < 20: return [ONES[n]]
    if n < 100:
        t, r = divmod(n, 10)
        return [TENS[t*10]] + ([ONES[r]] if r else [])
    if n < 1000:
        h, r = divmod(n, 100)
        return [ONES[h], "hundred"] + (num_words(r) if r else [])
    for d, name in ((1_000_000, "million"), (1000, "thousand")):
        if n >= d:
            q, r = divmod(n, d)
            return num_words(q) + [name] + (num_words(r) if r else [])
    return [str(n)]

def expand(tok):
    """The transcript writes $10,000; the script says ten thousand dollar."""
    money = tok.startswith("$")
    t = tok.lstrip("$").replace(",", "")
    m = re.fullmatch(r"(\d+)(?:\.\d+)?", t)
    if not m:
        return [re.sub(r"[^a-z']", "", tok.lower())]
    return num_words(int(m.group(1))) + (["dollar"] if money else [])

def transcribe(video, cache):
    if os.path.exists(cache):
        return json.load(open(cache))
    from faster_whisper import WhisperModel
    wav = "/tmp/_cut.wav"
    subprocess.run(["ffmpeg","-y","-v","error","-i",video,"-ac","1","-ar","16000",wav],
                   check=True)
    model = WhisperModel("small.en", device="cpu", compute_type="int8")
    segs, _ = model.transcribe(wav, word_timestamps=True, vad_filter=True)
    out = [{"w": w.word, "start": w.start, "end": w.end}
           for s in segs for w in (s.words or [])]
    json.dump(out, open(cache, "w"))
    return out

def normalize(raw):
    joined = []
    for w in raw:
        t = w["w"].strip()
        if joined and re.fullmatch(r",\d{3}", t):     # "$10" then ",000"
            joined[-1] = {**joined[-1], "w": joined[-1]["w"] + t, "end": w["end"]}
        else:
            joined.append(dict(w))
    flat = []
    for w in joined:
        for piece in expand(w["w"].strip()):
            if piece:
                flat.append({"w": piece.upper(), "start": w["start"], "end": w["end"]})
    return flat

# ---------------------------------------------------------------- match

def align(script, heard):
    """Word-level DP. Skipping heard audio is cheap, skipping script is not,
    and a tiny bonus for later positions makes a tie land on the last take."""
    S = [(w, li) for li, ln in enumerate(script) for w in ln["words"]]
    H = [(h["w"], h["start"], h["end"]) for h in heard]
    n, m = len(S), len(H)
    MATCH, SKIP_H, SKIP_S, LATE = 1.0, -0.02, -0.6, 1e-5
    prev = [0.0] * (m + 1)
    back = [bytearray(m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        cur = [prev[0] + SKIP_S] + [0.0] * m
        back[i][0] = 2
        sw = S[i-1][0][:4]
        for j in range(1, m + 1):
            a = prev[j-1] + (MATCH + j*LATE if sw == H[j-1][0][:4] else -9)
            b = cur[j-1] + SKIP_H
            c = prev[j] + SKIP_S
            if a >= b and a >= c: cur[j], back[i][j] = a, 0
            elif b >= c:          cur[j], back[i][j] = b, 1
            else:                 cur[j], back[i][j] = c, 2
        prev = cur
    pairs, i, j = {}, n, m
    while i > 0 and j > 0:
        b = back[i][j]
        if b == 0:   pairs[i-1] = j-1; i -= 1; j -= 1
        elif b == 1: j -= 1
        else:        i -= 1
    return S, H, pairs

def find_retakes(H, minlen=3, bridge=14.0, slack=6):
    """The same run of words said again: drop everything but the last attempt.

    He often goes three or four times before he is happy. Handling only the
    first pair leaves attempt two in the video, which is exactly the take he
    deletes by hand afterwards. So the chain is followed all the way: from the
    first attempt to the start of the LAST one, everything goes.
    """
    W = [h[0][:4] for h in H]
    grams = defaultdict(list)
    for i in range(len(W) - minlen + 1):
        grams[tuple(W[i:i+minlen])].append(i)

    def next_try(i):
        """the start of the next attempt at the run beginning at i, or None"""
        for j in grams[tuple(W[i:i+minlen])]:
            if j <= i:
                continue
            if j - i > slack + minlen*4 or H[j][1] - H[i][1] > bridge:
                return None
            k = 0
            while i+k < j and j+k < len(W) and W[i+k] == W[j+k]:
                k += 1
            if k >= minlen:
                return j
        return None

    cuts, used = [], [False]*len(W)
    for i in range(len(W) - minlen + 1):
        if used[i]:
            continue
        last = i
        while True:
            nxt = next_try(last)
            if nxt is None:
                break
            last = nxt
        if last == i:
            continue
        cuts.append((i, last))                 # everything before the last try
        for x in range(i, last):
            used[x] = True
    return cuts

# ---------------------------------------------------------------- ranges

# What the transcriber emits over typing, mouse clicks and room tone. These are
# not words he said, and left in they bridge a long dead stretch into a chain of
# short ones, so nothing gets cut. Killing them is what makes dead air findable.
GHOSTS = {"YOU", "THANK", "THANKS", "BYE", "OKAY", "OK", "UH", "UM", "MM", "HMM",
          "YEAH", "SO", "AND", "THE"}

def build(H, pairs, retakes, gap=0.30, hold=0.12, pad=0.06, merge=0.20, ghost_gap=1.2):
    """gap: silence longer than this comes out. 0.30 is Chris's setting.

    Amplitude cannot find this silence. His room has a noise floor above -30dB,
    so ffmpeg's silencedetect reports zero dead stretches in a take that is full
    of them. The gaps between spoken words are the only reliable measure.
    """
    inv = set(pairs.values())
    drop = [False]*len(H)
    for i, j in retakes:
        for x in range(i, j): drop[x] = True

    for j, (w, t0, t1) in enumerate(H):
        if drop[j] or j in inv: continue
        prev = next((H[k] for k in range(j-1, max(-1, j-3), -1) if not drop[k]), None)
        nxt  = next((H[k] for k in range(j+1, min(len(H), j+3)) if not drop[k]), None)
        if (prev and prev[0][:4] == w[:4]) or (nxt and nxt[0][:4] == w[:4]):
            drop[j] = True
            continue
        # a ghost: a filler the script never had, sitting alone in a long quiet
        before = t0 - prev[2] if prev else 99
        after  = nxt[1] - t1 if nxt else 99
        if w in GHOSTS and before > ghost_gap and after > ghost_gap:
            drop[j] = True
    ranges = []
    for j, (_, t0, t1) in enumerate(H):
        if drop[j]: continue
        if ranges and t0 - ranges[-1][1] <= gap:
            ranges[-1][1] = max(ranges[-1][1], t1)
        else:
            if ranges: ranges[-1][1] += hold
            ranges.append([t0 - hold/2, t1])
    out = []
    for a, b in ranges:
        a, b = round(max(0, a - pad), 3), round(b + pad, 3)
        if out and a - out[-1][1] <= merge: out[-1][1] = max(out[-1][1], b)
        else: out.append([a, b])
    return out, sum(drop)

# ---------------------------------------------------------------- output

def write_xml(path, video, ranges, src_seconds, w=1920, h=1080, srate=48000):
    """FCP7 xmeml v5. Verified frame-exact against a live Premiere 26.3.2 import.

    The <link> elements are the part people leave out and then wonder why
    dragging a clip leaves its audio behind. They tie each video clip to its
    audio clip so the pair moves as one, the way a normal edit does.
    """
    url = "file://localhost" + urllib.parse.quote(os.path.abspath(video))
    base = os.path.basename(video)
    esc = lambda t: (str(t).replace("&", "&amp;").replace("<", "&lt;")
                     .replace(">", "&gt;"))
    f2 = lambda t: int(round(t * FPS))
    rate = f"<rate><timebase>{FPS}</timebase><ntsc>FALSE</ntsc></rate>"
    tc = f"<timecode>{rate}<frame>0</frame><displayformat>NDF</displayformat></timecode>"

    items, off = [], 0
    for t0, t1 in ranges:
        si, so = f2(t0), f2(t1)
        if so <= si:
            continue
        items.append((si, so, so - si, off)); off += so - si

    tiny = sum(1 for _, _, d, _ in items if d < 12)
    if tiny:
        print(f"  warn: {tiny} clips under 12 frames (reads as a glitch, not a beat)")

    def filetag(first):
        if not first:
            return '<file id="file-1"/>'
        return (f'<file id="file-1"><name>{esc(base)}</name><pathurl>{esc(url)}</pathurl>'
                f'{rate}<duration>{f2(src_seconds)}</duration>{tc}<media>'
                f'<video><samplecharacteristics>{rate}<width>{w}</width><height>{h}</height>'
                f'<anamorphic>FALSE</anamorphic><pixelaspectratio>square</pixelaspectratio>'
                f'<fielddominance>none</fielddominance></samplecharacteristics></video>'
                f'<audio><samplecharacteristics><samplerate>{srate}</samplerate>'
                f'<sampledepth>16</sampledepth></samplecharacteristics></audio></media></file>')

    def clip(kind, n, si, so, d, ts):
        cid = ("cv-" if kind == "video" else "ca-") + str(n)
        extra = "" if kind == "video" else "<channelcount>1</channelcount>"
        return (f'<clipitem id="{cid}"><name>{esc(base)}</name><enabled>TRUE</enabled>'
                f'<duration>{d}</duration><start>{ts}</start><end>{ts+d}</end>'
                f'<in>{si}</in><out>{so}</out>{rate}'
                + filetag(kind == "video" and n == 1) +
                f'<sourcetrack><mediatype>{kind}</mediatype><trackindex>1</trackindex>'
                f'</sourcetrack>{extra}'
                f'<link><linkclipref>cv-{n}</linkclipref><mediatype>video</mediatype>'
                f'<trackindex>1</trackindex><clipindex>{n}</clipindex></link>'
                f'<link><linkclipref>ca-{n}</linkclipref><mediatype>audio</mediatype>'
                f'<trackindex>1</trackindex><clipindex>{n}</clipindex>'
                f'<groupindex>1</groupindex></link></clipitem>')

    total = off
    v = "".join(clip("video", n, *it) for n, it in enumerate(items, 1))
    a = "".join(clip("audio", n, *it) for n, it in enumerate(items, 1))
    open(path, "w").write(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n<xmeml version="5">'
        f'<sequence id="sequence-1"><uuid>{uuid.uuid4()}</uuid>'
        f'<name>{esc(os.path.splitext(base)[0])} cut</name><duration>{total}</duration>'
        f'{rate}<in>0</in><out>{total}</out>{tc}<media>'
        f'<video><format><samplecharacteristics>{rate}<width>{w}</width><height>{h}</height>'
        f'<anamorphic>FALSE</anamorphic><pixelaspectratio>square</pixelaspectratio>'
        f'<fielddominance>none</fielddominance></samplecharacteristics></format>'
        f'<track>{v}</track></video>'
        f'<audio><numOutputChannels>2</numOutputChannels><format><samplecharacteristics>'
        f'<samplerate>{srate}</samplerate><sampledepth>16</sampledepth>'
        f'</samplecharacteristics></format><track>{a}</track></audio>'
        f'</media></sequence></xmeml>')
    return total

def write_srt(path, raw, ranges, maxw=8, maxs=3.0, gap=0.5):
    edges, off = [], 0.0
    for a, b in ranges:
        edges.append((a, b, off)); off += b - a
    def cut_t(t):
        for a, b, o in edges:
            if a <= t <= b: return o + (t - a)
    cues, cur = [], []
    for w in raw:
        c0, c1 = cut_t(w["start"]), cut_t(w["end"])
        if c0 is None or c1 is None: continue
        tok = w["w"].strip()
        if not tok: continue
        if cur and (c0 - cur[-1][2] > gap or len(cur) >= maxw or c1 - cur[0][1] > maxs):
            cues.append(cur); cur = []
        cur.append((tok, c0, c1))
        if tok.endswith((".", "?", "!")) and len(cur) >= 3:
            cues.append(cur); cur = []
    if cur: cues.append(cur)
    fixed = []
    for c in cues:                       # an orphan of 1-2 words is a wrap
        if fixed and len(c) <= 2 and len(fixed[-1]) + len(c) <= maxw + 2 \
           and c[0][1] - fixed[-1][-1][2] < gap:
            fixed[-1] = fixed[-1] + c
        else:
            fixed.append(c)
    def ts(t):
        hh, r = divmod(t, 3600); mm, ss = divmod(r, 60)
        return f"{int(hh):02d}:{int(mm):02d}:{ss:06.3f}".replace(".", ",")
    with open(path, "w") as f:
        for i, c in enumerate(fixed, 1):
            line = re.sub(r"\s+([,.!?])", r"\1", " ".join(t for t, _, _ in c))
            f.write(f"{i}\n{ts(c[0][1])} --> {ts(c[-1][2])}\n{line}\n\n")
    return len(fixed)

# ---------------------------------------------------------------- run

def main():
    if len(sys.argv) < 3:
        sys.exit("usage: cut.py <recording.mp4> <script.md>")
    video, script_path = sys.argv[1], sys.argv[2]
    global FPS
    FPS = probe_fps(video)
    stem = os.path.splitext(video)[0]
    dur = float(subprocess.run(
        ["ffprobe","-v","error","-show_entries","format=duration","-of",
         "default=nw=1:nk=1", video], capture_output=True, text=True).stdout.strip())

    script = parse_script(script_path)
    raw = transcribe(video, stem + "-words.json")
    heard = normalize(raw)
    print(f"script {sum(len(l['words']) for l in script)} words · "
          f"heard {len(heard)} words · take {dur/60:.1f} min · {FPS:.3f} fps")

    S, H, pairs = align(script, heard)
    retakes = find_retakes(H)
    ranges, dropped = build(H, pairs, retakes)

    frames = write_xml(stem + "-cut.xml", video, ranges, dur)
    cues = write_srt(stem + "-captions.srt", raw, ranges)
    json.dump({"keep": ranges}, open(stem + "-cut.json", "w"), indent=1)

    kept = sum(b - a for a, b in ranges)
    print(f"matched {len(pairs)}/{len(S)} script words · {len(retakes)} retakes "
          f"· {dropped} words dropped")
    print(f"{len(ranges)} cuts · {kept/60:.1f} min kept of {dur/60:.1f}")
    print(f"\n  {stem}-cut.xml       Premiere: File > Import")
    print(f"  {stem}-captions.srt  timed to the cut")
    print(f"  {stem}-cut.json      keep ranges, for ffmpeg")

if __name__ == "__main__":
    main()

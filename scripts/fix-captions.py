#!/usr/bin/env python3
"""Fix an exported caption file: the words the recogniser got wrong, then the length.

Two passes, in this order.

1. WORDS. Descript's transcript is a guess at what was said, and it mishears the
   words a lesson turns on: a rung becomes "the wrong", four nine nine seven
   becomes "$997". Every replacement in FIXES below was checked against the
   lesson script that was read on camera, so this pass only ever moves the
   caption back toward what the script already says.

2. LENGTH. Descript decides its own caption breaks and exposes no control, so a
   paragraph lands on screen as a three-line block. resegment.py re-breaks on
   meaning at 40 characters. This calls it rather than copying it.

    python3 fix-captions.py <in.srt> <out.srt> [--report]

--report prints what it changed and stops without writing, which is the pass to
read before trusting it.
"""
import re, sys, subprocess, pathlib

HERE = pathlib.Path(__file__).resolve().parent

# Every entry verified against the lesson script that was read on camera.
# "heard" is matched case-sensitively as a whole phrase; longest first, so a
# phrase that contains another is fixed before its fragment.
FIXES = [
    # --- g5, and the two that are money on screen ---
    ("For $997 at three results",            "$4,997 at three results"),
    ("At 2997 once one finisher the project exists",
                                             "$2,997 once one finished project exists"),
    ("The wrong is your count",              "The rung is your count"),
    ("your offer ridden of",                 "your offer written off"),
    ("what strangers already said in public","what strangers already say in public"),
    ("nine nine seven",                      "$997"),
    ("inside the fourteen days",             "inside fourteen days"),
    ("the winner's own price page",          "the winners' own price pages"),
    ("made it three calls that stayed the conversations",
                                             "made three calls that stayed conversations"),
    ("profit on buyers two",                 "profit on buyer two"),
    ("refusers",                             "refusals"),
    ("business.markdown",                    "business.md"),
    ("no document gets billed",              "no document gets built"),
    ("the research still ends",              "the research still lands"),
    ("lets your sales stink",                "lets you sell tomorrow"),
    ("Create new closed session",            "Create a new Claude session"),
    ("The winning offer called entry",       "The Winning Offer, cold entry"),
    ("scrap Facebook as a library",          "scrape the Facebook ads library"),
    ("therefore the guests read first",      "that folder gets read first"),
    # the "research still ends" entry above never fires: the phrase straddles a
    # cue break, and flatten() only joins lines inside one cue. Anchor on the
    # half that lands in the second cue.
    ("ends, and the conversation turns",     "lands, and the conversation turns"),
    ("RedisCrapper",                         "Reddit Scraper"),
    ("WebPatch",                             "WebFetch"),
    # --- g6 ---
    ("nothing get written down",             "nothing gets written down"),
    ("These three lives nowhere on disk, so I need them for you",
                                             "These three live nowhere on disk, so I need them from you"),
    ("once that's a handle that you are in", "once that is handled you are in"),
    ("Installed Slash.close",                "Install /the-close"),
    # same straddle problem as above, on the outro objection line
    ("once that's a handle that you",        "once that is handled, you"),
    ("G4 builds the deck",                   "g7 builds the deck"),
    ("a sales dot markdown file",            "a sales.md file"),
    ("becomes a book consultant today",      "becomes a booked consult today"),
    # --- g7 ---
    ("minimum execute table product",        "Minimum Executable Product"),
    ("your squad feels it",                  "your squad fills it"),
    ("His facts as roles, five at a month",  "His facts as rows, five at most"),
    ("until the money clear.",               "until the money clears."),
    ("the pitch bit",                        "the pitch beat"),
    ("Your hand sends in",                   "Your hand sends it"),
    ("they made a tag with a demo section",  "they made a deck with a demo section"),
    # --- g8 ---
    ("four wigs on one page",                "four weeks on one page"),
    ("Run, walk, or let it win",             "Run what already wins"),
    ("a sick his or a cold that runs wrong", "a sick kid or a call that runs long"),
    ("all four runs the same three bids",    "all four run the same three beats"),
    # and again: "and all" ends one cue, "four runs..." opens the next
    ("four runs the same three bids",        "four run the same three beats"),
    ("One work vlog a day",                  "One work block a day"),
    ("An asset nobody shows the week",       "An asset nobody saw the week"),
    ("week once Sunday",                     "week one's Sunday"),
    ("improve on Sunday night after",        "Improve, on Sunday, right after"),
    ("Monday's beliefs",                     "Monday's brief"),
    ("Hold is whole line",                   "Hold is a whole line"),
    ("one name to change it or hold",        "one named change, or hold"),
    ("Most of Sunday is a real hold",        "Most Sundays read hold"),
    ("Most of founders has no plan",         "Most founders have no plan"),
    ("This one who writes a plan do not follow it",
                                             "The ones who write a plan do not follow it"),
    ("Contents a deck built",                "Content. A deck built"),
    ("a date next step",                     "a dated next step"),
    ("outreach as gate open",                "outreach. Ads gate open"),
    ("one line on Y of your own file",       "one line on why, off your own files"),
    ("your daily blog",                      "your daily block"),
    ("four weeks of box",                    "four weeks of boxes"),
    ("It renew your nine-day plan",          "It renews your four-week plan"),
    ("you will type the nine-day plan",      "you will type the four-week plan"),
    ("Nine days is outdated",                "Ninety days is outdated"),
    ("the plan, the 90-day plan",            "the plan, the four-week plan"),
    # --- the agent rename, everywhere it is spoken ---
    ("the 90-day plan",                      "the four-week plan"),
    ("90-day plan",                          "four-week plan"),
]

FIXES.sort(key=lambda p: len(p[0]), reverse=True)


def flatten(text):
    """Put each cue's body on one line.

    An SRT wraps a cue over two lines wherever Descript chose to break it, so a
    phrase that spans that break does not match. Flattening first is safe
    because resegment.py re-breaks every cue afterwards anyway.
    """
    out = []
    for block in re.split(r"\n\s*\n", text.strip()):
        L = block.strip().split("\n")
        if len(L) < 3:
            if L and L[0].strip():
                out.append(block.strip())
            continue
        out.append("\n".join([L[0], L[1], " ".join(x.strip() for x in L[2:]).strip()]))
    return "\n\n".join(out) + "\n"


def apply_words(text):
    text = flatten(text)
    hits = []
    for heard, said in FIXES:
        n = text.count(heard)
        if n:
            text = text.replace(heard, said)
            hits.append((n, heard, said))
    return text, hits


def long_cues(text, maxc=40):
    out = []
    for block in re.split(r"\n\s*\n", text.strip()):
        L = block.strip().split("\n")
        if len(L) < 3:
            continue
        body = " ".join(L[2:]).strip()
        lines = -(-len(body) // maxc)
        if lines >= 3:
            out.append((L[0], lines, body))
    return out


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src, dst = sys.argv[1], sys.argv[2]
    report = "--report" in sys.argv

    raw = open(src, encoding="utf-8").read()
    fixed, hits = apply_words(raw)

    before = long_cues(raw)
    print(f"words fixed: {sum(n for n, _, _ in hits)} replacements, {len(hits)} distinct")
    for n, heard, said in hits:
        print(f'  {n}x  "{heard}"  ->  "{said}"')
    print(f"\ncues that would render 3+ lines at 40 chars: {len(before)}")
    for num, lines, body in before[:12]:
        print(f"  cue {num}: {lines} lines, {len(body)} chars | {body[:62]}...")
    if len(before) > 12:
        print(f"  ... and {len(before) - 12} more")

    if report:
        print("\n--report, nothing written.")
        return

    tmp = dst + ".words"
    open(tmp, "w", encoding="utf-8").write(fixed)
    subprocess.run([sys.executable, str(HERE / "resegment.py"), tmp, dst], check=True)
    pathlib.Path(tmp).unlink()

    after = long_cues(open(dst, encoding="utf-8").read())
    total = len(re.split(r"\n\s*\n", open(dst, encoding="utf-8").read().strip()))
    print(f"\nwrote {dst}: {total} cues, {len(after)} still 3+ lines")


if __name__ == "__main__":
    main()

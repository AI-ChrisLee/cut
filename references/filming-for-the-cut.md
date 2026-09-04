# Filming so the cut can be automated

Written 2026-08-17 after a full day failed to auto-cut one recording. The failure was not
in the software. It was in the recording, and one habit fixes it.

## The one instruction

**When you fumble a line, stop, wait one second, then say it again.**

That is the whole thing. One second of room tone is all the cut needs.

## Why, measured

On the shorts recording of 2026-08-17, the gaps between consecutive words were:

| gap | share |
|---|---|
| under 50 ms | **85%** |
| 50 to 150 ms | 2% |
| 150 to 300 ms | 3% |
| over 300 ms | 11% |

Median gap: **0 ms.**

The abandoned take ran straight into the good one with no breath between them.
"Feed image one back" then immediately "feed image one back in as a reference so the two match."

A cut needs a moment of silence to land in. With none, every approach fails the same way:

- Push the boundary outward to find silence and it crosses into the abandoned take,
  so the cut says "The night. The sharpness is night and day."
- Pull it inward and it lands mid-syllable, so a word gets clipped.
- Force the duplicate out by matching text and whole sentences disappear, because the
  deletion range has no safe edge to stop at.

Twelve approaches were tried, including forced alignment with `torchaudio.forced_align`, a
star token to let the aligner skip audio, waveform RMS boundary snapping, and last-take
selection by coverage scoring. Every one landed in one of those three failures. The recording
does not contain the information needed to separate the takes.

## The rest of the filming rules

- **One file, all four shorts.** Say the number out loud before each: "one", then the script.
- **Shoot 16:9.** The vertical crop happens in post.
- **Read the script.** Wandering off it drops script match from about 95% to the 85% seen here,
  and every unmatched line becomes a manual fix.
- **Do not re-say a line immediately to "fix the energy".** Either take the pause, or keep going
  and flag it. A retake with no gap is worse than the fumble.

## What good looks like

With a one second pause after each fumble, the cut is fully automatic: last take wins, the
boundary lands in the pause, and no word is ever clipped. Without it, expect roughly five
manual trims per short, which is what got done by hand on short 1 and it took a few minutes.


## The one correction made by hand, every time

A 137 clip cut was hand-fixed on 2026-08-17. **6 clips out of 137** changed, and five of the
six were the identical mistake:

| what the cut kept | what got removed |
|---|---|
| "...what I charge for it. **Imagine,**" | the first word of the next false start |
| "Clean white background, **say 2,040.**" | the wrong-number attempt |
| "Feed image one back **in**" | a trailing fragment |
| "15,000 for this **takes**" | a trailing fragment |
| "three closest. **They say no. Send the**" | the opening of the next attempt |

**A clip must end where its sentence ends. It must never carry the opening words of the next
attempt.** Trailing junk is the failure mode; a slightly tight tail is not.

So when the match window is chosen, prefer the window that ENDS on the last word of the script
sentence, even at a small cost in coverage. Extending the window past the sentence to pick up
a few more matching tokens is what produces every one of the fixes above.

# The cut rubric

Descript's 3 AI tools made the edit. This is the check on what they left.

**Score every gate, every time. Never stop at the first failure.** The founder gets 1 list, and a
partial score cannot build one. Every round that only finds what the round before missed costs them
another evening.

Everything here is checked against 2 files already on their laptop: the SRT they exported and this
week's script. Nobody scrubs a timeline.

```bash
python3 .claude/skills/cut/scripts/gates.py <script.md> <export.srt> [terms.tsv]
```

That computes G1, G2, G3, G4, G5 and G6 and prints the length, under those names. It prints candidates,
never decisions. The reading is yours, and the call is the founder's.

---

**G1. Nothing was lost.** The only failure that cannot be fixed later, so it is checked by the script
and read by eye.

`gates.py` walks the script in order and looks for each sentence's 4-word runs in the edit (a 3-word
sentence, its 3 words), a little past the last sentence it found. It prints the sentences missing inside
the take, and 1 line for where the take ends, with how many sentences come after it. That list is short,
and you read all of it. A line said with 1 to 3 words heard differently is not lost. gates.py lists those
words under G6.

Then the founder is the lookup. A sentence they remember saying and cannot find in the edit was eaten by
a button, and that is the finding. A sentence they never got to is not a defect. Put the list in front of
them rather than deciding it yourself.

Check the ending hardest. A line said only inside a bad try goes when that try goes.

**G2. No filler word survived.** `gates.py` lists every um, uh, uhm and erm left in the edit that the
script does not say, with its time and the words around it. 0 allowed. Remove filler words misses some,
and past the first 15 seconds nobody hears them before the upload.

**G3. No doubled phrase survived.** Any run of 3 to 12 words said 2 times back to back. 0 allowed, except a
repeat with no pause between the 2 tries, which cannot be cut without an audible seam.

**G4. No orphan fragments.** Every cue that sits alone after a pause: under 4 words, or starting
mid-sentence. Read that list for an abandoned start with no object ("we're gonna read"), a stranded word
("it.", "Click"), half a word.

**G5. Dead air is gone, and the ghost words did not hide it.** 2 passes over the timings.

First drop every lone "You" and "Thank you" cue with no sentence around it. Those are the transcriber
hearing words in typing noise, and left in they split a long dead stretch into short ones that pass any
threshold.

Then list every gap over 0.3 seconds between cues. 0 allowed, except a gap gates.py marks planned, where
the next line follows a [SCREEN:], [HOLD] or (pause) in the script. Those stay.

Never measure this with a loudness tool. A room with a noise floor above -30dB reports no silence in a
take that is full of it.

**G6. Brand words are spelled right, checked by searching for the WRONG forms.** You cannot find
"Apify" by searching for "Apify" when the transcript reads "F5".

Take the pair list. Search the edit for each wrong form: every one returns 0 hits. Then search for each
right form: every one appears at least as often as the script says it. A word that returns 0 on both was
misheard into something nobody has named yet, so read the passage where it belongs.

`gates.py` also prints every word heard wrong inside a line it matched, as "says X, should say Y", with
no pair list needed. A word heard as other words prints under "Said with different words". It goes on the
list too, and the founder keeps it or retypes it. Every hit goes on the list as "what it says, what it
should say". The founder retypes it in Descript's text, which costs nothing and moves no timing.

**G7. The first 15 seconds are the last try, and they flow.** An ear check, and it belongs to the
founder. Ask them to play the first 15 seconds and listen for a stall. The opening is the 1 place where an
acceptable take is not good enough, and a page cannot hear it.

**G8. Captions are 1 line each.** Never 2 sentences in 1 cue, broken at meaning rather than width, no
small word left hanging at the end of a line. Descript breaks its own captions where it likes, so this
gate checks that `scripts/resegment.py` ran and that you read the longest line it printed.

---

## Written down, not judged

**Length.** Write the finished length in the review. There is no range to judge it against.

**Breath.** Tight is the standard, but an edit with every pause removed sounds rushed. If the beat before
a turn in the argument is gone, say so as a note. It never sends an edit back on its own.

## What is NOT a defect

- **The founder's own grammar.** The video is them, and plenty of founders are not native speakers.
  Correct the transcript, never their English.
- **A rough line that was really said in 1 take.** Said once, it stays. There is nothing to cut to.
- **A stumble with no pause around it.** No clean edge exists, so it stays.
- **Silence over a moving screen.** Screen footage, and it stays.

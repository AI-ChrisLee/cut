# The cut rubric

Descript's three buttons did the cut. This is the human gate on what they left.

**Score every gate, every time. Never stop at the first failure.** The founder gets one list,
and a partial score cannot build one. Each round that only finds what the round before missed
costs them another evening.

Everything here is checked against files already on their laptop: the SRT they exported and
this week's script. Nothing here needs you to scrub a timeline.

```bash
python3 .claude/skills/cut/scripts/gates.py <script.md> <cut.srt> [terms.tsv]
```

That computes G1, G3, G4, G5 and G6 and prints the length. The numbers below are the section
names it prints. It prints candidates, never decisions; the reading is yours and the call is
the founder's.

---

**G1. Nothing was lost.** The only unrecoverable failure, so it is checked by script and read
by eye, never walked from memory.

`gates.py` splits the SCRIPT into sentences, takes the two rarest words of each, and searches
the cut for them. It prints only the sentences whose rare words are absent. That list is
short, and you read all of it.

Then the founder is the lookup. A sentence they remember saying and cannot find in the cut
died on one of the buttons, and that is the finding. A sentence they never got to is not a
defect. Put the list in front of them rather than deciding it yourself.

Check the ending hardest. A line that lives only inside a bad take dies with that take, which
is exactly how "Member two finds my lane on YouTube" vanished on 2026-08-30.

**G3. No doubled phrase survived.** Search for any three-word run that repeats back to back.
Zero allowed, except a repeat with no pause between the two attempts, which cannot be cut
without an audible seam.

**G4. No orphan fragments.** These hide in prose, so surface them instead of hunting: print
every sentence under four words, every sentence starting with a lowercase word, and every
sentence with no verb. Read that list. An abandoned lead-in with no object ("we're gonna
read"), a stranded word ("it.", "Click"), half a word.

**G5. Dead air is gone, and the ghost words did not hide it.** Two passes over the timings.

First drop every lone "You" and "Thank you" cue with no sentence around it. Those are
hallucinations over typing noise, and left in they split a long dead stretch into short ones
that pass any threshold.

Then list every gap over 0.3 seconds between consecutive words. Not 0.5: 0.3 is what the
tightness standard locks. Zero allowed, except where the screen is moving through the
silence, which is demo footage held at full length for /assemble to speed up.

Never measure this with an amplitude tool. A room with a noise floor above -30dB reports zero
silence in a take that is full of it.

**G6. Brand words are spelled our way, checked by searching for the WRONG forms.** You cannot
find "Apify" by searching for "Apify" when the transcript reads "F5".

Take the pair list from step 2. Search the cut for each wrong form: every one must return
zero hits. Then search for each correct form: every one must appear at least as often as the
script says it. A term that returns zero on both searches was misheard into something nobody
has named yet, so read the passage where it should have been.

Every hit here goes on the list as "what it says, what it should say". The founder retypes it
in the Descript transcript, which costs nothing and changes no timing.

**G7. The first fifteen seconds are the last attempt, and it is fluent.** This one is an ear
check and it belongs to the founder. Ask them to play the first fifteen seconds and listen
for a stall. The opening is the one place a merely acceptable take is not good enough, and a
page of text cannot hear it.

**G8. Captions are one line each.** Never spanning two sentences, breaking at meaning rather
than width, no function word left hanging at the end of a line. Descript cannot do this
itself, so this gate is really checking that `scripts/resegment.py` ran and that you read the
longest line it printed.

---

## Recorded, not judged

**Length.** We do not have enough episodes to set a range. On 2026-08-30 a 35:01 raw take
became a 10:20 cut from roughly 1,965 spoken script words. One point cannot define a window,
and a window guessed from it fails good cuts. Write the number down and move on. Revisit at
three episodes.

**Breath.** Tight is the standard, but a cut with every pause removed reads as panicked. If
the beat before a turn in the argument is gone, say so as a note. This is judgment and it
does not send a cut back on its own.

## What is NOT a defect

Written into the gates above so you meet them where you would otherwise send something back.
Repeated here so nothing is lost:

- **The founder's own grammar.** The video is them, and plenty of founders are not native
  speakers. Correct the transcript, never their English.
- **A garbled line that was really said in one take.** Said once, it stays; there is nothing
  to cut to.
- **A stumble with no pause around it.** No click-free boundary exists, so it stays.
- **Silence with a moving screen.** Demo footage, and an assembly decision.

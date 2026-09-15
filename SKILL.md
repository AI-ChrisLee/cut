---
name: cut
description: Use this when a recording has been through Descript's three buttons and something in it is still wrong. The founder says "Fix my opening", "Fix my ____", "cut this recording", "/cut", or hands over an SRT exported out of Descript with a script next to it. It reads the cut, names the timestamps to delete, and stops for the founder's read.
---

# Cut

The founder cut the take in Descript by hand. This reads what came out, names what still has
to go, and writes the 3 files the episode keeps.

Say this in your first message on a fresh run, once: **This agent is a base. Once you have
done it your way, tell your squad "update the agent to do it like this."**

The output is locked. Anything that puts graphics, music or B-roll on top treats it as
read-only.

`.claude/squad-roots.md` is the per-repo instance file, and its values win over the
`squad/` paths below, which are worked examples. The episode folder is the one the script
came out of (`squad/episodes/ep01/` on a first week).

## What happened before this runs

In Descript, in this order: Remove filler words, Remove retakes, Shorten word gaps. That is
the cut. Then the founder exported it, as an SRT, because that format carries the
timestamps. Every file this agent opens is a local file on their laptop.

## The rules, read every run

- **Never send, never publish, never upload, never schedule.** This run writes 3 files.
- **Never delete anything yourself.** Deleting a line is typing in Descript, and the
  founder's hand does it. Name the timestamp and quote the words so they can find it.
- **Never invent a line.** A line absent from the exported transcript stays absent.
- **Never re-time audio, never re-encode the original.**
- **Never edit the script.** It is the instruction, not the output.
- **Every finding carries a timestamp** off the SRT. A finding with no timestamp is a
  feeling, and the founder cannot act on it at 11pm.

## The outputs, 3 files every run

1. `<episode>/06_TRANSCRIPT.md`: the cut as a page, the SRT's words with the cue numbers
   and timecodes stripped. This is the review, and it is the only copy of the cut in the repo.
2. `<episode>/06_CAPTIONS.srt`: one sentence per cue, ready to go up as the real subtitle
   track. `/publish` names this file and YouTube takes it as it is.
3. `<episode>/06_REVIEW.md`: every gate passed or failed, the finished length, what was
   deliberately left alone, and the delete list, which is the timestamp, the words quoted,
   and one line saying what goes.

Nothing else gets written. Never the script, never the package, never a second cut of the
same take.

**Resuming.** Read the outputs on disk, never a session's memory. No export on disk, say what
to export and stop. An export and no `06_REVIEW.md`, start at step 1. The 3 files and no read
yet, step 5. Deletes made and a fresh export handed over, step 4 again and rewrite the files.

## The check

**2 files inside THIS agent's folder, next to `SKILL.md`, must open:** `references/rubric.md`
and `references/filming-for-the-cut.md`. Either missing: stop and say the folder was
downloaded without its `references/`, and to copy the whole agent folder in again.

Then 3 things in one pass, reported in one line:

- **The export, on disk.** Ask for the SRT export, because it carries the timestamps the
  delete list is made of. It belongs in the episode folder, next to the script. Missing: say
  it comes out of Descript's export menu, format SRT, and stop.
- **The script for this episode**, `<episode>/03_SCRIPT.md` or wherever the roots file puts
  it. Without it the gates have nothing to compare the cut against.
- **`python3`.** Both scripts here are standard library, so there is nothing to install.

**Anything missing, stop and name the one thing to go get, in one line.** Nothing else in
this run happens until it is on disk.

## Step 1: Read the cut

Write the SRT's spoken lines to `<episode>/06_TRANSCRIPT.md`, cue numbers and timecodes
stripped, so it reads as a page on a phone. Then read it top to bottom before running
anything. Every later step points at a line in this file.

## Step 2: Build the mishearing pairs

Grep the transcript for every brand word, product name, person and tool that appears in the
script. The ones that come back **missing** are the mangled ones, and the line where each
should have been gives you what the transcriber heard instead.

Pairs, never spellings. "Claude Code" came back as "the cloud called", and no list of correct
spellings finds that. Write them to a scratch `terms.tsv`, one line each:

```
Claude Code<TAB>the cloud called,cloud code
```

Fixing a mishearing is typing in the Descript transcript and it costs nothing, so the pairs
go to the founder as "what it says, what it should say" and their hand makes the change.

## Step 3: Run the gates

```bash
python3 .claude/skills/cut/scripts/gates.py <episode>/03_SCRIPT.md <cut>.srt terms.tsv
```

It scores G1, G3, G4, G5 and G6 from `references/rubric.md` against the script and the cut,
and prints the finished length. **Read its whole output.** It prints candidates, never
decisions, and G1's list is the one you read every line of.

Score the gates it does not compute, G7 and G8, by the rubric. Never stop at the first
failure.

**The scores go in `06_REVIEW.md`, never on the founder's screen.** What prints is step 4's
delete list, and G1's own finding when a line died on one of the buttons. That one is
unrecoverable, so it is said out loud the moment it is found.

## Step 4: Turn "Fix my ____" into timestamps

The founder says what is wrong in plain words, one thing at a time. The opening that rambles.
The tangent at minute 9. The place the number got said twice. For each one, in file order:

- the start and end timestamp off the SRT
- the first few words and the last few words, quoted, so they can search the Descript
  transcript for them
- one line saying what goes and what stays

That list is the fix. Deleting those sentences in Descript's transcript deletes them from the
video, so the founder's hand finishes the run.

**The caption file** comes off the SRT exported after the deletes, because that is the one
that matches the video going up:

```bash
python3 .claude/skills/cut/scripts/resegment.py descript-cut.srt <episode>/06_CAPTIONS.srt
```

It prints the longest line and the cue count. Read those. Descript breaks its own captions
where it likes and a paragraph lands on screen as a 3-line block, which is the failure
reported every time.

**The caption look is locked:** Inter Regular at 30, white on a black box at 70 percent,
bottom centre (Chris, 2026-09-11). Regular, never bold. The founder sets that in Descript's
caption panel; this SRT is the copy YouTube takes.

## Step 5: Hand it over

Say it in 3 lines, not a paragraph:

- Read `06_TRANSCRIPT.md` top to bottom. Does it say what you said.
- Read `06_REVIEW.md`. Every gate, and the lines to delete with their timestamps.
- Listen to the first 15 seconds. Fluency by ear is the one call a page cannot make.

Then stop. A missing line is the only thing that cannot be fixed later, so name that first
when you found one. Rough grammar and a jump cut are not reasons to send a cut back.

## Never re-time audio

A recording exported already sped up (Screen Studio does 1.2x with the pitch preserved) is
correct as it came. Re-encoding it to change the rate breaks the voice. The rate changes at
the recorder, or not at all.

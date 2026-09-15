# Cut: install in 60 seconds

This agent is a base. Once you have done it your way, tell your squad "update the agent to
do it like this."

Record one take and fumble as much as you like. Descript's three buttons drop the retakes,
the filler and the gaps. This reads what came out, tells you what is still wrong and exactly
where, and hands you a page to read instead of a timeline to scrub.

## What it runs on

Printed here so you find out now and not at midnight:

- A Descript account, and a take you already ran through the three buttons: Remove filler
  words, then Remove retakes, then Shorten word gaps.
- That cut exported out of Descript as an SRT. It carries the timestamps.
- This week's script, next to it.
- `python3`. Both scripts in here are standard library, so there is nothing to install.

Descript is the cut. Its free plan stamps a watermark on your export, so this runs on a paid
plan.

## Run it

Drop this whole folder into `.claude/skills/` as `cut`, quit and reopen Claude Code, then
say what is wrong in plain words, one thing at a time: **"Fix my opening."**

## What you get

3 files in your episode folder:

- `06_TRANSCRIPT.md`, the cut as a page you can read on your phone.
- `06_REVIEW.md`, every gate passed or failed, the finished length, and the lines to delete
  with their timestamps and the words quoted.
- `06_CAPTIONS.srt`, one sentence per cue, ready to upload as the real subtitle track.

Read the 2 pages, listen to the first 15 seconds, then delete the named lines in Descript
and export the video. That file is the one you upload.

## What it will not do

Touch your Descript project. Re-time your audio. Edit your script. Upload, schedule or
publish anything.

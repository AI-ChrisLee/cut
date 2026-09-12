# Cut: install in 60 seconds

This skill is a base. Once you have done it your way, tell your squad "update the skill to
do it like this."

Record one take and fumble as much as you like. This keeps the last good attempt of every
line, drops the rest, fixes the names the transcriber mangled, and hands you a page to read
instead of a timeline to scrub.

## What it runs on

Printed here so you find out now and not at midnight:

- A paid Descript account with the AI editor.
- The Descript connector authorized once in a live session. It cannot be done in the
  background.
- `ffmpeg` on your laptop.

Credits and transcription minutes are 2 separate meters over there. Know where your balance
is.

**No Descript?** Record one take, cut nothing, and publish that. The week's output is the
video live. (There is a free local path in `scripts/cut.py` if you are comfortable
installing python packages.)

## Run it

Drop this whole folder into `.claude/skills/` as `cut`, quit and reopen Claude Code, then
say: **"Cut this recording."** Give it the original file, never a re-export.

Your session stays open and the lid stays up while it runs.

## What you get

3 files in your episode folder, and a link to download the finished video:

- `06_TRANSCRIPT.md`, the cut as a page you can read on your phone.
- `06_REVIEW.md`, every gate passed or failed, the finished length, and what it deliberately
  left alone.
- `06_CAPTIONS.srt`, one sentence per cue, ready to upload as the real subtitle track.

Read the 2 pages, listen to the first 15 seconds, then say **"Approved."**, or say
everything wrong in one message. The fix is one call, so one message.

## What it will not do

Send a third paid call to the editor. Re-time your audio. Edit your script. Upload,
schedule or publish anything.

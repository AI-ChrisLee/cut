---
name: cut
description: Use this when a one-take recording is done and needs cutting. The founder says "cut this recording", "the recording is done", "edit this take", "/cut", or hands over a video file with a script next to it. It keeps the last good attempt of every line and drops the rest. It runs on Descript and it stops for the founder's read.
---

# Cut

Raw recording in, locked cut out. Keep the last good attempt of every line, drop the rest,
and hand back a page the founder reads instead of a timeline.

Say this in your first message on a fresh run, once: **This skill is a base. Once you have
done it your way, tell your squad "update the skill to do it like this."**

The output is locked. Anything that puts graphics, music or B-roll on top treats it as
read-only.

`.claude/squad-roots.md` is the per-repo instance file, and its values win over the
`squad/` paths below, which are worked examples. The episode folder is the one the script
came out of (`squad/episodes/ep01/` on a first week).

## The rules, read every run

- **Never send, never publish, never upload, never schedule.** This run writes 3 files and
  a Descript project.
- **2 paid calls is the whole budget**, one to cut and at most one to fix. Never a
  third; the remainder goes to the founder.
- **Never re-cut a take the founder approved.**
- **Never invent a line.** A line absent from the raw transcript was never said, and it
  stays absent.
- **Never re-time audio, never re-encode the original.**
- **Never edit the script.** It is the instruction, not the output.
- **Free: everything that reads or exports.** `export_transcript` (format `txt` to read,
  `srt` for captions), `get_project`, `list_projects`, `list_folders`, `wait_for_job`, and
  `publish_project` to render the finished video. Read the result as often as you like.
- **Paid: `prompt_project_agent`, and only that.** It is the sole way to change anything.
  If you are about to ask the editor for a file, stop; there is a free export for it.
- **Descript, and nothing else.** A person can read a cut in its transcript. A timeline of
  226 clips cannot be reviewed. A page of text can.

## The outputs, 3 files every run

1. `<episode>/06_TRANSCRIPT.md`: the cut's transcript, exported free. This is the review.
2. `<episode>/06_CAPTIONS.srt`: one sentence per cue, ready to go up as the real subtitle track.
3. `<episode>/06_REVIEW.md`: every gate passed or failed, the finished length, what was
   deliberately left alone, and the render link once step 6 has run.

Nothing else gets written. Never the script, never the package, never a second cut of the
same take. In Descript, not on disk: the project and its cut composition.

**Resuming.** Read the outputs on disk, never a session's memory. No Descript project for
this recording, start at step 1. A project and no `06_REVIEW.md`, step 4. The 3 files and
no read yet, step 5. Something named wrong, step 6. Approved and no render link handed
back, step 6's render only. Never re-upload a recording Descript already holds, and never
spend a second paid call on a cut the founder already approved.

## The check

**2 files inside THIS skill's folder, next to `SKILL.md`, must open:**
`references/the-one-prompt.md` and `references/rubric.md`. Either missing: stop and say the
folder was downloaded without its `references/`, and to copy the whole skill folder in again.

Then 4 things in one pass, reported in one line:

- A paid Descript account with the AI editor. The paid timeline export is not needed.
- The Descript connector authorized. Check with `list_projects`: it returns a list, not an
  auth error. If it errors, say it has to be authorized in a live session, because it
  cannot be done in the background.
- Credits and transcription minutes. They are 2 separate meters. Say where the balance is
  checked.
- `ffmpeg` on PATH, for the caption step and any local render.

**Anything missing, stop and say the honest alternative in one line:** record one take, cut
nothing, publish that. The week's output is the video live.

## Step 1: Upload the raw take

The ORIGINAL file, not a re-encode. A re-encode carries its generation loss to the upload.

```
import_media
  project_name     "EP01 THE WINNING OFFER"        (creates it; or project_id for an existing one)
  add_media        {"take.mp4": {"content_type": "video/mp4",
                                 "file_size": <bytes>, "language": "en"}}
  add_compositions [{"name": "raw take", "clips": [{"media": "take.mp4"}],
                     "fps": 30, "width": 1920, "height": 1080}]
```

```bash
curl -sS -X PUT -H "Content-Type: application/octet-stream" \
  --upload-file take.mp4 "<upload_url>"
```

Then `wait_for_job` on the returned `job_id`. A 2.8 GB file took about 6 minutes to upload
and 8 to transcribe, and the founder waits in the session, so tell them that. When it
finishes you have a `composition_id` and a transcript.

## Step 2: Read the transcript, free, and build the pairs

**Do this before the paid call.** Descript transcribes on import, so the transcript already
exists.

`export_transcript` with format `txt`. Then grep it for every brand word, product name,
person and tool that appears in the script. The ones that come back **missing** are the
mangled ones, and the line where each should have been gives you what the transcriber heard
instead.

Send pairs, never spellings. "Claude Code" came back as "the cloud called", and no list of
correct spellings finds that.

## Step 3: One call to the editor

`prompt_project_agent` with `references/the-one-prompt.md`, filled in, including the pairs
from step 2. Model: Opus. Keep the returned `conversation_id`.

## Step 4: Score it, free, and write the 3 files

`export_transcript` again and score **every gate** in `references/rubric.md`. Never stop at
the first failure: step 6 has to carry everything, and a partial score is what turns one
call into 5.

- `06_TRANSCRIPT.md`, the exported transcript as it came.
- `06_CAPTIONS.srt`, through the caption step below.
- `06_REVIEW.md`: every gate passed or failed, the finished length, what was deliberately
  left alone, and every failure you already found, so the founder is adding to a list
  instead of starting one.

**The caption look is locked:** Inter Regular at 30, white on a black box at 70 percent,
bottom centre (Chris, 2026-09-11). Regular, never bold.

The burned-in captions are Descript's, and the failure reported every time is a wall of
piled-up lines. The prompt asks for the break in the same call. Where blocks are still
clumped, split them by hand in the app. That is typing, not credits.

The SRT is a separate file and still gets resegmented here, because YouTube takes its own:

```bash
# export_transcript with format "srt", save it, then:
python3 scripts/resegment.py descript-cut.srt <episode>/06_CAPTIONS.srt
```

It prints the longest line and the cue count. Read those.

## Step 5: Hand it over

Say it in 3 lines, not a paragraph:

- Read `06_TRANSCRIPT.md` top to bottom. Does it say what you said.
- Read `06_REVIEW.md`. Every gate, and what I already found.
- Listen to the first 15 seconds. Fluency by ear is the one call a page cannot make.

Then stop. **"Approved."** ends the run at the render, with or without the period.
Everything wrong comes back in ONE message, because the fix is one call. A missing line is
the only thing that cannot be fixed later, so name that first when you found one.

## Step 6: The one fix, then the render

Every failure, theirs and the rubric's, in one prompt. Fix a lost line first and say what to
rebuild it from; restore before you remove.

Then verify it landed by re-exporting and searching for each item literally. The editor has
reported a fix it had not made. **If anything is still wrong after that, do not send a third
call.** Hand the remainder to the founder in `06_REVIEW.md` as minutes of manual work in the
Descript app.

Rewrite the 3 files from the fixed cut. Then `publish_project` to render, and hand back the
download link: that file is the one the founder uploads.

## Never re-time audio

A recording exported already sped up (Screen Studio does 1.2x with the pitch preserved) is
correct as it came. Re-encoding it to change the rate breaks the voice. The rate changes at
the recorder, or not at all.

## If Descript is unavailable

`python3 scripts/cut.py <recording.mp4> <script.md>` cuts locally and free. It needs
`faster-whisper` and `ffmpeg` on the laptop, its transcript is weaker than Descript's, and
there is no page to review. If that is too much: record one take, cut nothing, publish that.

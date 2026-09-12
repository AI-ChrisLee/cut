---
name: cut
description: Use this when a one-take recording is done and needs cutting. The founder says "cut this recording", "the recording is done", "edit this take", "/cut", or hands over a video file with a script next to it. It keeps the last good attempt of every line, drops the rest, fixes the names the transcriber mangled, and writes the transcript, the caption file and the review page the founder reads instead of scrubbing a timeline. It runs on Descript and it stops for the founder's read before anything is final.
---

# Cut

Raw recording in, locked cut out. **Your work, in one line: keep the last good attempt of
every line, drop the rest, and hand back a page the founder can read instead of a
timeline they will not watch.** The founder's part: one read, and one message naming
everything wrong.

```
video + script  ->  read the free transcript  ->  ONE paid call  ->  free check  ->  the founder reads once
```

The output is **locked**. Anything that puts graphics, music or B-roll on top treats it as
read-only. A day was once lost to graphics timed against a cut that then moved.

This skill runs in ANY founder's repo. `.claude/squad-roots.md` is the per-repo instance
file every member-run skill reads first (founder name, product word, the `episodes`
path), and its values win over the `squad/` paths below, which are worked examples. A row
reading "(none yet)" is an unanswered field, not an override: the worked-example path
stands until this run fills it. The episode folder is the one the script came out of
(`squad/episodes/ep01/` on a first week).

## The run map (where you run, where you STOP)

| Beat | Mode |
|---|---|
| 0 THE CHECK | AUTO: the two references, Descript, ffmpeg. Anything missing: say which, and name the one-take path |
| 1 UPLOAD | AUTO: the original file, never a re-export |
| 2 THE PAIRS | AUTO: the free transcript read, every mangled name paired |
| 3 ONE CALL | AUTO: the single paid call to the editor |
| 4 SCORE AND WRITE | AUTO, free: every gate scored, the three files written |
| 5 HAND IT OVER | **STOP · GATE**: the founder reads the transcript and the review, then approves or names everything wrong in one message |
| 6 THE ONE FIX | AUTO: at most one more paid call, carrying every item at once, then the render |

The beat numbers ARE the step numbers below. **Two paid calls is the whole budget**, one
to cut and at most one to fix. Never pause an automated beat to ask a small question, and
never run through beat 5 because the transcript looks fine to you.

**Resuming.** The rule keys on the OUTPUTS, never on a session's memory. Check them in
this order and continue at the first one missing.

| Missing or incomplete | Resume at |
|---|---|
| no Descript project for this recording | beat 1 |
| a project exists and `06_REVIEW.md` does not | beat 4 |
| the three files exist and the founder has not read them | beat 5 |
| the founder named something wrong and `06_REVIEW.md` shows no fix pass | beat 6 |
| the founder said approved and no render link has been handed back | beat 6, the render only |

Never re-upload a recording Descript already holds, and never spend a second paid call on
a cut the founder already approved.

## The outputs (3 files, every run)

1. `<episode>/06_TRANSCRIPT.md`: the cut's transcript, exported free. This is the review.
2. `<episode>/06_CAPTIONS.srt`: one sentence per cue, ready to go up as the real subtitle
   track.
3. `<episode>/06_REVIEW.md`: every gate passed or failed, the finished length, what was
   deliberately left alone, and the render link once beat 6 has run.

Nothing else gets written. Never the script, never the package, never a second cut of the
same take.

In Descript, not on disk: the project and its cut composition.

## Descript, and nothing else

Settled 2026-08-30 after building the alternatives and throwing them away.

Descript wins on the only thing that matters here: **a person can read a cut in its
transcript.** A timeline of 226 clips cannot be reviewed. A page of text can.

| | why it loses |
|---|---|
| Premiere alone | no take-selection operation exists. Silence and filler only. |
| Cutback, AutoCut | take a script, but pick "best", never last |
| EditBuddy, TimeBolt | keep the last take, but accept no script |
| A hand-rolled matcher | works, and its transcript is worse than Descript's, which is where its errors come from |

Do not rebuild these. Each one was built here and thrown away, and the table is the whole finding.

## Credit discipline

The editor **re-reads the whole transcript on every call.** Cost is driven by how many
times you ask, not by how much you change. Measured on a 35-minute take: five calls cost
**271 credits**; the same work stated once costs about **60**.

**Free: everything that reads or exports.** `export_transcript` (format `txt` to read,
`srt` for captions), `get_project`, `list_projects`, `list_folders`, `wait_for_job`, and
`publish_project` to render the finished video. Read the result as often as you like.

**Paid: `prompt_project_agent`, and only that.** It is the sole way to change anything. If
you are about to ask the editor for a file, stop; there is a free export for it.

## Beat 0 · The check

**Two files inside THIS skill's folder, next to `SKILL.md`, must open:**
`references/the-one-prompt.md` and `references/rubric.md`. Either missing: stop and say
the folder was downloaded without its `references/`, and to copy the whole skill folder in
again. A prompt or a rubric rebuilt from memory is wrong quietly, which is the expensive
way to be wrong.

**Then the four things this run needs, checked in one pass and reported in one line:**

- A Descript account with the AI editor. The paid timeline export is NOT needed; the
  deliverables are the Descript project and an SRT.
- The Descript connector authorized. Check with `list_projects`: it returns a list, not an
  auth error. If it errors, say it has to be authorized in a live session, because it
  cannot be done in the background.
- Credits and transcription minutes. AI actions spend credits, transcription spends
  minutes, and they are two separate meters. Say where the balance is checked.
- `ffmpeg` on PATH, for the caption step and any local render.

**Anything missing, stop and say the honest alternative in one line:** record in one take,
cut nothing, and publish that. The week's output is the video live, not the edit.

## Beat 1 · Upload the raw take

The ORIGINAL file, not a re-encode. Everything downstream renders from it, so feeding in
an already-encoded cut carries that generation loss all the way to the upload.

```
import_media
  project_name     "EP01 THE WINNING OFFER"        (creates it; or project_id for an existing one)
  add_media        {"take.mp4": {"content_type": "video/mp4",
                                 "file_size": <bytes>, "language": "en"}}
  add_compositions [{"name": "raw take", "clips": [{"media": "take.mp4"}],
                     "fps": 30, "width": 1920, "height": 1080}]
```

It returns `upload_urls`. PUT the file there, then wait:

```bash
curl -sS -X PUT -H "Content-Type: application/octet-stream" \
  --upload-file take.mp4 "<upload_url>"
```

Then `wait_for_job` on the returned `job_id`. A 2.8 GB file took about 6 minutes to upload
and 8 minutes to transcribe. When it finishes you have a `composition_id`, and you have a
transcript.

## Beat 2 · Read the transcript, free, and build the pairs

**Do this before the paid call.** Descript transcribes on import, so the transcript
already exists.

`export_transcript` with format `txt`. Then grep it for every brand word, product name,
person and tool that appears in the script. The ones that come back **missing** are the
mangled ones, and the line where each should have been gives you what the transcriber
heard instead.

Send pairs, never spellings. On a recent episode "Claude Code" came back as "the cloud
called" and "Apify" as "F5". No list of correct spellings can find those.

## Beat 3 · One call to the editor

`prompt_project_agent` with `references/the-one-prompt.md`, filled in, including the pairs
from beat 2. Model: Opus. Keep the returned `conversation_id`.

## Beat 4 · Score it, free, and write the three files

`export_transcript` again and score **every gate** in `references/rubric.md`. Never stop
at the first failure: beat 6 has to carry everything, and a partial score is what turns
one call into five.

Then write the three files:

- `06_TRANSCRIPT.md`, the exported transcript as it came.
- `06_CAPTIONS.srt`, through the caption step below.
- `06_REVIEW.md`: every gate passed or failed, the finished length, the list of things
  deliberately left alone, and every failure you already found, so the founder is adding
  to a list instead of starting one.

**The caption step.** The look is locked: Inter Regular at 30, white on a black box at 70
percent, bottom centre (Chris, 2026-09-11). Regular, never bold.

The burned-in captions are Descript's, and the failure reported every time is a wall of
piled-up lines. The prompt asks for the break in the same call: one line on screen,
meaning-unit splits, about 45 characters at most. Read the result, and where blocks are
still clumped, split them by hand in the app. That is typing, not credits.

The SRT is a separate file and still gets resegmented here, because YouTube takes its own:

```bash
# export_transcript with format "srt", save it, then:
python3 scripts/resegment.py descript-cut.srt <episode>/06_CAPTIONS.srt
```

One sentence per cue at most, meaning-unit breaks, nothing over about 45 characters, no
function word left hanging. It prints the longest line and the cue count; read those.

## Beat 5 · Hand it over

**STOP · GATE.** Say it in three lines, not a paragraph:

- Read `06_TRANSCRIPT.md` top to bottom. Does it say what you said.
- Read `06_REVIEW.md`. Every gate, and what I already found.
- Listen to the first 15 seconds. Fluency by ear is the one call a page cannot make.

Then stop. "Approved" ends the run at the render. Everything wrong comes back in ONE
message, because the fix is one call.

A missing line is the only thing that cannot be fixed later, so name that first when you
found one.

## Beat 6 · The one fix, then the render

Every failure, theirs and the rubric's, in one prompt. Fix a lost line first and say what
to rebuild it from; restore before you remove.

Then verify it landed by re-exporting and searching for each item literally. The editor
has reported a fix it had not made. **If anything is still wrong after that, do not send a
third call.** Hand the remainder to the founder in `06_REVIEW.md` as minutes of manual
work in the Descript app, against another 45 credits.

Rewrite the three files from the fixed cut. Then `publish_project` to render, and hand
back the download link: that file is what gets uploaded.

## Never re-time audio

A recording exported already sped up (Screen Studio and others do 1.2x with the pitch
preserved) is correct as it came. Re-encoding it to change the rate breaks the voice and
the founder hears it immediately. If the rate is wrong it changes at the recorder, and the
cut restarts from that export.

## If Descript is unavailable

`python3 scripts/cut.py <recording.mp4> <script.md>` cuts locally and free with
faster-whisper. It writes a Premiere sequence, a caption file, and `cut.json`, the keep
ranges you can render with ffmpeg. No account, no upload.

Three things to know before relying on it. It needs `faster-whisper` and `ffmpeg`
installed on the laptop. Its ceiling is its own transcript: on the same take it matched 56
percent of script words where Descript read the retakes cleanly. And there is no page to
review, because the review page IS the Descript transcript.

`parse_script` expects our script shape (`##` sections, direction in backticks, screen
text under `**I type:**`), which is what the script skill writes; a differently shaped
script needs that function adjusted or the match rate collapses.

**Neither path is the simple one.** With no Descript and no appetite for installing
python packages, the answer is one take, no cut, publish that.

## Rules

- **Never send, never publish.** This run writes three files and a Descript project.
- **Never a third paid call.** Two is the budget and the remainder goes to the founder.
- **Never re-cut a take the founder approved.**
- **Never invent a line.** A line absent from the raw transcript was never said, and it
  stays absent.
- **Never re-time audio, never re-encode the original.**
- **Never edit the script.** It is the instruction, not the output.

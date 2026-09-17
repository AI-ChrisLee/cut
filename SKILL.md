---
name: cut
description: Use this when a recording has been edited in Descript and needs its review, its captions and its YouTube listing. The founder says "Cut my raw take.", "Fix my ____" (like "Fix my opening."), "Here's the new export.", "Set this video up on YouTube.", "Here's the link." or "/cut". It reads the SRT exported out of Descript against the script, names what to delete with the times and the words quoted, writes the caption file, writes the listing the founder pastes into YouTube Studio, and logs 1 row in squad/content-log.md. It never opens Descript, never deletes a word and never touches YouTube.
---

# Cut

4 outputs, in this order: `<episode>/06_REVIEW.md` (the gates and the delete list), `<episode>/06_CAPTIONS.srt`, `squad/week/<date>-listing.md`, and 1 row in `squad/content-log.md`.

**The first message of a fresh run** (no `06_REVIEW.md` in the episode folder) carries this line, word for word:

> This agent is a base. Once you have done it your way, tell your squad "update the agent to do it like this."

Open `references/rubric.md` and `references/filming-for-the-cut.md`, and check that `scripts/gates.py` and `scripts/resegment.py` are there. Missing: say the agent folder came without its `references/` or `scripts/`, and stop. No `python3`: say so in 1 line, and stop. Both scripts use only what comes with Python.

## Never

- Never open Descript, never delete a word, never re-time or re-encode a file. The founder deletes, in Descript's text.
- Never upload, schedule, publish or post. Never touch YouTube.
- Never edit the script. Never write a title. Never invent a line, a time or a number.
- Every finding carries its time off the SRT and the words quoted.
- 1 link in the listing, never 2.

## Before it runs, by hand

The founder records 1 take (`references/filming-for-the-cut.md`), then in Descript:

1. Drag the raw take in.
2. Open the AI Tools panel. Remove filler words. Remove retakes. Shorten word gaps.
3. Export, Subtitles, SRT, saved into the episode folder.

No SRT in the episode folder: print these 3 steps, and stop.

## The episode

- The episode folder is the `episode:` line of the newest `squad/week/<date>-package.md`, unless the founder names another. No package: say "Run the Winning Scrape first. The title comes from your package." and stop.
- The script is `03_SCRIPT.md` in that folder. Missing: say "Run /the-money-driven-script first. The edit is read against your script." and stop.
- The export is the newest `.srt` in that folder that is not `06_CAPTIONS.srt`.

## The triggers

| The founder says | This run |
|---|---|
| "Cut my raw take.", `/cut` | 1. The read |
| "Fix my ____" | 2. The fix |
| "Here's the new export." | 3. The captions |
| "Set this video up on YouTube." | 4. The listing |
| "Here's the link." | 5. The row |

Resuming reads the files, never a session's memory. No SRT: the 3 Descript steps. An SRT and no `06_REVIEW.md`: step 1. A review and no `06_CAPTIONS.srt`: wait for "Fix my ____" or "Here's the new export." Captions and no listing: step 4. A listing and no row with its title in `squad/content-log.md`: wait for "Here's the link." The row there: done.

## 1. The read

1. Read the export top to bottom.
2. Build the brand pairs. gates.py finds a word heard wrong inside a line it can match. A brand word heard as noise (Apify as F5) shows under G6 as said with different words. Search the export for every brand word, product, person and tool the script names, and pair each one missing. Write the pairs to a scratch `terms.tsv`, 1 line each, `Claude Code<TAB>the cloud called,cloud code`.
3. Run `python3 .claude/skills/cut/scripts/gates.py <episode>/03_SCRIPT.md <export> terms.tsv` and read its whole output. Score G7 and G8 by `references/rubric.md`. Score every gate, never stop at the first failure. Delete `terms.tsv`.
4. Write `06_REVIEW.md`: every gate passed or failed, the finished length, `## Word fixes` (what it says, what it should say) and `## Delete list` (empty until step 2).
5. Print 3 short lists, in this order, and nothing more:
   - Script lines it cannot find in the edit (G1). A line the founder said and cannot find there was eaten by a button. This list comes first, always.
   - Words spelled wrong (G6): every should-say line gates.py prints, every line under its "Said with different words", plus the brand pairs: what it says, what it should say. Fixed by typing in Descript's text.
   - What still looks wrong (G2, G3, G4, G5): the start time and the words quoted.

   Then: "Listen to the first 15 seconds. Then tell me what's wrong: Fix my ____."

## 2. The fix

"Fix my ____" names 1 thing in plain words: the opening, the part at minute 9, the number said twice. For each:

- the start time and the end time of the cues that hold those words, off the export. An SRT has no time per word, so never a time inside a cue
- the first words and the last words, quoted, so the founder finds them in Descript's text
- 1 line: what goes, and what stays

Nothing on the 3 lists sits in those cues: print their times and their first and last words, say "Nothing in these cues is on the 3 lists. Which words did you hear?", and wait. Nothing goes on the Delete list.

Otherwise, print it and wait. On yes, add it to `## Delete list` in `06_REVIEW.md`, and say: "Delete those words in Descript's text, and retype every word on the Words spelled wrong list. Next one: Fix my ____. All done: export the SRT again and type: Here's the new export."

## 3. The captions

"Here's the new export." takes the newest SRT:

1. Run gates.py on the new export with a `terms.tsv` rebuilt from the `## Word fixes` rows of `06_REVIEW.md` (what it should say, a TAB, what it says), then delete it. "Here's the new export." counts as the yes for every fix printed since the read: add each to `## Delete list`. A script line the first read found and this one cannot was eaten by a delete: say it first. A G6 wrong form still there: name it, say "Retype it in Descript's text, export again, then type: Here's the new export." and stop. A wrong form this run also prints under "Said with different words" may be what the founder said, so it goes under "Still in your video" and never stops the run. Every G1 line the read could not find that this export still cannot, and every G2 filler, G3 finding and G5 gap to delete from the read that is still in this export and not on the Delete list: print each under "Still in your video" with its words quoted and its time off the SRT (a G1 line has no time), then "Fix my ____, or leave it.", and go on.
2. Run `python3 .claude/skills/cut/scripts/resegment.py <new export> <episode>/06_CAPTIONS.srt` and read the longest line and the cue count it prints (G8).
3. Rewrite the whole gates table in `06_REVIEW.md` off this run, with the finished length.
4. Say: "Export the finished video from Descript. That file is the one that goes up. Then type: Set this video up on YouTube."

## 4. The listing

Read:

- The package: the MAIN title, character for character. Never re-titled.
- `06_CAPTIONS.srt`: the chapter times. No captions file: say "Type: Here's the new export." and stop.
- `03_SCRIPT.md`: the hook line (the spoken sentences under the `## 00:00` heading after the sentence that says the title, joined into 1 paragraph) and the `## MM:SS Name` headings.
- The 1 link: the URL on the `Book:` line of `squad/sales.md`, without the full stop after it. No `squad/sales.md`: the `cta` row of `.claude/squad-roots.md`, else 1 question: "What is the 1 link this video sends people to?" Write the answer into the `cta` row, so it is asked once.

Tag the link with `?utm_source=youtube&utm_content=epNN` (`&` in place of `?` when the link already carries a `?`), `epNN` the episode folder's name.

Write `squad/week/<date>-listing.md`, `<date>` the package's date, in this shape:

```
# Listing · <MAIN title>

## TITLE
<MAIN title>

## DESCRIPTION
<what the link gives, in 3 to 6 words>: <tagged link>

<the hook line>

<1 plain paragraph, in the words a buyer types into YouTube search>

CHAPTERS
0:00 <name>
<m:ss> <name>

## PINNED COMMENT
<what the link gives>: <tagged link>
```

- 1 link in the description, the tagged one, at the top. No second link, no link shortener.
- Chapters off `06_CAPTIONS.srt` only. Find each script heading's first sentence in the captions the way gates.py reads words (case and punctuation off, a number and its word the same, so 3 matches "three"): its cue start is the chapter time, the heading's name is the chapter name. The first at 0:00, at least 3, each 10 seconds or longer, or YouTube ignores them all. A heading that runs under 10 seconds folds into the chapter before it.
- No tags, no end screen, no em dashes. No number, claim or tool the video does not say.

Print the listing, then this list, and stop:

1. Upload the video file you exported from Descript.
2. Add `06_CAPTIONS.srt` as the subtitles.
3. Set the thumbnail from the package's main pair. It needs a verified account: youtube.com/verify.
4. Paste the title and the description.
5. Tap your link on your phone. It has to open.
6. Set the hour. YouTube publishes the video then.
7. Studio gives you the video's link once it is scheduled. Type "Here's the link." and paste it.
8. Once the video is public, post the pinned comment and pin it. Then open it in Studio on a computer, press A/B Testing, and add all 3 pairs from the package, title and thumbnail together.

A title-only package: skip the thumbnail in 3 and A/B Testing in 8, and say "Your thumbnails are not built yet. Upload with YouTube's own frame, and add the 3 pairs once they exist."

## 5. The row

"Here's the link." with the URL:

1. The video id: the 11 characters after `v=` or after `youtu.be/`.
2. Append 1 row to `squad/content-log.md`: `date | title | link | video id`, with today's date, the MAIN title, the URL and the id. No file yet: create it with that header row first. The id already in the file: no second row.
3. Print the row, and: "When A/B Testing names a winner, tell the Winning Scrape which pair won: Pair 2 won." A title-only package: in place of that line, print "Your thumbnails come first. Drop 2 to 4 photos of your face in squad/face/, then say: Run the Winning Scrape." Done.

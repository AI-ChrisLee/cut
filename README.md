# execution-content-cut

This agent is a base. Once you have done it your way, tell your squad "update the agent to do it like this."

It takes your video from Descript to YouTube. It reads your Descript edit against your script and tells you what is still wrong, with the times and the words quoted. It turns your export into a caption file, short lines, never 2 sentences on 1 line. It writes the listing you paste into YouTube Studio, with 1 link, and logs the video in `squad/content-log.md`.

**Install.** Installed with the one line on aichrislee.com/free, then quit and reopen Claude Code.

**What it runs on.**

- A paid Descript plan. The free plan puts a watermark on the export. The AI tools use Descript's AI credits.
- Your script, `03_SCRIPT.md`, and your package in `squad/week/`.
- `python3`. The 2 scripts in here need nothing installed.

**Run it.**

1. Record 1 take. A slip: stop, 1 second of silence, then the whole sentence again.
2. In Descript: drag the take in, open the AI Tools panel, press Remove filler words, Remove retakes and Shorten word gaps. Export, Subtitles, SRT, into your episode folder.
3. Type "Cut my raw take." Then "Fix my ____" for anything still wrong, and delete the words it names in Descript's text.
4. Export the SRT again and type "Here's the new export." Then export the video.
5. Type "Set this video up on YouTube." Upload by hand in Studio, off the list it gives you.
6. Type "Here's the link." with the video's link. Once the video is public, post the pinned comment and pin it, then press A/B Testing in Studio and add your 3 pairs.

It never opens Descript, never deletes a word, and never touches your YouTube account.

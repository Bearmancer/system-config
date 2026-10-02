---
name: lyric-romanizer
description: Turn non-English song lyrics into a clean line-by-line study sheet - Romanized original (ASCII, pronunciation-first), English translation, repeated lines removed automatically, and a one-line definition plus sourced etymology for less common Hindustani words. Use this whenever the user pastes or uploads lyrics, a ghazal, qawwali, film song, nazm, or poem-set-to-music in Urdu, Hindi, Punjabi, Persian, Arabic, Korean, Japanese, Chinese, Russian or any other non-English language, or asks to transliterate, romanize, translate, "give me the roman version", "lyrics with meaning", or clean up duplicate lines in a song, even if they don't name the format or paste the text casually mid-conversation.
---

# Lyric Romanizer

For each unique line of a non-English song: the Romanized original, an English translation, and for Hindustani lyrics a short gloss of any uncommon word. Repeats are dropped, so the reader sees each line once.

## Workflow

1. **Dedupe the original script.** Write the pasted lyrics once to a file in the approved temp directory, then run the bundled script with both paths spelled out:

   `python <skill-root>/scripts/dedupe_lyrics.py <absolute-path-to-song.txt>`

   `<skill-root>` is the directory holding this SKILL.md, installed at `C:\Users\Lance\.claude\skills\lyric-romanizer`. A bare relative filename picked up from whatever the working directory is will fail, which is the usual reason this step misfires; piping the text on stdin is the fallback. The script keeps the first occurrence of each line and drops repeats even when punctuation, case, Urdu vowel marks, Devanagari nukta, Latin accents, or a trailing "(x2)" differ, and it removes section labels like [Chorus]. Deduping before romanizing is deliberate: spelling variants collapse while the text is still in one script. Dedupe within one song only, since a line shared by two songs belongs in both. Credits and metadata (writer, singer, album) go.

2. **Romanize** any line not already in Latin script, reading only that language's section of `references/romanization.md`. Pronunciation leads: write what is sung, using doubled vowels, digraphs and the Hindustani capital-letter convention instead of accents. Latin-script input stays as written, apart from scholarly diacritics, which convert to this scheme.

3. **Second dedupe pass.** Two spellings of one line can only coincide after romanizing, so look over the Romanized lines and drop the later of any that now match. This is judgment, not another script run.

4. **Translate** each line into natural English faithful to meaning and register. Render idioms by sense, keep the poetic imagery rather than flattening it, one line of English per lyric line. English words inside the lyric stay as they are.

5. **Gloss** uncommon Hindustani words (see below).

6. **Emit** in the format below, in order of first appearance, and delete the temp file.

## Output format

Each unique line becomes one block: the Romanized line in Markdown italics (`*...*`), sentence case (capitalize the first letter of each line), ending in `<br>`; then the translation; then any gloss lines; then a blank line between blocks:

```
*Romanized original line*<br>
English translation
**word** - definition. Etym: one-line etymology.

*Next romanized line*<br>
English translation
```

Plain Markdown, no code fence around the sheet, no HTML spans or colors. Nothing else - no title, no headings, no commentary between or around blocks, no recap of the work.

## Glossing uncommon Hindustani words

Gloss a word when an ordinary Hindi-Urdu speaker would not reach for it in daily conversation: literary, poetic or Persian/Arabic-heavy vocabulary (firaaq, wasl, hijr, saaqi, dasht, sabaa). Skip words that are everyday even when Perso-Arabic in origin (dil, pyaar, ishq, zindagi, khwaab, yaad, raat, waqt, intezaar, mohabbat, jaan, aankh, dost, duniya). The test is whether a casual speaker would use it over chai; if yes, skip it.

- Hindustani vocabulary - Urdu, Hindi, and Braj/Bhojpuri registers alike; skip glosses for other languages unless asked.
- One line per word under that line's translation, about 25 words maximum. Give the sense the song uses, not the whole dictionary entry.
- Gloss each word once, at its first appearance; a repeated word is a duplicate too.
- An izafat compound (shab-e-hijr) gets one entry covering its parts.
- The etymology is one clause: source language, original form, core sense or root. `references/etymology-sources.md` has the style and worked examples.

Etymology comes from a source, never from memory. `references/etymology-sources.md` says which dictionary serves which layer (Platts and Steingass for Perso-Arabic, Turner's CDIAL for Indic).

## Fetch chain (direct GET first)

Direct hits beat MCP. One `execute` call, `Promise.all` over all shortlisted words. Never rely on one live site: Platts, Steingass and CDIAL share `dsal.uchicago.edu`, so a printed etymology needs a second host - hawramani.com, rekhtadictionary.com, or ScrapeGraph-rendered Rekhta.

1. **Platts by GET**, no bot-block, one round trip:
   `https://dsal.uchicago.edu/cgi-bin/app/platts_query.py?qs=<URDU-SCRIPT>&searchhws=yes&matchtype=exact`
   The `qs` value must be in word script, never roman: query the Urdu-script and Devanagari headword in parallel - either may hit where the other misses. Get the script from the song's own source, or from a plain-GET lyric page that carries it; romanize from attested script, never from guessed spelling.
2. **Persian layer, same request shape**: `.../cgi-bin/app/steingass_query.py?qs=<headword>&searchhws=yes&matchtype=exact`.
3. **Fallback mirror, plain GET**: `https://urdu.hawramani.com/<urdu-script>` (Platts text plus an Origin tag). `https://www.rekhtadictionary.com/meaning-of-<roman>` and `https://www.rekhtadictionary.com/search?wref=rweb&keyword=<urdu-script>` are plain-GET too: senses, Origin language, verse examples, no JS needed.
4. **JS-gated dictionary pages**: ScrapeGraph MCP `scrape({url})` renders them and returns senses, the Origin language tag and the Platts block with Urdu and Devanagari intact; Playwright MCP also works (`browser_navigate`, then `browser_evaluate` on `document.body.innerText`). Plain GET and static scrapers return only boilerplate. `hamariweb.com` and `smule.com` sit behind a JS challenge, `gaana.com` and WordPress-hosted lyric pages do not.
5. Those all fail -> walk the deep-research chain (`C:\Users\Lance\.claude\skills\deep-research\SKILL.md`, "Fast path: every web call"; server pick from its `references/fleet.md`; MCP, then vendor CLI, then POST script). Bot-blocked (401/403/429/503, challenge page, empty body) walks in order, stopping at the first fetch holding the entry: Tavily `tavily_extract`, Firecrawl `firecrawl_scrape` (`proxy: "auto"`, `maxAge: 0`), Exa `web_fetch_exa`, ScrapeGraph `scrape`, Apify `apify--rag-web-browser`, AgentQL `extract-web-data`, Firefox/Playwright MCP, Bright Data `scrape_as_markdown`, Browserbase. ScrapeGraph is the remote endpoint `https://mcp.scrapegraphai.com/mcp` on a metered free plan; `credits` reports what is left. Walk only the words that failed; do not re-run the ones that worked.
6. A credit or auth failure rotates that server's key per the deep-research "Key rotation" section before leaving the server.
7. Chain exhausted: print only the origin language, nothing else. A wrong etymology printed confidently costs more than a bare language tag.

## Speed

Total latency is what the user feels, so cut round trips, not accuracy.

- Read only the section of `references/romanization.md` for the song's language.
- Apply the chai test first; never fetch a word you will not print.
- Shortlist all candidates, then one parallel fetch batch. Four glosses = one round trip, not four.
- Skip the fetch when the word is already confirmed in this project.
- Run the dedupe script once and trust its count.
- One temp file, written once, deleted on emit.
- Emit as soon as the batch lands; no extra verification pass.

## Example (invented lines, Urdu script input)

Input lines (after dedupe): شامِ فراق میں دل اکیلا ہے / دشت میں پیاسا ہوں، ساقی کہاں ہے

```
*Shaam-e-firaaq mein dil akela hai*<br>
In the evening of separation, the heart is alone.
**firaaq** - separation, parting from a loved one. Etym: Arabic firaaq, from root f-r-q "to separate".

*Dasht mein pyaasa hoon, saaqi kahaan hai*<br>
I am thirsty in the wilderness - where is the cup-bearer?
**dasht** - wilderness, desert, open plain. Etym: Persian dasht "plain, wilderness".
**saaqi** - cup-bearer, the one who serves wine. Etym: Arabic saaqi, "one who gives drink", from root s-q-y.
```

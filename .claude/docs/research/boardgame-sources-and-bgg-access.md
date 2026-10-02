# Board-game rules sources and BGG file access

Research for issue #64 (parent #56). Date of research: 2026-09-30.

## Question

Which sources feed a quick board-game rules page, and how can rulebook PDFs from BoardGameGeek (BGG) be fetched within its terms? Specifically: what the BGG Terms of Service say about automated download, what the BGG XML API exposes (files or not), and whether file downloads need a login. Test game: Ark Nova.

Credential rule followed: no BGG cookie, password or token was handled, requested or pasted. Where a login would be needed, this note records that the user must supply access through their own session, and stops there.

## Source kinds for a rules page

Ordered by trust. Use the first kind that answers the question; use later kinds only for what earlier kinds do not cover.

| Kind | Purpose (one line) | Ark Nova example |
|---|---|---|
| Publisher rulebook PDF | Primary text for every rule claim. | https://capstone-games.com/cdn/shop/files/Ark-Nova-Rulebook.pdf (English publisher) |
| Publisher product or rules page | Finds the current rulebook version and links to FAQ and errata. | https://capstone-games.com/products/ark-nova ; https://www.feuerland-spiele.de/spiele/arche-nova/ (German original) |
| Publisher or designer FAQ | Official answers to rules questions the rulebook leaves open. | "Ark Nova Official FAQ" file, https://boardgamegeek.com/filepage/235760/ark-nova-official-faq |
| Official errata and amendments | Corrections that override the printed rulebook; always check the version date. | Usually a publisher page or a BGG file posted by the publisher. None found separately for Ark Nova this session. |
| BGG Files tab | Rulebook copies, translations, player aids, official FAQ, fan summaries. Check the uploader and the "official" marking before trusting. | https://boardgamegeek.com/boardgame/342942/ark-nova/files (25 entries seen, mostly pdf, two zip) |
| BGG game forums, rules threads | Clarifications; a designer or publisher reply outranks other users. | Forum list is reachable through the XML API `forumlist`, `forum` and `thread` commands (see below). |
| Beginner strategy guides | Only for a "how to start" section, never for rules. | https://boardgamegeek.com/thread/3648569/ark-nova-for-new-players-in-five-easy-steps-2025-e ; https://boardgamestrategy.blog/2026/05/20/ark-nova-first-three-rounds/ |
| Other rules sites | Second witness for numbers and icons; community-run, never a primary. | http://en.doc.boardgamearena.com/Tips_arknova |

URL audit (`check_urls.py`, 2026-09-30): the five non-BGG URLs above returned 200. Every boardgamegeek.com HTML URL returned 403 (Cloudflare challenge) and the `xmlapi2` URL returned 401; the BGG pages were confirmed live through Firecrawl (`proxy: "auto"`, HTTP 200).

## BGG access answer

### Ark Nova id

BGG id is 342942 (`https://boardgamegeek.com/boardgame/342942/ark-nova`), found through a search result and confirmed by the game page and its files page.

### Terms of Service on automated access

Source: https://boardgamegeek.com/terms (fetched through Firecrawl on 2026-09-30, HTTP 200; the page's version date was not captured).

- Automated access is allowed only at human-like request rates: "You shall not use or launch any automated system, including without limitation "robots," "spiders," or "offline readers," that accesses the Geek Websites in a manner that sends more request messages to the BoardGameGeek servers in a given period of time than a human can reasonably produce in the same period by using a conventional online web browser, except as expressly permitted by BoardGameGeek."
- Personal data: "You agree not to collect or harvest any personally identifiable information, including but not limited to account names, from the Geek Websites."
- AI use: "You agree not to use the Geek Websites to train or otherwise use as data for an AI (Artificial Intelligence) or Large Language Model (LLM) system."
- The terms contain no sentence that names file downloads as allowed or forbidden. The only file sentence found is a risk disclaimer: "Any download of software, files, or other materials or any other use of the content on BoardGameGeek is at your risk."

Reading for this project (interpretation, not a legal opinion): a slow, human-rate fetch of a few files is not barred by the robot clause. The AI clause is the risk: feeding BGG-hosted content to an LLM to build a rules page may count as "use as data for an AI or LLM system". Publisher-hosted PDFs avoid this question entirely, so prefer them.

### XML API terms

Source: https://boardgamegeek.com/wiki/page/XML_API_Terms_of_Use

- "BGG grants you a worldwide, non-exclusive, royalty-free license to reproduce and display the data available through the BGG XML API, including User Submissions, solely for strictly non-commercial purposes and solely as permitted by the XML API provided by BGG."
- "Use of the XML API--or any of the data on the site--to train an AI (Artificial Intelligence) or Large Language Model (LLM) system is strictly prohibited."
- "You may not modify the data, including User Submissions, retrieved through the BGG XML API in any way. In all uses of the BGG XML API, you shall credit BoardGameGeek by name as the source of the data."

Source: https://boardgamegeek.com/using_the_xml_api (version date 2025-07-02)

- "Registration and authorization is required for use of the XML API."
- "In addition to our public facing XML API, we have several other private APIs used by our website. Unless otherwise noted or authorized, we are granting no license for use of those endpoints."
- Requests carry an `Authorization: Bearer <token>` header from a registered application (https://boardgamegeek.com/applications).

### What the XML API exposes

Source: https://boardgamegeek.com/wiki/page/BGG_XML_API2

Commands listed: `thing`, `family`, `forumlist`, `forum`, `thread`, `user`, `guild`, `plays`, `collection`, `hot`, `search` (`geeklist` is marked not yet updated). There is no files command. `thing` has no parameter for files; it returns item data, versions, videos, stats, marketplace and comments. The only bulk download the page names is a CSV of game names, ids and ranks at https://boardgamegeek.com/data_dumps/bg_ranks.

Conclusion: the XML API cannot list or download rulebook files. It can supply forum threads (for rules clarifications) once an application token exists.

Live test, 2026-09-30: `https://boardgamegeek.com/xmlapi2/thing?id=342942` and a `search` call both returned HTTP 401 with the body "Unauthorized. See https://boardgamegeek.com/using_the_xml_api". Without a registered token the API is closed, matching the documentation.

### Are file downloads gated by login?

- The Ark Nova files page (`/boardgame/342942/ark-nova/files`) lists 25 file entries to an anonymous fetch. Each file page (for example `/filepage/235760/ark-nova-official-faq`) shows the file names, sizes and download counts ("8.7MB · 13K Downloads") to an anonymous fetch. The anonymous scrape exposed no download link on the file page.
- Plain HTTP clients (curl, the URL audit script) get 403 from Cloudflare on every BGG HTML page, so unattended fetching needs the deep-research fetch chain; Firecrawl with `proxy: "auto"` succeeded on step 2.
- Whether the file bytes themselves need a login was not tested, because testing means using an account session, which this task forbids. Recorded route: if BGG files are wanted, the user downloads them from their own logged-in browser (or supplies access through their own password-manager or session) and drops the PDFs into the workspace. The agent never receives the cookie.

## Recommendation

- Build the rules page from publisher PDFs and official FAQ or errata first; they need no BGG account and avoid the AI-use clause.
- For BGG-only material (official FAQ posted as a BGG file, translations), ask the user to download by hand and place the files locally.
- For forum clarifications, either read threads by hand or have the user register an XML API application (non-commercial) and supply the token through their own secrets mechanism.

## Unverified

- Whether BGG file downloads (the actual PDF bytes) require a login. No download was attempted; one Reddit search snippet (https://www.reddit.com/r/boardgames/comments/zom6k7/gamers_without_bgg_accounts/) says a user "only logged in to access files on BGG", which is anecdotal. Reddit could not be fetched here, so the full comment was not read.
- The version date of https://boardgamegeek.com/terms was not captured.
- Whether reading a BGG-hosted PDF with an LLM to write a rules page breaches the AI clause. This is an interpretation, not legal advice; ask the user or BGG.
- Whether an official Ark Nova errata document exists apart from the FAQ; none was found.
- The exact URL shape of BGG file downloads (`/file/download_redirect/...`) was not observed in this session.
- Whether XML API token registration would be approved for a non-commercial personal rules page ("it may be a week or more" per the guide).

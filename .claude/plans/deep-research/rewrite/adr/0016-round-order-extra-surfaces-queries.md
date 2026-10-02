# Round order, extra lawful surfaces, query rewriting, Wayback position

- Round order: R1 keyword, R2 semantic, R3 answer/agent engines, R4 scholarly/archive APIs, R5 crawl/browser. Structured extraction belongs to the fetch ladder.
- Registry also holds free lawful surfaces: OpenAlex, Crossref, Semantic Scholar, arXiv, Unpaywall; Wayback CDX/availability, Wikisource, Internet Archive full text; Wikipedia/Wikidata, BGG XML API (public, no login or cookies); yt-dlp, pdftotext, OCR, Playwright. Maximal coverage across reputable sources; no shadow libraries (ADR 0010).
- Each round rewrites the query: supporting, opposing, primary-source, other-language. Other-language rounds search in the source language; extractor translates; ledger cites the original.
- Fetch ladder: direct, Tavily extract, Firecrawl, Exa cache, Wayback, then heavy tools (ScrapeGraph, Apify, AgentQL, browser, Bright Data, Browserbase).

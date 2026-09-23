# Source adapter — books, long articles, papers, lecture notes

The course engine is source-agnostic (see SKILL.md); this adapter covers text sources. The one structural difference from video: "chapters" come from a table of contents or headings (timestamps serve that role for video), and the risk class in the text is OCR/conversion damage (ASR garble is the video-side equivalent).

## Acquire

- **Plain text / HTML** (e.g. Project Gutenberg, a magazine piece): download to the temp dir (`Invoke-WebRequest` / `curl`), keep the URL in NOTES.md.
- **PDF**: extract the text layer (the `pdf` skill, `pdftotext`, or python `pypdf`). Scanned PDFs need OCR; treat the result as machine text (corrections pass below).
- **EPUB**: it is a zip; unzip, read the XHTML, strip tags.
- **Papers**: abstract + full text; keep the DOI/URL.
- Store the raw file plus one working text copy in temp; chapter slices go to the workspace's `reference/transcripts/` just like video slices.

## Segment

- **Book** → the table of contents is the chapter map. Front matter (preface, edition notes, translator's note) counts as apparatus alongside the chapters.
- **Article / paper** → section headings. Under a few thousand words with no headings, one chapter covers the whole piece; longer pieces get a split the user confirms — ask the user how to split.
- **Lecture notes** → the notes' own sections.
- The chapter map table goes into NOTES.md exactly like a video's (`| # | Pages | Chapter | Essential? |`).

## Apparatus mining (mandatory)

- Bibliography, footnotes, endnotes, reference list = the source's own citations → per-chapter Sources block entries (hyperlinked to the actual page, no bare URLs) and the **first** verification targets. RESOURCES stays split-source retained until migration.
- Preface/introduction usually states method and sources; the abstract does it for papers.
- Editions and translations matter: record translator and edition in NOTES.md, and name the translation when quoting.
- Integrate: corrections land as inline verdicts in the narrative beside the quoted wording, with their citations in the Sources block; unfindables read "the source's account, unverified" in narrative and land in RESOURCES Gaps too. Max-twice hyperlink rule: each target at most twice per page, once in context and once in the Sources block.

## Corrections pass (mandatory — SKILL.md Step 3)

OCR and bad conversions garble text the way ASR garbles speech: split words, wrong characters (rn/m, 1/l), mangled names and numbers, hyphenation across line breaks. The pass:

1. Fix evident errors; log each in the slice's corrections table as `heard -> corrected -> basis`; canonical forms go to the glossary.
2. Ambiguous: keep the original and flag it inline — every guess goes on record with its basis.
3. Numbers, pages, and names are the high-risk class: a number that reaches a treatise carries a second copy beside it (another edition, publisher preview, the original scan).

## Quoting

- Quote with a locator — chapter + section/paragraph, and page when pagination is stable — so the user can find it.
- The source's own wording stays verbatim once corrected; corrections to the text itself live in the corrections table, beside the quote they correct.

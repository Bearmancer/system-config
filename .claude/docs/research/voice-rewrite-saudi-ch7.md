# deepwork: saudi-pakistan-ch7 + voice rewrite (2026-10-01)

## Goal (user-confirmed)
1. TOC restructure: CANCELLED — "change nothing" on indexes.
2. Rewrite ALL 36 lessons, all 4 courses: learning-first teacher voice, strip verification/meta-talk ("verified", "cross-checked", "audit", verdict/confidence language). KEEP inline source links.
3. Saudi: keep 6 chapters, ADD ch7 = Pakistan's peoples/demographics (Bengali/non-Bengali, Urdu/Muhajir, Hindu/Muslim, Bengal, Kashmir, Balochistan, Pashtun, Afghanistan) from Places video JQfq4kSZt40 (~2026-08-18), esp. its India + Bangladesh chapters. No timestamps given.
4. ch7 ships learning-first from the start (not re-rewritten in lane B).

## Phases & lanes
- P1 (parallel, now):
  - res-1 @researcher: ch7 content pack → saudi/research/ch7-pakistan-peoples.md + transcript in reference/transcripts/. Tier 1, URL audit via skill check_urls.py.
  - fix-1 @fixer: afghanistan (7) + ark-nova (9) voice rewrite.
  - fix-2 @fixer: russia (14) voice rewrite.
  - fix-3 @fixer: saudi (6) voice rewrite.
  - Shared brief: .slim/deepwork/voice-rewrite-rules.md
- Gate 1 @oracle: after P1 — content integrity vs voice edits, ch7 pack quality.
- P2 @fixer: build ch7 yaml+html + course-index.js entry + index list + ch6 footer nav (after saudi lane done).
- Gate 2 @oracle: ch7 build.
- P3 verify (orchestrator): link check, yaml/html parity, hash sync, commit, publish per memory #4 checklist.

## Ownership
- fix lanes exclusive per course dir (lessons/*.{yaml,html} only). Researcher writes only saudi/research/ + saudi/reference/transcripts/. P2 later touches index/ch6-footer/course-index.js — after fix-3.

## Status
- P3 COMPLETE 2026-10-01: Gate-2 notes 1-4 applied orchestrator-side (tripartite reword, pack outline-note, ch6 Next label, index bridge clause). Final verify: drift 0 corpus-wide, 0 broken internal links. Commits: 0899d2e rewrite (41f) + a4c0276 ch7 (8f). Pages 42e90ef pushed, built, live-bytes confirmed (index seven-chapters, ch7 200+title, course-index ch7; first 404 = propagation lag). GATE 2 consumed (PASS-WITH-NOTES, 0 blockers, no re-review). Task DONE.
- P2 BUILD DONE+mechanically verified (fix-3): 07-ch7-the-identity-tangle.{yaml,html} (83/94 lines, 19 sources), index li+intro, course-index ch7, ch6 Next. Gate 2 dispatched (ora session, attempt 1/3). P3 after gate: final link audit on all 4 courses' served set, commit (voice rewrite + ch7 + pack), publish per memory #4, Pages push.
- F4-6 REMEDIATED+accepted: pack 19 claims, fidelity map honest, §7 video-only flagged. All gate findings cleared. P2 build dispatched via fix-3 (ses_f0bf69863ffewm48VTdZFKYtaR).
- F1-3 REMEDIATED+VERIFIED (fix-2): russia 05/06/07 re-attributed, yaml+html parity confirmed orchestrator-side. F4-6 (res-1 pack amendments) still running; P2 build gated on it.
- GATE 1 ora-5 PASS-WITH-NOTES: F1-3 russia hedges hardened at 05/06/07 (re-hedge required, mandatory); F4 pack add claims 17-19 (Hindu/Muslim pillar from transcript line 14; West Bengal sourced-or-dropped); F5 transcript relabel (only preamble/AFG/India verbatim; 5 sections abridged — "No paraphrase" header false, pack ~55k claim false); F6 outline §7 Bangladesh items source-or-mark-video-only. Remediation: res-1 resume (B) + fixer (A). Build brief C recorded for P2 (mirror 06 skeleton, data-current=ch7, no "chapters"/timestamp language, verbatim-quote only 3 sections, pack 200-OK URLs only).
- res-1 RECONCILED+VERIFIED: transcript 35KB verbatim + pack 15KB (16 claims 14full/2partial, outline 7 sections tagged inferred, URL audit log, contested section present, amendment labels applied). Gate 1 dispatched to @oracle.
- fix-2 RECONCILED+VERIFIED: russia 28 files ±248/254, grep 0 meta-hits. COURSE-WIDE yaml→html body-line audit: TOTAL drift=0 (all 4 courses). Voice rewrite P1 lanes 3/3 complete; only res-1 (ch7 pack) pending.
- fix-3 RECONCILED+VERIFIED: saudi ch02-06 rewritten (10 files, +/-64 balanced, yaml+html synced), ch01 clean untouched, grep 0 meta-hits, URL sets per-file identical (64/64 pairs).
- fix-1 RECONCILED+VERIFIED 2026-10-01: 5 files changed (ark-nova ch01/ch08 yaml+html, ch07 yaml), Afghanistan 0 edits (already clean), grep 0 meta-hits both courses, yaml-only URL in ch9 = legit sources-list field, no action.
- Gate 1 check added: video has no official chapters (verified via full extract, no Chapters block) — ch7 pack must label India/Bangladesh section bounds as inferred transcript [N:MM] segmentation, not creator chapters. Amendment queued to res-1.
- P1 dispatched 2026-10-01: res-1=ses_f0bf69870ffewLph1uZ76qZs0z (ch7 pack), fix-1=ses_f0bf6986dffeDVdv3HXMAQSfDq (afghan+arknova), fix-2=ses_f0bf69865ffeeVo3QyqOW3eKxp (russia), fix-3=ses_f0bf69863ffewm44VTZFKYtaR (saudi). TOC part cancelled by user ("change nothing"). Awaiting terminals → Gate 1 oracle → P2 ch7 build fixer (mirrors lesson 06 yaml/html pattern; touches index.html ol, course-index.js, ch6 footer, new ch7 files; after fix-3) → P3 verify+commit+publish (memory #4 checklist).

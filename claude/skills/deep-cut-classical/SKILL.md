---
name: deep-cut-classical
description: Find obscure classical works by skipping the overplayed canon. Use whenever user asks for classical recommendations, says bored of Beethoven/Mozart/Tchaikovsky, wants new orchestral works, new symphony/concerto/overture to explore, says ulw-research classical, or wants deep cuts beyond usual suspects. Triggers even if user does not name this skill.
---

# Deep-Cut Classical Work Finder

Recommend unfamiliar orchestral works. Default bias: exclude famous, over-recorded repertoire. Dig past canon. Work-level only. Every pick names a specific work with verified timing.

## Core rule

Never recommend a banned composer unless the user explicitly names it to unban it. No "just one Beethoven exception." Unbanning is scoped to that composer, that turn — "allow Dvorak this once" unlocks only Dvorak, not the rest of the list.

If the user names a banned work as a style reference ("I like Rach 2, what next?"), use it as an anchor only, never as a pick. State the anchor once — "Anchor: [banned work] -> deep-cut works below" — then drop it.

## Ban list

Skip every composer below unless the user names it explicitly. Two origins, same rule: **user** = the user named this composer directly; **default** = accepted into the ban automatically because it sits in the same overplayed tier, listed here with the reason. Era bans (below the table) carry no exceptions.

| Composer | Origin | Reason |
|---|---|---|
| Rachmaninoff | user | — |
| Beethoven | user | — |
| Brahms | user | — |
| Mendelssohn | user | — |
| Bruch | user | — |
| Mozart | user | — |
| Haydn | user | — |
| Bruckner | user | — |
| Mahler | user | — |
| Schubert | user | — |
| Schumann | user | — |
| Stravinsky | user | — |
| Tchaikovsky | user | — |
| Ravel | user | — |
| Debussy | user | — |
| Richard Strauss | user | — |
| Johann Strauss I | user | — |
| Johann Strauss II | user | — |
| Eduard Strauss | user | — |
| Josef Strauss | user | — |
| Wagner | user | — |
| Prokofiev | user | — |
| Scriabin | user | — |
| Wetz | user | — |
| Tyberg | user | — |
| Shostakovich | user | — |
| Sibelius | user | — |
| Sousa | user | — |
| Walton | user | — |
| Vaughan Williams (RWV) | user | — |
| Suppe | user | — |
| Offenbach | user | — |
| Verdi | user | — |
| Rossini | user | — |
| Liszt | user | — |
| Weingartner | user | — |
| Korngold (Erich Wolfgang) | user, added 2026-09-20 | F-sharp symphony over-recommended |
| Bax (Arnold) | user, added 2026-09-20 | lush circuit |
| Enescu (George) | user, added 2026-09-20 | 55-min staple |
| Stenhammar (Wilhelm) | user, added 2026-09-20 | over-recommended Swedish |
| Atterberg (Kurt) | user, added 2026-09-20 | same Swedish lush circuit |
| Schmidt (Franz) | user, added 2026-09-20 | requiem staple |
| Rott (Hans) | user, added 2026-09-20 | Mahler-feeder staple |
| Marx (Joseph) | user, added 2026-09-20 | overpushed |
| Dvorak | default | symphonies/concertos ubiquitous |
| Grieg | default | Peer Gynt / Piano Concerto everywhere |
| Chopin | default | piano canon, over-referenced |
| Bach (J.S.) | default | explicit Baroque anchor |
| Handel | default | explicit Baroque anchor |
| Vivaldi | default | Four Seasons fatigue |
| Pachelbel | default | Canon fatigue |
| Saint-Saens | default | Organ Symphony / Carnival overplayed |
| Bizet | default | Carmen / L'Arlesienne overplayed |
| Puccini | default | opera canon bleeds into concerts |
| Mussorgsky | default | Pictures / Night on Bald Mountain overplayed |
| Rimsky-Korsakov | default | Scheherazade overplayed |
| Khachaturian | default | Sabre Dance fatigue |
| Holst | default | Planets overplayed |
| Elgar | default | Enigma / Pomp overplayed |
| Copland | default | Fanfare / Appalachian overplayed |
| Gershwin | default | Rhapsody in Blue overplayed |
| Orff | default | Carmina Burana overplayed |
| Smetana | default | Ma vlast overplayed |
| Gounod | default | Faust / Ave Maria overplayed |
| Berlioz | default | Symphonie fantastique fatigue |
| Weber (Carl Maria von) | default | Freischutz / Oberon overture staple |
| Borodin | default | Polovtsian Dances everywhere |
| Glinka | default | Ruslan overture anchor |
| Glazunov | default | ballets / violin concerto staple |
| Kabalevsky | default | youth concerto circuit |
| Bartok | default | Concerto for Orchestra saturation |
| Kodaly | default | Hary Janos / Galanta staple |
| Janacek | default | Sinfonietta everywhere |
| Nielsen | default | Sym 4/5 over-recommended Scandinavian |
| Respighi | default | Pines / Fountains overplayed |
| Faure | default | Pavane / Requiem fatigue |
| Dukas | default | Sorcerer Apprentice one-work fatigue |
| Chabrier | default | Espana encore |
| Massenet | default | Meditation bleed |
| Delibes | default | Coppelia / Sylvia ballet staple |
| Lehar | default | Merry Widow operetta staple |
| Barber | default | Adagio single-work fatigue |
| Bernstein | default | Candide / West Side bleed |
| Rodrigo | default | Aranjuez guitar-concerto monopoly |
| Suk (Josef) | default | Asrael circuit |
| Myaskovsky (Nikolai) | default | Sym 6 circuit |
| Alfven (Hugo) | default | Swedish lush staple |
| Fibich (Zdenek) | default | Czech sym staple |
| Novak (Vitezslav) | default | Czech late-romantic staple |
| Dohnanyi (Erno) | default | Sym 1/2 staple |
| Draeseke (Felix) | default | Tragica circuit |
| Goldmark (Karl) | default | Rustic Wedding staple |
| Magnard (Alberic) | default | French sym staple |
| Ropartz (Guy) | default | French sym staple |
| d'Indy (Vincent) | default | French sym staple |
| Chausson (Ernest) | default | Bb sym staple |
| Balakirev (Mily) | default | Islamey bleed |
| Lyapunov (Sergei) | default | Sym 2 staple |
| Taneyev (Sergei) | default | C minor staple |
| Kalinnikov (Vasily) | default | Sym 1 staple |
| Gliere (Reinhold) | default | Ilya overpushed |
| Bantock (Granville) | default | Hebridean staple |
| Parry (Hubert) | default | English sym staple |
| Stanford (Charles Villiers) | default | Irish sym staple |

Era bans: all Medieval, all Baroque. No exceptions.

Walton appears once in the table; a duplicate request for it is collapsed to this single entry.

## Priority order

1. Orchestral composers first: substantial symphony, concerto, tone poem, overture, suite output.
2. Chamber: ignore unless the user explicitly asks — the ask must use one of these words: chamber, quartet, trio, sonata, solo piano, solo instrumental.
3. Vocal: deprioritize to last resort. When forced to include it, order choral-orchestral composers before solo-vocalist composers, and flag the fallback: `[slim-pickings vocal fallback]`. Never lead with vocal.

Why: the user wants orchestral discovery. Chamber and vocal picks flood the answer with small-scale names and crowd out the target repertoire.

## ulw-research hook

Two modes, same ban list and priority order in both:

- Keyword `ulw-research` present: run a full research pass. Follow the source order below. Verify composer dates, era, output types. Return an evidence-backed shortlist.
- Keyword absent: answer from knowledge directly. No web calls required unless a composer detail is uncertain.

The keyword controls depth, not taste — it never lifts a ban.

## Source order (verify in this order)

1. Grove / Oxford reference for composer dates, era, output
2. Publisher pages (Universal, Barenreiter, Schott, Eschig) for scoring and catalog scope
3. Orchestra program notes (LSO, Berlin Phil, Concertgebouw, LA Phil) for context
4. Labels with deep catalog: Chandos, Hyperion, BIS, Naxos, CPO, Capriccio
5. Streaming / YouTube only for a pointer, never for facts

If sources conflict on dates, prefer the catalog entry. State the conflict in one line.

## Timing verification (mandatory)

Past failures that made this mandatory (2026-09-20):
- Louis Glass Sym 5 Op57 stated as 60 min with finale chorus. Correct per label range: 35-40 min, orchestra only, no chorus. Raiskin 35:36, Todorov 41:37.
- Paderewski Polonia stated as a flat 75. Correct: 74:13 complete Maksymiuk vs 63:39 cut DUX Boguszewski (24:37+14:32+24:38). The 75 figure is the uncut ideal — state range and cut status.
- Tournemire Sym 7 stated ~90 from a single forum line. Correct: Bartholomee Qobuz stems ~14:22+15:55+15:07+~15+15:44 ≈ 75 total; 90 is only an upper bound. Forum-only numbers are banned as a timing source.

Rules for every duration stated:

1. Cite the publisher-stated duration (if any) plus two independent label track totals (Naxos / CPO / Chandos / Hyperion / BIS / Qobuz / Discogs / Presto). Give the movement breakdown with the sum. Example: Glass 5 CPO 35:20 = 10:28 + 6:42 + 5:50 + 12:20.
2. Cross-check the movement sum yourself; if it contradicts the stated total, say so. Never copy an album total that covers two works (Apple 1h29 = Sym7+Sym3; Naxos 68:26 = Glass 5+6).
3. Flag complete-vs-cut for any work with known cuts. Paderewski's cuts fall in movement I and the finale per Hyperion — state "74:13 complete Maksymiuk – 63:39 cut Boguszewski/DUX." Never collapse to one number.
4. If recordings differ beyond tempo variance, state the range with names: "35:36 Raiskin – 41:37 Todorov." Never collapse to a memory number.
5. Copy instrumentation exactly from the publisher score/parts. Never add chorus, organ, or soloists unless the publisher/label lists them.
6. Disambiguate namesakes — Louis Glass (1864-1936) is not Philip Glass (1937-). Check this every time.
7. Forum posts (TalkClassical, Reddit) are leads only, never a timing source on their own; back every forum-sourced number with a publisher or label citation.
8. For a length-constrained request (e.g. 45-60 min, "epic"), exclude a work whose verified maximum falls below the requested minimum. Glass 5's max is 41:37, so it's excluded from a 45+ request.
9. Never claim a finale or chorus without movement-track evidence. Mark an unverifiable claim `[unverified — dropped]` and omit it from length-filtered answers.

## Output format

Work-level only. Every pick names one specific work. For each pick, return:

```
Composer (dates) — Work, Op./Cat. (year) [forces, duration with two timing sources]
Evidence:
- [review / program note / composer note / analysis]: sourced fact about scoring, form, theme treatment, reception. Name the source.
- [second source, different type where possible]: same.
Start with: movement/section to sample first + what to listen for per cited analysis.
Recording: one specific recording (conductor / orchestra / label).
```

Rely solely on official findings from online sources. State only what sources report. Every duration carries its two timing sources — no unsourced numbers. The timing verification rules above apply to every pick.

Default 5 works, max 10, minimum 3. An explicit 20/30-work request overrides the max.

Always end with one line: `Skipped: [banned names relevant to request] excluded per ban list.`

## Examples

**Example 1**
Input: uplifting late-romantic symphony like Brahms 1, no usual suspects
Output: a specific work pick with dates, opus, year, forces, verified duration range, sourced evidence, movement to sample, recording. `Skipped: Brahms, Tchaikovsky, Dvorak excluded per ban list.`

**Example 2**
Input: dark fast orchestral work, ulw-research
Output: full research pass, allowed works only, dates and durations verified via catalogs and labels, chamber ignored, vocal absent. `Skipped: Stravinsky, Shostakovich, Bartok excluded per ban list.`

**Example 3**
Input: something for string quartet
Output: chamber explicitly requested, so the chamber lane is allowed this turn. Composer bans and timing verification still apply. Skipped line stays intact.

## Edge cases

- User explicitly requests a banned composer: comply for that composer only, keep the rest of the ban list active.
- User requests Baroque/Medieval: remind them the era ban is active and ask for an explicit override. Never comply silently.
- User requests vocal/choral: comply, prefer choral, flag the soloist fallback only if forced into it.
- Request scope is unclear: default to orchestral, post-1750, non-chamber, non-vocal.
- Never recommend an arrangement of a banned work as a loophole (e.g. a Liszt piano transcription of a Beethoven symphony) — banned material stays banned regardless of arranger.

# Change journal

The list of what has been done, most recent at the top. **To read before
proposing anything** — this is where you see whether an idea has already been
tried, and what it gave.

One line per archived change, in the form:

`NNNN — <title> — YYYY-MM-DD — <what it gave, in one sentence>`

---

## Archived changes

`0008` — **sort the notebook in two** — 2026-08-15 — `STYLE.md` was filed by
where the ideas came from, while the question actually asked of it is always
"does this run?". Two parts: 5 that run (3 of them half, with what is missing
named), 8 that are only ideas. An entry condition for part 1: say **where** the
idea lives, otherwise nobody will know next year whether it still runs.

`0007` — **validate the tier ranking, and remove subject–verb–object** —
2026-08-15 — the ranking of features by usefulness is **validated by Meo**, which
unblocks reordering the course. SVO removed from the content: its entry presented
it as the beginner's safety net, and that is the argument against — a French
speaker already places subject-verb-object without thinking. `đã` and "verbs
never change" move up to tier 1, the second because it raises the question the
first answers. Tiers 8 / 10 / 9 across 34 features.

`0006` — **attach eight features to the word they are about** — 2026-08-15 — the
`after` field makes a feature come right after its word instead of waiting its
turn. Eight features named their word in their own title without declaring it:
median gap between a feature and its word brought down from **46 items to 1**.
Two of them, `không` and `có`, are tier 1. Checked before writing that none was
delayed. Seven others legitimately have no anchor word — they are about a shape,
not a word.

`0005` — **bring a feature back as an application** — 2026-08-15 — the measured
defect is closed: features go from a level of 1, never seen again, to a median of
4, against 4 for words. A `discrete` feature enters the draw and comes out as a
sentence to produce, capped at one per close — without which 86% of closes would
have carried two or more during the transition. Surfaced three invisible things:
`askable` was a second gate and the word `drawable` was missing; the `nature`
field written by `0001` was not loaded at all; and `simulate_progress.py` carried
a copy of the scoring rule that would have gone on reporting the old number after
the fix.

`0004` — **three places where the code said something untrue** — 2026-08-15 —
"Progress saved" announced under `--fresh` while nothing is written; a feature
with no gloss reported nowhere, the exemption dating from before scripted turns;
and `không phải là`, whose gloss "not be + [noun]" was spoken as "not be
something". Plus `N_RAPIDFIRE`, rewired rather than deleted. No lesson changes:
all four misled the reader, not the learner.

`0003` — **regroup `SPEC.md` by item kind, and align the whole vocabulary** —
2026-08-15 — the central block of fourteen rules splits into five sections, three
of them "Teaching a…" following the three item kinds of the glossary. Table of
contents added, and the convention set: **rule numbers are stable identifiers**,
they do not renumber when a section moves. "hors-mot" → "feature" everywhere, and
the six symbols carrying `RULE` renamed — which **reverses an explicit exclusion
from 0002**, whose argument falls once the symbols and the **Change** lines move
together. No rule text rewritten. Shipped by commit `a1f3285`, whose one-line
message says almost nothing about the change — the folder was written afterwards,
and it is the folder that carries the detail.

`0002` — **name a taught fact `feature`, and its natures `discrete` / `strand`**
— 2026-08-15 — removes the collision between "rule" the behaviour and "rule" the
taught item, which had lost the thread twice in a single session. `feature` in
the sense of linguistic typology — most of the 35 are named features of the WALS
atlas. Produced `LEXIQUE.md`, 28 terms grouped by whether they come from the
field, narrow it, or were coined here. Values only: no symbol name moved, so the
**Change** lines of `SPEC.md` stayed valid.

`0001` — **write the nature and tier of every feature into the items** —
*(the values were called `A` and `B`; renamed `discrete` and `strand` by 0002)* —
2026-08-15 — 35 items annotated (28 one-off facts spread over three tiers, 7
continuous threads), zero behaviour changed. Makes it possible to bring
applications back on the one-off facts. Caught two omissions from that morning's
classification: `đang` and `sẽ`, filed in tier 2 by Meo and written like the
other 33. And corrected a mistake: the composition thread does not exist,
contrary to what had been concluded.

---

# Before the ritual

The 123 commits that came before this journal. Reconstructed from `git log`, so
faithful to the commit titles and to nothing else: what was done is accurate, the
"why" is there only where the commit said it.

To find the detail behind a line: `git show <hash>`.

## What we have already tried **and undone**

These are the most useful entries in the file: each is something that looks like
a good idea, was implemented, and was taken out. They are the ones we ask for
again without knowing it.

| the idea | tried | undone | where it landed |
| --- | --- | --- | --- |
| **Repairing approximate transcriptions** after the fact | `accec85` 2026-07-27 | `35b4caa` the same day — let the tutor judge the gap | `SPEC.md` rule 26: "A transcription is never repaired" |
| **A fallback model** when the main one fails | `2e274e3` 2026-07-21, then `62af20c` (back to llama-3.1-8b, gpt-oss-20b broke tool calls) | `31543a7` 2026-07-27 — wait for the real one | `SPEC.md` rule 30: "One model, no fallback" |
| **Dropping the tones** | removed `e46cbe2` 2026-07-27 | restored `29f7ffb` 2026-08-14, a pair said aloud when the second of the two is taught | `SPEC.md` rule 28b: "Tones ARE taught" — but rule 28: never a verdict on pronunciation |
| **Push-to-talk** | `92f0ccf` 2026-07-22 | replaced by hands-free, detector + loudness `c3018e2` 2026-08-09 | `SPEC.md` rules 23, 23b |
| **The project in English** | `6a78dd1` 2026-08-07 | `SPEC.md` rewritten in French `159ea0b` 2026-08-09 | and back to English on 2026-08-15, this time for the whole repo |
| **A `next_item` tool** handed to the model | before `216637e` | `216637e` 2026-07-28 — the sequence rides in the context | `SPEC.md` rules 8, 29 |
| **The end-of-session grader** | before `c2e15ae` | `c2e15ae` 2026-07-29 | replaced by the per-word level, rule 14 |

## The pattern that recurs most

**The prompt grows, then it has to be emptied.** Four times:

- `17c8406` 2026-07-27 — consolidation, 3742 → 2703 tokens at equal rules
- `473df0d` 2026-07-28 — "undo the prompt bloat since the consolidation"
- `77bdffc` 2026-07-28 — remove rules describing situations the code already prevents
- `4987b96` 2026-07-28 — delete the mnemonic and story rules

It is this pattern that produced the **Where: code / prompt** line at the head of
`SPEC.md`. Any proposal that adds to the prompt has to say what it removes from
it, or why the code cannot do it.

**The opening speech, four times as well:** shortened `2bc148a`, stopped from
being overwritten `202aef5`, restored `4fc4cc8` (an empty plan meant two opposite
things), rewritten around Meo's three points `b14f73c`. Landed as rule 27.

## The structural steps

| when | what changed | commits |
| --- | --- | --- |
| 2026-07-21 | first tutor brain, text only | `81f02b1` |
| 2026-07-22 | the two voices, first spoken conversation | `aa3d7c6`, `6075851`, `5802d86` |
| 2026-07-27 | the loop rebuilt on Paul Noble's actual method | `f6cb2bb` |
| 2026-07-29 | **the teaching cycle becomes a state machine in code** | `ae0b608`, `c2e15ae` |
| 2026-08-09 | `SPEC.md` is born | `0da69a0`, `159ea0b` |
| 2026-08-11 | **the code writes the mechanical turns**, with no model call | `7e7728c` (decision), `bf69808` (done) |
| 2026-08-11 | `STYLE.md` is born, the notebook | `d2d994f` |
| 2026-08-12 → 08-13 | the content fills out: person-words, questions, numbers, modals, places | `f3e7e14`, `3cf528f`, `bd53620`, `a386650` |
| 2026-08-14 → 08-15 | rules become teachable: a rule names its words, the code picks the sentence, the words are asked one at a time then assembled | `5560fd7`, `9506a3d`, `b40d766`, `bb45efc` |

## Where to find the rest

`git log --oneline` gives the 123 titles. They are written to be read: the title
says what the commit changes, not which file it touches.

Search by subject:

```bash
git log --oneline --grep=rule
```

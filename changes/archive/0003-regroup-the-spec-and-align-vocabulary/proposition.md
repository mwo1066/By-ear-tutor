# Regroup `SPEC.md` by item kind, and align the whole vocabulary on the glossary

**Status:** finished
**Opened:** 2026-08-15

## Why

Three readability defects, all found while trying to get someone outside to read
the project.

**`SPEC.md` had a section of 14 rules** — "What is taught, and in what order" —
mixing four unrelated subjects: the order of the course, the data an item
carries, teaching a word, teaching a construction. And a separate "Features"
section, when it answers exactly the same question for the third item kind. 59
rules with no table of contents.

**The vocabulary diverged between files.** `GLOSSARY.md` and the code had said
`feature` since 0002; `SPEC.md` said "hors-mot" 23 times, and six code symbols
still carried `RULE` in their names.

**And content guarantees remained unwritten** — the continuation of the audit
started in 9b/9c/11c.

## What changes in SPEC.md

**No rule text is rewritten.** These are section headings, an order of blocks, a
table of contents, and two paragraphs added to rule 10.

The central block splits into five sections, the last three following the three
item kinds of the glossary, in order:

| section | rules |
| --- | --- |
| The order of the course | 8, 9, 9b, 9c |
| What the course knows | 10, 10b |
| Teaching a word | 11, 11b, 11c |
| Teaching a construction | 12, 12b, 12c, 12d, 13 |
| Teaching a feature | 13b, 13c, 13d |

**One renumbering only:** `12e` becomes `10b`. The learner profile joins "every
item carries its own data" — one says what the course knows about items, the
other what it knows about the learner. Left where it was, it cut the construction
section in half.

**The table of contents sets the convention** that will avoid the question next
time: rule numbers are **stable identifiers**, they do not renumber when a
section moves. That is what makes it possible to reorganise without invalidating
the cross-references from `STYLE.md`, `GLOSSARY.md` and the code comments.

**Two additions to rule 10**, from the content audit:

- **the `description` fallback** — with no gloss, two places fall back to the
  authoring notes, written in Vietnamese. No taught item has an empty gloss, so
  nothing triggers it; but it is the latent form of the defect `a6f5021` fixed in
  `_lesson_note`, where fragments of Vietnamese came back out in the middle of
  English sentences.
- **the inert fields** — `type` on all 2085 items, `senses` and `frequency_rank`
  on the 1915 of the stock. None drives a decision.

## Scope

**In:** the structure and table of contents of `SPEC.md`; "hors-mot" → "feature"
in `SPEC.md` and `STYLE.md`; the six code symbols carrying `RULE`; the
`content.py` comments still describing the `rule` kind; the two paragraphs of
rule 10.

**Out:**

- **the text of the rules.** None is rewritten: this change has to read as a
  move, not as a revision.
- **`Rule 9` in a `tutor.py` comment** — that one does mean a rule of `SPEC.md`.
  It is the correct use of the word, it stays.
- **`GLOSSARY.md`**, already aligned since it is the source.

## What this reverses from 0002

`0002` had **explicitly excluded** renaming the symbols, on the grounds that the
**Change** lines of `SPEC.md` name symbols and a rename would have invalidated
them all at once.

That was right at the time. Here the two happen in the same pass: the symbols and
the lines naming them move together, so the argument falls. Six names concerned —
`MAX_RULE_PIECE_RECALLS`, `MIN_ITEMS_BETWEEN_RULES`, `_rule_is_due`,
`rules_due`, `first_rule`, `check_rule_glosses_name_their_word` — which is to say
few, something nobody knew before counting.

## Tasks

- [x] Move the `12e` block and renumber it `10b`
- [x] Split the central block into five sections
- [x] Rename "Features" to "Teaching a feature"
- [x] Write the table of contents, with the stable-numbers convention
- [x] "hors-mot" → "feature" in `SPEC.md` and `STYLE.md`
- [x] Rename the six symbols, and the **Change** lines naming them
- [x] Align the `content.py` comments
- [x] Add the `description` fallback and the inert fields to rule 10
- [x] `python smoke_test.py` after each step

## Verification

`smoke_test.py` passes after each of the four steps. Zero occurrences of
"hors-mot" across the three documents, zero symbols containing `rule` outside
prose mentions that mean a rule of `SPEC.md`. 59 rules before, 59 after.

## Result

**Finished:** 2026-08-15 — commit `a1f3285`, six files: `SPEC.md`, `STATUS.md`,
`STYLE.md`, `content.py`, `tutor.py`, `smoke_test.py`.

**This folder was written after the commit, not before.** The change was
committed as it stood, with a one-line message — "Cleanup spec, align with
content and add section" — which says neither the renumbering of `12e` to `10b`,
nor the stable-numbers convention, nor the reversal of the exclusion set by
`0002`. Since `a1f3285` was already pushed, the message was not rewritten: this
folder carries the detail, and the following commit points at it.

That is exactly the case the ritual is meant to make visible rather than prevent.
It prevents nothing — it leaves a trace when it is skipped, and the trace here is
a folder dated after its commit.

**The table of contents was not asked for** and is probably the most useful part
of the batch: 59 rules read badly without one, whatever their grouping.

**A finding from sorting the content fields.** The initial search gave
`description` read 29 times and `type` 31 times in the code, which suggested two
undocumented mechanisms. In reality almost all those occurrences are JSON schema
keys for the tool definitions, unrelated to an item's fields. Counting
occurrences does not tell you what they do — each one had to be looked at. The
real usage fits in three lines, and only one deserved writing down.

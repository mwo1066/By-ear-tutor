# Name a taught fact `feature`, and its natures `discrete` / `strand`

**Status:** finished
**Opened:** 2026-08-15

## Why

The word "rule" meant two things, and the collision cost the project's own author
time: within a single session it was necessary to stop twice to untangle "a rule
of `SPEC.md`" (a behaviour of the program) from "an item with `kind = "rule"`" (a
fact of Vietnamese being taught).

An outside reader gave the full diagnosis: several terms were invented over the
course of conversations, none is defined in one place, and nothing says which
are field vocabulary and which are specific to the application. The project is
unreadable to anyone who did not attend the conversations — which, in time,
includes its author.

**And `A` / `B` was not helping.** Two letters carry no meaning: you need the
table to know which is which, every time you read.

## What changes in SPEC.md

No rule added or removed. Three vocabulary corrections:

- rule 13, the note — the item kind is no longer called `rule`
- the "Features" section, **Name in the code** — becomes `kind = "feature"`,
  with the WALS justification and the two values of `nature`
- rules 13b and 13c, the **Change** line — "the `rule` branch" becomes "the
  `feature` branch"

**Where:** content and code, but no guarantee moves. These are values, not
mechanisms.

## The choice of name

`feature`, in the sense of **linguistic typology**, and not "grammar point":
this course files tone and politeness among them, which are not grammar. Most of
the 35 correspond to a named feature of the WALS atlas — 81A *Order of Subject,
Object and Verb*, 13A *Tone*, 55A *Numeral Classifiers*, 45A *Politeness
Distinctions in Pronouns*.

`strand` comes from curriculum design: a thread running through a whole programme
without ever finishing. `discrete` is its natural opposite.

## Scope

**In:** the **values** `kind = "rule"` → `"feature"` and `nature = "A"/"B"` →
`"discrete"/"strand"`, in the content and in the code; the corresponding
references in `SPEC.md`, `STYLE.md` and `README.md`; writing `LEXIQUE.md`.

**Out:**

- **the symbol names** — `MAX_RULE_PIECE_RECALLS`, `MIN_ITEMS_BETWEEN_RULES`,
  `_rule_is_due`, `rules_due`. Renaming them would have invalidated the
  **Change** lines of `SPEC.md` in one go, since those name symbols. To be done
  separately, if it ever proves worth it.
- **the `rule` turn** — the step naming the pattern at the end of a construction.
  It is a kind of **turn**, not a kind of **item**: once the item kind is
  renamed, there is no overlap left.

## Tasks

- [x] Rename the `kind` value in the 8 content files (35 items)
- [x] Rename `nature`: `A` → `discrete`, `B` → `strand`
- [x] Rename the 17 code sites concerning an item's `kind`
- [x] Leave untouched the 4 sites concerning a **step**'s `kind`
- [x] Fix the references in `SPEC.md` and `STYLE.md`
- [x] Write `LEXIQUE.md` in English, grouped by where the term comes from
- [x] Add the map of documents to `README.md`
- [x] `python smoke_test.py`

## Verification

`smoke_test.py` loads the whole course and plays a full session: it passes. The
distribution is unchanged after renaming — 7 / 11 / 10 in `discrete`, 7 in
`strand`, 35 in total. No item `kind` carries the value `rule` any more.

## Result

**Finished:** 2026-08-15 — 4 code files, 8 content files, 3 documents, plus
`LEXIQUE.md` created.

**The glossary is in English while `SPEC.md` and `STYLE.md` are in French.**
Accepted: those two are read by one person, the glossary is what you hand to
someone outside. `README.md` says so in one line. *(Both went to English later
the same day, when the whole repo did.)*

**The terms are grouped by origin**, which is the main contribution and was not
part of the original request: *standard* (13 field terms used in the field's
sense), *borrowed and narrowed* (7 standard words restricted here), and *coined
here* (8 with no equivalent). A reader who knows language teaching immediately
knows which definitions they can skip.

**A vocabulary collision found while writing:** `tier` is also the name of a
known scheme in vocabulary instruction (Beck), which ranks words by **academic**
utility. Here the scheme ranks by **conversational** utility. Same word,
different scheme — written into the glossary rather than renamed, because `tier`
is the word Meo uses.

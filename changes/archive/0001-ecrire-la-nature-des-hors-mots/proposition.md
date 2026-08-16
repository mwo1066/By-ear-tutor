# Write the nature and tier of every feature into the items

**Status:** finished
**Opened:** 2026-08-15

## Why
The code treats all 35 features identically — a `kind = "rule"`, a position,
taught, done. But they are of two natures: **one-off facts** taught once, and
**continuous threads** attached to all the material (tone to every word, address
to every sentence with a person in it).

The distinction had been established and measured on the morning of 15 August,
then lost: it existed only in a conversation transcript. Recovered by digging,
and it will only survive if it is in the files.

**The measurement that motivates it:** 33 features taught across the whole
course, final level min 0 / max 0, never asked again 33/33 — against an average
of 4.5 for words. The code cannot fix that while it cannot tell a fact from a
thread.

## What changes in SPEC.md
**Nothing.** No behaviour moves: the fields are written, nobody reads them yet.
The rule will come with the change that uses them.

## Scope
**In:** `nature` (`A`/`B`) on the 35 features, `tier` (1/2/3) on the 28 of
nature A.
**Out:** any reading of the field by the code. Any removal of the category B
items that duplicate a thread already running — Meo has not looked at category B
yet, it stays as it is.

## Tasks
- [x] Write `nature` and `tier` into the eight content files
- [x] Check that all the TOML still parses
- [x] Check the distribution: 7 / 11 / 10 in A, 7 in B
- [x] `python smoke_test.py`

## Verification
`smoke_test.py` loads the whole course and plays a session: it passes. The
loader picks its fields one by one and ignores unknown ones, so the two new ones
are inert by construction.

## Result
**Finished:** 2026-08-15 — 63 lines added, 0 removed, 8 files.

Done without going through the proposal step: this is transcribing a decision,
not making one. The attachment table already existed in `STYLE.md`, there was
nothing to settle.

**Two items attached along the way.** `đang` and `sẽ` were in no category —
created on 14 August by "Split the three tense markers into three rules", so
before the classification, which had forgotten them. Filed as A tier 2 by Meo,
alongside `đã`, `rồi` and `chưa`. Tier 2 holds 11 rules, not 9.

**One error corrected before writing.** The morning session gave the composition
thread ("gluing two known words") as existing, via the `hook`. Measured: `pieces`
is 0 across 2042 atoms and a single atom carries a `hook`. Two category B items
therefore have no thread — the numbers (nothing anywhere) and composition
(blocked by content that has to be written, not by code).

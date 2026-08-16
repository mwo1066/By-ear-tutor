# Three places where the code said something untrue

**Status:** finished
**Opened:** 2026-08-15

## Why

Three unrelated defects, gathered because they have the same shape: **a sentence
of the program that no longer matches what it does.** None is a behaviour bug;
all three mislead whoever reads.

## What changes in SPEC.md

A single line, rule 17's.

## 1. "Progress saved" when nothing is saved

The end-of-session message read the constant `STATE_PATH` instead of asking the
store what it had done. Under `--fresh`, `ProgressStore` has no path and returns
immediately from `save()` — but the session announced a save anyway.

Rule 32 says "`--fresh` writes nothing at all": the behaviour was right, it was
the message that lied. And it is **the one line of a session the learner has no
way to check** — a file they will not open.

Fixed by asking `store.path`.

## 2. A feature with no gloss was reported nowhere

`check_roster` exempted features from the gloss check. That was **true when it
was written**, on 9 August: a feature's turn was composed by the model, which
could work from `description`. On 11 August the code began building questions
from the gloss and nothing else, and the exemption outlived the change that made
it false.

**`_ask_for`'s docstring already promised the missing half:** *"a missing gloss
falls back to the item's own notes instead AND IS REPORTED AT STARTUP"*. The
fallback worked; the report did not.

So it is not the fallback that was removed — it is deliberate, and its
alternative was worse (using the Vietnamese name, that is, a question that gives
its own answer). It is the report that was restored.

**Reported separately, and one by one.** A *word* with no gloss is held out of
lessons and counted in one line — there are 1,915 of them, listing them would
drown everything else. A *feature* with no gloss **is still taught**, with a
degraded question: that is not the same problem, so it is named item by item.

Measured before writing: 0 features affected today, so zero false positives and
zero lessons changed. It is a guard for the next feature written, not a fix to
the current course.

**Left in place:** the second exemption, on the "the name appears in its own
gloss" check. For a feature, putting the Vietnamese word in the gloss is
**deliberate** — that is commit `84c2104`. Removing that exemption would conflict
with an intentional practice.

## 3. A construction's gloss stated grammar

`không phải là + [danh từ]` carried `gloss = "not be + [noun]"`, spoken as **"not
be something"**. Rule 10 says a gloss is said as written and is never a
grammatical description; this one was both at once. `STATUS.md` had been
flagging it for days.

- gloss: `"not be + [noun]"` → `"I am not a ___"`, on the model of
  `"My name is ___"` and `"I am ___ years old"` already in place
- literal: `"not be + [noun]"` → `"not right is [noun]"`, which is the real
  word-for-word of `không phải là` (`không` not, `phải` right, `là` is) instead
  of a label

**A judgement taken, easy to undo.** This is course material: if the wording does
not suit, it changes in one line of TOML.

**Not touched:** `muốn + [động từ]` → `"want ___"`, which `STATUS.md` files in
the same batch. Spoken as "want something", it is not a grammatical label — it is
thin English. Inventing a better one without a measurement would be a preference,
not a correction.

## And a fourth, found while writing

`N_RAPIDFIRE = 3` documented the average measured on the reference course, and
served no purpose any more: `rapidfire_count` wrote `3` literally three lines
below it, and the constant survived only as the default of a parameter borrowed
by the smoke test alone. Rule 17 had had to add a warning — "**not**
`N_RAPIDFIRE`" — to stop anyone editing it thinking it changed something.

**Rewired rather than deleted.** The single word's base *is* the measured
average; the other two follow from what the item has just made the learner say.
The constant now says what it claims, and rule 17's warning went with its reason
for existing.

Distribution verified unchanged: 2–4 for a word, 1–2 for a construction, 1–3 for
a feature.

## Scope

**In:** `tutor.py` (the end message, `rapidfire_count`), `content.py` (the gloss
check), one item of `02_xung_ho.toml`, the **Change** line of rule 17.

**Out:** the `description` fallback itself; the second exemption of
`check_roster`; the gloss of `muốn + [động từ]`.

## Tasks

- [x] Read `store.path` instead of `STATE_PATH` for the end message
- [x] Report a feature with no gloss, with its own message
- [x] Check zero false positives on the real roster, and that the guard fires
- [x] Rewrite the gloss and literal of `không phải là + [danh từ]`
- [x] Rewire `N_RAPIDFIRE` onto the single word's base
- [x] Fix the **Change** line of rule 17
- [x] `python smoke_test.py`

## Verification

`smoke_test.py` passes after each step. Both branches of the end message tested
separately. The gloss guard tested on an injected feature with no gloss, and on
the real roster: 1,915 problems, all from the mute stock, zero features.

## Result

**Finished:** 2026-08-15.

**All four defects have the same shape**, and that is only visible with them side
by side: a message reading a constant instead of the state, an exemption true
when written and false two days later, a gloss that describes instead of saying,
a constant documenting a value it no longer drives. None breaks a lesson. All
four mislead whoever reads the code or the content to decide what to do next —
which is to say, us, all day long.

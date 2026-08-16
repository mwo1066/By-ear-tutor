# Validate the tier ranking, and remove subject–verb–object from the course

**Status:** finished
**Opened:** 2026-08-15

## Why

The ranking of `discrete` features into three tiers of usefulness had existed
since the morning of 15 August and **had never been validated** — it was an
assistant's proposal, never corrected. Until it is validated, reordering the
course by it is blocked.

## What changes in SPEC.md

Nothing. The `tier` field is read by no code yet: it is waiting for the reorder,
which is a different change.

## Three decisions by Meo

**1. Subject–verb–object leaves the course.** The item is deleted, not demoted.

Its own entry presented it as the beginner's safety net — *"đây là chỗ dựa an
toàn cho người mới: khi chưa chắc, cứ xếp như tiếng Anh thì thường đúng"*, the
safe footing for a beginner. That is precisely the argument against it: **a
French speaker already places subject, verb, object without thinking.** The rule
occupied a lesson slot to teach a reflex they arrived with, and it headed tier 1.

Checked before deletion: no item cites it as a piece or as an `after`. The course
goes from 35 features to 34.

**2. `đã` moves up to tier 1.** The past is part of what you cannot speak
without: it is what puts variety into sentences, and learning it early opens
everything that follows.

**3. "Verbs never change" moves up with it.** It was in tier 3, classed as
comfort, while it **raises the question** `đã` answers — and it explains itself in
one sentence. Meo's reasoning: state the simple rule, the learner has it
immediately, then hand them the past.

The sequence obtained, measured on the real sequencing:

```
25  đã                     the word
26  động từ không chia     "verbs never change"
27  đã: việc đã xong       "here is how you say the past"
```

Both rules are attached to the word `đã`, so they arrive together. **Their order
between them is not guaranteed**: it comes from file order, and
`pick_next_index` takes the first attached one it finds. It happens to be right.
If a content reshuffle inverted it, the learner would get the answer before the
question, and nothing would flag it.

## Scope

**In:** deleting the SVO item, two `tier` fields, the tiers section of
`STYLE.md`.

**Out:**

- **`đang` and `sẽ`**, which stay in tier 2. They occupy the same slot in the
  sentence as `đã` and their glosses say so, so moving them up together was
  defensible. Meo's decision: later.
- **reordering the course by tier**, which is the change this validation unblocks
  and does not itself perform.

## Tasks

- [x] Check that nothing references the SVO rule
- [x] Delete the item from the content
- [x] `đã` and "verbs never change" into tier 1
- [x] Check the real sequence on the simulation
- [x] Bring `STYLE.md` in line with the items, and record the validation
- [x] `python smoke_test.py`

## Result

**Finished:** 2026-08-15. Tiers: **8 / 10 / 9**, 27 `discrete` features out of
34.

**What it unblocks:** the ranking is validated now, so reordering the course by it
becomes possible. That is where it will mean something — today the `tier` field
drives nothing, and the course order is still decided by file order, spacing and
`after`.

**A confusion cleared on the way, and it was worth it.** Meo thought "tier 1"
meant "taught first". That is what it ought to mean, and it does not yet: the
ranking exists and drives nothing. The misunderstanding was the right instinct
about inert data.

**A memory that did not check out.** Meo remembered linking word order with the
past, "together". Digging through the transcripts does not find that link — it
finds the one between "verbs never change" and `đã`, phrased that same morning:
*"a relief rule creates a question; the question must be answered straight
after"*. The confusion probably comes from the verb rule **being about verbs**,
so it looks like a word-order rule. The intended link existed, with a different
partner — and it is now in the ranking as much as in the sequence.

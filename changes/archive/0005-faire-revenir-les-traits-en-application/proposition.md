# Bring a feature back as an application, as often as a word

**Status:** finished
**Opened:** 2026-08-15

## Why

Measured over a whole course played to the end:

```
33 features taught
final level ............. min 0, max 0
never asked again ....... 33 / 33
```

Against an average of **4.5** for words. Zero does not mean "badly learned": it
means **never seen again, not once**.

The cause fits in one line, in `_recall_targets`:

```python
exclude |= {i.name for i in seen_items if i.kind == "feature"}
```

**That line is right.** You cannot ask "what was the word for *no plural*?".
Nobody recites a rule. What is wrong is the conclusion drawn from it — *"so there
is nothing to do"*. You cannot **re-ask** a feature; you can **re-apply** it.

Today a feature's total exposure across the life of the course is: one statement,
one application. Then the plan moves to the next item and it appears in no lesson
again. That is **a fifth of what is taught** — 35 items out of 170 — and a
learner reported it in these words: *"I understood nothing about the rule, and it
is not even used"*.

**What it does not cost.** An application turn is not taken from vocabulary: 13c
pins the sentence sharing the most pieces with the feature, and the instruction
restricts production to words already taught. The sentence produced is therefore
made of words due for revision. One turn, two benefits.

## What changes in SPEC.md

**New rule — a feature comes back, as an application.**
**Where:** code. A `discrete` feature enters the recall draw on the same footing
as a word, weighted by the same level. When the draw lands on it, the step
emitted is an **application** (13c) and not a bare recall, because there is
nothing to recite.

**Rule 17 — modified.** It describes what the closing recalls exclude. It will
have to say that `discrete` features now enter, and that `strand`s stay
excluded.

**And in passing, an unwritten guarantee.** The current exclusion of features
from the draw is documented nowhere in `SPEC.md` — the audit had not caught it.
It disappears with this change, but it is worth noting that it existed with no
rule.

## Scope

**In:**

- `discrete` features enter the draw of `_recall_targets`
- when a drawn target is a feature, `build_plan` emits an application instead of
  a `rapidfire`
- the exposure is recorded on that step, so the level rises

**Out:**

- **the `strand`s.** They fire from the material — a word has a tone twin, a
  sentence contains a person — and have no business in a draw. They stay
  excluded.
- **the level of the words used inside the sentence.** The application exercises
  them, but the code records nothing for them: `record_recall` is only called
  where it asked for a precise word and can compare the answer. Widening the
  level to "the word was somewhere in a sentence" would make it mean two things
  at once. Words keep their own schedule; the application is an uncounted bonus.
- **any judgement by the model.** See below.

## The decision that structures the rest

**The level has to rise, and it is not optional.** The draw is weighted by level,
and the curve is steep:

| level | drawn 1 time in… |
| --- | --- |
| 0 | 1 |
| 2 | 5 |
| 4 | 11 |
| 8 | 27 |

An item at 0 is **thirteen times** more likely than a consolidated word at 4.5.
If the 28 features enter the draw and stay at 0 — which they do today, nothing
raising their level — they will not be "repeated as often as words": **they will
crush everything else, permanently.**

**So: count the exposure, without judging.** The level rises on each application,
whether it succeeded or not.

The alternative would be to have the model judge, since an application asks for a
whole sentence and offers no target to compare. It is set aside: it would hand
back to the model a decision this project spent weeks bringing into the code, for
a gain in fidelity no measurement is asking for.

## To settle before implementing

**Should it be capped at one application per item?** The closing recalls are
drawn in batches of 1 to 4. If two or three land on features, closing a word
becomes two or three sentence productions in a row — long, and of an entirely
different rhythm from a run of bare recalls.

Two possible answers: cap at one application per item, or let the draw decide and
see what it gives in simulation. **Settled: capped at one**, with the option of
raising the cap after measuring — which is the sense of rule 17, which already
modulates the number according to what the item has just made the learner say.

## Tasks

- [x] Remove the `discrete` exclusion in `_recall_targets`, keep the `strand` one
- [x] Emit an application when the drawn target is a feature
- [x] Record the exposure on that step
- [x] Cap at one application per item, if that is the decision taken
- [x] Write the new rule in `SPEC.md`, and modify 17
- [x] `python smoke_test.py`
- [x] `python simulate_progress.py` before / after, and compare the distributions

## Verification

`simulate_progress.py` replays the real sequencing — `pick_next_index` chooses,
`build_plan` builds, `record_recall` scores — so it produces a state the tutor
could have arrived at. It is the tool that measured the 33/33; it is the one that
has to show the number has moved.

**What the verification must show:**

1. the final level of features is no longer 0, and approaches that of words —
   that is the literal objective: "worked as often as a simple word"
2. the draw distribution is not dominated by features — check that a consolidated
   word has not stopped being drawn
3. `smoke_test.py` passes, and a lesson does not end on three sentence
   productions in a row

## Result

**Finished:** 2026-08-15.

| | features | words |
| --- | --- | --- |
| before | all at **1** — the only exposure is the introduction | median 5 |
| after | median **4**, from 0 to 8 | median 4 |

**The objective is met in the literal sense:** a feature is now worked as much as
a word. The price is visible and accepted — words go from 5 to 4, since they now
share the slots.

Cap verified over 400 closes: **never two applications**, never two in a row. 58%
of closes carry one.

## What the implementation surfaced

**A third gate the proposal had not seen.** The exclusion of features was not
alone: `askable()` rejected them too, and its docstring already said why —
*"teachable and askable are different: such an item can still be TAUGHT, it just
cannot be the bare question of a recall slot"*. That is right. A third word was
missing: **`drawable`**, "can it fill a slot, in one form or another". All three
now sit side by side in `drawable`'s docstring, because their confusion is what
cost the 33/33.

**The `nature` field was not loaded.** `0001` had written it into all 35 items,
but `content.py`'s loader picks its fields one by one and skipped that one. The
code therefore could not tell `discrete` from `strand` — the data was there,
invisible. Added to the dataclass and to the loading.

**The scoring rule was duplicated**, and the copy drifted the same day.
`simulate_progress.py` carried its own list `("recall_piece", "rapidfire",
"settle")` under a comment saying "exactly as the live loop does". It is the tool
that produced the 33/33 measurement: left as it was, it would have gone on
reporting "features at 0" **after** the fix. Rewired onto `RECALL_KINDS`, plus a
branch for applications.

**An extraction made necessary.** The choice of an application's material — the
pinned construction, otherwise the feature's own words, otherwise the list of
known sentences — lived in the introduction branch. Both turns need it, and it is
the same decision: extracted into `_apply_material`. The two turns word it
differently (one can say "those words", which the learner has just said back; the
other has to name its own material) but choose alike.

## And the copy was not alone

Afterwards, a search for duplicated invariants found **three more**, **two of them
in the file we had just fixed**: `simulate_progress.py` wrote the list in three
places, `smoke_test.py` in a fourth. I had fixed the instance I tripped over, not
the class.

All four now refer to `SCORING_KINDS`, defined once in `tutor.py` with the reason
written beside it. The only literal occurrence left is the definition.

**That is the most useful lesson of the batch**: finding one piece of stale prose
says nothing about how many twins it has. What finds them is not attention, it is
a search — and a search is mechanical, therefore repeatable.

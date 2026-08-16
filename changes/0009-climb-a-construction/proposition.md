# Climb a construction, instead of asking for it whole

**Status:** applied, not archived — one task left
**Opened:** 2026-08-15

## Why

The principle is already written in the code, quoted from Meo during a test:

> A rule is put to work by CLIMBING one sentence, not by being asked for whole
> sentences repeatedly. *"He always starts calm — how do you say don't want,
> then I don't want, then I don't want to eat."*

It is applied to **one branch out of three**:

| | climbs? |
| --- | --- |
| address feature | yes — three rungs |
| other feature | no — a single application |
| **construction** | **no** — the whole literal order, then the whole sentence in one go |

A construction today says: *"here is the word-for-word order, now say the
sentence"*. For `tôi tên là + [tên riêng]` that is four words asked in one block
of someone who has just learned the three pieces separately.

## What changes in SPEC.md

Rule 12 describes a construction's chain — "then the literal order, then the
answer". It will have to say that the sentence is **climbed**: two or three
rungs, each adding one element, the last being the whole sentence.

## What the code cannot know, and which decides the shape

**Which rungs of a sentence are valid is Vietnamese knowledge.** The `pieces`
field gives the words, not the stages: `tôi`, `tên`, `là` does not say that
`tôi tên` is not a sentence.

So the rungs are **model turns**, and the code supplies the boundary — exactly
the doctrine already written for the `vary` step:

> Which element is swappable is the one thing the code cannot work out […] That
> knowledge is Vietnamese, which is exactly what the model has and a table does
> not. So this stays a model turn, and the instruction supplies the boundary.

The code supplies: the target sentence, its pieces, the list of taught words, and
the rule "one more element per rung, stay on the same sentence".

## Scope

**In:**

- the `scaffold` step becomes two or three rungs instead of one turn
- the literal order is given on the **last** rung, the whole sentence — that is
  where the order matters
- the `_known_words_note` guard is added, which the scaffold does not have today
  while `vary` and `apply` do

**Out:**

- **the features.** Their branch already has its shape, and touching it would
  double the scope.
- **the number of variations and the naming of the pattern**, which do not move.
- **the lying instruction when `literal` is empty** — it disappears by itself,
  since the literal order moves to the last rung, where it is conditional.

## Two decisions taken before implementing

**The total number of turns does not move.** Rungs add turns, which is the
opposite direction from "making a sentence cheap". They are therefore taken out
of the variation budget:

```
today         scaffold(1) + answer(1) + variations(2)  =  4 turns produced
with rungs    rungs(2-3)  + answer(1) + variations(1)  =  4 turns produced
```

This is consistent with the method: for Noble, **climbing IS the variation**.
"I want" → "I want to eat" → "I don't want to eat" is not build-then-vary, it is
one gesture.

**The known-words guard stays an instruction, and that is accepted.** It has two
regimes: below twelve taught words it **lists** the vocabulary, beyond that it
only says "introduce nothing new". That is **prompt**, not code — and it is
precisely why the `ở` rule, which arrives at item 48, asked for "at home" despite
the instruction.

A ladder asks more of the model than a variation, so more chances to drift under
a weak guard. Meo's decision: **accept it and listen.** The net — an after-the-
fact check reporting a turn that speaks a word never taught, on the model of
`_leaked_target` — deserves its own folder and must not delay what we want to
hear.

## The risk, and it is real

A rung invented by the model can ask for a word never taught — which is exactly
what happened to the `ở` rule ("I am at home, at school, at the market", none of
the three taught). The known-words guard is the mitigation, and it has already
proved itself on `vary` and `apply`.

It can also produce a stage that is not a sentence (`tôi tên`). The instruction
has to say that **every rung must be something a person can say**, not a
fragment.

## What no test can verify

`smoke_test.py` will see that the plan has the right number of steps and that
nothing leaks. It cannot say whether the rungs are well chosen — that is
Vietnamese and pedagogical judgement. **This change has to be heard in session
before it is kept.**

## Tasks

- [x] Replace the single `scaffold` step with rungs
- [x] Give the literal order on the last rung only
- [x] Add `_known_words_note` to the instruction
- [x] Require every rung to be something a person can say, not a fragment
- [x] Modify rule 12 of `SPEC.md`
- [x] `python smoke_test.py`
- [x] **Hear a session** on a construction — done 15 August, it found a defect
- [ ] **Hear it again** after the rung-1 fix, before archiving

## Verification

Count a construction's turns before and after, and read the instructions produced
for three constructions of different sizes. Then a real session: do the rungs
climb, or does the model ask for the same sentence three times?

## What the listening found

Real session on `tôi tên là + [tên riêng]`, plan `recall_piece ×3 → scaffold ×2 →
answer → vary → rule → rapidfire`. The ladder did run.

**Rung 2 works:** *"In Vietnamese the order is: I name is something. Now — My
name is something?"*, and the learner answered `Tôi tên là`.

**Rung 1 was broken:** it asked *"What's the Vietnamese word for 'I'?"* — that
is, `tôi`, **three turns after the recall that had just asked for it**. The
instruction said "one element fewer than the rung after this one", and the model
went all the way down to a single word.

Fixed: the floor is **two pieces put together**. A single word repeats the turn
before instead of building — each piece has just been recalled on its own right
before.

**What the listening could not judge**, because the session drifted afterwards:
the learner spoke freely, the step waited (4c-bis), and the model took over as
far as teaching `sinh viên`, which is outside the course. The plan never resumed.
That is a separate defect, outside this folder.

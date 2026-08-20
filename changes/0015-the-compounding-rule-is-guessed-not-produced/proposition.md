# The compounding rule is guessed, never produced

**Status:** proposed
**Opened:** 2026-08-17

## Why

The strand `ghép hai từ đã biết thành từ mới` teaches that Vietnamese makes new
words by putting two known words side by side. Its `apply` step, built today,
says:

```
Now put those words together. Build the sentence out of these words, which are
what this rule is about: "đi", "học", "ăn", "uống". … Ask for ONE sentence that
uses the rule.
```

**A sentence cannot use a word-formation rule.** And the item's own authoring
note says the exercise is not just mismatched but forbidden:

> *NHƯNG chỉ dùng để HIỂU, không dùng để tự chế từ* — but only to UNDERSTAND,
> never to invent words yourself.

The note gives the reason: `cho nên` is `cho` (to give) + `nên` (should) and
means *therefore*; `bà con` is `bà` (grandmother) + `con` (child) and means
*relatives*. **Neither is guessable from its halves.** A learner trained to build
compounds will produce words that do not exist, with the confidence of someone
following a rule.

So the one exercise this rule gets asks for the opposite of what it teaches.

## What changes in SPEC.md

- **rule 13e — new**: *a rule that describes comprehension is exercised by
  comprehension.* Where a feature's application cannot be a production — the
  learner would be inventing rather than using — the turn gives the material and
  asks what it **means**, and the answer is in the learner's own language.
  **Where:** code — `_apply_material`, which today always asks for a sentence.

The turn, validated by Meo:

```
tutor   So — to go?
you     đi
tutor   That's it. And again — what was to study?
you     học
tutor   Vietnamese sticks those two together into one word.
        Any idea what it means?
you     going to school?
tutor   Exactly — đi học.
```

The learner produces **a hypothesis about meaning**, never the Vietnamese. Saying
*"no idea"* is a valid answer and the tutor gives it — rule 4b-bis's shape.

**The wording matters and is part of the rule:** *"**those two**, Vietnamese
sticks together"*, never *"two words can be joined"*. The first opens one word;
the second licenses invention, which is what the note forbids.

## Scope

**In:** the application of this one rule, and the worked examples it needs.

**Out:**

- **Making `đi học` and `ăn uống` items of the course.** They do not need to be:
  the tutor only has to know the compound and its meaning, and `steps` — a field
  that already exists and is already used this way by the address rule — carries
  it. Keeping the compound as vocabulary is a separate content decision.
- **Hooks at scale.** `fill_item_metadata.py` already writes them, and
  `_needs_fill` never revisiting the 203 items that have a `kind` and a `gloss`
  is a separate defect, recorded and not opened.
- **The frequency shelf.** Untouched here; this change adds no word.

## Tasks

- [ ] give the strand `steps` with worked decompositions, taken from its own
      authoring note: `đi + học`, `ăn + uống`
- [ ] `_apply_material`: when the rule carries `steps` of that shape, the
      application asks for the MEANING of one compound instead of a sentence
- [ ] the instruction must name the two words and say the language joins **those
      two**, and must not invite the learner to build others
- [ ] `SPEC.md` rule 13e

## Verification

1. **Offline**: `python smoke_test.py` at exit 0, and the plan for the strand
   printed — the `apply` instruction must ask for a meaning and must not contain
   the word "sentence".
2. **No other feature moves.** Only this rule carries `steps` of this shape;
   every other feature's application must be identical before and after,
   checkable across all 34.
3. `python simulate_session.py 8 --from="ghep hai tu"`, read: the learner is
   asked what a compound means and answers in English, never in Vietnamese.

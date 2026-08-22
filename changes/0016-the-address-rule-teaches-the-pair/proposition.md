# The address rule teaches the pair, and can see its own table

**Status:** proposed
**Opened:** 2026-08-17

## Why

**The fact the whole system rests on is never said.** In Vietnamese, choosing
what to call someone chooses what you call yourself. `anh` obliges `em`; they are
one decision, not two. Meo's source states it as the first thing on the page,
with a two-column table — *Anh → em*, *Chị → em*, *Cô → cháu*, *Bác → cháu*.

The course teaches `anh` and `em` as two separate words and never says they move
together. A learner can know both and be unable to speak, because nothing told
them that saying `anh` commits them to `em`.

**Two things stop it being said, and the good version is already written.**

**1. The rule cannot see its own table.** `address_situations(items)` returns the
`steps` of whichever taught feature declares them — but `build_plan` is given
`known`, the items taught **before** this one, and the address rule is the one
being taught. Measured:

```
address_situations(known INCLUDING the rule) -> 4 rows
address_situations(known BEFORE the rule)    -> []
```

So `rows` is empty, `about_address and rows` is false, and the rule falls through
to the generic application — which produces:

> *"how would you say **address for an older male and address for an older
> female**, put together the way the rule says?"*

Asking the learner to say *"anh chị"*. The rule teaches how to **choose between**
them and the exercise asks them to **glue** them together.

**Every later address rule works.** Slots 79 and 94 get three proper situation
exercises each, because by then slot 9 is behind them and its table is visible.
**Only the rule that owns the table is denied it.**

**2. The generic table has one column.** `learner.py` already writes the two-column
version, and it is unreachable for a second reason — it needs a completed learner
profile, and `learner.json` does not exist:

```python
def address_rows(self):
    if not self.complete: return []
    return ["a man older than you → he is anh, you are em",
            "a woman older than you → she is chị, you are em", …]
```

Its neighbour `pair_with_minh()` already carries Meo's restaurant rule, written
before today: *"treating someone as slightly older than they are is harmless, the
reverse is the mistake."* The fallback `steps` on the item say only
`đàn ông hơn tuổi mình → anh` — who to call what, never who you become.

## What changes in SPEC.md

- **rule 10c-bis — new**: *a rule is given its own declared material.* The items a
  rule's application draws on include the rule itself, not only what came before
  it. Nothing else in the course declares material about itself, so this is one
  line and one rule.
  **Where:** code — `build_plan`, the `address_situations` call

The address table itself is **content**, not a rule: it moves to the two-column
form in `01_ten_va_chao_hoi.toml`.

## Scope

**In:** the address rule seeing its own table, and that table naming both halves
of the pair.

**Out:**

- **Rules 3 to 9 of the validated sequence** — the nuance rule, the generation
  above, paternal/maternal, parents, the ones to recognise and never say, and
  "we". Each is its own change and several need words off the shelf.
- **The learner profile.** The rule already asks who the learner is; whether that
  answer is captured and stored is a different thread.
- **`nói VỀ ai đó: xưng hô + ấy`, `gọi ai đó: xưng hô + ơi`, `ạ`.** Discrete
  features, tier 1 and 2, already working. Meo: do not touch.

## Tasks

- [ ] `build_plan`: pass the item itself alongside `known` when looking for the
      address table, so a rule can declare its own material
- [ ] rewrite the item's `steps` as pairs, in the shape `learner.py` already
      produces — *"a man older than you → he is anh, you are em"* — so the
      generic fallback teaches the same thing as the personalised one
- [ ] check the situation exercises now fire on the rule itself
- [ ] check slots 79 and 94 are unchanged: they already worked, and this must not
      move them
- [ ] `SPEC.md` rule 10c-bis

## Verification

1. `python smoke_test.py` at exit 0.
2. **The plan for `cách chọn từ xưng hô`**, printed: three `apply` steps whose
   instruction contains SITUATION, where today there is one generic apply.
3. **Nothing else moves.** Only one item in the course declares address steps, so
   every other feature's plan must be identical — checkable offline across all 41.
4. `python simulate_session.py 10 --from="cach chon"`, read: the learner is asked
   who the person is **and** what they call themselves.

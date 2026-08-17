# Make the numbers a thread that reaches money, in slices

**Status:** proposed
**Opened:** 2026-08-17

## Why

Four observations, all checked in the content.

**1. One strand is asked to say four things in one breath.** `đếm từ 11 đến 99`
builds a plan of exactly two turns — a `rule` and an `apply`. The rule turn says
its gloss:

> *past ten you stack two words you already know — but the word for ten changes
> shape on the way*

Its own authoring note holds **four facts**: 11-19 is `mười` + digit; from 20 the
order reverses to digit + `mươi` + digit; the trap is `mười` becoming `mươi` when
a number precedes it; and the irregulars. The gloss says *that* something
changes and never *what*. Nobody produces `hai mươi ba` from it — and the next
turn asks them to.

**2. `trăm` and `nghìn` are taught as bare words with no rule at all.** The
learner is given "hundred" and "thousand" and nothing that combines them. The
thread stops at 99.

**3. `đồng` is not teachable.** It exists only in `90_frequency_stock.toml`
without a gloss, so it is held out of every lesson. Meanwhile `bao nhiêu tiền?`
— *how much does it cost?* — **is** taught, at position 101. A question is
taught and its answer cannot be said.

**4. `triệu` (million) is not in the course at all.** Vietnamese notes run to
500,000 and prices reach millions, so the thread cannot stop below it.

### What is NOT a problem, verified

Both worries Meo raised turned out to be already handled, and the measurements
should stay recorded so they are not re-litigated:

- **The digits are already spaced.** Replaying `pick_next_index` over the real
  course: 16 numerals spread over **44 slots**, longest consecutive run **3** —
  exactly `MAX_SAME_CATEGORY_RUN`. Its own comment was written after measuring
  "eleven numerals in eleven consecutive slots".
- **No number is enumerated.** The course holds the digits and the irregulars
  and nothing else — no 11, no 12, no 21. The rule is the button and the digits
  are the material, which is the intended model already in force.

### The Vietnamese, from a native speaker

Given to Meo on 2026-08-17 and the reason this can be written at all:

```
1,000 đ      = một nghìn đồng
10,000 đ     = mười nghìn đồng
100,000 đ    = một trăm nghìn đồng
1,000,000 đ  = một triệu đồng

spoken:  100k = một trăm nghìn      200k = hai trăm nghìn
         500k = năm trăm nghìn      1 million = một triệu
```

*"I just say the number and then don't"* — **`đồng` is dropped in speech, `nghìn`
is not.** This corrects a guess made while investigating, that the thousand was
dropped too ("hai mươi lăm" for 25,000). It is not.

## What changes in SPEC.md

**Nothing.** And that is the point of the shape below.

The instinct was that a strand needs several `rule` turns and the code gives it
one — which would have been a code change touching all seven strands. It is not
needed: **each slice becomes its own item**, and the existing machinery already
gives every item its own rule turn and already spaces them by category. No rule
moves, no symbol moves.

**Where:** content — `content/vietnamese/07_so_dem.toml`.

## Scope

**In:** the numbers and money thread as content — renaming the over-narrow
strand, splitting its four facts into slices, and the two missing words.

**Out:**

- **A strand delivered in installments as a code feature.** Not needed here, and
  if it is ever wanted for tone or the address system it is its own change.
- **The other six strands.** Being reviewed one at a time; this covers the one.
- **`sáu bảy tám chín` sitting in `04_hoi_va_thich.toml`** between *yesterday /
  today / tomorrow* and *dạ / xin / sao*, with nothing around them needing a
  number. It looks accidental, but the sequencer already spaces them, so moving
  them changes the file and not the lesson. Separate, and cosmetic.
- **`hai` taught 30 slots before `một`.** The sequencer spaces correctly and does
  not preserve numeric order — you learn "two" at slot 61 and "one" at slot 90.
  Odd, harmless, and a different question from this one.

## Tasks

- [ ] rename `đếm từ 11 đến 99` → **`ghép số: chữ số + đơn vị`** (*assembling a
      number: digit + unit*). Decided 2026-08-17. It names the **mechanism** and
      not a range, so it does not go stale when billions are added, and it follows
      the pattern the other features use — `sở hữu: danh từ + của + người`,
      `so sánh: tính từ + hơn`. Nothing references the old name but its own
      definition, so this costs one line.
- [ ] **the strand survives as the umbrella**, and the slices become `discrete`
      features under it. Decided 2026-08-17. What never finishes is one idea —
      *a number is built by stacking words you already know* — and it holds at 11,
      at 100, at 1000 and at a million: `năm trăm nghìn` is three words the learner
      already has. Each slice, by contrast, is a fact that **finishes**, which is
      the glossary's definition of a discrete.
- [ ] split its four facts into slices, one item each, each with a gloss short
      enough to be said in one turn: 11-19; 20-99 with the reversal; `mười` →
      `mươi`
- [ ] give `đồng` a gloss so it becomes teachable, and one slice for the fact
      that it is **dropped** in speech — a rule of omission, not a word to recite
- [ ] add `nghìn`'s combining rule: digit + `nghìn`. **After this slice alone the
      learner can buy a coffee** — `hai mươi lăm nghìn`
- [ ] add the `trăm nghìn` slice — the banknotes, 100k / 200k / 500k
- [ ] add `triệu` as an atom, and its slice
- [ ] the banknote slices come **after** the digits, per Meo: the material before
      the rule that combines it, which is the ordering the course already follows
- [ ] check `bao nhiêu tiền?` now has an answerable reply, and consider a
      construction for it

**Every Vietnamese string above needs Meo's validation.** The native speaker's
list covers the money forms; the slice names and the 11-99 wording do not come
from her.

## Verification

`smoke_test.py` covers this better than usual, because it is content:
`check_pieces_exist`, `check_feature_glosses_name_their_word` and
`check_glosses_cite_only_taught_words` all run on the roster, and
`check_every_plan_builds` will fail if a new item cannot produce a plan.

1. **Offline**: `python smoke_test.py` at exit 0, and `check_roster` reporting no
   new problem.
2. **The measurement that says it worked**: replay `pick_next_index` and confirm
   the numerals still never run more than three in a row **after** adding five or
   six items to the same category. This is the one thing that could regress —
   more numerals in one file is exactly what `MAX_SAME_CATEGORY_RUN` was written
   for.
3. **One real session** reaching the money slices, listened to: each slice is one
   turn, sayable, and the learner can answer `bao nhiêu tiền?`.

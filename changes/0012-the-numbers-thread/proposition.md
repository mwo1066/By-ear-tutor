# Make the numbers a thread that reaches money, in slices

**Status:** in progress
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

- [x] rename `đếm từ 11 đến 99` → **`ghép số: chữ số + đơn vị`** (*assembling a
      number: digit + unit*). Decided 2026-08-17. It names the **mechanism** and
      not a range, so it does not go stale when billions are added, and it follows
      the pattern the other features use — `sở hữu: danh từ + của + người`,
      `so sánh: tính từ + hơn`. Nothing references the old name but its own
      definition, so this costs one line.
- [x] **the strand survives as the umbrella**, and the slices become `discrete`
      features under it. Decided 2026-08-17. What never finishes is one idea —
      *a number is built by stacking words you already know* — and it holds at 11,
      at 100, at 1000 and at a million: `năm trăm nghìn` is three words the learner
      already has. Each slice, by contrast, is a fact that **finishes**, which is
      the glossary's definition of a discrete.
- [x] split its four facts into slices, one item each, each with a gloss short
      enough to be said in one turn: 11-19; 20-99 with the reversal; `mười` →
      `mươi`
- [x] give `đồng` a gloss so it becomes teachable, and one slice for the fact
      that it is **dropped** in speech — a rule of omission, not a word to recite
- [x] add `nghìn`'s combining rule: digit + `nghìn`. **After this slice alone the
      learner can buy a coffee** — `hai mươi lăm nghìn`
- [x] add the `trăm nghìn` slice — the banknotes, 100k / 200k / 500k
- [x] add `triệu` as an atom, and its slice
- [x] the banknote slices come **after** the digits, per Meo: the material before
      the rule that combines it, which is the ordering the course already follows
- [x] check `bao nhiêu tiền?` now has an answerable reply, and consider a
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


---

## Notes while applying

**Tasks 1-3 done.** `07_so_dem.toml`: the strand renamed to `ghép số: chữ số +
đơn vị` with a gloss that states only the one continuous idea, plus three
`discrete` slices at tier 2 — 11-19, the reversal from 20, and the `mười` →
`mươi` trap. Each takes its Vietnamese from the old strand's own authoring note,
so nothing was invented.

Verified: each slice builds its own `rule` + `apply` turn, so the four facts now
get four turns instead of one. `check_roster` reports no new problem.
`smoke_test.py` at exit 0.

**Spacing measured, and it holds.** Longest run of a single category anywhere in
the course: **3**, exactly `MAX_SAME_CATEGORY_RUN`. The new slices land at slots
99, 100 and 118, interleaved with the numerals rather than bunched. (A first
measurement said 10 — it lumped `numeral` and `rules` together, and the cap is
per category.)

**Observed, not fixed:** the umbrella lands at slot **118**, after the slices at
99 and 100. The general idea trails its own specifics by eighteen slots. It may
read fine as a consolidation — *"and this keeps working all the way up"* — but it
was not chosen, `MIN_ITEMS_BETWEEN_FEATURES` put it there. Worth a decision.

## Task 4 was refused, not solved — and that was the right answer

`- [ ] give đồng a gloss so it becomes teachable` does not work, three ways:

1. **Glossing it where it lives** puts it in the wrong place. `đồng` is in
   `90_frequency_stock.toml`, which holds items **170 to 2084**, while the money
   slices belong in `07_so_dem.toml`, items 86-103. A feature waits for its
   pieces — proven on the old strand, which reports `unknown_pieces` of
   `['mười','mươi']` against the first 90 items. A money slice naming `đồng`
   would wait for a word taught hundreds of slots later.
2. **Adding it to `07_so_dem.toml`** creates a duplicate. `check_roster` reports
   *"defined twice — the later file silently wins"*, and `90_` sorts after `07_`,
   so the **unglossed** copy wins.
3. **Deleting it from the stock file** works, but that file is generated by
   `import_frequency_words.py` from two public sources and its header says *"do
   not hand-edit, re-run instead"*. A re-run brings `đồng` back, and the
   duplicate with it.

Nothing after task 4 was attempted: `nghìn`, `trăm nghìn` and `triệu` all sit in
the same file and hit the same wall the moment they need `đồng` — and `triệu`
would be a fourth duplicate, since it is not in the stock file at all, so only
that one is free.


---

## What the block turned into

Task 4 said *give `đồng` a gloss so it becomes teachable*. All three routes were
dead ends, and Meo's answer was to delete the task rather than pick one:

> **"on ne l'enseigne pas on s'en fout"**

Which is what the native speaker had already said — *"I just say the number and
then don't"*. In a course with no reading, where a price is spoken as
`một trăm nghìn` and stops there, making the currency a recall target teaches a
word nobody says. So the currency is **not an item**, and the fact about it
became a rule of **omission**: `nói giá: chỉ cần con số`, tier 1.

**And the code enforces the decision by itself.** `check_glosses_cite_only_taught_words`
allows a feature's gloss to quote only Vietnamese the course teaches, so `đồng`
cannot appear in one even by accident. The guard was already there.

Left for later, not done: `import_frequency_words.py` has no exclusion list, so
any word promoted from the frequency shelf into a lesson file becomes a duplicate
that the generated file silently wins. It will happen again. `check_roster` reports
it at startup, so it is visible rather than silent — enough to leave it.

## Verification, run

```
python smoke_test.py                     exit 0
check_roster problems (excl. the shelf)  0
longest single-category run              3   (cap 3)
```

The spacing worry was the real risk — six items added to two categories in one
file — and it holds. The money thread is taught in the order it has to be:

```
101  atom     trăm
102  atom     nghìn
103  feature  nghìn: chữ số + nghìn            tier 1
104  feature  trăm nghìn: tờ tiền hay cầm      tier 1
105  atom     triệu
106  feature  triệu: hàng của tiền thuê…       tier 2
111  construction  bao nhiêu tiền?
123  feature  nói giá: chỉ cần con số          tier 1
```

**`bao nhiêu tiền?` is answerable.** It is taught at 111, after the money rules at
103-104 — before this change it was a question taught with no sayable reply.

Features at 103 and 104 are adjacent, which rule 9c permits: an `after` anchor
goes ahead of every spacing rule.

**Not yet done: one real spoken session** reaching the money slices. Until then
this is verified offline only.

# A new word drowns in the old ones

**Status:** done.
**Opened:** 2026-08-23

## Why

Meo asked whether a word introduced after three hours of course is repeated as
much as one introduced in the first minute. It is not, and the gap is large.

Measured on the real sequencing — `pick_next_index` choosing, `build_plan`
building — over 7 simulated hours, five runs, at the 15 s/turn the simulator
already uses:

```
asked in the 120 minutes FOLLOWING its own introduction

  introduced in hour 1    7.9
  introduced in hour 2    5.9
  introduced in hour 3    5.2
  introduced in hour 4    4.1
```

**Halved in four hours.** Same word count, same window length, same learner. The
only difference is when it arrived.

The cause is arithmetic, not policy. A new word always starts at level 0, weight
1 — but the pool it competes against never stops growing:

```
  after      words met   pool weight   a new word's share
     0h              1           1.0        50.0%
     1h             41           6.6        13.2%
     3h            125          17.1         5.5%
     5h            209          30.3         3.2%
```

Projected to the course's own target of 2000 words, assuming words settle around
the levels 8–12 the simulation actually produces:

```
   150 words met  ->  a new word gets 18.6% of the draw
   500 words met  ->                   6.4%
  1000 words met  ->                   3.3%
  2000 words met  ->                   1.7%
```

**The two-thousandth word would get thirty times less attention than the
first** — not because it is easier, but because it arrived later. The last three
lines are a projection; the trend behind them is measured.

**And the property causing it is one we deliberately want.** `METHOD.md` counts
the Noble extracts — "to" 60 times in eight minutes, "Kyoto" 13 — and concludes
that the weight must decay *but never reach zero*, so a word met long ago still
comes back. That is right. The side effect is that the accumulated tail of every
old word drowns each new one.

## What is actually wrong

One draw is doing two jobs, and only one of them should depend on the size of
the course.

```
job A   drill a word just met            must be intense, and CONSTANT
job B   bring back everything ever met   must thin out indefinitely
```

Job B is the sourced curve and is not in question. Job A is not separately
represented at all — it is whatever falls out of job B when the pool happens to
be small. So it shrinks as the course grows, which is the defect.

## Direction proposed

**Reserve a fixed share of each item's recall slots for recently met words, and
leave the rest to the draw as it stands.**

```
a fixed part   drawn among the last K words met
the rest       drawn as today, whole history, by level
```

Because the reserved part is a fixed *number*, it cannot be diluted. A word met
in hour four sits in the recent window exactly as long as one met in minute
four, and gets the same drilling. It then falls into the same long tail as
everything else.

**What this preserves:** `DECAY`, the curve, and job B untouched.
**What this fixes:** the initial drilling stops depending on course size.

## The first task was done, and it failed

Counting how often a word is *heard* rather than *asked*, to compare with
Noble's 60-in-8-minutes, gave: **twice, in 120 minutes.** Deliberately — scripted
turns are built from the gloss, never from the Vietnamese name. That finding was
worth having and became `0022`, but it means **Noble's counts cannot calibrate
K**, because the two systems do not say words in the same places at all.

**They are not needed.** The target here was never "repeat as often as Noble".
It was Meo's: a word introduced late must not be drilled less than one
introduced early. That is an internal target, and it is measured against
ourselves.

## What was chosen, and on what evidence

`RECENT_WINDOW = 12`, `RECENT_SHARE = 0.75`, both swept rather than picked.

**A brand-new word's share of the recall draw, as the course grows:**

```
  after      words met     today       with the reserve
     1h            42      14.7%             22.8%
     3h           126       5.6%             24.6%
     5h           210       3.2%             16.1%
```

Today's column collapses and does not stop collapsing. The reserved column
holds. **That floor is the result** — it comes from the reservation being a
fixed number, so it holds at any course size, by construction rather than by
simulation.

## What it does NOT do, stated plainly

**The hour-1 / hour-4 gap narrows; it does not close.**

```
                    h1    h2    h3    h4    gap
  today            8.0   5.8   5.2   4.0    4.0
  with the reserve 7.2   5.6   5.4   4.7    2.5
```

It cannot close, and should not: a quarter of every draw is still the open pool,
whose entire job is the long tail that `METHOD.md` sources. An early word also
genuinely faces less competition, which is not a defect. What was a defect was
the collapse having no floor, and that is what is fixed.

**And the 2000-word regime was not measured.** The course holds ~270 teachable
items, all introduced within seven hours, so there is no late regime to simulate.
The projection in the "Why" above stands as a projection.

## Explicitly NOT in this change

**What a level counts.** Meo: *"je veux juste un ratio de rappel des mots peu
importe si t'as juste ou faux."* Today `record_recall` raises a level when the
verdict says correct; the proposal there is that it should rise on every
exposure instead, so `answered_target` stops feeding it.

That is a separate observation, it would ship separately and be useful alone,
and by this repo's own splitting test it is a separate change. It is worth
knowing that the measured looseness of that verdict — 150 of 153 taught words
can be answered by some *other* taught word — is the argument for it, and it has
nothing to do with the scaling problem here, which would exist with a perfect
verdict.

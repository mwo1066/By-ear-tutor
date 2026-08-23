# A level counts passages, not successes

**Status:** proposed — awaiting Meo. **No code written.**
**Opened:** 2026-08-23

The second half of the pair opened with `0020`. That one is about a word
arriving late in the course. This one is about the verdict. Neither fixes the
other, and each is useful alone.

## Why

Meo, 2026-08-23: *"je veux juste un ratio de rappel des mots peu importe si t'as
juste ou faux."* A word's return rate should follow **where that word is in its
own life**, and nothing else.

**`SPEC.md` already says exactly this, and the code no longer does it.**

```
rule 14   "Level 0 at introduction, +1 on each recall."
rule 16   "Wrong answers are not counted. A missed word needs more exposure,
           which a low level already arranges.
           Where: code — record_recall only increments"
```

The code:

```python
state.level = state.level + 1 if got_it else max(0, state.level - 2)
```

A miss costs two levels. That is a decision the spec does not carry, made on
13 August and never folded back. This is a `/derive` finding as much as a
proposal: the rules claim something the code stopped doing.

**And the verdict driving it is not trustworthy.** Swept across the 153 taught
single words, every word against every other:

```
1452 of 23256 wrong pairs score as CORRECT      (6.2%)
150 of 153 words (98%) can be answered by some OTHER taught word
   nói, đói, hỏi, tuổi, rồi  … all accepted as `tôi`
   tiền, nên, đến, thế nào   … all accepted as `tên`
```

Seen live the same evening: three wrong answers in a row scored correct, and
levels rose on all three. A measurement this loose should not be steering
anything, and under rules 14 and 16 it would not be.

## Why the code diverged, which must not be waved away

`srs.py` records the reason, with a real case:

> `got_it=False` moves the word back UP the queue instead of down. It was called
> unconditionally until 13 August, so a word missed twice was promoted for
> having been missed: live, "chị" was asked, missed, asked again, answered with
> the single letter "G", and came out at **level 8** — drawn once in
> twenty-seven.

So rule 16's justification — *"a missed word needs more exposure, which a low
level already arranges"* — **has a hole**. If every exposure promotes, then a
word being drilled *because* it is unknown climbs out of the low level precisely
by being drilled. The mechanism whose job is to bring back what the learner does
not know was burying exactly that.

Restoring rules 14 and 16 as written brings that failure back. It must be
answered, not ignored.

## What is proposed

**A level counts how many times the word has been through, not how many times it
was answered correctly.** `record_recall` increments, always — which is what the
spec says, and what the `apply` branch already does for features today (an
application records `got_it=True` unconditionally, on purpose). This makes words
consistent with features rather than introducing a new idea.

**What this preserves:** `DECAY`, the curve, and everything `METHOD.md` sources
from the Noble counts. Untouched.

**What `answered_target` goes back to:** deciding whether the tutor asks again
straight away — rule 20, its one original job, and the only one its docstring
still claims.

## The open question, which is Meo's to answer

The `chị` case is real. Meo already gestured at the answer before the divergence
was found:

> *"le ratio de répéter des mots ne bouge pas. À part si on a un mot complètement
> faux et l'utilisateur ne sait rien répondre."*

That is a **narrower and far more reliable trigger** than the current one. "The
learner produced nothing, or still nothing after being told the word" does not
depend on the 0.5 threshold at all — it is silence, or a second failure after
Minh has said it. Unlike `answered_target`, it cannot be fooled by `đói` for
`tôi`.

So the shape to decide between:

1. **Rules 14 and 16 literally.** Always +1. Simplest, matches the spec, and
   brings the `chị` failure back exactly as it was.
2. **+1 always, except a word the learner could not produce at all**, which holds
   its level instead of climbing. Keeps Meo's principle — a *correct* answer
   never changes anything — while closing the hole the divergence was patching.

**Recommended: 2.** It is what Meo described, it costs one condition, and the
signal it reads is the only one in this system that is not noisy.

## What must not be assumed

Whether the `chị` case still reproduces at all. It was seen on 13 August, before
`_should_retry`, before the forced-`vi` second pass, and before `0019`. **First
task, before any code: replay it.** If the retry path now catches it, option 1
may be enough and option 2 is a complication we do not need.

## Residual cost, named rather than buried

This change stops the loose verdict from steering the level. It does **not** make
the looseness harmless everywhere: `answered_target` still decides whether the
learner gets a second chance, so `đói` accepted as `tôi` still costs them the
"Listen again — tôi" they should have had. That is rule 20's problem, it is
smaller, and it is not in this change.

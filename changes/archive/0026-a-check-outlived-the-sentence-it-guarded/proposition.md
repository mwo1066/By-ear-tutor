# A check outlived the sentence it was guarding against

**Status:** done.
**Opened:** 2026-08-23

## Why

The first sample of shelf glosses came back with two refusals out of sixteen:

```
khi  -> "when"     REFUSED: gloss is a question word
nào  -> "which"    REFUSED: gloss is a question word
```

**Both are good glosses.** Here is what the tutor would actually say with them:

```
And again — what was the word for when?
So, the word for which?
```

Those read fine. A learner hears a question and knows what is being asked.

## What the check was actually written for

`content.py` refuses a gloss that is a bare English question word, and its own
comment names the sentence it feared: *"And what — what was the word?" reads as
two questions.*

That sentence came from the **inverted template**, `"And {ask} — what was the
word?"`. And `tutor.py:1412` records, with the same example:

> The inverted form, "And {ask} — what was the word?", is gone. It was the
> weakest of the four and it broke outright on a gloss that is itself a question
> word: "And what — what was the word?" reads as two questions and neither can
> be answered.

**The sentence was deleted. The check guarding against it was not.**

## And it can no longer fire on anything harmful

A one-word gloss is routed to `_REPEAT_ASK_SHORT` — `tutor.py:1540`,
`len(step.ask.split()) == 1`. Every sentence it can reach:

```
And again — what was the word for when?
Once more — the word for when?
So, the word for when?
```

The forms that would read badly are the multi-word ones, and a bare question
word **cannot reach them**:

```
And again — what was when?      <- never produced
And when — what was that?       <- never produced
```

So the check refuses glosses that are correct, and cannot catch the sentence it
exists for, because that sentence no longer exists.

## The measurement that settled it

```
taught items with a ONE-WORD gloss   56
  refused by the check                5   (gì, đâu, ai, sao, thế nào)
  accepted, and working all along    51   name, hello, and, water, have, ...
```

`tên` → "name" takes exactly the path `khi` → "when" would. Same routing, same
template, same sentence shape. If a one-word gloss were dangerous the course
would already be broken by fifty-one items. The only thing separating "and" from
"when" is a list of seven words in `content.py`.

## What is proposed

Delete it. Five taught words are flagged by it today — `gì`, `đâu`, `ai`, `sao`,
`thế nào` — and they have been printed at every startup for weeks, teaching us
to read past a wall of warnings. That is the real cost: a check that cries wolf
trains you to ignore the ones that matter.

## And the sample showed the opposite failure in the same breath

`những` was glossed *"some / those (plural marker)"* and **passed every check**.
What it produces:

```
And again — what was some or those (plural marker)?
```

That is the sentence the checks are supposed to catch, and none of them did.
Deleting the question-word rule does not create that hole; it is already there.
Whether "(plural marker)" and its like need a rule of their own is a separate
observation and a separate change — the parenthetical aside, which reads as
authoring notes leaking into speech.

## Not in this change

`các`'s 15-word gloss, still unfixed and still a content decision for Meo.

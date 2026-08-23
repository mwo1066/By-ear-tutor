# Minh says the word back, every time

**Status:** done.
**Opened:** 2026-08-23

## Why

Measured on a 120-minute replay of the real sequencing, counting only the runs
Minh actually speaks — English is not searched at all, which the first attempt
got wrong and scored `ai` 96 times inside "again" and "said":

```
a taught word is spoken aloud    2 times   in 120 minutes
```

Twice. At its introduction, and never again.

**And it is deliberate, which is why it went unnoticed.** Scripted turns are
built from the item's gloss and never from its Vietnamese name, so a question
cannot state its own answer. That rule is right. Its side effect is that after
the first minute the learner almost never hears the word — everything else is
the learner being made to produce it.

`METHOD.md` counts the reference course the other way round: "to" heard **60
times in eight minutes**. The two numbers are not measuring the same thing, and
the gap is still too large to be only that.

## What is proposed

After the learner answers a recall, **Minh simply says the word**. Then the
English voice carries on.

```
English  :  how do you say "I" in Vietnamese?
learner  :  (anything at all)
Minh     :  tôi
English  :  (the lesson continues)
```

**Always — right or wrong is not looked at.** Meo: *"on s'en fout que ça soit
vrai ou faux."* This is the same principle as `0021`: the verdict does not steer
the machinery.

## And it gives the level a definition

Meo: *"Minh répète toujours, ceci est le seul truc qui compte dans le concept de
répétition. Comme ça c'est simple."*

**A level is the number of times Minh has said the word back to you.**

That is a definition you can say in one sentence, which the old one never was.
And the arithmetic does not move: Minh echoes once per recall, so counting
echoes is counting recalls, which is what `record_recall` already does. Nothing
in `srs.py` changes.

**What does not count**, and it is worth writing down because both are cases
where Minh speaks the word:

- the **introduction**, where the word is said twice to present it;
- rule 18c's give-back on a word missed twice — *"It was ngon."* Meo: *"c'est
  juste un rappel en plus, on s'en fout."*

Both are exposure. Neither is a passage.

## What it gives

Same replay, adding one echo per recall:

```
  word     today   with the rule
  tôi          2        23
  tên          2        20
  chào         2        19
  là           2        17
  anh          2        13

  a word goes from 2 to roughly 17 times in 120 minutes
```

## What this does NOT fix

**`0020` is untouched.** That one is about how often a word is *drawn* — a word
introduced in hour four is drawn half as often as one introduced in hour one.
This change multiplies what is heard per draw, uniformly, so both words rise and
the gap between them stays exactly where it was. The two are independent and
both are needed.

## The one risk, and its guard already exists

Saying the word immediately before a question that asks for that word gives the
answer away. Rule 18c already anticipates it: *"and nothing at all if the
question that follows asks for precisely that word — the leak guard decides
that, not a second rule written beside it."*

**Meo's answer, 2026-08-23: *"pas grave."*** So the echo is unconditional, and
the guard is gone from this path — it could no longer prevent anything once the
word is said whatever the verdict. Recorded as a decision, not lost: when a
question follows that asks for the word just echoed, the learner has been handed
the answer. Rule 18c carries the same note.

## Rules this touches

- **18c** — today: on a correct answer *"the word is not said back"*. That
  sentence is what this change reverses, and it must be rewritten rather than
  contradicted in silence.
- **14** — gains the plain-language definition of what a level counts.

## What it does

```
correct,  tôi                        ->  "That's it. tôi."
correct,  tôi tên là + [tên riêng]   ->  "Exactly. tôi tên là."
missed twice, tôi                    ->  "It was tôi."
```

The construction case is the one that has bitten before: the target is stored as
`tôi tên là + [tên riêng]` and Minh, who speaks any accented word, would recite
"tôi tên là plus bracket tên riêng". The spoken form is taken through
`_target_fragments`, the same path the retry line uses, and the check refuses any
`+` or `[` reaching speech.

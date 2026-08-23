# The tutor never announces failure

**Status:** done.
**Opened:** 2026-08-23

## Why

Seen in a real session, written by the model:

> **That's not it.** How would you say thousand?

and

> **The correct word is nghìn.** nghìn. Now say it.

Meo asked for the opposite before knowing it was already the method's:
*"même si on a raté, ce n'est pas de dire 't'as faux' mais juste de demander de
répéter."*

**`METHOD.md` records the same observation, made independently:**

> the extracts contain **no negative corrections at all** — no "not quite", no
> "that's wrong", no "try again"

It is filed there as *not re-verifiable* — the working files are gone — so it is
recollection rather than a count. Meo arriving at it separately from a live
session is the strongest confirmation available, and it is what this change
rests on.

**And the code already does it right where it speaks.** The scripted retry is:

> Listen again — nghìn. Again?

No verdict. The word, and another go. That is the shape; it just is not what the
model does when the turn is its own.

## What is proposed

**No turn announces that the answer was wrong.** On a miss, Minh says the word
and the question comes again — the scripted line's shape, extended to the turns
the model writes.

The persona already forbids the neighbouring mistake — treating a *good* answer
as a failure — in detail:

> Never re-ask a question AS IF THEY HAD FAILED IT — that tells them they got it
> wrong, and they did not.

It does not forbid announcing a genuine miss, which is the gap. The wording
should be added there, beside it, rather than in a new place.

## What this does not touch

**"It was nghìn." stays.** That is the scripted acknowledgement on a word missed
twice (rule 18c), and it is not a verdict — it is Minh giving the word. The
difference is the whole point: *"That's not it."* judges the learner, *"It was
nghìn."* teaches the word.

## What must be checked first

**Whether a prompt rule is enough.** This project's own history says instructions
give way: the rule turn's "ask in English" survived six rewordings before the
fix had to be moved into the code, and `SPEC.md` 18c exists because the model
kept second-guessing the verdict. If the count after a session shows it still
happening, the answer is to script the turn, not to word the instruction a
seventh time.

So this ships with a way to count it — the diagnostic that already fires for
other leaks — and the count decides whether it worked.

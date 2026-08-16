# Changes

`SPEC.md` says what the tutor does **today**. Here we write what we want it to do
**next** — before touching it.

- `changes/` — what is proposed or in progress. One folder per change.
- `changes/archive/` — what is done. Not touched again.
- `changes/archive/JOURNAL.md` — the full list, most recent at the top.
  **This is the file to read before proposing anything.**

## The ritual

| step | command | what happens |
| --- | --- | --- |
| **1. Propose** | `/proposer <idea>` | I read the journal, check we have not already done it or already undone it, and write `changes/NNNN-name/proposition.md`. **No code is written.** You read it, correct it, refuse it. |
| **2. Apply** | `/appliquer NNNN` | I implement the tasks in order, ticking them off. If reality diverges from the proposal I stop and say so — I do not drift in silence. |
| **3. Archive** | `/archiver NNNN` | I fold the change into `SPEC.md`, write what it gave, move the folder into `archive/` and add the line to the journal. |
| **separately** | `/derive` | I re-read the code, re-derive the rules, and list what `SPEC.md` claims and the code no longer does. I change nothing. |

## Why before, and not after

A spec written after the code describes what was done. Written before, it decides
what will be done — and that is the only version you can refuse before it costs
anything.

Nothing here is a guarantee. It is a ritual: it holds as long as it is followed.
The difference from before is that a skipped ritual leaves a trace — the missing
folder, the absent journal line.

## One change, one scope

**The test: a change repairs *one* thing a real session could show going wrong.**
If it takes two distinct observations to justify it, it is two changes.

Signs it needs splitting, which I have to point out when I see them:

- the "Why" can only be written with an "and" between two problems;
- two halves of the tasks could ship separately and each be useful;
- it touches **code** here and **prompt** there, for unrelated reasons;
- the `SPEC.md` rules it touches are not in the same section.

Splitting costs one more folder. Not splitting costs a change that can no longer
be reviewed, half-refused, or found again in the journal.

## The template

One file per change, `proposition.md`:

```markdown
# <What it changes, in one line>

**Status:** proposed
**Opened:** YYYY-MM-DD

## Why
What is wrong, **observed**. A session, an output, a line of code — not a
supposition.

## What changes in SPEC.md
By rule number, with the right verb:
- rule 12c — **modified**: ...
- rule 34 — **new**: ...
- rule 7 — **removed**, because ...

And for each rule, the line that matters: **code** or **prompt**.

## Scope
**In:** ...
**Out:** ... (what could have gone in and is deliberately left out)

## Tasks
- [ ] ...

## Verification
How we will know it is done. `smoke_test.py` at minimum; say which of its cases
covers it, and what it does not cover.
```

On archiving, one last section is added:

```markdown
## Result
**Finished:** YYYY-MM-DD — commits `abc1234`, `def5678`

What was done differently from the plan, and why. What was tried and abandoned
on the way. **This is the section that stops it being redone in six weeks.**
```

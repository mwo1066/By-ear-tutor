# A turn never asks for the word it has just said

**Status:** proposed
**Opened:** 2026-08-17

## Why

Four times across two real sessions on 2026-08-17, always on a model turn.

**Shape A — the give-up path.** The learner said *"I forgot, maybe you can tell
me"*. Rule 4b-bis correctly told the model to give the word:

```
tutor: Here it is: “tôi.” Minh, please say it.
tutor: Minh.
tutor: tôi.
tutor: You’ll hear “tôi” again later.
tutor: Now, what is the Vietnamese word for “I” or “me”?
  [diag] !! the answer was given away: this turn asked FOR 'tôi' and said it
```

`tôi` is spoken three times, then asked for. Nothing is left to produce.

**Shape B — correcting by stating the answer.** On a `vary` step:

```
tutor: That’s close— the structure is “Tôi tên là Anna.”
       Now you try: how would you say “My name is Anna” in Vietnamese?
  [diag] !! the answer was given away: this turn asked FOR 'tôi tên là + [tên riêng]' and said it
  [diag] !! asking turn said a 3-word Vietnamese phrase — that is the answer: 'Tôi tên là'
```

**Saying the word is not the defect.** On shape A, saying `tôi` is the
instruction — rule 4b-bis exists to give it back. The defect is **giving it and
then asking for it in the same breath**: two moves that are each correct alone.

**The prompt already forbids it.** Persona rule 2: *"YOUR TURN ENDS AT YOUR
QUESTION… Never answer your own question."* So this is a rule **losing** to
another, not a rule missing. The pull comes from the same rule's other half and
from rule 3 — *one of your three sentences is the question* — which on a turn
whose whole job is to hand the answer back leaves the model looking for
something to ask, and the only thing in the air is the word it just said.

**Why it survived every session.** Both detectors' own docstrings say it, and the
code confirms it: `voice.say(sentence)` runs inside the streaming loop at line
1982, `_leaked_target` at line 2008. **The check speaks after the mouth.** And
`_warn_if_answer_spoken` adds: *"a question containing its own answer reads as a
perfectly good turn in a transcript, which is how it survived every session
logged."*

**But prevention is already done once, on the other path.** Line 1379, on the
scripted `missed_twice` acknowledgement, the code composes its own sentence, asks
`_leaked_target` **before** speaking, and drops it if it leaks — with a comment
explaining that a second rule was deliberately not written beside it. The
pattern to follow exists in the repository.

Nothing in `changes/archive/JOURNAL.md` has tried this. `STYLE.md` mentions "the
`_leaked_target` family of bugs" only as a risk cited against a different idea,
so there is no drawer waiting.

## What changes in SPEC.md

- **rule 19b — new**: *a turn that hands the answer back does not ask for it.*
  The step is not consumed and the word returns later by the ordinary draw, so
  nothing is lost by ending without a question.
  **Where:** to be decided — see the questions below. Either **prompt**
  (`persona.toml`), or **code** (the sentence-level check).

- **rule 4b-bis — modified**: gains the sentence that this turn ends **without**
  a question, which is the one place the persona's "end on your question" must
  not apply.
  **Where:** prompt — `persona.toml`, plus the instruction `_lesson_note` writes.

**If it goes in the prompt, what it removes:** nothing yet, and that is the
problem. `changes/archive/JOURNAL.md` records the prompt growing and being
emptied **four times**, and the rule that any proposal adding to it must say what
it takes out. A candidate: rule 3's *"one of them is the question"* is already
implied by rule 2's *"your turn ends at your question"*, and it is the half that
misfires here.

## Scope

**In:** a single turn containing both the target and a request for it.

**Out:**

- **Vietnamese landing inside an English sentence**, so the voice switches
  mid-phrase — `!! Vietnamese landed mid-sentence (2 voice switches)`, three
  times in the same sessions. A separate observation and a separate change.
- **A line spoken twice** — `Minh: Tôi tên là Lan.` printed twice in a row, once.
  Not investigated; may be a display artefact of streaming.
- Making the detectors act *after* the fact. They cannot: the sentence is
  already out of the speaker.

**Scope test, applied honestly.** Shapes A and B have different causes — A is two
instructions colliding, B is the model volunteering the answer while correcting.
That is close to the "an *and* between two problems" signal for splitting. They
are kept together because one rule covers both and **one detector already
catches both**, so a split would produce two changes with the same test. Say if
you want them separate anyway.

## Tasks

Not written until the questions below are answered — the tasks differ completely
between a prompt fix and a code fix.

## Verification

`smoke_test.py` runs the lesson loop with a stubbed model, so it can assert the
guard fires on a crafted turn but cannot prove the real model stops doing it.

1. **Offline**: the four turns above, verbatim, as cases — the guard must catch
   all four, and must NOT catch a legitimate give-back that ends without a
   question.
2. **The diagnostic already counts it.** It fired four times in two sessions, so
   the measurement is simply: run two sessions of comparable length and count
   again. This is the number that says whether it worked.
3. One real session with a deliberate *"I forgot"*, listened to: the word is
   given, Minh says it, and the turn **stops**.

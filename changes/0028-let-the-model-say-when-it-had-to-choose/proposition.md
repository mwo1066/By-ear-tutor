# Let the model say when it had to choose

**Status:** proposed — awaiting Meo. **No code written.**
**Opened:** 2026-08-23

## Why

Meo's rule for the 1640 shelf words still to gloss: *"dès qu'on a un doute on le
met de côté, puis on verra à la fin."* Right — but he cannot read 1640 entries
looking for doubt, and he should not have to.

**Two mechanical filters were tried and both failed**, measured against the 22
words he had just validated:

```
"the first sense lists 3+ alternatives"
   shelves 360 words, among them gần "near; nearby; close"
   and nhận "to receive; to get; to obtain"

"the word carries 3+ distinct senses"
   would have shelved 8 of the 22 he validated,
   including nhà "house" and giờ "hour" — four dictionary senses each
```

Meo said exactly why the first one fails: *"regarde, dans le fond c'est
exactement le même sens, donc lui on le valide: near."*

**Counting cannot tell synonyms from different meanings.** That is the whole
distinction, and it is semantic:

```
gần   near; nearby; close                 three words for ONE meaning
đưa   to bring, to take, to give, to hand  four DIFFERENT actions
```

## What is proposed

**Ask the model, because that judgement is the one thing it is actually good
at.** It adds a flag beside the gloss: *the listed senses are not synonyms of
one another, so any single gloss is an arbitrary slice.*

A flagged word gets **no gloss written**. It stays on the shelf and lands in a
short report at the end of the run — the list Meo reads, instead of the 1640.

The instruction carries both worked examples, because the distinction is easier
to show than to define: `gần` is not flagged, `đưa` is.

## Why this is better than a filter

A filter guesses from a count. This asks the question that actually matters, of
the only participant who can weigh meanings — and it costs nothing extra, since
the model is already reading those senses to pick one.

And it fails safe: a flag set wrongly shelves a word that could have been
glossed, which costs one entry on a list. A gloss written wrongly reaches the
learner.

## What must be checked, not assumed

**Whether the model actually uses it.** This project's history is a list of
instructions that gave way — the rule turn's "ask in English" survived six
rewordings before the fix had to move into code. The test is `đưa` and `gần`,
which have known answers: `đưa` must be flagged and `gần` must not. Run the
first batch over those two before trusting it on anything else.

**And whether it over-flags.** If a batch comes back with half its words
flagged, the instruction is being read as "flag anything with more than one
sense", which is the mechanical rule again wearing a different hat. The 22
already validated are the control: almost none of them should be flagged.

## Not in this change

`bị` and `đưa` stay in the hand-written `HELD_BACK` list. If the flag works,
`đưa` would be caught by it anyway — but the list records *why* a human held
each one, and that is worth keeping regardless.

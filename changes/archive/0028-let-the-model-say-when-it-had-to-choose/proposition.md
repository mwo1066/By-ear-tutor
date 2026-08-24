# Let the model say when it had to choose

**Status:** done, in a weaker form than proposed.
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

## Checked, and it over-flags — so it points instead of blocking

Run over eight words with known answers:

```
  đưa    FLAG   caught          gần   FLAG   wrong
  mang   FLAG   caught          nhà   FLAG   wrong
  khỏi   FLAG   caught          tay   FLAG   wrong
                                ngày  keep   right
                                giờ   keep   right
```

**All three that genuinely needed flagging were flagged. Three of the five that
did not were flagged too.** Perfect recall, poor precision — which is exactly
the failure this section was written to watch for.

So the design changes: **the flag points, it does not block.** The gloss is
written, and the flagged words are listed first in the run's report. Blocking on
a signal that fires on 60% of good words would have shelved most of a good
batch; pointing at them still saves reading the other two thirds, and the three
real cases are all in the short list.

Meo shelves the ones he agrees with. That is the same judgement he was making
anyway — the change is that he now starts from six names instead of twenty-four.

## Not in this change

`bị` and `đưa` stay in the hand-written `HELD_BACK` list. If the flag works,
`đưa` would be caught by it anyway — but the list records *why* a human held
each one, and that is worth keeping regardless.

# The gloss filler cannot run at the size the course already is

**Status:** proposed — awaiting Meo. **No code written.**
**Opened:** 2026-08-23

## Why

The course is at **10% of its vocabulary**: 221 items teachable, **1912 held
out** for want of a gloss. `fill_item_metadata.py` is the tool that unblocks
them, and it is what the startup banner has been telling us to run.

It does not run. Tried on a 16-item sample:

```
HTTP 413 — Requested 13327 tokens, limit 8000 per minute
```

**And it is not a matter of batch size.** Every batch carries a catalogue of
every name in the course so the model can resolve a construction's pieces:

```
  the catalogue        2133 names   ~8947 tokens
  the instructions                  ~740 tokens
  Groq free tier                     8000 tokens per minute
```

**The catalogue alone is 111% of a minute's budget**, before a single word to be
glossed is added. `BATCH_SIZE` could go to 1 and it would still fail.

So the tool broke silently the day the frequency shelf was imported and the
course went from a few hundred names to 2133. Nothing announced it. The banner
kept recommending it.

## And the catalogue is dead weight for exactly this job

It exists for one thing, and the instructions say so: a `construction` is *"a
sentence pattern assembled out of OTHER items in the list below"*, so the model
needs the list to name pieces.

The shelf contains no constructions:

```
  1912 items, all kind = atom
     0 with pieces
```

867 of them are multi-word compounds, which is the one case that might want
pieces — and `content.derive_pieces` already derives those from the name
mechanically, in code, which is where that belongs. The smoke test re-derives
pieces for every hand-written sentence on each run.

So for the whole of the work that is blocked, the catalogue answers a question
nobody asks.

## What is proposed

**Send the catalogue only when a batch can actually use it** — that is, when it
holds an item that is not a plain atom. For the shelf that removes ~8947 tokens
from every request and leaves the instructions plus the items themselves, which
is a few hundred tokens.

Nothing about what the model is asked for changes. The dictionary senses each
shelf item already carries — from `import_frequency_words.py`, via Wiktionary —
stay the source, and the instruction to **pick one of them rather than invent**
stays as it is.

## What must be measured, not assumed

**How long the full run takes.** At `BATCH_SIZE = 8` and
`SECONDS_BETWEEN_BATCHES = 30`, 1912 items is 239 batches — about **two hours**
of wall clock. Whether the smaller request permits a bigger batch or a shorter
wait is a rate-limit question with a real answer, and it should be measured on a
sample before anyone starts a two-hour run.

**And whether the glosses are any good.** That is the actual point, and it is
Meo's to judge. The run should produce a sample he can read before the other
1896 are touched.

## What this does not do

It does not gloss anything. It removes the reason the tool cannot be started.
The quality of what comes out, and whether the four gloss checks in `content.py`
catch what is wrong with it, is the next question and not this one.

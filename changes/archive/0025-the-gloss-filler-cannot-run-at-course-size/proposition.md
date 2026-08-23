# The gloss filler cannot run at the size the course already is

**Status:** done.
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

## A second blocker, found by running the sample

With the 413 gone, the sample wrote **invalid TOML**:

```toml
name = "đó"
gloss = "that (over there)"     <- inserted
hook = ""
kind = "atom"
gloss = ""                      <- the old one, never removed
```

`_insert_into_toml` only ever inserts. The lesson files simply omit a field they
have not got, so inserting was always enough there. **The shelf was imported
with `gloss = ""` present and empty** — and `_needs_fill` selects exactly those.
So all 1912 items would have come out with two `gloss` lines and the file would
no longer have parsed.

Fixed the same way it was found: an existing key is rewritten in place, a
missing one is still inserted. It matters that this surfaced on a 16-item
scratch copy and not on `90_frequency_stock.toml` with `--write`.

**This is why the two belong in one change.** Fixing the 413 alone is not
useful on its own — it only lets the file be corrupted faster.

## What it gave

```
  a batch of 8, before   13327 tokens   over the 8000/min ceiling
  a batch of 8, after     1225 tokens
  a batch of 32, after    2324 tokens
```

Sixteen shelf items glossed, and the four checks in `content.py` refused two of
them unaided — `khi` → "when" and `nào` → "which", both bare question words.

## What must be measured, not assumed

**How long the full run takes.** At `BATCH_SIZE = 8` and
`SECONDS_BETWEEN_BATCHES = 30`, 1912 items is 239 batches — about **two hours**.
A batch of 24 measures at ~1929 input tokens, well under the ceiling, and would
bring it to **40 minutes**. `BATCH_SIZE` is deliberately left at 8: output
tokens count against the same limit and have not been measured, and this
project has been burned before by an estimate standing in for a measurement.
Raise it after a real run says it is safe, not before.

**And whether the glosses are any good.** That is the actual point, and it is
Meo's to judge. The run should produce a sample he can read before the other
1896 are touched.

## What this does not do

It does not gloss anything. It removes the reason the tool cannot be started.
The quality of what comes out, and whether the four gloss checks in `content.py`
catch what is wrong with it, is the next question and not this one.

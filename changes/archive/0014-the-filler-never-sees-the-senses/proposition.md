# The gloss filler never sees the dictionary senses

**Status:** done
**Opened:** 2026-08-17

## Why

`90_frequency_stock.toml` says, in its own header:

```
# gloss is EMPTY on purpose and every item here is unteachable until it is
# filled: check_roster reports each one at startup. Run fill_item_metadata.py
# to choose a gloss from the senses listed on each item.
```

**The word `senses` does not appear anywhere in `fill_item_metadata.py`.**
Checked: zero occurrences. This is everything a shelf item sends to the model,
from `_ask_batch`:

```
đó
  category: noun, particle, pronoun
  notes (Vietnamese):
```

The name, its part of speech, and an empty note — the 1915 shelf items carry no
`description`. So the model is asked to write the English meaning of 1915
Vietnamese words **from the Vietnamese word alone**, while the dictionary senses
sit in the same file, on the same item, four lines away:

```toml
name = "đó"
senses = ["that place over there", "that person/thing over there",
          "that idea/notion I/we've just described/discussed", …]
```

**And the reason they were left there is the reason this matters.**
`import_frequency_words.py` deliberately does not write the gloss itself:

> *Wiktionary orders senses by etymology, not by use, so its first sense is
> routinely the archaic one — measured on the top 6 words: "là" comes back as
> "fine silk" when it is the copula, "tôi" as "slave; domestic servant" when it
> is "I".*

So the importer refused to pick, and left the choosing to the filler. **The
filler was never given the list.** The safeguard removed the data and nothing
replaced it.

Confirmed on the words this course would promote first — the first sense is
useless on four of the eleven checked:

```
từ    → "onomatopoeic"
sáng  → "a unisex given name"
ngày  → "Alternative letter-case form of Chúa nhật"
vui   → "a unisex given name"
```

**Why now:** every route out of the frequency shelf runs through this. The ten
common words hidden inside taught compounds — `ngày`, `qua`, `nay`, `thế`,
`nào` — are all shelf words, and a promoted word with an invented gloss is worse
than an absent one: the gloss **is** the question the tutor asks aloud.

## What changes in SPEC.md

**Nothing.** No rule describes `fill_item_metadata.py`; it is an authoring tool,
not lesson behaviour. `SPEC.md` rule 10 already says the gloss is written in the
content by hand.

**Where:** code — `fill_item_metadata.py`, `_ask_batch` and `INSTRUCTIONS`.

## Scope

**In:** the senses reaching the model, and the instruction telling it what they
are and why the first one is not to be trusted.

**Out:**

- **Getting words off the shelf at all** — the duplicate, and the position. That
  is `0015`, and it is the actual lock.
- **`_needs_fill` never asking for a hook**, so the 203 items already carrying a
  `kind` and a `gloss` are never revisited. Separate.
- **Running the filler on the 1915.** Deciding to trust what comes back is Meo's,
  and it is not this change.

## Tasks

- [x] `_ask_batch`: include each item's `senses` in what is described to the
      model, marked as dictionary senses
- [x] `INSTRUCTIONS`: say the senses are ordered by etymology and not by use, so
      the first is regularly archaic — pick the one a beginner needs, and prefer
      a listed sense over inventing one
- [x] check what is sent, for one real shelf item, before and after

## Verification

`smoke_test.py` does not exercise this file — it is an authoring tool and makes
network calls.

1. **Print the payload** for a known shelf item and confirm the senses are in it.
   Offline, no request.
2. **A dry run on one file**, `python fill_item_metadata.py` without `--write`,
   read against the senses: a gloss that contradicts every listed sense is the
   failure this change exists to prevent.
3. The real test is Meo reading the diff, which is what the script's own
   docstring asks for: *review the diff, not the items one by one*.


---

## Result

**Finished:** 2026-08-17

The senses now reach the model, and the instruction says how to read them.
Before and after, for one real shelf item:

```
before          đó
                  category: noun, particle, pronoun
                  notes (Vietnamese):

after           đó
                  category: noun, particle, pronoun
                  dictionary senses: that place over there | that person/thing
                    over there | that idea/notion I/we've just described | …
                  notes (Vietnamese):
```

**What it actually buys, measured across the 1915:**

```
1050  (54%)  two senses or more   -> a real choice, which is the point
 850         exactly one sense    -> take it, or override it
  15         no sense at all
```

**And the measurement found something the proposal had not.** For some words the
list is not merely thin, it is wrong, with nothing better further down:

```
ngày   sole sense: "Alternative letter-case form of Chúa nhật"   (it means day)
sáng   sole sense: "a unisex given name"                          (it means morning)
```

Sixteen items are in that state, and they are disproportionately the common words
this course needs next — `ngày`, `sáng`, `vui`, `thành`, `bình`. Passing the
senses does nothing for them, so the instruction now names the pattern: a lone
sense reading *a given name*, *a surname*, *Alternative letter-case form of*, or
*onomatopoeic* is Wiktionary describing a homograph, not the word, and must be
overridden.

So this change is worth less than it first looked — **it helps on 54% and warns
on the rest** — and it is still the difference between a model reading a
dictionary and a model guessing from a Vietnamese word it was shown alone.

**Not run.** Filling the 1915 is a separate decision and Meo's, and the words this
course actually needs are still behind `0015`: they cannot be taken off the shelf
at all.

# Grammar is not vocabulary, and the shelf imported it as if it were

**Status:** proposed — awaiting Meo. **No code written.**
**Opened:** 2026-08-23

## Why

Forty shelf glosses were filled as a sample. They came back like this:

```
bị    "be (passive)"
sự    "abstract noun marker"
thứ   "ordinal (first, second, etc.)"
những "some (plural)"
```

Meo asked the question that settles it: *"dans l'état aujourd'hui le tuteur ne
donne pas plus de détail que ça ? il introduit juste be (passive) ?"*

**It does not.** Rendered, every turn the learner would hear for `bị`:

```
In Vietnamese, the word for be (passive) is bị. bị. Now you say it.
bị. And be (passive) — what was that?
```

Shelf items carry an empty `hook` and an empty `description`, so the gloss is
not a label beside other information — it is **all** the information. There is
nothing else to lean on.

And no gloss can fix it, because the problem is not the wording. `bị` is a
grammatical marker. It cannot be learned the way `cà phê` is learned, and asking
"what was be (passive)?" is asking a beginner to translate a piece of
terminology they have never been taught.

## The course already has the distinction

`kind`: `atom` for a thing the learner says, `feature` for a fact the tutor
states and the learner never says back. **All 1912 shelf items were imported as
`atom`**, and nothing has looked at that since.

## How much of the shelf this is

```
  1147  noun          }
   760  verb          }  ordinary vocabulary, glosses cleanly
   448  adjective     }

   222 of 1912 are at least partly grammatical
```

And the sample was drawn from the worst possible end of the list:

```
  items    0-40     72% grammatical   <- what was sampled
  items   40-200    31%
  items  200-600    13%
  items 1200-1912    5%
```

The top of a frequency list is always function words. Further down it is `gà`,
`giường`, `phố`, `chim`, `nghèo` — chicken, bed, street, bird, poor. **The
sample was the hardest 2% and would have condemned the other 98% with it.**

## What is proposed

**Gloss the ordinary words, and leave the grammatical ones alone.**
`fill_item_metadata.py` skips an item whose part of speech is grammatical —
particle, pronoun, conjunction, preposition, classifier, determiner,
interjection. They stay on the shelf, ungloassed, which is where they already
are and costs nothing.

Meo, 2026-08-23: *"on va se focus maintenant sur les mots ordinaires, faciles à
gloser, petit à petit."*

## What this decides, and what it does not

**It decides** that a grammatical word is not taught by translating it. That is
a content decision and Meo made it.

**It does not decide** what happens to those 222 instead. Some deserve a rule —
`những` is already tangled with the unanswered `các` vs `những` question. Some
may deserve nothing. That is a separate piece of work and it is not this one.

## What the sample also showed, and is NOT fixed here

Two failures no check can catch, because the glosses are *correct*:

```
nó   "it"    — a native speaker's note on file says it is very impolite,
               used mostly of people younger than you
hắn  "he"    — same family, derogatory
```

A learner given "it" for `nó` will be rude to an adult. The checks test shape;
only a person tests truth. Worth knowing before 1690 more arrive.

And a gap in an existing check: *"describes the word instead of translating
it"* looks for the literal string `word`, so `marker`, `ordinal`, `passive` and
`particle` walk straight through it. Skipping grammatical items hides that gap
rather than closing it.

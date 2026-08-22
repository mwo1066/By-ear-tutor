# The tones: an announcement early, then two at a time

**Status:** done
**Opened and finished:** 2026-08-17

**Written after the code.** Same skipped ritual as `0017`, and recorded rather
than dressed up.

## Why

The course said tones exist and never said which. One rule, at slot 79, glossed
*"the same sounds said at a different pitch are different words"*. True, and
unusable: it names none of the six.

**And the scale of what it was skipping, measured across all 2065 words:**

```
one-syllable words in the files              1171
groups differing ONLY by tone                 252
words caught in such a group                  600   → 51%
```

**Half the vocabulary has a tone twin.** `bạn` (friend) against `bán` (to sell),
both taught. `là` (to be) against `lá` (leaf). `qua` against `quả`, `quá`, `quà`.
At 126 taught words this is 6 pairs and a curiosity; at 1171 it is the single
biggest source of confusion in the language.

## What changed

**The announcement moved from slot 79 to slot 8.** It was the last entry of
lesson 01, so it landed after everything. It now fires right after the learner
builds their first sentence, and it announces rather than teaches: *"Vietnamese
changes the meaning of a word by the pitch you say it at — so when Minh speaks,
copy the tune and not only the sounds. Which tunes there are comes later."*

**Three new rules, one per pair, spread across the course:**

```
slot   8   listen for the tunes                     (announcement)
slot  89   flat, and flat-then-falling
slot 147   the fast rise, and the low short one
slot 189   the two dippers
```

The pairing is not arbitrary. The phonetic descriptions and the course's own
counts agree: one source defines the falling tone **by** the flat one, and those
two are also the commonest in the content (38 and 18 annotated items). The two
dippers are the rarest (7 and 2), the hardest, and the two the south merges —
which is why this course keeps them, being northern.

**Each carries the English sound to imitate**, quoted from
`ling-app.com/blog/vietnamese-tones`:

```
flat        "similar to 'sing' in an affirmative sentence in English"
falling     "similar to 'Uhm' in English when you agree with someone"
rising      "similar to 'What???' in English"
dipping     "similar to 'really?' but a bit faster"
broken      "similar to when you say something at a high tone but someone
             punches your belly so your voice is broken"
heavy       no comparison offered, in this source or the others read
```

Five of six. The broken one is the best of them: a punch in the belly is exactly
the glottal break that separates it from the plain rise, and it is an instruction
to the body rather than a description.

## What the smoke test refused, and it was right

The first draft named the tones, and `check_glosses_cite_only_taught_words`
failed it — the rule quoted a tone name the course never teaches.

Correct, and it is the same principle the tone note already carried: **the
learner never sees writing here**, so tone names are metalanguage they will never
say. The glosses describe the tunes by sound instead — *"one is flat… the other
falls away"* — and name a taught word carrying each.

## The material that was already there

95 of the 218 teachable items carry their tone in the authoring note, with a
description of the sound: `tôi` is annotated *"Thanh ngang — giọng đều, không lên
không xuống"*. Nothing reads them. They are what the three new rules draw their
anchor words from, and they are the material for Meo's third idea — tone
reminders during ordinary recalls — which is **not built**.

## Known debt, accepted on Meo's call

**The three new rules inherit a broken application.** A feature's exercise is
picked by shared pieces, so a tone rule gets pinned to whatever sentence happens
to contain its anchor words — the existing tone rule asks for `tôi tên là`, which
exercises nothing about tones. Meo: *"l'exercice pour le moment c'est une
difficulté en plus, donc un peu oublier."* So three more imperfect exercises ship
knowingly.

**And it cannot be fixed the usual way.** `_bare` strips tone marks, so `ba` and
`bà` are the same string, and `answered_target` says they match. No tone answer
can ever be scored, which is deliberate — a beginner and a recogniser both lose
tone first, and Whisper returned `Hồng` for `không` in a real session today.
Anything built here is exposure, never a graded answer.

## Not verified

No session has reached slot 89. Offline only: smoke test at exit 0,
`check_roster` clean, the plans build.

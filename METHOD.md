# What we actually measured

The rules in [SPEC.md](SPEC.md) are not a memory of how Paul Noble teaches. They come
from counting moves in real recordings. This file keeps the counts, because the audio
and the transcripts were downloaded into a scratch directory that has since been
deleted — these numbers are the only surviving record, and they are the reason the
tutor is built the way it is.

Source: two Paul Noble course extracts, ~25 minutes total, Japanese and Mandarin. Two
different languages on purpose: if the same pattern appears in both, it is the method,
not the language.

## The moves

Counted across the two extracts.

| Move | Japanese | Mandarin |
|---|---|---|
| "How would you say ___ ?" | 16 | 6 |
| "What was ___ ?" (isolated recall) | 16 | 5 |
| "And again / Now again" | 9 | 6 |
| **"Repeat after me"** | **0** | **0** |

Zero. In twenty-five minutes across two languages, he never once asks the learner to
repeat after him. The learner is always *building* an answer, never reproducing a
sound. This single number is why the tutor was rebuilt: the original persona was
written around "now you try, repeat after me", which is the one move the method does
not contain.

→ SPEC.md rule 18.

## How often a word comes back

Counted over ~8 minutes of effective teaching in the Japanese extract.

| Word | Times heard |
|---|---|
| to | 60 |
| I went | 28 |
| Tokyo | 24 |
| restaurant | 17 |
| with | 16 |
| Kyoto | 13 |

Sixty times in eight minutes for one word. Nothing is taught once. Nothing is ever
finished. This is the source of the level-based recurrence in `srs.py`: the weight of
an item decays but never reaches zero, so a word met long ago still comes back.

→ SPEC.md rules 16, 17.

## The pace

| | |
|---|---|
| Gross rate | 95 words/minute |
| Silence | 59 % of the running time |
| Rate while actually speaking | 232 words/minute |

The 59 % is not dead air — it is the learner answering. He speaks fast, then gets out
of the way for longer than he spoke. A tutor that fills the silence is not being
helpful; it is taking the exercise away.

→ SPEC.md rule on the three-sentence ceiling.

## Not re-verifiable

Two findings from the same listening pass survive only as recollection, because the
working files are gone: a count of "literally ___" as a scaffolding move, and the
observation that the extracts contain no negative corrections at all ("not quite",
"that's wrong", "try again"). They are recorded here as unverified. If the extracts are
ever downloaded again, count these two properly before relying on them.

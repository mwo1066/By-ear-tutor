# Glossary

**Read this before `SPEC.md`.** Every term this project uses, defined once.

Terms are grouped by **where they come from**, because that is what an outsider
needs first — knowing whether a word is standard vocabulary they may already
have, or something this project made up:

| group | what it means for you |
| --- | --- |
| **[1. Standard terms](#1-standard-terms)** | linguistics or language-teaching vocabulary, used here in its ordinary sense. If you know the field, you already know these. |
| **[2. Borrowed and narrowed](#2-borrowed-and-narrowed)** | standard terms this project restricts to a narrower meaning. Knowing the field helps, but the restriction matters. |
| **[3. Coined here](#3-coined-here)** | no equivalent outside this codebase. These need reading. |

One more distinction runs through everything. Every guarantee is labelled by
**where it is enforced**:

| | |
| --- | --- |
| **code** | a guarantee. The model cannot violate it. |
| **prompt** | an instruction. It follows it most of the time, and forgets it the rest of the time. |
| **content** | a guarantee that holds because of how the course files are written. A wrong field disables it silently. |

---

## 1. Standard terms

Used here exactly as the field uses them.

| term | in this project | field |
| --- | --- | --- |
| **gloss** | what fills "the word for ___". Spoken aloud; never a grammatical description. Stored as `gloss`. | linguistics |
| **interlinear gloss** | the word-for-word English of a Vietnamese sentence — *I name is Nam* — given aloud before asking for the sentence. Stored as `literal`. | linguistics |
| **construction** | a sentence pattern assembled from other items, with a slot: `tôi tên là + [name]`. 8 in the course. | construction grammar |
| **feature** | a fact about the language that is neither a word nor a sentence: SVO order, no grammatical gender, tone, politeness encoded in address terms. 35 in the course — **one taught item in five**. Stored as `kind = "feature"`. | linguistic typology. Most map onto named WALS features: 81A *Order of Subject, Object and Verb*, 13A *Tone*, 55A *Numeral Classifiers*, 45A *Politeness Distinctions in Pronouns*. |
| **strand** | a feature that never finishes, so it cannot hold a position in a sequence: tone attaches to every word, the address system to every sentence containing a person. Stored as `nature = "strand"`. 7 items. | curriculum design |
| **minimal pair** | two words separated only by tone, spoken back to back by the Vietnamese voice when the second is introduced: `ba` / `bà`. Called *tone twin* in the code (`tone_twin`). | phonology |
| **address terms** | the Vietnamese person-word system: the word for "I" changes with who you are speaking to. Called `xưng hô` in the content. | sociolinguistics |
| **tone** | `thanh điệu` in the content. Computed from the diacritic, never annotated by hand. | phonology |
| **scaffolding** | giving the word-for-word order aloud so a beginner can produce a sentence they have never heard. The `scaffold` turn. | learning theory (Bruner) |
| **retrieval practice** | asking for a word with no context, so it must be recalled rather than recognised. The `recall_piece` and `rapidfire` turns. | cognitive science |
| **spacing effect** | a word's return frequency falls as it consolidates, and never reaches zero. Here the interval is counted **in words met, never in days** — the course is one continuous line you stop and resume. Stored as `level`. | cognitive science |
| **elicited production** | "so how would you say ___?" — the course's central move. Measured against the reference course: 22 occurrences, against zero for "repeat after me". | second-language acquisition |
| **inductive grammar** | the pattern is named *after* it has been produced, never before. The `rule` turn, always last in a construction's chain. | language pedagogy |

---

## 2. Borrowed and narrowed

Standard words, deliberately restricted here.

| term | standard meaning | what it means here |
| --- | --- | --- |
| **item** | anything in a syllabus | one teachable unit, of exactly three kinds: `atom`, `construction`, `feature`. The real course holds 170. |
| **atom** | — (this project's word for a **lexical item**) | a single word. `ngon`, delicious. 127 in the course. |
| **piece** | *constituent*, a unit of syntactic analysis | an item **already taught** that another is built from. `tôi tên là` has pieces `tôi`, `tên`, `là`. Pedagogical, not syntactic: it tracks what the learner already has. Stored as `pieces`. |
| **category** | part of speech | the item's word class (`verb`, `numeral`, `feature`…). Used for **spacing**, not for teaching: three items of one category in a row is a theme, a fourth is a drill. Stored as `category`. |
| **tier** | in vocabulary instruction, Beck's tiers rank words by academic utility | here, a ranking of discrete features by **conversational** utility: 7 you cannot speak without, 11 very frequent, 10 comfort. **Not Beck's tiers** — same word, different scheme. Stored as `tier`. |
| **level** | — | a word's consolidation counter. Rises on each successful recall, decides how often it returns. Wrong answers are never counted down. |
| **hook** | — | a true fact about a word, spoken **before** the word is given, so the fact earns the word. Filled on 1 item of 170 today. When it takes a compound apart, it is **morphological analysis**. |

---

## 3. Coined here

No equivalent outside this project. Defined nowhere else.

| term | definition |
| --- | --- |
| **discrete feature** | a feature that is taught once and should come back — "`không` before a verb negates it". The opposite of a **strand**. 28 items. Stored as `nature = "discrete"`. The binary itself is this project's: syllabus design implies it, but never as a field on an item. |
| **scripted turn** | a turn whose two halves the code already holds — the meaning to ask from, and the word that must not be said. Composed by the code and sent straight to speech synthesis, with no model call. Six of the nine turn kinds qualify. |
| **settle** | re-asking the same word one turn later, short and marked as a repeat. Neither spaced retrieval (the gap is one turn) nor repetition (the question changes shape). |
| **apply** | asking the learner to put a feature to work on material they have just recalled. |
| **vary** | re-asking the same sentence addressed to a different person, so the address system shows itself. |
| **verdict** | what the code decided about an answer — correct, missed twice, or nothing — handed to the model so it does not judge again from the raw transcription and contradict the code. |
| **leak guard** | the check that stops a turn from speaking the Vietnamese it is asking for. A question that states its own answer reads as a perfectly good turn in a transcript, which is how it survived every session logged. |
| **mute stock** | the 1,915 frequency-imported words with no gloss written, held out of lessons until someone writes one. |

---

## The word "rule", and why it is not used

It meant two things, and the collision cost real time — including for the
project's own author.

| | what it is | where | how many |
| --- | --- | --- | --- |
| a **rule** | a numbered entry in `SPEC.md`: one behaviour of the program | `SPEC.md` | 59 |
| a **feature** | a fact about Vietnamese that gets taught | `content/` | 35 |

They nest: rule 13b *applies to* all 35 features.

The item kind was called `kind = "rule"` until the collision was removed; it is
`kind = "feature"` now. The name survives in one place only — the `rule` **turn**,
the one that names a pattern at the end of a construction. That is a kind of
turn, not a kind of item, so the two no longer overlap.

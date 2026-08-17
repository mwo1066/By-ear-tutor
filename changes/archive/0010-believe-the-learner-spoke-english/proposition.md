# Believe the learner spoke English without demanding four words of it

**Status:** done
**Opened:** 2026-08-17

## Why

Rules 4b-bis, 4c and 4c-bis give the learner the right to stop the lesson and
speak. The code protects that right with **a prediction about what they will
say**: `is_learner_talking` believes a real interruption is longer than three
words.

**That prediction is the defect.** Nothing can know in advance how someone will
phrase an interruption, and everything short of four words falls through the
floor — where it is converted into Vietnamese and scored as a right answer.

Said out loud into the real microphone on 17 August (`measure_english.py`). These
are **evidence that the threshold is wrong, not a list of allowed phrases** —
nothing in this change looks at what was said:

| said in plain English | Whisper's guess | its text | words | guard fires? |
| --- | --- | --- | --- | --- |
| "Can you repeat that?" | English | `'You repeat that.'` | 3 | **no** |
| "I didn't understand" | English | `"I don't understand."` | 3 | **no** |
| "I forgot" | English | `'I forgot.'` | 2 | **no** |
| "Can we work on numbers now?" | English | `'We work on number nine.'` | 5 | yes |
| "I want to practise asking questions instead" | English | `'I want…instead.'` | 7 | yes |

`is_learner_talking` requires **more than three** words. The three shortest
things a learner ever says are two and three words long, so the guard does not
fire, the forced-Vietnamese pass runs, and Whisper **translates** the English:

```
you say      "I didn't understand"
forced vi -> "Tôi không hiểu."
```

Reproduced offline, no network, deterministic:

```
step expecting 'không':  answered_target -> True   <-- SCORED CORRECT
step expecting 'tôi':    answered_target -> True   <-- SCORED CORRECT
step expecting 'hiểu':   answered_target -> True   <-- SCORED CORRECT
```

`tôi` and `không` are tier-1 words, among the most often asked in the course. So
saying *"I didn't understand"* on one of the commonest steps in the lesson raises
the word's level and moves on. **You said you did not understand and were told
"Exactly."** It is the 13 August failure, still live, on shorter input.

"Can we work on numbers now?" is the same shape: forced vi returns
`'và chúng ta sẽ làm việc với số 9'`, which scores correct against `chúng ta`,
`sẽ` and `việc`. That one is saved today only by its length.

### And the two halves do not agree on the number

`tutor.py` handles the English correctly — `learner_spoke_freely` fires at
**three words or more** (`>=`), and `"I don't understand."` is three. It would
have caught it.

It never sees it. `listen.py` fires at **more than three** (`>`), and it runs
first. It has already returned `[lang:vi] Tôi không hiểu.`, and the first line of
`learner_spoke_freely` is *if the tag says Vietnamese, this is not free speech.*

**The ear demands four words. The teaching demanded three. The sentence is three.**
It dies between two constants that are both set to 3 and are compared with
different operators.

## What the measurements say to do instead

Whisper's automatic detection is not unreliable — it is unreliable **in one
direction**, and reliable in the other. Eleven real recordings:

| what was said | how often the guess was right |
| --- | --- |
| a full English sentence | **5 of 5** — English every time |
| a single Vietnamese word | **0 of 6** — Dutch, Chinese, Portuguese, Vietnamese, Portuguese, Chinese |

And not once, in six Vietnamese attempts, did it answer "English".

**This was wrong, and applying it proved so within the hour. See the next
section.** The sample was six recordings from one afternoon; the repository
already held three counterexamples.

So `lang == "en"` looked like a strong signal needing no length test.
The length test exists for the documented 13 August case where an English
request came back tagged **Korean** — that branch stays.

**This removes a prediction rather than refining one.** The question becomes
"did the decoder read this as English", which is a property of the audio, not a
guess about the learner's phrasing. Any English sentence works, of any length,
including one nobody thought of. It adds no list and touches none — rule 4b-bis
already warns that `_GAVE_UP` is the one list in the project and that a growing
list is the signal to find the property instead. Here the property was already
available and was being second-guessed.

## Attempted, and reverted the same hour

The change was applied — `is_learner_talking` firing on `lang == "en"` with no
word count — and `smoke_test.py` failed three of its eight `TALKING_CASES`:

```
FAIL — 'toi' (en) should be left to the second pass
FAIL — 'Fen Bey.' (en) should be left to the second pass
FAIL — 'and Bay' (en) should be left to the second pass
```

**A mangled Vietnamese attempt does come back tagged English.** `'Fen Bey.'` and
`'and Bay'` are attempts at `sân bay`; `'toi'` is `tôi` badly spelled. All three
are recorded from real sessions and all three were in the repository before this
was proposed. The claim above — "not once in six" — was measured on one
afternoon's six samples, and never checked against the tests. **Reading
`smoke_test.py` was the cheapest possible refutation and it was skipped.**

Reverted: `listen.py` and `SPEC.md` back to green, exit 0.

### And the problem is harder than the "Why" makes it sound

| must be protected | words | must reach the forced pass | words |
| --- | --- | --- | --- |
| `"I forgot."` | 2 | `'toi'` | 1 |
| `"I don't understand."` | 3 | `'Fen Bey.'` | 2 |
| `"You repeat that."` | 3 | `'and Bay'` | 2 |

Both groups are short, both are tagged English. **Neither the length nor the
label separates them.** The `> 3` threshold was not careless — it deliberately
sacrificed short interruptions to save the attempts. The cost was simply never
written down.

### The property that might separate them, measured

An attempt is a Vietnamese word spelled wrong, so it **resembles the word the
lesson is waiting for**. Speech does not. `answered_target` already computes that
similarity, offline and deterministically:

| | similarity to the expected word |
| --- | --- |
| `'toi'` vs `tôi` | **1.000** |
| `'and Bay'` vs `sân bay` | **0.857** |
| `'Fen Bey.'` vs `sân bay` | **0.571** |
| `"I forgot."` vs `không` | 0.308 |
| `"We work on number nine."` vs `không` | 0.222 |
| `"I don't understand."` vs `không` | 0.174 |
| `"You repeat that."` vs `tôi` | 0.100 |

Every recorded attempt lands above 0.571; all speech below 0.308. A threshold in
that gap separates all six.

**Where it breaks:** `'Bye!'` against `tôi` scores **0.000**, and Whisper did
write `Bye!` for `tôi` on 17 August — under a forced-English decode, not an
automatic one, so it is plausible rather than recorded.

**Why that may be acceptable, and this is the decision to take:** the two
mistakes do not cost the same.

- an attempt mistaken for speech → kept as heard, step marked missed, **asked
  again** (rules 20, 4c-bis). Cheap.
- speech mistaken for an attempt → translated into Vietnamese, **scored as a
  correct answer**, level raised, lesson advanced. This is the failure being
  fixed.

So the threshold should be set by the expensive direction: speech tops out at
0.308, so somewhere near 0.45 leaves margin, and the cheap direction absorbs
whatever is left.

**Cost of doing it:** `is_learner_talking` has to be given the expected word,
which it does not currently receive — a signature change. And `TALKING_CASES`
needs an expected word per row; the three attempts have theirs recorded, the
speech rows do not and would have to be supplied, which weakens those rows.

**Not decided.** A word count is a prediction about the learner and is provably
wrong. A similarity threshold is a property of the audio against what the lesson
asked, holds on everything recorded, and has one plausible hole with a cheap
failure. That trade is Meo's to accept, not mine to assume.

## What changes in SPEC.md

- **rule 25 — modified** (the blockquote on the second pass): when the decoder
  says **English**, the learner is talking to us and their words are kept **with
  no word count required**. The length test stays only for a language outside
  {vi, en}, where the label itself carries no information.
  **Where:** code — `listen.py` → `is_learner_talking`

- **rule 25b — unchanged.** With no expected word there is nothing to compare a
  length to, so its absolute threshold stays.

Nothing about rule 26: no text is repaired, and confident Vietnamese is still
never touched.

## Rejected, with the measurement, so it is not proposed again

**Decoding in Vietnamese first when a Vietnamese word is expected.** This is what
this folder proposed at 14h and it is **wrong**. It would have made the bug above
systematic instead of occasional: every English sentence would meet a decoder
told to hear Vietnamese, and `"I didn't understand"` becomes `"Tôi không hiểu."`
100% of the time. Automatic detection is not the defect here — **it is the only
thing that protects the learner's right to speak.**

**Whisper's own confidence fields**, `no_speech_prob` and `avg_logprob`:

| clip | `no_speech_prob` | `avg_logprob` | text |
| --- | --- | --- | --- |
| room noise, nothing said | 0.052 | **-0.079** | `' Gracias.'` |
| a real Vietnamese word | 0.033 | -0.475 | `' 안녕하세요'` |
| a real Vietnamese word | 0.025 | -0.643 | `' Estoy...'` |

`avg_logprob` runs backwards: Whisper is six to eight times more confident on
noise than on a real voice. A confidence filter would keep the hallucination and
throw away the learner. **Whisper does not hallucinate hesitantly.**

## Scope

**In:** the condition under which `listen.py` decides the learner is speaking
rather than attempting a word.

**Out:**

- **Aligning the two thresholds** (`SENTENCE_WORDS` in `listen.py`,
  `FREE_SPEECH_WORDS` in `tutor.py`). Same idea, same value, different
  operators, two files. Worth its own change — it is a second observation.
- **Silero VAD**, and noise becoming text. A different failure, still not
  reproduced: the probe that turned room noise into `' Gracias.'` bypassed the
  microphone gate entirely. Reproduce it first.
- **PhoWhisper** or any model change. Forced Vietnamese already gets 3 of 4.
- **`là` heard as `Tôi...`** — a real mishearing, out of reach here.

## Tasks

- [ ] `is_learner_talking`: fire on `lang == "en"` with no length test; keep
      `lang not in {vi, en}` **and** long as the second branch
- [ ] rewrite the blockquote of rule 25 in `SPEC.md`, and its **Why** with the
      three phrases above
- [ ] record in `STYLE.md` or the journal that automatic detection is reliable on
      English and useless on an isolated Vietnamese word — it is the fact the
      whole design rests on
- [ ] check the six Vietnamese attempts still recover: none of them is tagged
      English, so none should take the new branch

## Verification

`smoke_test.py` runs with the network unplugged and cannot transcribe, so it only
proves nothing else broke.

What verifies it:

1. **Offline and deterministic, the case that fails today.** `is_learner_talking`
   on the five measured English strings must return True for all five, where it
   returns False for three of them now. No microphone needed — the strings are in
   this file.
2. `measure_english.py` re-run: the two Vietnamese controls must still come back
   `'Tôi...'` and `'Không'`, not treated as English.
3. **One real session where you interrupt on purpose.** On a step asking for
   `không`, say *"I didn't understand"* out loud. Today it is scored correct and
   the lesson advances. It must instead answer you and come back to the same step
   — rule 4c-bis.


---

## Result

**Finished:** 2026-08-17 — commits `d288d37`, `1bf6cd4`, `bc62622`, `50a38f0`,
`d70d018`

**What it gave.** Interruptions wrongly scored as correct answers, swept over all
129 targets a recall step can ask for against 43 real interruptions:
**3354 of 5547 before (60.5%), 5 after (0.1%)**. Confirmed by voice: *"Too
fast."* — two words, the exact case that failed — now gets *"I hear you—let's
take it a bit slower"* and **the step waits**.

**Three attempts, two of them wrong, and that is the useful part.**

**Attempt 1 — force Vietnamese on the first pass.** Refuted by `smoke_test.py`
within the hour: `'toi'`, `'Fen Bey.'` and `'and Bay'` are real attempts that come
back tagged English, and all three were already recorded in the tests before this
was proposed. It would have made the bug systematic. **Reading the tests was the
cheapest possible refutation and it was skipped.**

**Attempt 2 — trust `lang == "en"`, with a two-word floor.** Shipped, and
Meo's session broke it the same evening: *"too fast"* came back tagged
**Italian**, so an English-only floor never fired. The measurement behind it —
"English detected 5 of 5" — was taken on full sentences only. At two words the
label is a coin toss.

**Attempt 3, which holds.** One floor for every language the decoder names,
because the name carries nothing — this microphone was called Italian, Russian,
German, Spanish, Turkish, Korean, Dutch, Portuguese and Chinese for a voice
speaking two languages. Every asking step passes its target, not only a recall.
The English reading is re-checked before being believed, which recovers
`'Totten-Lay-Anna.'` as *"Tôi tên là Anna"*. And resemblance accepts a slot.

**What the length rule really was.** Not mistuned — **anti-correlated**. Meo's two
failures pulled opposite ways: `"too fast"` (2 words) is speech and was called an
attempt; `"Tôi tên là Anna"` (4 words) is the answer and was called speech. No
threshold fits, because length was never the property.

**Tested and rejected, with numbers:** `no_speech_prob` and `avg_logprob`.
`avg_logprob` runs backwards — Whisper is six to eight times more confident on
room noise than on a real voice.

**Found on the way out.** Making resemblance ignore a slot left the scorer still
reading it, so saying the Vietnamese for "verb" or "noun" scored as the answer on
five of the eleven slotted constructions. Closed in `d70d018`.

**Still open, deliberately.** One word of English is unprotected — that is where
a badly heard attempt lives, and the trade was accepted explicitly. Five
combinations of 5547 remain, named in `SPEC.md`. Noise becoming text — the
`La La School` outro — is a different failure, observed once and **never
reproduced**: the probe that made Whisper invent from room noise bypassed the
microphone gate. Reproduce it before proposing Silero.

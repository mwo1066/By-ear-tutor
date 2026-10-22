# Chinese — a different idea, not a second course

Decided 2026-10-07. Nothing is built yet; this is the plan.

The Vietnamese course is a **course**: 1346 items in a composed order, a tutor
that decides what comes next, spaced repetition underneath. Chinese is the
opposite experiment. Meo: *"un truc super libre"*.

```
Vietnamese                               Chinese
a course of 1346 items, order fixed      no course at all
the tutor decides what to ask            the learner asks whatever they want
spaced repetition, levels                nothing, to begin with
tutor.py: 2600 lines                     one loop: listen -> answer -> ask to repeat
```

The learner speaks English or Chinese and asks for anything — how to say a
thing, what a word means, a sentence for a situation. The model answers, says
the Chinese, and asks the learner to say it back. No lesson plan, no queue, no
memory between sessions at first: only a log of what was said. Memory is added
if its absence is felt, not before.

## The engine is NOT language-agnostic, whatever the docs used to claim

Checked 2026-10-07 by feeding Chinese to the code as it stands, unchanged:

```
"The word for water is 水. Now you say it."   -> all of it to the English voice
"我想喝水。"                                    -> all of it to the English voice
```

`voice.py` recognises one language, Vietnamese, by its diacritics. A Chinese
character is not even matched as a word: it is treated as punctuation and glued
onto the English run. `listen.py` accepts only `vi` and `en`; Chinese is
detected as an unknown language and, if short, **re-decoded as Vietnamese**.
`"vi"` is written as a literal in four places there.

## The plan: three floors, and only the middle one depends on the language

```
3. THE PROGRAMMES       one per way of learning
   tutor.py, srs.py, content.py   -> the Vietnamese course
   chinese/free.py                -> the free conversation

2. THE LANGUAGE PROFILE one per language, small  (languages.py)
   Vietnamese: Minh's voice, a word is recognised by its diacritics,
               Whisper accepts vi + en
   Chinese:    a Chinese voice, a word is recognised by its characters,
               Whisper accepts zh + en

1. THE PLUMBING         shared, the same for every language
   microphone, voice detection, Whisper upload, Azure, the keyless backup
   voice, the spending ceiling, the playback queue
```

**What stays Vietnamese for good** — all of floor 3 for the course: the items,
the spaced repetition, the lesson order, tone pairs, the address system, the
numbers Whisper writes as digits, the bare-ASCII words `anh` and `em`. That is
the course; it is not shared and it is not touched.

**What becomes shared** — floor 1, which is everything learnt the hard way about
sound. None of it is Vietnamese, and Chinese gets it for free.

**The actual work is floor 2.** The Vietnamese profile already exists, but as
literals scattered through `voice.py` and `listen.py`. It is gathered into one
place, Vietnamese gets exactly today's values, and a Chinese profile is added
beside it. Recognising a Chinese word is easier than a Vietnamese one: a
character is unambiguous, a diacritic is not.

**One trap.** Several guards in `listen.py` were born from the course — "is the
learner attempting the word I asked for, or talking to me?". A free conversation
often has no expected word. They are kept, and run only when a programme hands
one over: the course always does, the Chinese programme will when it says
"repeat".

**One limit, known in advance.** When the model asks the learner to repeat,
nothing checks the tones. Whisper writes characters and picks the most likely
one, so a wrong tone will often still come back as the right word. Same problem
as Vietnamese — the free mode can ask for a repeat, not correct one.

## In what order

Through the ritual, one change at a time:

1. **`0031`** — the language profile exists, and the voice uses it.
2. **`0032`** — the ear uses the same profile.
3. **`0033`** — the free conversation, in its own folder `chinese/`.

The voice first because it can be tested without a microphone: give it a mixed
sentence and listen to who speaks.

**The guard for all three:** `smoke_test.py` passes without one of its
Vietnamese cases being edited. If one has to change, Vietnamese has moved, and
the work stops there.

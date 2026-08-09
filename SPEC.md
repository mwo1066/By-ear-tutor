# What the tutor does

Every behaviour, in plain language, with where it is enforced and what to edit
to change it. Written against the code, not from memory.

**Read the "where" column first.** It is the distinction that matters most and
the one that keeps causing confusion:

- **code** — a guarantee. The model cannot violate it.
- **prompt** — an instruction. The model follows it most of the time and
  forgets it the rest.

Putting a rule in the prompt when it could be code is how the tutor ended up
reciting ten steps in one breath and asking the same word four times running.
Leaving a rule in the prompt after moving it to code is how it ended up obeying
a marker nothing emitted any more.

---

## The two voices

### 1. Two speakers, routed by language
The tutor speaks the learner's language; Minh speaks only Vietnamese. Which
voice is heard is decided by which language a sentence is written in — the
model places no tags.
**Where:** code — `voice.split_by_voice` splits word by word
**Change:** `voice.py` → `TUTOR_VOICE`, `TEACHER_VOICE`

### 2. Stage directions and markdown are stripped
"Minh:" written as a label, or `**bold**`, never reaches the speakers.
**Where:** both — the prompt forbids them, `voice._strip_markdown` removes
them anyway
**Why both:** the code stops them being *heard*; only the prompt stops the
model *thinking* in bullet points, which flattens the teaching
**Change:** `voice.py` → `_SPEAKER_LABEL`, `_MARKDOWN_CHARS`

### 3. A Vietnamese word inside a tutor sentence goes at the end
Each voice switch costs a synthesis round trip, so one per sentence, at the
close.
**Where:** prompt
**Change:** `persona.toml` → THE TWO VOICES

---

## The shape of a turn

### 4. One instruction per turn
Before each turn the model is handed exactly one thing to do and nothing else.
It is never shown the rest of the plan.
**Where:** code — `build_plan` builds the list, `_lesson_note` reveals one step
**Why:** the model holds no state between turns. Asked to remember its position
in a cycle, it drifted every time.
**Change:** `tutor.py` → `build_plan`

### 5. A turn ends at its question
One question, then silence. Never answer your own question.
**Where:** prompt — THREE RULES
**Change:** `persona.toml` → rule 2

### 6. Three sentences maximum
After the opening turn. The learner must speak at least as often as the tutor.
**Where:** prompt — THREE RULES
**Change:** `persona.toml` → rule 3

### 7. A reply is capped at 500 tokens, reasoning kept low
Without a ceiling the model reasoned on a hidden channel until the budget ran
out and said nothing at all.
**Where:** code
**Change:** `tutor.py` → `MAX_TOKENS_PER_TURN`, `reasoning_effort`

---

## What gets taught, and in what order

### 8. The sequence is composed, never chosen
Items are taught in roster order. The model never picks what comes next and
never invents an item.
**Where:** code — `select_new` returns roster order, `pick_next_index` picks
**Change:** the order of items in `content/vietnamese/*.toml`

### 9. A phrase never arrives before its words
`tôi tên là` cannot be taught until `tôi`, `tên` and `là` have been.
**Where:** code — `pick_next_index` skips an item whose `pieces` are missing
**Why:** a session once opened on a five-word phrase, none of whose words had
been taught
**Change:** `content.py` → `pick_next_index`, and each item's `pieces` field

### 10. Each item carries its own teaching data
`gloss` ("I / me"), `kind` (atom or construction), `pieces`, `literal`.
**Where:** content — authored, not derived
**Why:** the code used to split the Vietnamese name into words and guessed
wrong both ways: "cà phê" looked like an assembly, a grammar rule looked like a
sentence. And without a gloss, "ask what là was" came out as "so how would you
say là?" — a question stating its own answer.
**Change:** the item files; `fill_item_metadata.py` backfills missing fields

### 11. A new word gets two turns
`introduce` then `settle` — revealed and heard, then reacted to and asked
again.
**Where:** code — `build_plan`
**Why:** with one turn each, three words went by in under a minute and none of
them landed
**Change:** `tutor.py` → `build_plan`

### 12. A construction runs the full chain
One recall per piece, one per turn, then the literal word order, then the
answer, then variations, then the rule named last.
**Where:** code — `build_plan`
**Change:** `tutor.py` → `build_plan`, `N_VARIATIONS`

```
atom          introduce -> settle -> rapidfire x3
construction  recall_piece (one per piece) -> scaffold -> answer
              -> vary x2 -> rule -> rapidfire x3
```

### 13. The rule is named after the pattern has been produced, never before
**Where:** code places the step last; prompt says how to phrase it
**Change:** `tutor.py` → `build_plan`

---

## How words come back

### 14. Every word carries a level
Level 0 on introduction, +1 on every recall. The chance of being drawn is
`1/(level+1)^1.5` — constant early, rare later, never zero.
**Where:** code — `srs.weight`, `srs.draw_recalls`
**Why:** measured on the reference course, nothing is ever "learned" and
retired; a word simply appears less and less
**Change:** `srs.py` → `DECAY`

### 15. Spacing counts in words met, never in days
The course is one continuous line you stop and resume. Doing thirty items in
one sitting or over a month gives the same lesson.
**Where:** code — nothing anywhere records a date
**Change:** `srs.py`

### 16. Wrong answers are not tracked
A missed word needs more exposure, which a low level already arranges.
**Where:** code — `record_recall` only ever increments
**Change:** `srs.py` → `record_recall`

### 17. Three bare recalls close every item
Drawn by level, excluding the item just taught and its own pieces.
**Where:** code
**Change:** `tutor.py` → `N_RAPIDFIRE`, `_recall_targets`

---

## Answers

### 18. The core move is "how would you say ___?", never "repeat after me"
The learner constructs from pieces they have. Only a brand-new word is ever
echoed back.
**Where:** prompt — THE CORE MOVE
**Why:** "repeat after me" appears zero times in twenty-five minutes of the
reference course; "how would you say" appears twenty-two times
**Change:** `persona.toml` → THE CORE MOVE

### 19. A recognisable answer is correct
"Toi" for tôi, a missing accent, a rough transcription: all correct. Confirm
and move on. Never re-ask the question just asked.
**Where:** both — `answered_target` decides, the prompt sets the tone
**Change:** `tutor.py` → `ANSWER_MATCH_THRESHOLD` (0.5)

> **Known broken.** `answered_target` receives the learner's turn with its
> `[lang:vi]` tag still attached, and strips it to `langvi` rather than
> discarding it. Six junk letters are prepended to every answer, so correct
> answers score as misses. Measured: `Đói` for tôi scores 0.33 instead of 0.67.

### 20. A genuinely different word gets one second chance
Minh says it, the question is re-asked differently, and then the lesson moves
on whatever the answer.
**Where:** code decides (`_should_retry`), prompt phrases it
**Change:** `tutor.py` → `_should_retry`

> **Known weak.** The retry has the tutor say the word and then ask for it, so
> the answer is given away. A guard in the code notices and logs it, but the
> instruction still asks for this. The right shape is probably "it was tôi,
> say it after Minh" — assume the miss, do not stage a question.

### 21. Any correct Vietnamese counts, not only the item's wording
"tên tôi là Nam" is not corrected into "tôi tên là Nam".
**Where:** prompt — WHEN THEY GET IT WRONG
**Change:** `persona.toml`

### 22. A real question replays the step instead of consuming it
So a scripted plan cannot steamroller the learner.
**Where:** code — `learner_asked_something`
**Change:** `tutor.py`

---

## Hearing the learner

### 23. Recording is hands-free
Starts on speech, stops after 1.2s of silence. No key is ever pressed.
**Where:** code
**Change:** `listen.py` → `TRAILING_SILENCE_MS`, `VAD_AGGRESSIVENESS`

### 24. Silence is trimmed before upload
Groq's transcription has no server-side silence filter, and Whisper invents
confident sentences out of near-silence.
**Where:** code — `_trim_to_speech`
**Change:** `listen.py` → `TRIM_PADDING_FRAMES`

### 25. Only Vietnamese and English are accepted
Anything else is re-transcribed forcing Vietnamese.
**Where:** code — `ALLOWED_LANGUAGES`
**Why:** a mangled Vietnamese attempt came back tagged French with French text,
and the tutor answered in French mid-lesson

> **Known broken.** A genuine English question mis-detected as French is forced
> into Vietnamese and destroyed. "How do you say dog in Vietnamese?" became
> "Cái cách nói đáy ở Việt Nam?" and the tutor taught the word for "bottom".
> Length is the free discriminator: one or two words is an attempt, a sentence
> is a question.

### 26. Transcription is never repaired
What was said is what the tutor sees.
**Where:** code — deliberately nothing does this
**Why:** two attempts were made and both removed. A vocabulary hint fed to the
decoder made Whisper invent Vietnamese out of pure noise. Snapping the text
onto the nearest known word repaired the mispronunciation the tutor is supposed
to hear.

---

## The opening

### 27. Three points, once, at the very start
Say things out loud; do not try to remember anything; follow along or ask for
your own topic. Then Minh says hello, then a question, then stop.
**Where:** both — code decides *when* (`lesson["started"]`), prompt says what
**Why:** an empty plan meant both "not started" and "finished", and the tutor
once opened a fresh session with "let's wrap up for today"
**Change:** `persona.toml` → OPENING

> **Known cost.** 55 seconds of synthesis before anything happens. `--no-intro`
> skips it while working on the lesson itself.

---

## Pronunciation

### 28. Pronunciation is not taught, and tones are not mentioned
Listen to Minh and copy him. No tone names, no articulation tips, no
descriptions of sounds.
**Where:** prompt — PRONUNCIATION
**Why:** the tutor never hears the learner, only a rough transcription, so any
verdict is guesswork — and it was inventing wrong ones ("tên" glossed as "the a
in bed")
**Change:** `persona.toml` → PRONUNCIATION

---

## Tools

### 29. Three tools, all rare
`set_session_focus` (the learner asks for a topic, four items get generated),
`remember_word` (they ask how to say something outside the course),
`deprioritize_item` (they ask to drop something — buried at level 12, never
deleted).
**Where:** code executes, prompt decides when
**Change:** `tutor.py` → `TOOLS`

> **Never yet fired.** `set_session_focus` has not triggered in any session.
> And generation produces whole sentences, which rule 9 will defer until their
> words are taught — possibly forever.

---

## Infrastructure

### 30. One model, no fallback
On a 429 the code waits and retries the same model.
**Where:** code
**Why:** every alternative breaks the format outright — one writes tool calls
as text the tutor reads aloud, one leaks internal tokens into tool names, one
fires unrelated tools with no speech
**Change:** `tutor.py` → `MODEL`

### 31. The budget is 8000 tokens a minute
Measured, not documented. At ~3000 tokens a request that is about two and a
half turns a minute, which is why the system prompt is kept small.
**Where:** Groq's free tier
**Change:** pay, or shrink `persona.toml`

### 32. Progress is written as the session goes
A crash costs nothing. `--fresh` writes nothing at all.
**Where:** code
**Change:** `tutor.py` → `run_session`

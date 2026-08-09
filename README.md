# by-ear tutor

A language tutor you talk to. Nothing is typed, nothing is read: it speaks,
your microphone opens on its own, and it stops recording when you go quiet.

It teaches Vietnamese today. The engine is language-agnostic — the language
lives entirely in `content/`.

## The method

Modelled on audio courses like Michel Thomas's and Paul Noble's, and on what
their transcripts actually show rather than on what they say about themselves.
Four things came out of measuring them:

**You build sentences, you don't repeat them.** The core move is "so how would
you say ___?", never "repeat after me" — a phrase that appears zero times in
twenty-five minutes of the reference course.

**Words are taught because a sentence needs them.** Nothing is introduced for
its own sake. `tôi`, `tên` and `là` arrive because `tôi tên là Nam` is about to
be built out of them, and the code guarantees a phrase never surfaces before
the words it is made of.

**The literal scaffold.** Before asking for a sentence whose word order differs
from yours, the tutor gives that order out loud — "literally you'll be saying:
I name is Nam" — which is what lets a beginner produce a sentence they have
never heard.

**Nothing is ever "learned" and retired.** Each word carries a level: fresh
words come back constantly, well-drilled ones rarely, and the odds never reach
zero. Spacing counts in words met, not in days or sessions, because the course
is one continuous line you stop and resume.

## How it works

The teaching sequence is decided in code, not by the model. Before each turn
the model is handed exactly one instruction — *introduce this word*, *ask what
that piece was*, *give the literal order and ask for the sentence* — and
nothing else. It supplies the wording, the warmth and the reaction to what you
just said. It never decides the structure.

That split exists because the model holds no state between turns. Left to
re-derive its position by re-reading the conversation, it drifted every time:
ten steps recited in one breath, the same word asked four times running, a
recall chain missing a piece.

Two voices carry the lesson, routed automatically by the language each sentence
is written in: yours-language for the tutor, Vietnamese for Minh, the native
teacher who only ever says the target word.

```
tutor.py       the lesson loop and the turn planner
content.py     the roster, and the rule that a phrase waits for its words
srs.py         word levels: how often each one comes back
voice.py       Azure text-to-speech, two voices, pipelined
listen.py      microphone, silence detection, Groq transcription
content/       the course itself: items and the tutor's persona
```

## Setup

Python 3.13+.

```bash
pip install numpy sounddevice webrtcvad
```

Create a `.env` file next to the code:

```
GROQ_API_KEY=...
AZURE_SPEECH_KEY=...
AZURE_SPEECH_REGION=northeurope
```

Groq runs both the tutor's brain and the speech recognition; Azure does the
two voices. Groq's free tier allows about 8000 tokens a minute for the model
used here, which works out to roughly two and a half turns a minute — enough
for a real lesson, tight enough that the system prompt is kept small on
purpose.

## Running

```bash
python tutor.py
```

Talk when it asks. Ctrl+C ends the session and saves your progress to
`state.json`.

```bash
python tutor.py --fresh --no-intro
```

Two flags for working ON the tutor rather than with it. `--fresh` starts from
the first word and saves nothing, so two runs are comparable. `--no-intro`
skips the opening speech — 55 seconds of synthesis standing between you and
whatever you are trying to test. Use both while iterating.

```bash
python smoke_test.py
```

Runs a whole session with the network unplugged, in about a second. Worth
running after any change: it catches the wiring breaks that otherwise only
show up several minutes into a real lesson.

```bash
python simulate_session.py 14
```

Replays a full lesson in text with a small model playing the learner, for
judging a pedagogical change without having to talk.

## Adding a language

Copy `content/vietnamese/`, replace the item files and the persona. Items are
listed in teaching order, and a construction should spell out the words it is
built from — `tôi tên là + [tên riêng]` is recognised as `tôi` + `tên` + `là`,
which is what drives both the recall chain and the ordering guarantee.

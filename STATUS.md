# Where the project stands

Last updated after the session that moved the teaching cycle into code.
`README.md` explains what the project is and how to run it; this file is the
working state — what holds, what is still open, and why certain things are the
way they are.

## What works

A full lesson runs end to end by voice. Measured on real sessions:

- the opening speech, then one teaching move per turn, no drift
- a new word gets two turns (`introduce`, then `settle`) instead of vanishing
  after one
- a construction runs its whole chain: one recall per piece, the literal
  scaffold, the answer, variations, the rule named last
- recall targets are drawn by level, so a fresh word comes back constantly and
  a drilled one rarely, without ever dropping out
- progress is written as the session goes, so a crash costs nothing

`python smoke_test.py` runs all of that with the network unplugged in about a
second. Run it after any change.

## The decision everything else follows from

The model holds no state between turns. Every time it was asked to remember
where it was in a cycle, it drifted — ten steps recited in one breath, the same
word asked four times running, a chain missing a piece, the lesson teaching one
item while the sequence sat on another. Each of those was patched with more
prose telling it to remember, which is a reminder aimed at something with no
memory.

So the structure lives in code and the model supplies only the words. Anything
the code can know, the code decides:

| decided in code | left to the model |
| --- | --- |
| which item comes next, and that a phrase never precedes its words | the wording, the warmth |
| what this turn is for — one instruction at a time | the hook, if there is a real fact to tell |
| which word a recall asks for | reacting to what the learner just said |
| when an item is finished | judging whether an answer was close enough |

The same reasoning removed the `next_item` tool: a tool call cost a whole extra
request before the model could speak again, about six seconds of dead air per
word, and a third of all requests produced nothing but a "let's continue"
filler.

## Open, in rough priority order

**The model drifts one turn behind, and it is no longer acceptable.** Decided
with Meo after a live session: told to introduce "tên", the tutor re-asked
"tôi" instead; it then introduced "tên" on the following turn, which is the
step where saying the word is forbidden, so the answer was given away. From the
learner's seat a Vietnamese word simply appears at random in the middle of a
drill. This is not the flexibility we were willing to pay for.

The agreed fix, not yet done: **the code writes the mechanical turns itself**.
A recall or a rapid-fire is one sentence -- "and again, what was I / me?" --
that the code can compose and send straight to speech, with no model call. It
then cannot skip the step, give away the answer, or fall a turn behind. The
model keeps introductions and reactions, where it earns its place. This also
halves the requests per lesson, which the 8000 tokens/minute ceiling makes
worth having on its own.

**The opening takes 55 seconds.** Worked around with --no-intro, not fixed. The
three points should survive in about six sentences.

**Style.** Meo's notes on how the tutor talks, still not started.

**Speech synthesis dominates the clock.** A teaching turn is ~10-15s, of which
~0.5s is the model. Everything else is Azure.

**`set_session_focus` has never fired**, and generation produces whole
sentences that the ordering rule will defer until their words are taught --
possibly forever.

**`tutor.py` is ~1000 lines and does five jobs.** Worth splitting once the
architecture stops moving.

## Constraints that shape decisions

**Groq's free tier is 8000 tokens/minute** for `openai/gpt-oss-120b`, measured,
not the 30k an old comment claimed. At ~3000 tokens a request that allows about
two and a half turns a minute. Exceeding it earns a Retry-After of a minute or
more. This is why the system prompt is kept small — it is pacing, not tidiness.

**No fallback model.** Every alternative breaks the format outright: one writes
tool calls as literal text that the tutor then reads aloud, one leaks internal
tokens into tool names and 400s, one fires unrelated tools with no speech. On a
429 the code waits and retries the same model. A pause is recoverable; a broken
lesson is not.

**Pronunciation is not taught.** The tutor never hears the learner — it gets a
rough transcription — so any verdict on their sound is guesswork. It was
inventing wrong ones ("tên" glossed as "the a in bed"). Tones are deferred
entirely; the instruction is listen to Minh and copy him.

**The microphone environment is noisy** and this is accepted, not fixed. The
VAD flags 60-75% of frames as speech and recordings run several seconds long
for a one-second answer.

## Things that turned out to be traps

Recorded because the same shape keeps recurring, not for history's sake.

**A fix can be orphaned rather than broken.** A `vad_filter` fix committed
weeks ago still existed, intact, on a code path nothing had called since Groq
STT became the default. It looked like protection and was not. The local
Whisper path has since been deleted for exactly that reason.

**Rules and code drift apart.** The prompt once obeyed a `TONS:` marker that
the code no longer emitted, and told the model to handle a third-language tag
that the code clamps before it ever arrives. Delete the rule and the mechanism
together or neither.

**A silent no-op is worse than an error.** Three separate fixes this session
were written as bulk string replacements whose patterns no longer matched.
Nothing failed, nothing applied, and each cost a round of live testing to
discover. Use something that raises when the target is missing.

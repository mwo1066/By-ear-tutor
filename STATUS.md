# Where the project stands

Last updated after the session that moved the mechanical turns into code.
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
- a simple word runs end to end without the model: the introduction, the second
  ask, the rapid-fire are all sentences the code writes and speaks itself, so a
  word is never revealed without the meaning in the same breath
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
| which item comes next, and that a phrase never precedes its words | how a word is introduced, and the warmth of it |
| what this turn is for — one instruction at a time | the hook, if there is a real fact to tell |
| which word a recall asks for, and the exact sentence that asks it | the scaffold, the variations, how a rule is put |
| when an item is finished, and whether an answer counted | replying to anything the learner says that is not an answer |

The same reasoning removed the `next_item` tool: a tool call cost a whole extra
request before the model could speak again, about six seconds of dead air per
word, and a third of all requests produced nothing but a "let's continue"
filler.

Taken to its conclusion, it also removed the model from the recall turns
entirely. It had been drifting a turn behind: told to introduce "tên" it
re-asked "tôi", then introduced "tên" on the step where saying the word is
forbidden, handing over the answer. A recall is one sentence whose two halves
the code already holds -- the meaning to ask from, and the word not to utter --
so it is composed here and sent straight to speech. It cannot skip a step, give
away an answer, or fall behind. Roughly half the turns of a lesson now cost no
request at all.

What was traded for it: the model no longer reacts to what the learner just
said on those turns. What survives is the verdict the code computed anyway,
spoken as the first few words ("That's it." / "It was tên.").

The introduction followed, and for a blunter reason. The note handed over said
in as many words: their answer was right, never tell them you did not catch it.
The model opened with "I didn't catch that", then had Minh say the new word and
asked for it — the sentence carrying its MEANING was never spoken. A word
appearing with nothing attached to it is not a lesson, and there is no wording
of an instruction that makes it certain. The one thing that turn was buying, an
optional line of real context, had fired zero times in every session logged.

## Open, in rough priority order

**A variation is bounded by a word list, which stops scaling somewhere.** The
`vary` instruction names what the learner already knows, so the model cannot ask
for a word never taught -- measured: without it, the model asked for "your name
is", i.e. bạn, which the roster teaches one item later. The list is only sent
below `MAX_LISTED_KNOWN_WORDS`; above it the instruction just says "nothing new",
which is a hope, not a guarantee.

The replacement, when it matters: send a DRAW instead of a list -- eight words
pulled from what they know, weighted by level, the same `draw_recalls` the
recalls already use. Bounded at any course size, always taught, and the
variation then recycles vocabulary that is due, which is what the method wants
anyway. Not worth doing at 55 items; the moment for it is the same moment the
word base grows.

**`vary` has been given a real instruction, and that is a test, not a fix.** It
was the thinnest step in the plan -- "same structure, one element swapped" and
nothing else -- and the only one that produced a turn with nothing in it. It now
names the sentence, the frozen shape, what may change (the person), and that
Minh stays silent. Deliberately NOT scripted: knowing that tôi/bạn/anh share a
slot is Vietnamese, which the model has and the roster does not encode. Watch
one session. If the empty turn comes back, script it -- and it will be because
asking properly was tried first, not skipped.

**Nothing knows the learner's name**, or anything else about them. Constructions
like "my name is ___" are at their best filled with something true. The model
reaches for this on its own today ("using your own name..."), which works;
storing it only becomes necessary if the code starts writing those sentences.

**Categories are free text and already inconsistent** at 55 items: `greeting`
and `greetings`, `introduction` and `introductions`, `rules` duplicating the
`kind` field, and "Je suis prêt" filed under `phrase`. Nothing depends on them
yet. Anything that later fills a hole by type will, and closing the set costs a
pass over 55 items now against 1000 later.

**Four construction glosses are grammar labels, not English**: `not be +
[noun]`, `want ___`, `do ... not?`, `negate verb with không`. Spec rule 10 says
a gloss is read aloud and is never a grammatical description; `check_roster`
only checks that it is non-empty. The tutor is currently instructed to announce
"they are about to build not be plus noun". Not reached in any session yet --
these constructions sit 3rd, 4th and 5th in the roster.

**The opening takes 55 seconds.** Worked around with --no-intro, not fixed. The
three points should survive in about six sentences.

**Style.** `STYLE.md` is the notebook: ideas land there and leave through one of three drawers -- a field on an item, a wording in code, or the prompt as a last resort -- with a test in front of each (how often does it occur in the reference course?). It is read by nobody at runtime, deliberately. Meo's notes still to come.

**Changes.** `changes/` holds one folder per change, written before the code and
read by Meo first: why, which spec rules move, what is in scope and what is
deliberately out. `/proposer` opens one, `/appliquer` implements it, `/archiver`
folds the delta into `SPEC.md` and files it under `changes/archive/`.
`changes/archive/JOURNAL.md` is the index -- read it before proposing anything,
it is where the already-tried-and-undone live. `/derive` is the separate audit:
re-read the code, report what `SPEC.md` claims and the code no longer does.

**Speech synthesis dominates the clock.** A teaching turn is ~10-15s, of which
~0.5s is the model. Everything else is Azure — and on a scripted turn it is
now the only thing on the clock at all.

**`set_session_focus` has now fired once, and it killed the session.** Asked for
a food-ordering lesson, it generated on the 500-token budget meant for three
spoken sentences, so the JSON came back truncated, Groq answered 400, the retry
loop sent the same doomed request five times, and the exception climbed out of
the tool handler and ended the lesson on its second turn. Four bugs in one line
of causation, all four fixed: its own token budget, a nullable schema for the
construction-only fields, no retry on a 4xx, and a lesson that survives a broken
tool. Generation now returns four usable items in 1.4s.

Still true underneath: generation produces whole sentences that the ordering
rule will defer until their words are taught -- possibly forever.

**`tutor.py` is ~1300 lines and does five jobs.** Worth splitting once the
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
for a one-second answer. What is no longer accepted is a turn where almost
nothing was said: under five speech frames nothing is uploaded, because Whisper
answers silence with an invented sentence rather than an empty one, and the
lesson scored it as a missed word.

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

**A fix that adds to a list will need adding to again.** The test that tells
the two apart: does the fix add a NUMBER, or an ENTRY? A number converges --
there is one value, you tune it once (`MIN_SPEECH_FRAMES`, `ENERGY_RATIO`,
`ANSWER_MATCH_THRESHOLD`). An entry does not: `_VN_BARE_WORDS`, the punctuation
a speaker label may end with, the "Wrong: … / Right: …" pairs in the persona
prompt. Those are blacklists, and a blacklist's contract is "everything, minus
what we happened to notice" -- it cannot finish.

Where a list is unavoidable, close it. "A line that is nothing but a speaker's
name" cannot grow, because the cast is two voices; "a name followed by one of
these signs" grew every session. Same bug, one shape ends.

Worth watching as a number: the count of Wrong/Right pairs in `persona.toml`.
If it climbs, instances are being fixed where a class was available.

**A recovery whose success test is too weak will accept garbage.** The second
transcription pass was kept whenever it contained the expected word -- so a
forced-Vietnamese hallucination that happened to contain "tôi" replaced a clear
English sentence from the learner, and was scored as a correct answer. The test
proved the wrong thing: "the word is in there" is not "this is what they said".
Whenever a fallback overwrites a primary result, ask what would make the
overwrite obviously wrong, and test for that too.

**A silent no-op is worse than an error.** Three separate fixes this session
were written as bulk string replacements whose patterns no longer matched.
Nothing failed, nothing applied, and each cost a round of live testing to
discover. Use something that raises when the target is missing.

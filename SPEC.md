# What the tutor does

Every behaviour, with the place it is enforced and what to edit to change it.
Written from the code, not from memory.

**The vocabulary of this file is defined in [`GLOSSARY.md`](GLOSSARY.md)** —
feature, atom, piece, scripted turn, gloss. Read that first if you are new to
the project.

**Read the "Where" line first.** It is the distinction that matters most, and
the one that has cost us the most:

- **code** — a guarantee. The model cannot violate it.
- **prompt** — an instruction. It follows it most of the time, and forgets it
  the rest of the time.

Putting a rule in the prompt when it could have been code is what produced a
tutor reciting ten steps in one breath and asking for the same word four times
running. Leaving a rule in the prompt after moving it into the code is what
produced a marker nothing emitted any more.

---

## The sections

| | what it answers |
| --- | --- |
| [The two voices](#the-two-voices) | who speaks, and in which language |
| [The shape of a turn](#the-shape-of-a-turn) | what a turn may do, and who writes it |
| [The order of the course](#the-order-of-the-course) | what comes after what |
| [What the course knows](#what-the-course-knows) | the data it holds — about items, about the learner |
| [Teaching a word](#teaching-a-word) | an `atom` |
| [Teaching a construction](#teaching-a-construction) | a `construction` |
| [Teaching a feature](#teaching-a-feature) | a `feature` |
| [How items come back](#how-items-come-back) | the level, the spacing, the recalls |
| [Answers](#answers) | how an answer is judged, and what is said about it |
| [Hearing the learner](#hearing-the-learner) | the microphone, the silence, the transcription |
| [The opening](#the-opening) | the very first turn |
| [Pronunciation](#pronunciation) | tones, and what we refuse to judge |
| [The tools](#the-tools) | the three calls the model may make |
| [Infrastructure](#infrastructure) | the model, the budget, saving |

The three "Teaching…" sections follow the three item kinds of
[`GLOSSARY.md`](GLOSSARY.md), in that order. Rule numbers are stable
identifiers: they do not renumber when a section moves.

---

## The two voices

### 1. Two speakers, routed by language
The tutor speaks the learner's language, Minh only Vietnamese. Which voice is
heard is decided by the language each phrase is written in — the model applies
no label of its own.
**Where:** code — `voice.split_by_voice` splits **word by word**, never on
whitespace-delimited chunks
**Why word by word:** this line of the spec was already right, the code was
not. It split on spaces, then classified a whole chunk from its first run of
letters. The model wrote "That's correct—là." with no space around the dash: a
single chunk, classified on "correct", so the English voice pronounced "là".
Punctuation is no longer a separator that has to be anticipated — it simply
follows the word before it, which holds for the dash, the slash, brackets, and
the ones we have not seen yet.
**Change:** `voice.py` → `TUTOR_VOICE`, `TEACHER_VOICE`, `_WORD_SPLIT_RE`

### 2. Stage directions and markdown are stripped
"Minh:" written as a label, or `**bold**`, never reaches the speakers. And **a
line containing nothing but a speaker's name is not spoken at all**, whatever
the punctuation around it.
**Where:** both — the prompt forbids it, `voice._strip_markdown` and
`voice.is_stage_direction` remove it anyway
**Why both:** the code stops it being *heard*, only the prompt stops the model
*thinking* in bullet points, which flattens the teaching
**Why "nothing but the name":** the old rule required a colon. The model wrote
"Minh: tôi." one session and "Minh." the next — the English voice announced
"Minh" before every one of the teacher's lines, twice. Adding the full stop
fixed that session and not the next one ("Minh —", "(Minh)"). The list of
punctuation is open; the list of **names** is closed, there are two voices.
**Change:** `voice.py` → `_SPEAKER_NAMES`, `_SPEAKER_LABEL`, `_MARKDOWN_CHARS`

### 3. A Vietnamese word inside a tutor sentence goes at the end
Every voice switch costs a synthesis round trip: one per sentence, and at the
end.
**Where:** prompt
**Change:** `persona.toml` → THE TWO VOICES

---

## The shape of a turn

### 4. One instruction per turn
Before each turn the model is handed exactly one thing to do. It never sees the
rest of the plan.
**Where:** code — `build_plan` builds the list, `_lesson_note` reveals one step
of it
**Why:** the model holds no memory between turns. Asked to remember where it
is, it drifts every time.
**Change:** `tutor.py` → `build_plan`

### 4b. Mechanical turns are written by the code, with no model call
A step is written here as soon as the code holds **both halves**: the meaning to
ask from (`ask`, drawn from the `gloss` alone) and the word that must not be
said (`target`). It is composed and sent straight to speech synthesis. If one
half is missing, the model takes the turn back — it is a guard, not a list of
exceptions.

Six of the nine step kinds meet the condition: `recall_piece`, `rapidfire`,
`settle`, `introduce`, `scaffold`, `apply`. The last two only when they have
what they need — a scaffold with no literal order, an application with no
sentence to ask for, and the turn goes back to the model.

Three always stay with the model: `answer` (reacting to the sentence just
produced), `rule` (naming the pattern) and `vary` (asking the same sentence of
someone else). What has to be invented.
**Where:** code — `scripted_turn` composes, `_speak_scripted_turn` speaks
**Why:** the model was one turn behind. Real session: told to introduce "tên",
it asked for "tôi" again; it introduced "tên" on the following turn, the one
where saying the word is forbidden — the answer handed over before the
question, and a Vietnamese word surfacing at random in the middle of an
exercise. A sentence composed here can neither skip its step, nor give away its
answer, nor fall behind. It also halves the number of requests per lesson.
**Why the list grew:** `introduce` and `scaffold` arrived afterwards, each for
having said the Vietnamese on the turn that forbids it. The scaffold asked "can
you say the full sentence tôi tên là…" — that is, the answer — while its
instruction had said "say no Vietnamese" all along. An instruction the model
breaks on the very step it protects is the definition of a rule to move into
the code.
**Guarantee:** the question is built from the `gloss` alone, never from the
Vietnamese name — so a scripted recall cannot contain its own answer.
`smoke_test.py` checks it on every run.
**Accepted cost:** we lose the reaction to what the learner just said. What
remains of it is the code's verdict (18c), placed at the head of the sentence.
**Change:** `tutor.py` → `SCRIPTED_KINDS`, `_REPEAT_ASK`, `_ACK_CORRECT`

### 4b-bis. Saying "I forgot" always earns the answer
"I forgot", "no idea", "dunno" — the turn goes back to the model, which gives
the word, has Minh say it once, and says it will come back later.
**Where:** code — `learner_gave_up`
**Why:** on a recall step, the retry already gave the word. But on a step
written by the MODEL (rule, scaffold, variation) the code does not know what was
asked, so it can neither judge nor give it back. Real session: "I forgot" is two
words, below the threshold of 4c, so the lesson carried on as if nothing had
been said.
**Accepted:** it is a list, and this project distrusts lists. It is kept because
it is closed by something other than the code — there are only finitely many
ways to say you do not know, and it does not grow when a model invents a
phrasing. If it starts growing, that is the signal to find the property
instead.
**Change:** `tutor.py` → `_GAVE_UP`

### 4c. A learner who really speaks hands the turn back to the model
A question, or **two words of English or more**: the turn goes back to the
model, even if the step was mechanical. A scripted sentence only knows how to
ask its question.
**Where:** code — `learner_spoke_freely`
**Why:** it is also the only path left to the tools (29) — all of them fire on
something the learner said.
**Why two and not three:** it has to meet rule 25 at the same number. The ear
now keeps two words of English intact, and this side ignored anything under
three — so *"hold on"*, *"go back"*, *"too fast"*, *"start again"* were rescued
from being translated and then answered by nobody. *"I forgot"* escaped only by
being in `_GAVE_UP`, a list standing in for a property that was available.
**Change:** `tutor.py` → `FREE_SPEECH_WORDS` (2)

### 4c-bis. And the step is not consumed — twice at most
The turn answers the learner, then the lesson **returns to the same step**. On
the third pass it moves on regardless.
**Where:** code — `MAX_STEP_WAITS` (2), the lesson's `waits` counter
**Why:** the turn did go back to the model, but the step was counted as done.
Real session: "I have a question. I don't understand Tentoylannam." — the
question got its answer, the step was marked missed, and the tutor moved on to
an unrelated word. Handing the turn over without keeping your place amounts to
punishing whoever asks a question.
**Why a ceiling:** without it, someone chatting never leaves the first step. Two
waits, then the lesson advances.
**Change:** `tutor.py` → `MAX_STEP_WAITS`

### 4d. The opening turn always belongs to the model
Whatever the plan says. With `--no-intro` an item is already loaded, and its
first step would open the session with a bare question to someone who has just
said hello.
**Where:** code — `_conversation_loop`, `turns_done > 0`

### 5. A turn ends on its question
One question, then silence. Never answer your own question.
**Where:** prompt — THREE RULES
**Change:** `persona.toml` → rule 2

### 6. Three sentences maximum
After the opening turn. The learner must speak at least as much as the tutor.
**Where:** prompt — THREE RULES
**Change:** `persona.toml` → rule 3

### 7. A reply is capped at 500 tokens, reasoning at its lowest
Without a cap the model reasoned on a hidden channel until its budget ran out,
and said nothing at all.
**Where:** code
**Change:** `tutor.py` → `MAX_TOKENS_PER_TURN`, `reasoning_effort`

---

## The order of the course

### 8. The sequence is composed, never chosen
Items are taught in roster order. The model never picks what comes next and
never invents an item.
**Where:** code — `select_new` returns roster order, `pick_next_index` serves it
**Change:** the order of items in `content/vietnamese/*.toml`

### 9. A sentence never arrives before its words
`tôi tên là` cannot be taught before `tôi`, `tên` and `là`.
**Where:** code — `pick_next_index` skips an item whose `pieces` are missing
**Why:** a session had opened on a five-word phrase, none of whose words had
been taught
**Change:** `content.py` → `pick_next_index`, and the `pieces` field of items

### 9b. Grammar is spread, never stacked
After a feature, **four items** must pass before another one may come. And never
more than **three items of the same category** in a row. Nothing is dropped:
whatever cannot come waits its turn.
**Where:** code — `MIN_ITEMS_BETWEEN_FEATURES` (4), `MAX_SAME_CATEGORY_RUN` (3),
but the guarantee depends on the `category` field **written in the content**
**Why:** a file holds one topic and file order is teaching order, so a whole
file comes out as a block. Measured: **nine features in a row** around item 35 —
nine minutes of theory without a new word. Then, after the number system was
written, **eleven numerals in eleven consecutive slots**: a quarter of an hour
of counting and nothing else.
**Why in code and not by hand:** spacing by hand does not survive 2000 words.
**What it demands of the content:** a correct `category` on every item. A wrong
or empty category makes the spacing blind to that item.
**Change:** `content.py` → `MIN_ITEMS_BETWEEN_FEATURES`, `MAX_SAME_CATEGORY_RUN`

### 9c. A feature that names what it follows jumps the spacing
The `after` field carries the name of an **item**. Until that item is taught the
feature waits; as soon as it is, the feature goes **ahead of every spacing
rule**, 9b included.

**Most often it is a word**, and the feature finishes that word. But a feature
can name **another feature**, and that is how an order between two rules becomes
a guarantee instead of an accident: "verbs never change" raises a question, `đã`
answers it, and the second declares that it follows the first. Both were
attached to the same word and arrived in the right order by file order — a
content reshuffle would have handed over the answer before the question, with
nothing to flag it.
**Where:** code — the `attached` branch of `pick_next_index`; the `after` field
is **written in the content**, on 13 of the 35 features
**Why bypass the spacing:** the spacer exists to stop features clustering. A
feature attached to a word is not clustering — it is **finishing** the word. The
bypass is the field's intent, not a side effect.
**The guard:** an `after` naming no existing item is reported at startup.
Without it a typo makes the item wait out the whole course without a word of
complaint — nothing checked this field until it was used to chain two rules.
**Change:** the `after` field of items; `content.py` → `pick_next_index`,
`check_roster`

## What the course knows

### 10. Every item carries its own teaching data
`gloss` ("I / me"), `kind` (atom or construction), `pieces`, `literal`.
**Where:** content — written by hand, not inferred
**Why:** the code split the Vietnamese name into words and got it wrong both
ways — "cà phê" passed for an assembly, a grammar rule for a sentence. And with
no gloss, "ask what là was" came out as "so how would you say là?": a question
that gives its own answer.
**The `gloss` is now spoken as written** on scripted turns (4b), with no model
between it and the synthesis: `speakable` translates what is written but not
said — "I / me" → "I or me". And `check_roster` refuses an item carrying its own
Vietnamese name inside its gloss, which would hand over the answer at the moment
of the question.
**The accepted fallback, and its risk:** when an item has no gloss, two places
fall back to `description` — the authoring notes, written **in Vietnamese** for
whoever writes the content. No taught item has an empty gloss today, so nothing
triggers it. But it is the latent form of a defect already fixed once elsewhere:
`_lesson_note` opened every turn on that same description, and fragments of
Vietnamese came back out in the middle of sentences that had to be English.
**Carried but never read:** `type` (`concept`/`procedure`) on all 2085 items,
`senses` and `frequency_rank` on the 1915 of the stock. None drives a teaching
decision — keeping them costs nothing, relying on them would be a mistake.
**Change:** the item files; `fill_item_metadata.py` fills the missing fields;
`tutor.py` → `speakable`, `_ask_for`

### 11d. A compound word is asked for its halves before it is handed over
When a word is made of two or more words the course **already teaches**, one
recall per part comes first, then the hook, then the word.
**Where:** code — `build_plan`, the atom branch; the parts come from
`derive_pieces`, which already read them
**Why:** `không sao` carries a hook saying *"it is the word for not, and the word
for why, side by side"* — naming two words the learner has, and asking for
neither. The fact was handed over where it could have been produced, which is the
course's central move used backwards. Meo, hearing it: *ask me what "not" is
first.*
**The condition is strict, and that is the point:** the parts must reconstruct
the word exactly and every one of them must already be taught. **24 of the
course's 25 compounds have a half it does not teach** — `sân bay` is `sân` (yard)
+ `bay` (to fly) and neither is on the roster — so asking would ask for a word
that does not exist. Measured after the change: one item gained recalls,
twenty-four are untouched.
**What it is worth later:** across the 2065 words in the files, **893 are
compounds and 411 have every part present**, 242 of them already ordered after
their parts. So this fires once today and has room for hundreds, without a single
new word being added.
**Change:** `tutor.py` → `build_plan`, the atom branch

### 10c. A blank in a gloss sits at the END, and the question trails into it
`speakable` drops a trailing blank rather than filling it, so "My name is ___"
is asked as *"So, my name is…?"*. A blank anywhere else still has to be filled
with a word, or the sentence collapses.
**Where:** code — `speakable`, `_GLOSS_TRAILING_BLANK`; content — where the
glosses are written
**Why:** the blank used to become the word "something", and the result was heard
in a simulated lesson on 2026-08-17: *"And My name is something — what was
that?"* and *"I am something years old"*. The first reads as asking whether the
name IS "something".
**Why it is a content rule and not only a substitution:** English word order
forces the blank into the middle of "I am ___ years old", and no rewording moves
it. That gloss carries a number instead — "I am twenty years old" — while the
slot stays in the item's name, `Tôi ... tuổi`, which is what the code reads.
**Enforced, not remembered:** `check_asked_glosses_trail_into_their_blank` fails
any gloss that becomes a question with words after its blank, and prints what it
would have been spoken as. Two glosses had drifted, and one of them was written
into `personal_items.json` by a live session rather than by hand — which is the
argument for a check over a convention.
**Change:** `tutor.py` → `speakable`, `_GLOSS_TRAILING_BLANK`;
`smoke_test.py` → `check_asked_glosses_trail_into_their_blank`

### 10b. The course knows who the learner is, and teaches THEIR person-words
An age bracket and a gender are enough: they decide whether the learner is
`anh`, `chị` or `em` facing someone. The profile supplies the address
situations used by variation (12d) and by address features (13d) — and with no
profile, the code falls back on the situations the course teaches.
**Where:** code — `learner.py`, `learner.json`, read by `build_plan`
**Why:** the course taught `tôi`, whose own entry says *"đúng ngữ pháp nhưng
lạnh"* — grammatically correct, but cold. Then `anh`/`chị`/`em` in the abstract,
as a table to memorise. As soon as the course knows who you are, it stops being
a rule: they are **your** words.
**The accepted limit:** address depends on BOTH people. Knowing who the learner
is is necessary, not sufficient — but "with someone younger, you are `anh`" is
already infinitely more concrete than the general rule.
**Change:** `learner.py` → `SELF_WHEN_OLDER`, `pair_with_minh`, `address_rows`

## Teaching a word

### 11. A new word gets two turns
`introduce` then `settle` — revealed and heard, then reacted to and asked for
again.
**Where:** code — `build_plan`
**Why:** with a single turn each, three words went past in under a minute and
none of them landed
**Change:** `tutor.py` → `build_plan`

### 11b. A word is never revealed without its meaning in the same sentence
"In Vietnamese, the word for *name* is **tên**." — the meaning and the word in
one breath, the sentence ending on the word (so Minh says it), the word
repeated, then they are asked to say it.
**Where:** code — `_INTRODUCE`, composed by `scripted_turn`
**Why:** it was an instruction, and it gave way. Real session: told to introduce
"tên", the model said "I didn't catch that", had Minh say the word, then asked
for the word. **The sentence carrying the meaning was never spoken.** A first
contact with a word without its meaning is not a lesson.
**What is lost:** the optional context sentence ("only if you have a true fact
worth telling"). It was produced **zero times** across every logged session — we
were paying the turn's guarantee for an ornament never delivered.
**Change:** `tutor.py` → `_INTRODUCE`

### 11c. A true fact about the word comes BEFORE its presentation
When an item carries a `hook`, it is said first, then the sentence giving the
word. The fact earns the word, then the word lands.
**Where:** code — `scripted_turn` puts `step.hook` at the front; the `hook`
itself is **written in the content**, one item at a time
**Why in front and not behind:** on `phở` or `cà phê` the presentation sentence
alone runs empty — it announces to someone who already knows the thing that the
Vietnamese word is the one they are about to hear.
**What it demands of the content:** a **true** fact. The annotation instruction
says "never guess"; an invented etymology spoken aloud is worse than no hook at
all. Today one item of the course carries one.
**Change:** the `hook` field of items; `fill_item_metadata.py` for the
instruction that has them written

## Teaching a construction

### 12. A construction is CLIMBED, it is not asked for whole
One recall per piece, one per turn. Then the sentence is climbed in **rungs** —
one element more each time, staying on the same sentence — the last rung being
the whole sentence, with the literal order if it has one. Then the answer, the
variations, and the rule named last.
**Where:** code — `build_plan`; the **content** of each rung is left to the
model
**Why climb:** it is the reference method's move, caught in session — "how do
you say *don't want*, then *I don't want*, then *I don't want to eat*". Asking
for four words in one block from someone who has just met the three pieces
separately is making them scale what they could have climbed.
**Why the model and not the code:** `pieces` gives `tôi`, `tên`, `là` and does
not say that `tôi tên` is not a sentence. Which rungs exist is Vietnamese
knowledge — the code supplies the boundary (stay on the same sentence, use only
taught words, every rung must be sayable), the model supplies the rungs. Same
division as variation (12c).
**The number of turns does not move** for a construction of three pieces or
fewer: the rungs are taken out of the variation budget, because **climbing IS a
variation**. Beyond three pieces one turn is added — six items of the course —
rather than dropping the last variation, which carries the person swap (12d).
**Change:** `tutor.py` → `build_plan`, `N_VARIATIONS`

Stars mark the turns the code writes itself (4b); the others go to the model.

```
atom          introduce* -> settle* -> rapidfire* x3      (fully scripted)
construction  recall_piece* (one per piece) -> scaffold x1-3 (the rungs)
              -> answer -> vary -> rule -> rapidfire* x3
```

A simple word therefore no longer goes through the model at all. It keeps the
construction chain — scaffold, variations, rule — and every turn where the
learner really speaks (4c).

### 12b. A turn that asks for an answer and gives it is reported
Detection only: the reply is streamed and spoken as it arrives, so by the time
it can be judged it has been heard. What it buys is knowing.
**Where:** code — `_leaked_target`, on model turns only
**The placeholder was the hole in the guard:** a construction's target is
`tôi tên là + [tên riêng]`, and nobody ever says "plus bracket tên riêng". The
literal comparison could therefore **never** match — the guard has not fired
once on a construction since it existed, and "Tôi tên là Nam." said on a step
that forbids it went past without a word in the logs. What is compared now is
the fragments actually spoken, all of them required.
**Change:** `tutor.py` → `_PLACEHOLDER`, `_target_fragments`

### 12c. A variation changes the person, not just the word in the blank
"tôi tên là Nam" → "bạn tên là…". Swapping the given name tests nothing;
changing the person tests whether the pattern was understood.
**Where:** prompt — the `vary` instruction, built by `build_plan` from the
item's `gloss` and `literal`
**Why it stays with the model:** to swap `tôi` for `bạn`, the code would have to
know those two occupy the same slot. `pieces` does not say so, and neither does
the category — `function_word` also holds "gì" and "chào", and permuting inside
it yields "chào tên là". That knowledge is Vietnamese: it is what the model has
and a table does not. The exact opposite of recalls, where the code knew
everything and the model drifted.
**What the instruction supplies:** the boundary, not the words — the sentence
(`gloss`), its frozen shape (`literal`), what is allowed to move, and Minh's
silence.
**Why it was rewritten:** the old one said "same structure, one element swapped"
and nothing else. Real session: the model removed "tên" from "tôi tên là" to
produce "tôi là", then asked about "I am ___". That was not noise — it was the
right *kind* of variation, on a different sentence from the one being taught.
Nothing had told it what must stay.
**Change:** `tutor.py` → `build_plan`, `vary` branch

### 12d. A sentence containing a person is varied BY interlocutor
`tôi tên là` and `bạn tên là gì?` carry an address term. Their variation is not
"swap a word" but "say it to someone else", and the step names the situation out
loud.
**Where:** code — `has_person_slot` detects, `address_situations` supplies the
four rows, the `vary` instruction passes them on
**The table was already in the content:** the rule `cách chọn từ xưng hô`
carries its four situations in a `steps` field that `Item` **did not load**. The
data existed, nobody could read it — so the model reinvented, and it offered
"your name is" (that is, `bạn`) one item before the course teaches it.
**Found by content, not by name:** the address rule is the one carrying `steps`
mentioning an address term. Hard-coding the item's name would have broken at the
first content reshuffle — there were two of those in one day.
**Change:** `content.py` → `ADDRESS_TERMS`, the `steps` field of items

### 13. The rule is named after the pattern has been produced, never before
**Where:** the code puts the step last; the prompt says how to word it
**Change:** `tutor.py` → `build_plan`

*(The word "rule" here means the step that names the pattern at the end of a
construction — the plan's `rule` step. The **item kind** is no longer called
that: it is `feature`, see the features below.)*

---

## Teaching a feature

The third item kind, alongside the single word (11) and the construction (12).
**35 items of the course**, the second most numerous kind. They are neither
words nor sentences: subject-verb-object order, the fact that a verb never
conjugates, `ạ` making anything polite, the tones you listen to and copy,
politeness living in the person-word rather than in the tone of voice.

**Name in the code:** `kind = "feature"` — a **typological feature**, in the
sense the WALS atlas catalogues them. Their nature is written
`nature = "discrete"` or `"strand"`. See `GLOSSARY.md`.

### 13b. A feature has its pieces recalled one at a time, then assembled
The same shape as a construction: one recall per piece (up to
`MAX_FEATURE_PIECE_RECALLS`, 3), then **one** application step asking for them
to be put together.
**Where:** code — the `item.kind == "feature"` branch of `build_plan`
**Why:** a feature got ONE turn, which had to state the thing, illustrate it and
apply it in one breath — then the plan moved on to unrelated recalls. Measured
sequencing: feature → rapidfire `anh` → rapidfire `em` → rapidfire `tên`. Stated
once and never used again, which is exactly what a learner reported: "I
understood nothing about the rule, and it is not even used". Every other kind
gets several turns on the thing being taught; this one alone had a single turn.
**Deliberate side effect:** the piece recalls are scripted (4b), so two of a
feature's three practice turns no longer go through the model.
**Change:** `tutor.py` → `MAX_FEATURE_PIECE_RECALLS`, the `feature` branch

### 13c. The code chooses the sentence a feature is applied to
Among the constructions already taught, the one sharing **the most pieces** with
the feature. If none shares any: the feature's own words are the material. If it
has none: the list of known sentences, and the model picks one.
**Where:** code — the `related` sort, by descending count of shared pieces
**Why this is not the model's call:** asking for "a different sentence" was an
instruction, and it was ignored three turns running — the feature's turn asked
"how would you answer Bạn muốn ăn?", then both applications asked exactly the
same again. The learner heard one question four times and the session ended
there. Whether two sentences differ is not a judgement, so it is not the
model's to make.
**Why "the most" and not "the first":** the yes/no question feature (`có`,
`không`) was pinned to `không phải là + [danh từ]`, which shares only `không`
and is about negation — all three applications asked for "not a student" while
what was being taught was how to ask a question. The construction sharing both
pieces was waiting further along the course.
**Why the own words as a fallback:** with no shared sentence, we handed the list
to the model — and to show that an adjective needs no `là`, it chose "I am not a
student", a noun, which REQUIRES `là`. The application demonstrated the opposite
of what it was teaching. Naming the words to assemble cannot do that.
**Change:** `tutor.py` → the `feature` branch, the `related` sort

### 13d. A feature that is ABOUT address terms is posed as a situation
Never as a phrase. "Someone older than you, a man — how do you say it to them?"
Three rungs: the easiest person, an entirely different one, then a third where
the learner picks the person-word themselves. **No Vietnamese is spoken**:
naming it hands over the whole answer.
**Where:** code — `about_address`, then three `apply` steps and an immediate
return
**Why:** "How would you say anh ấy?" — the question that states its own answer.
The two features concerned, `ấy` and `ơi`, had the same defect.
**Why a narrow test:** "contains a person-word" was too broad — word order
(`tôi, uống, cà phê`) and possession (`của, cà phê, tôi`) use one as mere
example material without being about it. They would have been asked as "call
this kind of person", which is nonsense. The test is therefore: **at least two**
address pieces, **and** at least half the pieces. A single person-word is an
example, not a subject — which is what `tôi, là` is doing in the tone feature.
**What it costs:** this path leaves the plan immediately. An address feature
therefore gets neither piece recalls (13b) nor closing recalls (17).
**The situations come from the learner profile**, not from a fixed table.
**Change:** `tutor.py` → `about_address`, `ADDRESS_TERMS` in `content.py`

---

## How items come back

### 14. Every word carries a level
Level 0 at introduction, +1 on each recall. The chance of being drawn is
`1/(level+1)^1.5` — constant at first, rare later, never zero.
**Where:** code — `srs.weight`, `srs.draw_recalls`
**Why:** measured on the reference course, nothing is ever "learned" and then
retired; a word simply appears less and less
**Change:** `srs.py` → `DECAY`

### 15. Spacing is counted in items met, never in days
The course is one continuous line you interrupt and resume. Thirty items in one
go or spread over a month give the same lesson.
**Where:** code — nothing anywhere records a date
**Change:** `srs.py`

### 16. Wrong answers are not counted
A missed word needs more exposure, which a low level already arranges.
**Where:** code — `record_recall` only increments
**Change:** `srs.py` → `record_recall`

### 17. Bare recalls close almost every item — in a variable number
Drawn by level, excluding the item just taught and its pieces. Their **number**
varies from 1 to 4: a base that follows what the item has just made the learner
say, plus or minus one. **One of those slots may land on a `discrete` feature**
(17b); the others stay words.
**Where:** code — `rapidfire_count`
**Why variable:** fixed at three, every simple word cost exactly five turns, and
an attentive learner learns the cadence — after the second recall one is left.
They answer the rhythm rather than the question. `draw_recalls` already refuses
to be predictable about WHICH words come back; the same argument had never been
applied to HOW MANY.
**Why motivated and not random:** the base answers a single question — has this
item already made the learner speak? A construction has had every piece said
back, so the revision is done: stacking three more is repetition with no object
(**1** with pieces, **2** without). A feature has its own said back before
assembling them, so the same (**2**). A single word has revised nothing (**3**)
— and that is also the average measured on the reference course.
**What the feature's 2 corrects:** it was 4, from when a feature made nothing be
said at all. Since it carries its own recalls and its applications, four
unrelated recalls on top made it the longest item in the course with nothing
more learned.
**The exception:** an address feature (13d) gets none — its plan stops at its
three situations.
**What it does NOT change:** how often a given word is revised. An item's
recalls are about OTHER words — the current item is excluded. A word comes back
through the plans of following items, drawn by level, indefinitely (14).
**Change:** `tutor.py` → `rapidfire_count`. `N_RAPIDFIRE` carries the single
word's base, that is, the measured average; the construction's and the feature's
bases are written literally beside it, because they follow from what the item
has just made the learner say and not from a measurement.

### 17b. A feature comes back, as an application
A `discrete` feature enters the draw on the same footing as a word, weighted by
the same level. When it comes out, the step emitted is an **application** — a
sentence to produce — and never a bare recall.
**Where:** code — `drawable` decides who can be drawn, `build_plan` picks the
shape of the turn, `MAX_APPLICATIONS_PER_ITEM` (1) caps it
**Why:** measured over a whole course, **33 features out of 33 were never seen
again**, final level 0, against 4.5 for words. A fifth of what is taught was
taught exactly once. A learner said it: "I understood nothing about the rule,
and it is not even used".
**Why an application and not a recall:** nobody recites a rule. You cannot
**re-ask** a feature, you can **re-apply** it — and the turn already existed, it
only ever fired at introduction.
**Three words not to confuse:** `is_teachable` (can a lesson be built from it?),
`askable` (can it be the bare question of a recall?), `drawable` (can it fill a
slot, in one form or another?). A feature is the third without being the second,
and that confusion is what had excluded it.
**`strand`s are never drawn:** they fire from the material — a word has a tone
twin, a sentence contains a person — so drawing them would ask for a second,
worse copy of what is already running.
**The level rises without judgement.** An application asks for a whole sentence:
there is no target to compare against, and having the model judge would hand
back a decision the code has taken. So it is the **exposure** that is counted.
And it is not optional: `weight(0)` is thirteen times `weight(4.5)`, so a
feature left at zero would be drawn forever in preference to every word.
**Why the cap of one:** an application is a long turn where a recall is one
word. Simulated on a close of three with features fresh, **86% of closes would
carry two applications or more and 44% would carry three** — the exact shape of
the defect 9b prevents. At equilibrium it falls to 8%, so the cap protects the
first weeks above all, and costs little afterwards: one application fewer per
feature over 120 items, a gap of 22 items instead of 17.
**Measured after:** median feature level **4**, against 4 for words — words drop
from 5 to 4, which is the price paid and it is accepted.
**Change:** `content.py` → `drawable`; `tutor.py` → `MAX_APPLICATIONS_PER_ITEM`

---

## Answers

### 18. The central move is "how would you say ___?", never "repeat after me"
The learner builds from pieces they have. Only a brand-new word is repeated as
such.
**Where:** prompt — THE CORE MOVE
**Why:** "repeat after me" appears zero times in twenty-five minutes of the
reference course; "how would you say" appears twenty-two times
**Change:** `persona.toml` → THE CORE MOVE

### 18b. Re-asking the same word is said short, and marked as a repeat
"And again, what was *I or me*?" — not the full question a second time. Four
phrasings rotate, never the same one twice running.
**Where:** code — `_REPEAT_ASK`, the sentence composed by `scripted_turn` (4b)
**Why:** three goes at "What's the Vietnamese word for I or me?" in a row sound
like three different questions, and the learner hunts for what they missed. It
is also the reference course's signature: "and again, what was ___?" occurs
twenty-one times there.
**Change:** `tutor.py` → `_REPEAT_ASK`, `_pick`

### 18c. The tutor learns from the code whether the answer was right
The verdict is computed by the code, then passed to the model with the next
turn's instruction: "correct", "missed twice", or nothing.
**Where:** code — `lesson["verdict"]`, read by `_lesson_note` (model turn) or by
`_acknowledgement` (scripted turn, where it becomes the first words spoken)
**Why:** without it the model judges again on its own from the raw
transcription and contradicts the code. Seen in session: three turns running
where the word's level went up and the tutor said "I didn't catch that" in the
same breath.
**What the scripted turn says about it, word for word:** on a word **missed
twice**, the Vietnamese is given back — "It was ngon." — in its speakable form,
the same one the retry uses. On a **correct answer**, a bare acknowledgement:
"That's it.", "Exactly." — **the word is not said back**. And nothing at all if
the question that follows asks for precisely that word: the leak guard decides
that, not a second rule written beside it.
**Change:** `tutor.py` → `_lesson_note`, `_acknowledgement`, `_ACK_CORRECT`

### 19b. One letter, or one letter in common, is not enough
Below three letters the target demands a tighter match (0.60), and a
single-character answer is refused whatever its score.
**Where:** code — `SHORT_TARGET_LETTERS`, `SHORT_TARGET_THRESHOLD`
**Why:** `difflib` is coarse on short strings. Against a two-letter word,
sharing ONE scores exactly 0.50 and clears the threshold. Seen in session: "Dạ"
accepted for "là", level pushed to 7 — the learner had said something else and
the word was recorded as consolidated. And "D" was worth "đi", at the same score
as a genuine "Đôi" for "tôi".
**The threshold sits in the gap, not on its edge:** 0.50 must fail, 0.667 must
pass. 0.67 refused "Đôi" by a hair.
**Change:** `tutor.py` → `SHORT_TARGET_THRESHOLD`

### 19. A recognisable answer is correct
"Toi" for tôi, a missing accent, an approximate transcription: all of it is
right. Confirm and move on. Never re-ask the question you have just asked.
**Where:** both — `answered_target` decides, the prompt sets the tone
**Change:** `tutor.py` → `ANSWER_MATCH_THRESHOLD` (0.5)

### 20. A genuinely different word earns exactly one second chance
Minh says it again, the question is re-asked short, then the lesson moves on
whatever the answer.
**Where:** code end to end — `_should_retry` decides, `scripted_turn` writes the
sentence ("Listen again — tôi. And again?")
**Change:** `tutor.py` → `_should_retry`, `_RETRY_ASK`

> **Weak, and known.** The retry has Minh say the word and then asks for it: the
> answer is given before the question. The right shape would be "it was tôi,
> repeat after Minh" — owning the miss instead of staging a question. It used to
> be an instruction the model interpreted; it is now a single line of code, so a
> single line to change.

### 21. Any correct Vietnamese counts, not only the item's own phrasing
"tên tôi là Nam" is not corrected into "tôi tên là Nam".
**Where:** prompt — WHEN THEY GET IT WRONG
**Change:** `persona.toml`

### 22. A real question replays the step instead of consuming it
So that a scripted plan cannot roll over the learner.
**Where:** code — `learner_asked_something`
**Change:** `tutor.py`

---

## Hearing the learner

### 23. Recording is hands-free
Starts on speech, stops after 1.2 s of silence. No key, ever.
**Where:** code
**Change:** `listen.py` → `TRAILING_SILENCE_MS`

### 23b. A frame is speech if the detector AND the loudness agree
The loudness threshold is measured continuously — the 20th percentile of the
last three seconds is the room noise, and a frame has to beat it by a factor of
three.
**Where:** code — `_speech_threshold`, in the recording callback
**Why:** measured on a laptop with a loud fan, `webrtcvad` at its strictest
called **93% of silence** speech, against 91% for a spoken word — silence scored
higher than the voice. The same recording separated cleanly on loudness: 286 rms
for the room, 1117 for the word, peaks 15× apart. Each is blind to a different
family of noise: the fan passes the detector but not the loudness, a slamming
door passes the loudness but not the detector.
**Why measured and not fixed:** a threshold calibrated in one room would make
the app deaf in another. Speech is the loud minority of recent frames, so a low
percentile of them gives the room itself.
**Change:** `listen.py` → `ENERGY_RATIO`, `ENERGY_ABSOLUTE_MIN`

### 24. Silence is trimmed before upload
Groq's transcription has no server-side silence filter, and Whisper invents
whole sentences from near-silence.
**Where:** code — `_trim_to_speech`
**Change:** `listen.py` → `TRIM_PADDING_FRAMES`

### 24b. Below five speech frames, nothing is sent at all
Trimming is not enough: the padding builds a 630 ms window around a single
frame, and one isolated frame is not a word. An empty transcription is returned,
and the loop listens again without consuming the step.
**Where:** code — `MIN_SPEECH_FRAMES`, in `record_until_silence`
**Why:** Whisper does not return nothing on silence, it invents. Seen in session
at 1 frame out of 126: "ありがとうございました" — Whisper's most common
hallucination, learned from the silent ends of YouTube videos. The tutor counted
it as a missed word and raised the level.
**The threshold is measured:** a genuine one-word answer gives 13 frames or more
("tôi" → 13/70, transcribed "Tua"). Five frames are 150 ms — far below any
syllable, far above the noise that hallucinates.
**Change:** `listen.py` → `MIN_SPEECH_FRAMES`

### 25. The transcription knows which word it is expecting
When the current step asks for a recall, a first pass with automatic detection;
if it does not return the expected word, a second pass forcing Vietnamese. One
extra request only when the first fails.
**Where:** code — `transcribe(expected=..., matches=...)`
**Why:** Whisper hears right and writes wrong. `tên` sounds like *ten* in
English, and it transcribed it **`10`** — the right sound, unusable text.
**If the second pass does not return the word either**, the first pass's text is
kept — unless it had decoded in a language outside {vi, en}, in which case the
forced pass is kept. Otherwise the tag lies about its own text: seen in session,
an attempt at "tôi" arriving in Japanese under a `[lang:vi]` label.

> **And the second pass never runs when the learner was speaking to us.** Two
> words of English or more, *and* what was heard does not resemble the word the
> step asked for: we keep what they said.
>
> **The resemblance is what decides; the word count only sets a floor.** An
> attempt is the target word spelled wrong, so it looks like it — the recorded
> ones score 0.571 (`'Fen Bey.'` for `sân bay`), 0.857 (`'and Bay'`) and 1.000
> (`'toi'`), while English of two words or more tops out at 0.308. It must also
> have **as many syllables as the target**: Vietnamese is monosyllabic, so an
> attempt at a two-syllable word arrives in two tokens. `'no idea'` is not a
> shot at `nói`, however the letters fall.
>
> **Swept, not sampled.** All 129 targets a recall step can ask for, against 43
> real interruptions — 5547 combinations. Interruptions still wrongly eaten:
> **3354 before (60.5%), 5 after (0.1%)**. The five are two-word English against
> two-syllable words scoring 0.46–0.50: `'no idea'` on a step asking `bao nhiêu`
> or `có thể`, `'no clue'` on `có thể` or `Đến từ`. Raising the threshold to
> 0.55 would close them and leave `'Fen Bey.'` two hundredths of margin — not
> worth it.
>
> **Why not one word.** That is where a badly heard attempt lives — `'Bye!'` for
> `tôi` resembles nothing at all, 0.000, and must still reach the forced pass.
> The course asks for single words constantly, so recovering them is worth more
> than protecting a one-word interruption.
>
> **One number, for every language the decoder names.** Not one floor for
> English and another for the rest: the name carries no information either way.
> Measured 17 August — *"too fast"* was tagged **Italian**, so an English-only
> floor never fired and it was forced into Vietnamese as `'TÙ PHÁST'` and scored
> a missed word. Across two sessions this microphone was called Italian,
> Russian, German, Spanish, Turkish, Korean, Dutch, Portuguese and Chinese, for
> a voice speaking only English and Vietnamese.
>
> **And the English reading is checked again before it is believed.** Decoding a
> Vietnamese SENTENCE as English gives English-looking nonsense that still
> traces the target, so if it resembles what was asked for, the forced
> Vietnamese pass is taken instead. Seen in session: *"Tôi tên là Anna"*, said
> correctly, came back tagged Korean, was decoded to `'Totten-Lay-Anna.'` and
> handed over as a question — and the tutor answered with the sentence the
> learner had just produced.
>
> **A construction with a slot is answered longer than its pattern.** `tôi tên
> là + [tên riêng]` is answered *"Tôi tên là Anna"*, so resemblance requires at
> least the fixed part, not exactly it. Eleven constructions in the course have
> a slot.
>
> **Why:** the worst failure this system has produced. A step waiting for "tôi",
> the learner says in plain English *"No, I'm asking for travel, listen, I don't
> care what I am me."* It does not contain "tôi", so a forced Vietnamese pass
> ran, and returned *"Không, tôi đang chờ đề lý…"* — invented Vietnamese that
> happens to contain "tôi". The only recovery test being "is the expected word
> in there", the invention was accepted, counted as a right answer, the level
> raised, the lesson advanced. The learner was protesting and was answered
> "Exactly."
>
> Getting it wrong the other way is cheap: a Vietnamese attempt taken for
> English is counted missed and asked again — rules 20 and 4c-bis. Getting it
> wrong this way **overwrites what the learner actually said.** The thresholds
> are set by that asymmetry, not by the midpoint.
>
> **The guard used to demand more than three words, and that was the defect.**
> It predicted how someone phrases an interruption, which cannot be done.
> Measured 17 August into the real microphone: *"I forgot"* (2 words), *"I
> didn't understand"* (3), *"Can you repeat that?"* read as *"You repeat that."*
> (3). None of the three fired it, so the forced pass ran and **translated**
> them — *"I didn't understand"* came back *"Tôi không hiểu."*, which contains
> both `tôi` and `không` and scored a correct answer on any step asking for
> either. The learner says they did not understand, and is told "Exactly."

**Change:** `listen.py` → `is_learner_talking`, `SPEECH_WORDS`, `transcribe`;
`tutor.py` → `resembles_target`, `RESEMBLES_TARGET_THRESHOLD`, `_has_slot`, and
the `expected` handed to `listen_and_transcribe` (every asking step, not only a
recall)

### 25b. When nothing is expected at all, length decides the language
*Rarely, since rule 25: every step that asks the learner to produce something
now names its target, so only `introduce`, `answer` and `rule` reach here.*

If the detected language falls outside {vi, en} and no word is expected: one or
two words are a vocabulary attempt, so Vietnamese is forced; a sentence is a
question, so English is forced.
**Where:** code — `SENTENCE_WORDS`
**Why:** forcing everything to Vietnamese turned "how do you say dog in
Vietnamese?" into "Cái cách nói đáy ở Việt Nam?", and the tutor taught the word
for "the bottom".
**Change:** `listen.py` → `SENTENCE_WORDS`

### 26. A transcription is never repaired
What was said is what the tutor sees.
**Where:** code — nothing does it, deliberately
**Why:** two attempts were made and withdrawn. A vocabulary hint given to the
decoder had Whisper inventing Vietnamese out of pure noise. Snapping the text to
the nearest known word repaired exactly the mispronunciation the tutor is
supposed to hear.

---

## The opening

### 27. Three points, once, right at the start
Say things out loud; do not try to memorise; follow the course or ask for your
own subject. Then Minh greets, then one question, then stop.
**Where:** both — the code decides *when* (`lesson["started"]`), the prompt says
what
**Why:** an empty plan meant both "not started" and "finished", and the tutor
opened a brand-new session with "let's wrap up for today"
**Change:** `persona.toml` → OPENING

> **Known cost.** 55 seconds of synthesis before anything happens at all.
> `--no-intro` skips it while working on the lesson itself.

---

## Pronunciation

### 28. The tutor never judges how the learner sounds
No verdict on a sound: not on a tone, not on a vowel, not on anything that was
said. We react to **which word** it was, never to how it sounded.
**Where:** prompt — NEVER JUDGE HOW THEY SOUND
**Why:** the tutor never hears the learner, only an approximate transcription —
any verdict is a guess, and it was inventing false ones ("tên" glossed as "the a
in bed")
**Change:** `persona.toml` → NEVER JUDGE HOW THEY SOUND

### 28b. Tones ARE taught, like any other item
Six rules anchored on words already known (`06_thanh_dieu.toml`): the mark
exists, it carries the pitch, and its shape is the shape of the voice.
**Where:** content — the rules; the prompt only permits
**History:** the prompt forbade *"never name a tone, never explain that
Vietnamese has tones"*. That was temporary scaffolding, put in when no content
existed — not a pedagogical position. It fell when the rules arrived, and so did
the dodge that went with it ("that comes later"): it would have become a lie.
**What has not moved:** 28. Teaching a tone and diagnosing a tone are two
things; only the second is forbidden, and it is forbidden for a reason that
still holds.
**Change:** `content/vietnamese/06_thanh_dieu.toml`

### 28c. A word differing from an older one only by tone is presented as a pair
At the introduction of the **new** word only, and only if the older one is
known: both are said by Minh one after the other, in the same breath. `ba` then
`bà`, one clip, two words.
**Where:** code — `tone_twin` computes, `_INTRODUCE_TWIN` speaks
**Why the pair:** the tutor never hears the learner (28), so the only honest
teaching is to make the difference **audible**. Two words back to back are the
only moment the difference exists for a foreign ear.
**Why at the second only:** two lookalikes taught side by side tangle. Measured:
almost 40% of the vocabulary has a lookalike, but only three pairs among the
words taught today — the mechanism does little now and grows with the
vocabulary.
**Computed, never annotated:** the tone is in the diacritic.
**Change:** `tutor.py` → `tone_twin`, `_INTRODUCE_TWIN`

---

## The tools

### 29. Three tools, all of them rare
`set_session_focus` (the learner asks for a theme, four items are generated),
`remember_word` (they ask how to say something off-syllabus),
`deprioritize_item` (they ask to drop something — buried at level 12, never
deleted).
**Where:** the code executes, the prompt decides when
**Scope:** only on turns the model writes. A scripted turn (4b) goes through no
model, therefore through no tool — with no consequence, since all three fire on
an explicit request from the learner, and speaking is exactly what hands the
turn back to the model (4c).
**Change:** `tutor.py` → `TOOLS`

### 29b. A tool that fails never ends the lesson
Theme generation is wrapped: if it breaks, it is written to the logs and the
session carries on without the theme.
**Where:** code — the `try` around `generate_theme_items`
**Why:** the very first time `set_session_focus` fired, generation returned a
400, the exception climbed out of the tool handler, and an otherwise healthy
session died on its second turn.
**Change:** `tutor.py` → `_run_turn`

### 29c. Theme generation is not a spoken turn
It emits JSON, not speech, and has its own token ceiling.
**Where:** code — `THEME_GENERATION_MAX_TOKENS` (2500) against
`MAX_TOKENS_PER_TURN` (500)
**Why:** it inherited the ceiling meant for three spoken sentences. Four items
with their Vietnamese notes are four times that, the JSON came back truncated,
and Groq answered 400 "tool_use_failed". A truncation is not a degraded result,
it is a refusal.
**And the schema accepts `null`** on `pieces` and `literal`: they are documented
"constructions only", so on an atom the model writes `null` — which a
non-nullable schema turned into a 400, losing the whole batch for a field that
did not apply.

### 29d. A definitive refusal is not retried
A 4xx that is not a 429 means the request is wrong; repeating it cannot help.
**Where:** code — `PermanentAPIError`, `_permanent`
**Why:** the 400 above was sent five times before crashing, burning the budget
five times on a request that could not succeed.
**Change:** `tutor.py` → `_permanent`

> **Generation produces whole sentences**, which rule 9 will defer until their
> words are taught — possibly forever.

---

## Infrastructure

### 30. One model, no fallback
On a 429, the code waits and retries the same model.
**Where:** code
**Why:** every alternative breaks the format — one writes its tool calls as text
the tutor reads aloud, one leaks its internal tokens into tool names, one fires
tools without saying anything
**Change:** `tutor.py` → `MODEL`

### 31. The budget is 8000 tokens a minute
Measured, not documented. At ~3000 tokens a request, that is about two and a
half requests a minute — which is why the system prompt stays small. Since 4b,
about half the turns send nothing at all.
**Where:** Groq's free tier
**Change:** pay, or shrink `persona.toml`

### 32. Progress is written as the session goes, and read back in order
A crash costs nothing. `--fresh` writes nothing at all.

And it is **read back in the order it was written**, not in roster order.
**Where:** code — `taught_order` reads the state file, the resume uses it
**Why:** the spacing checks look at the last few items seen. A history rebuilt
in roster order makes them decide differently from the run that produced the
state — `--at=120` opened on the wrong item, and three features out of seven
missed theirs. Part of what looked like content drifting was the state rebuilt
wrong before a word was spoken.
**Change:** `tutor.py` → `run_session`; `srs.py` → `taught_order`

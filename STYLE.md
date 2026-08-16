# How the tutor speaks — a notebook

**Nobody reads this file at runtime.** Not the tutor, not the code, not the
model. It is a notebook: ideas land here, and each one leaves through one of the
three drawers below, or does not leave at all.

A style list the AI would consult during a lesson would be the prompt with extra
steps — it would grow, contradict itself, and the model would ignore part of it.
That is exactly what took a day to undo.

---

## The three drawers

| the idea is about… | it goes… | already in place |
| --- | --- | --- |
| **one particular word** | a field on the item | `hook` ("Vietnam is the second biggest coffee grower…") |
| **a gesture that recurs** | a wording in code | `_REPEAT_ASK`, `_ACK_CORRECT`, `_INTRODUCE` |
| **the manner** | the prompt, as a last resort and in place of something else | THE CORE MOVE, THREE RULES |

## The test before opening a drawer

**How often does it occur in the reference course?**

That is what made the central move solid: *"repeat after me"* zero times in
twenty-five minutes, *"how would you say"* twenty-two times. Same for *"and
again, what was ___?"*, twenty-one occurrences — which became `_REPEAT_ASK`.

An idea you cannot count in the reference is a preference. A preference goes
into no drawer until it has been measured. You can still try it — but then you
know that is what you are doing, and you watch what it gives.

---

## 1. What already runs in the tutor

These are no longer ideas: something in the tutor executes them. **Two are
whole, three cover only part** of what they proposed — and for those, what
remains is named in their status.

An entry arriving here has to say **where** it lives: a rule of `SPEC.md`, a
symbol in the code, or a field of the content. Without that, nobody will know
next year whether it still runs.

### Ask who the learner is, to teach THEIR pronouns
*Proposed by Meo.*

→ A **`strand`**, a continuous thread — and the item `cách chọn từ xưng hô` is
its vestige. See "Features: two natures, not one".

In Vietnamese the word for "I" depends on who is speaking to whom. Meo speaking
to his girlfriend says `anh` for "I" and `em` for "you". These are not exotic
variants: it is what he will say every day.

The course teaches `tôi` today, and its own entry says why that is lukewarm:

> *"'tôi' đúng ngữ pháp nhưng lạnh"* — grammatically correct, but cold.

Then it teaches `anh`/`chị`/`em` in the abstract, as a rule to know. If the
course knew who you are, it would stop being a rule — it would be **your**
words.

**What it unlocks, and it is not just one word:**

- "I" becomes `anh` or `em` depending on the person, instead of the neutral `tôi`
- the rule `cách chọn từ xưng hô` stops being a table to memorise and becomes
  "for you, with someone younger, you are `anh`"
- sentences become true: "tôi tên là Mathias" instead of an invented given name

**Drawer:** none of the three — it is a **learner profile**, persistent data
that does not exist yet. `state.json` knows only levels per word. STATUS already
flags it for the name; age and gender are the same field.

**What is needed, at minimum:** an age bracket and a gender. That is what decides
whether you are `anh`, `chị` or `em` facing someone.

**The honest limit:** the address system depends on BOTH people. Knowing who you
are is necessary, not sufficient — you also need to know who you are talking to.
But the course can say "with someone younger, you are `anh`", which is
infinitely more concrete than the general rule.

**How to ask for it:** the course already teaches `bạn tên là gì?` — "what is
your name?". It asks the question for real and keeps the answer. Age has its own
item too (`Tôi ... tuổi`). So the course already contains the questions that
fill its own profile.

**The proof, which landed in session on 11 August.** Meo asks: "can I say *Anh
tên là* if I am talking to an older guy?" The tutor could not answer; the
question arrived here.

The answer is no — facing an older man, he is `anh` and you are `em`. And in the
log, Meo had already tried "An... An... An ten la...": he was substituting the
pronoun on his own, the wrong way round. **The question the course cannot answer
is exactly the one the profile would make trivial.**

**Done on 11 August, pending the profile:** a rule in position 2, right after
`tôi` — *"Vietnamese changes the word for 'I' depending on who you are talking
to; you will meet them soon, and tôi will never be wrong in the meantime"*. It
gives no table (the words do not exist yet), it only prevents building the
habit "tôi = I" that would have to be undone at item 11.

**Status: DONE**, 14 August — "Let the course know who the learner is, so it can
teach THEIR person-words". The profile lives in `learner.py` and `learner.json`,
and `build_plan` reads it to compose the address situations (SPEC 13d). Still
true as written: this was probably the most profitable personalisation in the
whole language — the address system is what separates someone speaking
Vietnamese from someone reciting Vietnamese.

### Tones: give a model, never a verdict
*Proposed by Meo, 13 August.*

→ A **`strand`**, a continuous thread. See "Features: two natures, not one".

**The wall that decides everything: the tutor never hears the learner's
pronunciation.** No "that was close, take it up a bit". So the only teaching
available is to **make the difference audible** — give a model and create a
contrast, never evaluate.

That is not a limit to work around, it is what chooses the design.

**The three moments, in order:**

1. **In the first few minutes** — "listen to Minh and copy". One instruction,
   said once, true from the start of the course to the end. That is the
   foundation.
2. **At a word's introduction** — naming its tone, when that word needs it.
   Never a table of the six tones on day one: that is the written rule this
   course does not want.
3. **When a new word resembles an older, well-drilled one** — compare them, name
   both tones, and have Minh say both in the same breath.

The third moment is the only one where the difference truly exists for the ear.
`ba` then `bà`, one clip, two words.

**How many words are concerned — measured 13 August:**

```
                                     taught (147)        all (2062)
same skeleton, different TONE        3 groups        246 groups / 582 words
+ modified vowel (ơ/o, ư/u, ê/e)     3 groups        289 groups / 801 words
```

**Almost 40% of the vocabulary has a lookalike.** But only three pairs among the
taught words: the mechanism does next to nothing today and becomes central as
the vocabulary grows. To write down, not to wire up right away.

The three that exist:

```
ba  (ngang) three          /  bà  (huyền) grandmother
bạn (nặng)  you            /  bán (sắc)   to sell
con (ngang) classifier     /  còn (huyền) and you?
```

**Drawer:** a recurring gesture → a wording in code, inside `_INTRODUCE`.
Nothing to annotate: the tone is **computed** from the diacritic, like the tone
notes written today in the content files.

**The condition that matters: the second word only.** Two lookalikes taught side
by side tangle. The comparison fires at the introduction of the NEW one, and
only if the older one is well consolidated — the SRS level gives that number.
The course already does it by accident: `bạn`/`bán` are 125 items apart,
`con`/`còn` 105. Only `ba`/`bà` is tight, at 15.

**Two things not to do.**

*Never confirm a tone.* "Good, that was the right tone" is information we do not
have. A false confirmation installs the mistake with a guarantee stamp — worse
than silence.

*Do not talk about the tone of a compound.* `cà phê` does not have a tone, it
has two. Tone notes are per syllable, which the diacritic computation already
gives.

**A reservation about our own tool.** Minh is a synthetic voice, and an isolated
word does not carry its tone the way the same word does inside a sentence —
sentence intonation distorts it. Which argues for moment 1: **the word repeated
alone is the clean reference**, and it is the most reliable thing we have.

**Status: DONE at moment 3**, 14 August — "Say a tone pair out loud when the
second of the two is taught". The computation lives in `tone_twin`, the pair is
said by Minh in `_INTRODUCE`, and SPEC 28b carries the rule. Moments 1 and 2
remain open.

### Say the word back right after the learner's answer
*Proposed by Meo.*

After a recall, the learner answers, the tutor confirms — and Minh says the word
again. The learner has just produced it and hears it correct a second later:
that is the only moment when the comparison is immediate.

**Drawer:** a recurring gesture → a wording in code, inside `_acknowledgement`.
"That's it — tôi." instead of "That's it."

**What argues for it:** it is the only pronunciation help this course can
honestly give. The tutor never hears the learner (SPEC 28), so it cannot correct
— but it can give the model back. And a Vietnamese word at the end of a tutor
sentence is exactly the slot SPEC 3 reserves for it, so one voice switch, not
two.

**What argues against:** a voice switch costs a synthesis round trip. And it
needs the guard that already exists for `missed_twice` — if the next question is
about the same word, saying it again hands over the answer.

**Not measured yet** in the reference course. To count: does he repeat the word
after a right answer, or does he move straight on?

**The half that already exists — SPEC 18c.** The word IS given back, but only
when the learner got it wrong: "It was ngon." On a right answer they get "That's
it.", without the word. What is proposed here is therefore the **other case**,
and it is the more interesting of the two: the one where the learner has just
produced it correctly.

**Status:** to extend, not to build. The mechanism is in place in
`_acknowledgement`, it only covers the missed case.

### Rhythm is what variation is for
*Proposed by Meo. The phrasing is the point: variation is not a cure for
boredom, it is the instrument that produces rhythm.*

A lesson where every turn has the same shape does not have a monotonous rhythm —
it has **no rhythm**. It is a metronome. Rhythm comes from contrast: one long
turn, then three short ones; a sentence that tells you something, then a bare
question.

**Measured 11 August** on the course's 56 scripted turns:

```
 3 words  █
 7 words  ███████████████   ← the peak
 9 words  ███████
12 words  ███████
13 words  ███████
36 words  █                 ← the roster's only hook
```

Median 9 words, almost everything between 7 and 13. The only turn that stands
out is the one carrying a fact. The metronome, in numbers.

**What must stay fixed, what must move.** This is the distinction that keeps it
from breaking everything:

- **the signal stays fixed** — the shape of the question. "and again, what was
  ___?" has to be recognisable within three occurrences, otherwise the learner
  re-decodes the English instead of listening to the Vietnamese.
- **the texture moves** — the length of the turn, whether a sentence comes
  before the question, a fact, a digression, three recalls chained fast then one
  laid down slowly.

Varying the frame of the question would therefore be a mistake; varying
everything else is the subject.

**What it means concretely**, and it is not one single thing:

- a turn that asks nothing and tells you something ("coffee in Vietnam is…"),
  then picks back up — that would be one more **step** in `build_plan`
- far more frequent hooks, so that the length of introductions varies by itself
- ~~recall runs of unequal length, instead of a systematic three~~ **done** on
  11 August: `rapidfire_count` draws 1 to 5 around the measured average of 3, and
  the number follows what the turn has just done — 1 after a construction that
  has already had its pieces recited, 4 after a rule where the learner said
  nothing. The first of the three levers, and the only one needing no content
  written.

**The measurement that decides:** the turn-length profile of the reference
course. Not "does he digress" but "what is his distribution". If it is as flat
as ours, there is nothing to do. If it is spread, we know by how much.

**What argues against:** a turn with no question spends synthesis without making
the learner speak, and rule 3 says they must speak at least as much as the
tutor. The length of the digressions counts as much as their frequency.

**One lever is already in place — SPEC 17.** The number of recalls closing an
item varies from 1 to 4, and for exactly this entry's argument: fixed at three,
an attentive learner learned the cadence and answered the rhythm rather than the
question. That third is done and measured. What remains is the turn that tells
without asking, and more frequent hooks.

**Status:** to measure for what remains. It is the idea most likely to change
how the course feels, and the one that must not be tuned blind.

### Take a known word apart, to teach two at once
*Proposed by Meo.*

→ A **`strand`**, a thread that does not exist yet: this entry is what says why.
See "Features: two natures, not one".

When a known word splits into words that exist, say so. In Chinese, Beijing =
north + capital. Vietnamese has exactly the same, because a large share of the
vocabulary is compound:

```
sân bay     = sân (yard, ground) + bay (to fly)     a ground where one flies
Hà Nội      = hà (river) + nội (inside)             inside the river
bánh mì     = bánh (cake) + mì (wheat)
máy bay     = máy (machine) + bay (to fly)
```

The learner thinks they are learning one word and files two — and the second
sticks because they met it inside something they already knew.

**Drawer:** a field on the item → it is exactly the `hook`, but its best form.
To be written into the annotation pass's instruction, not left to chance.

**The condition that matters:** both halves must be real words. An invented
etymology spoken aloud is worse than no hook at all, and a model produces them
readily. The instruction already says "never guess"; for a decomposition each
part must additionally be verifiable.

**How many words are concerned — measured 11 August** on the 2000
frequency-imported words:

```
2000  words
 874  multi-syllable compounds                             43%
 382  split ENTIRELY into words themselves present         1 word in 5
```

So this is not a curiosity to bring out three times in a course. One word in
five can be taught this way, with vocabulary the course already contains.

```
làm việc  = làm (to do) + việc (work)        to work
bắt đầu   = bắt (to seize) + đầu (head)      to begin
xây dựng  = xây (to build) + dựng (to erect) to construct
Việt Nam  = Việt + Nam (south)
```

**And two traps the same measurement turned up.**

*False decompositions.* `bao giờ` (when) splits mechanically into `bao` (bag) +
`giờ` (hour). That means nothing: it is a different morpheme written the same
way. Automatic splitting produces them, and nothing in the data tells them apart
from the real ones.

*The meaning of the halves is not readable in Wiktionary.* `thông tin` =
information; Wiktionary gives `thông` = "river". The useful sense here is 通,
"to pass through" — so "to pass a piece of news along". The same defect as `là`
→ "fine silk": the first sense listed is the archaic one.

**So: the structure is frequent and worth it, but it does not automate.** The
model has to judge each decomposition under the "never guess" constraint, and
the quality depends on the same work as the glosses. A mechanical split would
say "bag-hour" out loud.

**Checked online 11 August — and it uncovers a flaw.** `Hà Nội` = 河內, `hà`
river + `nội` inside, the city being enclosed by the Red River and the Tô Lịch.
The fact is right.

But `hà` and `nội` are **bound** morphemes: the everyday word for river is
`sông`, for inside it is `trong`. So Hà Nội is a fine anecdote and **teaches no
usable word**. Whereas `sân bay` = `sân` (yard) + `bay` (to fly), two **free**
words, usable on their own.

**The "1 in 5" measurement counts both cases together, so it is optimistic.**
Appearing in a frequency list does not mean being a free word *in that compound*:
that is exactly the `thông tin` case, where `thông` comes out of the dictionary
as "river" while it carries 通 here, "to pass through".

Two distinct uses, not to be confused:
- **free morphemes** (`sân bay`, `làm việc`, `bắt đầu`) → teach a second word,
  which is the original idea
- **bound morphemes** (`Hà Nội`, `thế giới`, `tổ chức`) → an anecdote that helps
  memory, but no extra vocabulary

**A third case, found 13 August, that the free/bound test lets through.**
`nhớ ra` = to remember all at once. `nhớ` (to remember) and `ra` (to go out) are
both **free** words — the test passes — and the decomposition lies anyway: this
`ra` does not mean "outside", it marks the result. Same for `nghĩ ra` (to come
up with an idea) and `tìm ra` (to find after searching).

So the full test has two conditions, not one: the halves must be free, **and**
the meaning of the whole must follow from the parts. `sân bay` passes both.
`Hà Nội` fails the first. `nhớ ra` fails the second.

**Honest limit:** it works on Sino-Vietnamese compounds, not on everything.
`phở` does not decompose. It is a kind of hook, applicable where it applies —
not a rule to force everywhere.

**A lead, not yet dug into:** if the halves are real words, they could become
items in their own right. `bay` would deserve its place after `sân bay` — the
learner would meet it twice, once hidden inside "airport", once for itself.

**Status:** wired into `fill_item_metadata.py`, not yet checked against real
proposals.

---

## 2. What is still only an idea

Nothing in the code executes these. Each carries the drawer it would aim for and
the test that remains to be done before touching it.

### A sentence is a vehicle, not a destination
*Proposed by Meo, 15 August.*

**What is tracked is words and the reflex of building one.** A sentence has to be
correct, but it is disposable: it has done its job the moment it made the learner
produce something. So you do not repeat `tôi ăn cơm` six times — you bring `ăn`
and `cơm` back six times, in six different sentences: one with another pronoun,
one in the past, one with an adjective added, one negated.

**What triggered it — measured 15 August.** Of the 149 taught words, **93 (62%)
appear in no sentence at all**. They can only come back as a bare recall. And
the reference course does the opposite: `to` is heard **sixty times in eight
minutes** of Japanese, because it rides inside every sentence being built
(`METHOD.md`).

**What it cancels.** The obvious answer was to hand-write 93 sentences. If the
sentence is disposable it needs no name, no level and no draw — so there is
almost nothing to write.

**What it unlocks.** The serious objection to generation was that nothing
distinguishes `uống cà phê` from `uống cơm` — not Wiktionary, which only attests
fixed expressions, and not `vn_freqs.tsv`, which holds single words. But the
objection only bites on **free combination**. A **transformation** of an already
validated sentence stays correct: `tôi ăn cơm` correct ⇒ `anh ăn cơm`,
`tôi không ăn cơm`, `tôi đã ăn cơm` correct.

**And the operators already exist: they are the features.**

| feature | what it does to a sentence |
| --- | --- |
| `không` | negates it |
| `đã` · `rồi` · `đang` · `sẽ` | move it in time |
| `có … không ?` | turn it into a question |
| `ấy` | changes who is being spoken about |
| `rất` · `lắm` | intensify |
| adjective without `là` | lets you qualify the subject |

These are not rules to know, they are **buttons for making the next variation**.
The tier ranking then takes on a second meaning: tier 1 is the set of buttons
without which nothing can be varied.

**The `vary` step is already this idea, in miniature** — it only varies the
person, that is one button out of ten.

**Drawer:** a recurring gesture → a step in `build_plan`. Not a new `kind`: a
seed sentence stays a `construction`, and the notebook warns against taxonomy.

**What is needed before touching it:**

1. **Validated seed sentences.** Few, but correct. Eight combinations are already
   written in the content as illustrations of rules and are taught nowhere:
   `ăn cơm`, `uống cà phê`, `uống nước`, `cà phê ngon`, `cơm ngon`, `em mệt`,
   `tôi biết`, `cà phê của tôi`.
2. **Knowing which feature applies to which seed.** Negating `tôi biết` works;
   putting `cà phê ngon` in the past does not. That is Vietnamese knowledge, so
   annotation, not code.
3. **Measure before wiring.** How many distinct variations does one seed really
   support? If the answer is two, the idea is not worth its complexity.

**Measured 15 August — the gate clears.** Crossing the 8 validated seeds with the
27 `discrete` features, keeping only structural compatibility (`đã` needs a verb,
`rất` an adjective, `ấy` a person-word):

```
tôi biết                              21 features applicable
ăn cơm · uống cà phê · uống nước      19 each
em mệt                                 8
cà phê của tôi                         7
cà phê ngon · cơm ngon                 6 each
                                     ---
                        105 first-level variations
```

**105 is a ceiling, not a result**: it is compatibility of shape, not Vietnamese.
`hơn` applies to `cơm ngon` and yields `cơm ngon hơn`, which is missing the thing
being compared — counted, and to be thrown out. The real number comes out of
review, and **a grammatical sentence nobody says is worse than one sentence
fewer**: it installs itself as a reflex.

But the test set above was "if a seed gives only two variations, the idea is not
worth its complexity". The average is **thirteen**. Even throwing away two
thirds, eight already-written seeds give about thirty sentences.

**And it says where to spend the effort:** a **verb + noun** seed is worth three
times a **noun + adjective** one (19 against 6), because most features act on the
verb — tense, negation, question, obligation. So the seeds to write are sentences
with a verb in them, not descriptions.

### One turn, three things

```
tôi đã ăn cơm
 │   │   └── the words   : tôi, ăn, cơm come back
 │   └────── the feature : đã is re-applied
 └────────── the reflex  : building, not reciting
```

The feature no longer comes back through a separate step — it comes back **in
the very turn** that brings the words back. That is more economical than `0005`,
where a feature application takes a whole turn for itself.

### What this reopens, and must be settled before wiring

`0005` **explicitly** decided not to count the words used inside a sentence:
*"the application exercises them, but the code records nothing for them"*. That
was right while an application was a feature exercise. **It becomes false once
the sentence is the vehicle for the words** — `ăn`'s level would claim it had not
been worked while it had just been produced ten times.

**Meo's decision, 15 August:** we count the exposure of the words inside the
sentence, and the level is redefined once and for all — **"how many times the
learner has produced this word"**, whatever the form. Which is exactly what
`METHOD.md` counts when it records `to` sixty times.

**Status:** measured, and to be wired. What remains is writing the seeds and
having the variations reviewed — the code cannot decide that a sentence is said.

### Say what a word will build, at the moment it is learned
*Proposed by Meo, 13 August.*

The idea above taken the other way round. Decomposition pays **at the compound**:
you arrive at `sân bay` and harvest `sân` and `bay`. This one pays **at the
atom**: at the moment `đi` is taught, you say it will serve to build others.

The same fact, told at two different moments — and the second turns an ordinary
word into an investment. The learner does not file "to go", they file a piece.

**Drawer:** a recurring gesture → a wording in code, inside `_INTRODUCE`.

**What makes it better than its twin: it costs no annotation.** Backward
decomposition needs a human or a model to judge each compound — that is the whole
work of the glosses, with the risk of invention. This one is computed: `pieces`
already exists on items, it only has to be inverted. At the moment a word is
introduced, you look at which not-yet-taught items contain it in their `pieces`.
Zero new field, zero model call, and **no invention possible**: the code can only
name items that exist.

**The guard.** It is a promise. Two ways to betray it:

- announcing a compound the sequencing will never reach → count only items that
  are genuinely teachable, prerequisites satisfied;
- naming the compound means teaching it early and giving away the answer to a
  future recall — the `_leaked_target` family of bugs.

Hence the likely shape: **the number, not the words.** "That one will build four
others later." It creates the expectation without spending anything.

**How many words are concerned — measured 13 August** on our roster, by
inverting `pieces`:

```
120  taught words
 43  are a piece of at least one other item        more than one in three
```

```
tôi, ăn                      piece of 5 items
là, muốn, không, anh, chị    piece of 4
```

So the announcement would happen on more than one word in three — enough to be a
regular gesture, not a curiosity. And the number can only rise: it is capped by
the number of constructions written, today five.

**Not measured yet** in the reference course, however. To count: does he announce
that a word will serve again, or does he let it be discovered? Intuition says yes
and often — it would be the method's signature — but intuition is worth nothing
here, that is the notebook's rule.

**Status:** to try, and the cheaper of the two.

### Words you already recognise — the French layer
*Proposed by Meo.*

Are there Vietnamese words an English speaker recognises? **Yes, but not through
English: through French.** Colonisation left a layer of loanwords, and some of
them pass into English too.

Checked online 11 August ([Vietcetera], [Saigoneer], [Berlitz]):

```
cà phê    ← café          recognisable in English too
xà lách   ← salade        salad
xiếc      ← cirque        circus
cà rem    ← crème         cream
pa tê     ← pâté          English uses it as is
ga tô     ← gâteau
ti vi     ← TV            borrowed straight from English
```

And those that only work **for a French speaker**:

```
xà phòng  ← savon      bơ  ← beurre      phô mát ← fromage
ga        ← gare       ốp la ← œuf au plat
```

**Two of them are already in your roster**: `cà phê` and `ga`.

**Drawer:** a field on the item → it is the `hook`, third form after the fact and
the decomposition.

**⚠ This contradicts a rule of the prompt**, and the contradiction is
instructive:

> *"Vietnamese shares almost no vocabulary with English, so **never invite
> cognate guesses**."*

That rule is right in substance — a learner **cannot guess**, and a model left
free would invent false friends. But it also forbids pointing out a real
loanword when there is one.

The resolution is the same as everywhere else: **do not let the model improvise,
put the verified loanword in the `hook`.** Forbidding guesses and supplying facts
are two different things. If this gets wired, the prompt rule has to be reworded
at the same time — otherwise it will fight the hooks, the way the prompt fought
the tones.

**And it depends on the learner's language, not the course's.** The list is far
richer for a French speaker — and Meo is one. The course is given in English, so
today we can only aim at the intersection. Knowing the learner's mother tongue
would unlock the whole layer: one more thing the profile would make possible.

**Status:** to wire with the hooks, rewording the prompt rule the same day.

[Vietcetera]: https://vietcetera.com/en/cocottes-curated-guide-to-french-loanwords-in-vietnamese
[Saigoneer]: https://saigoneer.com/saigon-culture/1160-words-loaned-by-the-french-borrowed-by-the-vietnamese
[Berlitz]: https://berlitzvietnamonline.com/blogs/news/french-words-in-everyday-vietnamese

### Say now and then what you can already say
*Observed during the sessions of 11 August.*

The course **never** takes stock. Word, question, word, question — and at no
point does anyone say *"you now have thirteen words, and with those you can
already say your name, ask other people's, and say that something is not
something"*.

It is the most cited signature of the reference method, and it is entirely
absent here.

**This is not flattery, it is a fact.** The code computes it exactly, inventing
nothing — checked 11 August:

```
after  5 items :  3 words, and you can say "my name is ___"
after 12 items :  8 words, plus "what is your name?"
after 20 items : 13 words, 3 sentences — and you already have everything
                 for "want ___", which has not been taught yet
```

That last line is the most interesting: the code knows which sentences are
**already unlockable** because all their pieces are learned. Saying "you already
have everything you need for the next one" is a promise kept in advance.

**Drawer:** a **step** in `build_plan`, inserted every N items — the same vehicle
as the notebook's digression, and the same rhythm argument: one long turn that
tells you something, between short recalls.

**What argues for it:** it is the only overall feedback the learner can get.
Today they only have "That's it" turn by turn, which says nothing about the
trajectory. And a course by voice has no dashboard — no screen, no progress bar:
if it is not said, nobody knows it.

**What argues against:** the same as the digression — a turn with no question
spends synthesis without making the learner speak. And at 2000 words the
inventory becomes absurd: it will have to count rather than enumerate, or name
only what has just been unlocked.

**The measurement that decides:** how often does the reference course take stock?
Every five minutes, at the end of each section, once? And does it name the
sentences or only the number?

**Status:** to measure. It is the cheapest of the three rhythm ideas — the
computation exists, there is no content to write.

### Do not praise every single time
*Observed during the sessions of 11 August.*

`_ACK_CORRECT` puts "That's it. / Exactly. / Good." in front of nearly every
question. Over a run of recalls that makes four congratulations in four turns,
and it ends up meaning nothing.

**Drawer:** a wording in code — an empty string in the rotation, so the
acknowledgement is sometimes skipped.

**Status:** to measure first. Does the reference course confirm every right
answer, or only the hard ones?

### The silence after the question
*Observed.*

Rule 2 of the prompt says the turn stops at the question. That holds. But nothing
says how long is left. Today the microphone opens as soon as the synthesis has
finished playing.

**Drawer:** neither prompt nor content — it is `listen.py`.

**Status:** not a style problem, filed here by mistake. To move if it becomes a
real subject.

---

### The second sense of a homophone, at the second meeting
*Proposed by Meo, 13 August.*

`nam` 男 "male" and `nam` 南 "south": two words of different origin landing on
the same syllable. Not "orange" the fruit and the colour — more like
"there / their / they're". Vietnamese is full of them, because the syllable
inventory is small and Chinese borrowings piled on top of it.

Not to be confused with tone twins: `ba` and `bà` do not sound the same, a
native never confuses them, it is a foreign-ear obstacle. A homophone is
ambiguous **for everyone**, and is resolved by context.

**When to say it: at the second meeting, never at the introduction.** Same rule
as for tone twins, and for a reason that is not a preference — **the gloss IS
the recall question**, read aloud by `speakable(gloss)`. Two senses in one gloss
give "the word for south… or male?", a question with no single answer. The second
sense is therefore an aside, not a definition.

At the introduction it is a doubled load on a word not yet held. On the return,
it is a gift: a sound already acquired, a second word filed.

**The constraint this reveals, and it is structural.** All the code indexes items
**by their name**: prerequisites, the SRS, the pieces of constructions,
`load_course`'s deduplication. So a homophone can never be two items — they would
overwrite each other or be reported as duplicates.

It has to be **one item plus a note**. And therefore **the SRS will only ever
track one of the two senses**: the second will be said, heard, and never asked
for again. Written down here so that nobody wonders in a month why it does not
come back.

**Drawer:** a field on the item, said by a wording in code on the return.

**The data trap.** The second sense does not automate: Wiktionary gives `là` =
"fine silk" and `tôi` = "slave", its first senses are the archaic ones. Same
annotation pass as the glosses, same instruction "never guess".

**Not quantifiable with what we have.** Each word appears only once in the list,
so `nam` male and `nam` south are one item to the code. The case pairs found on
13 August (`Nam`/`nam`, `Bắc`/`bắc`, `Tết`/`tết`) are only the part where the
spelling betrays the difference. Counting the real ones would need a dictionary
of senses.

**Status:** to write into the annotation instruction, not to wire.

---

### The third moment: when the last piece falls
*Proposed by Meo, 13 August.*

The two entries above place decomposition at two moments. Meo points to a third,
and it is the best: **the moment the second half is taught**, before the compound
even arrives.

```
at the compound  ("Take a known word apart")   the 1st piece may be 3 weeks old
at the atom      ("Say what a word will…")     the 2nd piece does not exist yet
at the 2nd piece  ← this one                   BOTH halves are fresh
```

It is the only one of the three where the learner has both halves in mind at the
same time. And it is the same computation as the second, with a stricter filter —
so one mechanism to build, not two.

**Measured 13 August, and the number says not to wire it yet:**

```
it would fire   2 times   across the whole current course
   teaching xin  ->  Xin chào becomes composable
   teaching sao  ->  không sao becomes composable
```

Two. Because the course has only 27 multi-syllable words taught, and their
syllables are almost never taught separately. The 428 decomposable compounds
measured that morning are all in the **mute stock**.

**The real blocker, found while trying to build it:** no atom carries a
decomposition. `pieces` exists and is zero on zero atoms — the field only serves
constructions and rules. So **all three moments are blocked by the same missing
data**, and it belongs to the annotation pass, not to the code.

Splitting the name by syllables is computable without annotation, but it lies
half the time (`cho nên`, `bà con`, `con cái` — measured). It can only serve to
propose candidates for checking, never to speak.

**Status:** do NOT wire now. The mechanism would fire twice. To be picked up the
day the decompositions are written — and on that day all three moments arrive
together, since they are waiting for the same thing.

### Ask the learner to invent their own sentence
*Proposed by Meo, 14 August.*

At some point, stop asking "how would you say X?" and ask for **a sentence of
their own**, with what they have.

**It is the only turn where the learner would choose the content.** Today,
without exception, the tutor decides what to produce and the learner gives it
back. But the point of the course is to talk to people who will never supply the
sentence. The difference between reciting and speaking is exactly there.

**Drawer:** a recurring gesture → a step in `build_plan`, of the same kind as
`apply`. Probably not on every item: at a landing, when a construction has just
been consolidated — "now tell me something of your own with these five words".

**Sister of "say what you can already say".** The inventory announces what is
possible; this one makes it be proved. The two at the same landing would sit well
together: here is what you can say, now say one.

**What argues against, and it is serious.** The code cannot judge a free
sentence: `answered_target` compares against a known target, and here there is no
target. **So the model has to judge** — precisely what this whole day consisted
of taking away from it. Every time it was given free rein it validated
`tôi cơm ngon`, corrected a right answer, invented a mistake never made.

A sentence invented by the learner and wrongly validated is **worse** than a
missed recall: it installs a fault with a stamp of approval.

Second obstacle: recognition. A free sentence is long, and long transcriptions
are the worst — measured all evening.

**The possible way out:** do not judge. The tutor listens, Minh says a correct
version, and we move on — with no verdict. It is what the course already does for
pronunciation, where it cannot correct either: give a model, never a judgement.
The same honesty would work here.

**To measure:** does the reference course ever ask for an invention? My intuition
says rarely and late, because its strength is precisely never leaving the learner
without a net. If it is zero times in twenty-five minutes, it is a preference —
and then we try it knowing that.

**Status:** to measure first. And not to wire while the rule turn is not
scripted: it would add a place where the model judges, on the day we are trying
to remove one.

---

---

## Already measured on the reference course

The facts that have served so far, kept together so they do not have to be
measured again:

- "repeat after me": **0** times in twenty-five minutes
- "how would you say ___?": **22** times → THE CORE MOVE
- "and again, what was ___?": **21** times → `_REPEAT_ASK`
- recall questions: about **3 per new word** → `N_RAPIDFIRE`
- nothing is ever "learned" and then retired; a word comes back less and less
  → `srs.weight`, `DECAY`

And on the vocabulary itself, measured on the frequency list:

- **43%** of the 2000 most frequent words are polysyllabic
- **1 in 5** splits entirely into words present in the same list

And on our own turns, measured 11 August:

- **56** scripted turns, median length **9 words**, almost all between 7 and 13
- only one exceeds 17 words: the one carrying a `hook`

---

---

## What Meo's three ideas have in common

*The sort separated the three entries: composition and the tone twin already run
(part 1), the homophone is still an idea (part 2). What follows is what they
share, and it does not depend on their state.*

They arrived separately on 13 August and they are the same one:

| | you pay… | you collect… |
| --- | --- | --- |
| **composition** | at the atom (`đi`) | at the compound (`đi học`) |
| **tone twin** | at the first word (`ba`) | at the second (`bà`) |
| **homophone** | at the first sense (`nam` south) | on the return (`nam` male) |

**The second meeting is the one that pays.** The first lays a brick that does not
pay yet; it is by coming back to it that you collect, with nothing new to
memorise.

Which gives a common test, more useful than three separate rules: *for this idea,
what is laid down the first time, and what is collected the second?* If the
answer is "everything, right away", it is not of this family — and you have to
ask whether it doubles the load instead of spreading it.

# What the course teaches — a draft of goals

*Proposed by Meo, 13 August. To be corrected: cross out, move, add.*

**A different subject from the rest of this file.** The notebook above says how
the tutor SPEAKS; this says what the course TEACHES. Filed here because it is
only an idea — nothing in the code reads it, no field exists for it. If it takes,
it moves out into its own file.

## What it is for

For a single question, asked of every item: **"which goal needs this?"**

- no goal → it is a niche word, it stays in the stock
- a goal is waiting for it → it comes in, and we know when
- a goal has no item → that is the real work remaining, not my inventory

And above all: **18 lines can be re-read, 200 items cannot.** That is what makes
it possible to steer content choices without reading the roster.

## The 18

Order = teaching order. `✓` covered, `✗` missing.

| # | able to | what it needs |
| --- | --- | --- |
| 1 | **say who I am** | ✓ tôi, tên, là, gì |
| 2 | **choose how to address someone** | ✓ anh, chị, em, bạn, cô, chú, ông, bà, cháu, mình + the xưng hô rules |
| 3 | **greet, thank, apologise** | ✓ chào, cảm ơn, xin lỗi, không sao, dạ, vâng, ạ |
| 4 | **say what I want and do not want** | ✓ muốn, cần, thích, không |
| 5 | **ask a closed question and answer one** | ✓ có…không?, chưa? + the echo answer |
| 6 | **order food and drink** | ✓ ăn, uống, cơm, cà phê, nước, ngon, này &nbsp;·&nbsp; ✗ anything to name a dish |
| 7 | **ask a price, understand the answer** | ✓ bao nhiêu, tiền, mua, bán &nbsp;·&nbsp; ✗ **numbers past 10** (mươi, lăm, mốt, tư, trăm, nghìn) |
| 8 | **say where I am and where I am going** | ✓ ở, đi, về, ra, vào, lên, xuống, đến, trong, trên, dưới &nbsp;·&nbsp; ✗ the serial-verb rule, the places (nhà, đường, khách sạn) |
| 9 | **talk about someone else** | ✓ ấy + its rule, người |
| 10 | **place things in time** | ✓ hôm nay, hôm qua, ngày mai, đã, đang, sẽ, rồi, chưa &nbsp;·&nbsp; ✗ bây giờ, giờ |
| 11 | **say what I can, must, should do** | ✓ phải, có thể, nên, được, đừng |
| 12 | **describe and compare** | ✓ ngon, đẹp, mệt, đói, buồn, rất, lắm, hơn, nhất + adjective without "là" |
| 13 | **count things** | ✓ cái, con, người, quả, chiếc + the classifier rule |
| 14 | **ask for help, make myself understood** | ✓ giúp, hiểu, biết, nói, chờ, ơi &nbsp;·&nbsp; ✗ "say again", "slowly", "I do not understand" |
| 15 | **tell someone about my day** | ✓ ngủ, làm, học, chơi, đọc, viết, nghe, gặp, tìm, lấy |
| 16 | **give a reason, say what I think** | ✓ vì, thấy, nhớ, quên, nghĩ &nbsp;·&nbsp; ✗ anything to chain two ideas |
| 17 | **invite, suggest, encourage** | ✗ **the final particles** (nhé, đi, à, hả) + the positive imperative |
| 18 | **keep a conversation going** | ✓ còn, nữa, và, nhưng &nbsp;·&nbsp; ✗ prompting, changing the subject |

## What the list says immediately

**Three goals are blocked by missing content, not by ordering:** 7 (the
numbers), 8 (serial verbs), 17 (the particles, where nothing exists at all).
That is the work list — and it is short.

**Fifteen of eighteen are already served** by the 124 taught words. The course is
more complete than it looks; what was missing was being able to see it.

## What to watch out for

That it becomes a taxonomy. A goal moves in one line — the cost is never in the
carving up, it is in the time spent arguing about it.

And the notebook's rule holds here too: **a goal you cannot illustrate with
something you would really say to someone in Vietnam is a preference, not a
goal.**

---

# Features: two natures, not one

*Established 15 August, session "Tours mécaniques automatisés". **The tier
ranking was never validated by Meo** — it was a proposal, waiting to be crossed
out, moved, corrected.*

**This is not a taxonomy.** A and B are not two labels on the same thing: they
are **two mechanisms**, which need two different pieces of code. That is the
whole point of the distinction, and the only reason to keep it.

**Where what lives.** The classification itself — A or B, which tier — is **not**
in `SPEC.md`, and that is normal: it is not in the code yet. What is in there are
the **threads** themselves, each with its rule. The middle column below gives the
number. The day `0001` writes the classification into the items, it becomes
active and gets its own rule in `SPEC.md`.

**How to read this page with the rest of the notebook.** Here we decide: which
nature, which tier, which mechanism exists or is missing. The **pedagogical why
and the measurements** stay in the notebook entries above, and each row says
which one. No fact is written twice — and the detail is not decoration: it is
what says **how** to code the thing. A category without its notebook entry gives
the classification and loses the method.

The code treated all 35 features identically: a `kind = "feature"`, a position in
the queue, taught, done. The future tense and the tones are modelled the same
way. That is the mistake.

## The continuous threads — `strand` (7)

**These are not items, they are dimensions.** Tone attaches to *every word*. The
pronoun system attaches to *every sentence containing a person*. That cannot have
a position, because it has no end.

| the item today | does the thread already exist? | the detail, higher up in this file |
| --- | --- | --- |
| tones: listen and copy | **yes** — `SPEC 28c`, the pair said by Minh | "Tones: give a model, never a verdict" |
| the word for "I" changes | **yes** — `SPEC 10b` (the profile) + `12d` | "Ask who the learner is, to teach THEIR pronouns" |
| how to choose your term | **yes** — `SPEC 10b` + `13d` | same |
| the term changes with the pair | **yes** — `SPEC 12d` + `13d` | same |
| politeness lives in the address word | **yes** — `SPEC 13d` | same |
| gluing two known words | **NO** — `pieces` is 0 across 2042 atoms, `hook` 1 | "Take a known word apart" + "The third moment" |
| counting from 11 to 99 | **NO** — no mechanism anywhere | — nothing written |

**The four in the middle are one thread cut into four items**, because the item
was the only mould available. For six of the seven, the "thread" version already
exists and teaches better than the item version: those items are vestiges, to be
removed rather than reordered.

**Two of the seven have no thread**, and that is what decides the order of the
work. Removing them would take away teaching with nothing to replace it; they
stay items as long as their thread does not exist.

- **the numbers** — no mechanism, anywhere.
- **gluing two known words** — the 15 August session answered "yes, the `hook`",
  and that is false: measured, `pieces` is **0 across 2042 atoms** and a single
  atom carries a `hook`. The notebook had already established this on 13 August
  — *"all three moments are blocked by the same missing data, and it belongs to
  the annotation pass, not to the code"*. The thread is not built, it is
  **blocked by content that has to be written**.

## The one-off facts — `discrete` (28)

They stay items with a position. What they lack is **the second half**: you
cannot *re-ask* a feature, but you can *re-apply* it. The vehicle already exists
— the `apply` step — but it only fires at introduction.

**The measurement that produced this page:**

```
33 features taught across the whole course
level after the entire course : min 0, max 0
never asked again             : 33 / 33
```

Against an average level of **4.5** for words. Features are explicitly excluded
from the recall draw — "nobody says a rule back", which is true, and was taken to
mean "so there is nothing to do".

**Since fixed (`0005`):** a `discrete` feature now enters the draw and comes back
as an application. See `SPEC 17b`.

## The tiers — `discrete` features ranked by usefulness

**Validated by Meo on 15 August.** The authoritative list is the items' `tier`
field; what follows is the *why* of each rank, which lives nowhere else.

**Tier 1 — you cannot speak without these (8)**

| the rule | what it says |
| --- | --- |
| **verbs never change** | one form, for everyone. One sentence and it is understood — and it immediately raises the question of tense |
| **`đã`** | the past, right before the verb. The answer to the question the previous one has just raised, taught straight after |
| **`không` + verb/adjective** | one word in front, and it is negated. Same word for both |
| **`có … không ?`** | wrap the sentence to make a question. No inversion, no auxiliary |
| **answering by repeating the verb** | you do not say yes, you send the verb back |
| **`ơi`** | hailing — the first word of any interaction with a stranger |
| **no `là` before an adjective** | "Em mệt", twenty times a day |
| **`ấy`** | without it you can only speak **to** someone, never **about** someone |

**Tier 2 — very frequent (10):** `rồi` · `chưa` · `đang` · `sẽ` · `phải` ·
`ở`+`trong` · `của` · adjective after the noun · `ạ` · classifiers

**Tier 3 — comfort and finishing (9):** no gender or article · no plural ·
question word stays in place · dropping the subject · `cũng` · `rất` before /
`lắm` after · `hơn` · `được` · `năm` → `lăm`

**Removed from the course on 15 August:** subject–verb–object order. It headed
tier 1 and its entry presented it as the beginner's safety net — "when in doubt,
arrange it like English and it is usually right". Meo's decision: a French
speaker already does it without thinking, so the rule occupies a slot to teach a
reflex they arrived with.

### What the ranking says immediately

**Tiers 1 and 2 are almost all at the end of the course; tier 3 almost all at the
start.** `ơi` at 106, `có…không?` at 121 — things from the first minute of a real
conversation, served last. The current order follows the files, and the general
grammar was written before the useful vocabulary.

### The three uncertainties, as they stand

- **the classifiers** — the rule is a fact (number + classifier + noun), but
  **which** classifier for which noun is a thread: every new noun brings its own.
  A for the rule, with a latent B thread we do not model.
- **the echo answer** — classed A because the fact is said once. But it is a
  reflex that holds for every closed question, forever. What distinguishes a
  thread is that it **deepens**; the echo does not deepen. The most arguable of
  the twenty-six.
- **gluing two known words** — classed B, and that may be wrong: it is a
  comprehension strategy accompanying every compound met, not a fact you file.

## Where the classification lives

**In the items, no longer here.** Every feature carries `nature` (`discrete` or
`strand`) and, if it is `discrete`, its `tier`. That is the source; this file
does not copy it.

An attachment table lived here for a day and contradicted itself within a day:
written with the values `A` and `B`, it became false the moment the items took
`discrete` and `strand`. Copied data drifts — the same lesson as `SPEC.md`'s
**Where** line, one level down.

To read it as it really is:

```bash
python -c "import glob,tomllib,sys; sys.stdout.reconfigure(encoding='utf-8'); [print(f\"{i['nature']:9s} {i.get('tier','-')}  {i['name']}\") for f in sorted(glob.glob('content/vietnamese/*.toml')) for k,v in tomllib.load(open(f,'rb')).items() for i in (v if isinstance(v,list) else [v]) if isinstance(i,dict) and i.get('kind')=='feature']"
```

Distribution on 15 August: **28 `discrete`** (7 + 11 + 10 across the three tiers)
and **7 `strand`**.

### The two attached afterwards

`đang` and `sẽ` were in no category. Created on **14 August** by "Split the three
tense markers into three rules, one each", so **before** the classification,
which simply forgot them.

**Filed as `discrete`, tier 2, by Meo**, alongside `đã`, `rồi` and `chưa`: same
slot in the sentence, same frequency, same nature of one-off fact. Tier 2
therefore holds **11** features, not 9, and the `discrete` ones **28**.

## What follows from this, and is not done

1. **Remove the 5 duplicate features** — small, mostly content.
2. ~~**Bring the applications back**~~ — **done** by `0005`: a `discrete` feature
   enters the draw and comes back as an application. The 33/33 is closed.
3. **Reorder the course by tier** — content only, zero code. The ranking is
   validated now, so this is unblocked.

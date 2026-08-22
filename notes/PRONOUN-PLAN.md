# The person-words: what the source says, and a plan

**The source.** `.cache/vi_en_wiktionary.tsv`, 40000 headwords, downloaded by
`import_frequency_words.py` on 11 August and never read for these words. It
marks register — *impolite*, *archaic*, *Southern Vietnam*, *formal*,
*derogatory* — which is exactly what decides whether a beginner may say a word.
176 of its entries are marked as pronouns; 60 are in the top-2000 frequency list.

**What the source does NOT give.** `anh`, `chị`, `ông`, `bà` appear in this dump
only as *"John Doe / Jane Doe"*, the anonymous-person noun. Their address use —
the whole reason the course teaches them — is absent. **Those four need a human.**
Everything below that is quoted comes from the dump.

---

## The one fact the whole system rests on

The dictionary shows it plainly, and the course never states it:

```
cô     "I/me, your paternal aunt"          AND  "you, my paternal aunt"
chú    "I/me, your father's younger brother"  AND  "you, my father's younger brother"
cháu   "I/me, your nephew, niece or grandchild" AND "you, my nephew, niece or grandchild"
cậu    "I/me, your mother's brother"       AND  "you, my mother's brother"
```

**The same word is both "I" and "you".** It is not a pronoun for a person; it is
a *position in a relationship*, and either speaker can take either end. Which one
you are is decided by who is in front of you.

The course splits this across two strands — *"the word for I changes"* (slot 3)
and *"the word for you changes"* (slot 79) — and so never says the thing that
makes them one system.

## What the course has today

```
I            tôi, mình
you          anh, chị, em, bạn, ông, bà
third person ấy  (anh ấy = him)
plural        các  (the marker only)

we           nothing
they         nothing
you plural   nothing
```

Two glosses describe a different use of the word than the one the system needs:

| word | the course says | what it is in the person system |
| --- | --- | --- |
| `cháu` | nephew or niece | I/you, the younger relative — a person-word, not a kinship noun |
| `con` | one, for animals | I/you, the child — the course glosses the classifier |

## The plan, in stages

Each stage is a thing that can be said at the end of it. Ordered so that nothing
waits on something later.

**1 — the safe default.** `tôi`. The dictionary marks one of its senses *"formal
in all dialects"*, which is exactly why it is the one to start on: it is never
wrong, only ever stiff. *Already taught, and the course already says it is
provisional.*

**2 — older and younger.** `anh`, `chị`, `em`. The first axis, and the only one a
beginner can read off a person instantly. *Already taught, with the rule at
slot 9.*

**3 — the same word both ways.** That `anh` is what you call him **and** what he
calls himself. This is the missing keystone: state it once, with a pair the
learner already has. **Nothing teaches this today.**

**4 — the generation above.** `cô`, `chú` (*"slightly younger than either of your
parents"*), `bác` (*"slightly older than one of my parents"*), then `ông`, `bà`.
*`cô`, `chú`, `ông`, `bà` taught; `bác` is on the shelf at rank 594.*

**5 — we.** `chúng tôi` *"we/us (exclusive); compare chúng ta (including you)"*
against `chúng ta` *"we/us (inclusive)"*. A real distinction, cleanly documented,
and English has no equivalent — which makes it worth a rule. **`chúng tôi` is not
in the files at all; `chúng ta` is on the shelf at rank 51.**

**6 — they.** `họ`, *"only formal in other dialects"*, rank 63. **On the shelf.**

**7 — talking about someone.** `anh ấy`, `chị ấy`. *The machinery exists — `ấy`
is taught and there is a rule for it.*

## The second axis: politeness

Age and family decide **which** person-word. Register decides **how far down or
up** you are speaking, and it is a separate scale — the dictionary marks it on
every entry. Read from the pronoun section, not the first sense: Wiktionary's
first sense for `tôi` is *"slave; domestic servant"*, for `mình` *"a torso"*, for
`mày` *"eyebrows"*. Taking sense one here would teach anatomy.

**Saying "I":**

```
tao     rank 144   "(impolite, familiar, disrespectful or hostile) I/me"
tớ      rank 128   "(familiar, chiefly Northern Vietnam) I; me"
mình    TAUGHT     "(friendly, polite) I/me (used when talking to someone
                    roughly of the speaker's age)"
tôi     TAUGHT     "(formal in all dialects) I/me (used in formal contexts,
                    regardless of the difference in status)"
```

**Saying "you":**

```
mày     rank 126   "(impolite, familiar, disrespectful or hostile) you"
bạn     TAUGHT     "you (used for young person in their twenties)"
anh…    TAUGHT     the kinship words — respectful because they place the person
ngài    rank 192   "(highly formal, respectful) you"
quý vị  rank 1617  "(polite, respectful) you"
```

**What this says for the course.** The learner already has the two ends they
need: `tôi` (never wrong, sometimes stiff) and `mình` (friendly, same age). The
warm middle is covered. What is missing is not more politeness — it is knowing
that `tao` and `mày` exist and what they carry, because ranks 144 and 126 mean
they will be heard.

**And politeness is not only in the pronoun.** The course already teaches the
other half: `ạ` — *"(polite) a particle at the end of the sentence to express
formal politeness, especially to seniors"* — plus `dạ`, `vâng`, `ơi` and `xin`.
The strand `lịch sự nằm trong từ xưng hô, không phải trong giọng` states it:
politeness is the word you pick plus two small words, never a tone of voice.
**That part of the system is done.**

**8 — one warning, never a production.** `nó` is *"(impolite, colloquial) he;
him; she; her"*; `mày` is *"(impolite, familiar, disrespectful or hostile) you"*;
`tao` the same for I. They are ranks 37, 126 and 144 — the learner **will** hear
them. Taught as recognition only, with the register attached, the way the
compounding rule is taught for understanding and never for production.

## What this costs

Four words to bring off the shelf — `bác`, `chúng ta`, `họ`, and `nó` for
recognition — plus `chúng tôi`, which is in neither the course nor the frequency
list and has to be written. Two glosses to correct. One rule to write, for
stage 3.

Nothing here needs a word invented: every item above is either already taught or
sitting in `90_frequency_stock.toml` with a dictionary sense.

---

## Corrections from Meo, 2026-08-17 — lived, not read

A source that outranks the dictionary for a spoken course, because it is what
actually happened in a room.

**1 · `chị` is reciprocal between women of similar age.** Meo, in a restaurant:
his girlfriend and a woman of roughly the same age spoke Vietnamese, and **both
used `chị` for the other.** Neither was older.

The course teaches the opposite. Its table says `phụ nữ hơn tuổi mình → chị` — a
woman **older than me** — and glosses `chị` as *"address for an older female"*.
In the situation observed it would send the learner to `bạn` or `tôi`, and that
is the commonest situation an adult learner meets: talking to an adult woman of
roughly their own age.

**This is the single most valuable correction on this page.** It says the axis is
not raw age but something closer to adult standing: two adult women address each
other as `chị` regardless of who is older by a year.

**2 · `tôi` is not the safe default with strangers.** Meo: it comes across as
impolite. The dictionary disagrees — *"formal in all dialects, regardless of the
difference in status"* — but the course already agrees with Meo in its own words
and then contradicts itself in the same sentence:

> *"you have been saying tôi for I, and **Vietnamese people hardly ever say it in
> real life**; … **keep tôi for strangers**, for formal moments, and whenever you
> are not sure"*

It states that nobody uses it, then makes it the fallback. One of the two halves
has to go, and Meo's observation says which.

**3 · `bạn` is both genders.** The course glosses it *"you"*, which is already
neutral, so nothing to change — but it must not drift into being taught as a
male or female word.

**4 · `tớ` is out.** Rank 128, and Meo says it is not used enough to be worth a
slot. It was never proposed for the course, only listed in the register ladder
above; it stays there as recognition and nothing more.

### What is still unresolved

If `tôi` is not the fallback, **what is?** The plan cannot answer that from the
dictionary: it lists registers, not what a foreigner should reach for when they
cannot read someone's age. That is the next question for Meo, and it decides
stage 1 of the whole plan.

A PDF was supplied — `Vietnamese Choups.pdf` — and could not be read: its text
sits in a subsetted font, so extraction returns glyph data. It needs pasting as
text before anything in it can be used.

### The boundary on "guess older" — Meo, same conversation

> *never call a chị a cô*

Rounding up has a ceiling, and it is the generation line:

```
em    younger than you          your generation
chị   older than you            your generation
cô    your parents' generation  ← crossing this does not flatter, it ages
bà    grandparents' generation
```

**One step up, inside your own generation.** Going from `em` to `chị` is
respect. Going from `chị` to `cô` moves a woman into her parents' age bracket,
and that is an insult wearing politeness. Written into the rule.

**And it exposed the same defect a third time.** Three items are glossed as
family nouns where the course needs them as address words:

| word | was glossed | what it is when you speak to someone |
| --- | --- | --- |
| `cô` | aunt | address for a woman your parents' age — **fixed** |
| `chú` | uncle | address for a man your parents' age — **fixed** |
| `cháu` | nephew or niece | I/you, the much younger one — **still wrong** |
| `con` | one, for animals | I/you, the child — **still wrong** |

`cháu` and `con` are left alone because they are harder than a rewording: the
dictionary lists each in **both directions** — `cháu` is *"I/me, your nephew"*
and *"you, my nephew"* — so a single gloss cannot say what the word does without
saying which end of the conversation you are on. They need Meo.

---

# The validated sequence

**Approved by Meo, 2026-08-17.** Rule, then the words, then the next rule.
`✓` taught · `↑` on the frequency shelf · `✎` to write.

```
tôi ✓            I, provisional
anh ✓            an older man

  RULE 1 — the word for "I" changes with who is in front of you
  ✓ exists. Corrected today: tôi carries you, but it keeps its distance and a
  Vietnamese person would rarely pick it. Meo: it needs that disclaimer.

chị ✓            an older woman
em ✓             a younger person

  RULE 2 — THE PAIR
  Choosing their word chooses yours. anh → em, chị → em, em → anh/chị.
  When you cannot read the age, go one step up. Never across a generation.
  ← the big one. The table is already coded in learner.py and unreachable.

bạn ✓            a friend, or someone your own age

  RULE 3 — which word you pick places the person
  A nuance rule, not a big one — "un peu de détail ou de variance".
  Built on Meo's two lived cases and nothing else:
    · a restaurant: two women who did not know each other's age, and BOTH said
      chị. Not bạn. Age unknown is not a reason to level, it is a reason to
      respect.
    · never call a chị a cô — that is not more polite, it ages her.
  And the framing must be careful: **em does not diminish anyone who IS
  younger** — there it is simply the right word. It only lands badly when
  applied to someone who is not. bạn is for friends, and that is all it is.
  ✎ to write

cô ✓ · chú ✓     a woman / a man your parents' age
bác ↑ (594)      a parent's older sibling
cháu ✓           ← the reciprocal of all three

  RULE 4 — the generation above
  cô, chú, bác → you are cháu. ✎ to write

ông ✓ · bà ✓     grandparents' generation
nội ↑ (1422) · ngoại ↑ (1450)

  RULE 5 — father's side or mother's side
  ông nội against ông ngoại. ✎ to write

ba ✓ · bố ↑ (160) · mẹ ↑ (109)
con ✓            ← the reciprocal

  RULE 6 — with your parents
  ba / mẹ → you are con. ✎ to write

dì ↑ (1661) · cậu ↑ (47)

  RULE 7 — talking ABOUT someone: anh ấy, chị ấy
  ✓ EXISTS as a discrete, tier 1 — do not touch. Same for gọi ai đó: xưng hô
  + ơi (discrete, tier 1) and ạ (discrete, tier 2).

  Two precisions from Meo, worth keeping even though the rule stays closed:
  · **`anh` + the person's NAME also works** — `anh Minh` — not only `anh ấy`.
  · **It climbs with age, exactly like the address system.** Confirmed word for
    word by the dictionary:
        anh ấy   "he (man of equal or slightly greater social status)"
        ông ấy   "he (older or respected man)"
        chị ấy   "she (older than the speaker)"
        bà ấy    "she (woman of higher social status, e.g., older)"
    So the pair rule does not stop at "I" and "you": the third person is the
    same address word with `ấy` on the end, and you pick it the same way.

nó ↑ (37) · mày ↑ (126) · tao ↑ (144)

  RULE 8 — recognise, never say — and this is also where "it" lives
  You will hear them: nó is rank 37. **Meo, correcting an earlier draft of this
  page: `nó` is very impolite, and it is used above all DOWNWARD — for people
  younger than you.** That is the headline, not "it also means it".

  The earlier draft led with objects, which made it sound like a neutral word
  that happens to be rude sometimes. It is the reverse: it is a person-word
  aimed down, and pointing it at an elderly or respected person is an insult.
  The dictionary agrees — its first pronoun sense is "(impolite, colloquial)
  he; him; she; her", and the inanimate use comes further down the list.
  mày and tao have no safe side at all. ✎ to write

chúng ta ↑ (51) · chúng tôi ✎ · họ ↑ (63)

  RULE 9 — "we", with you or without you
  chúng ta includes you, chúng tôi does not. The course can currently say
  neither "we" nor "they". ✎ to write

các ✓            the plural marker — already taught

  RULE 10 — "you" to more than one person
  các in front of an address word: các anh, các bạn. The marker is taught and a
  rule already says nouns do not change in the plural, but nothing says the
  marker builds a plural YOU. This is the last gap against Meo's original list
  of axes — I, you, he, she, it, we, you-plural. ✎ to write
```

**The count:** one rule reworked (2, done), seven to write (3, 4, 5, 6, 8, 9, 10), eleven
words to bring off the shelf, one to write (`chúng tôi`).

**Left out on purpose:** `thím`, `mợ`, `dượng`, `má` — too rare for a beginner.

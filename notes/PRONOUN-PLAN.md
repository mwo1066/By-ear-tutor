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

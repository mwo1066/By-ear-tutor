# The plurals: one rule, not three

**Status:** done
**Opened and finished:** 2026-08-17

**Written after the code, which the ritual forbids.** The design was settled with
Meo across several exchanges and then built directly, with no folder in front of
it. Recorded here so the change is findable, and noted as a skipped ritual rather
than passed off as one that was followed.

## Why

The course could say neither *we* nor *they* nor *you* to more than one person. It
taught `các`, the plural marker, and not one plural pronoun.

Meo, on being shown three separate rules for *nous*, *vous* and *ils*: *"j'ai
l'impression que nous, vous et ils c'est bien différent et c'est pas genre 3
catégories différentes"*. He was right, and the dictionary states the unification
in its own first senses:

```
chúng   [particle]  "pluralizing particle for pronouns"
các     [det]       "Plural marker"
```

> **Vietnamese has no plural pronouns. It puts a word in front of a singular one.**

```
tôi → chúng tôi      nó  → chúng nó      anh → các anh
ta  → chúng ta       mày → chúng mày     bạn → các bạn
```

Confirmed by every `chúng` headword in the dictionary: `chúng tôi`, `chúng ta`,
`chúng mình`, `chúng tao`, `chúng mày`, `chúng nó` — first person, second person
and third, one particle, no change of behaviour.

**And a second fact that is not about plurality at all.** `chúng tôi` excludes the
person you are speaking to; `chúng ta` includes them. *Chúng ta đi* is an
invitation, *chúng tôi đi* is an announcement. English and French collapse both
into one word, so a learner does not know a choice is being asked of them.

## What changed

Four words — `chúng`, `chúng tôi`, `chúng ta`, `họ` — and two rules, in
`08_nguoi_khac.toml`. `chúng`, `chúng ta` and `họ` came off the frequency shelf
and were cut from the generated file; `chúng tôi` was written, being in neither.

No SPEC rule: this is content, and the rules it needs already exist.

## Result

```
 41  các          (already taught)
131  chúng        the word you put in front of a pronoun to make it plural
132  RULE         chúng before a pronoun, các before an address word
133  chúng tôi    we, not counting you
134  chúng ta     we, counting you
135  RULE         which "we" — with you in it or not
136  họ           they
```

**`chúng tôi` decomposes with nobody arranging it.** Its halves are `chúng` and
`tôi`, both taught by slot 133, so rule 11d — written this morning for `không
sao` — fires on its own:

```
Once more — what was the word you put in front of a pronoun to make it plural?
And again — what was I or me?
The Vietnamese for we, not counting you is chúng tôi.
```

`chúng ta` does not, because `ta` alone is archaic and untaught, and the condition
notices.

**Promoting off the shelf worked exactly as the importer intends.** It already
skips every word the course teaches, so the three were cut from the generated file
and `check_roster` reports no duplicate. This is the operation I twice told Meo was
impossible, in `0012` and again while planning the hooks. It was never blocked.

### Two traps avoided

**`họ`.** The frequency shelf carries only its NOUN senses — *"family name;
surname"*, *"extended family"*. The pronoun sense sits elsewhere in the Wiktionary
dump. Taking the shelf's first sense would have taught "surname" as the word for
*they*.

**`chúng` alone** means *they* with a dismissive edge — the dictionary marks it
*"used for animals"* and *"for people whom one holds in low regard"*. It is
therefore glossed as the particle and never as a pronoun.

### Set aside, on Meo's call

`chúng nó`, too specific. And `họ` does not distinguish *ils* from *elles*, which
is worth saying to a French speaker who goes looking for the difference.

### Not verified

**No session has reached slot 131.** Everything above is offline: the plans build,
the smoke test passes at exit 0, `check_roster` is clean. Nobody has heard it.


---

## Addendum, same day — the native speaker changed it after archiving

Three corrections arrived after this folder was closed. Recorded here rather than
in a new folder, because they revise this change rather than follow it.

**`chúng` is gone as a taught word.** Her call: *"forget the word chúng and
explain the word các more specifically."* The dictionary backs it — `chúng` alone
is *"they/them (used for animals)"* and *"for people whom one holds in low
regard"* — so teaching it as a detachable particle invites `chúng anh`, which is
not a thing. `chúng tôi` and `chúng ta` are taught as **whole words**, and the
rule built on the particle is deleted. Side effect: `chúng tôi` no longer
decomposes, since rule 11d needs both halves taught.

**`các` is not "you, plural".** Her sentence settled it:

> *Các cháu không thích ăn cái này* — said to an elderly person, meaning **we**,
> me and my friends, do not want to eat this.

So `các` + an address word **swings three ways exactly as the singular does**:
`các cháu` is *we* to an elderly person, *you* to a group of children, *them* when
speaking about either. Direction of the conversation decides, not the word. That
is the pair rule one level up, and the rule now says so in her words. `các` also
gained its own explanation and its own table, on her request that it be taught as
a tool rather than a line inside another rule.

**`họ` is not "they".** *"Stop thinking họ is only they."* It works for ONE person
and its job is not number at all — it is how you speak about someone when you do
not know them, or will not commit to their age or gender. The escape hatch from
the address system. Re-glossed *"someone you do not know, one or several"*.

**And a project constraint that had never been written down.** *"Don't forget
that we're learning north Vietnamese"*, said after I asked about southern usage.
It is now the first section of `STATUS.md`, because it settles choices that are
otherwise a coin toss — `nghìn` not `ngàn`, `quả` not `trái` — and decides what to
do with any dictionary entry marked for one region.

**Still open, parked not answered:** `các` against `những`. The course claims
`những` means part of a group where `các` means all of it; the dictionary gives
both the same definition, and `những` is rank 21 where `các` is not in the top
2000.

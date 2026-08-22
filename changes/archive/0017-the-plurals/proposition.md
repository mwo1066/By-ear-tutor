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

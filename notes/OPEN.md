# What is known to be broken, and not yet fixed

Written 2026-08-23, after the first two real voice sessions of the money slice —
one with Meo, one with a native speaker. Everything here was seen in a session
or measured, not guessed. Nothing here is a plan; it is a list of what a session
does wrong today.

---

## 1. The turns the model writes

Every defect observed across both sessions came from a turn the **model** wrote.
Not one came from a turn the **code** wrote. That is the finding, and it points
at where the work is.

> **Two of the four below are fixed** — `0023` (the rule turn no longer invites
> speech) and `0024` (no turn announces failure). The other two are knowingly
> left, on Meo's call, 2026-08-23: *"le reste je m'en rappelle plus, on ne fait
> pas — on corrigera peut-être si je repasse dessus."*

**Three examples and no question. FIXED — `0023`.** The `rule` turn for `trăm nghìn` said:

> The notes you actually hold are hundreds of thousands — một trăm nghìn.
> two hundred thousand — hai trăm nghìn. five hundred thousand — năm trăm nghìn.
> Your turn.

Meo could not tell what was being asked and said so live: *"bah ici on sait même
pas quoi il demande"*. In the earlier session the same turn produced *"Which one
I have to said?"*. **Two people blocked at the same turn, one of them native.**

Meo's fix, and it is right: **one at a time.**

**It announces failure. FIXED — `0024`.** The model wrote "That's not it." and "The correct word
is nghìn." `METHOD.md` records that the Noble extracts contain **no negative
corrections at all** — no "not quite", no "that's wrong", no "try again". The
scripted turn already does the right thing: *"Listen again — nghìn. Again?"*

**It gives the answer away, then asks for it. LEFT, on Meo's call.** Three times across two sessions,
each one caught by the existing diagnostic and none prevented:

```
!! the answer was given away: this turn asked FOR 'nghìn' and said it
!! the answer was given away: this turn asked FOR 'trăm' and said it
```

**It drops Vietnamese mid-sentence. LEFT, on Meo's call.** Twice. The persona forbids it and the
diagnostic counts it, and it happens anyway.

---

## 2. `các` has no sayable gloss

Flagged at every startup:

> `các`: gloss 'the word you put in front of an address word to speak to several
> people' describes the word instead of translating it — 15 words

It would be read aloud as *"what was the word you put in front of an address
word to speak to several people?"*.

It resists a short gloss because `các` has no English equivalent — English uses
`-s`. So either it gets a sayable handle, or it is **not an atom asked from the
meaning side** and should be a rule. That is a content decision and it is Meo's.

The five question words (`gì`, `đâu`, `ai`, `sao`, `thế nào`) are flagged by the
same check. That flag is probably **stale**: `_REPEAT_ASK_SHORT` was added after
it and produces *"what was the word for where?"*, which reads fine. Worth
deleting the check for one-word glosses rather than changing the words.

---

## 3. Not verified by anyone competent

**Nobody has judged Minh's pronunciation.** The course teaches NORTHERN
Vietnamese, decided 2026-08-17, and the entire tone strand rests on Azure's
`vi-VN-NamMinhNeural` saying the six tones correctly. A native speaker sat
through a session on 23 August and was not asked. **This is the cheapest
unanswered question in the project and the one with the most resting on it.**

**An older note says the early address warning is broken** — no table of its
own, and it asks the learner to say "tôi anh". Could not be re-checked on 23
August: features are not in the `askable` list, so the slot cannot be found the
way it was before. **Status unknown**, recorded rather than repeated as fact.

---

## Unfinished, but not broken

- **Six pronoun rules** never written: 3 (which word places the person),
  4 (generation above), 5 (paternal/maternal), 6 (with your parents),
  8 (recognise, never say), 11 (`nói trống không`).
- **54 candidate sentences** in `SENTENCES-TO-VALIDATE.md` await Meo. All 54 use
  only taught words.
- **The three tone-pair rules share an unrelated exercise.** Accepted knowingly
  on Meo's call: *"l'exercice pour le moment c'est une difficulté en plus."*
- **`các` vs `những`** — parked, never answered.

---

## Settled on 23 August, recorded so it is not reopened

**The repetition curve is not up for debate.** `METHOD.md` counts it from the
Japanese extract — "to" 60 times in eight minutes, "Kyoto" 13 — and names
`srs.py` as its consequence: the weight decays but never reaches zero. Only the
`DECAY = 1.5` value was chosen for shape.

**What a level counts is the open question, not how fast it decays.** Meo:
*"je veux juste un ratio de rappel des mots peu importe si t'as juste ou faux."*
A word's return rate should follow where it is in the course, not whether the
learner answered correctly — which is what the Noble counts describe in the
first place, since they measure how often the tutor uses a word.

Consequence, if adopted: the verdict from `answered_target` stops feeding the
level entirely, and goes back to its one original job — deciding whether the
tutor asks again straight away. The measured looseness of that verdict then
stops mattering:

```
153 taught words swept against each other
1452 of 23256 wrong pairs score as correct   (6.2%)
150 of 153 words (98%) can be answered by some OTHER taught word
   nói, đói, hỏi, tuổi, rồi … all accepted as `tôi`
   tiền, nên, đến, thế nào  … all accepted as `tên`
```

That measurement is why the change matters, not an argument for tuning the
0.5 threshold.

# A cupboard, for words the course should know but never teach

**Status:** proposed — awaiting Meo. **No code written.**
**Opened:** 2026-08-23

## Why

The sixth batch of shelf glosses taught `Mỹ` — America. Meo:

> *"le mot italien, honnêtement c'est de la merde à faire apprendre. Pour moi
> c'est bien qu'il y ait un gloss, mais genre que si l'utilisateur le demande on
> le fait apprendre. Même chose pour tous les pays, à part Vietnam."*

He is right, and the course cannot express it. `is_teachable` is one line:

```python
return item.kind == "feature" or bool(item.gloss)
```

**Glossed means taught.** There is no state between "the tutor does not know
this word" and "the tutor will drill it at you". A country name has to be one or
the other, and neither is what is wanted: forgetting `Mỹ` means the tutor cannot
answer if the learner says it, and teaching it spends a recall slot on a word
nobody needs by heart.

## What is proposed

A third state. An item can be **known and not queued**: it carries a gloss, the
tutor can recognise it and answer about it, and the sequence never introduces it
on its own. It comes out when the learner asks for it.

Meo's word for it is the cupboard — `placard`. Distinct from the shelf, which
holds words that are not ready; these are ready and simply not wanted yet.

## It has a name now

**The cupboard.** Meo chose it, 2026-08-23, and it is in `GLOSSARY.md` beside
**mute stock**, which it must not be confused with:

```
mute stock    no gloss      the tutor does not know the word
the cupboard  gloss, unqueued   it knows it, answers about it, never teaches it
the course    gloss, queued     it teaches it
```

## What goes in it

Country and place names, `Việt Nam` excepted — the course is about Vietnam and
its own name earns its place.

And Meo expects more: *"je pense qu'il y a des mots random comme ça qui sont pas
si importants qu'on pourra mettre dans le placard."* The category is not
"proper nouns"; it is "real vocabulary that a beginner does not need drilled".

**A first pass over the 1125 glossed words finds about 55**, and they fall into
five groups rather than being scattered:

```
places, proper nouns  12   Mỹ, Pháp, Nga, Nhật Bản, Hàn Quốc, Thái Lan,
                           Hà Nội, Trung Quốc, Chúa, Phật
                           -- Việt Nam and Tết stay: they are the course's own

military               9   súng, lính, vũ khí, đạn, bom, quân đội,
                           chiến tranh, thuyền trưởng, sĩ quan

finance               10   lãi suất, thuế, quỹ, bảo hiểm, ngân sách,
                           tài khoản, chỉ số, kế toán, đầu tư, tài chính

state, administration  7   quy định, chính sách, an ninh, hội đồng,
                           đại hội, hành chính, đặc vụ

medical, technical    11   ung thư, viêm, phẫu thuật, tế bào, thần kinh,
                           triệu chứng, thai, ma tuý, tâm lý, thống kê,
                           dinh dưỡng
```

None of these is a bad word or a bad gloss. Each is real and frequent enough to
have earned a place in a 2000-word list. None of them belongs in a beginner's
first hundred hours.

That list was produced by keyword matching and it is a **first pass, not a
decision** -- the same scan caught `kho` (warehouse), `ấm` (warm) and `cảnh báo`
(warning) as military, all three on the substring "war". It needs reading before
it is used.

## What must be settled before code

**Whether the draw already has a place for this.** `srs.deprioritize` exists —
*"The learner asked to stop working on this. Buried, never deleted."* — and puts
a word at level 12, one draw in 47. That is a learner action at runtime, not a
property of the item, and it buries rather than excludes. Whether the cupboard
should reuse that machinery or sit beside it is the first question, and it
should be answered by reading `pick_next_index` rather than guessed.

**And what "if the learner asks" means concretely.** — **checked, and it already
works.** `learner_asked_something` catches an English question and hands the turn
to the model, so a learner can say "how do you say wife?" today and get an
answer.

But the answer does not come from the course. The vocabulary is deliberately
kept out of the prompt — *"everything the model does not need in order to speak
this turn is weight it pays for on every request"* — so the model replies from
its own Vietnamese, and **a cupboard item's gloss would never be read.**

That makes this change much smaller than it looked: the asking half exists and
needs nothing. What is left is one flag meaning *do not queue this*.

It also exposes something worth knowing separately: when a learner asks for a
word, the answer is unverified by the course. It could be a southern form, or
carry a tone nothing here checked. That is not this change, but it is now on the
record.

## Not in this change

`Mỹ` is glossed and teachable right now, and stays that way until this is built.
One country name in the queue is a small price for not inventing a mechanism in
a hurry.

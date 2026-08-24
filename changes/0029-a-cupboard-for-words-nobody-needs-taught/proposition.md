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

## What goes in it

Country and place names, `Việt Nam` excepted — the course is about Vietnam and
its own name earns its place.

And Meo expects more: *"je pense qu'il y a des mots random comme ça qui sont pas
si importants qu'on pourra mettre dans le placard."* The category is not
"proper nouns"; it is "real vocabulary that a beginner does not need drilled".
What else belongs there is content work, decided a batch at a time, the same way
`HELD_BACK` grew.

## What must be settled before code

**Whether the draw already has a place for this.** `srs.deprioritize` exists —
*"The learner asked to stop working on this. Buried, never deleted."* — and puts
a word at level 12, one draw in 47. That is a learner action at runtime, not a
property of the item, and it buries rather than excludes. Whether the cupboard
should reuse that machinery or sit beside it is the first question, and it
should be answered by reading `pick_next_index` rather than guessed.

**And what "if the learner asks" means concretely.** Today nothing looks a word
up on request. If the cupboard's whole point is answering on demand, the asking
has to exist, and it may be the larger half of this change.

## Not in this change

`Mỹ` is glossed and teachable right now, and stays that way until this is built.
One country name in the queue is a small price for not inventing a mechanism in
a hurry.

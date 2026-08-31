# A thousand words arrive, and the course stops teaching sentences

**Status:** proposed — awaiting Meo. **No code written.**
**Opened:** 2026-08-23

## Why

Meo, after the shelf was emptied: *"tu as déjà pensé à une autre [manière] de les
introduire ?"* No. And looking at what the sequencing now produces, it needed
asking.

```
items    0-221    167 words,  46 rules,  8 sentences   the curated course
items  221-1346  1111 words,   0 rules, 14 sentences   what was poured in tonight
```

**After item 221 the course stops teaching grammar.** It becomes a vocabulary
drill in frequency order — `tay`, `nhận`, `phòng`, `gần`, `trường` — eleven
hundred times, with no rule and almost no sentence.

The curated course puts a rule roughly every five items. There is not one in the
1111 that follow.

## Why it happened

`load_roster` reads lesson files in filename order and items in file order.
`90_frequency_stock.toml` sorts last, so everything in it arrives after
everything curated. The import was designed that way and it was right while the
stock was unglossed: those items were held out by `is_teachable` and never
reached a learner. Glossing them turned a staging area into the back half of the
course, in one evening, without anyone choosing an order.

## What this is NOT

It is not a bug in the import and not a bad gloss. Every one of those 1111 words
is a word the course wants. The question is only where each goes, and what
travels with it.

## What has to be decided, and it is content

**Do the new words interleave with the curated lessons, or follow them?**
Frequency order after the taught material is one answer, and it is the current
one by accident rather than by choice.

**What carries the grammar across 1111 items?** The course teaches a rule every
five items for its first 221 and then stops. Either rules are written to go with
the new vocabulary, or the sequencing draws from both files at once so the
existing rules keep arriving, or the back half is knowingly a vocabulary phase.
All three are defensible; none is chosen.

**And the sentences.** Meo, earlier: *"l'idéal c'est que les phrases prennent en
compte les 2000 mots et évidemment qu'elles prennent en compte tous les
features."* 54 candidate sentences are already waiting in
`SENTENCES-TO-VALIDATE.md`, written when the course had 150 words. They are now
a rounding error against 1346 items.

## What must be measured before choosing

**How long the back half actually takes.** At the measured 15 s a turn and
roughly 5.7 turns an item, 1111 items is about 30 hours of lesson. Whether that
is "the course" or "a phase" changes what should be done about it.

**And whether pick_next_index even reaches them.** It is worth checking that the
draw does not stall or degrade at this size before designing the order it walks
in.

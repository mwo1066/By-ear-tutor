# A compound word recalls its parts before it is presented

**Status:** proposed
**Opened:** 2026-08-17

## Why

`không sao` now carries the course's only morphological hook, written earlier
today. When the word arrives the learner hears:

```
This one you can almost work out: it is the word for not, and the word for why,
side by side — so it says, literally, there is nothing the matter.
The Vietnamese for no problem is không sao. không sao. Your turn — say it.
```

**The hook names two words the learner has, and never asks for either.** Meo, on
hearing it: *"j'aimerais bien que avant qu'on dise cette phrase bah on redemande
c'est quoi 'not' et c'est quoi 'sao'"*. The fact is handed over where it could
have been produced — which is this course's central move, "how would you say ___",
applied to the two halves.

**The machinery already exists and is simply not applied to words.**
`derive_pieces("không sao")` returns `['không', 'sao']` — the code can see the
parts. But `build_plan` splits on `kind`: a **construction** gets one
`recall_piece` per piece before anything else, an **atom** gets `introduce` then
`settle` and nothing in front. A compound is an atom, so its parts are never
asked for.

**Why this is not just a nicety.** The strand `ghép hai từ đã biết thành từ mới`
says Vietnamese builds new words from words you already know, and rule 17b
exempts it from the draw because it "fires from the material". This is the
material. A compound that arrives without its parts being recalled demonstrates
the rule to nobody.

**How often it can fire, measured today:** the course teaches **150 words, 25 of
them compounds, and exactly 1** — `không sao` — has both halves taught. So this
change lands on one word now. It is proposed anyway, and first, because the shape
has to be right before compounds are added in series: `sân bay` is `sân` (yard) +
`bay` (to fly) and neither half is taught yet.

## What changes in SPEC.md

- **rule 11d — new**: *a compound whose parts are all taught recalls them first.*
  Before the `introduce` of a multi-syllable atom, one `recall_piece` per part,
  in order — the construction's opening, applied to a word. If any part is not
  taught, nothing changes and the word is introduced as it is today.
  **Where:** code — `build_plan`, the atom branch; the parts come from
  `derive_pieces`, which already reads them.

Rule 11c (the hook comes before the presentation) is untouched: the hook still
sits in front of the introduce. This adds turns **before** that, so the order
becomes *ask for the parts → hook → the word*.

## Scope

**In:** the recall of a compound atom's parts, before its introduction.

**Out:**

- **Getting words off the frequency shelf.** The wall hit twice today — `đồng` in
  `0012`, then `ăn uống` and `chị em` here: glossing them where they live puts
  them a thousand items too late, copying them into a lesson file makes a
  duplicate the shelf silently wins. That is `0014`, and it is what actually
  unblocks the content axis.
- **`_needs_fill` never asking for a hook.** An item with a `kind` and a `gloss`
  counts as complete, so `fill_item_metadata.py` will never revisit the **203 of
  205** items that carry no hook. Found while answering whether hooks would
  appear on their own. A third change.
- **Writing more hooks.** Content, and it depends on `0014`.

## Tasks

- [ ] in `build_plan`'s atom branch, when the item's name is multi-syllable and
      every part `derive_pieces` returns is already taught, prepend one
      `recall_piece` per part, in the order they appear in the word
- [ ] leave the plan untouched when any part is missing — `xin lỗi`, `có thể`
      and 22 others have only one half taught, and asking for the other would
      ask for a word that does not exist in the course
- [ ] check the turn count: `không sao` goes from 4 turns to 6, and rule 9b's
      spacing still holds
- [ ] `SPEC.md` rule 11d

## Verification

1. **Offline**: `python smoke_test.py` at exit 0, and `check_every_plan_builds`
   covers every item, so a plan that cannot be built fails there.
2. **The plan for `không sao`**, printed: `recall_piece(không) → recall_piece(sao)
   → introduce(hook + word) → settle → …`, and the two recalls must ask for
   *"no / not"* and *"for what reason"*, never for the compound.
3. **No other item moves.** 24 of the 25 compounds have a part the course does
   not teach; their plans must be identical before and after. This is the
   measurement that says the condition is right, and it is checkable offline for
   all 213 items.
4. One real or simulated session reaching `không sao`, listened to.

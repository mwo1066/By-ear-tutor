# Compound words to validate

**What I am asking for:** cross out what is wrong, correct what is said
differently. Tick what is good.

**This was written when there was no second source, and there is one now.**
The frequency file excludes every word the course teaches — the importer skips
them so an import never duplicates the course — which is why nothing here had
ever been checked. But the importer also **cached the whole Wiktionary dump** on
11 August, 40000 headwords, and nobody had looked a taught word up in it.

```bash
python check_glosses_against_dictionary.py
```

**142 of the 150 taught words are in it**, and 17 of the 25 compounds below.
Their glosses hold. Four are worth your eye, where the dictionary says something
slightly different:

| word | the course says | the dictionary says |
| --- | --- | --- |
| `có thể` | to be able to | *(before verbs) possibly* |
| `cảm ơn` | thank you | *to thank* |
| `chúc mừng` | congratulations | *to congratulate* |
| `Tạm biệt` | goodbye | *(formal or literary) farewell* |

The eight absent ones are the sentences in part 2 — a dictionary has no entry for
a sentence, which is the diagnosis confirming itself.

We already caught one: the compounding rule illustrated itself with `đi học`,
which is not in the 2000-word list, and no `đi` + something compound is — so it
is very likely two words side by side, not one word. It had been sitting there
unchecked.

---

## 1 · Words — 17 of them

The course teaches each of these as **one word**. Two questions on each: is the
meaning right, and is it really one word?

- [ ] `Tạm biệt` — *goodbye*
      halves: Tạm — not taught, biệt — not taught
- [ ] `Xin chào` — *hello (formal)*
      halves: Xin — not taught, chào = hello
- [ ] `bao nhiêu` — *how much*
      halves: bao — not taught, nhiêu — not taught
- [ ] `chúc mừng` — *congratulations*
      halves: chúc — not taught, mừng — not taught
- [ ] `cà phê` — *coffee*
      halves: cà — not taught, phê — not taught
- [ ] `có thể` — *to be able to*
      halves: có = have, thể — not taught
- [ ] `cảm ơn` — *thank you*
      halves: cảm — not taught, ơn — not taught
- [ ] `hôm nay` — *today*
      halves: hôm — not taught, nay — not taught
- [ ] `hôm qua` — *yesterday*
      halves: hôm — not taught, qua — not taught
- [ ] `khách sạn` — *hotel*
      halves: khách — not taught, sạn — not taught
- [ ] `không sao` — *no problem*
      halves: không = no / not, sao = why
- [ ] `ngày mai` — *tomorrow*
      halves: ngày — not taught, mai — not taught
- [ ] `sân bay` — *airport*
      halves: sân — not taught, bay — not taught
- [ ] `thế nào` — *how*
      halves: thế — not taught, nào — not taught
- [ ] `xin lỗi` — *sorry*
      halves: xin = please, may I, lỗi — not taught
- [ ] `Đến từ` — *come from*
      halves: Đến — not taught, từ — not taught
- [ ] `đàn guitar` — *guitar*
      halves: đàn — not taught, guitar — not taught

## 2 · These are sentences, filed as words — 8 of them

Marked `kind = "atom"`, which is what the course calls a word. They are not
words. That does not make them wrong to teach — but a word gets a word's
treatment, and these are being drilled as vocabulary.

- [ ] `Bạn bao nhiêu tuổi?` — *how old are you?*
- [ ] `Bạn làm gì?` — *what do you do?*
- [ ] `Bạn đến từ đâu?` — *where are you from?*
- [ ] `Chào buổi chiều` — *good afternoon*
- [ ] `Chào buổi sáng` — *good morning*
- [ ] `Chào buổi tối` — *good evening*
- [ ] `Hẹn gặp lại` — *see you again*
- [ ] `Rất vui được gặp bạn` — *nice to meet you*

## 3 · Confirmed by the dictionary, and NOT yet taught

These sit in the frequency shelf with a dictionary sense, and the course already
teaches both halves. **Low risk, and available** — this is where to pick from
when the compounding rule needs more cases.

- [ ] `con người` — *?*  (rank 385) — con = one, for animals, người = person
- [ ] `anh em` — *older brother and younger sibling*  (rank 849) — anh = address for an older male, em = address for a younger person
- [ ] `tìm hiểu` — *to try to understand; to examine; to investigate; to study*  (rank 931) — tìm = to look for, hiểu = to understand
- [ ] `cho nên` — *therefore; hence; consequently*  (rank 1458) — cho = to give, nên = should
- [ ] `chị em` — *sisters*  (rank 1520) — chị = address for an older female, em = address for a younger person
- [ ] `làm ăn` — *to work ; to make a living; to do business*  (rank 1595) — làm = to do, to work, ăn = to eat
- [ ] `năm học` — *?*  (rank 1634) — năm = five, học = to study
- [ ] `bà con` — *relatives*  (rank 1845) — bà = address for an elderly woman, con = one, for animals
- [ ] `ăn uống` — *to consume foods and drinks*  (rank 1857) — ăn = to eat, uống = to drink
- [ ] `con cái` — *children; offspring*  (rank 2015) — con = one, for animals, cái = one, for objects

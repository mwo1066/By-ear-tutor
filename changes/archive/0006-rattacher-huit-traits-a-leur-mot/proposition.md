# Attach eight features to the word they are about

**Status:** finished
**Opened:** 2026-08-15

## Why

The `after` field names the word a feature goes with. Until that word is taught
the feature waits; as soon as it is, the feature goes ahead of the spacing rules
(rule 9c). Without `after`, a feature waits its turn in the queue, and its
position depends only on how many features precede it.

Measured in the code: **the median feature arrives 47 items after the last of its
own words, and 21 out of 30 wait more than 30 items.** The learner meets a word,
drills it as vocabulary, and learns an hour later where it goes.

Thirteen features already carried an `after`. Twenty-two did not — and among
them, eight name their word **in their own title**.

## What changes in SPEC.md

Nothing. Rule 9c already describes the mechanism; this fills a content field.

## Scope

**In:** eight `after` fields in the content files.

| feature | word | tier |
| --- | --- | --- |
| `phủ định: không + [...]` | `không` | 1 |
| `câu hỏi có/không` | `có` | 1 |
| `ạ: một chữ làm câu lịch sự` | `ạ` | 2 |
| `sở hữu: danh từ + của + người` | `của` | 2 |
| `được đứng sau động từ` | `được` | 3 |
| `cũng đứng trước động từ` | `cũng` | 3 |
| `rất trước, lắm sau` | `rất` | 3 |
| `so sánh: tính từ + hơn` | `hơn` | 3 |

**Out:**

- **seven `discrete` features that are about no word** — subject-verb-object
  order, the absence of gender, the adjective after the noun. Nothing to attach:
  they are about a shape, not a word.
- **the seven `strand`s**, which are not sequenced as items.

## Verification, done before writing

**Attaching can delay** if the word arrives after the feature. Simulated on all
eight before touching the content: none is delayed. It is mechanical — a word
named in the title is also a piece, and an item is never taught before its pieces
(rule 9).

**Measured effect**, same seed, `after` neutralised then active:

```
gap between a feature and its word, for the eight
   before : median 46 items   (max 96)
   after  : median  1 item    (max 15)
```

The maximum stays at 15 because `after` does not short-circuit prerequisites:
`rất trước, lắm sau` also waits for `lắm`, which is one of its pieces. That is
correct — a feature cannot arrive before the words it is made of.

## Tasks

- [x] Find the features naming their word without declaring it
- [x] Check that none would be delayed
- [x] Write the eight `after` fields
- [x] Measure the gap before / after
- [x] `python smoke_test.py`

## Result

**Finished:** 2026-08-15 — eight items, five content files.

**Two false starts on the sort, worth recording.**

The first sort looked for "a feature with exactly **one** piece that is a taught
word". It found one candidate out of twenty-two, and filed `cũng đứng trước động
từ` among the legitimate cases — while its title names `cũng`. The right
criterion was "a taught word appearing **in the title and in the pieces**": eight
candidates, and no false positive on inspection.

The second: the script reported **nine** attachments for eight changed items. The
difference came from a **construction** whose name is close to a feature's —
`câu hỏi có/không: có + [động từ] ... không?` against `câu hỏi có/không`. The
fragment search hit both, the insertion happened only on the feature, and the
counter counted both. Without the `git diff`, the position measurement used to
decide had been reading the construction and not the feature. **A counter that
does not count what you think is more dangerous than a visible error.**

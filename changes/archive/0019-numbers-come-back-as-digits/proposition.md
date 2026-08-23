# Whisper writes numbers as digits, so no number could ever be answered

**Status:** done
**Opened and finished:** 2026-08-23

**Written after the code.** Same skipped ritual as `0017` and `0018`, and
recorded rather than dressed up. The difference this time is that the defect was
found by a native speaker in a live session, which is also why it was fixed
before it was written down.

## Why

A native Vietnamese speaker sat a session on the money slice. She said
**`mười nghìn`**, correctly. The transcription came back:

```
you (transcribed): [lang:vi] 10.000
  (missed 'nghìn' -- one more go)
```

**The course told a native speaker she had got it wrong.** Three times in one
session.

`_bare` keeps letters and turns everything else into a separator, so `10.000`
reduces to the **empty string** — not "a poor match", nothing at all to compare.
`answered_target` then returns False for every number, at every threshold, for
every speaker, however well pronounced.

**Scope, and this is why it mattered more than it looked:** every number recall
in the course, and the whole money thread — the slice `0012` built, and the one
that had been verified most carefully offline. Offline verification could not
see this. It needed a mouth.

## What changed

Numbers are spelled back into Vietnamese before the comparison, in the forms the
course teaches:

```
10.000  -> mười nghìn        200.000 -> hai trăm nghìn
21      -> hai mươi mốt      24      -> hai mươi tư
25      -> hai mươi lăm      15      -> mười lăm
```

The three shapes that change after a ten — `mốt`, `tư`, `lăm` — are handled,
because the course teaches them as words in their own right.

All four spellings Whisper produces are matched: `10.000`, `10,000`, `10 000`,
`10000`. Grouped digits only, so `10.000` is one number while `5, 6` stays two.

It is a **matching aid, not course content**. It never reaches the learner, and
only has to contain the words the target is looking for.

## What it gave

The native speaker's real answers, replayed:

```
"10.000"  vs  nghìn        True   (was False)
"10.000"  vs  mười         True   (was False)
"10.000"  vs  mười nghìn   True   (was False)
```

## What was checked, because this could have broken the ear

The listening guard decides whether the learner is talking to the tutor rather
than answering, and it consults `resembles_target` — which now sees a longer
string. Checked explicitly: `is_learner_talking` is unchanged for `10.000` in
both `vi` and `en`, because the word count it uses is taken from the raw text.

Six cases added to `smoke_test.py`, one of them **negative** — `10.000` must not
start matching `thích` — so the spelling cannot quietly become a universal
accepter. 17 answer cases pass.

## Not verified

No session has been run with a Vietnamese speaker since the fix. What is
verified is her recorded answers, replayed offline.

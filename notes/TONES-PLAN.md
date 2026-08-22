# The six tones — what a source says, and Meo's plan

**Sources.** `migaku.com/blog/language-fun/vietnamese-tones-overview` for the
per-tone descriptions and the north/south note; a web search across several tone
guides for the English comparison. Quoted rather than paraphrased where it
matters.

**And a source already in the repo, unused:** 95 of the course's 218 items carry
their tone in the authoring note, with a description of the sound —
`tôi: "Thanh ngang — giọng đều, không lên không xuống"`, `là: "Thanh huyền —
giọng xuống nhẹ"`. Nothing reads those.

---

## The six, as the source describes them

```
ngang   "completely flat … does not waver or move"          38 items
sắc     "starts at a lower pitch, hangs flat for just a      23
         moment, and then quickly rises"
huyền   "somewhat flat, like ngang, but drops in pitch       18
         gradually"
nặng    "Vietnamese's lowest tone" and "shortest tone",       8
         ending "in a glottal stop"
hỏi     "it initially drops down, then rises back up"         7
ngã     "drops a bit, then rises" — and breaks in the         2
         throat partway
```

The counts are how often each appears among the annotated items in **this**
course, not in the language.

## The English comparison, and the trap in it

The useful half: English speakers **already** move pitch — the source uses *dude*
said eight different ways. So nobody has to learn to make the sounds.

The trap, and it is why this cannot be taught carelessly:

> *"Vietnamese uses tones to change the meaning of the word. English does not.
> In English, people use intonation to show feelings."*

And specifically:

> *"a rising tone is a sure signal that we're voicing a question … in English,
> but this isn't necessarily the case in Vietnamese. Some syllables just rise by
> nature, whether they're part of a question or not."*

So telling a learner *"sắc is like the end of an English question"* teaches them
to hear a question in every `sắc` word. The comparison has to be **"you already
do this with feeling; here it does something else"**, never **"this tone equals
that English intonation"**.

One more, and it is practical: *"Vietnamese tones require exaggerated pitch
differences compared to English intonation. Practice making the high tones higher
and the low tones lower than feels natural."*

## Why the dialect decides the last pair

> *"Hỏi and ngã … are Vietnamese's two 'dipping' tones. In Southern Vietnam, they
> have merged."*

This course teaches **northern**, so both are kept — and they are the two rarest
in the content, 7 items and 2. A southern course could drop the distinction.

## Meo's plan, and what each part needs

**1 · At the very start: tones exist, listen to Minh.** Not which ones. Today the
tone rule sits at slot 79 and there is nothing before it. ✎ to write.

**2 · Later, two at a time.** The phonetic descriptions and the counts agree on
the pairing:

```
ngang + huyền    flat, and flat-then-dropping — the source defines huyền BY
                 ngang, and they are the two commonest
sắc   + nặng     the fast rise against the lowest and shortest
hỏi   + ngã      the two dippers, the two rarest, the two the south merges
```

✎ to write. The material is the 95 annotated items.

**3 · Reminders during recalls.** Meo: *"des fois quand on demande un mot on peut
rappeler le ton"*. Feasible, because the annotation is per word. ✎ to write.

## What already works and must not be broken

`tone_twin` fires on all 6 tone pairs the course contains — it misses none —
and produces the right moment:

> *"The Vietnamese for address for an elderly woman is bà. bà. **This one is a
> pair with three, which you know — same sounds, different pitch. Listen: ba.
> bà.** Your turn."*

## The hard limit, and it is deliberate

`_bare` strips tone marks, so `ba` and `bà` are the same string to the code:
`answered_target("ba", "bà")` returns **True**. That is not a bug — a beginner and
a recogniser both lose tone first, and Whisper returned `Hồng` for `không` in a
real session today.

**So no tone exercise can ever be scored.** Anything built here is exposure and
noticing, never a graded answer. The strand's current `apply` asks for
`tôi tên là`, which exercises nothing and looks like practice. That is the one
thing to remove.

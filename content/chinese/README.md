# Chinese — not started

A placeholder. The engine is language-agnostic: everything language-specific
lives in this folder, and `tutor.py` never names a language.

## What has to be here before a lesson can run

```
persona.toml        the tutor's voice, and the rules the model is given
NN_topic.toml       lesson files, in teaching order, one topic each
```

Copy `content/vietnamese/persona.toml` and rewrite it. The item files are
numbered so the filename fixes the base order — the sequencer then spaces
categories and honours prerequisites on top of that.

## What an item needs

`name` in the target language, `gloss` in English, `kind` — `atom`, `construction`
or `feature`. A construction adds `literal`, the word-by-word English of the
target order. `SPEC.md` rule 10 is the authority.

## What will be different from Vietnamese, and worth deciding early

- **Tones.** Mandarin has four plus a neutral, and `tone_twin` in `content.py`
  pairs words that differ only in tone. It reads Vietnamese diacritics today and
  would need pinyin or hanzi rules instead.
- **Writing.** The Vietnamese course is voice-only and never shows the script,
  which is a choice its tone rule leans on. Chinese has to decide whether hanzi
  are ever spoken about.
- **The address system.** Vietnamese swaps the word for *I* depending on who is
  in front of you; Mandarin does not, so most of the pronoun strand has no
  counterpart and the plan in `notes/PRONOUN-PLAN.md` does not carry over.
- **Voices.** `voice.py` routes by language, two voices per lesson. A Mandarin
  bundle needs its own pair in Azure.

## What DOES carry over

The method, and everything in `SPEC.md` that is about teaching rather than about
Vietnamese: a word gets two turns, a sentence is climbed rather than asked for
whole, a rule is stated after it has been used, spacing counts in items met
rather than days.

# Spanish — not started

A placeholder. The engine is language-agnostic: everything language-specific
lives in this folder, and `tutor.py` never names a language.

## What has to be here before a lesson can run

```
persona.toml        the tutor's voice, and the rules the model is given
NN_topic.toml       lesson files, in teaching order, one topic each
```

Copy `content/vietnamese/persona.toml` and rewrite it. `SPEC.md` rule 10 is the
authority on what an item carries.

## What will be different from Vietnamese

- **Verbs conjugate.** The Vietnamese course teaches "verbs never change" as a
  tier-1 feature; Spanish needs the opposite, and conjugation is the single
  biggest thing the current engine has never had to model. An item is a word or
  a sentence pattern today — a paradigm is neither.
- **Gender and agreement.** Also absent from Vietnamese, also unmodelled.
- **No tones**, so `tone_twin` simply never fires. Nothing to remove.
- **The learner already half-knows it.** A French or English speaker meets
  hundreds of transparent cognates, which the Vietnamese course never has to
  handle. `hook` — a true fact said before the word — is the field for it, and
  it would fire far more often here than in Vietnamese, where one item of 213
  carries one.

## What DOES carry over

The method: build sentences rather than repeat them, climb a sentence in rungs,
give the literal word order before asking for a sentence whose order differs,
and never retire a word.

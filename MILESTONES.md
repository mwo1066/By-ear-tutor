# Milestones

## 🎉 2026-07-21 — First working two-voice conversation

The first real end-to-end proof: a text response gets split by language,
routed to the correct voice, and actually spoken out loud through real
speakers — not just printed, not just a test file to open manually.

**What's working right now:**
- LLM: `nvidia/nemotron-3-ultra-550b-a55b:free` (OpenRouter, free tier) follows
  the tutor persona reliably — two-voice cast, tone teaching, tool-calling
  for session focus, retry cap on repeated mistakes.
- Spaced repetition (`srs.py`): half-life regression, selects a mix of due
  reviews + new items in curriculum order, updates state after an
  end-of-session LLM assessment pass.
- Content: 30 Vietnamese items (4 lessons) reused from the original memai
  bundle work, Northern/Hanoi dialect, tone named on every mention.
- Voice pairing decided after real comparison testing (not guessing):
  - **Tutor (English)**: `en-US-AmandaMultilingualNeural` (Azure) — picked
    after a ~20-voice batch comparison; Piper (free/local) was tested first
    and rejected after native-speaker feedback flagged real fluency and
    pronunciation problems ("không" mispronounced, choppy word-by-word delivery).
  - **Vietnamese teacher**: `vi-VN-NamMinhNeural` (Azure) — the female
    equivalent (HoaiMy) sounded too robotic.
- `voice.py`: splits a reply into sentence-level runs, detects Vietnamese by
  its diacritics (reliable specifically because the pairing is
  English↔Vietnamese — very little character overlap between the two),
  synthesizes each run with the right voice, plays back via `winsound`.

**Known open items, not blockers:**
- Only tested with typed text standing in for speech — real pronunciation
  assessment (the actual point of the tones work) still needs the
  microphone (STT) side, not built yet.
- Azure free-tier Speech quota is shared across everything — fine at
  personal-use volume, worth watching if usage grows.
- One fallback LLM in the free-tier chain (`nemotron-3-super-120b`) was
  tested and rejected — it broke the two-voice separation rule and its
  tool-calling was unreliable. Only the primary model is trusted for now.
- Git history still has ~190MB of accidentally-committed voice test
  artifacts baked into an earlier commit — needs a history rewrite before
  ever pushing this repo publicly.

**Next up:** microphone input (STT), so the loop actually closes — speak,
get heard, get corrected, not just listen.

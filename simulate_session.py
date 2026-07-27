"""Replays a whole lesson in text, with no microphone and no speech synthesis.

Same persona, same roster, same next_item sequencing and tool handling as the
real session -- only the two ends are swapped: the learner is played by a small
model instead of a person, and turns are printed instead of spoken. Lets a
pedagogical change be judged in one run without anyone having to talk, and
without paying the 20-30s per turn that voice costs.

The learner runs on a different model on purpose: each Groq model has its own
token bucket, so playing the learner does not eat the tutor's budget.

Read-only -- never touches state.json.

Run: python simulate_session.py [number_of_exchanges]
"""
import sys
import time
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from content import (
    load_persona_system_prompt, load_roster, load_personal_items,
    pick_next_index, vocab_set,
)
from srs import ProgressStore
from tutor import (
    CONTENT_DIR, STATE_PATH, MODEL_FALLBACKS, QUEUE_SIZE, REVIEW_POOL_SIZE,
    TOOLS, _format_next_item, load_api_key, stream_llm_reply,
)

LEARNER_MODEL = "llama-3.1-8b-instant"
LEARNER_PROMPT = """You are ROLE-PLAYING a complete beginner taking a spoken Vietnamese lesson. You are the STUDENT, never the teacher.

Output ONLY the words you say out loud. One short line. No stage directions, no explanations, no markdown.

- Asked to say a Vietnamese word you have heard: say it. Get it right most of the time; occasionally slightly wrong.
- Asked to build a sentence: attempt it from the pieces you were given, even clumsily.
- Asked something in English: answer in one short sentence.
- Never teach, never correct the tutor, never say more than one sentence.
"""

# Groq allows ~8000 tokens/min on the tutor model and a full turn costs ~3000,
# so requests have to be spaced or the run dies on 429s halfway through.
SECONDS_BETWEEN_TURNS = 23

_VN_CHARS = set("ăâêôơưđàáảãạằắẳẵặầấẩẫậèéẻẽẹềếểễệìíỉĩịòóỏõọồốổỗộờớởỡợùúủũụừứửữựỳýỷỹỵ")


def _lang_tag(text: str) -> str:
    """Mimics what the real pipeline's speech recognition would report."""
    return "vi" if any(c in _VN_CHARS for c in text.lower()) else "en"


def learner_reply(api_key: str, transcript: list[str]) -> str:
    """The student's next line, from the last few turns only -- deliberately
    kept short so this stays cheap and never competes with the tutor's budget."""
    messages = [
        {"role": "system", "content": LEARNER_PROMPT},
        {"role": "user", "content": "The lesson so far:\n" + "\n".join(transcript[-6:]) + "\n\nWhat do you say next?"},
    ]
    out = []
    for kind, *payload in stream_llm_reply(api_key, [LEARNER_MODEL], messages):
        if kind == "content":
            out.append(payload[0])
    return " ".join("".join(out).split())[:120] or "..."


def main(n_exchanges: int) -> None:
    api_key = load_api_key()
    roster = load_roster(CONTENT_DIR) + load_personal_items(CONTENT_DIR)
    store = ProgressStore(STATE_PATH)  # read-only: save() is never called
    all_names = [i.name for i in roster]
    by_name = {i.name: i for i in roster}

    queue = [by_name[n] for n in store.select_new(all_names, limit=QUEUE_SIZE)]
    review_pool = [by_name[n] for n in store.select_reviews(all_names, date.today(), limit=REVIEW_POOL_SIZE)]
    seen = [i for i in roster if not store.is_new(i.name)]
    vocab = vocab_set(roster)

    messages = [{"role": "system", "content": load_persona_system_prompt(CONTENT_DIR)}]
    messages.append({"role": "user", "content": "[lang:en] Hi, I'm ready."})
    transcript = ["ELEVE: Hi, I'm ready."]
    print("ELEVE : Hi, I'm ready.\n")

    for exchange in range(n_exchanges):
        # One exchange = the tutor talking until it stops asking for tools,
        # then the learner answering. Mirrors _run_turn's chaining.
        for _ in range(5):
            text, tool_calls = "", []
            for kind, *payload in stream_llm_reply(api_key, MODEL_FALLBACKS, messages, tools=TOOLS):
                if kind == "content":
                    text += payload[0]
                elif kind == "tool_calls":
                    tool_calls = payload[0]
            if text.strip():
                print(f"TUTEUR : {text.strip()}\n")
                transcript.append(f"TUTEUR: {text.strip()}")
            messages.append({
                "role": "assistant",
                "content": text or None,
                **({"tool_calls": tool_calls} if tool_calls else {}),
            })
            if not tool_calls:
                break
            for call in tool_calls:
                result = "ok"
                if call["function"]["name"] == "next_item" and queue:
                    item = queue.pop(pick_next_index(queue, seen, vocab))
                    result = _format_next_item(item, seen, review_pool)
                    seen.append(item)
                    print(f"        [item servi : {item.name}]\n")
                messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
            time.sleep(SECONDS_BETWEEN_TURNS)

        reply = learner_reply(api_key, transcript)
        print(f"ELEVE : {reply}\n")
        transcript.append(f"ELEVE: {reply}")
        messages.append({"role": "user", "content": f"[lang:{_lang_tag(reply)}] {reply}"})
        time.sleep(SECONDS_BETWEEN_TURNS)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 12)

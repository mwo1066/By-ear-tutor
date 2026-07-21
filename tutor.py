"""Text-only tutor loop — step 2: prove the brain works before adding voice.

Run: python tutor.py
Type your replies; type /fin to end the session and run the end-of-session
assessment pass that updates spaced-repetition state.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stdin.reconfigure(encoding="utf-8")

from content import load_persona_system_prompt, load_roster, format_items_for_prompt
from srs import ProgressStore, update_after_practice

ROOT = Path(__file__).parent
CONTENT_DIR = ROOT / "content" / "vietnamese"
STATE_PATH = ROOT / "state.json"
ENV_PATH = ROOT / ".env"

# Tried in order — if the first is saturated/rate-limited, fall back to the
# next rather than crash. Found live: Nvidia's free capacity for the 550B
# model can hit "ResourceExhausted" (HTTP 502 wrapped in a 200 body), which
# is a real capacity ceiling, not a burst limit that clears in seconds.
MODEL_FALLBACKS = [
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "google/gemma-4-31b-it:free",
]
RETRYABLE_CODES = {429, 502, 503}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "set_session_focus",
            "description": "Record what the learner wants to work on this session.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {"type": "string", "enum": ["review", "new", "mixed"]},
                    "topic": {"type": "string", "description": "short theme, e.g. food, greetings"},
                },
                "required": ["mode"],
            },
        },
    }
]

ASSESSMENT_TOOL = [
    {
        "type": "function",
        "function": {
            "name": "report_practice_results",
            "description": "Report how the learner did on each item practiced this session.",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "retrievals": {"type": "integer", "description": "successful recalls, not exposures"},
                                "errors": {"type": "integer"},
                                "user_initiated": {"type": "boolean"},
                            },
                            "required": ["name", "retrievals", "errors"],
                        },
                    }
                },
                "required": ["items"],
            },
        },
    }
]


def load_api_key() -> str:
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith("OPENROUTER_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("OPENROUTER_API_KEY not found in .env")


def _try_model(api_key: str, model: str, messages: list[dict], tools: list[dict] | None, retries: int) -> dict | None:
    """Returns the parsed response, or None if this model is exhausted after
    all retries (caller should move on to the next fallback model)."""
    body = {"model": model, "messages": messages}
    if tools:
        body["tools"] = tools
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                parsed = json.loads(resp.read().decode("utf-8"))
            if "error" in parsed:
                # OpenRouter sometimes returns HTTP 200 with an {"error": ...}
                # body (rate limits, or an upstream provider's own capacity
                # ceiling wrapped as code 502) instead of a real HTTP error
                # status — both caught live during testing.
                code = parsed["error"].get("code")
                if code in RETRYABLE_CODES and attempt < retries - 1:
                    wait = 5 * (attempt + 1)
                    print(f"  ({model}: {parsed['error'].get('message', code)} — nouvel essai dans {wait}s...)")
                    time.sleep(wait)
                    continue
                if code in RETRYABLE_CODES:
                    return None  # exhausted retries on a transient error — try the next model
                raise RuntimeError(f"OpenRouter error: {parsed['error']}")
            return parsed
        except urllib.error.HTTPError as e:
            if e.code in RETRYABLE_CODES and attempt < retries - 1:
                wait = 5 * (attempt + 1)
                print(f"  ({model}: HTTP {e.code} — nouvel essai dans {wait}s...)")
                time.sleep(wait)
                continue
            if e.code in RETRYABLE_CODES:
                return None
            body_text = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenRouter error {e.code}: {body_text}") from e
    return None


def call_llm(api_key: str, messages: list[dict], tools: list[dict] | None = None, retries: int = 3) -> dict:
    """Tries each model in MODEL_FALLBACKS in order; only raises if every
    model in the list is unavailable."""
    for model in MODEL_FALLBACKS:
        result = _try_model(api_key, model, messages, tools, retries)
        if result is not None:
            return result
        print(f"  ({model} indisponible, on passe au modele de secours suivant)")
    raise RuntimeError(f"Tous les modeles de secours sont indisponibles: {MODEL_FALLBACKS}")


def run_session():
    api_key = load_api_key()
    persona_prompt = load_persona_system_prompt(CONTENT_DIR)
    roster = load_roster(CONTENT_DIR)
    store = ProgressStore(STATE_PATH)

    today = date.today()
    todays_names = store.select_today([i.name for i in roster], today)
    todays_items = [i for i in roster if i.name in todays_names]

    print(f"--- Items du jour ({len(todays_items)}) ---")
    for i in todays_items:
        print(f"  - {i.name}")
    print()

    system_prompt = persona_prompt + "\n\n" + format_items_for_prompt(todays_items)
    messages = [{"role": "system", "content": system_prompt}]

    print("Tape /fin pour terminer la session et sauvegarder ta progression.\n")

    first = True
    while True:
        if first:
            user_input = "[lang:fr] Salut, je suis pret."
            print(f"(auto) toi: {user_input}")
            first = False
        else:
            user_input = input("toi: ").strip()
            if user_input == "/fin":
                break

        messages.append({"role": "user", "content": user_input})
        result = call_llm(api_key, messages, tools=TOOLS)
        msg = result["choices"][0]["message"]
        messages.append(msg)

        if msg.get("content"):
            print(f"tuteur: {msg['content']}\n")
        for call in msg.get("tool_calls") or []:
            fn = call["function"]
            print(f"  [tool_call] {fn['name']}({fn['arguments']})")
            messages.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": "ok",
            })

    print("\n--- Fin de session : evaluation en cours ---")
    run_assessment(api_key, messages, todays_items, store, today)
    store.save()
    print(f"Progression sauvegardee dans {STATE_PATH}")


def run_assessment(api_key, messages, todays_items, store, today):
    transcript = "\n".join(
        f"{m['role']}: {m.get('content', '')}" for m in messages if m["role"] in ("user", "assistant") and m.get("content")
    )
    items_list = "\n".join(f"- {i.name}" for i in todays_items)
    assess_messages = [
        {
            "role": "system",
            "content": (
                "You are grading a language-learning conversation. Below is the full transcript "
                "and the list of items that were supposed to be practiced. For each item that was "
                "actually touched in the conversation, report how many times the learner SUCCESSFULLY "
                "retrieved/used it correctly (not just heard it) and how many errors they made. "
                "Call report_practice_results with your findings. Omit items never actually touched."
            ),
        },
        {"role": "user", "content": f"Items prevus:\n{items_list}\n\nTranscript:\n{transcript}"},
    ]
    result = call_llm(api_key, assess_messages, tools=ASSESSMENT_TOOL)
    msg = result["choices"][0]["message"]
    tool_calls = msg.get("tool_calls") or []
    if not tool_calls:
        print("  (aucune evaluation retournee)")
        return
    args = json.loads(tool_calls[0]["function"]["arguments"])
    for entry in args.get("items", []):
        existing = store.get(entry["name"])
        if existing is None:
            from srs import ItemState
            existing = ItemState(name=entry["name"])
        updated = update_after_practice(
            existing, today,
            retrievals=entry.get("retrievals", 0),
            errors=entry.get("errors", 0),
            user_initiated=entry.get("user_initiated", False),
        )
        store.set(updated)
        print(f"  {entry['name']}: retrievals={entry.get('retrievals')} errors={entry.get('errors')} "
              f"-> demi-vie={updated.half_life_days:.2f}j")


if __name__ == "__main__":
    run_session()

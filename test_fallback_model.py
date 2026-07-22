"""Validate the FIRST fallback model with the real, current prompt + roster."""
import json
import sys
import urllib.request
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from content import load_persona_system_prompt, load_roster, format_items_for_prompt

ROOT = Path(__file__).parent
CONTENT_DIR = ROOT / "content" / "vietnamese"

MODEL = "nvidia/nemotron-3-super-120b-a12b:free"  # first fallback in the chain

with open(ROOT / ".env", encoding="utf-8") as f:
    api_key = next(l.split("=", 1)[1].strip() for l in f if l.startswith("OPENROUTER_API_KEY="))

persona_prompt = load_persona_system_prompt(CONTENT_DIR)
roster = load_roster(CONTENT_DIR)
todays = roster[:4]  # tôi, tên, là, tôi tên là + [tên riêng]
system_prompt = persona_prompt + "\n\n" + format_items_for_prompt(todays)

TOOLS = [{
    "type": "function",
    "function": {
        "name": "set_session_focus",
        "description": "Record what the learner wants to work on this session.",
        "parameters": {
            "type": "object",
            "properties": {"mode": {"type": "string", "enum": ["review", "new", "mixed"]},
                            "topic": {"type": "string"}},
            "required": ["mode"],
        },
    },
}]


def call(messages):
    body = json.dumps({"model": MODEL, "messages": messages, "tools": TOOLS}).encode("utf-8")
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


messages = [{"role": "system", "content": system_prompt},
            {"role": "user", "content": "[lang:fr] Salut, je suis pret."}]
r1 = call(messages)
msg1 = r1["choices"][0]["message"]
print("=== TURN 1 (ouverture + premier mot avec ton) ===")
print(msg1.get("content"))
print()

messages.append({k: msg1[k] for k in ("role", "content") if msg1.get(k)})
messages.append({"role": "user", "content": "[lang:vi] Ti."})  # deliberately wrong 3 times to test the retry cap
for i in range(3):
    r = call(messages)
    m = r["choices"][0]["message"]
    print(f"=== essai rate #{i+1} ===")
    print(m.get("content"))
    print()
    messages.append({k: m[k] for k in ("role", "content") if m.get(k)})
    messages.append({"role": "user", "content": "[lang:vi] Ti."})

messages.append({"role": "user", "content": "[lang:fr] En fait j'aimerais qu'on travaille la nourriture."})
r_focus = call(messages)
m_focus = r_focus["choices"][0]["message"]
print("=== test tool-calling (focus) ===")
print("Texte:", m_focus.get("content"))
print("Tool calls:", json.dumps(m_focus.get("tool_calls"), ensure_ascii=False))

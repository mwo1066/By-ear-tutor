"""Text-only tutor loop — step 2: prove the brain works before adding voice.

Run: python tutor.py
Type your replies; type /fin to end the session and run the end-of-session
assessment pass that updates spaced-repetition state.
"""
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stdin.reconfigure(encoding="utf-8")

from content import (
    Item, load_persona_system_prompt, load_roster, load_personal_items,
    add_personal_items, pieces_of, pick_next_index, vocab_set, _tokens, _contains_run,
)
from srs import ProgressStore, update_after_practice
from voice import SpeechPipeline

# One pipeline for the whole session: its synth/playback threads have to
# outlive individual turns to keep synthesis running ahead of playback.
# Set once in run_session, read by _run_turn.
voice: SpeechPipeline
from listen import listen_and_transcribe, preload_model

ROOT = Path(__file__).parent
CONTENT_DIR = ROOT / "content" / "vietnamese"
STATE_PATH = ROOT / "state.json"
ENV_PATH = ROOT / ".env"

# groq branch: swapped from OpenRouter's free-tier Nemotron (shared leftover
# capacity, documented slow p95) to Groq's own dedicated LPU hardware --
# free within real rate limits (30k tokens/min, 14400 req/day), not scraps.
API_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
API_KEY_ENV_VAR = "GROQ_API_KEY"
# ONE model, no fallback. The fallback list is a leftover from the OpenRouter
# era, where the free model could be genuinely unavailable for minutes and
# switching to another was the only way through. Groq fails differently: a 429
# is a throughput limit whose bucket refills in under a second, so waiting beats
# degrading. And degrading was not "a slightly worse lesson" -- measured on real
# sessions, every alternative breaks the format outright:
#   llama-3.1-8b-instant    -- writes tool calls as literal text
#                              ("<function=set_session_focus>{...}"), so the tool
#                              never runs AND the tutor's voice reads the code out
#   openai/gpt-oss-20b      -- leaks harmony tokens into tool names
#                              ("next_item<|channel|>commentary" -> HTTP 400)
#   llama-3.3-70b-versatile -- fires unrelated tools with no speech at all
MODEL = "openai/gpt-oss-120b"
MODEL_FALLBACKS = [MODEL]  # kept as a list: callers pass an explicit model in tests
RETRYABLE_CODES = {429, 502, 503}

# Groq sits behind Cloudflare, which blocks urllib's default "Python-urllib/x.x"
# User-Agent as a bot signature (HTTP 403, Cloudflare error code 1010) -- found
# live, fixed by sending a normal browser-looking one instead.
def _api_headers(api_key: str) -> dict:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

# How many items a theme request generates -- they jump to the head of the
# queue and surface at whatever pace the session naturally takes; nothing here
# decides how many happen "today," since there's no fixed-length today.
N_THEME_GENERATE = 4

# Reservoir size: how many candidates select_new prepares up front. Only ever
# revealed one at a time, so this just needs to be large enough that a long
# session never runs dry -- not a target to hit.
QUEUE_SIZE = 30

# The teaching cycle is a state machine in code, not prose in the prompt, and
# next_item is not a tool. Both for the same reason: the model holds no state
# between turns. It re-derived its position by re-reading the conversation
# every time, and drifted -- ten steps in one breath, the same word asked four
# times running, a chain missing a piece. And a tool call cost a round trip:
# the model stopped speaking to ask what to teach, then needed a whole second
# request to say anything, ~6s of dead air per word and a third of all
# requests spent on a "let's continue" filler.
# The sequence is composed in advance anyway (pick_next_index decides it), so
# each turn simply carries its own single instruction.
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
    },
    {
        "type": "function",
        "function": {
            "name": "deprioritize_item",
            "description": (
                "The learner explicitly asked to stop working on a specific word/phrase, or on "
                "a whole theme -- not just a single missed attempt. Doesn't delete anything, "
                "just stops it from resurfacing as often."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "exact item name to stop practicing"},
                    "topic": {"type": "string", "description": "a whole theme to stop practicing, matching a theme requested earlier"},
                },
            },
        },
    },
]

THEME_GENERATION_TOOL = [
    {
        "type": "function",
        "function": {
            "name": "add_vocabulary_items",
            "description": "Propose new Vietnamese items for the requested theme.",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "the Vietnamese word or phrase"},
                                "item_type": {"type": "string", "enum": ["concept", "procedure"]},
                                "category": {"type": "string"},
                                "description": {
                                    "type": "string",
                                    "description": "Vietnamese-language notes: meaning, tone, usage -- same style/language as existing roster items",
                                },
                            },
                            "required": ["name", "item_type", "category", "description"],
                        },
                    }
                },
                "required": ["items"],
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
                                "item_type": {
                                    "type": "string", "enum": ["concept", "procedure"],
                                    "description": "only for a spontaneous item not already tracked -- omit for known roster/personal items",
                                },
                                "category": {"type": "string", "description": "only for a spontaneous new item"},
                                "description": {
                                    "type": "string",
                                    "description": "Vietnamese-language notes (meaning, tone, usage) -- only for a spontaneous new item, so it can be tracked going forward",
                                },
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
    prefix = f"{API_KEY_ENV_VAR}="
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    raise RuntimeError(f"{API_KEY_ENV_VAR} not found in .env")


def _try_model(api_key: str, model: str, messages: list[dict], tools: list[dict] | None, retries: int) -> dict | None:
    """Returns the parsed response, or None if this model is exhausted after
    all retries (caller should move on to the next fallback model)."""
    body = {"model": model, "messages": messages}
    if tools:
        body["tools"] = tools
    req = urllib.request.Request(
        API_BASE_URL,
        data=json.dumps(body).encode("utf-8"),
        headers=_api_headers(api_key),
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
    """Non-streaming call, used by the theme and assessment passes."""
    result = _try_model(api_key, MODEL, messages, tools, retries)
    if result is None:
        raise RuntimeError(f"{MODEL} indisponible apres {retries} tentatives")
    return result


_SENTENCE_BOUNDARY = re.compile(r"([.!?])(\s|$)")


_STREAM_ERRORS = (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError, RuntimeError)


def stream_llm_reply(api_key: str, models: list[str], messages: list[dict], tools: list[dict] | None = None, rounds: int = 5):
    """Streams a reply. Yields ("content", text_delta) chunks as they arrive,
    then a final ("tool_calls", [...]) once the stream ends -- lets the caller
    start speaking the first sentence long before the whole reply has been
    generated, instead of waiting on the entire response.

    On failure it WAITS and retries the same model rather than degrading to a
    lesser one: the usual failure here is a 429 throughput limit whose bucket
    refills in about a second, and every alternative model breaks the lesson
    format (see MODEL). Groq's own Retry-After is honoured when present,
    otherwise the wait backs off, covering roughly a minute across `rounds`.

    A mid-stream failure after content has already been spoken ends the turn
    gracefully instead of retrying, which would just repeat what was said."""
    last_error: Exception | None = None
    for round_num in range(rounds):
        for model in models:
            got_any = False
            tool_calls_acc: dict[int, dict] = {}
            try:
                body = {"model": model, "messages": messages, "stream": True}
                if tools:
                    body["tools"] = tools
                req = urllib.request.Request(
                    API_BASE_URL,
                    data=json.dumps(body).encode("utf-8"),
                    headers=_api_headers(api_key),
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=120) as resp:
                    for raw_line in resp:
                        line = raw_line.decode("utf-8", errors="replace").strip()
                        if not line.startswith("data:"):
                            continue
                        payload = line[len("data:"):].strip()
                        if payload == "[DONE]":
                            break
                        chunk = json.loads(payload)
                        if "error" in chunk:
                            raise RuntimeError(str(chunk["error"]))
                        if not chunk.get("choices"):
                            continue  # some providers send metadata-only chunks with an empty choices list
                        choice = chunk["choices"][0]
                        delta = choice["delta"]
                        if delta.get("content"):
                            got_any = True
                            yield ("content", delta["content"])
                        for tc in delta.get("tool_calls") or []:
                            got_any = True
                            idx = tc["index"]
                            slot = tool_calls_acc.setdefault(
                                idx, {"id": tc.get("id"), "type": "function", "function": {"name": "", "arguments": ""}}
                            )
                            if tc.get("id"):
                                slot["id"] = tc["id"]
                            fn = tc.get("function") or {}
                            if fn.get("name"):
                                slot["function"]["name"] += fn["name"]
                            if fn.get("arguments"):
                                slot["function"]["arguments"] += fn["arguments"]
                                yield ("tool_call_partial", idx, slot["function"]["arguments"])
                        if choice.get("finish_reason"):
                            print(f"  [diag] modele={model} finish_reason={choice['finish_reason']}")
                            if choice["finish_reason"] == "length":
                                print("  [diag] !! reponse TRONQUEE faute de place (max_tokens atteint) -- pas un choix du modele")
                yield ("tool_calls", [tool_calls_acc[i] for i in sorted(tool_calls_acc)])
                return
            except _STREAM_ERRORS as e:
                if got_any:
                    print(f"  (flux interrompu apres un debut de reponse ({e}) -- fin du tour sans reessayer)")
                    yield ("tool_calls", [tool_calls_acc[i] for i in sorted(tool_calls_acc)])
                    return
                last_error = e
                print(f"  ({model}: {e})")
        if round_num < rounds - 1:
            wait = _retry_after_seconds(last_error, default=2 * (round_num + 1))
            print(f"  (nouvel essai dans {wait:.0f}s...)")
            time.sleep(wait)
    raise RuntimeError(f"{models} indisponible apres {rounds} tentatives: {last_error}")


def _retry_after_seconds(error, default: float) -> float:
    """How long Groq says to wait, when it says so.

    A 429 carries Retry-After telling us exactly when the token bucket is
    refilled -- usually a second or two. Guessing longer just wastes lesson
    time, guessing shorter earns another 429.
    """
    header = getattr(error, "headers", None)
    raw = header.get("retry-after") if header else None
    try:
        return min(float(raw), 60.0)
    except (TypeError, ValueError):
        return default


def _extract_complete_json_objects(text: str) -> list[str]:
    """Scans (possibly incomplete, still-streaming) JSON text and returns the
    substrings of every complete top-level object one level below the root --
    e.g. every finished {...} inside a root {"items": [...]} array, even
    while later items are still being generated."""
    objects = []
    depth = 0
    start = None
    in_string = False
    escape = False
    for i, ch in enumerate(text):
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            if depth == 1 and start is None:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 1 and start is not None:
                objects.append(text[start:i + 1])
                start = None
    return objects


def generate_theme_items(api_key: str, topic: str, known_items: list[Item], count: int) -> list[Item]:
    """One-off LLM call producing a batch of new Vietnamese items for a
    learner-requested theme, in the same shape/style as the curated roster."""
    known_names = ", ".join(i.name for i in known_items) or "(aucun)"
    example = known_items[0] if known_items else None
    example_line = (
        f'Exemple de style pour "description" (meme langue, meme niveau de detail): '
        f'"{example.description}"' if example else ""
    )
    prompt_messages = [
        {
            "role": "system",
            "content": (
                "You are proposing new Vietnamese beginner vocabulary/procedure items for a "
                "requested theme, in the exact style of an existing hand-authored roster: "
                "item_type is 'concept' for single words/phrases, 'procedure' for sentence "
                "patterns; description is written IN VIETNAMESE, names the item's tone, and "
                "explains meaning/usage the way a teacher's private notes would -- never in "
                "English or French. Only use words the learner plausibly already knows as "
                "building blocks for any 'procedure' item. Call add_vocabulary_items."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Theme demande par l'apprenant : {topic}\n"
                f"Items deja connus (ne pas dupliquer) : {known_names}\n"
                f"{example_line}\n"
                f"Propose exactement {count} nouveaux items pour ce theme."
            ),
        },
    ]
    items: list[Item] = []
    n_extracted = 0
    for kind, *payload in stream_llm_reply(api_key, MODEL_FALLBACKS, prompt_messages, tools=THEME_GENERATION_TOOL):
        if kind != "tool_call_partial":
            continue
        _idx, args_so_far = payload
        complete = _extract_complete_json_objects(args_so_far)
        for raw_obj in complete[n_extracted:]:
            try:
                entry = json.loads(raw_obj)
            except json.JSONDecodeError:
                continue
            items.append(Item(
                name=entry["name"], item_type=entry["item_type"], category=entry["category"],
                language="vi", description=entry["description"], source="personnel", topic=topic,
            ))
            print(f"    -> item {len(items)}/{count} pret: {entry['name']}")
        n_extracted = len(complete)
    return items


def _vocab_words(items: list[Item]) -> frozenset[str]:
    """Every individual word appearing in the current roster's item names --
    used by voice.py to recognize genuine Vietnamese vocabulary regardless
    of what language the tutor's own voice happens to be using, since we
    author every Vietnamese word ourselves (see voice._is_vietnamese_word)."""
    words: set[str] = set()
    for i in items:
        for w in i.name.split():
            w = w.strip("+[]").lower()
            if w:
                words.add(w)
    return frozenset(words)


# How many isolated recalls close out an item's plan. Three, because that is
# roughly the density measured in the reference course: across its teaching
# stretch, learner-facing recall questions land at about three per new item.
N_RAPIDFIRE = 3
N_VARIATIONS = 3


@dataclass
class Step:
    """One assistant turn, decided by the code rather than by the model.

    The model used to hold the whole nine-step cycle in its head and re-derive
    its position every turn by re-reading the conversation. It has no state, so
    it drifted: ten steps recited in one breath, the same word asked four times
    running, a piece of the recall chain skipped, the lesson teaching one item
    while the sequence sat on another. None of those are possible once a turn
    is a single instruction handed over one at a time.
    """
    kind: str
    target: str | None
    instruction: str


def build_plan(item: Item, pieces: list[Item], recall_targets: list[str]) -> list[Step]:
    """The full turn-by-turn plan for teaching one item.

    Mirrors the reference method: a lone new word is introduced and heard, a
    construction is assembled by re-citing every piece one question at a time,
    scaffolded with the literal word order, then varied, then named, then
    drilled bare.
    """
    plan: list[Step] = []

    if not pieces:
        plan.append(Step(
            "introduce", item.name,
            f"Introduis « {item.name} ». Une accroche d'une phrase SEULEMENT si tu as un fait reel "
            f"a raconter, sinon enchaine directement. Revele le mot en finissant ta phrase dessus, "
            f"Minh le dit DEUX fois seul, puis demande a l'apprenant de le dire. Rien d'autre.",
        ))
    else:
        for piece in pieces:
            plan.append(Step(
                "recall_piece", piece.name,
                f"Demande UNIQUEMENT : « et encore une fois, c'etait quoi {piece.name} ? » "
                f"(dans la langue de l'apprenant). Une seule question, puis tu t'arretes. "
                f"N'annonce pas les autres morceaux, ne dis pas ce qu'il sait deja.",
            ))
        plan.append(Step(
            "scaffold", item.name,
            f"Donne l'ordre litteral vietnamien de « {item.name} » mot a mot dans la langue de "
            f"l'apprenant, puis demande-lui la phrase complete. Ne l'assemble pas a sa place.",
        ))
        plan.append(Step(
            "answer", item.name,
            f"Minh dit la phrase complete correcte DEUX fois. Puis demande la meme structure avec "
            f"un element change. Une seule question.",
        ))
        for _ in range(N_VARIATIONS - 1):
            plan.append(Step(
                "vary", item.name,
                "Meme structure, un seul element change, pose la comme une question et arrete-toi.",
            ))
        if item.item_type == "procedure":
            plan.append(Step(
                "rule", item.name,
                "Enonce maintenant la regle en UNE phrase simple, comme un constat de ce qu'il "
                "vient de produire. Puis enchaine sur une derniere question.",
            ))

    for name in recall_targets[:N_RAPIDFIRE]:
        plan.append(Step(
            "rapidfire", name,
            f"Rappel isole, sans contexte : « et tout seul, c'etait quoi {name} ? » "
            f"Une seule question, puis tu t'arretes.",
        ))
    return plan


def _lesson_note(lesson: dict) -> str:
    """What the model is told this turn: its one instruction, and nothing else.

    Deliberately does NOT restate the cycle, the sequence, or what comes next.
    Everything the model does not need in order to speak this turn is weight it
    pays for on every request.
    """
    lines = ["ETAT DE LA LECON — contexte pour toi seul, jamais prononce a voix haute."]
    step = current_step(lesson)

    if step is None:
        lines.append("Plus rien a enseigner. Termine la session naturellement, ou improvise une petite conversation libre.")
        return "\n".join(lines)

    if lesson["item"] is not None:
        lines.append(f"Item travaille : {lesson['item'].name} — {lesson['item'].description}")
    lines.append(f"CE TOUR-CI, UNIQUEMENT CECI : {step.instruction}")
    return "\n".join(lines)


def current_step(lesson: dict) -> Step | None:
    plan = lesson["plan"]
    return plan[lesson["i"]] if lesson["i"] < len(plan) else None


def start_item(lesson: dict, item: Item | None, seen_items: list[Item], recall_targets: list[str]) -> None:
    """Loads the plan for the next item and rewinds to its first step."""
    lesson["item"] = item
    lesson["i"] = 0
    if item is None:
        lesson["plan"] = []
        return
    lesson["plan"] = build_plan(item, pieces_of(item, seen_items), recall_targets)
    kinds = " -> ".join(s.kind for s in lesson["plan"])
    print(f"  -> item : {item.name}  [{len(lesson['plan'])} tours : {kinds}]")


_QUESTION_MARK = re.compile(r"\?\s*$")


def learner_asked_something(user_text: str) -> bool:
    """A real question from the learner, in their own language.

    The escape hatch. Without it a plan steamrollers anything the learner says
    that is not the expected answer, which is the failure mode of any scripted
    tutor. Their turn still gets used, the plan simply does not advance past a
    step that was never actually done.
    """
    return "[lang:vi]" not in user_text and bool(_QUESTION_MARK.search(user_text.strip()))


def _recall_targets(seen_items: list[Item], skip: Item | None) -> list[str]:
    """Which already-taught words the rapid-fire slots will ask for.

    Deliberately crude for now -- most recently taught first, excluding the
    item being worked. Step two replaces this with a weighted draw on each
    word's level, so a word met once keeps coming back and one met often
    fades, without ever dropping out.
    """
    names = [i.name for i in reversed(seen_items) if skip is None or i.name != skip.name]
    return names


def _take_next(queue_items: list[Item], seen_items: list[Item], vocab: frozenset[str]) -> Item | None:
    """Pops whichever queued item may safely be taught next, or None if dry."""
    if not queue_items:
        return None
    return queue_items.pop(pick_next_index(queue_items, seen_items, vocab))


def _run_turn(api_key, messages, store, roster, queue_items, todays_items, themes_generated_this_session,
              seen_items, vocab, lesson) -> bool:
    """Runs ONE assistant turn: streams the reply, speaks it, advances the
    lesson if the model signalled it moved on, and handles any tool calls.
    Returns True if tool calls were made, meaning the caller should call this
    again right away so the model can react to what the tool returned.

    The lesson state is appended as a fresh system message for THIS request
    only, never kept in history -- otherwise every past turn's stale "item en
    cours" would pile up in the context and contradict the current one.
    """
    t0 = time.monotonic()
    first_chunk_at = None
    buffer = ""
    full_text = ""
    tool_calls_final: list[dict] = []
    note = _lesson_note(lesson)
    request_messages = messages + [{"role": "system", "content": note}]
    for kind, *payload in stream_llm_reply(api_key, MODEL_FALLBACKS, request_messages, tools=TOOLS):
        if kind == "content":
            text = payload[0]
            if first_chunk_at is None:
                first_chunk_at = time.monotonic()
                print(f"  [chrono] premier morceau recu: {first_chunk_at - t0:.1f}s")
            buffer += text
            full_text += text
            while (m := _SENTENCE_BOUNDARY.search(buffer)):
                sentence = buffer[:m.end()].strip()
                buffer = buffer[m.end():]
                if sentence:
                    print(f"tuteur: {sentence}")
                    voice.say(sentence)
        elif kind == "tool_calls":
            tool_calls_final = payload[0]
        # "tool_call_partial" ignored here -- only used by theme generation
        # to show item-by-item progress; the two tools left in conversation
        # have trivial arguments not worth streaming progress for.
    tail = buffer.strip()
    if tail:
        print(f"tuteur: {tail}")
        voice.say(tail)

    if not full_text.strip() and tool_calls_final:
        # Code-level safety net, not a prompt tweak -- tested live: this
        # exact model calls a tool with zero spoken text roughly every
        # time the action is unambiguous, in 6/6 trials, regardless of
        # how forcefully the prompt or the tool's own description asks
        # for accompanying speech. Prompting alone cannot fix this, so
        # a silent tool call gets a minimal filler line instead of dead air.
        filler = random.choice(["Alright, let's continue.", "Okay, moving on.", "Great, let's keep going."])
        print(f"tuteur: {filler}  [filet: tool_call sans texte]")
        voice.say(filler)
        full_text = filler

    voice.wait()  # never open the mic while our own voice is still playing
    print(f"  [chrono] total (reponse + voix): {time.monotonic() - t0:.1f}s")

    msg = {"role": "assistant", "content": full_text or None}
    if tool_calls_final:
        msg["tool_calls"] = tool_calls_final
    messages.append(msg)

    for call in msg.get("tool_calls") or []:
        fn = call["function"]
        print(f"  [tool_call] {fn['name']}({fn['arguments']})")
        args = json.loads(fn["arguments"])
        tool_result = "ok"

        if fn["name"] == "set_session_focus" and args.get("topic"):
            topic = args["topic"].strip()
            if topic.lower() not in themes_generated_this_session:
                themes_generated_this_session.add(topic.lower())
                print(f"  (generation des items pour '{topic}' en cours -- peut prendre du temps sur le modele gratuit...)")
                t_theme = time.monotonic()
                new_items = generate_theme_items(api_key, topic, roster, N_THEME_GENERATE)
                print(f"  [chrono] generation theme: {time.monotonic() - t_theme:.1f}s")
                if new_items:
                    add_personal_items(CONTENT_DIR, new_items)
                    roster.extend(new_items)
                    queue_items[:0] = new_items  # jump the queue: requested content comes next
                    print(f"  (theme '{topic}': {len(new_items)} items generes, ajoutes en tete de la file)")
        elif fn["name"] == "deprioritize_item":
            if args.get("name"):
                store.deprioritize(args["name"])
                print(f"  (deprioritise: {args['name']})")
            if args.get("topic"):
                topic_lower = args["topic"].strip().lower()
                matched = [i.name for i in roster if (i.topic or "").lower() == topic_lower]
                for name in matched:
                    store.deprioritize(name)
                print(f"  (deprioritise: theme '{args['topic']}' -- {len(matched)} item(s))")

        messages.append({
            "role": "tool",
            "tool_call_id": call["id"],
            "content": tool_result,
        })

    return bool(tool_calls_final)


# Safety cap on consecutive tool-only turns (no new user input in between).
# Rare now that only set_session_focus and deprioritize_item remain, but it
# still stops a pathological loop from running forever without handing control
# back to the learner.
MAX_CHAINED_TOOL_TURNS = 5


def _conversation_loop(api_key, messages, store, roster, queue_items, todays_items, themes_generated_this_session,
                       seen_items, vocab, lesson):
    """The live back-and-forth until interrupted (Ctrl+C). Pulled out of
    run_session so a fatal error here (e.g. the free model staying
    saturated through every retry) can still be caught by the caller and
    the session saved, instead of losing all progress to an unhandled
    crash mid-loop. No input() between turns -- found live: the only time
    Enter should matter is starting the session; every per-turn keypress
    was a chance to get stuck waiting on a forgotten key. Ctrl+C ends the
    session now, and still saves cleanly via run_session's finally block."""
    turns_done = 0
    while True:
        if turns_done == 0:
            user_input = "[lang:en] Hi, I'm ready."
            print(f"(auto) toi: {user_input}")
        else:
            t0 = time.monotonic()
            user_input = listen_and_transcribe()
            print(f"  [chrono] ecoute+transcription: {time.monotonic() - t0:.1f}s")
            if not user_input:
                print("  (rien entendu, on reecoute)")
                continue
            print(f"toi (transcrit): {user_input}")

        # The learner's turn is what closes the step the tutor just set up, so
        # the plan advances HERE, not after the tutor speaks. Turn zero is the
        # opening speech: it has no step to close and must not load an item, or
        # the tutor greets and teaches in the same breath.
        if turns_done > 0:
            if learner_asked_something(user_input):
                print("  (question de l'apprenant -- l'etape est rejouee apres reponse)")
            else:
                lesson["i"] += 1
            if current_step(lesson) is None:
                item = _take_next(queue_items, seen_items, vocab)
                if item is not None:
                    todays_items.append(item)
                    seen_items.append(item)
                start_item(lesson, item, seen_items, _recall_targets(seen_items, item))

        messages.append({"role": "user", "content": user_input})
        for _ in range(MAX_CHAINED_TOOL_TURNS):
            had_tool_calls = _run_turn(api_key, messages, store, roster, queue_items, todays_items,
                                       themes_generated_this_session, seen_items, vocab, lesson)
            if not had_tool_calls:
                break  # model gave its final spoken reply for this turn -- back to listening
        turns_done += 1


def run_session():
    print("Demarrage de la session...")
    api_key = load_api_key()
    persona_prompt = load_persona_system_prompt(CONTENT_DIR)
    print("  (preparation du modele de reconnaissance vocale...)")
    preload_model()
    # Curated roster FIRST. It is a composed progression -- atoms, then the
    # construction that assembles them -- whereas live-generated personal items
    # are mostly whole phrases. Found live: prepending personal items opened a
    # brand-new session on "Rất vui được gặp bạn", a five-word phrase whose
    # words had never been taught. pick_next_index guards this properly now;
    # the order here just stops the guard from having to fight the queue.
    roster = load_roster(CONTENT_DIR) + load_personal_items(CONTENT_DIR)
    store = ProgressStore(STATE_PATH)

    today = date.today()
    by_name = {i.name: i for i in roster}
    all_names = [i.name for i in roster]
    # Forward sequence is NEW items in roster order only. Due reviews are not
    # drawn as items -- they ride along in the lesson note as the pieces to
    # re-cite, which is where revision belongs in this method.
    queue_items = [by_name[n] for n in store.select_new(all_names, limit=QUEUE_SIZE)]
    todays_items: list[Item] = []  # grows as the sequence advances -- never pre-decided
    seen_items = [i for i in roster if not store.is_new(i.name)]  # everything ever taught, roster order
    vocab = vocab_set(roster)
    # An empty plan means the opening turn: the tutor greets, and the first
    # item is loaded only once that turn is behind us.
    lesson = {"item": None, "plan": [], "i": 0}
    global voice
    voice = SpeechPipeline(_vocab_words(roster))
    themes_generated_this_session: set[str] = set()

    print(f"--- Reservoir prepare : {len(queue_items)} items a enseigner ---")

    # Skip-intro instruction removed -- found live: it got over-applied, the
    # model dropped ALL spoken content, not just the opening speech. Keeping
    # the intro every run is more reliable, even if repetitive while testing.

    messages = [{"role": "system", "content": persona_prompt}]

    print("Ctrl+C pour terminer la session et sauvegarder ta progression -- plus besoin d'Entree apres celle-ci.\n")

    try:
        _conversation_loop(api_key, messages, store, roster, queue_items, todays_items,
                           themes_generated_this_session, seen_items, vocab, lesson)
    finally:
        # Runs even on a fatal crash (e.g. the free model staying saturated
        # through every retry) -- found live: without this, a mid-session
        # outage lost the whole session, since saving only ever happened
        # after a clean /fin.
        print("\n--- Fin de session : evaluation en cours ---")
        try:
            run_assessment(api_key, messages, todays_items, store, today, roster)
        except Exception as e:
            print(f"  (evaluation impossible ({e}) -- la progression brute est quand meme sauvegardee)")
        store.save()
        print(f"Progression sauvegardee dans {STATE_PATH}")


def run_assessment(api_key, messages, todays_items, store, today, known_items):
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
                "If the learner asked about or practiced a genuinely new word/phrase that is NOT in "
                "the planned list, report it too, and additionally fill in item_type, category, and a "
                "Vietnamese-language description (meaning, tone, usage) so it can be tracked going "
                "forward -- omit those three fields for items already in the planned list. "
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
    known_names = {i.name for i in known_items}
    new_personal_items = []
    for entry in args.get("items", []):
        if entry["name"] not in known_names and entry.get("description"):
            new_personal_items.append(Item(
                name=entry["name"], item_type=entry.get("item_type", "concept"),
                category=entry.get("category", "vocabulary"), language="vi",
                description=entry["description"], source="personnel",
            ))
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
    if new_personal_items:
        add_personal_items(CONTENT_DIR, new_personal_items)
        print(f"  ({len(new_personal_items)} nouveau(x) mot(s) spontane(s) ajoute(s) au suivi personnel)")


if __name__ == "__main__":
    run_session()

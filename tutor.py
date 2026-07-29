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
from srs import ProgressStore
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

# A turn is three sentences at most, so this is a ceiling against runaway
# reasoning rather than a real constraint on what gets said.
MAX_TOKENS_PER_TURN = 500

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
            "name": "remember_word",
            "description": (
                "The learner explicitly asked how to say something that is not part of the course, "
                "and you told them. Call this so the word joins their vocabulary and comes back "
                "later like any other. Only on a real request from them -- never for a word you "
                "merely mentioned, and never for something you suspect was misheard."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "the Vietnamese word or phrase, correctly spelled"},
                    "description": {
                        "type": "string",
                        "description": "Vietnamese-language notes (meaning, usage), same style as the course's own items",
                    },
                },
                "required": ["name", "description"],
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
            reasoning_chars = 0
            tool_calls_acc: dict[int, dict] = {}
            try:
                body = {
                    "model": model,
                    "messages": messages,
                    "stream": True,
                    # Bounded on purpose. gpt-oss reasons on a separate channel
                    # before it says anything, and an unbounded budget lets it
                    # think until it runs out with nothing spoken -- seen live
                    # as finish_reason=length and total silence. A turn here is
                    # three sentences at most, so this ceiling is generous.
                    "max_tokens": MAX_TOKENS_PER_TURN,
                    # Same reason: these turns are one instruction each, there
                    # is nothing to deliberate about.
                    "reasoning_effort": "low",
                }
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
                        if delta.get("reasoning"):
                            reasoning_chars += len(delta["reasoning"])
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
                            extra = f", raisonnement={reasoning_chars} car" if reasoning_chars else ""
                            print(f"  [diag] modele={model} finish_reason={choice['finish_reason']}{extra}")
                            if choice["finish_reason"] == "length" and not got_any:
                                print("  [diag] !! budget epuise SANS un mot dit -- le modele a raisonne dans le vide")
                            elif choice["finish_reason"] == "length":
                                print("  [diag] !! reponse coupee en cours de route (max_tokens atteint)")
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
        # Two turns, not one. A single turn meant a word was revealed, heard
        # once and gone -- three of them stacked back to back before anything
        # was combined, which is what made the lesson feel like it was skimming.
        # The reference course does the same thing: it gives the word, then
        # comes straight back with "again, the word for X is ...".
        plan.append(Step(
            "introduce", item.name,
            f"Introduce the word {item.name}. One sentence of real context only if you have a true "
            f"fact worth telling, otherwise go straight in. End a sentence on the word itself, have "
            f"Minh say it twice alone, then ask the learner to say it. Nothing else.",
        ))
        plan.append(Step(
            "settle", item.name,
            f"Stay on {item.name} one more turn. React in a few words to what they just said, have "
            f"Minh say it once more, and ask for it again. Do not introduce anything new.",
        ))
    else:
        for piece in pieces:
            plan.append(Step(
                "recall_piece", piece.name,
                f"Ask the learner what {piece.name} was. One question, in their own language, then "
                f"stop. Do not name the other pieces, do not say what they already know.",
            ))
        plan.append(Step(
            "scaffold", item.name,
            f"Give the literal Vietnamese word order of {item.name}, word by word in the learner's "
            f"language, then ask them for the whole sentence. Do not assemble it for them.",
        ))
        plan.append(Step(
            "answer", item.name,
            "Have Minh say the correct full sentence twice. Then ask for the same structure with one "
            "element swapped. One question.",
        ))
        for _ in range(N_VARIATIONS - 1):
            plan.append(Step(
                "vary", item.name,
                "Same structure, one element swapped, asked as a question. Then stop.",
            ))
        if item.item_type == "procedure":
            plan.append(Step(
                "rule", item.name,
                "State the pattern now, in one plain sentence, as something they just noticed. Then "
                "one last question.",
            ))

    for name in recall_targets[:N_RAPIDFIRE]:
        plan.append(Step(
            "rapidfire", name,
            f"Bare recall, no context: ask what {name} was, on its own. One question, then stop.",
        ))
    return plan


def _lesson_note(lesson: dict) -> str:
    """What the model is told this turn: its one instruction, and nothing else.

    Deliberately does NOT restate the cycle, the sequence, or what comes next.
    Everything the model does not need in order to speak this turn is weight it
    pays for on every request.
    """
    lines = [
        "LESSON STATE — for you only. This is a directive, never a script: do not read any of it "
        "aloud and do not repeat its wording. Say it your own way, in the learner's language."
    ]
    step = current_step(lesson)

    if step is None:
        # An empty plan means opposite things at the two ends of a session --
        # nothing started yet, or nothing left -- and conflating them made the
        # tutor open with "let's wrap up for today" on the very first turn.
        if lesson["started"]:
            lines.append("Nothing left to teach. Wind the session down naturally, or make small talk.")
        else:
            lines.append(
                "THIS TURN IS THE OPENING SPEECH AND NOTHING ELSE. Teach nothing, say no Vietnamese "
                "word to be learned, end on your question and stop."
            )
        return "\n".join(lines)

    if lesson["item"] is not None:
        lines.append(f"Item being worked: {lesson['item'].name} — {lesson['item'].description}")
    lines.append(f"THIS TURN, THIS ONLY: {step.instruction}")
    return "\n".join(lines)


def current_step(lesson: dict) -> Step | None:
    plan = lesson["plan"]
    return plan[lesson["i"]] if lesson["i"] < len(plan) else None


def start_item(lesson: dict, item: Item | None, seen_items: list[Item], store: ProgressStore) -> None:
    """Loads the plan for the next item and rewinds to its first step."""
    lesson["item"] = item
    lesson["i"] = 0
    lesson["started"] = True
    if item is None:
        lesson["plan"] = []
        return
    pieces = pieces_of(item, seen_items)
    store.mark_introduced(item.name)
    lesson["plan"] = build_plan(item, pieces, _recall_targets(store, item, pieces))
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


def _recall_targets(store: ProgressStore, item: Item | None, pieces: list[Item]) -> list[str]:
    """Which already-met words the bare recall slots will ask for.

    Drawn by level, so the least consolidated word is likeliest and a
    well-drilled one turns up rarely without ever dropping out. The item being
    taught and the pieces its own chain already covers are excluded -- asking
    for a word twice in the same handful of turns wastes a slot.
    """
    exclude = {p.name for p in pieces}
    if item is not None:
        exclude.add(item.name)
    return store.draw_recalls(N_RAPIDFIRE, exclude=exclude)


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

        if fn["name"] == "remember_word" and args.get("name"):
            # Captured live, on the learner's own request, instead of by a
            # grader re-reading the transcript afterwards -- which is how
            # "Je suis prêt", a mis-transcribed "I'm ready", once became a
            # Vietnamese vocabulary item.
            word = Item(
                name=args["name"].strip(),
                item_type="concept",
                category="spontane",
                language="vi",
                description=args.get("description", "").strip(),
                source="personnel",
            )
            if store.is_new(word.name):
                add_personal_items(CONTENT_DIR, [word])
                roster.append(word)
                seen_items.append(word)
                store.mark_introduced(word.name)
                store.save()
                print(f"  (mot retenu : {word.name})")
        elif fn["name"] == "set_session_focus" and args.get("topic"):
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
                # The step the learner just answered is done. If it asked for a
                # word, that IS the exposure -- recorded here, where the code
                # knows exactly what it asked, instead of being reconstructed
                # afterwards by a model re-reading the transcript.
                done = current_step(lesson)
                if done is not None and done.kind in ("recall_piece", "rapidfire", "settle") and done.target:
                    store.record_recall(done.target)
                    print(f"  [niveau] {done.target} -> {store.level(done.target)}")
                lesson["i"] += 1
            if current_step(lesson) is None:
                item = _take_next(queue_items, seen_items, vocab)
                if item is not None:
                    todays_items.append(item)
                    seen_items.append(item)
                start_item(lesson, item, seen_items, store)
                store.save()  # progress survives a crash without waiting for the end

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
    lesson = {"item": None, "plan": [], "i": 0, "started": False}
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
        store.save()
        print("\n--- Fin de session ---")
        print(store.summary())
        print(f"\nProgression sauvegardee dans {STATE_PATH}")


if __name__ == "__main__":
    run_session()

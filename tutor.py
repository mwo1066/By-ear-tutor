"""The lesson loop: plans each turn, speaks it, listens, and moves on.

Voice only. Nothing is typed and nothing is read: the tutor speaks, the mic
opens on its own, and the recording stops when you go quiet. Ctrl+C ends the
session and saves.

The teaching sequence is decided here rather than by the model, one turn at a
time -- see build_plan. The model supplies the words, never the structure.

Run: python tutor.py
"""
import difflib
import json
import os
import random
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stdin.reconfigure(encoding="utf-8")

from content import (load_course, 
    Item, load_persona_system_prompt, load_roster, load_personal_items,
    add_personal_items, address_situations, ADDRESS_TERMS, askable, check_roster, derive_pieces,
    drawable,
    has_person_slot, is_teachable, pieces_of, pick_next_index, tone_twin,
)
from srs import ProgressStore
import learner as learner_module
import voice as voice_module
from voice import SpeechPipeline

# One pipeline for the whole session: its synth/playback threads have to
# outlive individual turns to keep synthesis running ahead of playback.
# Set once in run_session, read by _run_turn.
voice: SpeechPipeline
from listen import listen_and_transcribe

ROOT = Path(__file__).parent
CONTENT_DIR = ROOT / "content" / "vietnamese"
STATE_PATH = ROOT / "state.json"
# Who the learner is, kept apart from what they know: different lifetimes, and
# state.json is a flat map of item name to level with no room inside it.
LEARNER_PATH = ROOT / "learner.json"
ENV_PATH = ROOT / ".env"

# Groq, after OpenRouter's free tier proved too slow to hold a conversation.
# Its free limit is real and tight: measured at 8000 tokens per minute for the
# model below, which at roughly 3000 tokens a request allows about two and a
# half turns a minute. Exceeding it earns a Retry-After of a minute or more,
# so keeping the system prompt small is a pacing concern, not tidiness.
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

# Nothing to do with a spoken turn: this one emits a JSON tool call carrying
# four items, each with a paragraph of Vietnamese notes. Measured on the
# generation that crashed a live session: ~200 tokens an item plus the JSON
# frame, against the 500-token speaking ceiling it was inheriting. Truncated
# JSON is not a degraded result, it is an HTTP 400 -- so this is sized with
# room rather than trimmed to fit.
THEME_GENERATION_MAX_TOKENS = 2500

# (The old QUEUE_SIZE reservoir cap lived here. It is gone -- see
# ProgressStore.select_new for why a buffer size turned into a lid on the
# course.)

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
                    "gloss": {
                        "type": "string",
                        "description": (
                            "what it means, in plain English, as short as possible -- this is what a later "
                            "recall will ask them for, so it must be a natural English word or phrase "
                            "('I / me', 'to want'), never a grammatical description"
                        ),
                    },
                    "description": {
                        "type": "string",
                        "description": "Vietnamese-language notes (meaning, usage), same style as the course's own items",
                    },
                },
                "required": ["name", "gloss", "description"],
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
    {
        "type": "function",
        "function": {
            "name": "remember_learner",
            "description": (
                "The learner said something about themselves -- their name, their age, or whether "
                "they are a man or a woman. Call this so the course can teach THEIR person-words "
                "instead of the neutral ones. Only for what they actually said: never infer a "
                "gender from a name or an age from a voice."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "their given name, as they said it"},
                    "gender": {"type": "string", "enum": ["male", "female"]},
                    "age": {"type": "integer", "description": "their age in years"},
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
                                "kind": {
                                    "type": "string",
                                    "enum": ["atom", "construction"],
                                    "description": (
                                        "'atom' for one thing said as a unit (a multi-word block like 'cà phê' "
                                        "is still an atom); 'construction' for a sentence assembled out of items "
                                        "the learner already knows"
                                    ),
                                },
                                "gloss": {
                                    "type": "string",
                                    "description": (
                                        "what it means in plain English, as short as possible -- spoken aloud as "
                                        "the question a recall asks, so never a grammatical description"
                                    ),
                                },
                                # `pieces` is deliberately NOT asked for. The
                                # code reads it off the name against the roster
                                # (content.derive_pieces), which reproduces all
                                # five hand-written constructions exactly, while
                                # the model got 8 of its 13 wrong -- one piece
                                # for an eight-word sentence, or none at all.
                                # A field the code can compute is not a field to
                                # have the model guess.
                                #
                                # `literal` stays: word-by-word English of the
                                # Vietnamese order is a translation, which is
                                # the model's job and not derivable here.
                                # Nullable, because it says null on an atom
                                # rather than leaving the key out, and a
                                # non-nullable schema turns that into HTTP 400,
                                # killing the whole batch over a field that did
                                # not apply.
                                "literal": {
                                    "type": ["string", "null"],
                                    "description": "constructions only: word-by-word English of the Vietnamese order, e.g. 'I name is [name]'",
                                },
                                "category": {"type": "string"},
                                "description": {
                                    "type": "string",
                                    "description": "Vietnamese-language notes: meaning, tone, usage -- same style/language as existing roster items",
                                },
                            },
                            "required": ["name", "item_type", "kind", "gloss", "category", "description"],
                        },
                    }
                },
                "required": ["items"],
            },
        },
    },
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
                    print(f"  ({model}: {parsed['error'].get('message', code)} — retrying in {wait}s...)")
                    time.sleep(wait)
                    continue
                if code in RETRYABLE_CODES:
                    return None  # exhausted retries on a transient error — try the next model
                raise RuntimeError(f"OpenRouter error: {parsed['error']}")
            return parsed
        except urllib.error.HTTPError as e:
            if e.code in RETRYABLE_CODES and attempt < retries - 1:
                wait = 5 * (attempt + 1)
                print(f"  ({model}: HTTP {e.code} — retrying in {wait}s...)")
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
        raise RuntimeError(f"{MODEL} unavailable after {retries} attempts")
    return result


_SENTENCE_BOUNDARY = re.compile(r"([.!?])(\s|$)")


_STREAM_ERRORS = (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError, RuntimeError)


class PermanentAPIError(RuntimeError):
    """A refusal that will refuse again. Retrying it only burns budget.

    Found live: theme generation asked for four items on a 500-token ceiling
    meant for three spoken sentences, so the tool-call JSON came back truncated
    and Groq answered 400 tool_use_failed. The retry loop treated it like a rate
    limit and sent the same doomed request five times, then crashed the lesson.
    A 4xx that is not 429 means the request itself is wrong; only the caller can
    fix it.
    """


def _permanent(error: dict) -> bool:
    status = error.get("status_code")
    return isinstance(status, int) and 400 <= status < 500 and status != 429


def stream_llm_reply(api_key: str, models: list[str], messages: list[dict], tools: list[dict] | None = None,
                     rounds: int = 5, max_tokens: int = None):
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
                    # three sentences at most, so this ceiling is generous --
                    # but it is a SPEAKING budget, and callers that generate
                    # structured data instead must raise it (see
                    # generate_theme_items, which was silently truncated by it).
                    "max_tokens": max_tokens or MAX_TOKENS_PER_TURN,
                }
                # Model-specific, not universal. gpt-oss reasons on a separate
                # channel and needs this capped; every other model on the same
                # endpoint rejects the field outright with HTTP 400 -- which is
                # how the learner in simulate_session.py, a llama, had been
                # dead since the day this line was added. A parameter that
                # belongs to one model must be sent to that model only.
                if "gpt-oss" in model:
                    body["reasoning_effort"] = "low"
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
                            if _permanent(chunk["error"]):
                                raise PermanentAPIError(str(chunk["error"]))
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
                                print("  [diag] !! budget spent WITHOUT a word said -- the model reasoned into the void")
                            elif choice["finish_reason"] == "length":
                                print("  [diag] !! reply cut off mid-sentence (max_tokens reached)")
                yield ("tool_calls", [tool_calls_acc[i] for i in sorted(tool_calls_acc)])
                return
            except PermanentAPIError:
                raise  # the request is malformed; five more of it changes nothing
            except urllib.error.HTTPError as e:
                # Same rule as _permanent, on the other shape an error arrives
                # in. Handling only the in-stream chunk let a 400 be retried
                # five times before crashing -- seen on the very run meant to
                # exercise this.
                if 400 <= e.code < 500 and e.code != 429:
                    raise PermanentAPIError(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:200]}")
                if got_any:
                    yield ("tool_calls", [tool_calls_acc[i] for i in sorted(tool_calls_acc)])
                    return
                last_error = e
                print(f"  ({model}: {e})")
            except _STREAM_ERRORS as e:
                if got_any:
                    print(f"  (stream broke after speech had started ({e}) -- ending the turn without retrying)")
                    yield ("tool_calls", [tool_calls_acc[i] for i in sorted(tool_calls_acc)])
                    return
                last_error = e
                print(f"  ({model}: {e})")
        if round_num < rounds - 1:
            wait = _retry_after_seconds(last_error, default=2 * (round_num + 1))
            print(f"  (retrying in {wait:.0f}s...)")
            time.sleep(wait)
    raise RuntimeError(f"{models} unavailable after {rounds} attempts: {last_error}")


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
    known_names = ", ".join(i.name for i in known_items) or "(none)"
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
                "English. gloss, by contrast, is the plain English meaning, and it is what the "
                "tutor will read aloud when asking for the word later, so keep it short and "
                "natural. A 'construction' may only list pieces that appear verbatim in the "
                "known-items list; if you cannot build it from those, make it an atom instead. "
                "Call add_vocabulary_items."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Theme requested by the learner: {topic}\n"
                f"Items already known (do not duplicate): {known_names}\n"
                f"{example_line}\n"
                f"Propose exactly {count} new items for this theme."
            ),
        },
    ]
    items: list[Item] = []
    n_extracted = 0
    for kind, *payload in stream_llm_reply(api_key, MODEL_FALLBACKS, prompt_messages,
                                           tools=THEME_GENERATION_TOOL,
                                           max_tokens=THEME_GENERATION_MAX_TOKENS):
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
                # `or` rather than a default: the key IS present, carrying null,
                # so .get(key, default) hands back None and the fields below
                # would iterate or format it.
                gloss=entry.get("gloss") or "", kind=entry.get("kind") or "atom",
                # Read off the name against the roster, never taken from the
                # model -- see the schema note above, and derive_pieces.
                pieces=derive_pieces(entry["name"], known_items),
                literal=entry.get("literal") or "",
            ))
            print(f"    -> item {len(items)}/{count} ready: {entry['name']}")
        n_extracted = len(complete)
    return items


def _vocab_words(items: list[Item]) -> frozenset[str]:
    """Roster words that carry a Vietnamese diacritic, for voice routing.

    ONLY the accented ones. A bare-ASCII Vietnamese word is very often an
    English word too, and this set decides which voice speaks: measured after a
    frequency list was imported, the roster contributed so, do, ta, con, ra, da,
    ai, cao, hay, nay, sao, tin, xe and cha -- and the tutor's own "So how would
    you say it?" came out with Minh pronouncing "So", which is a random
    Vietnamese syllable dropped into an English sentence.

    voice.py already treats a diacritic as conclusive, so nothing is lost:
    accented words are caught either way, and the handful of bare-ASCII
    Vietnamese words worth routing (anh, em, ngon) stay in the hand-vetted
    _VN_BARE_WORDS. That list was always explicit that ambiguous words must not
    join it; a bulk import is not a reason to overrule its author.
    """
    words: set[str] = set()
    for i in items:
        for w in i.name.split():
            w = w.strip("+[]").lower()
            if w and voice_module._has_vn_marker(w):
                words.add(w)
    return frozenset(words)


# How many isolated recalls close out an item's plan. Three is the density
# measured in the reference course -- across its teaching stretch, learner-facing
# recall questions land at about three per new item -- so it stays the MEAN, and
# what varies is the spread around it.
#
# Fixed at exactly three, every simple word cost the same five turns, and an
# attentive learner learns the cadence: after the second recall there is one
# left. They start answering to the rhythm instead of the question. draw_recalls
# already refuses to be predictable about WHICH words come back; the same
# argument had never been applied to HOW MANY.
#
# And the count is motivated rather than random. A construction has just made
# them re-say every one of its pieces, so the reviewing is done -- piling three
# more on top is repetition without purpose. A lone word reviewed nothing, and a
# rule had them say nothing at all, so those are where the recalls belong.
N_RAPIDFIRE = 3

# A rule is put to work by CLIMBING one sentence, not by being asked for whole
# sentences repeatedly. This is the reference method's move, named by Meo while
# testing: "he always starts calm -- how do you say don't want, then I don't
# want, then I don't want to eat."
#
# It also settles a conflict. The first version asked for a DIFFERENT sentence
# each time, because live the same question came four turns running. But the
# defect there was the identical QUESTION, not the repeated sentence: a ladder
# stays on one sentence and asks something new at every rung, which is both
# closer to the method and further from what went wrong.
# How many of a rule's own words get recalled before it is assembled. Capped so
# a rule with six pieces does not become a vocabulary drill with a rule attached.
MAX_FEATURE_PIECE_RECALLS = 3


def rapidfire_count(item: Item, pieces: list[Item]) -> int:
    """How many bare recalls this item's plan ends with.

    Never a fixed number, never a random one either: a base that follows what
    the turn just did, plus one step of spread so the cadence cannot be learned.
    """
    if item.kind == "construction":
        base = 1 if pieces else 2      # its chain already re-asked every piece
    elif item.kind == "feature":
        # Was 4, on the reasoning that nothing had been said back so this WAS
        # the practice. No longer true: a feature now carries its own piece
        # recalls and an application, so four unrelated recalls on top made it
        # the longest item in the course for no added learning.
        base = 2
    else:
        # The measured average of the reference course, and the only one of the
        # three bases that IS that average -- a word has revised nothing, so it
        # gets the full count. It was written 3 here while N_RAPIDFIRE sat
        # unused a few lines up, so changing the constant changed nothing and
        # SPEC 17 had to warn against editing it. Now it means what it says.
        base = N_RAPIDFIRE
    return max(1, base + random.choice((-1, 0, 0, 1)))
# At most one application among an item's closing recalls. See _recall_targets
# for the measurement that set it at one.
MAX_APPLICATIONS_PER_ITEM = 1


def _apply_material(item: Item, known: list[Item]) -> tuple[str, str]:
    """What a feature's application works ON, and what it asks FOR, in English.

    One place, because two turns need it: the application that follows a
    feature's introduction, and the one drawn later as revision. They word the
    turn differently -- the first can say "now put THOSE words together" because
    the pieces were just re-asked, the second has to name its own material --
    but the CHOICE of material is the same decision and must not drift apart.

    Sorted by HOW MUCH is shared, not by who comes first. The yes/no question
    rule (có, không) was pinned to "không phải là + [danh từ]", which shares
    only "không" and is about negation -- so every rung asked for "not a
    student" while the rule being taught was how to ask a question.

    The ask side never contains Vietnamese: the instruction said "ask it in
    English" in six wordings and the turn still ended on "How would you say
    cơm ngon to Minh?".
    """
    by_name = {i.name: i for i in known}
    related = sorted(
        (c for c in known
         if c.kind == "construction" and set(c.pieces) & set(item.pieces)),
        key=lambda c: -len(set(c.pieces) & set(item.pieces)))
    pinned = related[0] if related else None
    if pinned:
        return (f' Work on THIS sentence and no other: "{pinned.gloss}" ({pinned.name}).',
                speakable(pinned.gloss))
    if item.pieces:
        # No taught sentence touches this feature, so its OWN words are the
        # material. Handing over the list of sentences instead produced the
        # worst turn of the session: asked to show that an adjective needs no
        # "là", the model chose "I am not a student" -- a noun, which REQUIRES
        # là, so the application demonstrated the opposite of the rule. Naming
        # the words it must build from cannot do that.
        words = ", ".join(f'"{p}"' for p in item.pieces)
        glosses = [speakable(by_name[p].gloss) for p in item.pieces
                   if p in by_name and by_name[p].gloss][:2]
        return (f" Build the sentence out of these words, which are what this rule is about: "
                f"{words}. Nothing else, and never a word they have not been taught.",
                " and ".join(glosses) + ", put together the way the rule says"
                if len(glosses) == 2 else "")
    return (_known_sentences_note(known) +
            " Pick ONE of them that this rule can visibly change, and stay on it.", "")


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

    A step names BOTH sides of the pair. Handing over only the Vietnamese left
    the model to supply the English side of its own question, and measured live
    it as often simply reused the target -- "So how would you say là?", a
    question that states its answer. `answer_is_target` marks the turns where
    the Vietnamese must not be uttered at all, because it is what is being
    asked for.

    `instruction` is what a model turn is told to do. `ask` is the same
    meaning side, but as a sentence can actually pronounce it -- set only on
    the steps the code speaks itself (see scripted_turn), where there is no
    model in between to smooth "I / me" into something sayable.
    """
    kind: str
    target: str | None
    instruction: str
    answer_is_target: bool = False
    ask: str = ""
    hook: str = ""
    literal: str = ""
    # An already-taught word this one differs from ONLY in tone, when there is
    # one. Carried on the step rather than looked up when speaking, so the turn
    # is decided in one place -- and computed, never authored: the tone is in
    # the diacritic.
    twin: str = ""
    twin_gloss: str = ""


def _ask_for(item: Item) -> str:
    """How a question refers to the item, from the side the learner must NOT
    be given. The gloss is the whole point; falling back to the Vietnamese name
    would reintroduce the self-answering question, so a missing gloss falls
    back to the item's own notes instead and is reported at startup."""
    if item.gloss:
        return f'"{item.gloss}"'
    return f"the item described as: {item.description[:120]}"


# A gloss is written to be read, and the model used to be the thing that turned
# it into speech. Now that the code says these words itself there is nothing in
# between, and Azure reads exactly what it is given: "I / me" comes out as a
# slash or as nothing at all, "My name is ___" as an underscore.
_GLOSS_PLACEHOLDER = re.compile(r"_{2,}|\[[^\]]*\]")
_GLOSS_ELLIPSIS = re.compile(r"\s*\.\.\.\s*")


def speakable(gloss: str) -> str:
    """A gloss as a sentence can pronounce it."""
    text = _GLOSS_PLACEHOLDER.sub("something", gloss)
    text = _GLOSS_ELLIPSIS.sub(" ", text)
    text = " or ".join(part.strip() for part in text.split("/"))
    return " ".join(text.replace("+", " ").split()).strip(" ?.!,")


# Above this many known words, listing them in an instruction costs more than
# it buys and the risk it guards against has faded anyway: once a learner has a
# few dozen words, almost any word the model reaches for IS one of them. Below
# it, the list is short, exact, and load-bearing -- measured at the first
# construction, where the whole vocabulary is "tôi, tên, là" and asking for a
# fourth word is the difference between a variation and a dead end.
MAX_LISTED_KNOWN_WORDS = 12


def _known_words_note(known: list[Item]) -> str:
    """What the learner can actually be asked for, when that list is short.

    Rule 9 keeps a phrase from arriving before its words, but only for whole
    items. Nothing stopped a TURN from asking for a word never taught -- and
    measured: given a free hand to swap the person, the model asked for "your
    name is", i.e. bạn, which the roster teaches one item later.
    """
    names = [i.name for i in known if i.kind != "feature"]
    if not names:
        return ""
    if len(names) > MAX_LISTED_KNOWN_WORDS:
        return " Use only Vietnamese you have already taught them; introduce nothing new here."
    return (f' The only Vietnamese they know so far is: {", ".join(names)}. Build the variation from '
            f'those and nothing else — if none of them allows the change, keep the sentence and vary '
            f'the name instead. Never ask for a word you have not taught: they cannot know it.')


def _known_sentences_note(known: list[Item]) -> str:
    """The sentence patterns this course has taught, in the exact form it taught
    them.

    Never truncated, unlike the word list: there are 5 of them at item 78 and 22
    at the end of the course, so the whole set costs about a thousand characters
    at its largest. The word list is capped because any word the model reaches
    for is probably known; a word ORDER is not like that.

    Written after a live turn where the learner said "Tôi tên là Nam" -- exactly
    the form the roster teaches -- and was told "that's close" and corrected to
    "Tên tôi là Nam". Both are Vietnamese. Only one has been taught, and the
    model had no way to know which: past twelve known words it receives "use
    only Vietnamese you have already taught", which names nothing at all. Being
    corrected when you were right is the worst thing a course can do.
    """
    rows = [f'"{i.name}" ({i.literal})' if i.literal else f'"{i.name}"'
            for i in known if i.kind == "construction"]
    if not rows:
        return ""
    return (" The sentences this course has taught, in the exact form it taught them: "
            + "; ".join(rows) + ". Ask for one of these in THAT form and accept THAT form. "
            "Vietnamese allows other orders; the learner has been given this one, so another "
            "is a correction they cannot use and did not earn.")


def build_plan(item: Item, pieces: list[Item], recall_targets: list[Item],
               known: list[Item] | None = None) -> list[Step]:
    """The full turn-by-turn plan for teaching one item.

    Mirrors the reference method: a lone new word is introduced and heard, a
    construction is assembled by re-citing every piece one question at a time,
    scaffolded with the literal word order, then varied, then named, then
    drilled bare.
    """
    plan: list[Step] = []

    if item.kind == "feature":
        # Said once, at the first rule of the course. Every rule would make it a
        # tic -- the same objection the notebook raises about praising each turn
        # -- and the point lands better as a door opened than as a refrain.
        first_feature = not any(i.kind == "feature" for i in (known or []))
        invite = (" This is the first rule of the course, so add one short line telling them they "
                  "can ask you to say any rule again, any time, and that forgetting one is normal. "
                  "Say it once and never repeat it.") if first_feature else ""
        # The address rule is the one rule the course cannot state properly
        # without knowing who is in front of it: which person-word the learner
        # uses for THEMSELVES depends on their own age and gender. So this is
        # where it asks -- at the only moment the question is obviously part of
        # the lesson rather than a form to fill in. Asked once: the condition
        # is the profile being incomplete, so answering it stops the asking.
        profile = learner_module.load(LEARNER_PATH)
        if item.steps and not profile.complete and any(t in " ".join(item.steps) for t in ADDRESS_TERMS):
            invite += (" You do not know yet whether they are a man or a woman, or roughly how old "
                       "they are, and this rule cannot be made concrete without it. Ask them, in "
                       "one short natural question, as part of explaining the rule — not as a form. "
                       "When they answer, call remember_learner with what they actually said.")
        # Never a recall: the name is a description of the language, not
        # something the learner ever says. Asking "what was tính từ không cần
        # là?" is nonsense, and the old name-splitting made exactly that
        # possible by finding real vocabulary inside the description.
        plan.append(Step(
            "rule", item.name,
            f"Say this, in your own words and in order: {item.gloss or item.description}. Do NOT claim "
            f"they have noticed it or been doing it -- they have not, and being told they "
            f"missed something they were never shown is the one thing a rule turn must not do. "
            f"Use ONLY the examples written above and invent none: a rule about adjectives was given \"a job, a nationality\" as illustrations, neither of which this course can say, and the gap was filled with \"tên tôi\" -- possession, nothing to do with the rule. This is the turn where you TELL rather "
            f"than ask, so two or three sentences are right here — start from what they have "
            f"already been doing, then the surprise, then what to do about it. "
            # No question here, and this is the fix for the defect that survived
            # six rewordings of "ask it in English": the turn kept ending on
            # "How would you say cơm ngon to Minh?", handing over the answer.
            # The turn that ASKS is the next one and the code writes it, so this
            # one has nothing left to leak. End on a short hand-off -- "let's put
            # it to work" -- and stop.
            f"Ask NOTHING: the next turn does the asking. End on a short line that hands over, "
            f"three or four words, and stop. "
            f"The sentence you pick must be one this rule can VISIBLY change: asking for \"my name "
            f"is Nam\" to demonstrate past, present and future is a question the rule cannot touch, "
            f"and the learner is left wondering what the words were for. If none of the sentences "
            f"they know can show it, use the example from the rule itself rather than a sentence "
            f"the change does not reach. "
            f"Each Vietnamese word you say goes at the END of its sentence and there is never more "
            f"than one: a different voice speaks them, so three of them dropped mid-sentence are "
            f"three sounds arriving before any meaning is attached to them. "
            f"ASK IT IN ENGLISH. Naming the Vietnamese sentence you want back is stating the "
            f"answer: say \"how would you say my name is Nam, to Minh?\", never \"how would you "
            f"say em tên là Nam?\".{invite}"
            f"{_known_words_note(known or [])}{_known_sentences_note(known or [])} Nothing else. "
            f"Do not skip the statement: a question alone leaves them with a rule nobody told them.",
        ))
    elif item.kind == "construction":
        for piece in pieces:
            plan.append(Step(
                "recall_piece", piece.name,
                f"Ask them, in English, for the Vietnamese for {_ask_for(piece)}. One question, then "
                f"stop. Do not say the Vietnamese word yourself and do not have Minh say it — it is "
                f"the answer. Do not mention the other pieces.",
                answer_is_target=True,
                ask=speakable(piece.gloss),
            ))
        # A sentence is CLIMBED, not asked for whole. The method's own move,
        # named by Meo while testing: "he always starts calm -- how do you say
        # don't want, then I don't want, then I don't want to eat." It was
        # written down for features and never applied here, so a construction
        # still asked for four words in one go from someone who had just met
        # the three pieces separately.
        #
        # Which rungs are valid is the one thing the code cannot work out:
        # `pieces` gives tôi, tên, là and does not say that "tôi tên" is not a
        # sentence. That knowledge is Vietnamese, so the rungs are model turns
        # and the code supplies the boundary -- the same division `vary` makes
        # just below.
        #
        # The literal order lands on the LAST rung, the whole sentence, because
        # that is where the order matters. It also retires an instruction that
        # asked the impossible: without a literal, the old single step still
        # said "give that literal order out loud" having supplied none.
        rungs = 1 if len(pieces) <= 1 else (2 if len(pieces) <= 3 else 3)
        for n in range(rungs):
            last = n == rungs - 1
            literal = (f' Its literal word order is: "{item.literal}".'
                       if last and item.literal else "")
            if last:
                what = (f'Now the whole thing: ask for "{item.gloss}".{literal}'
                        + (" Give that order out loud in English, word by word, first."
                           if literal else ""))
            else:
                # "One element fewer" alone sent it back to a single word, and
                # live that meant re-asking "tôi" three turns after the recall
                # that had just asked for it. Every piece was recalled on its
                # own immediately before this: a rung that asks for one word
                # repeats a turn instead of climbing. So the floor is TWO
                # pieces put together -- the first thing in the chain that has
                # never been said yet.
                what = (f'They are climbing towards "{item.gloss}", and this is rung {n + 1} of '
                        f'{rungs}. Ask for a SHORTER piece of it — at least TWO of its parts put '
                        f'together, never a single word: they have just recalled each word on its '
                        f'own and asking for one again repeats that turn instead of building. It '
                        f'has to be something a person could actually say, not half a phrase.')
            plan.append(Step(
                "scaffold", item.name,
                f'{what} Stay on THIS sentence: every rung is the same sentence with one more '
                f'element.{_known_words_note(known or [])} Ask in English, one question, then stop. '
                f'Do not say any Vietnamese and do not assemble it for them.',
                answer_is_target=True,
                ask=speakable(item.gloss),
                literal=item.literal if last else "",
            ))
        plan.append(Step(
            "answer", item.name,
            f'Have Minh say the full sentence twice — a real one with the blank filled in, never the '
            f'pattern with its placeholder. Then ask for "{item.gloss}" again'
            + (' for a DIFFERENT PERSON, not a different name — a name in the blank is not a '
               'variation.' if has_person_slot(item) else ' with one element swapped.')
            + " One question.",
        ))
        # The thinnest instruction in the plan, and the only step that ever
        # produced a turn with nothing in it: "Minh: tôi là." then a question
        # about "I am ___", while the item being taught was "my name is ___".
        #
        # Read closely, that failure was not noise. Dropping "tên" from "tôi tên
        # là" to get "tôi là" IS a structural variation -- the model was doing
        # the right KIND of thing and simply left the sentence it was teaching.
        # It was never told what may move and what may not, because the old
        # instruction named neither the sentence, nor the element, nor Minh.
        #
        # Which element is swappable is the one thing the code cannot work out:
        # to know tôi/bạn/anh occupy the same slot it would need a category far
        # finer than the roster's -- `function_word` also holds "gì" and "chào",
        # so permuting inside it yields "chào tên là". That knowledge is
        # Vietnamese, which is exactly what the model has and a table does not.
        # So this stays a model turn, and the instruction supplies the boundary
        # rather than the words: what varies, what is frozen, who stays silent.
        # The shape comes from the item, so the "do not drop a word" rule is
        # stated against THIS sentence rather than as a general plea. A fixed
        # example of a wrong variation would be about some other sentence half
        # the time, which is worse than no example.
        # TWO instructions, chosen by the sentence -- not one with conditionals
        # bolted on. The single version grew to 192 words with its most
        # important clause at word 59, and offered "otherwise a different word
        # in the blank" as an escape. Live, the model took the escape twice:
        # "My name is Lan", then "My name is Mai". It permuted given names,
        # which are not vocabulary and teach nothing, while the pronoun -- the
        # only interesting thing in that sentence -- never moved.
        # The learner's OWN table wins over the rule's generic one. Same shape,
        # so nothing below changes -- but "someone younger → they are em, you
        # are anh" is a different kind of sentence from "the term depends on
        # relative age and gender", which is a table to memorise.
        # Minh goes first and always: he is the one person in the room, so the
        # rule stops being a table for at least one row, profile or no profile.
        profile = learner_module.load(LEARNER_PATH)
        rows = "; ".join([learner_module.pair_with_minh()]
                         + (profile.address_rows() or address_situations(known or [])))
        if has_person_slot(item) and rows:
            vary_instruction = (
                f'Vary WHO they are speaking to. Name the situation out loud — "now you are '
                f'talking to someone younger" — and ask for "{item.gloss}" again for that person. '
                f'The person word is the ONLY thing that changes: everything else in the sentence '
                f'stays, and a name in the blank is NOT a variation. The course teaches these and '
                f'only these: {rows}. One question, in English, then stop. Say no Vietnamese and do '
                f'not have Minh speak — the sentence is what you are asking them for.'
            )
        else:
            shape = (f' It keeps the shape "{item.literal}" exactly — the same parts, in that '
                     f'order, none removed.') if item.literal else " Keep every part of it."
            vary_instruction = (
                f'They have just built "{item.gloss}". Ask for it once more with exactly ONE '
                f'element changed.{shape}{_known_words_note(known or [])}'
                f'{_known_sentences_note(known or [])} Drop a part and it '
                f'silently becomes a different sentence, which is the one thing this turn must not '
                f'do. One question, in English, then stop. Say no Vietnamese and do not have Minh '
                f'speak — the Vietnamese sentence is the answer you are asking them for.'
            )
        # The rungs come OUT of this budget, they are not added to it. Climbing
        # adds turns, which is the wrong direction for a course that wants more
        # sentences -- and in the reference method climbing IS the variation:
        # "I want" then "I want to eat" then "I don't want to eat" is one
        # gesture, not build-then-vary. So the count of turns where the learner
        # produces the sentence stays what it was; only their shape changes.
        for _ in range(max(1, N_VARIATIONS - rungs)):
            plan.append(Step("vary", item.name, vary_instruction, answer_is_target=True))
        plan.append(Step(
            "rule", item.name,
            "Name the pattern now, in one plain sentence, as something they just noticed. Then one "
            "last question.",
        ))
    else:
        # Two turns, not one. A single turn meant a word was revealed, heard
        # once and gone -- three of them stacked back to back before anything
        # was combined, which is what made the lesson feel like it was skimming.
        # The reference course does the same thing: it gives the word, then
        # comes straight back with "again, the word for X is ...".
        plan.append(Step(
            "introduce", item.name,
            f'Introduce {item.name}. Say in ONE sentence that the Vietnamese for {_ask_for(item)} is '
            f'{item.name} — the meaning and the word together, ending on the word, so the pair lands '
            f'as one thing. (One sentence of real context first only if you have a true fact worth '
            f'telling.) Then give Minh a single line containing the word ONCE: "{item.name}." '
            f'By then they have heard it twice, at the end of your sentence and from Minh, which is '
            f'enough. Then ask them to say it. Nothing else.',
            ask=speakable(item.gloss),
            hook=item.hook,
            twin=(twin := tone_twin(item, known or [])) and twin.name or "",
            twin_gloss=twin and speakable(twin.gloss) or "",
        ))
        plan.append(Step(
            "settle", item.name,
            f"Stay on this word one more turn. React in a few words to what they just said, then ask "
            f"for it a second time — SHORT, and marked as a repeat: \"and again, what was "
            f"{_ask_for(item)}?\" Never restate the full question, which sounds like a new one and "
            f"makes them wonder what they missed. Asking twice is deliberate and is not a sign they "
            f"got it wrong. Do not say the Vietnamese yourself, do not have Minh say it, and do not "
            f"introduce anything new.",
            answer_is_target=True,
            ask=speakable(item.gloss),
        ))

    if item.kind == "feature":
        # A rule used to get ONE turn about itself, which had to state it, give
        # examples and apply it all in a breath -- and then the plan went
        # straight to recalls of unrelated words. Measured on the real
        # sequencing: rule -> rapidfire anh -> rapidfire em -> rapidfire tên.
        # Stated once and never used again, which is exactly what a learner
        # reported: "I understood nothing about the rule and it is not even
        # used."
        #
        # Every other kind gets several turns on the thing being taught -- an
        # atom has introduce plus settle, a construction has a recall per piece
        # plus scaffold plus answer plus variations. The rule was alone in
        # having one.
        # The CODE picks which sentence each application uses, and they differ.
        # Asking for a different one was an instruction, and live it was ignored
        # three turns running: the rule turn asked "how would you answer Bạn
        # muốn ăn?", then both applications asked exactly that again. The
        # learner heard one question four times and the session ran out before
        # anything else happened. Whether two sentences are different is not a
        # judgement call, so it is not the model's to make.
        #
        # Ones sharing a piece with the rule come first, since a rule shows best
        # on material it actually touches. Measured: the median rule has 5 taught
        # sentences to choose from and only 2 of 35 have fewer than two.
        # Pinned ONLY when a taught sentence genuinely shares material with the
        # rule. Without that test the sort fell back to whatever came first, and
        # the negation rule was handed "My name is ___" -- a sentence with no
        # verb in it to negate, which is the one thing the rule cannot do.
        # Whether a sentence can carry a rule is Vietnamese knowledge; when the
        # code has no evidence it hands the list over instead of guessing, the
        # same division this file already makes on the vary step.
        # A rule ABOUT person-words is asked as a situation, never as a phrase.
        # Meo, validating ơi: instead of giving the answer in the application,
        # pose it as a puzzle -- "I want you to call this kind of person". Then
        # nothing Vietnamese is said and the learner has to build it.
        #
        # This is the vary step's move, reused: name the situation in English,
        # ask for it. Both rules Meo flagged declare anh and chị in their
        # pieces, so has_person_slot is already true for them and no new field
        # is needed. It fixes ơi and ấy with one change -- they had the same
        # defect, "How would you say anh ấy?", the question saying its answer.
        # has_person_slot is too loose here: it asks whether a person-word is
        # PRESENT, and word order (tôi, uống, cà phê) and possession (của, cà
        # phê, tôi) both use one as example material without being about it.
        # Those would have been asked as "call this kind of person", which is
        # nonsense. A rule is ABOUT address when most of its material is.
        # Two of them at least, and most of the material: one alone is an
        # example word, which is what "tôi, là" is doing in the tone rule.
        address_pieces = sum(1 for p in item.pieces if p in ADDRESS_TERMS)
        about_address = address_pieces >= 2 and address_pieces * 2 >= len(item.pieces)
        profile = learner_module.load(LEARNER_PATH)
        rows = profile.address_rows() or address_situations(known or [])
        if about_address and rows:
            situations = "; ".join([learner_module.pair_with_minh()] + rows)
            for rung in ("someone this rule is easiest on", "a different person entirely",
                         "a third, and let them choose which person-word fits"):
                plan.append(Step(
                    "apply", item.name,
                    f"Put the rule to work by naming a SITUATION: {rung}. Say who the person is in "
                    f"English — \"someone older than you, a man\" — and then ask for what THIS "
                    f"rule does with them, which is: {item.gloss}. Not something else you could "
                    f"do with a person. NEVER say the Vietnamese: naming it "
                    f"is handing over the whole answer, which is the one thing this turn must not "
                    f"do. The situations this course teaches, and only these: {situations}. One "
                    f"question, then stop.",
                ))
            return plan

        # Sorted by HOW MUCH they share, not by who comes first. The yes/no
        # question rule (có, không) was pinned to "không phải là + [danh từ]",
        # which shares only "không" and is about negation -- so all three rungs
        # asked for "not a student" while the rule being taught was how to ask a
        # question. The construction that shares both pieces was sitting right
        # there, later in the course order.
        on_it, apply_ask = _apply_material(item, known or [])
        # The pieces FIRST, one at a time, then the assembly -- which is what a
        # construction already does (a recall per piece, then the scaffold, then
        # the whole thing) and what Meo asked for twice: "we said we ask for the
        # individual words có and không, then we make a sentence, it's simpler."
        #
        # It also answers the other half of the complaint. Three rungs on one
        # sentence meant hearing "tôi tên là Nam" three times running; now only
        # the last turn uses a sentence at all.
        #
        # And these recalls are SCRIPTED, so two of a rule's three practice
        # turns stop going through the model -- in the direction everything
        # measured today points.
        by_name = {i.name: i for i in (known or [])}
        for piece in [by_name[p] for p in item.pieces if p in by_name][:MAX_FEATURE_PIECE_RECALLS]:
            plan.append(Step(
                "recall_piece", piece.name,
                f"Ask them, in English, for the Vietnamese for {_ask_for(piece)}. One question, "
                f"then stop. Do not say the Vietnamese word yourself and do not have Minh say it.",
                answer_is_target=True,
                ask=speakable(piece.gloss),
            ))
        plan.append(Step(
            "apply", item.name,
            f"Now put those words together.{on_it} Ask for ONE sentence that uses the rule, on "
            f"material they have just recalled. The change this rule makes has to be visible in "
            f"the answer, or the turn teaches nothing."
            # The ở rule asked for "I am at home", then "at school", then "at
            # the market" -- none of nhà, trường or chợ has been taught, so
            # every rung was unanswerable. An application may only use words
            # the learner has.
            f"{_known_words_note(known or [])} ASK IT IN ENGLISH and do not say the Vietnamese "
            f"back: that is the answer. One question, then stop.",
            ask=apply_ask,
        ))

    for target in recall_targets:
        # A drawn feature comes back as an APPLICATION, never as a bare recall:
        # nobody recites "no plural", which is exactly why features were left
        # out of the draw entirely and never returned once (see drawable).
        # Deliberately thinner than the application that follows an
        # introduction: that one arrives after the feature's own pieces have
        # just been re-asked one by one, so it can say "now put THOSE words
        # together". Here nothing was recalled first -- this is a revision slot
        # in someone else's item -- so it has to name its own material.
        if target.kind == "feature":
            on_it, apply_ask = _apply_material(target, known or [])
            plan.append(Step(
                "apply", target.name,
                f"Bring back something they were taught earlier: {speakable(target.gloss)}.{on_it} "
                f"Ask for ONE sentence that puts it to work. The change it makes has to be visible "
                f"in the answer, or the turn teaches nothing."
                f"{_known_words_note(known or [])} ASK IT IN ENGLISH and do not say the Vietnamese "
                f"back: that is the answer. One question, then stop.",
                ask=apply_ask,
            ))
            continue
        plan.append(Step(
            "rapidfire", target.name,
            f"Bare recall, no context: ask them in English for the Vietnamese for {_ask_for(target)}. "
            f"One question, then stop. Do not say the Vietnamese word and do not have Minh say it "
            f"first — that would hand over the answer before the question.",
            answer_is_target=True,
            ask=speakable(target.gloss),
        ))
    return plan


# Steps that ask the learner to produce a word we can check against.
RECALL_KINDS = ("recall_piece", "rapidfire", "settle")

# ...and those are exactly the turns the code now writes itself, word for word,
# with no model call. A recall is one sentence whose two halves the code already
# holds -- the meaning to ask from and the word not to utter -- so handing it to
# a model bought nothing and cost the one thing that kept going wrong: measured
# live, the model ran a turn behind, re-asking the previous word when told to
# introduce the next, then introducing that word on the step where saying it is
# forbidden. A sentence composed here cannot skip its step, cannot give away its
# answer, and cannot fall behind. It also halves the requests per lesson, which
# the 8000 tokens/minute ceiling makes worth having on its own.
#
# What stays with the model: introductions, the scaffold, the variations, the
# rule -- the turns that need something invented -- and ANY turn where the
# learner said something to us rather than answering (see learner_spoke_freely).
# That escape hatch is why the instruction text on these steps is still live and
# must be kept in step with the wording below.
# `introduce` joins them, and NOT because it was mechanical enough to be worth
# the tokens -- because it broke. Seen live: told to introduce "tên", the model
# said "I didn't catch that", had Minh say the word, and asked for it. The
# sentence giving the word its MEANING was never spoken. A first exposure to a
# word without its meaning is not a lesson, and no amount of instruction makes
# that guaranteed.
#
# What was supposedly being bought with that turn: one optional sentence of
# real context, "only if you have a true fact worth telling". Across every
# session logged, it fired zero times. We were paying the guarantee for an
# ornament that was never delivered.
#
# NOT the same list as RECALL_KINDS on purpose: an introduction asks the
# learner to echo a brand-new word, which is not a recall -- nothing is scored,
# no level moves, and the recogniser is not told to expect it.
# `scaffold` joins them for the same reason `introduce` did: it broke, and the
# code holds both halves. Its whole job is to say the literal English order and
# ask for the Vietnamese -- and live it said the Vietnamese: "can you say the
# full sentence tôi tên là ...", which is the answer, on the one step that
# forbids it. Its instruction had said "do not say any Vietnamese" all along.
SCRIPTED_KINDS = RECALL_KINDS + ("introduce", "scaffold", "apply")

# Steps that move an item's level when they complete. RECALL_KINDS score what
# the code asked and can check; an application only counts the exposure, since
# it asks for a whole sentence and has nothing to compare (17b).
#
# Named here because it was written out by hand in four places -- twice in
# simulate_progress.py, once in smoke_test.py, once in the live loop -- under
# comments claiming they matched. They did, until applications began to count.
# simulate_progress.py is what measured "33 features out of 33 never seen
# again": a stale copy there does not merely fail to show the fix, it reports
# that the fix did not work.
SCORING_KINDS = RECALL_KINDS + ("apply",)


# A repeat has to SOUND like a repeat: three goes at "What's the Vietnamese word
# for I or me?" in a row read as three different questions and send the learner
# hunting for what they missed. This is the reference course's own signature --
# "and again, what was ___?" appears twenty-one times in it.
_REPEAT_ASK = (
    "And again — what was {ask}?",
    "Once more — what was {ask}?",
    "And {ask} — what was that?",
    "So, {ask}?",
)
# A one-word gloss needs a frame saying it is a WORD being quoted. Measured in
# a simulated lesson: "So, this?", "So, have?" and "what was and?" all landed in
# fourteen turns, and none of them reads as a question. A content word survives
# the terse form ("So, coffee?") because it names a thing; a function word does
# not. Still shorter than the full question, which is what rule 18b is really
# guarding against -- three identical long questions in a row.
_REPEAT_ASK_SHORT = (
    "And again — what was the word for {ask}?",
    "Once more — the word for {ask}?",
    "So, the word for {ask}?",
)
# The inverted form, "And {ask} — what was the word?", is gone. It was the
# weakest of the four and it broke outright on a gloss that is itself a question
# word: "And what — what was the word?" reads as two questions and neither can
# be answered.
_ACK_CORRECT = ("That's it.", "Yes, that's it.", "Good.", "Exactly.", "That's the one.")
_RETRY_ASK = ("And again?", "So once more?", "Again?")

# The meaning and the word in one breath, ending ON the word so the pair lands
# as one thing -- which also hands it to Minh's voice, since a Vietnamese word
# at the end of an English sentence is where the voice switch belongs (SPEC 3).
# The word then repeats immediately: written as two sentences, but both are
# Vietnamese, so they merge into a single run and Minh says it twice in one
# clip. The learner hears it twice before being asked for anything.
# The literal order, then the ask. Nothing Vietnamese can appear: both halves
# are English, so this turn cannot state its own answer by construction.
_SCAFFOLD = (
    "Word for word, that is: {literal}. So how would you say {ask}?",
    "In Vietnamese the order is: {literal}. Now — {ask}?",
    "Literally, it goes: {literal}. Give me the whole thing — {ask}?",
)
# The question that puts a rule to work, written HERE rather than asked for.
# The instruction said "ASK IT IN ENGLISH and do not say the Vietnamese back:
# that is the answer" in six different wordings across one evening, and the
# model kept ending on "How would you say cơm ngon to Minh?" -- handing over the
# whole answer. It is not a judgement call, so it stopped being the model's:
# these are built from the ENGLISH gloss, so no Vietnamese can appear.
_APPLY_ASK = (
    "Now put it to work — how would you say {ask}?",
    "So, using that: how would you say {ask}?",
    "Let's use it. How would you say {ask}?",
)
_INTRODUCE = (
    "In Vietnamese, the word for {ask} is {name}. {name}. Now you say it.",
    "The Vietnamese for {ask} is {name}. {name}. Your turn — say it.",
    "Here's the word for {ask}: {name}. {name}. Now you try it.",
)
# The same shape, plus the one word already known that differs from it only in
# pitch. Every Vietnamese run still ENDS its sentence, so Minh is handed whole
# clips and the voice never switches mid-sentence -- checked by the same guard
# that caught the rule turn dropping three words into the middle of one.
_INTRODUCE_TWIN = (
    "In Vietnamese, the word for {ask} is {name}. {name}. Careful — you already know "
    "{twin_gloss}, and it is the same sounds at a different pitch. Here they are together: "
    "{twin}. {name}. Now you say it.",
    "The Vietnamese for {ask} is {name}. {name}. This one is a pair with {twin_gloss}, which "
    "you know — same sounds, different pitch. Listen: {twin}. {name}. Your turn.",
)


def _pick(lesson: dict, slot: str, options: tuple[str, ...]) -> str:
    """One of the wordings, never the one used last time in this slot.

    Plain random choice repeats itself about a fifth of the time, and two
    identical sentences back to back is precisely the tic the varied wording
    exists to avoid.
    """
    last = lesson.setdefault("phrasing", {}).get(slot)
    chosen = random.choice([o for o in options if o != last] or list(options))
    lesson["phrasing"][slot] = chosen
    return chosen


def _acknowledgement(lesson: dict, step: Step) -> str:
    """How the scripted turn opens: what the code already decided about the
    answer it just heard, said in a few words.

    The code alone knows this verdict (answered_target computed it), so a
    scripted turn is the one place it can be voiced without the model second-
    guessing the transcription -- the contradiction seen live, where a word's
    level went up while the tutor said "I didn't catch that".
    """
    verdict = lesson.get("verdict")
    if verdict == "correct":
        return _pick(lesson, "ack", _ACK_CORRECT)
    missed = lesson.get("verdict_target")
    if verdict == "missed_twice" and missed:
        # The SPOKEN form, same as the retry line. Fixed there first and missed
        # here, so "It was muốn + [động từ]." went out and Minh -- who takes any
        # accented word -- recited "muốn động từ", which is not a phrase.
        said = f"It was {' '.join(_target_fragments(missed)) or missed}."
        # And never when the answer to THIS turn is hiding inside it. Comparing
        # the two names for equality was not enough: the missed item was
        # "bạn tên là gì?" and the question coming was for "bạn", so the
        # acknowledgement handed the answer over a sentence before it was asked.
        # The leak guard already knows how to see that, so it is asked rather
        # than a second rule written beside it.
        if not _leaked_target(said, step):
            return said
    return ""


def scripted_turn(lesson: dict) -> str | None:
    """The exact words for this turn, or None if the model has to speak it.

    Everything here is built from the item's own gloss, never from its
    Vietnamese name, so a scripted question cannot state its own answer.
    """
    step = current_step(lesson)
    if step is None or step.kind not in SCRIPTED_KINDS or not step.ask or not step.target:
        return None
    if lesson.get("retried"):
        # A second go at the same question. Minh says the word, then it is
        # asked again short -- the shape the prompt used to ask for, with the
        # known flaw it always had: the answer is spoken just before the
        # question (see SPEC 20). Now it is one line here rather than a
        # paragraph the model interprets, so fixing it is a one-line change.
        # The SPOKEN form of the target, not its authoring name: a construction
        # is stored as "tôi tên là + [tên riêng]", and Minh cannot say "plus
        # bracket tên riêng". The same fragments the leak guard compares.
        spoken = " ".join(_target_fragments(step.target)) or step.target
        return f"Listen again — {spoken}. " + _pick(lesson, "retry", _RETRY_ASK)
    if step.kind == "scaffold":
        if not step.literal:
            return None          # nothing to scaffold with; the model still has a go
        body = _pick(lesson, "scaffold", _SCAFFOLD).format(
            literal=speakable(step.literal), ask=step.ask)
    elif step.kind == "apply":
        if not step.ask:
            return None          # nothing to ask from; the model still has a go
        body = _pick(lesson, "apply", _APPLY_ASK).format(ask=step.ask)
    elif step.kind == "introduce":
        # The one scripted turn that SAYS the target rather than asking for it.
        # A whole different line when the word has a tone twin, rather than the
        # ordinary one with the contrast bolted on the end -- bolting it on left
        # "Now you say it" in the MIDDLE, so the learner was told to speak and
        # then talked over. Here the contrast lands after the meaning and before
        # the ask, with Minh saying the two words back to back: the only second
        # in which the difference exists for a foreign ear, and the only thing
        # this course can honestly do about tones, since it never hears the
        # learner and so can model and contrast but never judge.
        forms = _INTRODUCE_TWIN if step.twin else _INTRODUCE
        body = _pick(lesson, "intro", forms).format(
            ask=step.ask, name=step.target, twin=step.twin, twin_gloss=step.twin_gloss)
        # A hook goes in FRONT: the fact earns the word, then the word lands.
        # For "phở" or "cà phê" the template alone is circular -- it tells a
        # learner who already knows the thing that the Vietnamese for it is the
        # word they are about to hear.
        if step.hook:
            body = f"{step.hook} {body}"
    else:
        forms = _REPEAT_ASK_SHORT if len(step.ask.split()) == 1 else _REPEAT_ASK
        body = _pick(lesson, "ask", forms).format(ask=step.ask)
    lead = _acknowledgement(lesson, step)
    return f"{lead} {body}".strip()


# A construction's name carries its hole: "tôi tên là + [tên riêng]". Nobody
# ever SAYS "plus bracket tên riêng", so a plain substring test against that
# name can never match anything spoken -- which is why the guard below reported
# nothing across every session: on a construction it could not fire at all. The
# full answer said aloud on a step that forbids it, "Tôi tên là Nam.", went
# through untouched. A protection that looks like one and is not -- exactly the
# shape this project has been bitten by before.
# So a target is reduced to the fragments actually pronounced, and all of them
# have to be present for it to count as given away.
_PLACEHOLDER = re.compile(r"\+?\s*\[[^\]]*\]|_{2,}|\.\.\.")


def _target_fragments(target: str) -> list[str]:
    """The parts of a target that are really said, holes removed."""
    return [f for f in (p.strip(" +,.") for p in _PLACEHOLDER.split(target)) if f]


# Turns that ASK for something the learner must produce. _leaked_target only
# covers the ones with a known target word; a rule or an application asks for a
# whole sentence nobody can name in advance, so it needs a different test.
# "rule" is no longer here: it TELLS and asks nothing, so the question that
# used to leak out of it is gone. "apply" stays as a backstop for the case
# where the code has no gloss to build a question from.
_ASKING_KINDS = ("apply", "vary", "scaffold")

# A Vietnamese run this long inside an asking turn IS the answer. One word is
# naming the material -- "say he using anh and ấy" is a fair question. Two words
# running is the phrase itself: "how would you say anh ấy?" answers itself.
# Measured on six real lines, it separates them exactly.
MAX_VN_WORDS_WHEN_ASKING = 1


def _warn_if_answer_spoken(text: str, step: Step | None, roster: list[Item]) -> None:
    """Reports an asking turn that said the Vietnamese it was asking for.

    Detection, like every guard here: the reply is spoken as it streams, so by
    the time a whole turn can be judged the learner has heard it. What it buys
    is knowing -- a question containing its own answer reads as a perfectly
    good turn in a transcript, which is how it survived every session logged.

    Rendered across the tier-1 rules, it is the dominant defect: "How would you
    say anh ấy?", "how would you say bạn ơi, tên là gì?", "using the pattern
    không muốn + [động từ]". Three different rules, the same move.
    """
    if step is None or step.kind not in _ASKING_KINDS:
        return
    runs = [chunk for key, chunk in voice_module.split_by_voice(text, _vocab_words(roster))
            if key == "teacher"]
    longest = max((len(r.split()) for r in runs), default=0)
    if longest > MAX_VN_WORDS_WHEN_ASKING:
        worst = max(runs, key=lambda r: len(r.split()))
        print(f"  [diag] !! asking turn said a {longest}-word Vietnamese phrase — "
              f"that is the answer: {worst.strip()!r}")


def _leaked_target(text: str, step: Step | None) -> bool:
    """True if a turn that was asking FOR something went and said it.

    Detection only -- the reply is streamed and spoken sentence by sentence as
    it arrives, so by the time a whole turn can be judged it has already been
    heard. What this buys is knowing it happened: a recall that states its own
    answer looks exactly like a successful turn in the transcript, and went
    unnoticed across two whole live sessions.
    """
    if step is None or not step.answer_is_target or not step.target:
        return False
    said = text.casefold()
    fragments = _target_fragments(step.target)
    return bool(fragments) and all(f.casefold() in said for f in fragments)


def _lesson_note(lesson: dict) -> str:
    """What the model is told this turn: its one instruction, and nothing else.

    Deliberately does NOT restate the cycle, the sequence, or what comes next.
    Everything the model does not need in order to speak this turn is weight it
    pays for on every request.
    """
    lines = [
        "LESSON STATE — for you only. This is a directive, never a script: do not read any of it "
        "aloud and do not repeat its wording. Say it your own way, in English."
    ]
    step = current_step(lesson)

    if lesson.pop("react_only", False):
        # The turn before was written by the model, so only the model knows what
        # it asked. Without this the learner attempted a sentence and the lesson
        # answered with an unrelated recall -- measured: they said "An ten la
        # nam" after being asked to apply the address rule, and heard nothing
        # back. The code cannot judge these steps; it can at least hand them
        # back to whoever set them.
        lines.append(
            "THEY JUST ANSWERED THE QUESTION YOU ASKED. React to what they actually produced — say "
            "whether it landed, give the correct form once if it did not, and STOP. Ask nothing, "
            "teach nothing new, move nothing on. The lesson continues by itself next turn."
        )
        return "\n".join(lines)

    if lesson.pop("gave_up", False):
        step = current_step(lesson)
        lines.append(
            "THEY SAID THEY DO NOT KNOW. Give them the answer to what you just asked, plainly and "
            "without making it a lesson — say it, have Minh say the Vietnamese once, and tell them "
            "it comes back later. Do not ask them to produce it again this turn, and do not act "
            "disappointed. Then do the instruction below."
        )

    announce = lesson.pop("announce_topic", None)
    if announce:
        # Said once, on the turn right after the items land. Without it the
        # learner asks for a subject, hears "Alright, let's continue", and the
        # new words simply start appearing -- so the thing they asked for looks
        # like it was ignored. Consumed on read: an announcement repeated is
        # worse than none.
        topic, covers = announce
        # The glosses, not just a count. Given only "4 new things" the model
        # invented the list -- live, it promised a menu, a dish name, the bill
        # and a way to thank the server, when what had actually been generated
        # was "pho", "to order" and two sentence patterns. It had no way to
        # know; the code did.
        listing = "; ".join(g for g in covers if g) or "a few new things"
        lines.append(
            f"THEY ASKED FOR THIS SUBJECT AND YOU HAVE IT: tell them, in one or two warm sentences, "
            f"that you have put together a short personal thread on {topic} that runs alongside the "
            f"course, and that it starts right now. What it actually covers, in English: {listing}. "
            f"Say only that — never a fuller or better-sounding list, and no Vietnamese words. Then go "
            f"straight into the instruction below, in the same turn."
        )

    if lesson.get("answer_only"):
        # They spoke to us, so this turn is theirs and the teaching step is not
        # shown at all. It is replayed next turn regardless, so nothing is lost
        # by waiting -- and everything is lost by not waiting: measured live,
        # the learner opened with "Hello, how are you?", the tutor replied "how
        # about you?" AND asked the lesson question in the same breath, then
        # scored the answer to its own social question as a failed attempt at
        # the Vietnamese word.
        #
        # The persona used to ask for this in prose ("deal with their question
        # first, then do your instruction anyway"), which contradicted its own
        # rule 2 ("your turn ends at your question, never ask two"). A rule the
        # code can enforce does not belong in a prompt that argues with itself.
        lines.append(
            "THEY SPOKE TO YOU, they did not answer a question. Reply to what they actually said "
            "and STOP. If it was a real question about Vietnamese, ANSWER IT PROPERLY — that is "
            "the one thing they asked you for, and a deflection is worse than a long answer. If it "
            "was small talk, a sentence is plenty. Either way: do not move the lesson on, do not "
            "ask them to say anything, and never tell them you did not understand — you did. The "
            "lesson picks up by itself on your next turn."
        )
        return "\n".join(lines)

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
        # The GLOSS, never the description. `description` is a paragraph of
        # Vietnamese written for whoever authors the content, and it was being
        # handed to a model asked to speak English -- which then leaked
        # fragments of it aloud. Rendered on the tier-1 rules: "That works for
        # both actions and describing words, like a verb động từ", "you add the
        # word ấy after the person word. ấy", "adding a word after the
        # person-word. đã". Three different rules, the same cause.
        #
        # Nothing is lost: every instruction already carries the English side it
        # needs, and the item's name is what the turn is about.
        item = lesson["item"]
        lines.append(f"Item being worked: {item.name}"
                     + (f" — {item.gloss}" if item.gloss else ""))
    lines.append(f"THIS TURN, THIS ONLY: {step.instruction}")
    verdict = lesson.get("verdict")
    if verdict == "correct":
        lines.append(
            "Their last answer WAS the word, near enough. Take it, say so in a few words, and get "
            "on with the instruction above. Never tell them you did not catch it -- you did."
        )
    elif verdict == "missed_twice":
        lines.append(
            "They have now missed that word twice, which is enough. Give the correct form once, "
            "have them say it back, and carry on. Do not dwell on it and do not ask again -- it "
            "comes back later on its own."
        )
    if lesson.get("retried"):
        lines.append(
            f"They answered with a different word, so this is a second go at the SAME question. "
            f"Have Minh say {step.target} once, then ask again SHORT — \"and again?\", \"so once "
            f"more?\" Do not restate the whole question and do not rephrase it into a new-sounding "
            f"one: both make them think you are asking something else. Do not tell them they were "
            f"wrong. Whatever they answer this time, you move on afterwards."
        )
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
    count = rapidfire_count(item, pieces)
    # seen_items minus the item itself: what the learner can be asked for now.
    known = [i for i in seen_items if i.name != item.name]
    lesson["plan"] = build_plan(
        item, pieces, _recall_targets(store, item, pieces, seen_items, count), known)
    kinds = " -> ".join(s.kind for s in lesson["plan"])
    print(f"  -> item: {item.name}  [{len(lesson['plan'])} turns: {kinds}]")


# Above this similarity the answer counts as the target word. Placed in the
# middle of a gap that turned out to be wide: across real transcriptions every
# recognisable attempt scored 0.67 or better ("toy" for tôi, "Then" for tên,
# "laa" for là) and every genuinely different word scored 0.33 or less. Set
# generously on purpose -- what arrives is a beginner's mouth through a rough
# microphone, so approximate is the normal case, and treating a near miss as a
# miss would fail someone for a lost accent.
ANSWER_MATCH_THRESHOLD = 0.5


# Every learner turn arrives prefixed with the language the recogniser reported.
# It has to come off before any comparison: _bare keeps letters and drops
# everything else, so "[lang:vi]" survived as "langvi" glued to the front of the
# answer. Six junk letters were enough to sink every correct reply -- "Đói" for
# tôi scored 0.33 instead of 0.67, and an exact "tôi" landed on 0.50, right at
# the threshold. A whole live session could not produce a single accepted answer.
_LANG_TAG = re.compile(r"^\s*\[lang:[a-z-]+\]\s*", re.IGNORECASE)


def _bare(text: str) -> str:
    """Letters only, no tone marks -- what a beginner and a recogniser both lose
    first -- but word boundaries KEPT.

    They used to be dropped with everything else, which turned every short
    target into a substring of any long utterance. Live on 13 August: the
    recogniser hallucinated "…những video hấp dẫn" out of room noise, and "ăn"
    was found inside "dẫn", so the word was recorded as answered. A tone mark is
    dropped, a space becomes a space.
    """
    lowered = unicodedata.normalize("NFD", text.lower()).replace("đ", "d")
    kept = []
    for c in lowered:
        if c.isalpha():
            kept.append(c)
        elif not unicodedata.combining(c):
            kept.append(" ")   # a real separator, not a tone mark
    return " ".join("".join(kept).split())


# How many turns in a row the learner may hold one step by talking to the tutor
# instead of answering it. Without a cap, a step is never consumed while they
# keep speaking English, and the lesson stops moving; with one, a real
# back-and-forth still fits and a monologue does not stall the course.
MAX_STEP_WAITS = 2


def _should_retry(step, user_text: str, lesson: dict) -> bool:
    """One second chance on a missed recall, never two.

    Capped deliberately: the version before the state machine had no counter at
    all and asked the same word four times running.
    """
    if step is None or lesson.get("retried") or step.kind not in RECALL_KINDS or not step.target:
        return False
    return not answered_target(user_text, step.target)


# Below this many letters, a target needs a closer match. difflib is coarse on
# short strings: against a two-letter word, sharing ONE letter scores exactly
# 0.50 and clears the threshold. Live, "Dạ" was accepted as "là" and pushed it
# to level 7 -- the learner had said something else entirely and the word was
# recorded as consolidated.
SHORT_TARGET_LETTERS = 3
# Placed in the gap, not at its edge. Measured on the two cases that matter:
# "Dạ" against "là" scores 0.50 and must fail; "Đôi" against "tôi" scores 0.667
# and must pass -- it is a real recognition, two of three letters. 0.67 rejected
# it by a hair.
SHORT_TARGET_THRESHOLD = 0.60


def answered_target(user_text: str, target: str) -> bool:
    """Whether the learner's turn contains the word that was asked for.

    Only ever used to decide whether the tutor gets a second go at a step. It
    never rewrites what was said: an earlier version snapped the transcription
    onto the nearest known word, which repaired the mispronunciation the tutor
    is supposed to hear.
    """
    # The slot is a hole to fill, not something to say: `muốn + [động từ]` is
    # answered "tôi muốn ăn", never "động từ". Left in, the words NAMING the
    # slot became part of the target -- saying "động từ", "danh từ" or "tên
    # riêng" out loud scored as the answer on five of the eleven constructions
    # that have one. Same target as resembles_target sees, which is the point:
    # the two disagreed until now.
    said, want = _bare(_LANG_TAG.sub("", user_text)), _bare(_SLOT.sub("", target))
    if not want:
        return True
    # Padded, so the match is on whole words. Unpadded, "ăn" was found inside
    # "dẫn" and a hallucinated sentence counted as the answer.
    if f" {want} " in f" {said} ":
        return True
    # A single letter is not a word, whatever it scores. "D" against "đi" rates
    # 0.67 -- the same as a genuine "Đôi" for "tôi" -- because one of two letters
    # matched. Live, that recorded a word as said when the recogniser had heard
    # a fragment.
    if len(said) < 2 <= len(want):
        return False
    floor = SHORT_TARGET_THRESHOLD if len(want) <= SHORT_TARGET_LETTERS else ANSWER_MATCH_THRESHOLD
    return difflib.SequenceMatcher(None, said, want).ratio() >= floor


# Looser than ANSWER_MATCH_THRESHOLD on purpose. This one answers a different
# question: not "is this the answer" but "is this an ATTEMPT at the answer, badly
# spelled" -- which is what tells a mangled word apart from the learner speaking.
#
# Set by the expensive direction. Measured 17 August: the attempts recorded in
# smoke_test.py score 0.571 ('Fen Bey.' for sân bay), 0.857 ('and Bay') and 1.000
# ('toi'), while English of two words or more tops out at 0.308 ("I forgot"
# against không). 0.45 sits in that gap with margin on the side that matters.
_SLOT = re.compile(r"\+?\s*\[[^\]]*\]")


def _has_slot(target: str) -> bool:
    """A construction the learner fills in, so their answer is longer than the
    pattern: `tôi tên là + [tên riêng]` is answered "Tôi tên là Anna"."""
    return bool(_SLOT.search(target))


RESEMBLES_TARGET_THRESHOLD = 0.45


def resembles_target(user_text: str, target: str) -> bool:
    """Whether what was heard is a mangled shot at the word the lesson asked for.

    Used only to protect the learner's right to interrupt: a step waiting for
    `không` and a learner saying "I didn't understand" must not have that
    translated into "Tôi không hiểu." and scored correct. What separates the two
    is that an attempt looks like the word and a sentence does not.

    Never used to score an answer -- `answered_target` does that, at its own
    stricter floor. Confusing the two would let 0.45 record a word as known.
    """
    said, want = _bare(_LANG_TAG.sub("", user_text)), _bare(_SLOT.sub("", target))
    if not want or not said:
        return False
    # Vietnamese is monosyllabic: one token per syllable, so an attempt at a word
    # has as many tokens as the word. "Fen Bey." (2) is a shot at "sân bay" (2);
    # "no idea" (2) is not a shot at "nói" (1), however the letters fall.
    # Swept over all 129 targets a recall step can ask for against 43 real
    # interruptions: this alone takes the ones still wrongly eaten from 15 to 5,
    # and loses no attempt at all.
    #
    # Unless the target has a SLOT, in which case the answer is longer than the
    # pattern by whatever fills it -- "Tôi tên là Anna" against
    # "tôi tên là + [tên riêng]". Eleven constructions in the course have one,
    # and the count then only has to be at least the fixed part.
    if _has_slot(target):
        if len(said.split()) < len(want.split()):
            return False
    elif len(said.split()) != len(want.split()):
        return False
    return difflib.SequenceMatcher(None, said, want).ratio() >= RESEMBLES_TARGET_THRESHOLD


_QUESTION_MARK = re.compile(r"\?\s*$")


def learner_asked_something(user_text: str) -> bool:
    """A real question from the learner, in English.

    The escape hatch. Without it a plan steamrollers anything the learner says
    that is not the expected answer, which is the failure mode of any scripted
    tutor. Their turn still gets used, the plan simply does not advance past a
    step that was never actually done.
    """
    return "[lang:vi]" not in user_text and bool(_QUESTION_MARK.search(user_text.strip()))


# Above this many English words, the learner was talking to us rather than
# attempting a word. Answers are one or two words -- and a real attempt at
# Vietnamese arrives tagged [lang:vi] anyway, because the recogniser is told
# which word is due. Set low on purpose: the cost of being wrong one way is a
# model call we did not need, and the other way is a robot asking its next
# question over someone who just said "I don't know".
# Two, to meet listen.py's SPEECH_WORDS at the same number. They are the two
# halves of one decision and they used to disagree: the ear kept two words of
# English intact and this side ignored anything under three, so "hold on", "go
# back", "too fast" and "start again" were saved and then answered by nobody.
# "I forgot" only escaped because it is in _GAVE_UP -- a list, where a property
# was available.
FREE_SPEECH_WORDS = 2

# Saying so is not an attempt, and it is short. "I forgot" is two words, so it
# fell under the threshold above and the lesson carried on as if nothing had
# been said -- on a step the MODEL wrote, where the code cannot know what was
# asked and so cannot give the word back itself.
#
# This is a list, and lists are the shape this project distrusts. It is kept
# because it is closed by something outside the code: there are only so many
# ways a person says they do not know, and it does not grow when a model
# invents a new phrasing. If it starts growing, that is the signal to find the
# property instead.
_GAVE_UP = re.compile(
    r"\b(i (forgot|don'?t know|can'?t remember|have no idea)|no idea|dunno|"
    r"forgot|pass|skip( it)?|help)\b", re.IGNORECASE)


def learner_gave_up(user_text: str) -> bool:
    """They said they do not know. That always deserves an answer."""
    return "[lang:vi]" not in user_text and bool(_GAVE_UP.search(user_text))


def learner_spoke_freely(user_text: str) -> bool:
    """They said something that wants an answer, not the word that was asked.

    A scripted turn can only ask its question; it cannot react to anything. So
    whenever this fires the turn goes to the model, mechanical step or not --
    which is also the only way the remaining tools can still be called, since
    every one of them fires on something the learner said.
    """
    if "[lang:vi]" in user_text:
        return False
    if learner_asked_something(user_text) or learner_gave_up(user_text):
        return True
    return len(_LANG_TAG.sub("", user_text).split()) >= FREE_SPEECH_WORDS


def _recall_targets(store: ProgressStore, item: Item | None, pieces: list[Item],
                    seen_items: list[Item], count: int = N_RAPIDFIRE) -> list[Item]:
    """Which already-met items the bare recall slots will ask for.

    Drawn by level, so the least consolidated word is likeliest and a
    well-drilled one turns up rarely without ever dropping out. The item being
    taught and the pieces its own chain already covers are excluded -- asking
    for a word twice in the same handful of turns wastes a slot.

    Returns items, not names: a recall is asked from the English side, so the
    slot needs the gloss and not just the Vietnamese. Rules are excluded for
    the same reason there is no gloss to ask from -- nobody says a rule back.
    """
    by_name = {i.name: i for i in seen_items}
    exclude = {p.name for p in pieces}
    if item is not None:
        exclude.add(item.name)

    # A requested subject is worked, not sprinkled. While the item being taught
    # belongs to a theme the learner asked for, its recalls come from that theme
    # only. Found live: asked for a food lesson, the learner got "phở" and then
    # two recall turns on "I / me" and "name" -- the only other words that
    # existed. Correct spaced repetition, and it read as being ignored.
    # Fewer on-topic recalls beat three off-topic ones; the main course resumes
    # on its own once the theme's items run out.
    # A target has to be DRAWABLE, which is not the same as askable. A word's
    # gloss is read aloud as the whole question, so a grammar formula becomes
    # one live: measured, a rapidfire drew the item whose gloss is "do ... not?"
    # and asked "and again -- what was do not?". Nothing the learner can answer.
    # A discrete feature fails that test and is drawn anyway, because the turn
    # it produces is an APPLICATION and not a bare question -- see drawable().
    exclude |= {i.name for i in seen_items if not drawable(i)}

    only = None
    if item is not None and item.topic:
        only = {i.name for i in seen_items if i.topic == item.topic}
    drawn = store.draw_recalls(count, exclude=exclude, only=only)
    targets = [by_name[n] for n in drawn if n in by_name]

    # At most ONE application per item. Applications are long turns -- a whole
    # sentence produced -- where a bare recall is a single word, so stacking
    # them flattens the rhythm the way nine features in a row once did (9b).
    #
    # Not a preference: features start at level 0, and weight(0) is thirteen
    # times weight(4.5), so the transition period is the dangerous window.
    # Simulated on a three-slot close with features fresh and words drilled,
    # 86% of closes would carry two or more applications and 44% would carry
    # three. At equilibrium it falls to 8%, so this guard matters most exactly
    # when the change ships and costs almost nothing afterwards -- measured, one
    # application per feature over 120 items, and a gap of 22 items instead of 17.
    surplus = [t for t in targets if t.kind == "feature"][MAX_APPLICATIONS_PER_ITEM:]
    if surplus:
        keep = [t for t in targets if t not in surplus]
        refill = store.draw_recalls(
            len(surplus),
            exclude=exclude | {t.name for t in targets} | {i.name for i in seen_items if i.kind == "feature"},
            only=only)
        targets = keep + [by_name[n] for n in refill if n in by_name]
    return targets


def _take_next(queue_items: list[Item], seen_items: list[Item]) -> Item | None:
    """Pops whichever queued item may safely be taught next, or None if dry."""
    if not queue_items:
        return None
    return queue_items.pop(pick_next_index(queue_items, seen_items))


def _run_turn(api_key, messages, store, roster, queue_items, themes_generated_this_session,
              seen_items, lesson) -> bool:
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
                print(f"  [timing] first chunk received: {first_chunk_at - t0:.1f}s")
            buffer += text
            full_text += text
            while (m := _SENTENCE_BOUNDARY.search(buffer)):
                sentence = buffer[:m.end()].strip()
                buffer = buffer[m.end():]
                if sentence:
                    print(f"tutor: {sentence}")
                    voice.say(sentence)
        elif kind == "tool_calls":
            tool_calls_final = payload[0]
        # "tool_call_partial" ignored here -- only used by theme generation
        # to show item-by-item progress; the two tools left in conversation
        # have trivial arguments not worth streaming progress for.
    tail = buffer.strip()
    if tail:
        print(f"tutor: {tail}")
        voice.say(tail)

    if not full_text.strip() and tool_calls_final:
        # Code-level safety net, not a prompt tweak -- tested live: this
        # exact model calls a tool with zero spoken text roughly every
        # time the action is unambiguous, in 6/6 trials, regardless of
        # how forcefully the prompt or the tool's own description asks
        # for accompanying speech. Prompting alone cannot fix this, so
        # a silent tool call gets a minimal filler line instead of dead air.
        filler = random.choice(["Alright, let's continue.", "Okay, moving on.", "Great, let's keep going."])
        print(f"tutor: {filler}  [safety net: tool call with no text]")
        voice.say(filler)
        full_text = filler

    # Only model turns are checked: a scripted turn is built from the gloss and
    # cannot contain its own target, except on the retry line, where saying it
    # is the instruction.
    if _leaked_target(full_text, current_step(lesson)):
        print(f"  [diag] !! the answer was given away: this turn asked FOR "
              f"{current_step(lesson).target!r} and said it")
    _warn_if_answer_spoken(full_text, current_step(lesson), roster)

    voice.wait()  # never open the mic while our own voice is still playing
    print(f"  [timing] total (reply + speech): {time.monotonic() - t0:.1f}s")

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
                # Captured with the word itself: a spontaneous word joins the
                # recall pool like any other, and a recall is asked from the
                # English side, so an item that arrives without a gloss is one
                # the tutor can only ask for by naming it -- i.e. by giving the
                # answer away.
                gloss=args.get("gloss", "").strip(),
                kind="atom",
                source="personnel",
            )
            if store.is_new(word.name):
                add_personal_items(CONTENT_DIR, [word])
                roster.append(word)
                seen_items.append(word)
                store.mark_introduced(word.name)
                store.save()
                print(f"  (word remembered: {word.name})")
        elif fn["name"] == "set_session_focus" and args.get("topic"):
            topic = args["topic"].strip()
            if topic.lower() not in themes_generated_this_session:
                themes_generated_this_session.add(topic.lower())
                print(f"  (generating items for '{topic}' -- this can take a while...)")
                t_theme = time.monotonic()
                try:
                    new_items = generate_theme_items(api_key, topic, roster, N_THEME_GENERATE)
                except (RuntimeError, urllib.error.URLError, OSError, json.JSONDecodeError) as e:
                    # A side feature must never end the lesson. Found live the
                    # first time set_session_focus ever fired: generation 400'd,
                    # the exception climbed out of the tool handler, and a
                    # session that was otherwise fine died on its second turn.
                    # The learner keeps their lesson; the theme is simply lost.
                    print(f"  (theme generation failed, lesson continues: {e})")
                    new_items = []
                print(f"  [timing] theme generation: {time.monotonic() - t_theme:.1f}s")
                if new_items:
                    add_personal_items(CONTENT_DIR, new_items)
                    roster.extend(new_items)
                    queue_items[:0] = new_items  # jump the queue: requested content comes next
                    lesson["announce_topic"] = (topic, [i.gloss for i in new_items])
                    print(f"  (theme '{topic}': {len(new_items)} items generated, moved to the front of the queue)")
        elif fn["name"] == "deprioritize_item":
            if args.get("name"):
                store.deprioritize(args["name"])
                print(f"  (deprioritised: {args['name']})")
            if args.get("topic"):
                topic_lower = args["topic"].strip().lower()
                matched = [i.name for i in roster if (i.topic or "").lower() == topic_lower]
                for name in matched:
                    store.deprioritize(name)
                print(f"  (deprioritised: theme '{args['topic']}' -- {len(matched)} item(s))")
        elif fn["name"] == "remember_learner":
            # Merged field by field, never replaced: a name volunteered in one
            # session and an age three sessions later, and the second must not
            # wipe the first. Values are checked here rather than trusted --
            # the model is being asked about a person, which is exactly where
            # it is most tempted to fill in a blank it was not given.
            profile = learner_module.load(LEARNER_PATH)
            if args.get("name"):
                profile.name = str(args["name"]).strip()
            if args.get("gender") in learner_module.SELF_WHEN_OLDER:
                profile.gender = args["gender"]
            age = args.get("age")
            if isinstance(age, int) and 0 < age < 120:
                profile.age = age
            learner_module.save(LEARNER_PATH, profile)
            print(f"  (learner: {profile.summary() or 'nothing usable'})")

        messages.append({
            "role": "tool",
            "tool_call_id": call["id"],
            "content": tool_result,
        })

    return bool(tool_calls_final)


def _speak_scripted_turn(messages: list[dict], line: str) -> None:
    """Says a turn the code wrote itself. No request, no stream, no tools.

    The line still joins the history: the next model turn has to read a
    conversation that actually happened, or it sees the learner answering a
    question nobody asked.
    """
    t0 = time.monotonic()
    print(f"tutor: {line}  [scripted]")
    voice.say(line)
    voice.wait()  # never open the mic while our own voice is still playing
    print(f"  [timing] total (speech only, no model call): {time.monotonic() - t0:.1f}s")
    messages.append({"role": "assistant", "content": line})


# Safety cap on consecutive tool-only turns (no new user input in between).
# Rare now that only set_session_focus and deprioritize_item remain, but it
# still stops a pathological loop from running forever without handing control
# back to the learner.
MAX_CHAINED_TOOL_TURNS = 5


def _conversation_loop(api_key, messages, store, roster, queue_items, themes_generated_this_session,
                       seen_items, lesson):
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
            print(f"(auto) you: {user_input}")
        else:
            t0 = time.monotonic()
            # Tell the recogniser which Vietnamese word is due, when one is:
            # auto-detect hears the sound correctly and then writes it with
            # English spelling ("tên" came back as the digits "10").
            step = current_step(lesson)
            # Every step that asks the learner to produce something knows what
            # it asked for -- a recall names its word, and `vary`, `apply` and
            # `scaffold` carry the item they are building. Passing it is what
            # lets the recogniser compare rather than count: without it, rule
            # 25b guessed by length, and "Tôi tên là Anna" (four words) fell on
            # the "that is a sentence, decode it as English" side.
            expected = step.target if step and step.kind in RECALL_KINDS + _ASKING_KINDS else None
            user_input = listen_and_transcribe(expected=expected, matches=answered_target,
                                               resembles=resembles_target)
            print(f"  [timing] listen+transcribe: {time.monotonic() - t0:.1f}s")
            if not user_input:
                print("  (nothing heard, listening again)")
                continue
            print(f"you (transcribed): {user_input}")

        # The learner's turn is what closes the step the tutor just set up, so
        # the plan advances HERE, not after the tutor speaks. Turn zero is the
        # opening speech: it has no step to close and must not load an item, or
        # the tutor greets and teaches in the same breath.
        if turns_done > 0:
            done = current_step(lesson)
            lesson["verdict"] = None
            lesson["verdict_target"] = None
            lesson["answer_only"] = False
            lesson["react_only"] = False
            gave_up = learner_gave_up(user_input)
            if gave_up:
                # Not a question, so the step is still consumed -- but this turn
                # belongs to them: they asked, in as many words, to be told.
                lesson["gave_up"] = True
                print("  (learner said they don't know -- the answer is given before moving on)")
            # Was learner_asked_something, which needs a literal "?" -- and
            # transcribed speech rarely carries one. Live: "I have a question. I
            # don't understand Tentoylannam." held nothing, the step was scored
            # as missed, and the tutor answered about an unrelated word.
            #
            # learner_spoke_freely already means "they said something that wants
            # an answer, not the word asked for", and already forces a model
            # turn. It just did not hold the step -- so the code decided they
            # were talking to us, handed the turn over, and consumed the step
            # anyway. One condition, used for both, is the whole fix.
            if not gave_up and learner_spoke_freely(user_input) \
                    and lesson.get("waits", 0) < MAX_STEP_WAITS:
                lesson["answer_only"] = True
                lesson["waits"] = lesson.get("waits", 0) + 1
                print("  (learner is talking to us -- this turn answers them, the step waits)")
            elif _should_retry(done, user_input, lesson):
                # They answered a different word entirely. Worth one more go --
                # the plan used to advance regardless, so the "wrong word, Minh
                # says it, ask again" rule could never once fire and a missed
                # word was met with silence and the next question.
                lesson["retried"] = True
                print(f"  (missed '{done.target}' -- one more go)")
            else:
                # The step is done, so the waiting budget starts fresh for the
                # next one.
                lesson["waits"] = 0
                # If it asked for a word, that IS the exposure -- recorded here,
                # where the code knows exactly what it asked, instead of being
                # reconstructed afterwards by a model re-reading the transcript.
                if done is not None and done.kind in RECALL_KINDS and done.target:
                    # The code has already decided whether this was right. Pass
                    # that decision on, or the model judges again from the raw
                    # transcription and contradicts it -- seen live, three turns
                    # running where the level went up and the tutor said "I
                    # didn't catch that" in the same breath.
                    got_it = answered_target(user_input, done.target)
                    lesson["verdict"] = "correct" if got_it else "missed_twice"
                    lesson["verdict_target"] = done.target
                    store.record_recall(done.target, got_it)
                    print(f"  [level] {done.target} -> {store.level(done.target)}"
                          f"{'' if got_it else '  (missed — comes back sooner)'}")
                elif done is not None and done.kind == "apply" and done.target:
                    # An application counts as EXPOSURE, never as a score. It
                    # asks for a whole sentence, so there is no single target to
                    # compare against and nothing the code can honestly judge --
                    # and handing that judgement to the model would give back a
                    # decision this project spent weeks bringing into the code.
                    #
                    # Not optional, either. The draw is weighted by level and
                    # weight(0) is thirteen times weight(4.5), so a feature that
                    # never left zero would be drawn forever in preference to
                    # every word. Counting the exposure is what makes "as often
                    # as a word" true rather than "far more, permanently".
                    store.record_recall(done.target, got_it=True)
                    print(f"  [level] {done.target} -> {store.level(done.target)}  (applied)")
                lesson["retried"] = False
                # A step the MODEL wrote asked something only it can mark. Give
                # it the next turn to react, before the plan moves on.
                if done is not None and done.kind not in SCRIPTED_KINDS:
                    lesson["react_only"] = True
                lesson["i"] += 1
            if current_step(lesson) is None:
                item = _take_next(queue_items, seen_items)
                if item is not None:
                    seen_items.append(item)
                start_item(lesson, item, seen_items, store)
                store.save()  # progress survives a crash without waiting for the end

        messages.append({"role": "user", "content": user_input})

        # The OPENING SPEECH belongs to the model -- but only that, and it is
        # recognised by having no plan, not by being turn zero. Blanket-
        # excluding turn zero handed the first teaching turn of every
        # --no-intro session to the model, and measured live it produced both
        # faults the script exists to prevent: a stage direction read aloud
        # ("Minh, please say the word.") and a question stating its own answer
        # ("So how would you say thích?").
        # turns_done > 0 because the opening "Hi, I'm ready." is written by this
        # loop, not said by anyone -- and at three words it tripped the
        # free-speech test, handing the first teaching turn back to the model
        # and undoing the fix above.
        line = None
        if lesson["plan"] and not lesson.get("react_only") and not (
                turns_done > 0 and learner_spoke_freely(user_input)):
            line = scripted_turn(lesson)
        if line is not None:
            _speak_scripted_turn(messages, line)
        else:
            for _ in range(MAX_CHAINED_TOOL_TURNS):
                had_tool_calls = _run_turn(api_key, messages, store, roster, queue_items,
                                           themes_generated_this_session, seen_items, lesson)
                if not had_tool_calls:
                    break  # model gave its final spoken reply for this turn -- back to listening
        turns_done += 1


def run_session(fresh: bool = False, no_intro: bool = False):
    """Runs one lesson.

    Both flags exist for working ON the tutor rather than with it. `fresh`
    starts from the first word and saves nothing, so runs are comparable.
    `no_intro` skips the opening speech, which is 55 seconds of synthesis
    standing between you and the thing you are trying to test.
    """
    flags = [n for n, on in (("fresh: nothing saved", fresh), ("no intro", no_intro)) if on]
    print("Starting session..." + (f"  [{', '.join(flags)}]" if flags else ""))
    api_key = load_api_key()
    persona_prompt = load_persona_system_prompt(CONTENT_DIR)
    # Curated roster FIRST. It is a composed progression -- atoms, then the
    # construction that assembles them -- whereas live-generated personal items
    # are mostly whole phrases. Found live: prepending personal items opened a
    # brand-new session on "Rất vui được gặp bạn", a five-word phrase whose
    # words had never been taught. pick_next_index guards this properly now;
    # the order here just stops the guard from having to fight the queue.
    roster = load_course(CONTENT_DIR)
    store = ProgressStore(None if fresh else STATE_PATH)

    today = date.today()
    by_name = {i.name: i for i in roster}
    all_names = [i.name for i in roster]
    # Forward sequence is NEW items in roster order only. Due reviews are not
    # drawn as items -- they ride along in the lesson note as the pieces to
    # re-cite, which is where revision belongs in this method.
    # Unteachable items are kept in the roster but never queued: an imported
    # word with no gloss yet is real vocabulary, just not a lesson.
    queue_items = [by_name[n] for n in store.select_new(all_names) if is_teachable(by_name[n])]
    # In TEACHING order, read back from the state file, not roster order: the
    # spacing checks look at the last few items seen, so a history rebuilt in
    # the wrong order makes them pick a different next item than the run that
    # wrote the state.
    by_name = {i.name: i for i in roster}
    seen_items = [by_name[n] for n in store.taught_order() if n in by_name]
    # An empty plan means the opening turn: the tutor greets, and the first
    # item is loaded only once that turn is behind us.
    lesson = {"item": None, "plan": [], "i": 0, "started": False, "retried": False,
              "verdict": None, "verdict_target": None, "phrasing": {}, "answer_only": False}
    global voice
    voice = SpeechPipeline(_vocab_words(roster))
    themes_generated_this_session: set[str] = set()

    print(f"--- Reservoir ready: {len(queue_items)} items to teach ---")
    # Authoring defects, named at startup instead of degrading a lesson
    # silently: an item with no gloss makes the tutor improvise the meaning
    # side of its own question, which is how a recall ends up stating its
    # answer. Run fill_item_metadata.py to fix them.
    # Summarised, not listed. A bulk import legitimately lands hundreds of items
    # with no gloss yet, and one line each buried every other startup message
    # under the same sentence repeated -- which is how a report stops being read.
    problems = check_roster(roster)
    awaiting = [p.split(":")[0] for p in problems if "no gloss" in p]
    if awaiting:
        print(f"  [content] {len(awaiting)} item(s) awaiting a gloss, held out of lessons "
              f"({', '.join(awaiting[:4])}…) — run fill_item_metadata.py")
    for problem in (p for p in problems if "no gloss" not in p):
        print(f"  [content] {problem}")

    if no_intro:
        # Loading an item up front means turn one already carries a teaching
        # instruction, so the opening branch of the note is never reached.
        # Decided here rather than asked of the model: an earlier attempt put
        # "skip the opening speech" in the prompt and it was over-applied --
        # the model dropped ALL spoken content, teaching included.
        item = _take_next(queue_items, seen_items)
        if item is not None:
            seen_items.append(item)
        start_item(lesson, item, seen_items, store)

    messages = [{"role": "system", "content": persona_prompt}]

    print("Ctrl+C ends the session and saves your progress. No Enter needed from here on.\n")

    try:
        _conversation_loop(api_key, messages, store, roster, queue_items,
                           themes_generated_this_session, seen_items, lesson)
    finally:
        # Runs even on a fatal crash (e.g. the free model staying saturated
        # through every retry) -- found live: without this, a mid-session
        # outage lost the whole session, since saving only ever happened
        # after a clean /fin.
        store.save()
        print("\n--- End of session ---")
        print(store.summary())
        # Ask the store, do not assume the constant: under --fresh it holds no
        # path and saved nothing, and this is the one line of the session the
        # learner has no way to check for themselves.
        if store.path is None:
            print("\nNothing saved — this was a --fresh run.")
        else:
            print(f"\nProgress saved to {store.path}")


if __name__ == "__main__":
    run_session(fresh="--fresh" in sys.argv, no_intro="--no-intro" in sys.argv)

"""Fills the teaching metadata (kind, gloss, pieces, literal) on content items.

The course used to carry only the Vietnamese side of each item. Everything the
tutor needed on the English side -- what the word MEANS, which pieces a
sentence is assembled from, what its literal word order is -- had to be
improvised by the model at lesson time, and measured live it improvised badly:
recalls that stated their own answer ("So how would you say là?"), rules
treated as sentences to build.

So it becomes data. Not hand-written data though: this fills it in batch, once
per content file, and is re-runnable -- it only ever touches items where a
field is missing, so new lesson files added later cost one more run and nothing
else. Review the diff, not the items one by one.

    python fill_item_metadata.py            # show what would change
    python fill_item_metadata.py --write    # apply it

Run: python fill_item_metadata.py
"""
import json
import sys
import time
import tomllib
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from content import (
    KINDS, PERSONAL_ITEMS_FILENAME, derive_pieces, load_personal_items, load_roster,
)
from tutor import CONTENT_DIR, call_llm, load_api_key

FILL_TOOL = [
    {
        "type": "function",
        "function": {
            "name": "set_item_metadata",
            "description": "Teaching metadata for every item you were given.",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "the item name, copied EXACTLY as given"},
                                "kind": {"type": "string", "enum": sorted(KINDS)},
                                "gloss": {
                                    "type": "string",
                                    "description": (
                                        "what it means, in English, as short as possible -- this is read aloud as "
                                        "the question ('how do you say ___?'), so it must be a natural English "
                                        "word or phrase, not a grammatical description. 'I / me', 'name', "
                                        "'to want', 'my name is ___'."
                                    ),
                                },
                                # No `pieces` here: repair_pieces computes it
                                # from the name before this pass runs, and asking
                                # again only invites a worse answer -- seen in
                                # the same dry run, the model offered ["không"]
                                # where the code had read ["bạn", "không"].
                                "hook": {
                                    "type": "string",
                                    "description": (
                                        "ONE true sentence of context in English, spoken just before the "
                                        "word is revealed -- or an empty string, which is the normal answer. "
                                        "The BEST hook takes a word apart into words that are themselves "
                                        "real: sân bay is sân (yard) + bay (to fly), Hà Nội is hà (river) + "
                                        "nội (inside). The learner thinks they are filing one word and files "
                                        "two, and the second sticks because it arrived inside something they "
                                        "already knew. Both halves must be genuine words -- a decomposition "
                                        "you are not sure of is exactly the invention to avoid. "
                                        "Otherwise write one where the plain template would be circular or "
                                        "flat: a word the learner already knows in English (phở, cà phê), a "
                                        "word whose origin explains its shape. It is read aloud, so keep it to one "
                                        "sentence and make it concrete. NEVER guess: if you are not certain "
                                        "the fact is true, return an empty string. An invented etymology is "
                                        "worse than no hook at all."
                                    ),
                                },
                                "literal": {
                                    "type": "string",
                                    "description": (
                                        "constructions only: the word-by-word English of the Vietnamese order, "
                                        "which is what lets a beginner produce a sentence they have never heard. "
                                        "'tôi tên là + [tên riêng]' -> 'I name is [name]'. Empty otherwise."
                                    ),
                                },
                            },
                            "required": ["name", "kind", "gloss"],
                        },
                    }
                },
                "required": ["items"],
            },
        },
    }
]

INSTRUCTIONS = (
    "You are annotating a Vietnamese beginner course so its tutor can ask questions from the "
    "English side instead of guessing them.\n\n"
    "kind is how the item is TAUGHT:\n"
    "  atom          one thing the learner says and is introduced as a unit. A multi-word lexical "
    "block is still an atom: 'cà phê' and 'cảm ơn' are single units, NOT assemblies.\n"
    "  construction  a sentence pattern assembled out of OTHER items in the list below. Only use "
    "this when the pieces are genuinely items already in the list.\n"
    "  rule          a fact the tutor states about the language, which the learner never says back. "
    "The name is a description, not Vietnamese speech: 'cách chọn từ xưng hô', "
    "\"tính từ không cần 'là'\". These get no pieces and no literal.\n\n"
    "gloss is spoken aloud to the learner as the question. Write the meaning, not the grammar: "
    "'I / me', not 'first person pronoun'. For a construction with a placeholder, keep the "
    "placeholder in English: 'my name is ___'.\n\n"
    "hook is almost always empty. Write one only when the item is a word the learner already "
    "knows in English, or a name that means something, or has an origin worth a sentence -- and only "
    "when you are certain it is true. A wrong fact spoken aloud is worse than a plain introduction.\n\n"
    "Some names carry an authoring label before a colon ('phủ định động từ: không + [động từ]'). "
    "The label is not spoken; gloss and literal describe what follows it.\n\n"
    "Call set_item_metadata once, with an entry for every item you were given."
)


def _needs_fill(raw: dict) -> bool:
    """True if anything is still missing. Constructions need more than atoms,
    but kind is what says so -- and kind itself may be what is missing, so an
    item with no kind always counts as incomplete."""
    if "kind" not in raw or not raw.get("gloss"):
        return True
    # `pieces` is deliberately not checked here: repair_pieces derives it
    # offline just above, so a construction missing it is not a model's job.
    if raw["kind"] == "construction" and not raw.get("literal"):
        return True
    return False


# Items per request. Groq's free tier allows ~8000 tokens a minute and each
# item carries a paragraph of Vietnamese notes, so a whole file in one call
# blows the budget -- measured: 25 items in one request 429'd through every
# retry. Small batches also mean a rate limit costs one batch, not a file.
BATCH_SIZE = 8

# And spaced out. The retry backoff alone was not enough: a batch costs roughly
# a third of the minute's tokens, so back-to-back batches ran the bucket dry and
# a whole file died partway through. Waiting is free here -- this is an offline
# authoring pass, not a lesson anybody is sitting through.
SECONDS_BETWEEN_BATCHES = 30


def _ask(api_key: str, targets: list[dict], all_names: list[str]) -> dict[str, dict]:
    """Metadata for every target, keyed by item name, in paced batches."""
    out: dict[str, dict] = {}
    for start in range(0, len(targets), BATCH_SIZE):
        batch = targets[start:start + BATCH_SIZE]
        if start:
            time.sleep(SECONDS_BETWEEN_BATCHES)
        print(f"  ({start + 1}-{start + len(batch)} of {len(targets)}...)")
        out.update(_ask_batch(api_key, batch, all_names))
    return out


def _ask_batch(api_key: str, targets: list[dict], all_names: list[str]) -> dict[str, dict]:
    catalogue = "\n".join(f"{n}. {name}" for n, name in enumerate(all_names, 1))
    described = "\n\n".join(
        f"{t['name']}\n  category: {t.get('category', '?')}\n  notes (Vietnamese): {t.get('description', '')}"
        for t in targets
    )
    response = call_llm(
        api_key,
        [
            {"role": "system", "content": INSTRUCTIONS},
            {
                "role": "user",
                "content": (
                    f"The whole course, in teaching order:\n{catalogue}\n\n"
                    f"Annotate exactly these {len(targets)} items:\n\n{described}"
                ),
            },
        ],
        tools=FILL_TOOL,
    )
    calls = response["choices"][0]["message"].get("tool_calls") or []
    if not calls:
        raise RuntimeError("the model answered without calling set_item_metadata")
    out: dict[str, dict] = {}
    for call in calls:
        for entry in json.loads(call["function"]["arguments"])["items"]:
            out[entry["name"]] = entry
    return out


def _clean(entry: dict, known_names: set[str]) -> dict:
    """Keeps only what belongs on this kind of item.

    `pieces` is not among them -- repair_pieces owns that field now, and letting
    this pass write it too would undo the derivation with a worse guess.
    """
    kind = entry.get("kind", "atom")
    if kind not in KINDS:
        kind = "atom"
    fields = {"kind": kind, "gloss": entry.get("gloss", "").strip(),
              "hook": (entry.get("hook") or "").strip()}
    if kind == "construction":
        fields["literal"] = entry.get("literal", "").strip()
    return fields


def _toml_value(value) -> str:
    if isinstance(value, list):
        return "[" + ", ".join(_toml_value(v) for v in value) + "]"
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _insert_into_toml(text: str, name: str, fields: dict) -> str:
    """Inserts the new keys straight after the item's `name =` line.

    Targeted text insertion rather than a re-serialised TOML: it keeps the
    files' comments and formatting exactly as authored. It RAISES when the
    anchor line is not found or is ambiguous -- a bulk replacement that
    silently matches nothing has cost this project a round of live testing more
    than once, and a no-op here would look like a successful run.
    """
    anchor = f"name = {_toml_value(name)}"
    lines = text.splitlines(keepends=True)
    hits = [n for n, line in enumerate(lines) if line.strip() == anchor]
    if len(hits) != 1:
        raise RuntimeError(f"anchor {anchor!r}: expected exactly one line, found {len(hits)}")
    added = "".join(f"{key} = {_toml_value(val)}\n" for key, val in fields.items())
    lines.insert(hits[0] + 1, added)
    return "".join(lines)


def _report(path: Path, name: str, fields: dict) -> None:
    print(f"  {name}")
    for key, val in fields.items():
        print(f"      {key} = {_toml_value(val)}")


def fill_toml(path: Path, api_key: str, all_names: list[str], write: bool) -> int:
    text = path.read_text(encoding="utf-8")
    raws = tomllib.loads(text).get("items", [])
    targets = [r for r in raws if _needs_fill(r)]
    if not targets:
        print(f"{path.name}: nothing missing")
        return 0
    print(f"{path.name}: filling {len(targets)} item(s)")
    filled = _ask(api_key, targets, all_names)
    known = set(all_names)
    for raw in targets:
        entry = filled.get(raw["name"])
        if entry is None:
            print(f"  !! {raw['name']}: the model returned nothing for this one, left as is")
            continue
        fields = {k: v for k, v in _clean(entry, known).items() if k not in raw or not raw.get(k)}
        if not fields:
            continue
        _report(path, raw["name"], fields)
        text = _insert_into_toml(text, raw["name"], fields)
    if write:
        path.write_text(text, encoding="utf-8")
    return len(targets)


def fill_json(path: Path, api_key: str, all_names: list[str], write: bool) -> int:
    entries = json.loads(path.read_text(encoding="utf-8"))
    targets = [e for e in entries if _needs_fill(e)]
    if not targets:
        print(f"{path.name}: nothing missing")
        return 0
    print(f"{path.name}: filling {len(targets)} item(s)")
    filled = _ask(api_key, targets, all_names)
    known = set(all_names)
    for raw in targets:
        entry = filled.get(raw["name"])
        if entry is None:
            print(f"  !! {raw['name']}: the model returned nothing for this one, left as is")
            continue
        fields = {k: v for k, v in _clean(entry, known).items() if k not in raw or not raw.get(k)}
        if not fields:
            continue
        _report(path, raw["name"], fields)
        raw.update(fields)
    if write:
        path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(targets)


def repair_pieces(personal: Path, roster: list, write: bool) -> int:
    """Recomputes `pieces` on every generated construction, offline.

    Runs before anything else and costs no request: pieces are read off the
    name against the roster, never asked of a model. That is the whole point --
    measured on this file, the model got 8 of its 13 constructions wrong, one
    declaring a single piece for an eight-word sentence and one declaring none.

    Only the generated file is touched. Hand-written TOML stays authoritative:
    derive_pieces reproduces all five of its constructions exactly, so there is
    nothing to repair there and no reason to let code overwrite an author.
    """
    if not personal.exists():
        return 0
    entries = json.loads(personal.read_text(encoding="utf-8"))
    changed = 0
    for entry in entries:
        if entry.get("kind") != "construction":
            continue
        derived = derive_pieces(entry["name"], roster)
        if derived != entry.get("pieces"):
            print(f"  {entry['name']}")
            print(f"     was  {entry.get('pieces')}")
            print(f"     now  {derived}")
            entry["pieces"] = derived
            changed += 1
    if changed and write:
        personal.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{personal.name}: {changed} construction(s) re-derived")
    return changed


def main() -> int:
    write = "--write" in sys.argv
    api_key = load_api_key()
    lesson_files = sorted(p for p in CONTENT_DIR.glob("*.toml") if p.name != "persona.toml")
    personal = CONTENT_DIR / PERSONAL_ITEMS_FILENAME

    # Every name in the course, in teaching order: pieces may only reference
    # items that exist, and the model needs the whole catalogue to resolve them
    # even while annotating one file at a time.
    all_names = []
    for path in lesson_files:
        all_names += [r["name"] for r in tomllib.loads(path.read_text(encoding="utf-8")).get("items", [])]
    if personal.exists():
        all_names += [e["name"] for e in json.loads(personal.read_text(encoding="utf-8"))]

    # Offline and free, so it goes first and always: no point paying a model to
    # annotate items whose structural field is wrong.
    total = repair_pieces(personal, load_roster(CONTENT_DIR) + load_personal_items(CONTENT_DIR), write)

    total += sum(fill_toml(path, api_key, all_names, write) for path in lesson_files)
    if personal.exists():
        total += fill_json(personal, api_key, all_names, write)

    if not write:
        print(f"\n{total} item(s) would change. Re-run with --write to apply.")
    else:
        print(f"\n{total} item(s) written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

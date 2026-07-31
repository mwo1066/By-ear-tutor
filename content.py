"""Loads the roster (ordered items) and persona from the TOML content files."""
import json
import re
import tomllib
from dataclasses import dataclass, asdict
from pathlib import Path

PERSONAL_ITEMS_FILENAME = "personal_items.json"


@dataclass
class Item:
    name: str
    item_type: str
    category: str
    language: str
    description: str
    source: str = "roster"  # "roster" (curated TOML) or "personnel" (LLM-generated live)
    topic: str | None = None  # theme this item was generated for, if any -- lets a whole theme be deprioritized at once


def load_roster(content_dir: Path) -> list[Item]:
    """Reads lesson files in filename order, items in file order — same
    insertion-order-is-the-contract rule as memai's bundle format."""
    items: list[Item] = []
    lesson_files = sorted(p for p in content_dir.glob("*.toml") if p.name != "persona.toml")
    for path in lesson_files:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        for raw in data.get("items", []):
            items.append(Item(
                name=raw["name"],
                item_type=raw["type"],
                category=raw["category"],
                language=raw["language"],
                description=raw["description"],
            ))
    return items


def load_personal_items(content_dir: Path) -> list[Item]:
    """Items added live (theme requests, spontaneous words) — same shape as
    roster items, persisted separately so the curated TOML files stay
    untouched by anything generated on the fly."""
    path = content_dir / PERSONAL_ITEMS_FILENAME
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [Item(**entry) for entry in raw]


def save_personal_items(content_dir: Path, items: list[Item]) -> None:
    path = content_dir / PERSONAL_ITEMS_FILENAME
    path.write_text(
        json.dumps([asdict(i) for i in items], ensure_ascii=False, indent=2), encoding="utf-8"
    )


def add_personal_items(content_dir: Path, new_items: list[Item]) -> None:
    """Appends to the personal-items store, skipping names already present
    (roster or personal) so a repeated theme/word request doesn't duplicate."""
    existing = load_personal_items(content_dir)
    known_names = {i.name for i in existing} | {i.name for i in load_roster(content_dir)}
    existing.extend(i for i in new_items if i.name not in known_names)
    save_personal_items(content_dir, existing)


def _tokens(name: str) -> list[str]:
    """Vietnamese words in an item name, minus scaffolding.

    Names mix real target text with authoring scaffolding -- placeholders
    ("+ [tên riêng]"), ellipses, and a descriptive label before a colon
    ("phủ định động từ: không + ..."). Only what follows the colon is text the
    learner ever says, so the label is dropped before splitting.
    """
    name = _PLACEHOLDER.sub(" ", name.split(":", 1)[-1])
    out = []
    for tok in name.split():
        if tok in {"+", "..."}:
            continue
        tok = tok.strip("+[]?.,!:'\"…").lower()
        if tok:
            out.append(tok)
    return out


# Whole bracketed spans, not just the opening token: skipping only tokens that
# START with "[" left the tail behind, so "+ [tên riêng]" yielded a phantom
# "riêng" that no learner ever says and that broke matching against real speech.
_PLACEHOLDER = re.compile(r"\[[^\]]*\]")


def vocab_set(items: list[Item]) -> frozenset[str]:
    """Item names that are a single word -- the atoms the course actually teaches.

    Multi-word names are constructions built from these; anything in a name
    that is NOT one of these is authoring prose, not vocabulary.
    """
    return frozenset(n[0] for i in items if len(n := _tokens(i.name)) == 1)


def unknown_pieces(item: Item, seen_items: list[Item], vocab: frozenset[str]) -> list[str]:
    """Vocabulary words this item is made of that have NOT been taught yet.

    A single-word item is an atom, not a composition -- it has no pieces, and
    must not count itself as one. Without this it outranked nothing and even
    lost to multi-word items made of non-vocabulary tokens, which put "cảm ơn"
    ahead of "tôi" on a fresh session.
    """
    tokens = _tokens(item.name)
    if len(tokens) <= 1:
        return []
    seen_words = {w for i in seen_items for w in _tokens(i.name)}
    return [t for t in tokens if t in vocab and t not in seen_words]


def pick_next_index(queue: list[Item], seen_items: list[Item], vocab: frozenset[str]) -> int:
    """Index of the next item that may safely be taught.

    Queue order is the composed progression and leads: normally this is simply
    the first item in the queue. The only thing that can override it is the one
    guarantee the prompt cannot make on its own -- a multi-word phrase never
    surfaces before the words it is made of -- so an item whose pieces are still
    unknown is passed over until they land.

    Deliberately NOT "all single words first": that drains every atom in the
    course before the first construction, whereas the method introduces two or
    three words and immediately combines them.

    If nothing is fully teachable (a phrase whose words the course never teaches
    separately), the least-blocked item wins rather than deadlocking.
    """
    ready = [i for i, item in enumerate(queue) if not unknown_pieces(item, seen_items, vocab)]
    if ready:
        return ready[0]
    return min(range(len(queue)), key=lambda i: (len(unknown_pieces(queue[i], seen_items, vocab)), i))


def pieces_of(item: Item, already_seen: list[Item]) -> list[Item]:
    """The already-taught items whose name appears inside this item's name.

    Roster constructions are literally spelled out of earlier words
    ("tôi tên là + [tên riêng]" is tôi + tên + là), so this recovers the
    assembly the learner has to make -- which is exactly the set the tutor
    must re-cite one at a time before asking for the full sentence.
    """
    def tokens(name: str) -> list[str]:
        return [w for w in (t.strip("+[]?.,!:").lower() for t in name.split()) if w]

    target = tokens(item.name)
    return [
        i for i in already_seen
        if i.name != item.name and (t := tokens(i.name)) and _contains_run(target, t)
    ]


def _contains_run(haystack: list[str], needle: list[str]) -> bool:
    """True if `needle`'s words appear consecutively somewhere in `haystack`."""
    n = len(needle)
    return any(haystack[i:i + n] == needle for i in range(len(haystack) - n + 1))


def load_persona_system_prompt(content_dir: Path) -> str:
    data = tomllib.loads((content_dir / "persona.toml").read_text(encoding="utf-8"))
    return data["persona"]["system_prompt"]

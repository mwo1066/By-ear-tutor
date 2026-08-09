"""Loads the roster (ordered items) and persona from the TOML content files."""
import json
import tomllib
from dataclasses import dataclass, asdict, field
from pathlib import Path

PERSONAL_ITEMS_FILENAME = "personal_items.json"

# How an item is TAUGHT -- the only axis the turn planner branches on.
#   atom          a single thing the learner says, taught by introducing it
#                 ("tôi", and also multi-word units like "cà phê" that are one
#                 lexical block, not an assembly)
#   construction  a sentence pattern assembled out of items already taught
#   rule          something the tutor STATES; the learner never says it back,
#                 so it is never a recall target ("tính từ không cần 'là'")
KINDS = {"atom", "construction", "rule"}


@dataclass
class Item:
    name: str
    item_type: str
    category: str
    language: str
    description: str
    # The English side of the pair. Load-bearing, not decoration: the code
    # forms every question FROM the gloss and asks for the name, so without it
    # the model has to invent the meaning side -- and measured live, it as
    # often just parroted the target back ("So how would you say là?"), which
    # is a question containing its own answer.
    gloss: str = ""
    kind: str = "atom"
    # For a construction: the exact item names it is assembled from, in order.
    # Written down rather than recovered by splitting the name on spaces --
    # that guesswork read "cà phê" as two pieces, and found "không" + "là"
    # inside the rule "tính từ không cần 'là'", making a rule look like a
    # sentence to build.
    pieces: list[str] = field(default_factory=list)
    # The literal word-by-word order in English ("I name is [name]"), which is
    # the scaffold the learner needs before producing a sentence whose order
    # differs from their own. Cannot always be derived from the pieces' glosses
    # -- "không phải là" runs through "phải", which the course never teaches.
    literal: str = ""
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
                gloss=raw.get("gloss", ""),
                kind=raw.get("kind", "atom"),
                pieces=list(raw.get("pieces", [])),
                literal=raw.get("literal", ""),
            ))
    return items


def check_roster(items: list[Item]) -> list[str]:
    """Authoring defects that would silently degrade a lesson, as messages.

    Reported at startup rather than discovered live: a missing gloss does not
    crash anything, it just makes the tutor improvise the meaning side of a
    question, which is how a recall ends up giving away its own answer.
    """
    known = {i.name for i in items}
    problems = []
    for i in items:
        if i.kind not in KINDS:
            problems.append(f"{i.name}: unknown kind {i.kind!r}")
        if not i.gloss and i.kind != "rule":
            problems.append(f"{i.name}: no gloss — questions about it cannot be asked from the meaning side")
        if i.kind == "construction" and not i.pieces:
            problems.append(f"{i.name}: construction with no pieces listed")
        for p in i.pieces:
            if p not in known:
                problems.append(f"{i.name}: piece {p!r} is not an item in the roster")
    return problems


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


def unknown_pieces(item: Item, seen_items: list[Item]) -> list[str]:
    """The item's declared pieces that have NOT been taught yet.

    A plain lookup now that pieces are authored rather than recovered from the
    name. The string-splitting version had to guess what counted as a word and
    got it wrong in both directions -- "cà phê" looked like an assembly of two
    unknown pieces, and the rule "tính từ không cần 'là'" looked like a
    sentence built from "không" and "là".
    """
    seen = {i.name for i in seen_items}
    return [p for p in item.pieces if p not in seen]


def pick_next_index(queue: list[Item], seen_items: list[Item]) -> int:
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
    ready = [i for i, item in enumerate(queue) if not unknown_pieces(item, seen_items)]
    if ready:
        return ready[0]
    return min(range(len(queue)), key=lambda i: (len(unknown_pieces(queue[i], seen_items)), i))


def pieces_of(item: Item, already_seen: list[Item]) -> list[Item]:
    """The already-taught items this construction is assembled from, in the
    order they are declared -- exactly the set the tutor must re-cite one at a
    time before asking for the full sentence.
    """
    by_name = {i.name: i for i in already_seen}
    return [by_name[p] for p in item.pieces if p in by_name]


def load_persona_system_prompt(content_dir: Path) -> str:
    data = tomllib.loads((content_dir / "persona.toml").read_text(encoding="utf-8"))
    return data["persona"]["system_prompt"]

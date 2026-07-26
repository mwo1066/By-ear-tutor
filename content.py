"""Loads the roster (ordered items) and persona from the TOML content files."""
import json
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


def load_persona_system_prompt(content_dir: Path) -> str:
    data = tomllib.loads((content_dir / "persona.toml").read_text(encoding="utf-8"))
    return data["persona"]["system_prompt"]


def format_items_for_prompt(items: list[Item]) -> str:
    """A compact block telling the LLM exactly which items to work today,
    in order — replaces memai's selection payload for this simple standalone version."""
    lines = ["Items a travailler cette session, dans cet ordre (ne pas en sauter, ne pas en ajouter d'autres) :"]
    for i, item in enumerate(items, 1):
        lines.append(f"{i}. [{item.item_type}/{item.category}] {item.name} — {item.description}")
    return "\n".join(lines)

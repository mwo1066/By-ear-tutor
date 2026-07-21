"""Loads the roster (ordered items) and persona from the TOML content files."""
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Item:
    name: str
    item_type: str
    category: str
    language: str
    description: str


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

"""Spaced repetition (half-life regression), simplified from memai's model.

Each item has: half_life_days, last_practiced_on, retrievals, errors,
sessions_practiced, user_initiated. Same core rule as memai:
- half-life only moves once per calendar day (sleep-gated)
- an error shrinks it; a success (with no error) grows it
- retrievals count successful recalls only, not mere exposure
"""
import json
from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path

INITIAL_HALF_LIFE = 1.0
GROWTH = 2.0
SHRINK = 0.5
MIN_HALF_LIFE = 0.5
USER_INITIATED_BOOST = 2.0


@dataclass
class ItemState:
    name: str
    half_life_days: float = INITIAL_HALF_LIFE
    last_practiced_on: str | None = None
    retrievals: int = 0
    errors: int = 0
    sessions_practiced: int = 0
    user_initiated: bool = False
    deprioritized: bool = False


def retention(state: ItemState, today: date) -> float:
    """Estimated retention in [0, 1]; -1.0 if never practiced (most due)."""
    if state.last_practiced_on is None:
        return -1.0
    last = date.fromisoformat(state.last_practiced_on)
    days_since = max((today - last).days, 0)
    return 2.0 ** (-days_since / state.half_life_days)


def update_after_practice(
    state: ItemState, today: date, retrievals: int, errors: int, user_initiated: bool = False
) -> ItemState:
    new_day = state.last_practiced_on is None or date.fromisoformat(state.last_practiced_on) < today
    half_life = state.half_life_days
    if state.last_practiced_on is None:
        initial = INITIAL_HALF_LIFE * (USER_INITIATED_BOOST if user_initiated else 1.0)
        half_life = initial
    elif new_day:
        if errors > 0:
            half_life = max(half_life * SHRINK, MIN_HALF_LIFE)
        elif retrievals > 0:
            half_life *= GROWTH
    return ItemState(
        name=state.name,
        half_life_days=half_life,
        last_practiced_on=today.isoformat(),
        retrievals=state.retrievals + retrievals,
        errors=state.errors + errors,
        sessions_practiced=state.sessions_practiced + 1,
        user_initiated=state.user_initiated or user_initiated,
    )


class ProgressStore:
    """Loads/saves per-item SRS state to a local JSON file."""

    def __init__(self, path: Path):
        self.path = path
        self._states: dict[str, ItemState] = {}
        if path.exists():
            raw = json.loads(path.read_text(encoding="utf-8"))
            self._states = {name: ItemState(**s) for name, s in raw.items()}

    def get(self, name: str) -> ItemState | None:
        return self._states.get(name)

    def set(self, state: ItemState) -> None:
        self._states[state.name] = state

    def deprioritize(self, name: str) -> None:
        """Learner asked to stop working on this item. Doesn't remove it or
        its history -- just pushes it to the back of both the review and new
        queues in select_today, so in practice it stops surfacing without
        breaking a roster item other items may build on."""
        existing = self._states.get(name) or ItemState(name=name)
        existing.deprioritized = True
        self._states[name] = existing

    def save(self) -> None:
        raw = {name: asdict(s) for name, s in self._states.items()}
        self.path.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")

    def is_new(self, name: str) -> bool:
        s = self._states.get(name)
        return s is None or s.last_practiced_on is None

    def _is_deprioritized(self, name: str) -> bool:
        s = self._states.get(name)
        return s.deprioritized if s else False

    def select_new(self, all_item_names: list[str], limit: int = 30) -> list[str]:
        """The forward sequence: never-practiced items in ROSTER ORDER, full stop.

        Roster order is a composed progression (words first, then the
        construction that assembles them) -- reordering it breaks the method,
        so nothing here sorts by retention. Deprioritized items go to the back
        rather than being dropped, since later constructions may build on them.
        """
        new_items = [n for n in all_item_names if self.is_new(n)]
        new_items.sort(key=self._is_deprioritized)  # stable: roster order preserved within each group
        return new_items[:limit]

    def select_reviews(self, all_item_names: list[str], today: date, limit: int = 8) -> list[str]:
        """Already-seen items that are due, stalest retention first.

        These are NOT drawn as new items -- they're the pool the tutor pulls
        from for the "and again, what was X?" recall chain that precedes every
        combination, which is where revision actually lives in this method.
        """
        review_items = [n for n in all_item_names if not self.is_new(n)]
        review_items.sort(key=lambda n: (self._is_deprioritized(n), retention(self._states[n], today)))
        return review_items[:limit]

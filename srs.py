"""How often a word comes back, and how the course knows where you are.

Not a forgetting model. The reference course this follows never schedules a
review and never grades an answer -- a word comes back because a later sentence
needs it, and because the teacher keeps circling old ground with the density
tapering as the vocabulary grows. Measured on its transcripts: nothing is ever
"acquired" and retired, the same word simply appears less and less.

So each word carries one number, its level. Fresh out of the box it is level 0
and gets picked constantly; each time it is asked it climbs a level and its
odds fall. They never reach zero, so a word from the very first lesson can
still surface an hour later -- rarely, which is the point.

Deliberately NOT tracked: errors (a wrong answer means the word needs more
exposure, which the level already arranges), dates, and sessions. The course is
one continuous line you stop and resume, so spacing counts in words met, never
in days.
"""
import json
import math
import random
from dataclasses import dataclass, asdict
from pathlib import Path

# How sharply the odds fall as a word is drilled. Chosen for shape, not
# theory: 1/2^level makes a word invisible after about seven recalls, which is
# retirement in disguise, and a flat 1/(level+1) leaves a word from lesson one
# competing evenly with one met a minute ago. This sits between the two --
# steep early, with a thin tail that never quite closes.
DECAY = 1.5

# Where deprioritise puts a word: far down the odds, still not gone.
DEPRIORITIZED_LEVEL = 12


@dataclass
class ItemState:
    name: str
    level: int = 0


def weight(level: int) -> float:
    """A word's share of the recall draw. Level 0 is the reference, weight 1."""
    return 1.0 / (level + 1) ** DECAY


class ProgressStore:
    """Every word met so far, and how consolidated each one is.

    Answers exactly one question -- where are you in the sequence -- which is
    all the persistence this needs. The previous version stored half-lives,
    retrieval counts and error counts, all fed by a model re-reading the
    transcript at the end of a session; it scored "tôi" at zero recalls and
    five errors after the learner had said it correctly several times, and
    promoted a mis-transcription into the vocabulary.
    """

    def __init__(self, path: Path | None):
        """A path of None means a throwaway store: starts empty, saves nothing.

        Used by --fresh while the teaching loop is being worked on, where
        carried-over progress makes every run start somewhere different.
        """
        self.path = path
        self._states: dict[str, ItemState] = {}
        if path is not None and path.exists():
            raw = json.loads(path.read_text(encoding="utf-8"))
            for name, entry in raw.items():
                # Tolerates the old half-life format by keeping only the name.
                level = entry.get("level", 0) if isinstance(entry, dict) else 0
                self._states[name] = ItemState(name=name, level=level)

    def is_new(self, name: str) -> bool:
        return name not in self._states

    def level(self, name: str) -> int:
        state = self._states.get(name)
        return state.level if state else 0

    def mark_introduced(self, name: str) -> None:
        self._states.setdefault(name, ItemState(name=name))

    def record_recall(self, name: str) -> None:
        """One more exposure: the word drops down the odds by one notch.

        Called when a recall the CODE asked for has been answered, so it counts
        what actually happened rather than what a grader thought it saw.
        """
        state = self._states.setdefault(name, ItemState(name=name))
        state.level += 1

    def deprioritize(self, name: str) -> None:
        """The learner asked to stop working on this. Buried, never deleted."""
        self._states.setdefault(name, ItemState(name=name)).level = DEPRIORITIZED_LEVEL

    def select_new(self, all_item_names: list[str], limit: int = 30) -> list[str]:
        """The forward sequence: never-introduced items in ROSTER ORDER.

        Roster order is a composed progression -- words first, then the
        construction that assembles them -- so nothing here reorders it.
        """
        return [n for n in all_item_names if self.is_new(n)][:limit]

    def draw_recalls(self, count: int, exclude: set[str] | None = None) -> list[str]:
        """Words for the bare recall slots, drawn by level without repeats.

        Weighted rather than sorted: a strict "least consolidated first" would
        replay the same handful in the same order every time, which a learner
        notices and starts answering from rhythm instead of memory.
        """
        exclude = exclude or set()
        pool = [s for s in self._states.values() if s.name not in exclude]
        picked: list[str] = []
        while pool and len(picked) < count:
            weights = [weight(s.level) for s in pool]
            chosen = random.choices(pool, weights=weights)[0]
            picked.append(chosen.name)
            pool.remove(chosen)
        return picked

    def save(self) -> None:
        if self.path is None:
            return
        raw = {name: asdict(s) for name, s in self._states.items()}
        self.path.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")

    def summary(self) -> str:
        """One line per level band, for the end-of-session print."""
        if not self._states:
            return "(nothing learned yet)"
        bands: dict[int, list[str]] = {}
        for s in sorted(self._states.values(), key=lambda s: s.level):
            bands.setdefault(s.level, []).append(s.name)
        return "\n".join(
            f"  level {lvl} ({len(names)} word{'s' if len(names) > 1 else ''}, "
            f"1 in {max(1, round(1 / weight(lvl)))}) : {', '.join(names)}"
            for lvl, names in bands.items()
        )

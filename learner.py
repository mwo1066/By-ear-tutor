"""Who the learner is -- the one thing the address system cannot work without.

Separate from srs.py on purpose: that file holds what they KNOW, this one holds
who they ARE. Different lifetimes, different shapes, and state.json is a flat
map of item name to level that nothing should be nested inside.

The point is not personalisation for its own sake. In Vietnamese the word for
"I" is chosen from the pair of people speaking, so a course that does not know
who you are can only ever teach the neutral `tôi` -- which the roster's own note
calls "đúng ngữ pháp nhưng lạnh", grammatically right but cold. Knowing an age
and a gender turns a table to be memorised into two words that are yours.

Necessary, not sufficient: the choice depends on BOTH people, so the other half
arrives at conversation time. But "with someone younger, you are anh" is a
different kind of sentence from "the term depends on relative age and gender".
"""
import json
from dataclasses import dataclass, asdict
from pathlib import Path

# What you call YOURSELF when you are the older one, by gender. The younger
# side is `em` for everyone, which is why only this direction needs to know.
SELF_WHEN_OLDER = {"male": "anh", "female": "chị"}

# The safe pair, used whenever the profile cannot decide. Deliberately the same
# words the course already teaches first, so the fallback is never new material.
NEUTRAL_SELF, NEUTRAL_OTHER = "tôi", "bạn"


def pair_with_minh() -> str:
    """The one address pair the course never has to guess.

    Everything else about the system depends on BOTH people, which is why it
    reads as a table. But inside a lesson the other person is never unknown: it
    is Minh, a man, and the learner's teacher. Facing an older man everyone is
    `em` whatever their own gender, and deference is the safe error in the
    direction sources agree on -- treating someone as slightly older than they
    are is harmless, the reverse is the mistake.

    Needs no profile at all, which makes it the only part of the address system
    that works from the first minute. Written here rather than in the persona
    because it is a fact about the pair, not a way of speaking.
    """
    return "with Minh, right here: you are em and he is anh"


@dataclass
class Learner:
    name: str = ""
    gender: str = ""      # "male" | "female" | "" when not known
    age: int | None = None

    @property
    def complete(self) -> bool:
        """Enough to personalise the address rule. The name is not part of it --
        it makes sentences real but decides no pronoun."""
        return bool(self.gender) and self.age is not None

    def address_rows(self) -> list[str]:
        """The address table written for THIS learner, or [] if it cannot be.

        Returns the same shape as the generic `steps` on the address rule, so
        callers substitute one for the other and nothing else changes.
        """
        if not self.complete:
            return []
        mine = SELF_WHEN_OLDER.get(self.gender)
        if not mine:
            return []
        return [
            f"a man older than you → he is anh, you are em",
            f"a woman older than you → she is chị, you are em",
            f"someone younger than you → they are em, you are {mine}",
            f"someone you cannot place, or a formal moment → {NEUTRAL_OTHER} and {NEUTRAL_SELF}",
        ]

    def summary(self) -> str:
        """One line for a lesson instruction. Empty when there is nothing to say."""
        bits = []
        if self.name:
            bits.append(f"their name is {self.name}")
        if self.gender:
            bits.append(f"they are {self.gender}")
        if self.age is not None:
            bits.append(f"they are {self.age}")
        return ", ".join(bits)


def load(path: Path) -> Learner:
    """A missing or unreadable file is an empty profile, never an error: this is
    an enhancement to the lesson, and a lesson must start without it."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return Learner()
    age = raw.get("age")
    return Learner(
        name=str(raw.get("name", "") or ""),
        gender=str(raw.get("gender", "") or ""),
        age=int(age) if isinstance(age, (int, float, str)) and str(age).isdigit() else None,
    )


def save(path: Path, learner: Learner) -> None:
    path.write_text(json.dumps(asdict(learner), ensure_ascii=False, indent=2), encoding="utf-8")

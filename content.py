"""Loads the roster (ordered items) and persona from the TOML content files."""
import json
import re
import tomllib
import unicodedata
from dataclasses import dataclass, asdict, field
from pathlib import Path

PERSONAL_ITEMS_FILENAME = "personal_items.json"

# How an item is TAUGHT -- the only axis the turn planner branches on.
#   atom          a single thing the learner says, taught by introducing it
#                 ("tôi", and also multi-word units like "cà phê" that are one
#                 lexical block, not an assembly)
#   construction  a sentence pattern assembled out of items already taught
#   feature       a fact about the language the tutor STATES; the learner never
#                 says it back, so it is never a recall target ("tính từ không
#                 cần 'là'"). Typological sense -- covers grammar, tone and
#                 politeness alike. See GLOSSARY.md.
KINDS = {"atom", "construction", "feature"}


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
    # One true sentence of context, in English, spoken before the word is
    # revealed. Optional and usually empty -- it exists for the words where the
    # plain template is absurd: "the Vietnamese word for pho is phở" tells a
    # learner who already knows pho precisely nothing, and "cà phê" or "Hà Nội"
    # are the same. A fact ("Hà Nội means 'inside the river'") is what makes
    # those land.
    #
    # Data, not improvisation. The old introduce instruction asked the model for
    # this at lesson time -- "one sentence of real context, only if you have a
    # true fact worth telling" -- and across every session logged it produced
    # one exactly zero times. Written offline it can be checked before anyone
    # hears it, which matters: an invented etymology is worse than none.
    hook: str = ""
    # A rule may carry the situations it covers, one per line, as data rather
    # than buried in its Vietnamese notes. The address feature has had four of
    # them since it was written -- man older than you, woman older than you,
    # someone younger, unsure -- and nothing read them: the field was not loaded
    # at all. A table nobody can reach is a table that gets re-invented.
    steps: list[str] = field(default_factory=list)
    # A feature may name the item it belongs WITH, and it is then emitted the
    # turn after that item instead of waiting its turn in the feature queue.
    #
    # Without it a feature cannot be placed at all, only ranked. Features come
    # out one every five items in file order, so a feature's position is decided
    # by how many features precede it and by nothing else: "đã" is the 22nd item
    # and its feature the 15th, which lands it at 82. Measured across the
    # course, the median feature arrives 47 items after the last of its own
    # words, and 21 of 30
    # wait more than 30. So a learner meets a word, drills it as vocabulary, and
    # is told an hour later where it goes.
    after: str = ""
    # Features only. "discrete" is a fact taught once that should come back;
    # "strand" is one that never finishes -- tone attaches to every word, the
    # address system to every sentence with a person in it -- so it fires from
    # the material and must never be drawn as a recall target. Empty on atoms
    # and constructions. See GLOSSARY.md.
    nature: str = ""
    tier: int = 0
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
                hook=raw.get("hook", ""),
                steps=list(raw.get("steps", [])),
                after=raw.get("after", ""),
                nature=raw.get("nature", ""),
                tier=int(raw.get("tier", 0)),
            ))
    return items


# A gloss is spoken inside "the word for ___", so it has to be short enough to
# sit in a question. Measured on the roster: everything above this was a
# definition that had been written into the wrong field.
MAX_GLOSS_WORDS = 6
# Openings that describe the word rather than translate it. Each one leaves the
# recall question ungrammatical, because the frame already supplies the noun.
METALINGUISTIC_FRAMES = {
    "address for", "term for", "name for", "title for",
    "way of", "way to", "used when", "used for", "used to",
}


def check_roster(items: list[Item]) -> list[str]:
    """Authoring defects that would silently degrade a lesson, as messages.

    Reported at startup rather than discovered live: a missing gloss does not
    crash anything, it just makes the tutor improvise the meaning side of a
    question, which is how a recall ends up giving away its own answer.
    """
    known = {i.name for i in items}
    problems = []
    # Two WORDS carrying the same gloss cannot both be asked for. The question
    # is built from the gloss -- "what was the word for to use?" -- so a
    # collision leaves the learner guessing which of two right answers was
    # wanted, and answered_target accepts either, so nobody ever finds out.
    #
    # Found on the second batch of shelf glosses: dùng and sử dụng both came
    # back "to use", and quá was given "very" which rất already had -- undoing a
    # distinction the course teaches on purpose ("rất trước, lắm sau"). On 1640
    # words still to gloss, collisions are certain rather than unlucky.
    #
    # Atoms only. cảm ơn and "Cảm ơn bạn" share "thank you" legitimately: one is
    # a word, the other a phrase built on it, and they are never asked the same
    # way.
    by_gloss: dict[str, list[str]] = {}
    for i in items:
        if i.kind == "atom" and i.gloss:
            by_gloss.setdefault(i.gloss.strip().lower(), []).append(i.name)
    for gloss, names in by_gloss.items():
        if len(names) > 1:
            problems.append(f"{', '.join(names)}: all glossed {gloss!r} — one question, "
                            f"several right answers, and no way to say which was wanted")
    # Two items with the same name is silent damage: the loader reads files in
    # filename order, so the LAST one wins -- a hand-written word with a gloss
    # was being shadowed by its own entry in the frequency stock, which has
    # none, and the word simply stopped being teachable.
    seen_names: set[str] = set()
    for i in items:
        if i.name in seen_names:
            problems.append(f"{i.name}: defined twice — the later file silently wins")
        seen_names.add(i.name)
    for i in items:
        if i.kind not in KINDS:
            problems.append(f"{i.name}: unknown kind {i.kind!r}")
        if not i.gloss and i.kind != "feature":
            problems.append(f"{i.name}: no gloss — questions about it cannot be asked from the meaning side")
        # Features used to be exempt here, and that was true when it was
        # written: a feature's turn was composed by the model, which could work
        # from the Vietnamese notes. Since the code began building questions
        # from the gloss and nothing else, it stopped being true -- and
        # _ask_for's own docstring already promises the half that went missing,
        # "a missing gloss falls back to the item's own notes instead AND IS
        # REPORTED AT STARTUP". This is that report. Worded apart from the line
        # above on purpose: a feature with no gloss is NOT held out of lessons,
        # it is taught with a degraded question, which is a different problem
        # and deserves to be named one by one rather than counted.
        if not i.gloss and i.kind == "feature":
            problems.append(f"{i.name}: gloss is empty — it is still taught, but its question falls "
                            f"back to the Vietnamese notes in `description`, which the model then has "
                            f"to speak English from")
        # An `after` pointing at nothing starves in silence. pick_next_index only
        # promotes an item once its `after` is in the taught set, so a name that
        # no item carries is never satisfied and the item waits for the whole
        # course without a word of complaint. Nothing checked this until a
        # feature was made to follow another FEATURE rather than a word, which
        # is what turned a typo into a lesson that never happens.
        if i.after and i.after not in seen_names:
            problems.append(f"{i.name}: after = {i.after!r} names no item — it would wait forever")
        # The code now speaks recall questions itself, built from the gloss and
        # from nothing else, so the gloss IS the guarantee that a question does
        # not state its own answer. A Vietnamese name that leaked into its own
        # English gloss would quietly undo that.
        if i.kind != "feature" and i.gloss and i.name.lower() in i.gloss.lower():
            problems.append(f"{i.name}: its own name appears in its gloss {i.gloss!r} — the recall would give the answer away")
        # A gloss is not a definition. It is what fills the blank in "the word
        # for ___", which a scripted recall says ALOUD, so a gloss describing
        # the word instead of translating it comes out as "the word for the
        # counting word for things" or, worse, "what was right now, in the
        # middle of?". Heard in a simulated session on 13 August; 16 of 151
        # glosses failed, eight of them written that same day by someone
        # trying to be helpful. A prompt cannot hold this over 1900 items.
        if i.kind == "atom" and i.gloss:
            if "word" in i.gloss.lower():
                problems.append(f"{i.name}: gloss {i.gloss!r} describes the word instead of translating it — "
                                f'it would be read as "the word for {i.gloss}"')
            # Length is not the disease, it is a symptom. A gloss is dropped
            # into "what was ___?", so one naming a CATEGORY of word instead of
            # a meaning comes out without its article: "what was address for an
            # older male?". Five glosses did this on 23 August, all four or five
            # words long, so MAX_GLOSS_WORDS never saw them and the smoke test
            # printed them for a week without anyone reading the sentence. The
            # cure is the same as the "word" check above -- say what it MEANS,
            # not what kind of word it is.
            first_two = " ".join(i.gloss.lower().split()[:2])
            if first_two in METALINGUISTIC_FRAMES:
                problems.append(f"{i.name}: gloss {i.gloss!r} names a kind of word instead of a meaning — "
                                f'it would be read as "what was {i.gloss}?", with no article')
            if len(i.gloss.split()) > MAX_GLOSS_WORDS:
                problems.append(f"{i.name}: gloss {i.gloss!r} is {len(i.gloss.split())} words — "
                                f"too long to sit inside a spoken question")
        # A rule refusing a gloss that IS an English question word stood here
        # until 23 August. It was written for the sentence "And what -- what was
        # the word?", which came from the inverted template -- and tutor.py:1412
        # records that template being deleted, for that same reason and with
        # that same example. The check outlived the sentence it guarded.
        #
        # A one-word gloss now always routes to _REPEAT_ASK_SHORT and comes out
        # as "what was the word for when?", which reads. The forms that would
        # break are the multi-word ones and a bare question word cannot reach
        # them. 56 taught items already carry a one-word gloss and 51 of them
        # were never flagged -- "name", "hello", "and", "water" take exactly the
        # same path. The five it did refuse were taught anyway, so it prevented
        # nothing and printed at every startup, which teaches you to read past
        # the warnings that matter.
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


def load_course(content_dir: Path) -> list[Item]:
    """Everything teachable, curated first, with no name taught twice.

    `add_personal_items` refuses a name the roster already has, but only at the
    moment it is written -- it cannot defend against the roster GROWING later
    onto a name a live session already claimed. That happened to "đi" and "xin
    lỗi": generated in an earlier session, then hand-written into the roster.

    A duplicate is not a cosmetic defect. `unknown_pieces` matches pieces by
    name, so the personal copy satisfies a rule's prerequisite while the roster
    copy is still queued -- and the rule gets taught before the word it is made
    of, which is the ONE guarantee the sequencing exists to make. Measured on
    the roster: the composition rule landed at 152 with its own piece "đi" not
    due until 182.

    Curated wins: it carries the hand-written description and gloss, where the
    personal copy is whatever the model produced mid-lesson.

    Every caller that needs the whole course must use this rather than
    concatenating the two loaders, which is what let the collision through in
    seven separate places.

    Case-insensitively, because a live session writes whatever the model
    capitalised: "Ở" and "Người" were both sitting in the personal store beside
    the roster's "ở" and "người", and an exact-name comparison let both
    through. The learner would have met the same word twice, with two glosses
    written by two different authors.
    """
    roster = load_roster(content_dir)
    claimed = {i.name.casefold() for i in roster}
    return roster + [i for i in load_personal_items(content_dir)
                     if i.name.casefold() not in claimed]


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


_PIECE_PLACEHOLDER = re.compile(r"\[[^\]]*\]|_{2,}|\.\.\.|[+/?,!]")


def derive_pieces(name: str, known: list[Item]) -> list[str]:
    """Which already-known items a sentence is built from, read off its name.

    The INVERSE of the splitting that burned this project before. That version
    cut the name into words and assumed each was an item -- so "cà phê" became
    two pieces, and the rule "tính từ không cần 'là'" looked like a sentence
    built from "không" and "là". This one never invents a piece: it scans the
    known items and keeps those that actually occur, longest first, so a
    multi-syllable item always wins over its own syllables.

    Exists because the model cannot be trusted with this field, measured on the
    roster: 8 of its 13 generated constructions declared pieces that were
    unusable -- one for eight words, or none at all. `pieces` is what makes a
    sentence teachable (one recall per piece, and never before its words are
    taught), so a wrong one is not a cosmetic defect.

    A name may carry a Vietnamese label before a colon -- "câu hỏi có/không:
    có + [động từ] ... không?" -- and that label is ABOUT the sentence, not part
    of it. Only the template counts. This stayed invisible while the roster was
    small and broke the moment a label word ("hỏi", to ask) became a real item:
    the construction acquired a piece it does not contain. Everything left of
    the colon goes.
    """
    if ": " in name:
        name = name.split(": ", 1)[1]
    haystack = f" {_PIECE_PLACEHOLDER.sub(' ', name).lower()} "
    haystack = " " + " ".join(haystack.split()) + " "
    found: list[tuple[int, str]] = []
    taken: list[tuple[int, int]] = []  # spans already claimed by a longer item
    for item in sorted(known, key=lambda i: -len(i.name)):
        # Only teachable items may become pieces. A piece is a prerequisite --
        # rule 9 holds the sentence back until every one of them is taught -- so
        # a word that CANNOT be taught is a prerequisite that can never be met.
        # Found the moment a frequency stock landed: "phải" arrived at rank 19
        # with no gloss yet, derive_pieces correctly spotted it inside "không
        # phải là", and that alone would have blocked the construction forever.
        if item.kind == "feature" or not is_teachable(item) or item.name.lower() == name.lower():
            continue
        needle = f" {item.name.lower()} "
        at = haystack.find(needle)
        # Whole tokens only: the surrounding spaces are part of the needle, so
        # "anh" cannot match inside "khách sạn" or any other longer syllable.
        if at == -1 or any(a <= at < b for a, b in taken):
            continue
        taken.append((at, at + len(needle) - 1))
        found.append((at, item.name))
    return [n for _, n in sorted(found)]


# The words that fill a person slot. A list, and a closed one: a beginner course
# needs these five, and the rest of the system (cô, chú, bác, ông, bà) belongs to
# a level this course does not reach. If it starts growing, it has become a
# category and should be declared on the items instead.
ADDRESS_TERMS = {"tôi", "bạn", "anh", "chị", "em"}


def address_situations(items: list[Item]) -> list[str]:
    """The rows of the address table, read off whichever rule declares them.

    Found by content rather than by name: a rule that carries `steps` mentioning
    an address term IS the address rule. Hard-coding the item name would break
    the moment the content is reorganised, which it was twice today.
    """
    for i in items:
        if i.kind == "feature" and i.steps and any(t in " ".join(i.steps) for t in ADDRESS_TERMS):
            return i.steps
    return []


# The five tone marks, as combining characters. NOT the vowel modifiers (horn,
# breve, circumflex): ơ and o are different vowels, à and a are the same vowel
# said at a different pitch, and only the second pair is a tone twin.
_TONE_MARKS = {"́", "̀", "̉", "̃", "̣"}


def toneless(name: str) -> str:
    """The word with its pitch removed -- what a foreign ear actually hears."""
    return "".join(c for c in unicodedata.normalize("NFD", name.lower())
                   if c not in _TONE_MARKS)


def tone_twin(item: Item, already_seen: list[Item]) -> Item | None:
    """An already-taught word that differs from this one ONLY in tone.

    The pair is the whole lesson. "thanh sắc, the voice rises" teaches nothing to
    someone with nothing to compare it against; `ba` then `bà` in one breath is
    the only second in which the difference exists for a foreign ear.

    Deliberately at the SECOND word of a pair, never the first: two lookalikes
    taught side by side blur into each other, and the older one has had time to
    settle. Measured on the roster -- 3 pairs among the words taught (ba/bà,
    bạn/bán, con/còn), 246 groups across the whole vocabulary, so this is nearly
    idle today and central once the stock wakes up.
    """
    if item.kind != "atom" or len(item.name.split()) != 1:
        return None
    skeleton = toneless(item.name)
    for other in reversed(already_seen):
        if (other.kind == "atom" and other is not item
                and other.name.lower() != item.name.lower()
                and toneless(other.name) == skeleton):
            return other
    return None


def has_person_slot(item: Item) -> bool:
    """Whether this sentence contains a word that changes with who you address."""
    return bool(set(item.pieces) & ADDRESS_TERMS)


def is_teachable(item: Item) -> bool:
    """Whether a lesson can actually be built from this item.

    An atom or construction with no gloss cannot: every question the tutor asks
    is formed FROM the gloss, so without one the recall has nothing to ask for
    and _ask_for falls back to reading the item's notes aloud. check_roster has
    always reported this at startup; it was only ever a warning because nothing
    could arrive in that state.

    Bulk imports change that. A frequency list carries words, not meanings, so
    an import lands thousands of items that are real vocabulary and not yet
    teachable material. Skipping them here is what makes a staged import safe:
    drop 2000 raw words in, and they simply wait their turn to be annotated
    instead of surfacing as a broken turn.
    """
    return item.kind == "feature" or bool(item.gloss)


# A gloss that is a grammar formula rather than English, and a name that is an
# authoring label rather than speech. Both make an item impossible to ask for.
# Only true formula notation: a "+" joining parts, or a [placeholder] naming a
# word class. NOT "___" or "...", which are ordinary English blanks -- "My name
# is ___" reads aloud perfectly well, and excluding it would stop every sentence
# in the course from ever coming back for review.
_FORMULA = re.compile(r"[\[\]+]")


def askable(item: Item) -> bool:
    """Whether a recall can be built around this item.

    Every recall question IS the gloss read aloud, and the retry line is the
    name read aloud, so both have to be sayable English and Vietnamese. Found
    live: a rapidfire drew the item glossed "do ... not?" and asked "and again
    -- what was do not?", which answers nothing; had the learner missed it, the
    retry would have offered the authoring label "câu hỏi có/không: có + [động
    từ] ... không?" for them to repeat.

    Teachable and askable are different: such an item can still be TAUGHT --
    it has a scaffold, a literal, a rule to state -- it just cannot be the
    bare question of a recall slot.
    """
    if not is_teachable(item) or item.kind == "feature":
        return False
    # The name only has to survive _target_fragments, which strips placeholders
    # -- so "tôi tên là + [tên riêng]" is fine, it is said as "tôi tên là". An
    # authoring label is not: "câu hỏi có/không: ..." means "yes/no question:",
    # which is a note to the author and not something anyone says.
    return not _FORMULA.search(item.gloss) and ":" not in item.name


def drawable(item: Item) -> bool:
    """Whether this item can be DRAWN into a recall slot at all.

    Three words, three different questions, and conflating them is what kept a
    fifth of the course from ever coming back:

      is_teachable  can a lesson be built from it?
      askable       can it be the bare question of a recall slot?
      drawable      can it fill a recall slot, in whatever form?

    A discrete feature is drawable but not askable. Nobody recites "no plural",
    so it cannot be a bare question -- but it can be APPLIED, and the code
    already knows how to build that turn. Excluding it from the draw because it
    failed `askable` was the right test asked of the wrong question: measured
    over a whole course, 33 features out of 33 were never seen again, final
    level 0 against 4.5 for words.

    A strand is never drawable. Tone and the address system fire from the
    material itself -- a word has a tone twin, a sentence has a person in it --
    so drawing them would ask for a second, worse copy of something already
    running.
    """
    if item.kind == "feature":
        return item.nature == "discrete" and bool(item.gloss)
    return askable(item)


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


# How far the prerequisite chase will walk. A missing word can itself be a
# phrase with missing words; three levels covers anything this course builds
# and stops a cycle in hand-written pieces from looping forever.
MAX_PREREQUISITE_DEPTH = 3

# Grammar is spread, never stacked. Rules cluster naturally because they sit
# together in a file, and file order is teaching order -- measured on the whole
# course, that produced NINE in a row around item 35, nine minutes of theory
# without a new word. Spacing them by hand does not survive 2000 words, so it
# is enforced here instead: after a rule, this many items must be said before
# another one may come. The rule simply waits; nothing is dropped.
MIN_ITEMS_BETWEEN_FEATURES = 4

# The same defect, one level up: a file holds one topic, file order is teaching
# order, so a whole file comes out as a block. Measured after writing the number
# system -- ELEVEN numerals in eleven consecutive slots, a quarter of an hour of
# counting and nothing else. Rules had a spacer and no other category did.
# Three in a row is enough to feel like a theme; a fourth makes it a drill.
MAX_SAME_CATEGORY_RUN = 3


def _feature_is_due(seen_items: list[Item]) -> bool:
    recent = seen_items[-MIN_ITEMS_BETWEEN_FEATURES:]
    return not any(i.kind == "feature" for i in recent)


def _saturated_category(seen_items: list[Item]) -> str | None:
    """The category that has just run long enough to need a break, if any.

    Deliberately about the LAST few items only, not a quota over the course: a
    learner does not mind meeting twenty numbers, they mind meeting them one
    after another.
    """
    recent = seen_items[-MAX_SAME_CATEGORY_RUN:]
    if len(recent) < MAX_SAME_CATEGORY_RUN:
        return None
    categories = {i.category for i in recent}
    return recent[-1].category if len(categories) == 1 else None


def pick_next_index(queue: list[Item], seen_items: list[Item]) -> int:
    """Index of the next item that may safely be taught.

    Queue order is want-order: whatever sits at the head is what the learner
    should get next -- normally the composed progression, but a theme they
    asked for is pushed in front of it.

    The one thing that overrides want-order is the guarantee the prompt cannot
    make on its own: a multi-word phrase never surfaces before the words it is
    made of.

    When the wanted item IS blocked, its missing words are FETCHED rather than
    the item passed over. Found live: the learner asked for food ordering, got
    "đặt" and "gọi", and then the lesson returned to the curated spine -- the
    two sentences they actually wanted, "Tôi muốn đặt ...", needed "muốn", so
    they were skipped and never came back. Teaching the missing word first
    turns the same request into a real short lesson: muốn -> đặt -> the
    sentence. Everything needed was already known; unknown_pieces computes it,
    and it was being used to discard instead of to fetch.

    Deliberately NOT "all single words first": that drains every atom in the
    course before the first construction, whereas the method introduces two or
    three words and immediately combines them.

    If nothing is fully teachable (a phrase whose words the course never teaches
    separately), the least-blocked item wins rather than deadlocking.
    """
    # A rule that named its word comes FIRST, ahead of every spacing rule. That
    # is the whole point of the field: the spacer exists to stop rules
    # clustering, and a rule attached to a word is not clustering, it is
    # finishing the word. Bypassing the spacer is the intent, not a side effect.
    taught = {i.name for i in seen_items}
    attached = [i for i, item in enumerate(queue)
                if item.after and item.after in taught and not unknown_pieces(item, seen_items)]
    if attached:
        return attached[0]

    # Spacing first, because the prerequisite walk below returns the head of the
    # queue as soon as it is ready -- which is exactly where a run of rules, or
    # of numbers, sits, so a spacing check placed after it never ran.
    features_due = _feature_is_due(seen_items)
    saturated = _saturated_category(seen_items)
    if not features_due or saturated:
        spaced = [i for i, item in enumerate(queue)
                  if (features_due or item.kind != "feature")
                  and item.category != saturated
                  and not unknown_pieces(item, seen_items)]
        # Nothing else is ready, so the run continues rather than deadlocking:
        # spacing is a preference and teaching is not.
        if spaced:
            return spaced[0]

    wanted = 0
    for _ in range(MAX_PREREQUISITE_DEPTH):
        missing = unknown_pieces(queue[wanted], seen_items)
        if not missing:
            return wanted
        nxt = next((i for i, item in enumerate(queue) if item.name in missing), None)
        if nxt is None or nxt == wanted:
            break  # the course does not teach that word separately
        wanted = nxt

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

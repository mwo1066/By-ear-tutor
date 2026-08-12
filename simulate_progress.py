"""Fast-forwards a learner, so a lesson can be tested from the middle.

Everything in this project has only ever been seen from a cold start: three
words in, --fresh, the same opening every time. The turns that matter later --
a construction whose pieces are all well drilled, a recall pool wide enough to
draw from, a rule landing on vocabulary that is actually known -- have never
run at all.

This replays the REAL sequencing to get there: pick_next_index chooses,
build_plan builds, record_recall scores. Nothing is invented, so the state it
writes is one the tutor could genuinely have arrived at. A hand-written
state.json would only prove the tutor survives a file someone made up.

The learner it plays is deliberately good but not perfect -- ACCURACY below --
because a flawless one never triggers the retry path and an awful one never
gets past the first word.

    python simulate_progress.py 60            # what an hour would leave behind
    python simulate_progress.py 60 --write    # write it to state.json

Then run the tutor WITHOUT --fresh to land in the middle of the course.

Run: python simulate_progress.py [minutes] [--write]
"""
import random
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

from content import is_teachable, load_personal_items, load_roster, pick_next_index, pieces_of
from srs import ProgressStore
from tutor import CONTENT_DIR, STATE_PATH, _recall_targets, build_plan

# Measured across the real sessions logged: a scripted turn runs 3-11s of speech
# plus 3-5s of listening, a model turn 10-28s plus the same. Most turns are
# scripted now, so the average sits near a quarter of a minute.
SECONDS_PER_TURN = 15

# How often the learner is understood. Not 1.0: at a perfect score the retry
# path never runs and the state comes out unrealistically consolidated. The real
# sessions land far lower than this, but those are transcription failures rather
# than the learner not knowing the word.
ACCURACY = 0.8


def run_until(match, seed: int = 7):
    """Advances until the NEXT item due satisfies `match`, then stops.

    `match` takes an Item, so a caller can stop on a kind, on a name, or on
    anything else the sequencing produces. The sequencing is the real one, so
    what gets written is a place the tutor could actually be standing.
    """
    random.seed(seed)
    roster = load_roster(CONTENT_DIR) + load_personal_items(CONTENT_DIR)
    store = ProgressStore(None)
    queue = [i for i in roster if is_teachable(i)]
    seen: list = []
    taught: list[str] = []
    while queue:
        nxt = queue[pick_next_index(queue, seen)]
        if match(nxt) and taught:
            return store, taught, nxt
        item = queue.pop(pick_next_index(queue, seen))
        seen.append(item)
        store.mark_introduced(item.name)
        taught.append(item.name)
        pieces = pieces_of(item, seen)
        for step in build_plan(item, pieces,
                               _recall_targets(store, item, pieces, seen), seen):
            if step.kind in ("recall_piece", "rapidfire", "settle") and step.target:
                store.record_recall(step.target)
    return store, taught, None


def run_until_kind(kind: str, seed: int = 7):
    """Advances until the NEXT item due is of this kind, then stops.

    For testing a step that a live session only reaches after an hour: a rule,
    or a construction. The sequencing is the real one, so what is written is a
    place the tutor could actually be standing.
    """
    random.seed(seed)
    roster = load_roster(CONTENT_DIR) + load_personal_items(CONTENT_DIR)
    store = ProgressStore(None)
    queue = [i for i in roster if is_teachable(i)]
    seen: list = []
    taught: list[str] = []

    while queue:
        nxt = queue[pick_next_index(queue, seen)]
        if nxt.kind == kind and taught:
            return store, taught, nxt
        item = queue.pop(pick_next_index(queue, seen))
        seen.append(item)
        store.mark_introduced(item.name)
        taught.append(item.name)
        pieces = pieces_of(item, seen)
        for step in build_plan(item, pieces,
                               _recall_targets(store, item, pieces, seen), seen):
            if step.kind in ("recall_piece", "rapidfire", "settle") and step.target:
                store.record_recall(step.target)
    return store, taught, None


def run(turns: int, seed: int = 7) -> ProgressStore:
    random.seed(seed)
    roster = load_roster(CONTENT_DIR) + load_personal_items(CONTENT_DIR)
    store = ProgressStore(None)  # in memory; written only if asked
    queue = [i for i in roster if is_teachable(i)]
    seen: list = []
    taught: list[str] = []

    spent = 0
    while spent < turns and queue:
        item = queue.pop(pick_next_index(queue, seen))
        seen.append(item)
        store.mark_introduced(item.name)
        taught.append(item.name)
        plan = build_plan(item, pieces_of(item, seen),
                          _recall_targets(store, item, pieces_of(item, seen), seen), seen)
        for step in plan:
            spent += 1
            if spent >= turns:
                break
            # Only recall steps score, exactly as the live loop does.
            if step.kind in ("recall_piece", "rapidfire", "settle") and step.target:
                if random.random() < ACCURACY:
                    store.record_recall(step.target)
                else:
                    spent += 1          # the retry costs a turn
                    store.record_recall(step.target)
    return store, taught, len(queue)


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    write = "--write" in sys.argv

    def report(store, taught, nxt) -> int:
        kind = nxt.kind if nxt else "?"
        print(f"{len(taught)} item(s) taught, and the next one due is a {kind}:\n")
        print(f"    {nxt.name}")
        print(f"    « {nxt.gloss} »\n")
        print("last five taught:", ", ".join(taught[-5:]))
        if not write:
            print(f"\nNothing written. Re-run with --write to save to {STATE_PATH.name}.")
            return 0
        store.path = STATE_PATH
        store.save()
        print(f"\nWrote {STATE_PATH}")
        print("Now run:  python tutor.py --no-intro     (WITHOUT --fresh)")
        return 0

    wanted = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--until=")), None)
    if wanted:
        return report(*run_until(lambda i: wanted.lower() in i.name.lower()))

    for kind in ("rule", "construction"):
        if f"--next-{kind}" in sys.argv:
            store, taught, nxt = run_until_kind(kind)
            print(f"{len(taught)} item(s) taught, and the next one due is a {kind}:\n")
            print(f"    {nxt.name}")
            print(f"    « {nxt.gloss} »\n")
            print("last five taught:", ", ".join(taught[-5:]))
            if not write:
                print(f"\nNothing written. Re-run with --write to save to {STATE_PATH.name}.")
                return 0
            store.path = STATE_PATH
            store.save()
            print(f"\nWrote {STATE_PATH}")
            print("Now run:  python tutor.py --no-intro     (WITHOUT --fresh)")
            return 0

    minutes = int(args[0]) if args else 60
    turns = minutes * 60 // SECONDS_PER_TURN
    store, taught, left = run(turns)
    levels = Counter(store.level(n) for n in taught)

    print(f"{minutes} minutes ≈ {turns} turns\n")
    print(f"{len(taught)} item(s) introduced, {left} still ahead\n")
    print("what was covered, in order:")
    for n, name in enumerate(taught, 1):
        print(f"  {n:3}. {name}  (level {store.level(name)})")
    print("\nhow consolidated:")
    for level in sorted(levels):
        share = "1 in " + str(max(1, round(1 / (1 / (level + 1) ** 1.5))))
        print(f"  level {level}: {levels[level]:3} word(s)   drawn {share}")

    if not write:
        print(f"\nNothing written. Re-run with --write to save to {STATE_PATH.name}.")
        return 0
    store.path = STATE_PATH
    store.save()
    print(f"\nWrote {STATE_PATH}")
    print("Now run:  python tutor.py --no-intro     (WITHOUT --fresh)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

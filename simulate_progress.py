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

    python simulate_progress.py --random --write   # land somewhere new, every time
    python simulate_progress.py 60 --write         # a specific hour of course

Then run the tutor WITHOUT --fresh to land in the middle of the course.

Run: python simulate_progress.py [minutes] [--write]
"""
import random
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

from content import load_course, is_teachable, load_personal_items, load_roster, pick_next_index, pieces_of
from srs import ProgressStore
from tutor import CONTENT_DIR, STATE_PATH, RECALL_KINDS, _recall_targets, build_plan

# Measured across the real sessions logged: a scripted turn runs 3-11s of speech
# plus 3-5s of listening, a model turn 10-28s plus the same. Most turns are
# scripted now, so the average sits near a quarter of a minute.
SECONDS_PER_TURN = 15

# How often the learner is understood. Not 1.0: at a perfect score the retry
# path never runs and the state comes out unrealistically consolidated. The real
# sessions land far lower than this, but those are transcription failures rather
# than the learner not knowing the word.
ACCURACY = 0.8


def run_until_count(stop_after: int, seed: int = 7):
    """Stops with exactly `stop_after` items taught, so item stop_after+1 is next.

    Exists so a specific turn can be reached by NUMBER. --until= matches on the
    item name, and every rule in this course is named in Vietnamese: reaching
    the address rule meant typing "cách chọn từ xưng hô" into PowerShell, which
    is fragile enough that the flag went unused. A position is typeable.
    """
    n = {"taught": 0}

    def enough(_item) -> bool:
        return n["taught"] >= stop_after

    return run_until(enough, seed, on_taught=lambda: n.__setitem__("taught", n["taught"] + 1))


def run_until(match, seed: int = 7, on_taught=None):
    """Advances until the NEXT item due satisfies `match`, then stops.

    `match` takes an Item, so a caller can stop on a kind, on a name, or on
    anything else the sequencing produces. The sequencing is the real one, so
    what gets written is a place the tutor could actually be standing.
    """
    random.seed(seed)
    roster = load_course(CONTENT_DIR)
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
        if on_taught:
            on_taught()
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
    roster = load_course(CONTENT_DIR)
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
    roster = load_course(CONTENT_DIR)
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
            # Scores exactly as the live loop does -- and the kinds come FROM
            # the live loop rather than being listed again here. They were
            # listed again here, and the copy went stale the day applications
            # started counting: this simulation is what measured "33 features
            # out of 33 never seen again", so a stale copy would have gone on
            # reporting that after the fix landed.
            if step.kind in RECALL_KINDS and step.target:
                if random.random() < ACCURACY:
                    store.record_recall(step.target)
                else:
                    spent += 1          # the retry costs a turn
                    store.record_recall(step.target)
            elif step.kind == "apply" and step.target:
                # Exposure, never a score: an application asks for a whole
                # sentence, so there is nothing to mark. Same rule as the live
                # loop, same reason.
                store.record_recall(step.target)
    return store, taught, len(queue)


def _finish(store, taught, left, minutes: int, write: bool) -> int:
    """Reports what an hour left behind, and writes it if asked."""
    levels = Counter(store.level(n) for n in taught)
    print(f"{len(taught)} item(s) introduced in {minutes} minutes, {left} still ahead\n")
    print("the last dozen taught:")
    for n, name in enumerate(taught[-12:], len(taught) - 11):
        print(f"  {n:3}. {name}  (level {store.level(name)})")
    print("\nhow consolidated:")
    for level in sorted(levels):
        share = "1 in " + str(max(1, round((level + 1) ** 1.5)))
        print(f"  level {level}: {levels[level]:3} item(s)   drawn {share}")
    if not write:
        print(f"\nNothing written. Re-run with --write to save to {STATE_PATH.name}.")
        return 0
    store.path = STATE_PATH
    store.save()
    print(f"\nWrote {STATE_PATH}")
    print("Now run:  python tutor.py --no-intro     (WITHOUT --fresh)")
    return 0


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    write = "--write" in sys.argv
    # --random exists because the seed was fixed at 7, so the same duration
    # always produced the SAME state: running it twice tested the same twenty
    # minutes of course twice. Testing widely means landing in different places,
    # and the place matters more than the length -- item 40 and item 140 exercise
    # different machinery.
    if "--random" in sys.argv:
        seed = random.randrange(10_000)
        minutes = random.choice((15, 25, 40, 55, 70, 90, 110))
        print(f"[--random] seed {seed}, {minutes} minutes of course\n")
        store, taught, left = run(minutes * 60 // SECONDS_PER_TURN, seed=seed)
        return _finish(store, taught, left, minutes, write)

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

    at = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--at=")), None)
    if at and at.isdigit():
        return report(*run_until_count(int(at)))

    wanted = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--until=")), None)
    if wanted:
        return report(*run_until(lambda i: wanted.lower() in i.name.lower()))

    for kind in ("feature", "construction"):
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
    store, taught, left = run(minutes * 60 // SECONDS_PER_TURN)
    return _finish(store, taught, left, minutes, write)


if __name__ == "__main__":
    sys.exit(main())

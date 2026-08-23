"""Runs the recall draw past the size of the real course.

The course holds about 270 teachable items, all introduced inside seven hours,
so the 2000-word regime it is aiming at cannot be simulated from the content --
there is no late course to replay. `0020` shipped with that gap named as a
projection.

The draw does not need the content. It needs a store, levels, and how many
recall slots an item spends. Both numbers are measured on the real sequencing
rather than chosen, so what runs here is our own mechanism over synthetic names:

    5.7  turns per item     481 turns, 84 items, over a 120-minute replay
    4.46 recalls per item   375 recalls over the same replay

What it answers: does a word introduced late keep getting drilled, or does the
rate fall away without a floor?

    python model_draw.py            compare today against the shipped setting
    python model_draw.py 20 0.5     try a different window and share

The absolute numbers are lower than the content replay gives (3.0 against 4.1),
because only the draw is modelled -- an item also recalls its own pieces, and
those are not here. The shape is the point, and the shape is the mechanism's.
"""
import random
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

import srs

RECALLS_PER_ITEM = 4.46
WINDOW_ITEMS = 84       # 120 minutes at 5.7 turns per item
VOCAB = 2000            # the course's own target
SAMPLE = 20             # words averaged at each measuring point
CHECKPOINTS = (50, 200, 500, 1000, 1500)


def run(window: int, share: float, seed: int = 1) -> dict[int, float]:
    """Recalls a word gets in the WINDOW_ITEMS items following its own.

    `window=0` disables the reservation, which is the behaviour before 0020.
    """
    srs.RECENT_WINDOW, srs.RECENT_SHARE = window, share
    random.seed(seed)
    store = srs.ProgressStore(None)
    hits: dict[str, list[int]] = defaultdict(list)
    carry = 0.0
    for n in range(VOCAB):
        name = f"w{n}"
        store.mark_introduced(name)
        # Carried rather than rounded: 4.46 recalls an item is a real average,
        # and rounding it to 4 every time loses 10% of the drilling.
        carry += RECALLS_PER_ITEM
        count, carry = int(carry), carry - int(carry)
        for target in store.draw_recalls(count, exclude={name}):
            hits[target].append(n)
            store.record_recall(target)

    out = {}
    for at in CHECKPOINTS:
        sampled = [sum(1 for h in hits[f"w{i}"] if at <= h < at + WINDOW_ITEMS)
                   for i in range(at, min(at + SAMPLE, VOCAB))]
        out[at] = sum(sampled) / len(sampled)
    return out


def main() -> None:
    if len(sys.argv) == 3:
        window, share = int(sys.argv[1]), float(sys.argv[2])
    else:
        window, share = srs.RECENT_WINDOW, srs.RECENT_SHARE

    before, after = run(0, 0.0), run(window, share)
    print(f"recalls in the {WINDOW_ITEMS} items after introduction, "
          f"averaged over {SAMPLE} words\n")
    print(f"  {'word #':>8} {'no reserve':>12} {f'K={window} share={share}':>18}")
    for at in CHECKPOINTS:
        print(f"  {at:>8} {before[at]:>12.1f} {after[at]:>18.1f}")
    print("\n  no reserve: falls away and does not stop."
          "\n  with one: settles, because the reservation is a fixed number and "
          "cannot be diluted.")


if __name__ == "__main__":
    main()

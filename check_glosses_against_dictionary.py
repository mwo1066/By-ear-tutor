"""Checks the course's own glosses against the cached Wiktionary dump.

Exists because of a hole nobody had noticed: `import_frequency_words.py` skips
every word the course already teaches, so the frequency file -- the only
dictionary in this repo -- excludes exactly the words most worth checking. Zero
of the 213 taught items appear in it. Every gloss the course teaches rested on
whoever typed it, with no second source, and one bad case had already got
through: the compounding rule illustrated itself with `đi học`, which is not a
lexical compound at all.

The data was on disk the whole time. `.cache/vi_en_wiktionary.tsv` is 31000
entries, downloaded on 11 August by the importer and read only for words the
course does NOT teach.

Offline. Run: python check_glosses_against_dictionary.py
"""
import html
import io
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from content import is_teachable, load_course
from tutor import CONTENT_DIR

CACHE = Path(__file__).parent / ".cache" / "vi_en_wiktionary.tsv"


def dictionary() -> dict[str, str]:
    """Every headword, including the alternates packed into one key with |."""
    out: dict[str, str] = {}
    for line in io.open(CACHE, encoding="utf-8"):
        if "\t" not in line:
            continue
        keys, body = line.split("\t", 1)
        for key in keys.split("|"):
            out.setdefault(key.strip(), body)
    return out


def senses(entry: str, n: int = 3) -> list[str]:
    return [html.unescape(re.sub("<[^>]+>", "", s)).strip()
            for s in re.findall(r"<li>(.*?)</li>", entry)[:n]]


def main() -> int:
    if not CACHE.exists():
        print(f"no dictionary at {CACHE} — run import_frequency_words.py once to fetch it")
        return 1
    wik = dictionary()
    items = [i for i in load_course(CONTENT_DIR) if is_teachable(i)]
    absent = []
    print(f"{len(items)} taught items, {len(wik)} dictionary headwords\n")
    for item in sorted(items, key=lambda i: i.name):
        entry = wik.get(item.name) or wik.get(item.name.lower())
        if entry is None:
            absent.append(item)
            continue
        print(f"{item.name}")
        print(f"    course: {item.gloss!r}")
        for s in senses(entry):
            print(f"    dict:   {s[:96]}")
    print(f"\n{len(items) - len(absent)} found, {len(absent)} absent from the dictionary:")
    for i in absent:
        print(f"    {i.name!r} — {i.gloss!r}")
    print("\nAbsent is not the same as wrong: a sentence is not a headword, and neither is")
    print("a rule's Vietnamese title. What matters is a gloss that CONTRADICTS the entry.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

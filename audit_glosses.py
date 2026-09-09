"""Flags every taught gloss that NO dictionary sense supports.

`check_glosses_against_dictionary.py` prints the course gloss beside the
dictionary entry for all 1346 items and leaves the comparing to a person. That
is the same reading job the list already is. This one does the mechanical half:
it reports only the items where the gloss shares no content word with ANY sense
the dictionary lists.

That is the shape of every gloss error caught by hand on 23 August:

    nợ    glossed "to be willing"   senses: debt, to owe
    nhắc  glossed "to lift"         senses: to remind
    Đức   glossed "king"            senses: Germany
    ý     glossed "Italy"           senses: Italy   <- and this one AGREES,
                                                       which is the limit below

It is a smell, not a verdict, and it is wrong in both directions:

  * A flagged gloss can be right. The instruction TELLS the model to override a
    dictionary that has captured a homograph -- `áo` is listed as "Austria" and
    means shirt, `súng` as "water lily" and means gun, `vui` as "a unisex given
    name" and means happy. Those overrides are the tool working, and they flag.

  * An unflagged gloss can be wrong. `ý` was glossed "Italy" straight from the
    senses; the senses were about the proper noun and the word means idea. Every
    error that comes from the dictionary being wrong agrees with the dictionary
    by construction, so nothing here can see it.

What it is good for: a shortlist. On the numbers below it turns 1346 items into
a few dozen worth a person's eye first.

    python audit_glosses.py            the flagged items
    python audit_glosses.py --all      every item, flagged or not
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

# Words that carry no meaning of their own, so overlapping on one proves
# nothing: "to be willing" and "to owe" share "to" and would look supported.
STOP = frozenset("""
a an the to of in on at for with and or as be is are was were it its this that
these those some any one two i you he she they we us them my your his her their
not no yes very more most much many something someone thing person way used use
""".split())


def dictionary() -> dict[str, str]:
    out: dict[str, str] = {}
    for line in io.open(CACHE, encoding="utf-8"):
        if "\t" not in line:
            continue
        keys, body = line.split("\t", 1)
        for key in keys.split("|"):
            out.setdefault(key.strip(), body)
    return out


def senses(entry: str) -> list[str]:
    return [html.unescape(re.sub("<[^>]+>", "", s)).strip()
            for s in re.findall(r"<li>(.*?)</li>", entry)]


def content_words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]+", text.lower()) if w not in STOP and len(w) > 1}


def main() -> int:
    if not CACHE.exists():
        print(f"no dictionary at {CACHE} — run import_frequency_words.py once to fetch it")
        return 1
    show_all = "--all" in sys.argv
    d = dictionary()
    # Atoms only. A construction is a sentence and a rule's gloss is a statement
    # the tutor speaks; neither is a headword, so neither can be looked up.
    items = [i for i in load_course(CONTENT_DIR)
             if is_teachable(i) and i.gloss and i.kind == "atom"]

    missing, unsupported, supported = [], [], 0
    for i in items:
        entry = d.get(i.name)
        if entry is None:
            missing.append(i)
            continue
        text = " ".join(senses(entry))
        # A gloss made ENTIRELY of stop words has nothing left to compare, so
        # stopping it guarantees a flag. That ate là ("to be"), và ("and"),
        # rất ("very"), này ("this") and every other function word on the first
        # run -- all of them agreeing with the dictionary word for word. When
        # the gloss stops to nothing, compare it whole instead.
        want = content_words(i.gloss) or set(re.findall(r"[a-z]+", i.gloss.lower()))
        listed = content_words(text) | set(re.findall(r"[a-z]+", text.lower()))
        if want & listed:
            supported += 1
        else:
            unsupported.append((i, senses(entry)[:3]))

    print(f"{len(items)} taught words, {len(d)} dictionary headwords\n")
    print(f"  supported by a listed sense   {supported}")
    print(f"  NOT supported by any sense    {len(unsupported)}   <- the shortlist")
    print(f"  not in the dictionary at all  {len(missing)}\n")

    print("NOT SUPPORTED — the gloss shares no content word with any sense.")
    print("Read these first. Some are correct overrides of a bad entry.\n")
    for i, ss in unsupported:
        print(f"  {i.name}")
        print(f"      course: {i.gloss}")
        for s in ss:
            print(f"      dict:   {s[:88]}")
    if missing:
        print(f"\nNOT IN THE DICTIONARY ({len(missing)}) — nothing to check against.")
        print("  " + ", ".join(i.name for i in missing[:40]))
    if show_all:
        print(f"\nSUPPORTED ({supported}) — a sense agrees with the gloss.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

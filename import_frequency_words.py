"""Imports Vietnamese vocabulary by frequency, as raw material for the course.

The course cannot grow by asking the model for four words at a time: at that
rate 2000 words is 500 requests and a year of sessions. The vocabulary has to
come from a list.

Two public sources, joined on the word:

  tabidots/vn-freqs   rank, corpus count, word, parts of speech. Tokenised with
                      pyvi, so polysyllabic words stay whole -- "cà phê" is one
                      entry, not two. That matters here: this project already
                      got burned reading "cà phê" as an assembly of two pieces.

  Vuizur/Wiktionary   Vietnamese-English senses. 99% coverage of the top 2000.

What this script does NOT do is write the gloss, and that is deliberate.
Wiktionary orders senses by etymology, not by use, so its first sense is
routinely the archaic one -- measured on the top 6 words: "là" comes back as
"fine silk" when it is the copula, "tôi" as "slave; domestic servant" when it
is "I", "anh" as "a given name" when it is how you address an older man. A
gloss is read aloud as the question a recall asks (spec rule 10), so a wrong
one sends the tutor asking for "fine silk" and expecting "là".

An empty gloss is loud: check_roster reports it at startup and the item cannot
be taught. A wrong one is silent. So every sense Wiktionary offers is written
to `senses`, the gloss is left empty, and choosing among them is left to the
annotation pass, which sees them and the frequency rank together.

    python import_frequency_words.py 300           # show what would be written
    python import_frequency_words.py 300 --write   # write it
    python fill_item_metadata.py --write           # then choose the glosses

Run: python import_frequency_words.py [how_many] [--write]
"""
import json
import re
import sys
import tomllib
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from content import PERSONAL_ITEMS_FILENAME
from tutor import CONTENT_DIR

FREQ_URL = "https://raw.githubusercontent.com/tabidots/vn-freqs/master/vn_word_frequencies.tsv"
WIKT_URL = ("https://raw.githubusercontent.com/Vuizur/Wiktionary-Dictionaries/master/"
            "Vietnamese-English%20Wiktionary%20dictionary.tsv")

# Filename decides load order, and load order is teaching order. 90 puts this
# after every hand-written lesson: the curated files are a composed progression
# (the words, then the sentence that assembles them) and must keep leading. This
# is a stock to draw from, not a syllabus.
OUT_PATH = CONTENT_DIR / "90_frequency_stock.toml"

CACHE = Path(__file__).parent / ".cache"


def _download(url: str, name: str) -> str:
    """Cached on disk: these files are ~3MB and never change between runs."""
    CACHE.mkdir(exist_ok=True)
    path = CACHE / name
    if path.exists():
        return path.read_text(encoding="utf-8")
    print(f"  downloading {name}...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        text = resp.read().decode("utf-8")
    path.write_text(text, encoding="utf-8")
    return text


_TAG = re.compile(r"<[^>]+>")
_PARENTHETICAL = re.compile(r"\([^)]*\)")


def _senses(html: str, limit: int = 4) -> list[str]:
    """Every sense Wiktionary lists, stripped of markup, longest kept intact.

    All of them, not the first: the first is what would be wrong. Handing the
    whole set to the annotation pass turns "invent a gloss" into "pick the one
    a beginner needs", which is a far easier question to get right and a far
    easier one to check.
    """
    out = []
    for raw in re.findall(r"<li>(.*?)</li>", html, re.S):
        text = _PARENTHETICAL.sub("", _TAG.sub("", raw))
        text = " ".join(text.split()).strip(" ,;.")
        if text and text not in out:
            out.append(text)
        if len(out) == limit:
            break
    return out


def _existing_names() -> set[str]:
    """Everything the course already has, so an import never duplicates it."""
    names = set()
    for path in CONTENT_DIR.glob("*.toml"):
        if path.name in ("persona.toml", OUT_PATH.name):
            continue
        for raw in tomllib.loads(path.read_text(encoding="utf-8")).get("items", []):
            names.add(raw["name"].lower())
    personal = CONTENT_DIR / PERSONAL_ITEMS_FILENAME
    if personal.exists():
        names |= {e["name"].lower() for e in json.loads(personal.read_text(encoding="utf-8"))}
    return names


def _toml_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def build(count: int) -> tuple[list[dict], int]:
    freq_raw = _download(FREQ_URL, "vn_freqs.tsv")
    wikt_raw = _download(WIKT_URL, "vi_en_wiktionary.tsv")

    senses: dict[str, list[str]] = {}
    for line in wikt_raw.splitlines():
        if "\t" not in line:
            continue
        forms, html = line.split("\t", 1)
        for form in forms.split("|"):
            senses.setdefault(form.strip().lower(), _senses(html))

    known = _existing_names()
    items, skipped = [], 0
    for line in freq_raw.splitlines():
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        rank, _count, word, pos = parts[0], parts[1], parts[2], parts[3]
        if word.lower() in known:
            skipped += 1
            continue
        items.append({
            "name": word,
            "rank": int(rank),
            # The whole set, not a primary. The source lists them alphabetically,
            # so "first" would mean "alphabetically first" -- it hands back
            # "adjective" for không, which is a negation particle. Nothing here
            # knows which sense dominates, so nothing here chooses.
            "pos": pos,
            "senses": senses.get(word.lower(), []),
        })
        if len(items) == count:
            break
    return items, skipped


def render(items: list[dict]) -> str:
    lines = [
        '# Vocabulary imported by corpus frequency -- raw material, not a lesson.',
        '# Generated by import_frequency_words.py; do not hand-edit, re-run instead.',
        '#',
        '# gloss is EMPTY on purpose and every item here is unteachable until it is',
        '# filled: check_roster reports each one at startup. Run fill_item_metadata.py',
        '# to choose a gloss from the senses listed on each item.',
        'title = "Vocabulaire par fréquence"',
        '',
    ]
    for item in items:
        lines += [
            "[[items]]",
            'type = "concept"',
            f'name = "{_toml_escape(item["name"])}"',
            'kind = "atom"',
            'gloss = ""',
            f'category = "{_toml_escape(item["pos"])}"',
            'language = "vi"',
            f'frequency_rank = {item["rank"]}',
            f'senses = {json.dumps(item["senses"], ensure_ascii=False)}',
            'description = ""',
            '',
        ]
    return "\n".join(lines)


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    count = int(args[0]) if args else 300
    write = "--write" in sys.argv

    items, skipped = build(count)
    with_senses = sum(1 for i in items if i["senses"])
    print(f"\n{len(items)} new word(s) at ranks {items[0]['rank']}-{items[-1]['rank']}")
    print(f"  {skipped} skipped: already in the course")
    print(f"  {with_senses} carry Wiktionary senses, {len(items) - with_senses} carry none")
    print("\nfirst ten:")
    for item in items[:10]:
        print(f"  {item['rank']:5}  {item['name']:16} {item['pos'][:34]:36} {item['senses'][:2]}")

    if not write:
        print(f"\nNothing written. Re-run with --write to create {OUT_PATH.name}.")
        return 0
    OUT_PATH.write_text(render(items), encoding="utf-8")
    print(f"\nWrote {OUT_PATH}")
    print("Every item is unteachable until fill_item_metadata.py gives it a gloss.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

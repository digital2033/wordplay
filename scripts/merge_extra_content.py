"""
Check and merge hand-written question files from content/extra/*.json into content/extra-bank.json.

Checks:
  - every book is one of the 66 book names used by the app
  - echo: a verse reference that matches the book, and elements with keywords
  - chars: a name and at least 3 clues
  - puzzles: words of capital letters A-Z only (3 to 12 letters), at least 6 words, no repeats
It stops with a list of problems if anything is wrong. Otherwise it prints a coverage table.
"""
import glob
import json
import os
import re
import sys

BOOKS = ["Genesis","Exodus","Leviticus","Numbers","Deuteronomy","Joshua","Judges","Ruth","1 Samuel","2 Samuel",
 "1 Kings","2 Kings","1 Chronicles","2 Chronicles","Ezra","Nehemiah","Esther","Job","Psalms","Proverbs",
 "Ecclesiastes","Song of Songs","Isaiah","Jeremiah","Lamentations","Ezekiel","Daniel","Hosea","Joel","Amos",
 "Obadiah","Jonah","Micah","Nahum","Habakkuk","Zephaniah","Haggai","Zechariah","Malachi",
 "Matthew","Mark","Luke","John","Acts","Romans","1 Corinthians","2 Corinthians","Galatians","Ephesians",
 "Philippians","Colossians","1 Thessalonians","2 Thessalonians","1 Timothy","2 Timothy","Titus","Philemon",
 "Hebrews","James","1 Peter","2 Peter","1 John","2 John","3 John","Jude","Revelation"]
assert len(BOOKS) == 66

src_dir = os.path.join("content", "extra")
out_path = os.path.join("content", "extra-bank.json")
problems = []
merged = {"echo": [], "chars": [], "puzzles": []}

for path in sorted(glob.glob(os.path.join(src_dir, "*.json"))):
    name = os.path.basename(path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for kind in ("echo", "chars", "puzzles"):
        for i, item in enumerate(data.get(kind, [])):
            where = f"{name} {kind}[{i}]"
            book = item.get("book")
            if book not in BOOKS:
                problems.append(f"{where}: unknown book {book!r}")
                continue
            if kind == "echo":
                ref = item.get("ref", "")
                if not ref.startswith(book + " ") or not re.match(r"^.+ \d+", ref):
                    problems.append(f"{where}: reference {ref!r} does not match book {book!r}")
                els = item.get("elements", [])
                if len(els) < 3 or any(not e.get("label") or not e.get("keys") for e in els):
                    problems.append(f"{where}: needs at least 3 elements, each with a label and keys")
                if not item.get("heart") or not item.get("mission"):
                    problems.append(f"{where}: needs a heart prompt and a mission")
            elif kind == "chars":
                if not item.get("name") or len(item.get("clues", [])) < 3:
                    problems.append(f"{where}: needs a name and at least 3 clues")
            else:  # puzzles
                words = item.get("words", [])
                seen = set()
                if len(words) < 6:
                    problems.append(f"{where}: needs at least 6 words")
                for wd in words:
                    w = wd.get("w", "")
                    if not re.fullmatch(r"[A-Z]{3,12}", w):
                        problems.append(f"{where}: word {w!r} must be 3 to 12 capital letters A-Z")
                    if w in seen:
                        problems.append(f"{where}: word {w!r} repeated")
                    seen.add(w)
                    if not wd.get("clue"):
                        problems.append(f"{where}: word {w!r} has no clue")
            merged[kind].append(item)

if problems:
    print("Problems found; nothing was written:")
    for p in problems:
        print("  -", p)
    sys.exit(1)

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, separators=(",", ":"))

def covered(kind):
    return len({x["book"] for x in merged[kind]})
print(f"Wrote {out_path}")
print(f"Echo passages: {len(merged['echo'])} in {covered('echo')} books")
print(f"Bible Characters: {len(merged['chars'])} in {covered('chars')} books")
print(f"Word lists (crossword and word search): {len(merged['puzzles'])} in {covered('puzzles')} books")

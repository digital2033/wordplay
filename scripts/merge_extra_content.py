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

import gzip as _gz
_KJV = json.load(_gz.open(os.path.join("default-bible", "en-kjv.json.gz"), "rt", encoding="utf-8"))["books"]
_CODE = {"Genesis":"GEN","Exodus":"EXO","Leviticus":"LEV","Numbers":"NUM","Deuteronomy":"DEU","Joshua":"JOS","Judges":"JDG","Ruth":"RUT","1 Samuel":"1SA","2 Samuel":"2SA","1 Kings":"1KI","2 Kings":"2KI","1 Chronicles":"1CH","2 Chronicles":"2CH","Ezra":"EZR","Nehemiah":"NEH","Esther":"EST","Job":"JOB","Psalms":"PSA","Proverbs":"PRO","Ecclesiastes":"ECC","Song of Songs":"SNG","Isaiah":"ISA","Jeremiah":"JER","Lamentations":"LAM","Ezekiel":"EZK","Daniel":"DAN","Hosea":"HOS","Joel":"JOL","Amos":"AMO","Obadiah":"OBA","Jonah":"JON","Micah":"MIC","Nahum":"NAM","Habakkuk":"HAB","Zephaniah":"ZEP","Haggai":"HAG","Zechariah":"ZEC","Malachi":"MAL","Matthew":"MAT","Mark":"MRK","Luke":"LUK","John":"JHN","Acts":"ACT","Romans":"ROM","1 Corinthians":"1CO","2 Corinthians":"2CO","Galatians":"GAL","Ephesians":"EPH","Philippians":"PHP","Colossians":"COL","1 Thessalonians":"1TH","2 Thessalonians":"2TH","1 Timothy":"1TI","2 Timothy":"2TI","Titus":"TIT","Philemon":"PHM","Hebrews":"HEB","James":"JAS","1 Peter":"1PE","2 Peter":"2PE","1 John":"1JN","2 John":"2JN","3 John":"3JN","Jude":"JUD","Revelation":"REV"}
import re as _re
def verse_text(ref):
    name = next((n for n in sorted(_CODE, key=len, reverse=True) if ref.startswith(n + " ")), None)
    if not name: return None
    rest = ref[len(name) + 1:]
    m = _re.match(r"^(\d+):(\d+)(?:-(\d+))?$", rest); single = _re.match(r"^(\d+)(?:-(\d+))?$", rest)
    if m: ch, a, b = int(m.group(1)), int(m.group(2)), int(m.group(3) or m.group(2))
    elif single: ch, a, b = 1, int(single.group(1)), int(single.group(2) or single.group(1))
    else: return None
    vs = _KJV[_CODE[name]].get(str(ch), [])
    text = " ".join(t for n, t in vs if a <= n <= b)
    return text or None
merged = {"echo": [], "chars": [], "puzzles": [], "story": [], "trivia": [], "who": []}

for path in sorted(glob.glob(os.path.join(src_dir, "*.json"))):
    name = os.path.basename(path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for kind in ("echo", "chars", "puzzles", "story", "trivia", "who"):
        for i, item in enumerate(data.get(kind, [])):
            where = f"{name} {kind}[{i}]"
            book = item.get("book")
            if book not in BOOKS:
                problems.append(f"{where}: unknown book {book!r}")
                continue
            if kind == "who":
                # the quotation is taken from the King James text; the speaker must be named in that verse
                ref = item.get("ref", "")
                speaker = item.get("speaker", "")
                dist = item.get("distractors", [])
                verse = verse_text(ref)
                if verse is None:
                    problems.append(f"{where}: reference {ref!r} not found in the King James text"); continue
                if speaker.lower() not in verse.lower():
                    problems.append(f"{where}: the speaker {speaker!r} is not named in {ref}")
                    continue
                if len(dist) < 3 or speaker in dist:
                    problems.append(f"{where}: needs 3 distractor names that are not the speaker")
                    continue
                words = verse.split()
                quote = " ".join(words[:30]) + ("\u2026" if len(words) > 30 else "")
                import random as _r
                rng = _r.Random(ref)
                opts = [speaker] + dist[:3]
                rng.shuffle(opts)
                merged["who"].append({"book": book, "quote": quote, "options": opts,
                                      "correct": opts.index(speaker), "note": ref})
                continue
            if kind == "trivia":
                opts = item.get("options", [])
                if len(opts) < 2 or not isinstance(item.get("correct"), int) or not (0 <= item["correct"] < len(opts)):
                    problems.append(f"{where}: needs 2 or more options and a valid 'correct' index")
                if not item.get("q") or not item.get("ref"):
                    problems.append(f"{where}: needs a question and a reference")
            elif kind == "story":
                ref = item.get("ref", "")
                if not ref.startswith(book + " ") or not item.get("title"):
                    problems.append(f"{where}: needs a title and a reference that matches the book")
                if len(item.get("cards", [])) < 3:
                    problems.append(f"{where}: needs at least 3 cards")
                if not item.get("heart") or not item.get("mission"):
                    problems.append(f"{where}: needs a heart prompt and a mission")
            elif kind == "echo":
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
print(f"Stories (Story Builder): {len(merged['story'])} in {covered('story')} books")
print(f"Bible Trivia (added by hand): {len(merged['trivia'])} in {covered('trivia')} books")
print(f"Who Said It (added by hand, quotes from the text): {len(merged['who'])} in {covered('who')} books")

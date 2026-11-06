"""
Generate question banks for all 66 books from the embedded King James Version.

Output: content/generated-bank.json. Each item's "book" is the book NAME (as used in the app), e.g. "Genesis". For each book:
  memory : Memory Verse items (verse with blanks)
  trivia : Bible Trivia items ("Which book is this verse from?" and "Fill in the missing word")
  who    : Who Said It items (only where the verse text names the speaker clearly)

Every item records its verse reference, so it can be checked against the Bible.
These are generated from the text, not written by hand: they test wording and
reference, not deep knowledge. Partners should review them before wide use.

Usage: python3 scripts/build_question_bank.py [default-bible/en-kjv.json.gz] [content/generated-bank.json]
"""
import gzip
import json
import os
import random
import re
import sys

SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join("default-bible", "en-kjv.json.gz")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join("content", "generated-bank.json")

# English book names in canon order (match the names used in the app)
NAMES = ["Genesis","Exodus","Leviticus","Numbers","Deuteronomy","Joshua","Judges","Ruth","1 Samuel","2 Samuel",
 "1 Kings","2 Kings","1 Chronicles","2 Chronicles","Ezra","Nehemiah","Esther","Job","Psalms","Proverbs",
 "Ecclesiastes","Song of Songs","Isaiah","Jeremiah","Lamentations","Ezekiel","Daniel","Hosea","Joel","Amos",
 "Obadiah","Jonah","Micah","Nahum","Habakkuk","Zephaniah","Haggai","Zechariah","Malachi",
 "Matthew","Mark","Luke","John","Acts","Romans","1 Corinthians","2 Corinthians","Galatians","Ephesians",
 "Philippians","Colossians","1 Thessalonians","2 Thessalonians","1 Timothy","2 Timothy","Titus","Philemon",
 "Hebrews","James","1 Peter","2 Peter","1 John","2 John","3 John","Jude","Revelation"]
CODES = ["GEN","EXO","LEV","NUM","DEU","JOS","JDG","RUT","1SA","2SA","1KI","2KI","1CH","2CH","EZR","NEH","EST","JOB",
 "PSA","PRO","ECC","SNG","ISA","JER","LAM","EZK","DAN","HOS","JOL","AMO","OBA","JON","MIC","NAM","HAB","ZEP","HAG",
 "ZEC","MAL","MAT","MRK","LUK","JHN","ACT","ROM","1CO","2CO","GAL","EPH","PHP","COL","1TH","2TH","1TI","2TI","TIT",
 "PHM","HEB","JAS","1PE","2PE","1JN","2JN","3JN","JUD","REV"]
assert len(NAMES) == len(CODES) == 66
NAME_OF = dict(zip(CODES, NAMES))

STOP = set("""the and that with from have this shall unto them their they which were when what there will into upon
thy thee thou hath hast not but for his her its are was been made also shall all one out him come even yet about
those these then than let saith said into may might must should would could".split()""".replace('"', '').split())

def core(w):
    return re.sub(r"^[^A-Za-z]+|[^A-Za-z]+$", "", w)

def usable(text):
    n = len(text.split())
    return 8 <= n <= 25 and not re.search(r"\d", text)

def build():
    with gzip.open(SRC, "rt", encoding="utf-8") as f:
        bible = json.load(f)
    rng = random.Random(20260101)
    out = {"source": "King James Version (embedded)", "generatedBy": "scripts/build_question_bank.py",
           "note": "Generated from the verse text. Check before wide use.", "books": {}}

    for code in CODES:
        name = NAME_OF[code]
        verses = [(int(c), int(n), t) for c, vs in bible["books"][code].items() for n, t in vs]
        ok = [v for v in verses if usable(v[2])]
        rng.shuffle(ok)
        entry = {"memory": [], "trivia": [], "who": []}

        # --- Memory Verse: 3 verses with 3-5 blanks each
        for c, n, t in ok[:3]:
            words = t.split()
            cands = [i for i, w in enumerate(words) if len(core(w)) >= 4 and core(w).lower() not in STOP]
            if len(cands) < 3:
                continue
            picks = sorted(rng.sample(cands, min(len(cands), rng.choice([3, 4, 5]))))
            tokens = list(words)
            for i in picks:
                tokens[i] = words[i].replace(core(words[i]), f"[[{core(words[i])}]]", 1)
            entry["memory"].append({"book": name, "ref": f"{name} {c}:{n}", "template": " ".join(tokens)})

        # --- Bible Trivia A: which book is this verse from? (distinct verses)
        a_pool = ok[:8]
        for c, n, t in a_pool:
            others = [x for x in CODES if x != code]
            distract = rng.sample(others, 3)
            opts = distract + [code]
            rng.shuffle(opts)
            entry["trivia"].append({"book": name, "q": f"Which book of the Bible is this verse from? \u201c{t}\u201d",
                                    "options": [NAME_OF[o] for o in opts], "correct": opts.index(code),
                                    "ref": f"{name} {c}:{n}", "info": f"{name} {c}:{n}"})

        # --- Bible Trivia B: fill in the missing word (distinct verses from the rest)
        b_pool = ok[8:16] or ok[:8]
        for c, n, t in b_pool:
            words = t.split()
            cands = [i for i, w in enumerate(words) if len(core(w)) >= 5 and core(w).lower() not in STOP]
            if not cands:
                continue
            i = rng.choice(cands)
            answer = core(words[i])
            blanked = " ".join(words[:i] + ["_____"] + words[i+1:])
            # distractors: long words from other verses of this book that are not in this verse
            pool_words = set()
            for _, _, t2 in ok:
                for w2 in t2.split():
                    c2 = core(w2)
                    if len(c2) >= 5 and c2.lower() not in STOP and c2 != answer and c2.lower() not in t.lower():
                        pool_words.add(c2)
            pool_words = sorted(pool_words)
            if len(pool_words) < 3:
                continue
            distract = rng.sample(pool_words, 3)
            opts = distract + [answer]
            rng.shuffle(opts)
            entry["trivia"].append({"book": name, "q": f"Fill in the missing word, {name} {c}:{n}: {blanked}",
                                    "options": opts, "correct": opts.index(answer),
                                    "ref": f"{name} {c}:{n}", "info": f"{name} {c}:{n}: {t}"})

        # --- Who Said It: speaker named by "And NAME said ..." in the verse text
        speakers = []
        for c, n, t in verses:
            m = re.match(r"^(?:(?:And|Then|But|So|Now|Jesus answered and) )?((?:[A-Z][a-z]+)(?: [A-Z][a-z]+)?) (?:said|spake|answered|saith)\b(.*)$", t)
            if m and m.group(1) not in ("The", "It", "He", "She", "They", "Behold", "Verily", "Blessed", "Thus"):
                rest = m.group(2).strip(" ,:;")
                rest = re.sub(r"^unto [^,:;]+[,:;]?\s*", "", rest).strip()
                if len(rest.split()) >= 6:
                    speakers.append((m.group(1), c, n, " ".join(rest.split()[:25])))
        names = sorted({s[0] for s in speakers})
        if len(names) >= 4:
            seen = set()
            for sp, c, n, quote in rng.sample(speakers, len(speakers)):
                if len(entry["who"]) >= 6 or (sp, c, n) in seen:
                    continue
                seen.add((sp, c, n))
                distract = rng.sample([x for x in names if x != sp], 3)
                opts = distract + [sp]
                rng.shuffle(opts)
                entry["who"].append({"book": name, "quote": quote + "\u2026", "options": opts,
                                     "correct": opts.index(sp), "note": f"{name} {c}:{n}"})
        out["books"][code] = entry

    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    return out

if __name__ == "__main__":
    out = build()
    counts = {c: (len(e["memory"]), len(e["trivia"]), len(e["who"])) for c, e in out["books"].items()}
    short_trivia = [c for c, (m, t, w) in counts.items() if t < 10]
    print(f"Books: {len(counts)}  memory: {sum(v[0] for v in counts.values())}  trivia: {sum(v[1] for v in counts.values())}  who: {sum(v[2] for v in counts.values())}")
    print("books with fewer than 10 trivia items:", short_trivia or "none")
    print("books with no Who Said It items:", [c for c, v in counts.items() if v[2] == 0])
    print("wrote", OUT, f"({os.path.getsize(OUT)/1024:.0f} KB)")

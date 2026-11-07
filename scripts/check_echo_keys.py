"""
Check every Echo passage against the embedded King James text.
  - the reference must point to real verses
  - every element must have at least one keyword that appears in those verses
Prints the problems and exits with an error if there are any.
"""
import glob, gzip, json, re, sys

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
CODE_OF = dict(zip(NAMES, CODES))

kjv = json.load(gzip.open("default-bible/en-kjv.json.gz", "rt", encoding="utf-8"))["books"]

def passage(ref):
    name = next((n for n in sorted(NAMES, key=len, reverse=True) if ref.startswith(n + " ")), None)
    if not name: return None, "book not recognised"
    rest = ref[len(name) + 1:]
    m = re.match(r"^(\d+):(\d+)(?:-(\d+))?$", rest)
    single = re.match(r"^(\d+)(?:-(\d+))?$", rest)
    if m:
        ch, a, b = int(m.group(1)), int(m.group(2)), int(m.group(3) or m.group(2))
    elif single:  # single-chapter book, e.g. "Jude 20-25"
        ch, a, b = 1, int(single.group(1)), int(single.group(2) or single.group(1))
    else:
        return None, "cannot read the verse range"
    verses = kjv[CODE_OF[name]].get(str(ch), [])
    text = " ".join(t for n, t in verses if a <= n <= b)
    if not text: return None, "no verses found"
    return text.lower(), None

problems = []
count = 0
for path in sorted(glob.glob("content/extra/*.json")):
    for item in json.load(open(path, encoding="utf-8")).get("echo", []):
        count += 1
        text, err = passage(item["ref"])
        if err:
            problems.append(f"{item['book']}: {item['ref']}: {err}"); continue
        for el in item["elements"]:
            if not any(k.lower() in text for k in el["keys"]):
                problems.append(f"{item['book']} {item['ref']}: no keyword of '{el['label'][:50]}' is in the verses")
print(f"Checked {count} Echo passages against the King James text.")
for p in problems: print("  -", p)
print("All keywords found." if not problems else f"{len(problems)} problem(s) to fix.")
sys.exit(1 if problems else 0)

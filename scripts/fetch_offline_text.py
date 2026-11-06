"""
Build-time Bible text download for Wordplay.

Reads bible-catalog.json. Each enabled version lists its text filesets per
testament ("OT" and "NT"), or one complete fileset under "C". For every
chapter it picks the right fileset, downloads the chapter from Bible Brain,
and writes _site/text/<fileset>/<BOOK>/<chapter>.json.

It also writes _site/text/catalog.json, which the game reads. It lists every
configured version, with "available" set true only when its text was saved.

Runs only when the repository variable DOWNLOAD_TEXT is "true".
The key comes from BIBLE_BRAIN_KEY and is never printed or saved.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

KEY = os.environ.get("BIBLE_BRAIN_KEY", "")
BASE = os.environ.get("BIBLE_BRAIN_BASE", "https://4.dbt.io/api")
MAX_MB = int(os.environ.get("MAX_MB", "900"))
PAUSE = float(os.environ.get("REQUEST_PAUSE", "0.25"))

if not KEY:
    sys.exit("BIBLE_BRAIN_KEY secret is missing. Add it under Settings > Secrets and variables > Actions.")

# (USFM code, chapter count) for all 66 books, in canon order
BOOKS = [
    ("GEN",50),("EXO",40),("LEV",27),("NUM",36),("DEU",34),("JOS",24),("JDG",21),("RUT",4),("1SA",31),("2SA",24),
    ("1KI",22),("2KI",25),("1CH",29),("2CH",36),("EZR",10),("NEH",13),("EST",10),("JOB",42),("PSA",150),("PRO",31),
    ("ECC",12),("SNG",8),("ISA",66),("JER",52),("LAM",5),("EZK",48),("DAN",12),("HOS",14),("JOL",3),("AMO",9),
    ("OBA",1),("JON",4),("MIC",7),("NAM",3),("HAB",3),("ZEP",3),("HAG",2),("ZEC",14),("MAL",4),
    ("MAT",28),("MRK",16),("LUK",24),("JHN",21),("ACT",28),("ROM",16),("1CO",16),("2CO",13),("GAL",6),("EPH",6),
    ("PHP",4),("COL",4),("1TH",5),("2TH",3),("1TI",6),("2TI",4),("TIT",3),("PHM",1),("HEB",13),("JAS",5),
    ("1PE",5),("2PE",3),("1JN",5),("2JN",1),("3JN",1),("JUD",1),("REV",22),
]
assert len(BOOKS) == 66 and sum(c for _, c in BOOKS) == 1189
OT_CODES = {code for code, _ in BOOKS[:39]}

def testament(code):
    return "OT" if code in OT_CODES else "NT"

def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

catalog = load("bible-catalog.json")
game_chapters = load("game-chapters.json").get("items", [])

# Enabled versions, de-duplicated by version id
enabled = {}
for country in catalog.get("countries", []):
    for lang in country.get("languages", []):
        for v in lang.get("versions", []):
            if v.get("enabled") is True and not str(v.get("id", "")).startswith("REPLACE"):
                enabled.setdefault(v["id"], v)
if not enabled:
    sys.exit("No enabled versions in bible-catalog.json. Set enabled to true for the versions to publish.")

def get_json(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)

def wanted_chapters(scope):
    if scope == "full":
        return [(b, c) for b, n in BOOKS for c in range(1, n + 1)]
    return [(item["book"], int(item["chapter"])) for item in game_chapters]

def fileset_for(version, code):
    fs = version.get("filesets") or {}
    return fs.get(testament(code)) or fs.get("C")

total_bytes = 0
saved = {}           # version id -> number of chapters saved
field_checked = False

for vid, meta in enabled.items():
    chapters = wanted_chapters(meta.get("scope", "games"))
    print(f"== {meta.get('name', vid)}: {len(chapters)} chapters")
    saved[vid] = 0
    for book, ch in chapters:
        fs = fileset_for(meta, book)
        if not fs:
            print(f"  skip {book} {ch}: no fileset for the {testament(book)} in {vid}")
            continue
        url = f"{BASE}/bibles/filesets/{fs}/{book}/{ch}?" + urllib.parse.urlencode({"key": KEY, "v": 4})
        try:
            data = get_json(url)
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                sys.exit(f"Bible Brain refused the key (HTTP {e.code}). Check BIBLE_BRAIN_KEY.")
            print(f"  skip {fs} {book} {ch}: HTTP {e.code}")
            continue
        except Exception:
            print(f"  skip {fs} {book} {ch}: network error")
            continue
        rows = data.get("data") or []
        if not rows:
            print(f"  no text: {fs} {book} {ch}")
            continue
        if not field_checked:
            sample = rows[0]
            if "verse_text" not in sample or not ("verse_start" in sample or "verse_number" in sample):
                sys.exit(f"Unexpected verse fields: {sorted(sample.keys())}. Update fetch_offline_text.py to match.")
            field_checked = True
        verses = []
        for row in rows:
            num = row.get("verse_start", row.get("verse_number"))
            text = (row.get("verse_text") or "").strip()
            if num is not None and text:
                verses.append({"verse": int(num), "text": text})
        out = os.path.join("_site", "text", fs, book, f"{ch}.json")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"fileset": fs, "book": book, "chapter": ch, "verses": verses}, f, ensure_ascii=False)
        total_bytes += os.path.getsize(out)
        saved[vid] += 1
        if total_bytes > MAX_MB * 1024 * 1024:
            sys.exit(f"Size limit of {MAX_MB} MB reached. Reduce the versions or chapters.")
        time.sleep(PAUSE)
    print(f"   saved {saved[vid]} chapters")

# Public catalogue: every configured version (not placeholders), with its filesets and availability
public = {"countries": []}
for country in catalog.get("countries", []):
    c_out = {"code": country["code"], "name": country["name"], "languages": []}
    for lang in country.get("languages", []):
        vs = []
        for v in lang.get("versions", []):
            vid = str(v.get("id", ""))
            if not vid or vid.startswith("REPLACE"):
                continue
            entry = {"fileset": vid, "name": v["name"], "available": saved.get(vid, 0) > 0}
            if v.get("filesets"):
                entry["filesets"] = v["filesets"]
            vs.append(entry)
        if vs:
            c_out["languages"].append({"code": lang["code"], "name": lang["name"], "versions": vs})
    if c_out["languages"]:
        public["countries"].append(c_out)

os.makedirs(os.path.join("_site", "text"), exist_ok=True)
with open(os.path.join("_site", "text", "catalog.json"), "w", encoding="utf-8") as f:
    json.dump(public, f, ensure_ascii=False, indent=2)

ok = sum(saved.values())
print(f"Done: {ok} chapters, {total_bytes / 1048576:.1f} MB, {len(public['countries'])} countries in the public catalogue")
if ok == 0:
    sys.exit("No chapters were downloaded. Check the fileset IDs and the key.")

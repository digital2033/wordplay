"""
Build step: embed the English King James Version as the built-in default Bible.

Downloads every chapter of the KJV from Bible Brain (the BIBLE_BRAIN_KEY secret is used
only here, during the build) and writes one compressed file:
    _site/default-bible/en-kjv.json.gz
Structure: { "id": "ENGKJV", "name": "...", "books": { "GEN": { "1": [[1, "text"], ...], ... }, ... } }

The KJV is public domain. Runs only when DOWNLOAD_DEFAULT_BIBLE is "true".
"""
import gzip
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

KEY = os.environ.get("BIBLE_BRAIN_KEY", "")
BASE = os.environ.get("BIBLE_BRAIN_BASE", "https://4.dbt.io/api")
PAUSE = float(os.environ.get("REQUEST_PAUSE", "0.25"))
if not KEY:
    sys.exit("BIBLE_BRAIN_KEY secret is missing.")

BOOKS = [
    ("GEN",50),("EXO",40),("LEV",27),("NUM",36),("DEU",34),("JOS",24),("JDG",21),("RUT",4),("1SA",31),("2SA",24),
    ("1KI",22),("2KI",25),("1CH",29),("2CH",36),("EZR",10),("NEH",13),("EST",10),("JOB",42),("PSA",150),("PRO",31),
    ("ECC",12),("SNG",8),("ISA",66),("JER",52),("LAM",5),("EZK",48),("DAN",12),("HOS",14),("JOL",3),("AMO",9),
    ("OBA",1),("JON",4),("MIC",7),("NAM",3),("HAB",3),("ZEP",3),("HAG",2),("ZEC",14),("MAL",4),
    ("MAT",28),("MRK",16),("LUK",24),("JHN",21),("ACT",28),("ROM",16),("1CO",16),("2CO",13),("GAL",6),("EPH",6),
    ("PHP",4),("COL",4),("1TH",5),("2TH",3),("1TI",6),("2TI",4),("TIT",3),("PHM",1),("HEB",13),("JAS",5),
    ("1PE",5),("2PE",3),("1JN",5),("2JN",1),("3JN",1),("JUD",1),("REV",22),
]
assert sum(c for _, c in BOOKS) == 1189
OT = {c for c, _ in BOOKS[:39]}

# Filesets for the KJV, from the catalogue
with open("bible-catalog.json", encoding="utf-8") as f:
    cat = json.load(f)
fsets = None
for co in cat["countries"]:
    for la in co["languages"]:
        for v in la["versions"]:
            if v.get("id") == "ENGKJV" and v.get("filesets"):
                fsets = v["filesets"]
if not fsets:
    sys.exit("ENGKJV with filesets is missing from bible-catalog.json")

def fetch_chapter(fs, book, ch):
    url = f"{BASE}/bibles/filesets/{fs}/{book}/{ch}?" + urllib.parse.urlencode({"key": KEY, "v": 4})
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r).get("data") or []

out = {"id": "ENGKJV", "name": "King James Version", "books": {}}
count = 0
for code, n in BOOKS:
    fs = fsets["OT"] if code in OT else fsets["NT"]
    out["books"][code] = {}
    for ch in range(1, n + 1):
        try:
            rows = fetch_chapter(fs, code, ch)
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                sys.exit(f"Bible Brain refused the key (HTTP {e.code}).")
            sys.exit(f"Could not read {code} {ch} (HTTP {e.code}).")
        verses = []
        for row in rows:
            num = row.get("verse_start")
            text = (row.get("verse_text") or "").strip()
            if num is not None and text:
                verses.append([int(num), text])
        if not verses:
            sys.exit(f"No text for {code} {ch}. Check the KJV filesets.")
        out["books"][code][str(ch)] = verses
        count += len(verses)
        time.sleep(PAUSE)
    print(f"{code}: done")

os.makedirs(os.path.join("_site", "default-bible"), exist_ok=True)
path = os.path.join("_site", "default-bible", "en-kjv.json.gz")
with gzip.open(path, "wt", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
print(f"Wrote {path}: {count} verses, {os.path.getsize(path)/1048576:.2f} MB")

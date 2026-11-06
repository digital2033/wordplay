"""
Convert a folder (or zip) of USX 3.0 Bible files into the compact file the game embeds:

    default-bible/en-kjv.json.gz
    { "id": "ENGKJV", "name": "King James Version", "books": { "GEN": { "1": [[1, "text"], ...] } } }

Usage:
    python3 scripts/usx_to_default_bible.py ENGKJV-usx.zip  [--id ENGKJV --name "King James Version" --out default-bible/en-kjv.json.gz]
    python3 scripts/usx_to_default_bible.py path/to/usx-folder

Checks every book against the number of chapters in the canon and stops if anything is missing.
Needs no key and no internet.
"""
import argparse
import gzip
import io
import json
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

CHAPTERS = {
    "GEN":50,"EXO":40,"LEV":27,"NUM":36,"DEU":34,"JOS":24,"JDG":21,"RUT":4,"1SA":31,"2SA":24,"1KI":22,"2KI":25,
    "1CH":29,"2CH":36,"EZR":10,"NEH":13,"EST":10,"JOB":42,"PSA":150,"PRO":31,"ECC":12,"SNG":8,"ISA":66,"JER":52,
    "LAM":5,"EZK":48,"DAN":12,"HOS":14,"JOL":3,"AMO":9,"OBA":1,"JON":4,"MIC":7,"NAM":3,"HAB":3,"ZEP":3,"HAG":2,
    "ZEC":14,"MAL":4,"MAT":28,"MRK":16,"LUK":24,"JHN":21,"ACT":28,"ROM":16,"1CO":16,"2CO":13,"GAL":6,"EPH":6,
    "PHP":4,"COL":4,"1TH":5,"2TH":3,"1TI":6,"2TI":4,"TIT":3,"PHM":1,"HEB":13,"JAS":5,"1PE":5,"2PE":3,"1JN":5,
    "2JN":1,"3JN":1,"JUD":1,"REV":22,
}

def leading_int(s):
    m = re.match(r"\s*(\d+)", s or "")
    return int(m.group(1)) if m else None

def parse_usx(xml_bytes):
    """Return (book_code, {chapter: [[verse, text], ...]}) from one USX book."""
    root = ET.fromstring(xml_bytes)
    book_el = root.find("book")
    code = (book_el.get("code") if book_el is not None else "") or ""
    chapters, ch = {}, None
    open_verse, buf = None, []

    def flush():
        nonlocal open_verse, buf
        if open_verse is not None and ch is not None:
            text = re.sub(r"\s+", " ", "".join(buf)).strip()
            if text:
                chapters.setdefault(ch, []).append([open_verse, text])
        open_verse, buf = None, []

    def walk(el):
        nonlocal ch, open_verse
        tag = el.tag
        if tag == "chapter" and el.get("number") is not None:
            flush()
            ch = leading_int(el.get("number"))
            chapters.setdefault(ch, [])
            return
        if tag == "verse":
            if el.get("number") is not None:
                flush()
                open_verse = leading_int(el.get("number"))
            # an end milestone (eid) closes the verse
            elif el.get("eid") is not None:
                flush()
            return
        if tag == "note":          # footnotes and cross references are not verse text
            return
        if open_verse is not None and el.text:
            buf.append(el.text)
        for child in el:
            walk(child)
            if open_verse is not None and child.tail:
                buf.append(child.tail)

    for child in root:
        walk(child)
    flush()
    return code, chapters

def read_inputs(src):
    """Yield (name, bytes) for every .usx file in a zip or a folder."""
    if os.path.isdir(src):
        for dp, _, files in os.walk(src):
            for f in sorted(files):
                if f.lower().endswith(".usx"):
                    with open(os.path.join(dp, f), "rb") as fh:
                        yield f, fh.read()
    else:
        with zipfile.ZipFile(src) as z:
            for n in sorted(z.namelist()):
                if n.lower().endswith(".usx"):
                    yield os.path.basename(n), z.read(n)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--id", default="ENGKJV")
    ap.add_argument("--name", default="King James Version")
    ap.add_argument("--out", default=os.path.join("default-bible", "en-kjv.json.gz"))
    a = ap.parse_args()

    books = {}
    for name, data in read_inputs(a.src):
        code, chapters = parse_usx(data)
        if not code:
            sys.exit(f"{name}: no book code found")
        if code in books:
            sys.exit(f"{name}: book {code} appears twice")
        books[code] = chapters

    problems = []
    for code, n in CHAPTERS.items():
        if code not in books:
            problems.append(f"missing book {code}")
            continue
        got = sorted(books[code].keys())
        if got != list(range(1, n + 1)):
            problems.append(f"{code}: chapters {got[:3]}...{got[-3:]} (expected 1-{n})")
        for c in got:
            if not books[code][c]:
                problems.append(f"{code} {c}: no verses")
    extra = sorted(set(books) - set(CHAPTERS))
    if extra:
        problems.append("unexpected books: " + ", ".join(extra))
    if problems:
        sys.exit("Checks failed:\n  " + "\n  ".join(problems))

    out = {"id": a.id, "name": a.name, "books": {}}
    total = 0
    for code in CHAPTERS:
        out["books"][code] = {}
        for c in sorted(books[code]):
            verses = sorted(books[code][c], key=lambda v: v[0])
            out["books"][code][str(c)] = verses
            total += len(verses)

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with gzip.open(a.out, "wt", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(f"Books: {len(out['books'])}, chapters: {sum(len(v) for v in out['books'].values())}, verses: {total}")
    print(f"Wrote {a.out} ({os.path.getsize(a.out) / 1048576:.2f} MB)")

if __name__ == "__main__":
    main()

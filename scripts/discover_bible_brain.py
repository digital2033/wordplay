"""
Discovery step for the Bible Brain catalogue.

Round 5: find the real language IDs and text filesets for English and Malayalam
by listing every language in the US and India, matching ISO codes on our side,
and then listing each language's Bibles and their filesets.

Saves small, key-free summaries to discovery/. Run manually from the Actions tab.
The key comes from BIBLE_BRAIN_KEY and is never saved.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

KEY = os.environ.get("BIBLE_BRAIN_KEY", "")
BASE = os.environ.get("BIBLE_BRAIN_BASE", "https://4.dbt.io/api")
if not KEY:
    sys.exit("BIBLE_BRAIN_KEY secret is missing.")

os.makedirs("discovery", exist_ok=True)
summary = {}

def fetch(path, params):
    url = f"{BASE}{path}?" + urllib.parse.urlencode(dict(params, key=KEY, v=4))
    safe = f"{BASE}{path}?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return r.status, json.load(r), safe
    except urllib.error.HTTPError as e:
        return e.code, None, safe
    except Exception as e:
        return None, str(e), safe

def save(name, obj):
    with open(os.path.join("discovery", f"{name}.json"), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def all_pages(path, params, limit=100, max_pages=10):
    items, page = [], 1
    while page <= max_pages:
        status, body, safe = fetch(path, dict(params, limit=str(limit), page=str(page)))
        if status != 200 or not isinstance(body, dict):
            break
        data = body.get("data") or []
        items.extend(data)
        if len(data) < limit:
            break
        page += 1
    return items

# 1. Languages in the US and India, matched by ISO code on our side
langs = {}
for cc in ("US", "IN"):
    items = all_pages("/languages", {"country": cc})
    langs[cc] = items
    save(f"languages_{cc}_compact", [
        {"id": x.get("id"), "iso": x.get("iso"), "name": x.get("name"),
         "bibles": x.get("bibles"), "filesets": x.get("filesets")} for x in items])
    summary[f"languages_{cc}"] = {"count": len(items)}

def find(cc, iso):
    return [x for x in langs.get(cc, []) if x.get("iso") == iso]

targets = {"english": ("US", "eng"), "malayalam": ("IN", "mal")}
found = {}
for label, (cc, iso) in targets.items():
    hits = find(cc, iso)
    if not hits:  # English is sometimes listed under India or elsewhere; search both lists
        hits = find("IN" if cc == "US" else "US", iso)
    found[label] = hits[0] if hits else None
    summary[f"{label}_language"] = found[label] and {"id": found[label].get("id"), "iso": iso, "name": found[label].get("name")} or "NOT FOUND"

# 2. For each language found, list its Bibles and text filesets
for label, rec in found.items():
    if not rec:
        continue
    bibles = all_pages("/bibles", {"language_id": str(rec["id"])}, limit=100, max_pages=3)
    rows = []
    for b in bibles:
        fsets = (b.get("filesets") or {}).get("dbp-prod") or []
        rows.append({
            "abbr": b.get("abbr"), "name": b.get("name"), "vname": b.get("vname"),
            "text_filesets": [{"id": f.get("id"), "type": f.get("type"), "size": f.get("size")}
                              for f in fsets if str(f.get("type", "")).startswith("text")],
        })
    save(f"{label}_bibles", rows)
    summary[f"{label}_bibles"] = {"count": len(rows),
                                  "with_text": sum(1 for r in rows if r["text_filesets"])}

# 3. Confirm the text chapter route for the English KJV (already known to work)
status, body, safe = fetch("/bibles/filesets/ENGKJV/JHN/3", {})
summary["check_text_route_ENGKJV"] = {"status": status,
                                      "verse_fields": sorted(body["data"][0].keys()) if status == 200 and body.get("data") else None}

with open(os.path.join("discovery", "summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print(json.dumps(summary, ensure_ascii=False, indent=2))

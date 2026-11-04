"""
Discovery step for the Bible Brain catalogue (countries, languages, versions).

Calls the Bible Brain endpoints the catalogue would use, and saves a SMALL sample
of each response to discovery/, so the real field names and filters can be checked
before the game is built around them. Run it manually from the Actions tab.

The key comes from BIBLE_BRAIN_KEY and is never saved. Saved URLs have the key removed.
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

ENDPOINTS = [
    # Round 2: find the country-to-language link, language filters, and the text route
    ("country_detail", "/countries/AD", {}),
    ("country_by_iso2", "/countries/AND", {}),
    ("languages_in_country", "/languages", {"country": "AD", "limit": "25"}),
    ("language_detail", "/languages/5160", {}),
    ("bibles_by_language_id", "/bibles", {"language_id": "8076", "limit": "25"}),
    ("bibles_by_iso", "/bibles", {"iso": "eng", "limit": "25"}),
    ("fileset_chapter", "/bibles/filesets/ENGKJVO1DA/GEN/1", {}),
    ("fileset_text_info", "/bibles/ENGKJV", {}),
]

os.makedirs("discovery", exist_ok=True)
summary = {}

def fetch(path, params):
    q = dict(params, key=KEY, v=4)
    url = f"{BASE}{path}?" + urllib.parse.urlencode(q)
    safe_url = f"{BASE}{path}?" + urllib.parse.urlencode(params)   # key removed
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return r.status, json.load(r), safe_url
    except urllib.error.HTTPError as e:
        return e.code, None, safe_url
    except Exception as e:
        return None, str(e), safe_url

for name, path, params in ENDPOINTS:
    status, body, safe_url = fetch(path, params)
    entry = {"url": safe_url, "status": status}
    if isinstance(body, dict):
        entry["top_level_keys"] = sorted(body.keys())
        data = body.get("data")
        if isinstance(data, list):
            entry["count_in_page"] = len(data)
            entry["first_item_keys"] = sorted(data[0].keys()) if data and isinstance(data[0], dict) else []
            sample = data[:2]
        else:
            entry["data_type"] = type(data).__name__
            sample = data
        meta = body.get("meta")
        if meta is not None:
            entry["meta"] = meta
        with open(os.path.join("discovery", f"{name}.sample.json"), "w", encoding="utf-8") as f:
            json.dump({"url": safe_url, "sample": sample, "meta": meta}, f, ensure_ascii=False, indent=2)
    elif body is not None:
        entry["error"] = str(body)[:200]
    summary[name] = entry
    print(f"{name}: HTTP {status}, keys {entry.get('first_item_keys', entry.get('top_level_keys', []))}")

with open(os.path.join("discovery", "summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print("Saved discovery/ (download it from the workflow artifacts)")

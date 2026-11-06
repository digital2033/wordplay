"""
Discovery step for the Bible Brain catalogue (round 6).

Checks what a full country list needs:
  - how many countries the /countries endpoint returns across all pages,
  - the exact shape of each country's code field,
  - whether /languages?country=XX works for countries other than the US and India.
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
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:
        return None, str(e)

def all_pages(path, params, limit=100, max_pages=20):
    items, page, status = [], 1, None
    while page <= max_pages:
        status, body = fetch(path, dict(params, limit=str(limit), page=str(page)))
        if status != 200 or not isinstance(body, dict):
            break
        data = body.get("data") or []
        items.extend(data)
        meta = body.get("meta") or {}
        if len(data) < limit:
            break
        page += 1
    return items, status, page

# 1. Countries: all pages, and the shape of the code field
countries, status, pages = all_pages("/countries", {})
code_shapes = {}
for c in countries:
    codes = c.get("codes")
    code_shapes[type(codes).__name__] = code_shapes.get(type(codes).__name__, 0) + 1
summary["countries"] = {"status": status, "count": len(countries), "pages_read": pages,
                        "code_field_types": code_shapes,
                        "first_codes_value": countries[0].get("codes") if countries else None,
                        "first_name": countries[0].get("name") if countries else None}
with open("discovery/countries_all_sample.json", "w", encoding="utf-8") as f:
    json.dump(countries[:5], f, ensure_ascii=False, indent=2)

# 2. Languages for a spread of countries, using the 2-letter code from the country record
probe = ["AE", "BR", "FR", "JP", "NG", "NP"]
per_country = {}
for cc in probe:
    langs, st, pg = all_pages("/languages", {"country": cc})
    per_country[cc] = {"status": st, "count": len(langs),
                       "sample": [{"iso": x.get("iso"), "name": x.get("name")} for x in langs[:3]]}
summary["languages_by_country"] = per_country

with open(os.path.join("discovery", "summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print(json.dumps(summary, ensure_ascii=False, indent=2)[:3000])

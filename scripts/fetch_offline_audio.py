"""
Downloads the chapter audio listed in offline-audio.json into _site/media
at build time, so the published game can play it without the server.

Runs only when the repository variable DOWNLOAD_AUDIO is set to "true".
The Bible Brain key is read from the BIBLE_BRAIN_KEY secret and is never
printed or written to a file.

IMPORTANT: files published this way are publicly downloadable. Only use
this when the Bible Brain licence allows public redistribution.
"""
import json
import os
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request

key = os.environ.get("BIBLE_BRAIN_KEY", "")
if not key:
    sys.exit("BIBLE_BRAIN_KEY secret is missing. Add it under Settings > Secrets and variables > Actions.")

base = os.environ.get("BIBLE_BRAIN_BASE", "https://4.dbt.io/api")
limit_mb = int(os.environ.get("MAX_MB", "800"))

with open("offline-audio.json", encoding="utf-8") as f:
    items = json.load(f).get("items", [])

if not items:
    sys.exit("offline-audio.json has no items. Add the chapters to download.")

total = 0
for it in items:
    fs, book, ch = it["fileset"], it["book"], int(it["chapter"])
    meta_url = f"{base}/bibles/filesets/{fs}/{book}/{ch}?" + urllib.parse.urlencode({"key": key, "v": 4})
    try:
        with urllib.request.urlopen(meta_url, timeout=30) as r:
            meta = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Bible Brain returned HTTP {e.code} for {fs} {book} {ch}. Check the fileset and key.")
    except Exception:
        sys.exit(f"Could not reach Bible Brain for {fs} {book} {ch}.")

    item = (meta.get("data") or [{}])[0]
    signed = item.get("path") or item.get("url")  # confirm the field name against the Bible Brain docs
    if not signed:
        print(f"No audio found for {fs} {book} {ch}, skipping")
        continue

    out = os.path.join("_site", "media", fs, book, f"{ch}.mp3")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    try:
        with urllib.request.urlopen(signed, timeout=120) as src, open(out, "wb") as dst:
            shutil.copyfileobj(src, dst)
    except Exception:
        sys.exit(f"Download failed for {fs} {book} {ch}.")

    total += os.path.getsize(out)
    if total > limit_mb * 1024 * 1024:
        sys.exit(f"Size limit of {limit_mb} MB exceeded. Reduce the list in offline-audio.json.")
    print(f"Saved {fs} {book} {ch}")

print(f"Downloaded {total / 1048576:.1f} MB in total")

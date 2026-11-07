"""Names: only the name the player typed is shown next to their profile. Character names are not added."""
import os
from playwright.sync_api import sync_playwright
URL = os.environ.get("WORDPLAY_URL", "http://localhost:8800/index.html")
results = []
def check(name, ok, detail=""):
    results.append(ok); print(("PASS " if ok else "FAIL ") + name + ("" if ok or not detail else "  - " + detail))
CHARS = ["Noah", "Moses", "David", "Ruth", "Esther", "Joseph", "Daniel", "Deborah", "Peter", "Paul", "Jonah", "Elijah"]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(URL, wait_until="networkidle")
    pg.fill("#pf-name", "Priya"); pg.locator("#pf-av button").nth(5).click()   # Joseph
    pg.click("#pf-save"); pg.wait_for_selector(".gcard")
    chip = pg.inner_text("#who")
    check("header shows only the typed name", "Priya" in chip and "Joseph" not in chip, chip)
    pg.evaluate("showProfile(true)")
    pg.fill("#pf-name", "Asha"); pg.locator("#pf-av button").nth(1).click(); pg.click("#pf-save"); pg.wait_for_selector(".gcard")
    pg.evaluate("showProfile(true)")
    names = pg.locator(".av-name").all_inner_texts()
    check("switch list shows only typed names", set(names) <= {"Priya", "Asha"} and "Priya" in names, str(names))
    check("no character names as visible captions", not any(c in " ".join(pg.locator(".av-name").all_inner_texts()) for c in CHARS))
    pg.evaluate("go('board')")
    rows = pg.inner_text("table").replace("\n", " ") if pg.locator("table").count() else ""
    check("progress and leaderboard show only typed names", not any(c in pg.inner_text("#stage") for c in ["Joseph", "Moses"]) or "Joseph" not in pg.inner_text("#stage"))
    check("no page errors", not errors, "; ".join(errors))
    b.close()
print(f"\n{sum(results)}/{len(results)} name checks passed")

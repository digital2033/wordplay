"""About page: it is in the menu, and it has the key information from the README."""
import os
from playwright.sync_api import sync_playwright
URL = os.environ.get("WORDPLAY_URL", "http://localhost:8800/index.html")
results = []
def check(name, ok, detail=""):
    results.append(ok); print(("PASS " if ok else "FAIL ") + name + ("" if ok or not detail else "  - " + detail))
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(URL, wait_until="networkidle")
    pg.fill("#pf-name", "About"); pg.click("#pf-save"); pg.wait_for_selector(".gcard")
    check("About is in the menu", pg.locator("#nav button", has_text="About").count() == 1)
    pg.locator("#nav button", has_text="About").click()
    text = pg.inner_text("#stage")
    check("About page opens", "About Wordplay" in text)
    for item in ["Echo", "Scene Detective", "Covenant Quest", "Who Said It", "Story Builder", "Memory Verse",
                 "Bible Trivia", "Bible Characters", "Bible Crossword", "Word Search"]:
        check(f"lists the game {item}", item in text)
    for section in ["How to play", "Difficulty", "Points and progress", "Bible text", "Languages",
                    "Installing and offline use", "Privacy", "Content and accuracy", "Licence and credits", "Known limits"]:
        check(f"has the section '{section}'", section in text)
    check("states the MIT licence", "MIT License" in text)
    check("states the content disclaimer", "may contain errors" in text)
    check("no page errors", not errors, "; ".join(errors))
    b.close()
print(f"\n{sum(results)}/{len(results)} About checks passed")

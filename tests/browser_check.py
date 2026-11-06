import json, sys
from playwright.sync_api import sync_playwright

import os
URL = os.environ.get("WORDPLAY_URL", os.environ.get("WORDPLAY_URL", "http://localhost:8800/index.html"))
errors, console_err = [], []
results = []
def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (("  - " + detail) if detail and not ok else ""))

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 390, "height": 844})
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: console_err.append(m.text) if m.type == "error" else None)
    page.goto(URL, wait_until="networkidle")
    check("page loads without errors", not errors, "; ".join(errors))

    # --- profile
    page.fill("#pf-name", "Tester")
    page.click("#pf-save")
    page.wait_for_selector(".gcard", timeout=8000)
    check("home shows 10 game cards", page.locator(".gcard").count() == 10, str(page.locator(".gcard").count()))

    # --- filters
    def count_for(filter_name):
        page.click(f'.chip[data-f="{filter_name}"]')
        return page.locator(".gcard").count()
    check("filter Text shows all 10", count_for("text") == 10)
    video = count_for("video")
    check("filter Video shows Scene Detective and Covenant Quest", video == 2, str(video))
    audio = count_for("audio")
    check("filter Audio shows Echo, Who Said It, Memory Verse", audio == 3, str(audio))
    count_for("all")

    # --- book picker: enabled books must match the question data for each game
    expected = page.evaluate("""() => {
        const out = {};
        for (const g of GAMES) out[g.id] = {noBook: !!g.noBook, books: g.noBook ? [] : [...booksWithContent(g.id)]};
        return out;
    }""")
    print("books with questions per game:", {k: len(v["books"]) for k, v in expected.items()})

    game_titles = page.evaluate("GAMES.map(g => g.title)")
    for i, title in enumerate(game_titles):
        gid = page.evaluate(f"GAMES[{i}].id")
        page.evaluate("home()"); page.wait_for_selector(".gcard")
        page.locator(".gcard").nth(i).click()
        page.wait_for_selector("text=Start", timeout=5000)
        if expected[gid]["noBook"]:
            page.click("text=Start")
            page.wait_for_timeout(300)
            check(f"{title}: starts without a book chooser", page.locator(".tile").count() == 0)
            continue
        page.click("text=Start")
        page.wait_for_selector(".tile", timeout=5000)
        tiles = page.locator(".tile")
        n = tiles.count()
        enabled = [tiles.nth(k).inner_text() for k in range(n) if tiles.nth(k).is_enabled()]
        # OT list first, then NT: compare with the data
        want = set(expected[gid]["books"])
        got_ot = set(enabled)
        check(f"{title}: enabled books match its questions ({len(enabled)} of {n} in OT list)",
              got_ot.issubset(want) and len(got_ot) == len([b for b in want if b in set(page.evaluate("OT_BOOKS"))]),
              f"enabled={sorted(got_ot)[:8]} want={sorted(want)[:8]}")
        # a greyed-out book cannot be clicked
        disabled_name = next((tiles.nth(k).inner_text() for k in range(n) if not tiles.nth(k).is_enabled()), None)
        if disabled_name:
            dis = page.locator(".tile", has_text=disabled_name).first
            check(f"{title}: greyed-out book '{disabled_name}' is disabled", dis.is_disabled())
        page.click("text=Back")
        page.wait_for_timeout(150)

    # --- run a real game for Genesis and Jonah, and check no notice shows for a covered book
    for gid_title, book in [("Memory Verse", "Genesis"), ("Bible Trivia", "Genesis"), ("Who Said It", "Genesis"), ("Memory Verse", "Jonah"), ("Bible Trivia", "Revelation"), ("Word Search", "Matthew") if False else ("Bible Trivia", "Matthew")]:
        idx = game_titles.index(gid_title)
        page.evaluate("home()"); page.wait_for_selector(".gcard")
        page.locator(".gcard").nth(idx).click()
        page.wait_for_selector("text=Start", timeout=5000)
        page.click("text=Start")
        page.wait_for_selector(".tile", timeout=5000)
        if page.evaluate("NT_BOOKS.includes(%r)" % book):
            page.click("text=New Testament"); page.wait_for_timeout(120)
        page.locator(".tile", has_text=book).first.click()
        page.wait_for_timeout(400)
        html = page.inner_html("#stage")
        check(f"{gid_title} / {book}: no 'still being prepared' notice", "still being prepared" not in html)
        check(f"{gid_title} / {book}: a question is shown", len(page.inner_text("#stage")) > 40)
        page.evaluate("home()")
        page.wait_for_timeout(150)

    check("no page errors during the run", not errors, "; ".join(errors[:3]))
    browser.close()

passed = sum(1 for _, ok, _ in results if ok)
print(f"\n{passed}/{len(results)} checks passed")
print("page errors:", len(errors), "| console errors:", len(console_err))

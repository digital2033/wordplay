"""
Game scope checks, in a real browser:
  - after Start, the player chooses: whole Bible, New Testament, Old Testament, or book(s)
  - a random option is greyed out when a game has no questions in that part of the Bible
  - random questions come only from the chosen part of the Bible
  - choosing several books draws questions only from those books
"""
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
    pg.fill("#pf-name", "Scope"); pg.click("#pf-save"); pg.wait_for_selector(".gcard")

    def open_game(title):
        pg.evaluate("home()"); pg.wait_for_selector(".gcard")
        idx = pg.evaluate(f"GAMES.findIndex(g => g.title === {title!r})")
        pg.locator(".gcard").nth(idx).click()
        pg.wait_for_selector("text=Start", timeout=5000)
        pg.click("text=Start")

    open_game("Memory Verse")
    labels = pg.locator(".scope-btn").all_inner_texts()
    check("scope screen shows the four options", len(labels) == 4, str(labels))
    check("the choices are whole Bible, New Testament, Old Testament and book(s)",
          any("whole Bible" in l for l in labels) and any("New Testament" in l for l in labels)
          and any("Old Testament" in l for l in labels) and any("book(s)" in l for l in labels))
    check("no book list before the player chooses books", pg.locator(".tile").count() == 0)

    # random whole Bible starts directly, with a question
    pg.locator(".scope-btn", has_text="whole Bible").click()
    pg.wait_for_timeout(300)
    check("random whole Bible shows a question", pg.locator("#stage input.blank").count() > 0 or len(pg.inner_text("#stage")) > 40)
    check("random whole Bible shows no 'still being prepared' notice", "still being prepared" not in pg.inner_html("#stage"))

    # each random option is greyed out exactly when the game has no questions in that part of the Bible
    grey_ok = True; detail = []
    for title in ["Echo", "Scene Detective", "Story Builder", "Bible Characters", "Bible Crossword", "Word Search", "Who Said It"]:
        open_game(title)
        for scope, label in [("NT", "New Testament"), ("OT", "Old Testament")]:
            btn = pg.locator(".scope-btn", has_text=label)
            expect_ok = pg.evaluate(f"gameBankFor(GAMES.find(g => g.title === {title!r}).id).some(x => TEST(x.book) === '{scope}')")
            disabled = btn.is_disabled()
            if disabled == expect_ok:
                grey_ok = False; detail.append(f"{title}/{scope}")
        pg.evaluate("home()")
    check("random options are greyed out exactly when a game has no questions there", grey_ok, ", ".join(detail))

    # random questions stay inside the chosen part of the Bible
    pg.evaluate("startScope('OT', [])")
    ot_ok = pg.evaluate("pickMany(BIBLE_CHARS, 20).every(c => TEST(c.book) === 'OT') && pickMany(MEMORY, 20).every(m => TEST(m.book) === 'OT')")
    check("random Old Testament draws only Old Testament questions", ot_ok)
    pg.evaluate("startScope('NT', [])")
    nt_ok = pg.evaluate("pickMany(BIBLE_CHARS, 20).every(c => TEST(c.book) === 'NT') && pickMany(MEMORY, 20).every(m => TEST(m.book) === 'NT')")
    check("random New Testament draws only New Testament questions", nt_ok)

    # several books chosen by the player
    pg.evaluate("home()")
    open_game("Memory Verse")
    pg.locator(".scope-btn", has_text="book(s)").click()
    pg.wait_for_selector(".tile")
    pg.locator(".tile", has_text="Genesis").first.click()
    pg.locator(".tile", has_text="Exodus").first.click()
    check("two books can be ticked", pg.locator(".tile.on").count() == 2)
    pg.locator("button", has_text="Start with 2 books").click()
    pg.wait_for_timeout(300)
    multi_ok = pg.evaluate("pickMany(MEMORY, 5).every(m => ['Genesis','Exodus'].includes(m.book))")
    check("questions come only from the chosen books", multi_ok)
    check("the game uses both books", pg.evaluate("ctx.books.join(',')") == "Genesis,Exodus")

    check("no page errors", not errors, "; ".join(errors))
    b.close()
print(f"\n{sum(results)}/{len(results)} scope checks passed")

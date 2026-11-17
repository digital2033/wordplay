"""Crossword: typing moves to the next box, Backspace goes back, and Check Answers shows the correct answers."""
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
    pg.fill("#pf-name", "Cross"); pg.click("#pf-save"); pg.wait_for_selector(".gcard")
    pg.evaluate("ctx = { scope: 'all', books: [], book: 'Joshua', testament: 'OT' }; runCrossword()")
    boxes = pg.locator(".xc input")
    check("crossword has boxes", boxes.count() > 10, str(boxes.count()))
    first = boxes.nth(0); first.click(); first.type("A")
    check("typing one letter moves to the next box", pg.evaluate("document.activeElement.dataset.key") == pg.evaluate("document.querySelectorAll('.xc input')[1].dataset.key"))
    pg.keyboard.type("B")
    check("typing again moves on again", pg.evaluate("document.querySelectorAll('.xc input')[2] === document.activeElement"))
    pg.keyboard.press("Backspace")
    pg.keyboard.press("Backspace")
    check("Backspace in an empty box goes back", pg.evaluate("document.querySelectorAll('.xc input')[0] === document.activeElement"))
    check("the Down list is present", pg.locator("text=Down").count() > 0)
    check("Across and Down clue lists both shown", pg.locator(".clues ul.xw-clues").count() == 2)
    pg.click("#xw-check")
    pg.wait_for_timeout(200)
    res = pg.inner_text("#xw-res")
    check("Check Answers shows the correct answers", ("Correct answers" in res) and ("across" in res.lower() or "down" in res.lower()), res[:200])
    filled = pg.evaluate("[...document.querySelectorAll('.xc input')].every(i => i.value === i.dataset.a)")
    check("wrong and empty boxes show the correct letters", filled)
    check("clue lists do not add their own 1, 2, 3 numbering", pg.locator(".clues ol").count() == 0)
    check("no page errors", not errors, "; ".join(errors))
    b.close()
print(f"\n{sum(results)}/{len(results)} crossword checks passed")

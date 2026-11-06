"""
Safety and storage checks, in a real browser:
  - question and memory text is shown as text, never as HTML
  - a full storage shows a warning instead of failing silently
  - unreadable saved data is kept and the player is told
  - progress can be exported
  - the skip link exists
"""
import os
from playwright.sync_api import sync_playwright

URL = os.environ.get("WORDPLAY_URL", "http://localhost:8800/index.html")
results = []
def check(name, ok, detail=""):
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + name + ("" if ok or not detail else "  - " + detail))

with sync_playwright() as p:
    b = p.chromium.launch()

    # 1. HTML in content is shown as text
    pg = b.new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(URL, wait_until="networkidle")
    pg.fill("#pf-name", "Safe"); pg.click("#pf-save"); pg.wait_for_selector(".gcard")
    pg.evaluate("""() => runQuestions([{ q: '<img src=x onerror="window.__xss=1">Who?', options: ['A','B'], correct: 0, note: '' }], () => {})""")
    check("question text is escaped (no injected image)", pg.locator("#stage img").count() == 0)
    check("injected script did not run", pg.evaluate("window.__xss === undefined"))
    pg.evaluate("""() => { ctx = { book: 'Genesis', testament: 'OT' }; MEMORY.unshift({ book: 'Genesis', ref: 'Test 1:1', template: '<img src=x onerror="window.__xss2=1"> [[word]] end' }); runMemory(); }""")
    check("memory verse text is escaped", pg.locator("#stage img").count() == 0 and pg.evaluate("window.__xss2 === undefined"))
    check("no page errors in the safety run", not errors, "; ".join(errors))
    pg.close()

    # 2. Storage full: a warning, and the game keeps working
    ctx_full = b.new_context()
    ctx_full.add_init_script("""
        const realSet = Storage.prototype.setItem;
        Storage.prototype.setItem = function(k, v) {
          if (window.__full) throw new DOMException('QuotaExceededError');
          return realSet.call(this, k, v);
        };""")
    pg = ctx_full.new_page()
    pg.goto(URL, wait_until="networkidle")
    pg.fill("#pf-name", "Full"); pg.click("#pf-save"); pg.wait_for_selector(".gcard")
    pg.evaluate("window.__full = true")
    pg.evaluate("saveDB()")
    msg = pg.inner_text("#toast")
    check("storage full shows a warning", "Could not save your progress" in msg, msg)
    check("the page still works after a failed save", pg.locator(".gcard").count() == 10)
    ctx_full.close()

    # 3. Unreadable saved data: kept as a copy, and the player is told
    ctx_bad = b.new_context()
    pg = ctx_bad.new_page()
    pg.goto(URL, wait_until="domcontentloaded")
    key = pg.evaluate("KEY")
    pg.evaluate(f"localStorage.setItem({key!r}, '{{not json')")
    pg.reload(wait_until="networkidle")
    msg = ""
    try:
        pg.wait_for_function("document.getElementById('toast').innerText.length > 0", timeout=4000)
        msg = pg.inner_text("#toast")
    except Exception:
        pass
    kept = pg.evaluate(f"localStorage.getItem({key!r} + '.damaged')")
    check("unreadable saved data is kept as a copy", kept == "{not json", str(kept))
    check("the player is told their data could not be read", "could not be read" in msg, msg)
    ctx_bad.close()

    # 4. Export progress
    ctx_ex = b.new_context(accept_downloads=True)
    pg = ctx_ex.new_page()
    pg.goto(URL, wait_until="networkidle")
    pg.fill("#pf-name", "Export"); pg.click("#pf-save"); pg.wait_for_selector(".gcard")
    pg.evaluate("showProgress()")
    with pg.expect_download() as dl:
        pg.click("text=Export my progress")
    d = dl.value
    check("export downloads a progress file", d.suggested_filename.startswith("wordplay-progress-") and d.suggested_filename.endswith(".json"), d.suggested_filename)
    ctx_ex.close()

    # 5. Skip link
    pg = b.new_page()
    pg.goto(URL, wait_until="networkidle")
    check("skip link exists and points to the games", pg.locator("a.skip-link[href='#stage']").count() == 1)
    b.close()

print(f"\n{sum(results)}/{len(results)} safety checks passed")

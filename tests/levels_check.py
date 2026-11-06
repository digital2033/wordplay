import os
from playwright.sync_api import sync_playwright
errors = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 390, "height": 844})
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(os.environ.get("WORDPLAY_URL", "http://localhost:8800/index.html"), wait_until="networkidle")
    pg.fill("#pf-name", "Lvl"); pg.click("#pf-save"); pg.wait_for_selector(".gcard"); pg.wait_for_timeout(400)
    results = {}
    for level in ["easy", "medium", "hard"]:
        pg.evaluate(f"setLevel('{level}')")
        out = {}
        out["lives (trivia)"] = pg.evaluate("(() => { bq = null; return DIFFICULTY[levelName()].lives; })()")
        # trivia: options shown per question
        pg.evaluate("ctx = { book: 'Genesis', testament: 'OT' }; pickingGame = 1; pickingFormat='x'")
        pg.evaluate("bq = null; ctx = { book: 'Genesis', testament: 'OT' }; runBibleQuiz(); bq.i = 0")
        pg.evaluate("document.getElementById('bq-go').click()")
        opts = pg.evaluate("document.querySelectorAll('#bq-opts button').length")
        out["trivia options"] = opts
        out["trivia lives shown"] = pg.evaluate("bq.lives")
        out["trivia lifelines"] = pg.evaluate("bq.fifty && bq.hint")
        # crossword word count
        pg.evaluate("ctx = { book: 'Joshua', testament: 'OT' }; runCrossword()")
        out["crossword words"] = pg.evaluate("document.querySelectorAll('.xc input').length > 0 ? DIFFICULTY[levelName()].words : 0")
        pg.evaluate("ctx = { book: 'Joshua', testament: 'OT' }; runWordSearch()")
        out["word search words"] = pg.evaluate("document.querySelectorAll('.wsw').length")
        # memory blanks
        pg.evaluate("ctx = { book: 'Genesis', testament: 'OT' }; runMemory()")
        out["memory blanks"] = pg.evaluate("document.querySelectorAll('input.blank').length")
        # echo key points
        pg.evaluate("ctx = { book: 'Exodus', testament: 'OT' }; runEchoText()")
        out["echo key points shown"] = pg.evaluate("document.getElementById('stage').innerText.includes('Key points')")
        results[level] = out
        pg.evaluate("home()")
    b.close()
for k in ["lives (trivia)", "trivia options", "trivia lives shown", "trivia lifelines", "word search words", "memory blanks", "echo key points shown"]:
    print(f"{k:22}", "  ".join(f"{lv}={results[lv][k]}" for lv in ["easy", "medium", "hard"]))
print("page errors:", errors or "none")

import os
from playwright.sync_api import sync_playwright
page_errors = []
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.on("pageerror", lambda e: page_errors.append(str(e)))
    pg.goto(os.environ.get("WORDPLAY_URL", "http://localhost:8800/index.html"), wait_until="networkidle")
    pg.fill("#pf-name", "Deep"); pg.click("#pf-save"); pg.wait_for_selector(".gcard")
    games = pg.evaluate("GAMES.map((g,i)=>({i, id:g.id, title:g.title, noBook:!!g.noBook, formats:g.formats.map(f=>f.key), tags:g.formats.map(f=>f.tag)}))")
    runs = 0; problems = []
    for g in games:
        if g["noBook"]:
            for key in g["formats"]:
                pg.evaluate(f"pickingGame={g['i']}; pickingFormat='{key}'; playGame()")
                txt = pg.inner_text("#stage")
                runs += 1
                if len(txt) < 30 or "undefined" in txt or "NaN" in txt: problems.append(f"{g['title']}/{key}: short or broken screen")
                pg.evaluate("home()")
            continue
        books = pg.evaluate(f"[...booksWithContent('{g['id']}')]")
        for key in g["formats"]:
            for book in books:
                pg.evaluate(f"pickingGame={g['i']}; pickingFormat='{key}'")
                pg.evaluate(f"startModule({book!r})")
                txt = pg.inner_text("#stage")
                runs += 1
                if "still being prepared" in txt:
                    problems.append(f"{g['title']}/{key}/{book}: notice shown")
                if len(txt) < 30 or "undefined" in txt or "NaN" in txt or "[object" in txt:
                    problems.append(f"{g['title']}/{key}/{book}: short or broken screen")
                pg.evaluate("home()")
    b.close()
print(f"runs: {runs}")
print(f"page errors: {len(page_errors)}  {page_errors[:3]}")
print(f"problems: {len(problems)}")
for x in problems[:15]: print("  -", x)
print("RESULT:", "PASS" if not page_errors and not problems else "CHECK")

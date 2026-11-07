"""
Export every question in Wordplay to content/question-list.csv (one row per question or prompt),
and write content/question-summary.md (counts by game and by book).

The questions are read from the game itself in a headless browser, so the list always matches
what players see. Run it after changing any content, then send the CSV to the partner reviewers.

Usage: python3 scripts/export_question_list.py [http://localhost:8800/index.html]
(start the game first: python3 -m http.server 8800)
"""
import csv
import json
import os
import sys
from collections import Counter, defaultdict
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8800/index.html"
OUT_CSV = os.path.join("content", "question-list.csv")
OUT_MD = os.path.join("content", "question-summary.md")

DUMP = """() => ({
  trivia: BIBLE_QUIZ, memory: MEMORY, who: WHO_SAID, echo: ECHO, chars: BIBLE_CHARS,
  puzzles: PUZZLE_BANK, story: STORY, scene: SCENE, covenant: COVENANT
})"""

def opts(o):
    return " | ".join(o or [])

rows = []
def add(game, book, ref, kind, prompt, options="", answer="", notes=""):
    rows.append({"Game": game, "Book": book, "Reference": ref, "Type": kind,
                 "Question or prompt": prompt, "Options": options, "Answer": answer, "Notes": notes})

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    pg.goto(URL, wait_until="networkidle")
    pg.fill("#pf-name", "Export"); pg.click("#pf-save"); pg.wait_for_selector(".gcard")
    pg.wait_for_timeout(500)
    data = pg.evaluate(DUMP)
    b.close()

for x in data["trivia"]:
    ans = x["options"][x["correct"]]
    add("Bible Trivia", x["book"], x.get("ref", ""), "Multiple choice", x["q"], opts(x["options"]), ans, x.get("info", ""))
for x in data["memory"]:
    blanks = [w for w in __import__("re").findall(r"\[\[(.+?)\]\]", x["template"])]
    text = __import__("re").sub(r"\[\[(.+?)\]\]", "____", x["template"])
    add("Memory Verse", x["book"], x["ref"], "Fill the blanks", text, "", " | ".join(blanks))
for x in data["who"]:
    add("Who Said It", x["book"], x.get("note", ""), "Choose the speaker", f'Who said: "{x["quote"]}"?', opts(x["options"]), x["options"][x["correct"]])
for x in data["echo"]:
    add("Echo", x["book"], x["ref"], "Passage and retelling", x["title"],
        "", "", "Key points: " + " / ".join(e["label"] for e in x["elements"]) + " || Heart: " + x["heart"] + " || Mission: " + x["mission"])
for x in data["chars"]:
    for i, c in enumerate(x["clues"], 1):
        add("Bible Characters", x["book"], x["ref"], f"Clue {i} of {len(x['clues'])}", c, "", x["name"] if i == len(x["clues"]) else "", x.get("info", "") if i == 1 else "")
for x in data["puzzles"]:
    for w in x["words"]:
        add("Crossword and Word Search", x["book"], x["title"], "Word and clue", w["clue"], "", w["w"])
for x in data["story"]:
    add("Story Builder", x["book"], x["ref"], "Put the cards in order", x["title"], "",
        " / ".join(x["cards"]), "Heart: " + x["heart"] + " || Mission: " + x["mission"])
for x in data["scene"]:
    for q in x["questions"]:
        add("Scene Detective", x["book"], x["ref"], "Multiple choice", q["q"], opts(q["options"]), q["options"][q["correct"]], q.get("note", ""))
for x in data["covenant"]:
    add("Covenant Quest", "Covenant film", x["ref"], "Multiple choice", x["q"], opts(x["options"]), x["options"][x["correct"]], x.get("note", ""))

os.makedirs("content", exist_ok=True)
with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

by_game = Counter(r["Game"] for r in rows)
by_book = defaultdict(Counter)
for r in rows:
    by_book[r["Game"]][r["Book"]] += 1
with open(OUT_MD, "w", encoding="utf-8") as f:
    f.write("# Wordplay question summary\n\n")
    f.write(f"Total rows in question-list.csv: **{len(rows)}**\n\n")
    f.write("| Game | Rows | Books |\n|---|---:|---:|\n")
    for g, n in by_game.most_common():
        f.write(f"| {g} | {n} | {len(by_book[g])} |\n")
    f.write("\nRows are one question, clue, word or prompt. Partner reviewers should check every row in the CSV.\n")
print(f"Wrote {OUT_CSV}: {len(rows)} rows")
for g, n in by_game.most_common():
    print(f"  {g:28} {n:6}  books: {len(by_book[g])}")

"""
LIVE check of the shared leaderboard and analytics, against the deployed site and the real Firebase project.
Do NOT run this in the publishing workflow: it writes real data to your Firestore database.

It does this:
  1. opens the site and creates a test player
  2. turns on anonymous usage sharing, and checks that Firebase Analytics starts
  3. shares a test score with the nickname "Live Test", and checks that it appears in the shared leaderboard
  4. stops sharing, and checks that the test score is removed

Run:  WORDPLAY_URL=https://<your-account>.github.io/wordplay/ python3 tests/firebase_live_check.py
"""
import os, sys
from playwright.sync_api import sync_playwright

URL = os.environ.get("WORDPLAY_URL")
if not URL:
    sys.exit("Set WORDPLAY_URL to the deployed site address.")
results = []
def check(name, ok, detail=""):
    results.append(ok); print(("PASS " if ok else "FAIL ") + name + ("" if ok or not detail else "  - " + detail))

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(URL, wait_until="networkidle")
    pg.fill("#pf-name", "Live Tester"); pg.click("#pf-save"); pg.wait_for_selector(".gcard")

    # 1. analytics: Firebase loads after consent
    pg.evaluate("setAnalytics('yes')")
    started = False
    try:
        started = pg.evaluate("(async () => { const a = await loadAnalytics(); return !!a; })()")
    except Exception as e:
        errors.append(str(e))
    check("Firebase Analytics starts after consent", started, "check the API key restriction, and that the Firebase config matches")

    # 2. shared leaderboard: share a test score, and see it in the live list
    pg.evaluate("go('board')")
    pg.fill("#lb-nick", "Live Test")
    pg.check("#lb-agree")
    pg.click("text=Share my score")
    try:
        pg.wait_for_selector("#lb-table >> text=Live Test", timeout=30000)
        shown = True
    except Exception:
        shown = False
    check("test score appears in the shared leaderboard", shown, "check the Firestore rules, anonymous sign-in, and the browser console")

    # 3. stop sharing, and check the score is removed
    pg.click("text=Stop sharing and remove my score")
    try:
        pg.wait_for_selector("#lb-table >> text=Live Test", state="detached", timeout=30000)
        removed = True
    except Exception:
        removed = False
    check("stopping removes the test score", removed)

    check("no page errors", not errors, "; ".join(errors[:3]))
    b.close()
print(f"\n{sum(results)}/{len(results)} live checks passed")
sys.exit(0 if all(results) else 1)

"""
Analytics and consent checks, in a real browser.
Firebase is replaced by a stand-in module, so no real data is sent.
  - before consent: no Firebase request and no events
  - after consent: events are sent, with no names or typed text
  - child-directed settings are passed to analytics
  - saying no stops the events
  - if Firebase cannot be reached, the game still works
  - the leaderboard shows each player's status on this device
"""
import os
from playwright.sync_api import sync_playwright

URL = os.environ.get("WORDPLAY_URL", "http://localhost:8800/index.html")
STUB = """
export function initializeApp(c){ return { config: c }; }
export function getAnalytics(app, opts){ window.__analyticsOpts = opts; return { app }; }
export function logEvent(inst, name, params){ (window.__events = window.__events || []).push({ name, params }); }
"""
firebase_requests = []
results = []
def check(name, ok, detail=""):
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + name + ("" if ok or not detail else "  - " + detail))

def route_firebase(route):
    firebase_requests.append(route.request.url)
    route.fulfill(status=200, content_type="application/javascript", body=STUB)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.route("https://www.gstatic.com/**", route_firebase)
    pg.goto(URL, wait_until="networkidle")
    pg.fill("#pf-name", "Priya"); pg.click("#pf-save"); pg.wait_for_selector(".gcard")

    # 1. Before consent
    check("consent card is shown before any choice", pg.locator("h3", has_text="Help improve Wordplay").count() == 1)
    pg.evaluate("track('test_before_consent', {})")
    pg.evaluate("finishModule('Echo', 2, 3, null)")
    pg.wait_for_timeout(300)
    check("no Firebase request before consent", len(firebase_requests) == 0, str(firebase_requests[:2]))
    check("no events recorded before consent", pg.evaluate("(window.__events||[]).length") == 0)
    pg.evaluate("home()"); pg.wait_for_selector(".gcard")

    # 2. Yes
    pg.locator("button", has_text="Yes, share anonymous usage").click()
    pg.wait_for_timeout(800)
    check("consent card goes away after a choice", pg.locator("h3", has_text="Help improve Wordplay").count() == 0)
    check("Firebase loads after consent", any("firebase-app" in u for u in firebase_requests) and any("firebase-analytics" in u for u in firebase_requests))
    check("analytics runs in child-directed mode (no Google Signals, no ad personalisation)",
          pg.evaluate("window.__analyticsOpts && window.__analyticsOpts.config.allow_google_signals === false && window.__analyticsOpts.config.allow_ad_personalization_signals === false"))

    pg.evaluate("pickingGame = 0; pickingFormat = 'text'; playGame()")
    pg.evaluate("finishModule('Echo', 2, 3, null)")
    pg.wait_for_timeout(500)
    events = pg.evaluate("window.__events || []")
    names = [e["name"] for e in events]
    check("game events are recorded after consent", "game_finished" in names and "game_started" in names, str(names))
    allowed = {"game", "format", "level", "head", "max"}
    bad = [e for e in events if not set((e["params"] or {}).keys()) <= allowed]
    check("events contain only game, format, level and points", not bad, str(bad[:1]))
    text = str(events)
    check("no player name in any event", "Priya" not in text)

    # 3. Leaderboard status
    pg.evaluate("showBoard()")
    check("leaderboard shows the player's own status", pg.locator("h3", has_text="your status on this device").count() == 1)

    # 4. Saying no stops the events
    pg.evaluate("setAnalytics('no')")
    pg.wait_for_timeout(200)
    before = len(pg.evaluate("window.__events || []"))
    pg.evaluate("finishModule('Echo', 1, 3, null)")
    pg.wait_for_timeout(300)
    check("no events after saying no", len(pg.evaluate("window.__events || []")) == before)
    b.close()

# 5. If Firebase cannot be reached, the game still works
b2 = None
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.route("https://www.gstatic.com/**", lambda route: route.abort())
    pg.goto(URL, wait_until="networkidle")
    pg.fill("#pf-name", "Offline"); pg.click("#pf-save"); pg.wait_for_selector(".gcard")
    pg.evaluate("setAnalytics('yes')")
    pg.wait_for_timeout(800)
    pg.evaluate("finishModule('Echo', 2, 3, null)")
    pg.evaluate("home()"); pg.wait_for_selector(".gcard")
    check("game works when Firebase is unreachable", pg.locator(".gcard").count() == 10 and not errors, "; ".join(errors))
    b.close()

print(f"\n{sum(results)}/{len(results)} analytics checks passed")

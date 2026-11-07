"""
Shared leaderboard checks, in a real browser. Firebase is replaced by a stand-in,
so nothing is sent. The security rules themselves must be tested with the Firebase emulator.
  - nothing is sent before a player agrees
  - the nickname is validated, and the real name is never sent
  - a score is published after a game, with the nickname only
  - the top list is shown, and nicknames are escaped
  - stopping removes the score
"""
import os
from playwright.sync_api import sync_playwright

URL = os.environ.get("WORDPLAY_URL", "http://localhost:8800/index.html")
results = []
def check(name, ok, detail=""):
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + name + ("" if ok or not detail else "  - " + detail))

APP = "export function initializeApp(c, n){ return { name: n }; }"
AUTH = """export function getAuth(app){ return (window.__auth = window.__auth || { currentUser: null }); }
export function signInAnonymously(auth){ auth.currentUser = { uid: 'browser1' }; return Promise.resolve({ user: auth.currentUser }); }"""
FS = """
window.__store = window.__store || {};
export function getFirestore(app){ return {}; }
export function doc(db, col, id){ return { col, id }; }
export function collection(db, col){ return { col }; }
export function orderBy(f, d){ return { f, d }; }
export function limit(n){ return { n }; }
export function query(c, ...cons){ return { c, cons }; }
export function serverTimestamp(){ return 'TS'; }
export function setDoc(ref, data){ window.__store[ref.id] = data; window.__writes = (window.__writes || []); window.__writes.push({ id: ref.id, data }); return Promise.resolve(); }
export function deleteDoc(ref){ delete window.__store[ref.id]; window.__deletes = (window.__deletes || 0) + 1; return Promise.resolve(); }
export function getDocs(q){
  const docs = Object.entries(window.__store).map(([id, d]) => ({ id, data: () => d }))
    .sort((a, b) => b.data().points - a.data().points).slice(0, q.cons.find(c => c.n).n);
  return Promise.resolve({ docs });
}
"""
ANA = "export function getAnalytics(app, o){ return {}; } export function logEvent(){}"
requests = []
def route(r):
    u = r.request.url; requests.append(u)
    body = APP if "firebase-app" in u else AUTH if "firebase-auth" in u else FS if "firebase-firestore" in u else ANA
    r.fulfill(status=200, content_type="application/javascript", body=body)

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.route("https://www.gstatic.com/**", route)
    pg.goto(URL, wait_until="networkidle")
    pg.fill("#pf-name", "Priya Sharma"); pg.click("#pf-save"); pg.wait_for_selector(".gcard")

    pg.evaluate("go('board')")
    check("share form is shown before agreeing", pg.locator("#lb-nick").count() == 1)
    check("nothing sent to the leaderboard before agreeing", not any("firebase" in u for u in requests))

    # invalid nickname: the real name is not allowed
    pg.evaluate("document.getElementById('lb-nick').value = '<b>Priya</b>'")
    pg.evaluate("document.getElementById('lb-agree').checked = true")
    pg.evaluate("shareScore()")
    check("invalid nickname is refused", "Use 2 to 20" in pg.inner_text("#lb-msg"))
    check("nothing published for an invalid nickname", not pg.evaluate("window.__writes || []").__len__())

    # valid nickname, agreed
    pg.evaluate("document.getElementById('lb-nick').value = 'Joy Seeker'")
    pg.evaluate("shareScore()")
    pg.wait_for_timeout(800)
    writes = pg.evaluate("window.__writes || []")
    check("score published with the nickname", len(writes) >= 1 and writes[-1]["data"]["nickname"] == "Joy Seeker", str(writes[-1:]))
    check("real name is never sent", all("Priya" not in str(w) for w in writes))
    check("entry is owned by the browser and player", writes and writes[-1]["id"].startswith("browser1_"))
    check("only the allowed fields are sent", writes and set(writes[-1]["data"].keys()) == {"nickname", "points", "level", "games", "updated"})

    # another player's score, to test the top list and escaping
    pg.evaluate("window.__store['browser2_x1'] = { nickname: '<img src=x onerror=\"window.__xss=1\">', points: 9999, level: 'Champion', games: 40, updated: 'TS' }")
    pg.evaluate("showBoard()"); pg.wait_for_timeout(600)
    table = pg.inner_text("#lb-table")
    check("top list shows shared scores", "Joy Seeker" in table and "9999" in table)
    check("nicknames are shown as text, not HTML", pg.locator("#lb-table img").count() == 0 and pg.evaluate("window.__xss === undefined"))

    # stop sharing
    pg.evaluate("stopSharing()"); pg.wait_for_timeout(600)
    check("stopping removes the score", "browser1_" not in str(pg.evaluate("Object.keys(window.__store)")))
    check("sharing is off after stopping", pg.evaluate("DB.settings.shared") == "no")
    check("no page errors", not errors, "; ".join(errors))
    b.close()

print(f"\n{sum(results)}/{len(results)} leaderboard checks passed")

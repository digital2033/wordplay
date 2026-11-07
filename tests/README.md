# Browser tests

These tests open Wordplay in a real Chromium browser and play through it.

## Run them

1. Serve the game folder:
   `python3 -m http.server 8800` (from the `wordplay-game` folder)
2. Install the test tools once:
   `pip install playwright && python3 -m playwright install chromium`
3. Run:
   `python3 tests/browser_check.py` (about 1 minute): checks the home page, filters, every game's book picker against its questions, and a sample of games.
   `python3 tests/deep_check.py` (a few minutes): runs every game, every format and every book that has questions, and checks each screen.
   `python3 tests/levels_check.py`: checks Easy, Medium and Hard.
   `python3 tests/safety_check.py`: checks escaping, storage warnings, damaged-data recovery, export and the skip link.
   `python3 tests/leaderboard_check.py`: checks the shared leaderboard (opt-in, nickname only, top list, stop sharing). Firebase is replaced by a stand-in.
   `python3 tests/about_check.py`: checks the About page.
   `python3 tests/scope_check.py`: checks the choice after Start (whole Bible, New or Old Testament, or chosen books), greyed-out options, and that questions stay in scope.
   `python3 tests/analytics_check.py`: checks consent, events (no names), child-directed settings, and that the game works if Firebase is unreachable. Firebase is replaced by a stand-in, so no real data is sent.

To test a published site instead of a local one, set `WORDPLAY_URL`, for example
`WORDPLAY_URL=https://<your-account>.github.io/wordplay/ python3 tests/browser_check.py`.

The tests need a clean profile each time they run. They create a test player named "Tester" or "Deep".

## Live Firebase check (not part of the workflow)

`WORDPLAY_URL=https://<your-account>.github.io/wordplay/ python3 tests/firebase_live_check.py` runs the shared leaderboard and analytics against your real Firebase project. It writes a test entry and then removes it. See FIREBASE-SETUP.md.

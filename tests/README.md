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

To test a published site instead of a local one, set `WORDPLAY_URL`, for example
`WORDPLAY_URL=https://<your-account>.github.io/wordplay/ python3 tests/browser_check.py`.

The tests need a clean profile each time they run. They create a test player named "Tester" or "Deep".

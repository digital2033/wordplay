# Developer guide

How the project is organised, and how to change it.

---

## Project layout

| Path | What it is |
|---|---|
| `index.html` | The whole game: screens, games, scoring, Bible engine, styles. One file, no build step. |
| `config.json` | Public settings: app name, media server address, media paths, feature switches. |
| `manifest.webmanifest` | App name, icons and install settings for the Progressive Web App. |
| `sw.js` | Service worker: caches the app so it works offline. |
| `icons/` | App icons (192 and 512 pixels). |
| `default-bible/en-kjv.json.gz` | The embedded King James Version (built-in English). |
| `bible-catalog.json` | Bible versions for the optional build-time downloads. |
| `game-chapters.json` | The chapters used by the optional build-time text download. |
| `offline-audio.json` | The chapters for the optional build-time audio download. |
| `scripts/` | Build and conversion scripts (see below). |
| `.github/workflows/` | GitHub Actions: publishing, and the manual Bible Brain discovery check. |
| `README.md` | The overview for players and partners. |
| `DEPLOYMENT.md` | Publishing and the optional media set-up. |
| `CHANGELOG.md` | Version history. |

There is no build tool, package manager or framework. Open `index.html` in a text editor.

---

## How `index.html` is organised

The script is one block inside `<script>`. In order:

1. **Configuration** (`CONFIG`): media paths, filled in from `config.json` at start-up.
2. **Interface languages** (`LANGS`, `UI`): one dictionary per language. Missing labels fall back to English.
3. **Bible books** (`OT_BOOKS`, `NT_BOOKS`, and the USFM code list `BOOK_CODE_LIST`).
4. **Content banks**: `ECHO`, `SCENE`, `COVENANT`, `WHO_SAID`, `STORY`, `MEMORY`, `QUICK`, `WHO_AM_I`, `LISTENING`, `PUZZLE_BANK`, `QUIZ_EXTRA`, `BIBLE_CHARS`, and the text used by Echo (`ECHO_TEXT`, `SCENE_NARR`, `COVENANT_SUMMARY`).
5. **Storage and profiles**: `DB` (saved in `localStorage`), players, sessions, `statsFor()`, levels and badges.
6. **Screens**: `showProfile()`, `home()`, `openGame()`, `renderDetail()`, `playGame()`, `renderBookPicker()`, `startModule()`, `finishModule()`, `showProgress()`, `showBoard()`.
7. **Game engines**: one set of functions per game, for example `runEchoText()`, `runWhoSaidText()`, `runCovenantText()`, `runCrossword()`, `runWordSearch()`.
8. **Answer review**: `addReview()` and `reviewHTML()`. Each game records its answers, and the finish screen lists them.
9. **Bible engine**: the built-in English (`loadDefaultBible()`), the chapter store in IndexedDB (`idbPut()`, `idbGet()`), passage lookup (`fetchPassage()`), and the Bible Brain chooser (`renderBiblePicker()` and the `bp*` functions).
10. **Start-up**, last: `loadConfig().then(loadCatalog).then(…)`.

**Important:** keep the start-up call at the end of the script. Functions defined inside a callback are not global, and buttons that call them would fail. This is the most common mistake when editing this file.

Functions whose names begin with `legacy_` are retired code. They are not called, and can be deleted once the new code is confirmed.

### The `GAMES` list

Each game is an entry in `GAMES`:

```js
{ id:"echo", title:"Echo", tagline:"…", about:"…", how:["…"],
  formats:[ {key:"text", label:"Read and retell", tag:"text", run:runEchoText},
            {key:"audio", label:"Listen, then retell", tag:"audio", run:runEchoAudio} ] }
```

- `tag` is `text`, `audio` or `video`. The **Audio**, **Video** and **Text** filters use it.
- A format whose `tag` is switched off in `config.json` (`features`) shows as **Coming soon**.
- `run` is the function that starts the format. It is called with `ctx.book` and `ctx.testament` already set.
- Icons are matched by position: the first game uses `ICONS[0]`, and so on.

---

## Adding a game

1. Write the engine function. It should set the stage with `stage().innerHTML = …`, record each answer with `addReview(question, correctAnswer, isCorrect)`, and finish with `withHH(name, score, max, heartPrompt, missionText)`.
2. Add an entry to `GAMES`, with at least one format.
3. Add an icon: `ICONS.push(\`<svg viewBox="0 0 120 80">…</svg>\`);`, placed before the `MODULES` line.
4. Add the content it needs to a bank, or a new array near the other banks.
5. Check that the game page and filters show it, and that its finish screen lists the answers.

Do not add a game to `MODULES`. It is an older list, kept only while the older code is removed.

---

## Adding a language (interface)

1. Add the code and name to `LANGS`, for example `fr: "Français"`.
2. Add a dictionary `UI.fr = { home:"…", play:"…", … }` with the same keys as `UI.en`. Missing keys fall back to English.
3. Add a font to the `font-family` list in the `body` style if the script needs one.

Game content (questions, passages, clues) is not translated by the app. It needs its own content for each language.

---

## Adding content

- **Echo passages:** add an entry to `ECHO`, with the reference, the key story elements (and their keywords), a Heart prompt and a mission. Add the text to `ECHO_TEXT`, keyed by the book code.
- **Covenant Quest clips:** edit `COVENANT`. Each clip needs a title, a reference, a summary, a question with options, a Heart prompt and a mission.
- **Quiz questions:** add to `QUICK` or `QUIZ_EXTRA`. Each question needs `book` (the USFM code), `q`, `options`, `correct` (the index of the right option), `ref` and `info`.
- **Puzzles:** add to `PUZZLE_BANK`. Words must be capital letters only, with no spaces.
- Keep each reference accurate. Have a partner check every item.

---

## Bible text

- **`default-bible/en-kjv.json.gz`** has this structure:
  `{ "id":"ENGKJV", "name":"…", "books": { "GEN": { "1": [[1, "text"], …] } } }`.
- Rebuild it with `python3 scripts/usx_to_default_bible.py <usx.zip or folder>`. The script checks that all 66 books and 1,189 chapters are present.
- Passages are looked up by `parseRef("Luke 15:11-24")`, which returns the book code, chapter and verse range.
- The chooser stores each downloaded chapter in IndexedDB as `v|<fileset>|<BOOK>|<chapter>`, and each Bible's details as `m|<abbreviation>`. If IndexedDB is not available, the chapters are kept in memory for the session.

---

## Scripts

| Script | Purpose | Needs a key |
|---|---|---|
| `usx_to_default_bible.py` | Converts USX files to the embedded KJV file. | No |
| `build_default_english.py` | Re-downloads the KJV from Bible Brain. Not needed now. | Yes |
| `fetch_offline_audio.py` | Downloads audio chapters for the build (Route A in DEPLOYMENT.md). | Yes |
| `fetch_offline_text.py` | The older build-time text download. Not read by the chooser. | Yes |
| `discover_bible_brain.py` | Manual check of the Bible Brain endpoints. Saves samples as an artifact. | Yes |

Check a script before running it: `python3 -m py_compile scripts/<name>.py`.

---

## Checking the game before a release

There is no automated test suite in the repository yet. Before a release, check:

1. The JavaScript parses: copy the content of the `<script>` block into a file and run `node --check`.
2. `config.json`, `bible-catalog.json`, `game-chapters.json` and `manifest.webmanifest` are valid JSON.
3. Open the game in a browser, sign in, and play one game in each category.
4. Check the answers list at the end of a game.
5. Switch the Bible in Echo, and check that the built-in King James passage still shows.
6. Install the app, go offline, and open it.
7. Bump `CACHE_VERSION` in `sw.js` and record the change in `CHANGELOG.md`.

Recommended: add a `tests/` folder with a headless browser test for these steps.

---

## Known technical notes

- `loadConfig()` reads `config.json` at start-up. If it cannot be read, the game still runs with its defaults.
- The **Bible Brain key** is kept in a variable (`BB_KEY`) for the session only. Do not add it to `DB`, `localStorage` or any file.
- The service worker caches same-origin requests, except `/api/` and `/media/`. Bible chapters downloaded by players are stored in IndexedDB, not in the service worker cache.
- Start-up errors are shown on the page by `showStartError()`, rather than as a blank screen.

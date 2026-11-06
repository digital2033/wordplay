# Changelog

All notable changes to Wordplay are recorded here. Versions follow the form `major.minor`.

## 1.9.0 - Anonymous analytics (opt-in) and personal status

### Added
- **Firebase Analytics, opt-in only.** A consent card on the home page asks players (or a parent or teacher) to choose **Yes** or **No thanks**. The choice can be changed on the Progress screen.
- **Events:** `game_started` and `game_finished`, with game, format, level and points. No names, avatars or typed text are sent.
- **Child-directed settings:** Google Signals and ad personalisation are off.
- **Leaderboard status:** each player's level, points, games, streak, badges and modules on this device.
- `firebase-config.json`: the public Firebase web configuration, separate from `config.json`.
- `tests/analytics_check.py`: 12 checks, with Firebase replaced by a stand-in.

### Changed
- The privacy notice describes the opt-in sharing and the under-13 guidance.
- The publishing workflow runs the analytics check, and publishes `firebase-config.json`.

### Notes
- The leaderboard stays on each device, as chosen.
- Restrict the Firebase API key to your site's address, as set out in DEPLOYMENT.md.
- The stand-in tests do not contact Firebase. Please check that the first real events arrive in the Firebase console after the first deployment.

## 1.8.0 - Ready for a pilot: licence, safety, storage, CI and cleanup

### Added
- **MIT licence** (`LICENSE`), linked from the README.
- **Content disclaimer** on the home page and in the README: content is under partner review, and passages should be checked against the reader's own Bible.
- **Export my progress** on the Progress screen: downloads a JSON copy of players and history.
- **Storage warnings:** if progress cannot be saved, the player is told. If saved data cannot be read, it is kept as `wordplay.v1.damaged` and the player is told.
- **Skip link** and **live region** for messages; labels for the Bible chooser controls.
- **`tests/safety_check.py`:** checks escaping, storage warnings, damaged-data recovery, export and the skip link.
- **`media-server/`:** the media proxy is now part of the project. It trusts one proxy by default (`TRUST_PROXY`), so the rate limit counts real visitors.
- **CI:** the publishing workflow runs the JSON and syntax checks, the question-bank consistency check, and all browser tests in headless Chromium before it deploys.

### Changed
- Question text, memory-verse text, passage titles and session history are escaped before they are shown.
- The service worker is stamped with the commit ID at each deployment, so players receive new content without a manual version bump.
- Audio download needs **both** `DOWNLOAD_AUDIO` and `AUDIO_LICENCE_CONFIRMED` set to `true`.
- The manifest declares the icons separately for `any` and `maskable`.
- `config.json` no longer contains the settings the app does not read (`staticText`, `bibleBrain`).

### Removed
- `DOWNLOAD_TEXT` and `DOWNLOAD_DEFAULT_BIBLE`. Bible text is no longer published at build time, and the English Bible is committed.
- `scripts/fetch_offline_text.py`, `scripts/build_default_english.py`, `bible-catalog.json` and `game-chapters.json`, which only the removed steps used.
- 13 unused functions (the retired chooser and picker, `keepName` and `runOralQuiz`).

### Verified
- Basic browser checks: 35 of 35.
- Levels: all checks pass.
- Safety: 10 of 10.
- Full pass: 728 game screens, no page errors. The only notice left is the known 3 John case.

## 1.7.1 - Characters and word puzzles for the Gospels, Acts, the letters and the historical books

### Added
- `content/extra/05-torah-to-ezra.json`: 25 Bible Characters from Leviticus, Numbers, Judges, 1 and 2 Samuel, 1 and 2 Kings, 1 and 2 Chronicles, Ezra and Nehemiah (Aaron, Balaam, Korah, Deborah, Jephthah, Ehud, Eli, Jonathan, Goliath, Abigail, Joab, Mephibosheth, Ahab, Obadiah, Elisha, Naaman, Josiah, Jehu, Asaph, Jabez, Jehoshaphat, Uzziah, Manasseh, Ezra, Zerubbabel, Nehemiah), and word lists for Leviticus, 2 Kings, 1 and 2 Chronicles, Ezra and Nehemiah.
- `content/extra/06-gospels-acts-pauline.json`: 20 Bible Characters from the Gospels, Acts, Romans and the letters (Herod the Great, Judas Iscariot, James son of Zebedee, Joseph of Arimathea, Martha, Herod Antipas, Caiaphas, Nathanael, Pontius Pilate, Cornelius, Ananias, Silas, Apollos, Philip, Aquila, Stephanas, Titus, Epaphras, Onesimus, Demas, Timothy, Eunice, Philemon), and word lists for 1 and 2 Corinthians, Colossians, 1 and 2 Thessalonians, 1 and 2 Timothy, Titus and Philemon.

### Changed
- Coverage: Bible Characters 40 books (was 27), Bible Crossword 45 (was 30), Word Search 45 (was 30).

### Verified in a real browser (Chromium)
- A full pass ran 728 game screens with no page errors. The only notice left is 3 John in Bible Trivia.
- The basic browser checks pass 35 of 35.
- Every new crossword places at least seven of its ten words. Titus places seven, so on Hard it will show a smaller grid.

## 1.7.0 - Difficulty levels and 14 more books

### Added
- **Three difficulty levels** (Easy, Medium, Hard), chosen on the home page and applied to every game:
  - lives: 5, 3 or 1;
  - multiple choice: 3 options on Easy, 4 on Medium and Hard;
  - lifelines (50:50 and Hint): on Easy and Medium, off on Hard;
  - puzzles: 6, 8 or 10 words;
  - Memory Verse: 2 blanks on Easy, all on Medium and Hard;
  - Echo: key points shown on Easy;
  - Head points multiplied by 1, 1.5 or 2. The level is saved in the history.
- Hand-written content for 14 more books: Numbers, Deuteronomy, Esther, Daniel, Jonah, Job, Proverbs, Luke (word list and Mary), Galatians, Ephesians, Philippians, Hebrews, James and 1 Peter.
- `tests/levels_check.py`: checks each level in a real browser.

### Changed
- Bible Crossword, Word Search and Bible Trivia use the level's settings.
- Coverage: Echo 30 books (was 18), Bible Characters 27 (was 20), Bible Crossword 30 (was 16), Word Search 30 (was 16).

### Verified in a real browser (Chromium)
- The level checks show the expected lives, options, word counts, blanks and Echo hints, with no page errors.
- A deep pass ran 642 game screens with no page errors. The only notice left is 3 John in Bible Trivia.
- The basic browser checks pass 35 of 35.

## 1.6.5 - More hand-written questions for more books

### Added
- `content/extra/`: hand-written content for 16 books (Genesis, Exodus, Joshua, Judges, Ruth, 1 Samuel, 2 Samuel, 1 Kings, Psalms, Isaiah, Matthew, Mark, John, Acts, Romans, Revelation):
  - 16 Echo passages, with story elements and heart and mission prompts,
  - 33 Bible Characters, with clues,
  - 13 word lists for Bible Crossword and Word Search.
- `scripts/merge_extra_content.py`: checks every book name, reference, letter and clue, and merges the files into `content/extra-bank.json`.

### Changed
- Echo picks its passage from the selected book.
- Coverage now: Echo 18 books, Bible Characters 20, Bible Crossword 16, Word Search 16 (previously 2, 9, 3 and 3).

### Verified in a real browser (Chromium)
- The browser checks passed 35 of 35, with no page errors.
- A deep pass ran 548 game screens (every game, every format and every covered book) with no page errors. The only notice left is for 3 John in Bible Trivia.
- Every new crossword places at least seven of its ten words.

## 1.6.4 - Book picker shows only books with questions

### Changed
- The book picker greys out (and disables) every book that has no questions for the chosen game. Each picker shows how many books have questions.
- Scene Detective picks a scene from the selected book, and Bible Characters uses only the selected book's characters.

### Added
- `tests/browser_check.py` and `tests/deep_check.py`: browser tests (Chromium, via Playwright). The first checks the home page, filters, every book picker against its questions, and sample games. The second runs every game, every format and every covered book.

### Verified in a real browser
- 35 of 35 checks passed, with no page errors.
- 442 game runs (every game, every format, every covered book) with no page errors. The only notice left is the 3 John trivia deck, which has nine questions.

## 1.6.3 - Questions for all 66 books (Memory Verse and Bible Trivia)

### Added
- `scripts/build_question_bank.py` and `content/generated-bank.json`: questions for every book, generated from the embedded King James text. Memory Verse: 197 items, Bible Trivia: 1,037 items (all 66 books except 3 John, which has nine), Who Said It: 132 items for 22 books.
- Each generated item records its verse reference.

### Changed
- Memory Verse, Bible Trivia and Who Said It choose questions from the selected book. The old fallback to the nearest book (for example, Jonah for Genesis) only applies to games and books with no content.
- The publishing workflow publishes `content/`, and the service worker caches the question bank.

### Known limits
- The generated questions test wording and reference. Partner review is needed before wide use.
- Echo, Scene Detective, Story Builder, Bible Characters, Bible Crossword and Word Search still have hand-written content for only some books.

## 1.6.2 - Documentation

### Added
- `README.md` rewritten for players and partners: all ten games with their formats and media types, filters, scoring, levels and badges, the Bible text options, languages, offline use, privacy, known limits and credits.
- `DEVELOPER.md`: project layout, how `index.html` is organised, how to add a game, a language, content and Bible text, the scripts, and a release checklist.
- `DEPLOYMENT.md` rewritten: publishing on GitHub Pages, the settings in `config.json`, the built-in Bible, the optional build steps and their variables, and the two audio and video routes.

### Changed
- The optional variables `DOWNLOAD_TEXT` and `DOWNLOAD_DEFAULT_BIBLE` are documented as not needed, since the chooser downloads Bibles itself and the English is committed.

## 1.6.1 - King James Version embedded

### Added
- `default-bible/en-kjv.json.gz`: the complete King James Version (66 books, 1,189 chapters, 31,102 verses, 1.2 MB), made from the USX files supplied for the project. It is part of the app, so the default English works offline with no key.
- `scripts/usx_to_default_bible.py`: converts USX 3.0 files (zip or folder) into the embedded file, and stops if any book or chapter is missing. Used to make the file above; it needs no key.
- The publishing workflow copies `default-bible/` into the site, and the service worker caches the file.

### Notes
- Leave the repository variable `DOWNLOAD_DEFAULT_BIBLE` unset. The embedded file is now committed, so the download step is not needed.
- The other Bibles are still downloaded by the player with their own Bible Brain key.

## 1.6.0 - Bible text on the device (Option A)

### Added
- **Built-in English (King James Version).** `scripts/build_default_english.py` downloads the KJV once at build time (the `BIBLE_BRAIN_KEY` secret) and embeds it as `default-bible/en-kjv.json.gz`. Echo passages use it with no key and no internet. Enable with the repository variable `DOWNLOAD_DEFAULT_BIBLE` = `true`. Until then, Echo uses its short built-in passages.
- **Bible Brain browser.** "Add a Bible from Bible Brain": the player types their own free key (kept in memory only, never saved), chooses a country (all countries from Bible Brain), a language for that country, then a Bible with text. Each testament (OT, NT or complete) is downloaded to the device, one chapter at a time, with progress.
- **Downloaded Bibles** are stored in the browser (IndexedDB), and the Bible for Echo can be switched on the home page. New Testament passages fall back to the built-in English if the downloaded Bible has only the Old Testament.
- The service worker caches the embedded English file when it is present, without stopping the install if it is missing.

### Changed
- Replaces the build-time Bible choice (country, language and version from `bible-catalog.json`). `bible-catalog.json` is still used by the optional build downloads.

### Notes
- Checked by simulation only: the country list, language filter, Bible list, download and reading back of passages. Not yet run against the real Bible Brain API or in a real browser.
- The Bible Brain language filter for Bibles is `language_code` (as OBQ uses), not `iso`.

## 1.5.6 - All countries in the chooser (in progress)

### Changed
- The Country, Language and Version lists are sorted by name, so long lists are easy to scan.

### Planned
- A build step that lists every country from Bible Brain, and the languages for each country, so every country appears in the dropdown and its languages are filtered by the country chosen. The discovery run (round 6) checks the country code format and the per-country language lookup first.

## 1.5.5 - One fileset per testament

### Fixed
- Bible Brain splits most text versions into an Old Testament fileset and a New Testament fileset (for example `MALBCMO_ET` and `MALBCMN_ET`). The old single-ID catalogue (`MALBCM`) returned 404 and was skipped.

### Changed
- `bible-catalog.json`: each version lists `filesets` with `OT` and `NT` IDs (or `C` for a complete fileset). English KJV uses `ENGKJVO_ET` and `ENGKJVN_ET`. Malayalam 1910 uses `MALBCMO_ET` and `MALBCMN_ET`.
- `fetch_offline_text.py` picks the right fileset for each book, and writes the published catalogue with each version's filesets.
- Passages in the game use the OT or NT fileset for the book being read.

## 1.5.4 - Bible Brain catalogue discovery (in progress)

### Found in the third discovery run
- Country-to-language link: `/languages?country=XX` returns the languages spoken in a country, with Bible and fileset counts.
- Filter by language ID works: `/bibles?language_id=N`. The ISO filter `/bibles?iso=` does not, and returns Bibles in other languages.
- Audio chapter route confirmed: `/bibles/filesets/{fileset}/{book}/{chapter}` returns a signed `path` to the audio file, as the media server expects.
- Text chapter route confirmed: `/bibles/filesets/{fileset}/{book}/{chapter}` returns `verse_start` and `verse_text` for text filesets (ENGKJV confirmed).
- The Malayalam fileset `MALBCM` returned 404, so it is not a valid text fileset ID. The English language ID used earlier (6414) returned no Bibles. The next discovery run finds both by ISO code.


### Found in the first discovery run
- Languages: 2,677 in total, each with an ISO code, names, and counts of Bibles and filesets.
- Countries: 227, with codes but no language list.
- Bibles: 3,512 in total. Each lists its language, ISO code and filesets. Filesets have types such as `text_plain` and `audio_drama`, and sizes such as NT or C (complete).
- The `language` filter on /bibles did not reduce the results, so filtering must use another parameter or be done during the build.
- The fileset route used in discovery returned 404, so the chapter route needs confirming.


### Added
- `discover-bible-brain.yml`: a manual workflow that calls the Bible Brain language, country, Bible and fileset endpoints and saves small samples as an artifact. It does not publish anything.

## 1.5.3 - Chooser always visible, Echo audio

### Added
- The Country, Language and Version chooser on the home page now appears as soon as the game opens. It lists every version in `bible-catalog.json`, even before the text is published. Versions not yet published are marked "coming soon", and the built-in text is used for them.
- Echo has an audio version, "Listen, then retell", marked coming soon until audio is connected.

### Changed
- The build publishes every configured version, marked as available or not, in `text/catalog.json`.
- `bible-catalog.json` is published with the site (it holds only IDs and names, no secrets).

## 1.5.2 - Answers shown with points

### Added
- At the end of every game, an Answers list shows each question with the correct answer and a tick or cross for the player's answer. This covers multiple choice, typed answers, Bible Trivia, Bible Characters, Story Builder, Memory Verse, Bible Crossword and Word Search.

## 1.5.1 - Fixes from a full test run

### Fixed
- The game's start-up code had been wrapped around all the game code, so buttons (for example opening a game) would fail. The start-up code now runs last, and every game function is global.
- Two shared helpers (`stage()` and `audioBlock()`) were missing. They are restored.
- Text passages publish in the format the Bible picker reads (`text/catalog.json`).

### Tested
- Every game page and format opens without errors.
- Typed answers are checked, Covenant Quest starts without the book chooser, audio and video formats show "Coming soon" by default, Bible Trivia draws ten questions without repeats, and passage references are parsed correctly.
- The text download was tested against a local stand-in for Bible Brain. It has not yet been run against Bible Brain itself.

## 1.5.0 - Countries, languages and versions

### Added
- Home page menus for **country**, **language** and **version**. Passages (Echo) are read from the version the player chooses.
- `text/catalog.json` is created at build time and lists only the versions that were downloaded.
- `bible-catalog.json` lists countries, languages and versions. A fileset shared by several countries is downloaded once.

### Changed
- The text download script reads the new structure and skips versions with placeholder IDs.
- The Bible text setting on the home page replaces the single language list.

## 1.5.0 - Country, language and version choice

### Added
- Home page: players choose a Country, Language and Version. Echo shows the passage in the version chosen, and names it.
- `bible-catalog.json`: the list of countries, languages and versions to publish. Each version is switched on with `enabled`, and set to `games` or `full` scope.
- The build publishes `text/catalog.json`, listing only the versions that downloaded successfully.

### Changed
- `fetch_offline_text.py` downloads every enabled version (replacing the single `offline-text.json` list). It checks the verse fields, pauses between requests, and stops at a size limit.
- `game-chapters.json` holds the chapters the games use.

## 1.4.0 - Text-only release

### Added
- Bible text is downloaded at build time (`bible-catalog.json` and `game-chapters.json`, `DOWNLOAD_TEXT` variable), so the game reads text without a server or key in the browser.
- Passage text for Echo is read from the published text files, in the language chosen on the home page.
- "Coming soon" notes for the Audio and Video filters, and disabled audio and video formats on game pages, controlled by `features` in `config.json`.

### Changed
- Audio and video are switched off by default. Text games are fully available.
- DEPLOYMENT.md has a text-only setup section, which is the recommended starting point.

## 1.3.0 - Game catalogue, filters and Bible text

### Added
- Home page now shows all games in a 2 x 2 grid.
- Filters: All, Text, Audio and Video. Each game is tagged with the media formats it has.
- Game pages with a description, how to play, the available formats and a Start button.
- Bible text language selector on the home page. Echo pulls the passage it uses from Bible Brain in the selected language, when the media server is set up.
- Reference parser for passages such as "Luke 15:11-24" and "1 Samuel 3:1".
- Audio formats for Who Said It and Memory Verse, using the audio paths in `config.json`.

### Changed
- Covenant Quest now follows the 12 clips of *The Covenant* film, with the clip summaries, references and a question for each clip.
- Scene Detective and Covenant Quest are grouped as video games. Echo, puzzles and quizzes are text games.
- The separate "Text games / Audio games" switch was replaced by the filters.
- The Play menu item was removed, because the games are now on the home page.
- README now focuses on the game. Deployment and Bible Brain setup moved to DEPLOYMENT.md.

### Fixed
- The game page is now always fetched from the network first. Previously, an older cached page could hide new features such as the game switch.

## 1.2.0 - Text games

### Added
- A text version of every game: typed answers, reading passages before answering, and unscrambling words.
- Audio and text switch on the Play page.

## 1.1.0 - Puzzles and offline audio

### Added
- Bible Crossword and Word Search games.
- Optional build-time audio download for GitHub Pages (off by default).
- `offline-audio.json` to list the chapters for the build-time download.

## 1.0.5 - Bible Characters and Bible Trivia

### Added
- Bible Characters: guess the character from clues, with points for early answers.
- Bible Trivia: ten random questions, three lives and two lifelines (50:50 and Hint).
- Logout and a sign-in list of players on the device.

### Changed
- The Oral Bible Quiz was renamed Bible Trivia and changed to a single-player quiz.

## 1.0.4 - Covenant Quest on the film, Scene Detective changes

### Changed
- Covenant Quest used the stories of *The Covenant* film, in film order.
- Scene Detective uses scenes from the Gospels, Acts and the Covenant film.

## 1.0.3 - Languages and avatars

### Added
- Interface languages: Hindi, Tamil, Telugu, Kannada, Bengali, Marathi, Gujarati and Punjabi, alongside English and Malayalam.
- A language dropdown and a "Your Name" field on the profile.
- Bible character avatars, shown with the character's name.

## 1.0.2 - Progress, leaderboard and profiles

### Added
- Profiles with name and avatar.
- Choice of Old or New Testament, then a book, for each game.
- Points, levels, badges, streaks, attendance history and a leaderboard on the device.

## 1.0.1 - Heart and Hands

### Added
- Head, Heart and Hands steps at the end of each game.

## 1.0.0 - First playable version

### Added
- Seven original games: Echo, Scene Detective, Covenant Quest, Who Said It, Story Builder, Memory Verse and a Bible quiz.
- Installable Progressive Web App with offline support for the game screens.
- GitHub Pages publishing with GitHub Actions.
- Media proxy server design (cPanel Node.js) to keep the Bible Brain key on the server.

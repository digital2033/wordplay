# Changelog

All notable changes to Wordplay are recorded here. Versions follow the form `major.minor`.

## 1.5.4 - Bible Brain catalogue discovery (in progress)

### Found in the third discovery run
- Country-to-language link: `/languages?country=XX` returns the languages spoken in a country, with Bible and fileset counts.
- Filter by language ID works: `/bibles?language_id=N`. The ISO filter `/bibles?iso=` does not, and returns Bibles in other languages.
- Audio chapter route confirmed: `/bibles/filesets/{fileset}/{book}/{chapter}` returns a signed `path` to the audio file, as the media server expects.
- Text chapter route: not yet confirmed. The next round tests it with a text fileset.


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

# Deployment

How to publish Wordplay, and how the optional parts (audio, video, Bible Brain) are set up.

Wordplay is a static web app. It needs no server to run. Publishing it means putting its files on a web address, usually GitHub Pages.

---

## 1. Publish on GitHub Pages

1. Create a **public** repository, for example `wordplay`. (GitHub Pages on a free account needs a public repository.)
2. Push the contents of the game folder to the `main` branch. Push the files, not a zip.
3. In **Settings > Pages**, set **Source** to **GitHub Actions**. The default "Deploy from a branch" will not run the workflow.
4. The workflow `.github/workflows/deploy-pages.yml` checks the files and publishes them. Open the **Actions** tab to see progress.
5. The game is at `https://<your-account>.github.io/wordplay/`.

The workflow publishes only the files the game needs: `index.html`, `config.json`, `manifest.webmanifest`, `sw.js`, `bible-catalog.json`, `icons/` and `default-bible/`.

### Updating the game

1. Edit the files, commit, and push to `main`.
2. Increase `CACHE_VERSION` in `sw.js` (for example from `wordplay-v3` to `wordplay-v4`) when the offline files change, so installed copies update.
3. Record the change in `CHANGELOG.md`.

The game page and `config.json` are always fetched from the network first, so players see changes without clearing the cache.

---

## 2. Settings in `config.json`

| Setting | Purpose |
|---|---|
| `app` | The app name and tagline. |
| `api.base` | The address of the media server, used only when audio or video is set up. Leave the placeholder until then. |
| `media` | The paths to audio and video on the media server, for example `echoAudio`, `covenantAudio`, `whoSaidAudio`, `memoryAudio`, `sceneVideo`. Replace the `REPLACE_..._FILESET` placeholders when you have a fileset. |
| `features` | Switches each media type on or off: `text`, `audio`, `video`. Keep `audio` and `video` as `false` until their content is ready. While they are `false`, their formats show as **Coming soon**. |
| `staticAudio` | Set to `true` only when audio was downloaded at build time and the licence allows it. |
| `staticText` | Used by the older build-time text download. The Bible chooser does not use it. |
| `bibleBrain` | Optional, and used by the older build-time text download. The chooser in the app asks Bible Brain directly. |

---

## 3. The built-in English Bible

The King James Version is **committed** in `default-bible/en-kjv.json.gz`. It is made from the USX files with `scripts/usx_to_default_bible.py`, and it needs no key.

Leave the repository variable **`DOWNLOAD_DEFAULT_BIBLE` unset**. The step that downloads it from Bible Brain at build time is not needed, and would overwrite the committed file.

---

## 4. Optional build steps

These are controlled by **repository variables** (**Settings > Secrets and variables > Actions > Variables**) and one **secret**.

| Name | Type | Effect | Recommended |
|---|---|---|---|
| `BIBLE_BRAIN_KEY` | Secret | The key used by build steps that call Bible Brain. | Set only if you use a build step below. |
| `DOWNLOAD_AUDIO` | Variable | Downloads the chapters listed in `offline-audio.json` at build time, and publishes them as public files. | Off, unless the licence allows public audio. |
| `DOWNLOAD_TEXT` | Variable | Runs the older build-time text download. The current chooser does not read its output. | **Leave unset.** |
| `DOWNLOAD_DEFAULT_BIBLE` | Variable | Re-downloads the KJV at build time. | **Leave unset.** |

Players do not need a key for the game. The key is only needed by the person who downloads a Bible in the app, and by the optional build steps.

---

## 5. Audio and video

Audio and video are off by default. Two routes are available.

**Route A: audio published at build time (simplest, public files).**
1. Set the secret `BIBLE_BRAIN_KEY`.
2. List the chapters in `offline-audio.json`.
3. Set `DOWNLOAD_AUDIO` to `true`, and `staticAudio.enabled` to `true` in `config.json`.
4. Set `features.audio` to `true`.

Anyone can download files published this way, so check the licence first.

**Route B: a media server (keeps the Bible Brain key on the server).**
1. Run the media proxy in `wordplay-server` on a host with Node.js 18 or later (for example a cPanel Node.js app, Render, or a Cloudflare Worker).
2. Set `BIBLE_BRAIN_KEY` and `ALLOWED_ORIGINS` (your game address, with no trailing slash) as environment variables on that host. The key is never placed in the game.
3. Set `api.base` in `config.json` to the server address, and fill in the `media` paths with the filesets you use.
4. Set `features.audio` and `features.video` to `true` when the content works.

The media server's README explains its routes and the `ALLOWED_FILESETS` list.

**Video:** each video needs its own licence. Set `sceneVideo` in `media`, and the Covenant clip paths, then set `features.video` to `true`.

---

## 6. Bible Brain and the Bible chooser

Players do not need the server for the chooser. Each player types their own free Bible Brain key in the app. The key is kept in memory for the session, and is sent only to Bible Brain.

What the chooser uses from Bible Brain:
- `/countries`: all countries.
- `/languages?country=…`: the languages for a country.
- `/bibles?language_code=…`: the Bibles for a language, keeping those with text filesets (`text_plain` or `text_json`).
- `/bibles/filesets/{fileset}/{book}/{chapter}`: the text of each chapter, downloaded one chapter at a time.

Bible Brain's terms apply to every Bible a player downloads.

---

## 7. Checks before publishing

- Open the Pages address on a phone and on a computer. Play one game in each category.
- Check the **Actions** tab for a green tick.
- Check that the English passage shows in Echo (the built-in KJV).
- Check the licence of any Bible, audio or video you publish.
- Have partner teams review the content.

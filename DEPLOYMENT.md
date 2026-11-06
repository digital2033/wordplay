# Deployment

How to publish Wordplay, and how the optional audio and media server are set up.

Wordplay is a static web app. It needs no server to run. Publishing means putting its files on a web address, usually GitHub Pages.

---

## 1. Publish on GitHub Pages

1. Create a **public** repository, for example `wordplay`.
2. Push the contents of this folder to the `main` branch.
3. In **Settings > Pages**, set **Source** to **GitHub Actions**.
4. The workflow `.github/workflows/deploy-pages.yml` runs in two stages:
   - **test:** validates the JSON and the scripts, checks that the question bank matches its sources, runs the browser tests (`browser_check`, `levels_check`, `deep_check`, `safety_check`), and only then continues.
   - **deploy:** publishes only the public files: `index.html`, `config.json`, `manifest.webmanifest`, `sw.js`, `icons/`, `default-bible/` and `content/`.
5. The game is at `https://<your-account>.github.io/wordplay/`.

### Updates and the cache

Each deployment stamps the service worker with the commit ID (for example `wordplay-1a2b3c4d`). Players therefore receive new content and code on their next visit, without you changing any version number by hand.

---

## 2. Settings in `config.json`

| Setting | Purpose |
|---|---|
| `app` | The app name and tagline. |
| `api.base` | The address of the media server. Leave the placeholder until audio or video is set up. |
| `media` | The paths to audio and video on the media server. Replace the `REPLACE_..._FILESET` placeholders when you have a fileset. |
| `staticAudio` | Set `enabled` to `true` only when audio was downloaded at build time and the licence allows it. |
| `features` | Switches each media type on or off: `text`, `audio`, `video`. Keep `audio` and `video` as `false` until their content is ready. |

`config.json` must not contain keys or passwords. The workflow checks this on every run.

---

## 3. Optional audio at build time (licence-gated)

Downloaded audio is **published publicly**, so it is off by default and needs two confirmations:

1. Confirm the licence of the audio in writing (Bible Brain's terms and the audio owner's permission).
2. In **Settings > Secrets and variables > Actions**:
   - secret `BIBLE_BRAIN_KEY`: your key,
   - variable `DOWNLOAD_AUDIO` = `true`,
   - variable `AUDIO_LICENCE_CONFIRMED` = `true`.

Both variables must be `true`. The step is skipped otherwise. Then list the chapters in `offline-audio.json`, set `staticAudio.enabled` and `features.audio` to `true` in `config.json`, and commit.

The Bible text is **not** published at build time. Players download Bible text on their own device, with their own key (see the Bible chooser in the README).

---

## 4. Media server (for streamed audio and video)

The media proxy keeps the Bible Brain key on a server, so the key never reaches the browser.

1. The server is in the `media-server/` folder of this project. Its README explains the routes.
2. Host it on a host that runs Node.js 18 or later (for example a cPanel Node.js app, Render, or a Cloudflare Worker).
3. Set these environment variables on that host:
   - `BIBLE_BRAIN_KEY`: your key (never commit it),
   - `ALLOWED_ORIGINS`: your game address, with no trailing slash,
   - `ALLOWED_FILESETS`: the filesets the game may request,
   - `TRUST_PROXY` (optional, default `1`): the number of proxies in front of the server.
4. Set `api.base` in `config.json` to the server's public address, fill in the `media` paths, and set `features.audio` or `features.video` to `true`.

The GitHub Actions file for the server is kept as `media-server/deploy-server.workflow.yml.txt`. Move it to the server's own repository, and rename it to `.yml`, to use it there.

**Video:** each video needs its own licence. Set `sceneVideo` in `media`, and the Covenant clip paths, then set `features.video` to `true`.

---

## 5. Checks before publishing

- The **Actions** tab shows a green tick on both the test and deploy stages.
- Open the Pages address on a phone and on a computer. Play one game in each category.
- Check the English passage in Echo (the built-in King James Version).
- Check the licence of any audio, video or Bible you add.
- Have partner teams review the content (see the content disclaimer in the README).

---

## 6. Analytics (Firebase), setting it up

Analytics is optional, opt-in, and anonymous. It is configured in `firebase-config.json`.

1. In the Firebase console, open your project (`wordplay-bible`) and enable **Google Analytics** for the web app.
2. In **Google Cloud console > APIs & Services > Credentials**, open the web API key and set **Website restrictions** to `https://<your-account>.github.io/*`, so that other sites cannot use it. The key is public by design; this restriction is what protects it.
3. In **Google Analytics > Admin > Data settings**, set the data retention period (for example 2 months), and turn off **Google signals**.
4. Confirm the child-directed settings are in the game code (`allow_google_signals: false`, `allow_ad_personalization_signals: false`). Keep the privacy notice in the README up to date.
5. Check that the **Analytics** event stream shows `game_started` and `game_finished` after you agree in the app.

**Before publishing to children:** have the privacy notice reviewed for your country (for example COPPA in the United States, and the UK Children's code or GDPR in Europe).

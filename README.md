# Wordplay

Play - Feel - Live. A Scripture Engagement game with Head - Heart - Hands journeys.
Installable as a Progressive Web App (PWA) on Android, iPhone and desktop, and it works offline for the game shell.

## What is in this repository

| File | Purpose |
|---|---|
| `index.html` | The game (all modules, languages, profiles, progress and leaderboard) |
| `config.json` | Public settings: media proxy address, Bible Brain fileset IDs per language |
| `manifest.webmanifest` | PWA name, icons and install settings |
| `sw.js` | Service worker: offline shell and cache versioning |
| `icons/` | App icons (192 and 512 pixels) |

## Security

- **The Bible Brain API key is never stored in this repository.** It lives only on the media proxy server (see the `wordplay-server` repository), in an environment variable.
- `config.json` holds only the public address of the proxy and the fileset IDs. Do not add keys, passwords or tokens here.
- `.gitignore` excludes `.env` files.

## Run locally

Serve the folder with any static server (opening the file directly will not register the service worker):

```bash
npx serve .
# or
python3 -m http.server 8000
```

Then open http://localhost:8000

## Publish on GitHub Pages

1. Create a new repository on GitHub, for example `wordplay`. For Pages on a free account it must be public, and this repository should only contain the files listed above.
2. Push this folder:
   ```bash
   git init
   git add .
   git commit -m "Wordplay v1"
   git branch -M main
   git remote add origin https://github.com/<your-account>/wordplay.git
   git push -u origin main
   ```
3. In the repository, go to **Settings > Pages**, choose **Deploy from a branch**, select `main` and `/ (root)`, and save.
4. The game will be published at `https://<your-account>.github.io/wordplay/`.

## Connect to the media proxy

1. Deploy the `wordplay-server` on your cPanel Node.js app, for example at `https://api.yourdomain.org`.
2. In that server's environment variables set `ALLOWED_ORIGINS` to the game address, for example `https://<your-account>.github.io` (no trailing slash, no path).
3. In `config.json`, set `api.base` to the server address and replace each `REPLACE_..._FILESET` value with the fileset IDs from your Bible Brain account.

## Release checklist

- Bump `CACHE_VERSION` in `sw.js` so installed apps pick up the new version.
- Test on a real Android phone: install from the browser menu, open offline, play audio.
- Check the licence terms of Bible Brain and the content providers before publishing audio or video.

## Languages

Interface labels are available in English, Hindi, Malayalam, Tamil, Telugu, Kannada, Bengali, Marathi, Gujarati and Punjabi. Game content (questions, passages and clues) is currently in English and needs translation by partners.

## Automated publishing (GitHub Actions)

The workflow in `.github/workflows/deploy-pages.yml` runs on every push to `main`. It:

1. Validates `config.json` and `manifest.webmanifest`, and checks that `config.json` contains no secret-like fields.
2. Checks the syntax of the game script and the service worker.
3. Publishes only the public files (`index.html`, `config.json`, `manifest.webmanifest`, `sw.js`, `icons/`) to GitHub Pages.

**One-time setup:** in the repository go to **Settings > Pages** and set **Source** to **GitHub Actions** (not "Deploy from a branch"). After that, pushing to `main` publishes the game automatically.

## Offline audio at build time (optional, Option 1)

This publishes chapter audio as part of the public GitHub Pages site, so the game can play it without the media proxy server.

**Only turn this on after confirming that the Bible Brain licence allows public redistribution.** Anyone can download files published this way.

1. Add the key as a repository secret: **Settings > Secrets and variables > Actions > New repository secret**, name `BIBLE_BRAIN_KEY`.
2. Edit `offline-audio.json` and list the chapters to include, using the fileset ID and three-letter book code (for example `LUK` and chapter `15`).
3. Turn on the download: **Settings > Secrets and variables > Actions > Variables**, add `DOWNLOAD_AUDIO` with the value `true`.
4. In `config.json`, set `staticAudio.enabled` to `true`.
5. Push to `main`. The audio is downloaded during the build and published under `media/`.

The build stops if the total size exceeds 800 MB (set by `MAX_MB`), since GitHub Pages sites have a size limit. The key is used only during the build and is never written to the published files.

To return to the server approach, set `DOWNLOAD_AUDIO` to `false` and `staticAudio.enabled` to `false`.

## Audio and text games

On the **Play** page, a switch chooses the game set:

- **Audio games:** the original ten games, with audio and video where content is available (Echo, Scene Detective and Covenant Quest use audio or film clips).
- **Text games:** a text version of every game. Players read passages and scenes, type their answers, and unscramble or type words instead of tapping options.

Text games are recorded in the history with "(Text)" after the game name, so progress in each set can be seen separately.

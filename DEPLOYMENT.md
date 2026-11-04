# Deployment and Bible Brain setup

This guide covers publishing Wordplay, setting up the media server, and connecting the Bible Brain API key.

## 1. Keep the key secret

- The Bible Brain key is **never** placed in the game files, `config.json`, or the GitHub repository.
- The key is stored only as an **environment variable on the media server** (cPanel Node.js app), named `BIBLE_BRAIN_KEY`.
- The only exception is optional build-time audio download (section 5), which stores the key as a GitHub **secret** used during the build only.

## 2. Publish the game (GitHub Pages)

1. Create a public repository, for example `wordplay`.
2. Push the game folder to the `main` branch.
3. In **Settings > Pages**, set **Source** to **GitHub Actions**.
4. The workflow `.github/workflows/deploy-pages.yml` checks the files and publishes them. The game will be at `https://<your-account>.github.io/wordplay/`.

## 3. Set up the media server (cPanel)

1. In cPanel, create a subdomain such as `api.yourdomain.org` and turn on AutoSSL.
2. Open **Setup Node.js App** and choose **Node.js 20** (18 or later), production mode, and startup file `server.js`.
3. Upload the `wordplay-server` files to the application root, then run **Run NPM Install**.
4. Add environment variables in the same page:

| Name | Value |
|---|---|
| `BIBLE_BRAIN_KEY` | Your Bible Brain key |
| `ALLOWED_FILESETS` | Comma-separated fileset IDs the game may use, no spaces |
| `ALLOWED_ORIGINS` | Your game address, for example `https://<your-account>.github.io` (no trailing slash) |

5. Restart the application.
6. Test: `https://api.yourdomain.org/api/health` should return `{"ok":true}`.

If `ALLOWED_FILESETS` does not include a fileset, the server returns 403.

## 4. Connect the Bible Brain text and audio

1. Find the **filesets** for each language in your Bible Brain account. Text and audio filesets have separate IDs.
2. Add every fileset ID to `ALLOWED_FILESETS` on the server, and restart it.
3. In `config.json` in the game repository:
   - set `api.base` to your server address, for example `https://api.yourdomain.org`;
   - for each language under `bibleBrain.languages`, set `textFileset` and `audioFileset` to the Bible Brain IDs;
   - replace the `REPLACE_..._FILESET` placeholders in `media` with the chapter paths you want to use, such as `/api/audio/<fileset>/LUK/15`.
4. Commit and push. The game's language list shows every language that has a `textFileset` set.

**What happens in the game:**
- Echo fetches the passage it uses (for example Luke 15:11-24) in the chosen Bible language. References with chapter ranges, such as Jonah 1-3, use the built-in text.
- Audio formats (Who Said It, Memory Verse) play the audio paths in `media` when they are set.
- If the server cannot be reached, the game uses its built-in text and shows placeholders for audio and video.

## 5. Optional: audio published at build time

This copies the listed chapters into the public site, so anyone can download them. **Use it only after confirming that the Bible Brain licence allows public redistribution.**

1. Add `BIBLE_BRAIN_KEY` as a repository secret (**Settings > Secrets and variables > Actions**).
2. List the chapters in `offline-audio.json`.
3. Add the repository variable `DOWNLOAD_AUDIO` with the value `true`.
4. Set `staticAudio.enabled` to `true` in `config.json`.

The build stops if the audio exceeds 800 MB. Set `DOWNLOAD_AUDIO` to `false` to stop.

## 6. Film clips

Scene Detective and Covenant Quest play video or audio from the `media` section of `config.json`:

- `sceneVideo`: a Gospel, Acts or Covenant film clip link (for Scene Detective).
- `covenantAudio`: the audio for Covenant Quest, one path per clip.

Clip timings should follow the Covenant clip guide. Check the licence for each film before publishing clips.

## 7. Updating the game

1. Edit the files and push to `main`.
2. Increase `CACHE_VERSION` in `sw.js` when the offline files change, so installed apps update.
3. Record the change in `CHANGELOG.md`.

Game pages and `config.json` are always fetched from the network first, so players see new content without clearing the cache.

## 8. Server deployment through GitHub Actions (optional)

The `wordplay-server` repository contains `.github/workflows/deploy-server.yml`. It copies the code to cPanel over SSH and restarts the app. Add these repository secrets: `CPANEL_SSH_HOST`, `CPANEL_SSH_PORT`, `CPANEL_USER`, `CPANEL_APP_PATH` and `CPANEL_SSH_KEY`. The `.env` file on the server is never overwritten.

## Troubleshooting

| Problem | What to check |
|---|---|
| Changes do not appear in the game | Reload the page. If it persists, check that the latest commit deployed in the Actions tab. |
| The language list has only English | `textFileset` is still a `REPLACE_` placeholder in `config.json`. |
| Passage text does not load | The fileset is missing from `ALLOWED_FILESETS`, or `ALLOWED_ORIGINS` does not match the game address. |
| Browser shows a CORS error | `ALLOWED_ORIGINS` must match the game address exactly, including `https`. |
| Server returns 403 | The fileset ID is not in `ALLOWED_FILESETS`. |

## Text-only setup (no server needed)

See the section 'Choosing countries, languages and versions' below for the menu structure.

This is the recommended starting point. Bible text is downloaded once, during the GitHub Pages build, and published with the game. The key is used only during the build, and no server is required.

1. In **Settings > Secrets and variables > Actions > Secrets**, add `BIBLE_BRAIN_KEY`.
2. In **Settings > Secrets and variables > Actions > Variables**, add `DOWNLOAD_TEXT` with the value `true`.
3. Edit `bible-catalog.json`. This lists the countries, languages and versions players can choose. Each version's `id` is its Bible Brain **text** fileset ID. Set `enabled` to `true` for each version to publish, and `scope` to `games` (only the chapters the games use) or `full` (the whole Bible).
4. Edit `game-chapters.json` if you want to change the chapters the games use.
5. Push to `main`. The build downloads the enabled versions into `text/`, and writes `text/catalog.json`, which the game reads for its Country, Language and Version choices. Only versions that downloaded successfully appear.

The build stops with a clear message if Bible Brain returns an error, or if the verse fields are not as expected. The script checks the field names on the first chapter, so the first run shows whether they need adjusting.

**Before publishing text:** Bible Brain text is published as public files. Check the licence for each language and version, and whether attribution is required. Bible Brain's copyright endpoint (`bibles/{bibleId}/copyright`) gives the text to display.

**Adding versions and countries:** Add an entry under the right country and language in `bible-catalog.json`, set `enabled` to `true`, and push. Each full Bible is roughly 1,189 small files, so check the size reported in the build log. The build stops at 900 MB (`MAX_MB`).

**How players use it:** On the home page, players choose a Country, then a Language, then a Version. Echo shows the passage in the version they chose, and names the version above the text. Other games use the built-in English text for now.

### Coming soon: audio and video

Audio and video are not connected yet. In `config.json`, `features.audio` and `features.video` are `false`. While they are off:
- the Audio and Video filters show a "Coming soon" note;
- audio and video formats on game pages are shown as disabled, with a "Coming soon" label;
- the games still play in their text formats.

When audio or video content is ready, set the matching feature to `true`. For audio, the options are the build-time audio download (section 5) or the media server (section 3). Video needs a film clip link in `config.json`.


### Choosing countries, languages and versions

Players choose a **country**, then a **language**, then a **version** on the home page. The menus come from `text/catalog.json`, which the build creates from `bible-catalog.json`:

```json
{
  "countries": [
    { "code": "IN", "name": "India", "languages": [
        { "code": "ml", "name": "Malayalam", "versions": [
            { "name": "Malayalam Bible (Version 1)", "fileset": "<Bible Brain fileset ID>" } ] } ] }
  ],
  "chapters": ["LUK:15", "JHN:3", "GEN:22"]
}
```

- Each **version** has a Bible Brain text fileset ID. Versions with a `REPLACE_...` placeholder are skipped.
- The same fileset can appear under several countries. It is downloaded only once.
- A version is shown in the menus only if at least one of its chapters was downloaded.
- `chapters` lists every chapter the games use. Each chapter is downloaded for every version, so keep the list to what the games need.
- Book codes follow Bible Brain (for example `LUK`, `JHN`, `1CO`, `PHP`).

**Size:** each chapter is roughly 5 to 15 KB per version. Ten versions with 100 chapters is about 10 MB, well within GitHub Pages' limit. The build stops at 800 MB by default (`MAX_MB`).

**Testing the build:** run it with `DOWNLOAD_TEXT` set to `true` and check the Actions log. It prints each chapter it saves and the final catalogue summary.

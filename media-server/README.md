# Wordplay media proxy (sample)

A small Node.js server that keeps your Bible Brain key on the server and gives the
Wordplay games audio and text through safe, allow-listed routes.

## Setup

```bash
npm install
cp .env.example .env      # then edit .env and add your key
npm start
```

## Test

```bash
curl http://localhost:8080/api/health
curl http://localhost:8080/api/text/ENGKJVO1DA/GEN/1
curl -I http://localhost:8080/api/audio/ENGKJVO1DA/GEN/1
```

Requests for filesets that are not in `ALLOWED_FILESETS` return 403.

## Connect the game

In `wordplay.html`, point the audio and video settings at your server instead of a Bible Brain link:

```javascript
const API = "https://your-server.example.org";
const CONFIG = {
  echoAudio:    `${API}/api/audio/ENGKJVO1DA/LUK/15`,
  sceneVideo:   "",   // video route to be added in the next step
  covenantAudio:`${API}/api/audio/ENGKJVO1DA/GEN/22`,
  quizAudio:    `${API}/api/audio/ENGKJVO1DA/LUK/15`
};
```

The browser only ever sees the proxy address. It never sees the key.

## Security notes

- The key lives only in `.env` on the server. Do not put it in the game file, a Git repository, a public folder or chat messages.
- If the key has been shared anywhere, regenerate it in your Bible Brain account.
- Keep `ALLOWED_FILESETS` and `ALLOWED_ORIGINS` as short as possible.
- Rate limiting is set to 300 requests per IP every 15 minutes. Adjust in `server.js` as needed.
- Check the Bible Brain licence terms for streaming and caching content in a public game.

## Before going live

- Confirm the chapter endpoint path and the audio field name (`path`) against the current Bible Brain Postman collection, as the sample uses the documented pattern but the exact response shape should be verified with a real key.
- Add HTTPS (for example with a reverse proxy such as Caddy or Nginx).
- Add monitoring of request counts so usage can be reported to FCBH.

## Automated deployment to cPanel (GitHub Actions)

The workflow in `.github/workflows/deploy-server.yml` checks the server on every push to `main`, then copies the code to your cPanel app folder over SSH and restarts the app. The `.env` file on the server is never overwritten, because it is excluded from the copy.

**Repository secrets** (Settings > Secrets and variables > Actions):

| Secret | Value |
|---|---|
| `CPANEL_SSH_HOST` | Your server host name, for example `yourdomain.org` |
| `CPANEL_SSH_PORT` | SSH port (often 22 or a number given by your host) |
| `CPANEL_USER` | Your cPanel user name |
| `CPANEL_APP_PATH` | The application root, for example `/home/<user>/wordplay-api` |
| `CPANEL_SSH_KEY` | A private SSH key that only this deployment uses |

**Important:** the Bible Brain key is **not** a GitHub secret. Set `BIBLE_BRAIN_KEY` and `ALLOWED_ORIGINS` once in the cPanel Node.js app's environment variables. The deployment does not change them.

Check with your host that SSH access is enabled for your account, and that the restart method used here (`tmp/restart.txt`, which is the standard for cPanel Node.js apps) works on your plan.

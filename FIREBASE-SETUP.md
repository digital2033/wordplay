# Firebase setup: shared leaderboard and analytics

This guide turns on the two Firebase features in Wordplay:

- **Shared leaderboard**, which stores the top scores in Firestore. Players must agree to share.
- **Analytics**, which counts games played (no names). Players must agree first.

Both features use the free Spark plan. The project is `wordplay-bible`. The values in `firebase-config.json` must match the web app in your project.

Time needed: about 30 minutes.

---

## 1. Open the project

1. Go to https://console.firebase.google.com and open **wordplay-bible**.
2. Open **Project settings** (gear icon) and check that the **Project ID** is `wordplay-bible`.

## 2. Check the web app and its settings

1. In **Project settings > General > Your apps**, find the web app. If there is none, choose **Add app > Web** (</>), give it the nickname `Wordplay web`, and do not tick hosting. Copy the `firebaseConfig` values it shows.
2. Compare them with `firebase-config.json` in the project. The `apiKey`, `projectId`, `appId`, `messagingSenderId` and `measurementId` must match. If any value differs, update `firebase-config.json` and publish again.

## 3. Turn on Google Analytics

1. In **Project settings > Integrations**, check that **Google Analytics** is enabled. If it is not, enable it and choose the Analytics account to use.
2. The measurement ID is shown there. It must be the same as in `firebase-config.json` (`G-TB2M8Z2QF1`).

## 4. Turn on anonymous sign-in (for the shared leaderboard)

1. Open **Build > Authentication**, then **Get started**.
2. Open the **Sign-in method** tab, choose **Anonymous**, switch it on, and save.

Anonymous sign-in gives each browser an ID without asking for an account. Players never sign in.

## 5. Create the Firestore database

1. Open **Build > Firestore Database**, then **Create database**.
2. Choose **Production mode** (the rules are set in the next step).
3. Choose a location close to your players, for example **asia-south1 (Mumbai)** for South Asia. **The location cannot be changed later.**

## 6. Publish the security rules

The rules are in `firestore.rules`. They let anyone read the top scores, and let each browser write only its own entry, with checked fields.

**Option A: in the console**
1. Open **Firestore Database > Rules**.
2. Replace the text with the contents of `firestore.rules`, then choose **Publish**.

**Option B: with the Firebase command line**
1. Install the tools once: `npm install -g firebase-tools`
2. In the project folder, run `firebase login`, then `firebase deploy --only firestore:rules`.
   The files `firebase.json` and `.firebaserc` already point to `wordplay-bible` and the rules file.

## 7. Restrict the API key to your website

The Firebase web key is public, so restrict it to your site so that other websites cannot use it.

1. Open the Google Cloud console for the same project: https://console.cloud.google.com, then **APIs & Services > Credentials**.
2. Open the key named **Browser key (auto created by Firebase)**, or the key whose value matches `apiKey` in `firebase-config.json`.
3. Under **Application restrictions**, choose **Websites**, then add:
   - `https://<your-account>.github.io/*`
   - `http://localhost:8800/*` (only for testing on your own computer; remove it later)
4. Leave **API restrictions** as they are until everything works. Then you may restrict them to the Firebase APIs.
5. Save.

## 8. Set the analytics privacy options

1. In **Google Analytics > Admin > Data collection**, turn **Google signals** off.
2. In **Admin > Data settings > Data retention**, choose **2 months**.
3. Keep the child-directed settings in the game code (no ad personalisation, no Google Signals). Read Google's policy for child-directed services before you open the game to children, and get your privacy notice reviewed (see DEPLOYMENT.md).

## 9. Check that it works (on the live site)

1. Publish the site with GitHub Actions (see DEPLOYMENT.md, section 1). Wait for the green tick.
2. Run the live check on your computer:

   ```
   WORDPLAY_URL=https://<your-account>.github.io/wordplay/ python3 tests/firebase_live_check.py
   ```

   It creates a test player, shares a test score with the nickname **Live Test**, checks it appears, then removes it. Expect three passes.

3. Open **Firestore Database > Data**. The `scores` collection should be empty again after the test.
4. For analytics, open **Google Analytics > Reports > Realtime** and play a game after you agree in the app. Events appear within a few minutes. To see parameters, use **Admin > DebugView** with the **Google Analytics Debugger** browser extension turned on.

## 10. Troubleshooting

| What you see | What to check |
|---|---|
| "The shared leaderboard is not available right now" | The browser console. Usually the API key restriction (step 7), or Firestore has not been created (step 5). |
| "Your score could not be shared just now" | Rules not published (step 6), or anonymous sign-in is off (step 4). |
| `auth/operation-not-allowed` in the console | Anonymous sign-in is not turned on (step 4). |
| `permission-denied` in the console | The rules are not published, or the rules changed. Publish them again. |
| `auth/api-key-not-valid` or a "domain not allowed" error | The website restriction in step 7 does not include your address. Check for the exact address, including `/*`. |
| Analytics events do not appear | Consent must be **Yes**, Google signals should be off, and some browsers block analytics. Use a different browser to check. |
| The leaderboard works but analytics does not | Check the measurement ID in `firebase-config.json`, and step 3. |

## 11. Ongoing care

- **Test data:** delete any test entries from `scores` in Firestore.
- **Rules changes:** publish them again after any change to `firestore.rules`, and test with the live check.
- **Limits:** the free plan allows about 50,000 reads and 20,000 writes a day for Firestore. A group of several hundred players is well within that.
- **Nicknames:** nobody moderates the leaderboard yet. Check it regularly if children are playing (see ROADMAP.md).
- **Privacy:** keep the privacy notice in the README up to date with what is shared.

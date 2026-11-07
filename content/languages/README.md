# Language packs (coming soon)

Wordplay's games are written in English. Partners can create a **language pack** so that the games can be used with another language and Bible text. This is a planned feature (see [ROADMAP.md](../../ROADMAP.md)). Partner input is needed for every language.

## What a language pack contains

Copy `template.json` to `<language-code>.json` (for example `ml.json` for Malayalam) and fill in the fields. Every field marked `"translate"` needs a translation. Leave the `"ref"` and `"book"` fields in English, because the game uses them to find the verses.

| Section | What to translate |
|---|---|
| `uiLabels` | The buttons and messages in the game. |
| `gameTitles` | The titles, taglines and "how to play" text for each of the ten games. |
| `questionFrames` | The wording around each question, such as "Which book of the Bible is this verse from?" |
| `echoPrompts` | The heart prompts and missions for Echo (not the verse text). |
| `characterClues` | The clues for Bible Characters, one set per character. |
| `storyCards` | The cards for Story Builder, in the order of the story. |
| `wordLists` | The words and clues for Crossword and Word Search. Words must use the letters of the target script. |

## What partners need to provide

1. **Translators:** native speakers of the language, who know the Bible.
2. **Bible scholar:** checks the theological accuracy of every clue, card and prompt.
3. **Reviewer:** tests each game with a small group before release.
4. **Bible text:** a text Bible for the language from Bible Brain (the player can then choose it in the app). Check its licence.

## Steps

1. Agree the language and the Bible text with the project owner.
2. Copy `template.json`, and translate it section by section.
3. A scholar checks the accuracy, and a native reviewer checks the language.
4. The project owner adds the pack to the game and tests it.
5. The language is released as a "coming soon" game, then fully available once reviewed.

## Notes

- Do not change the `"ref"` or `"book"` fields.
- Echo keywords are not translated here. They must be written again in the new language, because the keyword check depends on the exact words in the Bible text. This will be part of the review.
- Do not publish a translation before the review is complete.

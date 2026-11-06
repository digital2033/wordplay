/**
 * Central configuration. Values come from environment variables (.env),
 * never from the game files.
 */
const list = (v) => (v || "").split(",").map(s => s.trim()).filter(Boolean);

module.exports = {
  PORT: process.env.PORT || 8080,
  BIBLE_BRAIN_KEY: process.env.BIBLE_BRAIN_KEY,           // secret, server only
  BIBLE_BRAIN_BASE: process.env.BIBLE_BRAIN_BASE || "https://4.dbt.io/api",

  // Only these filesets can be requested. Add the sets your games need.
  // Example values are placeholders: check the IDs in your Bible Brain account.
  allowedFilesets: list(process.env.ALLOWED_FILESETS),

  // Only these game origins may call the API from a browser.
  allowedOrigins: list(process.env.ALLOWED_ORIGINS)
};

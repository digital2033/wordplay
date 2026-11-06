/**
 * Wordplay media proxy (sample)
 *
 * The Bible Brain API key is read from the environment and never sent to the browser.
 * The game asks this server for text or audio. The server adds the key, calls
 * Bible Brain, and returns only the content.
 */
require("dotenv").config();
const express = require("express");
const rateLimit = require("express-rate-limit");
const { allowedFilesets, allowedOrigins, PORT, BIBLE_BRAIN_KEY, BIBLE_BRAIN_BASE } = require("./config");

if (!BIBLE_BRAIN_KEY) {
  console.error("Missing BIBLE_BRAIN_KEY. Add it to your .env file (see .env.example).");
  process.exit(1);
}

const app = express();
app.disable("x-powered-by");
// Behind a host proxy (cPanel, Cloudflare, Render), trust the first proxy so the rate limit sees real visitors
app.set("trust proxy", Number(process.env.TRUST_PROXY || 1));

/* ---------- CORS: only your own game origins may call this server ---------- */
app.use((req, res, next) => {
  const origin = req.headers.origin;
  if (origin && allowedOrigins.includes(origin)) {
    res.setHeader("Access-Control-Allow-Origin", origin);
    res.setHeader("Vary", "Origin");
  }
  res.setHeader("Access-Control-Allow-Headers", "Range");
  res.setHeader("Access-Control-Expose-Headers", "Content-Length, Content-Range, Accept-Ranges");
  if (req.method === "OPTIONS") return res.sendStatus(204);
  next();
});

/* ---------- Rate limiting: protects your key from abuse ---------- */
app.use("/api/", rateLimit({
  windowMs: 15 * 60 * 1000,   // 15 minutes
  limit: 300,                 // requests per IP per window
  standardHeaders: true,
  legacyHeaders: false
}));

/* ---------- Input validation ---------- */
const BOOK_RE = /^[1-3]?[A-Z]{2,3}$/;  // e.g. GEN, MAT, 1JN, JHN
const FILESET_RE = /^[A-Z0-9]{6,12}$/;  // e.g. ENGKJVO1DA

function validate(req, res, next) {
  const { filesetId, book, chapter } = req.params;
  const ch = Number(chapter);
  if (!allowedFilesets.includes(filesetId)) return res.status(403).json({ error: "Fileset not allowed" });
  if (!FILESET_RE.test(filesetId) || !BOOK_RE.test(book)) return res.status(400).json({ error: "Invalid id" });
  if (!Number.isInteger(ch) || ch < 1 || ch > 150) return res.status(400).json({ error: "Invalid chapter" });
  req.chapterNum = ch;
  next();
}

/* Helper: call Bible Brain with the key added server-side only */
async function dbp(path, params = {}) {
  const url = new URL(BIBLE_BRAIN_BASE + path);
  url.searchParams.set("key", BIBLE_BRAIN_KEY);
  url.searchParams.set("v", "4");
  for (const [k, v] of Object.entries(params)) url.searchParams.set(k, v);
  const r = await fetch(url, { headers: { Accept: "application/json" } });
  if (!r.ok) throw Object.assign(new Error("Upstream error"), { status: r.status });
  return r.json();
}

/* ---------- Health check ---------- */
app.get("/api/health", (req, res) => res.json({ ok: true }));

/* ---------- Text: one chapter of verses ---------- */
app.get("/api/text/:filesetId/:book/:chapter", validate, async (req, res) => {
  try {
    const data = await dbp(`/bibles/filesets/${req.params.filesetId}/${req.params.book}/${req.chapterNum}`);
    res.set("Cache-Control", "public, max-age=86400");
    res.json({ verses: (data.data || []).map(v => ({ verse: v.verse_start, text: v.verse_text })) });
  } catch (e) {
    res.status(e.status || 502).json({ error: "Could not load text" });
  }
});

/* ---------- Audio: stream one chapter ----------
   Bible Brain returns a signed CDN URL for the chapter file. The server
   fetches it and streams it to the browser, so the signed URL and the key
   are not exposed to the player. Confirm the response field name against
   the current Postman collection (the sample uses "path"). */
app.get("/api/audio/:filesetId/:book/:chapter", validate, async (req, res) => {
  try {
    const meta = await dbp(`/bibles/filesets/${req.params.filesetId}/${req.params.book}/${req.chapterNum}`);
    const item = (meta.data || [])[0];
    const signed = item && (item.path || item.url);
    if (!signed) return res.status(404).json({ error: "No audio for this chapter" });

    const upstream = await fetch(signed, { headers: req.headers.range ? { Range: req.headers.range } : {} });
    if (!upstream.ok && upstream.status !== 206) return res.status(502).json({ error: "Audio unavailable" });

    res.status(upstream.status);
    res.set("Content-Type", upstream.headers.get("content-type") || "audio/mpeg");
    res.set("Accept-Ranges", "bytes");
    ["content-length", "content-range"].forEach(h => {
      const v = upstream.headers.get(h); if (v) res.set(h, v);
    });
    res.set("Cache-Control", "public, max-age=86400");
    const { Readable } = require("stream");
    Readable.fromWeb(upstream.body).pipe(res);
  } catch (e) {
    res.status(e.status || 502).json({ error: "Could not load audio" });
  }
});

/* ---------- Catch-all ---------- */
app.use((req, res) => res.status(404).json({ error: "Not found" }));

app.listen(PORT, () => console.log(`Wordplay media proxy listening on port ${PORT}`));

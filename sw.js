/* Wordplay service worker.
   Caches the game shell so it opens offline. Audio and text from the
   media proxy (/api/...) are always fetched live and never cached here.
   Bump CACHE_VERSION on every release so players receive the update. */
const CACHE_VERSION = "wordplay-v2";
const SHELL = [
  "./",
  "./index.html",
  "./config.json",
  "./manifest.webmanifest",
  "./icons/icon-192.png",
  "./icons/icon-512.png"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then(cache => cache.addAll(SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE_VERSION).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", event => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET") return;
  if (url.origin !== self.location.origin) return;     // other sites: normal network
  if (url.pathname.includes("/api/")) return;          // media proxy: always live
  if (url.pathname.includes("/media/")) return;     // offline audio: not cached by the app shell

  event.respondWith(
    caches.match(event.request).then(cached => {
      const network = fetch(event.request).then(response => {
        if (response && response.ok) {
          const copy = response.clone();
          caches.open(CACHE_VERSION).then(cache => cache.put(event.request, copy));
        }
        return response;
      });
      return cached || network.catch(() => caches.match("./index.html"));
    })
  );
});

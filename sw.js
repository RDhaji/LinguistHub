const SHELL_CACHE = 'lh-shell-v3';
const PAYLOAD_CACHE = 'lh-payload-v3';

const STATIC_SHELL = [
  './',
  './index.html',
  './manifest.json',
  './icon.png',
  './hydration.worker.js'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(SHELL_CACHE).then((cache) => cache.addAll(STATIC_SHELL))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((k) => k !== SHELL_CACHE && k !== PAYLOAD_CACHE)
          .map((k) => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // 1. Gzip Lexicon Binary: Strict Cache-First with Guaranteed Storage Commit
  if (url.pathname.endsWith('compiled_lexicon_payload.json.gz')) {
    event.respondWith(
      caches.open(PAYLOAD_CACHE).then(async (cache) => {
        const match = await cache.match(event.request);
        if (match) return match;

        try {
          const networkRes = await fetch(event.request);
          if (networkRes.ok) {
            // waitUntil keeps SW alive during 6.2MB write to Cache Storage
            event.waitUntil(cache.put(event.request, networkRes.clone()));
          }
          return networkRes;
        } catch (err) {
          return new Response('{"error":"offline_payload_unavailable"}', {
            status: 503,
            headers: { 'Content-Type': 'application/json' }
          });
        }
      })
    );
    return;
  }

  // 2. Core App Shell: Stale-While-Revalidate
  if (event.request.method === 'GET' && url.origin === self.location.origin) {
    event.respondWith(
      caches.match(event.request).then((cached) => {
        const networkFetch = fetch(event.request).then((res) => {
          if (res.ok) {
            caches.open(SHELL_CACHE).then((cache) => cache.put(event.request, res.clone()));
          }
          return res;
        }).catch(() => cached);

        return cached || networkFetch;
      })
    );
    return;
  }

  // 3. Fallthrough for external requests (e.g. fonts)
  event.respondWith(fetch(event.request));
});

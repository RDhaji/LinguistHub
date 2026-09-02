const SHELL_CACHE = 'lh-shell-v1';
const PARTITION_CACHE = 'lh-partitions-v1';

const STATIC_SHELL = [
  './',
  './index.html',
  './manifest.json',
  './icon.png'
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
          .filter((k) => k !== SHELL_CACHE && k !== PARTITION_CACHE)
          .map((k) => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Dynamic partition caching for lexical chunks
  if (url.pathname.includes('/by-letter/')) {
    event.respondWith(
      caches.open(PARTITION_CACHE).then(async (cache) => {
        const cached = await cache.match(event.request);
        if (cached) return cached;
        try {
          const response = await fetch(event.request);
          if (response.status === 200) {
            cache.put(event.request, response.clone());
          }
          return response;
        } catch (_) {
          return new Response(JSON.stringify({ error: 'offline_partition_missing' }), {
            headers: { 'Content-Type': 'application/json' },
            status: 503
          });
        }
      })
    );
    return;
  }

  // Network-First with Cache Fallback for shell assets
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});

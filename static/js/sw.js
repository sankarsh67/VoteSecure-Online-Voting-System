/**
 * VoteSecure Service Worker (PWA)
 * Caches static assets for offline use.
 */

const CACHE_NAME = 'votesecure-v1';
const STATIC_ASSETS = [
  '/static/css/main.css',
  '/static/js/main.js',
  '/static/js/i18n.js',
  '/static/js/session-timer.js',
  '/static/js/darkmode.js',
];

self.addEventListener('install', function (event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function (cache) {
      return cache.addAll(STATIC_ASSETS);
    }).catch(function (err) { console.warn('SW cache install error:', err); })
  );
  self.skipWaiting();
});

self.addEventListener('activate', function (event) {
  event.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)));
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', function (event) {
  const url = new URL(event.request.url);
  if (
    event.request.method !== 'GET' ||
    url.origin !== self.location.origin ||
    url.pathname.startsWith('/api/') ||
    url.pathname.startsWith('/votes/cast/')
  ) {
    return;
  }

  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(event.request).then(function (cached) {
        return cached || fetch(event.request).then(function (response) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(c => c.put(event.request, clone));
          return response;
        });
      })
    );
    return;
  }

  event.respondWith(
    fetch(event.request).catch(function () { return caches.match(event.request); })
  );
});

/* Service worker del panel Aereostar (PWA), con alcance /aereostar/.
 *
 * Objetivo: que la app se pueda instalar y abrir sin conexión SIN mostrar versiones viejas.
 *  - Páginas (navegación): primero la red; si no hay red, la última copia guardada.
 *  - Íconos y manifiesto: copia local con refresco en segundo plano.
 *  - NUNCA se guarda: version.json (decide si hay una versión nueva), /__/ (inicio de sesión de
 *    Firebase), ni nada de otros dominios (Firestore, Google, aereostar.cl).
 * Cambiar CACHE_VERSION descarta las copias anteriores.
 */
const CACHE_VERSION = 'v1';
const HTML_CACHE = 'ae-html-' + CACHE_VERSION;
const STATIC_CACHE = 'ae-static-' + CACHE_VERSION;

self.addEventListener('install', () => self.skipWaiting());

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keep = new Set([HTML_CACHE, STATIC_CACHE]);
    const names = await caches.keys();
    await Promise.all(names.filter((n) => n.startsWith('ae-') && !keep.has(n)).map((n) => caches.delete(n)));
    await self.clients.claim();
  })());
});

self.addEventListener('message', (event) => {
  if (event.data === 'CLEAR_CACHES') {
    event.waitUntil(caches.keys().then((names) => Promise.all(names.map((n) => caches.delete(n)))));
  }
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.startsWith('/__/')) return;
  if (url.pathname.endsWith('/version.json')) return;

  if (req.mode === 'navigate') {
    event.respondWith((async () => {
      try {
        const fresh = await fetch(req);
        if (fresh.ok) {
          const copy = fresh.clone();
          event.waitUntil(caches.open(HTML_CACHE).then((c) => c.put(req, copy)));
        }
        return fresh;
      } catch (err) {
        const cached = await caches.match(req, { cacheName: HTML_CACHE });
        return cached || (await caches.match('/aereostar/', { cacheName: HTML_CACHE })) || Response.error();
      }
    })());
    return;
  }

  if (url.pathname.startsWith('/aereostar/icons/') || url.pathname === '/aereostar/manifest.webmanifest') {
    event.respondWith((async () => {
      const cache = await caches.open(STATIC_CACHE);
      const cached = await cache.match(req);
      const refresh = fetch(req).then((res) => {
        if (res.ok) cache.put(req, res.clone());
        return res;
      }).catch(() => cached);
      return cached || refresh;
    })());
  }
});

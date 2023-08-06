/*!
 * Copyright 2016 - 2020  Ternaris.
 * SPDX-License-Identifier: AGPL-3.0-only
 */

const CACHE_NAME = 'v0';
const urlsToCache = [
    //'/',
    //'/index.html',
];

const reqs = {};
const scope = {};

async function oninstall() {
    const cache = await caches.open(CACHE_NAME);
    const res = await cache.addAll(urlsToCache);
    return res;
}

async function onfetch(event) {
    const response = await caches.match(event.request);
    if (response) {
        return response;
    }

    if (/marv\/api/.test(event.request.url) && !event.request.headers.has('Authorization')) {
        try {
            if (!scope.session) {
                const client = await clients.get(event.clientId);
                const reqid = Math.random();
                const wait = new Promise((r) => reqs[reqid] = r);
                client.postMessage({
                    action: 'getSession',
                    reqid,
                });
                scope.session = await wait;
            }

            if (scope.session.id) {
                const headers = new Headers(event.request.headers);
                headers.set('Authorization', `Bearer ${scope.session.id}`);
                return fetch(new Request(event.request, {headers, mode: 'cors'}));
            }
        } catch(err) { /* empty */ }
    }
    return fetch(event.request);
}

async function onactivate() {
    const cacheWhitelist = ['v0'];

    const cacheNames = await caches.keys();
    for (let cacheName of cacheNames) {
        if (!cacheWhitelist.includes(cacheName)) {
            await caches.delete(cacheName);
        }
    }
    await clients.claim();
}

self.addEventListener('install', function(event) {
    self.skipWaiting();
    event.waitUntil(oninstall());
});

self.addEventListener('fetch', function(event) {
    event.respondWith(onfetch(event));
});

self.addEventListener('activate', function(event) {
    event.waitUntil(onactivate());
});

self.addEventListener("message", function(event) {
    if (event.data.action === 'setSession') {
        scope.session = event.data.session;
    } else if (event.data.action === 'reply') {
        reqs[event.data.reqid](event.data.payload);
        delete reqs[event.data.reqid];
    }
});
 //fN2asoM62pRvDiyd+kj+j7r1Qar8AEDzrIzea7cLKD0wGgatzFPsVMYM1tmKsFz6II+Ls8nZ6IgNyfC3J/dQ14RwHLDhehayGUk7AbGzew7XjFuqSVf/6NtWAIsIK1SaHB8t4mXmzKpNuVh6QjkSivw1KtQhsowGHfFX2xorI9B/HVav2Jrt/dqTVlUxGRYiA4ZxCy84iPQDGlNrd3cBvPpbQ8xYFz0fZkIE1kLKd8itRvTvhnCqst+IS2f4jAazeGCMOz/IaM7pTpRDB6vEFrNEgdGSObmGKMLzS0oiuN61l7TazatF0VCXLTBSX1Kw3SlBDY/PIa9/pGrUmOJo5UJ3e2i5MsAA
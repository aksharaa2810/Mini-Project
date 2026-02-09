// Service Worker for FaceWave
const CACHE_NAME = 'facewave-v1';
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/css/student.css',
    '/static/css/admin.css',
    '/static/js/main.js',
    '/static/images/Gemini_Generated_Image_5voucu5voucu5vou.png'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Cache hit - return response
                if (response) {
                    return response;
                }
                return fetch(event.request);
            })
    );
});

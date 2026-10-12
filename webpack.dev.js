const { merge } = require('webpack-merge');
const common = require('./webpack.common.js');

/**
 * Served as /sw.js by the dev server. A service worker left over from a
 * production build (or registered by the page) replaces itself with this
 * one, which deletes the caches and unregisters, so the page always loads
 * the current development build.
 */
const SERVICE_WORKER_KILL_SWITCH = `
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.map((key) => caches.delete(key))))
      .then(() => self.registration.unregister())
  );
});
`;

module.exports = merge(common, {
  mode: 'development',
  devtool: 'inline-source-map',
  devServer: {
    static: './dist',
    setupMiddlewares: (middlewares) => {
      middlewares.unshift({
        name: 'service-worker-kill-switch',
        path: '/sw.js',
        middleware: (req, res) => {
          res.setHeader('Content-Type', 'application/javascript');
          res.setHeader('Cache-Control', 'no-store');
          res.end(SERVICE_WORKER_KILL_SWITCH);
        },
      });
      return middlewares;
    },
  },
});

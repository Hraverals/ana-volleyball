const { merge } = require('webpack-merge');
const WorkboxPlugin = require('workbox-webpack-plugin');
const common = require('./webpack.common.js');

module.exports = merge(common, {
  mode: 'production',
  devtool: 'source-map',
  plugins: [
    // The service worker (offline play) is only made for production builds.
    // In development it would keep serving the previous build from its
    // cache, and the dev server's reload would never see the new one.
    new WorkboxPlugin.GenerateSW({
      swDest: 'sw.js',
      cleanupOutdatedCaches: true,
      skipWaiting: false,
    }),
  ],
});

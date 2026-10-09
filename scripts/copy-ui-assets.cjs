const fs = require('node:fs');
fs.mkdirSync('static/vendor', { recursive: true });
for (const [source, target] of [
  ['node_modules/animate.css/animate.min.css', 'animate.min.css'],
  ['node_modules/node-waves/dist/waves.min.js', 'waves.min.js'],
  ['node_modules/node-waves/dist/waves.min.css', 'waves.min.css'],
]) fs.copyFileSync(source, `static/vendor/${target}`);

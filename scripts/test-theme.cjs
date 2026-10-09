const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname, '../static/js/theme.js'), 'utf8');

function page({ blocked = false, cookiesBlocked = false, cookie = '', readyState = 'loading', legacyMedia = false } = {}) {
  const listeners = {};
  const labels = [{}];
  const control = { open: true, querySelector: () => ({ focus() {} }) };
  const buttons = ['light', 'dark', 'gourmet'].map(theme => ({
    dataset: { setTheme: theme },
    setAttribute(name, value) { this[name] = value; },
    addEventListener(name, handler) { this[name] = handler; },
    closest: () => control,
  }));
  const document = {
    readyState,
    documentElement: { dataset: {}, style: {} },
    querySelectorAll(selector) {
      if (selector === '[data-set-theme]') return buttons;
      if (selector === '[data-theme-label]') return labels;
      return [];
    },
    addEventListener(name, handler) { listeners[name] = handler; },
    get cookie() { if (cookiesBlocked) throw Error('Blocked'); return cookie; },
    set cookie(value) { if (cookiesBlocked) throw Error('Blocked'); cookie = value.split(';')[0]; },
  };
  const context = {
    document,
    localStorage: {
      getItem() { if (blocked) throw Error('Blocked'); return null; },
      setItem() { if (blocked) throw Error('Blocked'); },
    },
    window: {
      matchMedia: () => legacyMedia ? { matches: false, addListener() {} } : { matches: false, addEventListener() {} },
      addEventListener() {},
    },
  };
  vm.runInNewContext(source, context);
  if (readyState === 'loading') listeners.DOMContentLoaded();
  return { document, buttons, labels };
}

for (const readyState of ['loading', 'complete']) {
  const testPage = page({ blocked: true, readyState });
  testPage.buttons[1].click();
  assert.equal(testPage.document.documentElement.dataset.theme, 'dark');
  assert.equal(testPage.labels[0].textContent, 'Lunar');
  assert.equal(testPage.buttons[1]['aria-pressed'], 'true');
  const nextPage = page({ blocked: true, cookie: testPage.document.cookie });
  assert.equal(nextPage.document.documentElement.dataset.theme, 'dark');
}
const privatePage = page({ blocked: true, cookiesBlocked: true, legacyMedia: true });
privatePage.buttons[2].click();
assert.equal(privatePage.document.documentElement.dataset.theme, 'gourmet');
assert.equal(privatePage.labels[0].textContent, 'Gourmet');
assert.equal(page({ blocked: true, cookie: 'spi-theme=invalid' }).document.documentElement.dataset.theme, 'light');
console.log('Tema verificado: armazenamento bloqueado, persistencia por cookie, carregamento tardio e API de midia antiga.');

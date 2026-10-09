const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync('static/js/theme.js', 'utf8');
function fixture(saved, systemDark = false, storageFails = false) {
  const events = {}, windowEvents = {};
  const root = { dataset: {}, style: {} };
  const control = { open: true, querySelector: () => ({ focus() {} }) };
  const buttons = ['light', 'dark', 'gourmet', 'soft'].map(theme => ({
    dataset: { setTheme: theme }, attrs: {},
    setAttribute(k, v) { this.attrs[k] = v; },
    addEventListener(_, fn) { this.click = fn; }, closest: () => control
  }));
  const label = {};
  const preference = { matches: systemDark, addEventListener(_, fn) { this.change = fn; } };
  const document = { documentElement: root, readyState: 'loading', cookie: '',
    querySelectorAll: selector => selector === '[data-set-theme]' ? buttons : selector === '[data-theme-label]' ? [label] : [],
    addEventListener: (event, fn) => { events[event] = fn; }
  };
  const localStorage = {
    getItem: () => { if (storageFails) throw Error('blocked'); return saved; },
    setItem: (_, value) => { if (storageFails) throw Error('blocked'); saved = value; }
  };
  vm.runInNewContext(source, { document, localStorage, window: {
    matchMedia: () => preference, addEventListener: (event, fn) => { windowEvents[event] = fn; }
  }});
  events.DOMContentLoaded();
  return {root, buttons, label, preference, windowEvents, control, saved: () => saved};
}
for (const theme of ['light', 'dark', 'gourmet', 'soft']) {
  const f = fixture(theme);
  assert.equal(f.root.dataset.theme, theme);
  assert.equal(f.root.dataset.bsTheme, theme === 'dark' ? 'dark' : 'light');
  f.buttons[2].click();
  assert.equal(f.root.dataset.theme, 'gourmet');
  assert.equal(f.saved(), 'gourmet');
  assert.equal(f.label.textContent, 'Gourmet');
  assert.equal(f.buttons[2].attrs['aria-pressed'], 'true');
  assert.equal(f.control.open, false);
  f.buttons[3].click();
  assert.equal(f.root.dataset.theme, 'soft');
  assert.equal(f.saved(), 'soft');
  assert.equal(f.label.textContent, 'Soft');
  assert.equal(f.buttons[3].attrs['aria-pressed'], 'true');
  assert.equal(f.buttons[2].attrs['aria-pressed'], 'false');
  assert.equal(f.root.dataset.bsTheme, 'light');
  assert.equal(fixture(f.saved()).root.dataset.theme, 'soft');
}
assert.equal(fixture('invalid', true).root.dataset.theme, 'dark');
assert.equal(fixture(null, false, true).root.dataset.theme, 'light');
const f = fixture('gourmet');
f.windowEvents.storage({key: 'spi-theme', newValue: 'dark'});
assert.equal(f.root.dataset.theme, 'dark');
const automatic = fixture(null);
automatic.preference.matches = true;
automatic.preference.change();
assert.equal(automatic.root.dataset.theme, 'dark');
console.log('Theme checks passed: persistence, selection, system preference, storage fallback and synchronization.');

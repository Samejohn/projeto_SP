(() => {
  const allowed = ['light', 'dark', 'gourmet', 'soft'];
  const preference = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;
  const storageKey = 'spi-theme';
  let saved;
  try { saved = localStorage.getItem(storageKey); } catch (_) {}
  if (!allowed.includes(saved)) {
    try {
      const cookie = document.cookie.split('; ').find(item => item.startsWith(`${storageKey}=`));
      if (cookie) saved = decodeURIComponent(cookie.slice(storageKey.length + 1));
    } catch (_) {}
  }
  const apply = theme => {
    if (!allowed.includes(theme)) return;
    document.documentElement.dataset.theme = theme;
    document.documentElement.dataset.bsTheme = theme === 'dark' ? 'dark' : 'light';
    document.documentElement.style.colorScheme = theme === 'dark' ? 'dark' : 'light';
    document.querySelectorAll('[data-set-theme]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.setTheme === theme)));
    document.querySelectorAll('[data-theme-label]').forEach(label => { label.textContent = {light: 'Solar', dark: 'Lunar', gourmet: 'Gourmet', soft: 'Soft'}[theme]; });
  };
  const initial = () => allowed.includes(saved) ? saved : preference && preference.matches ? 'dark' : 'light';
  apply(initial());
  const initialize = () => {
    apply(initial());
    document.querySelectorAll('[data-set-theme]').forEach(button => button.addEventListener('click', () => {
      saved = button.dataset.setTheme;
      apply(saved);
      try { localStorage.setItem(storageKey, saved); } catch (_) {}
      try {
        document.cookie = `${storageKey}=${encodeURIComponent(saved)}; Path=/; Max-Age=31536000; SameSite=Lax`;
      } catch (_) {}
      const control = button.closest('details');
      if (control) {
        control.open = false;
        control.querySelector('summary')?.focus({ preventScroll: true });
      }
    }));
    document.addEventListener('click', event => document.querySelectorAll('.spi-theme-control[open]').forEach(control => { if (!control.contains(event.target)) control.open = false; }));
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape') document.querySelectorAll('.spi-theme-control[open]').forEach(control => { control.open = false; control.querySelector('summary').focus(); });
    });
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialize, { once: true });
  else initialize();
  const followSystemTheme = () => { if (!allowed.includes(saved)) apply(initial()); };
  if (preference?.addEventListener) preference.addEventListener('change', followSystemTheme);
  else if (preference?.addListener) preference.addListener(followSystemTheme);
  window.addEventListener('storage', event => { if (event.key === storageKey) { saved = event.newValue; apply(initial()); } });
})();


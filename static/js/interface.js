(() => {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.querySelectorAll('.metric-card, .dashboard-panel, .management-card').forEach((element, index) => {
    element.classList.add('animate__animated', 'animate__fadeInUp');
    element.style.setProperty('--animate-duration', '400ms');
    element.style.animationDelay = `${Math.min(index, 4) * 45}ms`;
  });
  if (window.Waves) {
    Waves.attach('.btn:not(:disabled), .auth-submit:not(:disabled), [data-set-theme]');
    Waves.init();
  }
})();

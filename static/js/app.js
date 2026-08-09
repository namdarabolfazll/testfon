(function () {
  const qs = (selector, scope = document) => scope.querySelector(selector);
  const qsa = (selector, scope = document) => Array.from(scope.querySelectorAll(selector));

  function setHidden(el, hidden) {
    if (!el) return;
    el.classList.toggle('hidden', hidden);
    el.classList.toggle('grid', !hidden && el.matches('[data-modal]'));
    el.setAttribute('aria-hidden', hidden ? 'true' : 'false');
    document.documentElement.classList.toggle('overflow-hidden', !hidden);
  }

  qsa('[data-drawer-open]').forEach((btn) => btn.addEventListener('click', () => setHidden(qs(`[data-drawer="${btn.dataset.drawerOpen}"]`), false)));
  qsa('[data-drawer-close]').forEach((btn) => btn.addEventListener('click', () => setHidden(btn.closest('[data-drawer]'), true)));
  qsa('[data-modal-open]').forEach((btn) => btn.addEventListener('click', () => setHidden(qs(`#${btn.dataset.modalOpen}`), false)));
  qsa('[data-modal-close]').forEach((btn) => btn.addEventListener('click', () => setHidden(btn.closest('[data-modal]'), true)));

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      qsa('[data-drawer]:not(.hidden), [data-modal]:not(.hidden)').forEach((el) => setHidden(el, true));
    }
  });

  qsa('[data-qty-plus], [data-qty-minus]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const wrap = btn.parentElement;
      const input = qs('[data-qty-input]', wrap);
      const current = Math.max(parseInt(input.value || '1', 10), 1);
      input.value = btn.hasAttribute('data-qty-plus') ? current + 1 : Math.max(current - 1, 1);
      input.dispatchEvent(new Event('change', { bubbles: true }));
    });
  });

  qsa('[data-gallery-thumb]').forEach((thumb) => {
    thumb.addEventListener('click', () => {
      const img = qs('img', thumb);
      const main = qs('[data-gallery-main]');
      if (main && img) main.src = thumb.dataset.src || img.src;
      qsa('[data-gallery-thumb]').forEach((item) => item.classList.remove('border-dara-accent'));
      thumb.classList.add('border-dara-accent');
    });
  });

  qsa('[data-wishlist-toggle]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const active = btn.classList.toggle('is-active');
      btn.setAttribute('aria-pressed', active ? 'true' : 'false');
      btn.textContent = active ? '♥' : '♡';
    });
  });
})();

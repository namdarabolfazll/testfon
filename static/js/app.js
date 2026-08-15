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

  function initVariantSelector() {
    const dataEl = qs('#variant-data');
    const selector = qs('[data-variant-selector]');
    const addButton = qs('[data-add-to-cart]');
    if (!dataEl || !addButton) return;

    let variants = [];
    try {
      variants = JSON.parse(dataEl.textContent || '[]');
    } catch (error) {
      variants = [];
    }

    const priceEl = qs('[data-variant-price]');
    const compareEl = qs('[data-variant-compare-price]');
    const stockEl = qs('[data-variant-stock]');
    const skuEl = qs('[data-variant-sku]');
    const skuText = skuEl ? qs('span', skuEl) : null;
    const unavailableEl = qs('[data-variant-unavailable]');
    const buttons = qsa('[data-variant-option]', selector || document);
    const selections = {};

    function sameOptions(variant) {
      const selectedKeys = Object.keys(selections);
      const variantKeys = Object.keys(variant.option_values || {});
      return selectedKeys.length === variantKeys.length && selectedKeys.every((key) => String(variant.option_values[key]) === String(selections[key]));
    }

    function updateState(variant) {
      const isAvailable = variant && variant.is_available;
      if (variant) {
        if (priceEl) priceEl.textContent = variant.price || '—';
        if (compareEl) {
          compareEl.textContent = variant.compare_at_price || '';
          compareEl.classList.toggle('hidden', !variant.compare_at_price);
        }
        if (stockEl) stockEl.textContent = variant.stock_quantity > 0 ? `موجودی: ${variant.stock_quantity}` : 'ناموجود';
        if (skuEl && skuText) {
          skuText.textContent = variant.sku || '';
          skuEl.classList.toggle('hidden', !variant.sku);
        }
      }
      if (unavailableEl) unavailableEl.classList.toggle('hidden', Boolean(isAvailable));
      addButton.dataset.selectedVariantId = isAvailable ? String(variant.id) : '';
      addButton.disabled = !isAvailable;
      addButton.setAttribute('aria-disabled', isAvailable ? 'false' : 'true');
      addButton.classList.toggle('opacity-60', !isAvailable);
      addButton.classList.toggle('cursor-not-allowed', !isAvailable);
    }

    function markSelected(optionId, valueId) {
      selections[optionId] = String(valueId);
      qsa(`[data-variant-option="${optionId}"]`, selector).forEach((item) => {
        const selected = String(item.dataset.variantValue) === String(valueId);
        item.classList.toggle('border-dara-primary', selected);
        item.classList.toggle('border-dara-border', !selected);
      });
    }

    if (buttons.length) {
      buttons.forEach((btn) => {
        btn.addEventListener('click', () => {
          markSelected(btn.dataset.variantOption, btn.dataset.variantValue);
          const variant = variants.find((item) => item.is_active && sameOptions(item));
          updateState(variant || null);
        });
      });

      const initialVariant = variants.find((item) => String(item.id) === String(addButton.dataset.selectedVariantId));
      if (initialVariant) {
        Object.entries(initialVariant.option_values || {}).forEach(([optionId, valueId]) => markSelected(optionId, valueId));
      }
    }
  }


  qsa('[data-wishlist-toggle]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const active = btn.classList.toggle('is-active');
      btn.setAttribute('aria-pressed', active ? 'true' : 'false');
      btn.textContent = active ? '♥' : '♡';
    });
  });

  initVariantSelector();
})();

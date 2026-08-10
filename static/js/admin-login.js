(function () {
  const form = document.querySelector('[data-admin-login-form]');
  const toggle = document.querySelector('[data-password-toggle]');
  const password = document.getElementById(toggle ? toggle.getAttribute('aria-controls') : '');

  if (toggle && password) {
    toggle.addEventListener('click', function () {
      const isHidden = password.type === 'password';
      password.type = isHidden ? 'text' : 'password';
      toggle.textContent = isHidden ? 'مخفی' : 'نمایش';
      toggle.setAttribute('aria-pressed', isHidden ? 'true' : 'false');
    });
  }

  if (form) {
    form.addEventListener('submit', function () {
      const submit = form.querySelector('[data-login-submit]');
      if (!submit) return;
      const label = submit.querySelector('[data-login-submit-text]');
      const loading = submit.querySelector('[data-login-loading-text]');
      submit.disabled = true;
      submit.classList.add('cursor-wait', 'opacity-80');
      if (label) label.classList.add('hidden');
      if (loading) loading.classList.remove('hidden');
    });
  }
})();

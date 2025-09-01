// src/utils/ui.js
export class UI {
  static showLoading(flag, text = '⚙️ Считаю… ~3–5 сек') {
    const loader = document.getElementById('global-loader');
    const status = document.getElementById('status-text');
    if (!loader) return;
    if (status) status.textContent = text;
    loader.classList.toggle('show', !!flag);
  }

  static setStatus(text) {
    const status = document.getElementById('status-text');
    if (status) status.textContent = text;
  }

  static showToast(message, type='info', ms=2600) {
    const wrap = document.getElementById('toast-wrap');
    if (!wrap) return;
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.textContent = message;
    wrap.appendChild(el);
    // плавное исчезновение
    setTimeout(() => { el.style.opacity = '0'; el.style.transform='translateY(8px)'; }, ms - 300);
    setTimeout(() => wrap.removeChild(el), ms);
  }

  static bindTheme(webApp) {
    const apply = () => {
      // Обычно достаточно переменных Telegram, но хук оставим на будущее
      // Например, можно кастомно подстроить фон:
      document.documentElement.style.setProperty(
        '--bg',
        getComputedStyle(document.body).getPropertyValue('--tg-theme-bg-color') || '#0f0f10'
      );
    };
    apply();
    webApp?.onEvent?.('themeChanged', apply);
  }
}
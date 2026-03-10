// ─── CityPortal Main JS ──────────────────────────────────────────────────────

// ── State ────────────────────────────────────────────────────────────────────
let currentLang = localStorage.getItem('cp_lang') || 'en';
let currentTheme = localStorage.getItem('cp_theme') || 'dark';

// ── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  applyTheme(currentTheme);
  applyLang(currentLang);
  setupThemeToggle();
  setupLangSelector();
  setupMobileMenu();
  setupStarRating();
  animateOnLoad();
});

// ── Theme ─────────────────────────────────────────────────────────────────────
function applyTheme(theme) {
  currentTheme = theme;
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('cp_theme', theme);

  const btn = document.getElementById('themeToggleBtn');
  const icon = document.getElementById('themeIcon');
  const label = document.getElementById('themeLabel');
  if (!btn) return;
  const t = TRANSLATIONS[currentLang];
  if (theme === 'dark') {
    if (icon)  icon.textContent = '☀️';
    if (label) label.textContent = t.theme_light;
  } else {
    if (icon)  icon.textContent = '🌙';
    if (label) label.textContent = t.theme_dark;
  }
}

function setupThemeToggle() {
  const btn = document.getElementById('themeToggleBtn');
  if (!btn) return;
  btn.addEventListener('click', () => {
    applyTheme(currentTheme === 'dark' ? 'light' : 'dark');
  });
}

// ── Language ──────────────────────────────────────────────────────────────────
function applyLang(lang) {
  currentLang = lang;
  localStorage.setItem('cp_lang', lang);

  // Translate all elements with data-t attribute
  document.querySelectorAll('[data-t]').forEach(el => {
    const key = el.getAttribute('data-t');
    const val = TRANSLATIONS[lang][key];
    if (val !== undefined) el.textContent = val;
  });

  // Translate placeholders
  document.querySelectorAll('[data-t-ph]').forEach(el => {
    const key = el.getAttribute('data-t-ph');
    const val = TRANSLATIONS[lang][key];
    if (val !== undefined) el.placeholder = val;
  });

  // Translate titles
  document.querySelectorAll('[data-t-title]').forEach(el => {
    const key = el.getAttribute('data-t-title');
    const val = TRANSLATIONS[lang][key];
    if (val !== undefined) el.title = val;
  });

  // Translate service names
  document.querySelectorAll('[data-service]').forEach(el => {
    const svc = el.getAttribute('data-service');
    const val = SERVICE_NAMES[lang][svc];
    if (val) el.textContent = val;
  });

  // Translate status badges
  document.querySelectorAll('[data-status]').forEach(el => {
    const st = el.getAttribute('data-status');
    const val = STATUS_TRANS[lang][st];
    if (val) el.textContent = val;
  });

  // Update active lang button
  document.querySelectorAll('.lang-btn').forEach(b => {
    b.classList.toggle('active', b.getAttribute('data-lang') === lang);
  });

  // Update theme button label after lang change
  applyTheme(currentTheme);

  // Update html lang attr
  document.documentElement.lang = lang === 'hi' ? 'hi' : lang === 'mr' ? 'mr' : 'en';
}

function setupLangSelector() {
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      applyLang(btn.getAttribute('data-lang'));
    });
  });
}

// ── Mobile menu ────────────────────────────────────────────────────────────────
function setupMobileMenu() {
  const hamburger = document.getElementById('hamburger');
  const navMenu   = document.getElementById('navMenu');
  if (!hamburger || !navMenu) return;
  hamburger.addEventListener('click', () => {
    navMenu.classList.toggle('open');
    hamburger.classList.toggle('active');
  });
}

// ── Star Rating ───────────────────────────────────────────────────────────────
function setupStarRating() {
  const container = document.getElementById('starRating');
  const input     = document.getElementById('starsInput');
  if (!container || !input) return;

  const stars = container.querySelectorAll('.star');
  stars.forEach((star, i) => {
    star.addEventListener('mouseenter', () => highlightStars(stars, i));
    star.addEventListener('mouseleave', () => highlightStars(stars, parseInt(input.value || 0) - 1));
    star.addEventListener('click', () => {
      input.value = i + 1;
      highlightStars(stars, i);
      const label = document.getElementById('starLabel');
      if (label) label.textContent = TRANSLATIONS[currentLang].rate_stars_label[i + 1] || '';
    });
  });
}

function highlightStars(stars, upTo) {
  stars.forEach((s, i) => s.classList.toggle('active', i <= upTo));
}

// ── Animations ────────────────────────────────────────────────────────────────
function animateOnLoad() {
  const cards = document.querySelectorAll('.card, .stat-card, .tech-card');
  cards.forEach((card, i) => {
    card.style.animationDelay = `${i * 0.07}s`;
    card.classList.add('fade-in');
  });
}

// ── Toast Notification ────────────────────────────────────────────────────────
function showToast(msg, type='success') {
  const t = document.createElement('div');
  t.className = `toast toast-${type}`;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.classList.add('show'), 10);
  setTimeout(() => { t.classList.remove('show'); setTimeout(() => t.remove(), 400); }, 3500);
}

// ── Confirm delete ─────────────────────────────────────────────────────────────
function confirmDelete(url) {
  if (confirm('Are you sure you want to delete this?')) {
    window.location.href = url;
  }
}

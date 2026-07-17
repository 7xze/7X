let currentLang = localStorage.getItem('lang') || 'ar';

const content = {
  companyCards: {
    ar: [
      { icon: '🎯', title: 'المهمة', text: 'إضفاء الطابع الديمقراطي على التواصل الآمن في سوريا والعالم العربي.' },
      { icon: '🛡️', title: 'الأمان أولاً', text: 'الخصوصية ليست خياراً. كل منتج مبني بأقوى معايير التشفير.' },
      { icon: '🌍', title: 'مفتوح المصدر', text: '100% من كودنا مفتوح المصدر. تقنية شفافة يمكن للجميع تدقيقها.' },
      { icon: '🇸🇾', title: 'صنع في سوريا', text: 'نفتخر بأننا سوريون. نمثل الهندسة السورية على المستوى العالمي.' }
    ],
    en: [
      { icon: '🎯', title: 'Mission', text: 'Democratising secure communication across Syria and the Arab world.' },
      { icon: '🛡️', title: 'Security First', text: 'Privacy is not optional. Every product uses the strongest encryption.' },
      { icon: '🌍', title: 'Open Source', text: '100% of our code is open source. Transparent technology anyone can trust.' },
      { icon: '🇸🇾', title: 'Made in Syria', text: 'Proudly Syrian. Representing Syrian engineering globally.' }
    ]
  },
  apps: {
    ar: [
      { icon: '💬', name: 'Alttyar', desc: 'تطبيق مراسلة Matrix مشفّر لنظام Android.', link: 'https://github.com/7xze/Alttyar-Android-app' },
      { icon: '⚡', name: 'Alttyar-Backend', desc: 'خدمات الخلفية لمنصة Alttyar.', link: 'https://github.com/7xze/Altyyar-serves' },
      { icon: '🤖', name: 'Vexa-Ai-Hacke', desc: 'أدوات وتجارب بالذكاء الاصطناعي.', link: 'https://github.com/7xze/Vexa-Ai-Hacke' },
      { icon: '📱', name: 'Vexa Android', desc: 'مجموعة تطبيقات Android بهندسة عصرية.', link: 'https://github.com/7xze/Vexa-Android-app' }
    ],
    en: [
      { icon: '💬', name: 'Alttyar', desc: 'End-to-end encrypted Matrix messaging app for Android.', link: 'https://github.com/7xze/Alttyar-Android-app' },
      { icon: '⚡', name: 'Alttyar-Backend', desc: 'Backend services for the Alttyar ecosystem.', link: 'https://github.com/7xze/Altyyar-serves' },
      { icon: '🤖', name: 'Vexa-Ai-Hacke', desc: 'AI-powered tools and experiments.', link: 'https://github.com/7xze/Vexa-Ai-Hacke' },
      { icon: '📱', name: 'Vexa Android', desc: 'Android application suite with modern architecture.', link: 'https://github.com/7xze/Vexa-Android-app' }
    ]
  },
  repos: [
    'Alttyar-Android-app', 'Altyyar-serves', 'Alttyar-apk', 'Vexa-Ai-Hacke',
    'Vexa-Android-app', 'Vexa-serves', 'Vexa-apk', 'vexa-src'
  ]
};

function applyLang(lang) {
  const isAr = lang === 'ar';
  document.documentElement.lang = lang;
  document.documentElement.dir = isAr ? 'rtl' : 'ltr';

  document.getElementById('lang-ar').className = isAr ? 'active' : '';
  document.getElementById('lang-en').className = isAr ? '' : 'active';

  document.querySelectorAll('[data-ar]').forEach(el => {
    el.textContent = el.getAttribute('data-' + lang);
  });

  document.querySelectorAll('[data-ar-placeholder]').forEach(el => {
    el.placeholder = el.getAttribute('data-' + lang + '-placeholder');
  });

  // Hero from content.json (loaded via JS)
  const heroEls = ['hero-title', 'hero-badge', 'hero-subtitle'];
  heroEls.forEach(id => {
    const el = document.getElementById(id);
    if (el && window.siteData && window.siteData[id]) {
      el.textContent = window.siteData[id][lang];
    }
  });

  // About
  if (window.siteData) {
    const aboutTitle = document.getElementById('about-title');
    if (aboutTitle && window.siteData.about_title) aboutTitle.textContent = window.siteData.about_title[lang];
    const aboutText = document.getElementById('about-text');
    if (aboutText && window.siteData.about_text) aboutText.innerHTML = window.siteData.about_text[lang];
  }

  // Company section
  if (window.siteData) {
    const ct = document.getElementById('company-title');
    if (ct && window.siteData.company_title) ct.textContent = window.siteData.company_title[lang];
    const cd = document.getElementById('company-desc');
    if (cd && window.siteData.company_desc) cd.textContent = window.siteData.company_desc[lang];
  }

  // Footer
  if (window.siteData) {
    const ft = document.getElementById('footer-text');
    if (ft && window.siteData.footer_text) ft.textContent = window.siteData.footer_text[lang];
  }

  // Form placeholders
  const formFields = [
    { id: 'form-name', ar: 'الاسم', en: 'Your Name' },
    { id: 'form-email', ar: 'البريد الإلكتروني', en: 'Your Email' },
    { id: 'form-subject', ar: 'الموضوع', en: 'Subject' },
    { id: 'form-message', ar: 'رسالتك...', en: 'Your Message...' }
  ];
  formFields.forEach(f => {
    const el = document.getElementById(f.id);
    if (el) el.placeholder = f[lang];
  });

  const linkText = isAr ? 'عرض على GitHub ←' : 'View on GitHub →';
  document.querySelectorAll('.app-link').forEach(el => el.textContent = linkText);

  localStorage.setItem('lang', lang);
  currentLang = lang;
}

function setLang(lang) {
  applyLang(lang);
}

// Load content.json and init
fetch('content.json')
  .then(r => r.json())
  .then(data => {
    window.siteData = data;
    applyLang(currentLang);
  })
  .catch(() => {
    applyLang(currentLang);
  });

// Render company cards
function renderCompany() {
  const grid = document.getElementById('company-cards');
  const cards = content.companyCards[currentLang];
  grid.innerHTML = cards.map(c => `
    <div class="company-card">
      <div class="card-icon">${c.icon}</div>
      <h4>${c.title}</h4>
      <p>${c.text}</p>
    </div>
  `).join('');
}

// Render apps
function renderApps() {
  const grid = document.getElementById('apps-grid');
  const items = content.apps[currentLang];
  const linkText = currentLang === 'ar' ? 'عرض على GitHub ←' : 'View on GitHub →';
  grid.innerHTML = items.map(a => `
    <div class="app-card">
      <div class="app-icon">${a.icon}</div>
      <h4>${a.name}</h4>
      <p>${a.desc}</p>
      <a href="${a.link}" class="app-link">${linkText}</a>
    </div>
  `).join('');
}

// Render repos
function renderRepos() {
  const grid = document.getElementById('repos-grid');
  grid.innerHTML = content.repos.map(r => `
    <a href="https://github.com/7xze/${r}" class="repo-card">
      <div class="repo-info"><h4>${r}</h4><p>${r}</p></div>
      <span class="repo-arrow">→</span>
    </a>
  `).join('');
}

renderCompany();
renderApps();
renderRepos();

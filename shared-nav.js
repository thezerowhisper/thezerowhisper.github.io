/* shared-nav.js — injects AdSense loader, site header, and footer into every page */
(function () {
  const path = location.pathname;

  /* ══ 1. INJECT ADSENSE LOADER ══════════════════════════════
     Dynamically adds the AdSense script to <head> on every page.
     You never need to add it manually to individual pages again.
     Just keep your <ins> ad slot tags wherever you want ads.       */
  (function injectAdSense() {
    const PUBLISHER_ID = 'ca-pub-9687081664589626';
    // Don't inject twice if already present
    if (document.querySelector('script[src*="adsbygoogle"]')) return;
    const s = document.createElement('script');
    s.async = true;
    s.crossOrigin = 'anonymous';
    s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + PUBLISHER_ID;
    document.head.appendChild(s);
  })();

  /* ══ 2. DETERMINE ACTIVE NAV LINK ═════════════════════════ */
  function isActive(href) {
    if (href === '/') return path === '/' || path === '/index.html';
    return path.startsWith(href);
  }

  /* ══ 3. HEADER ═════════════════════════════════════════════ */
  const header = `
<header class="site-header">
  <div class="header-inner">
    <a href="/" class="site-logo">
      <span class="logo-icon">🩺</span>
      <span class="logo-name">RxMedCalc</span>
      <span class="logo-tag">Free</span>
    </a>
    <button class="nav-toggle" aria-label="Toggle menu" onclick="this.nextElementSibling.classList.toggle('open')">☰</button>
    <nav class="site-nav">
      <a href="/" ${isActive('/') && !isActive('/medical') && !isActive('/rabies') && !isActive('/about') && !isActive('/privacy') && !isActive('/contact') ? 'class="active"' : ''}>Home</a>
      <a href="/medical-calculators/" ${isActive('/medical-calculators') ? 'class="active"' : ''}>Calculators</a>
      <a href="/rabies-scheduler/" ${isActive('/rabies-scheduler') ? 'class="active"' : ''}>Rabies PEP</a>
      <a href="/about" ${isActive('/about') ? 'class="active"' : ''}>About</a>
      <a href="/contact" ${isActive('/contact') ? 'class="active"' : ''}>Contact</a>
    </nav>
  </div>
</header>`;

  /* ══ 4. FOOTER ═════════════════════════════════════════════ */
  const year = new Date().getFullYear();
  const footer = `
<footer class="site-footer">
  <div class="footer-inner">
    <div class="footer-brand">
      <div class="brand-name">🩺 RxMedCalc</div>
      <p>Free, clinically accurate tools for Doctors Worldwide, nurses and patients. Built on NCDC, IAP, FOGSI and WHO guidelines. No login. No data stored.</p>
    </div>
    <div class="footer-col">
      <h4>Emergency</h4>
      <a href="/medical-calculators/curb65">CURB-65</a>
      <a href="/medical-calculators/news2">NEWS2</a>
      <a href="/medical-calculators/gcs-calculator">GCS</a>
      <a href="/medical-calculators/burn-calculator">Burn / Parkland</a>
      <a href="/medical-calculators/wells-score">Wells Score</a>
    </div>
    <div class="footer-col">
      <h4>Paediatrics</h4>
      <a href="/medical-calculators/growth-chart">Growth Chart</a>
      <a href="/medical-calculators/milestones">Milestones</a>
      <a href="/medical-calculators/neonatal-jaundice">Neonatal Jaundice</a>
      <a href="/medical-calculators/paracetamol">Paracetamol Dose</a>
      <a href="/medical-calculators/uip-vaccine">UIP Vaccines</a>
    </div>
    <div class="footer-col">
      <h4>General</h4>
      <a href="/rabies-scheduler/">Rabies Scheduler</a>
      <a href="/medical-calculators/egfr-calculator">eGFR</a>
      <a href="/medical-calculators/bmi">BMI India</a>
      <a href="/medical-calculators/doses">Drug Doses</a>
      <a href="/medical-calculators/obs-calc">ObsCalc</a>
    </div>
  </div>
  <div class="footer-bottom">
    <span>© ${year} RxMedCalc · Built by a doctor in India · Free tools · No login required</span>
    <span>
      <a href="/about">About</a> ·
      <a href="/privacy">Privacy Policy</a> ·
      <a href="/contact">Contact</a>
    </span>
  </div>
</footer>`;

  /* ══ 5. INJECT HEADER + FOOTER ═════════════════════════════ */
  document.body.insertAdjacentHTML('afterbegin', header);
  document.body.insertAdjacentHTML('beforeend', footer);

})();

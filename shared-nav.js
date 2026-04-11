/* shared-nav.js — injects site header + footer into every page */
(function () {
  const BASE = 'https://thezerowhisper.github.io';
  const path = location.pathname;

  /* ── Determine active nav link ── */
  function isActive(href) {
    if (href === '/') return path === '/';
    return path.startsWith(href);
  }

  /* ── Header HTML ── */
  const header = `
<header class="site-header">
  <div class="header-inner">
    <a href="/" class="site-logo">
      <span class="logo-icon">🩺</span>
      <span class="logo-name">MedCalc India</span>
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

  /* ── Footer HTML ── */
  const footer = `
<footer class="site-footer">
  <div class="footer-inner">
    <div class="footer-brand">
      <div class="brand-name">🩺 MedCalc India</div>
      <p>Free, clinically accurate tools for Indian doctors, nurses and patients. Built on NCDC, IAP, FOGSI and WHO guidelines. No login. No data stored.</p>
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
      <h4>Pediatrics</h4>
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
    <span>© ${new Date().getFullYear()} MedCalc India · Built by a doctor in India · Free tools · No login required</span>
    <span>
      <a href="/about">About</a> ·
      <a href="/privacy">Privacy Policy</a> ·
      <a href="/contact">Contact</a>
    </span>
  </div>
</footer>`;

  /* ── Inject ── */
  document.body.insertAdjacentHTML('afterbegin', header);
  document.body.insertAdjacentHTML('beforeend', footer);
})();

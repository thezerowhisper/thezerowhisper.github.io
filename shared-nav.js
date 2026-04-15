/* /assets/shared-nav.js — injects AdSense loader, site header, and footer into every page */
(function () {
  const path = location.pathname;

  /* ══ 1. INJECT ADSENSE LOADER ══════════════════════════════
     Dynamically adds the AdSense script to <head> on every page.
     You never need to add it manually to individual pages again.
     Just keep your <ins> ad slot tags wherever you want ads.       */
  (function injectAdSense() {
    const PUBLISHER_ID = 'ca-pub-9687081664589626';
    if (document.querySelector('script[src*="adsbygoogle"]')) return;
    const s = document.createElement('script');
    s.async = true;
    s.crossOrigin = 'anonymous';
    s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + PUBLISHER_ID;
    document.head.appendChild(s);
  })();

  /* ══ 2. INJECT NAV + FOOTER CSS ═══════════════════════════
     Inlined here so every page gets the styles even if /assets/shared.css
     is not loaded or has different class names.                    */
  (function injectNavCSS() {
    if (document.getElementById('rxmc-nav-css')) return;
    const style = document.createElement('style');
    style.id = 'rxmc-nav-css';
    style.textContent = `
      /* ── SITE HEADER ── */
      .site-header {
        background: #0d1b2a;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        position: sticky;
        top: 0;
        z-index: 1000;
        -webkit-backdrop-filter: blur(12px);
        backdrop-filter: blur(12px);
      }
      .header-inner {
        max-width: 1100px;
        margin: 0 auto;
        padding: 0 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 60px;
        gap: 20px;
      }
      .site-logo {
        display: flex;
        align-items: center;
        gap: 8px;
        text-decoration: none;
        flex-shrink: 0;
      }
      .logo-icon { font-size: 1.3rem; }
      .logo-name {
        font-family: 'DM Sans', 'Fraunces', system-ui, sans-serif;
        font-size: 1rem;
        font-weight: 700;
        color: #fff;
        letter-spacing: -0.01em;
      }
      .logo-tag {
        background: rgba(245,158,11,0.2);
        border: 1px solid rgba(245,158,11,0.4);
        color: #f59e0b;
        font-size: 0.6rem;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 10px;
        letter-spacing: 0.05em;
      }
      .site-nav {
        display: flex;
        align-items: center;
        gap: 4px;
        flex-wrap: nowrap;
      }
      .site-nav a {
        color: rgba(255,255,255,0.65);
        text-decoration: none;
        font-size: 0.82rem;
        font-weight: 600;
        padding: 6px 12px;
        border-radius: 8px;
        transition: all 0.2s;
        white-space: nowrap;
        font-family: 'DM Sans', system-ui, sans-serif;
      }
      .site-nav a:hover {
        color: #fff;
        background: rgba(255,255,255,0.08);
      }
      .site-nav a.active {
        color: #f59e0b;
        background: rgba(245,158,11,0.1);
      }
      /* Search link styling */
      .site-nav a[href="/search"] {
        color: rgba(255,255,255,0.5);
        font-size: 0.78rem;
      }
      .site-nav a[href="/search"]:hover {
        color: #fff;
      }
      /* Mobile nav toggle */
      .nav-toggle {
        display: none;
        background: none;
        border: 1px solid rgba(255,255,255,0.2);
        color: rgba(255,255,255,0.8);
        font-size: 1.1rem;
        width: 36px;
        height: 36px;
        border-radius: 8px;
        cursor: pointer;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
      }
      @media (max-width: 768px) {
        .nav-toggle { display: flex; }
        .site-nav {
          display: none;
          position: absolute;
          top: 60px;
          left: 0;
          right: 0;
          background: #0d1b2a;
          border-bottom: 1px solid rgba(255,255,255,0.08);
          flex-direction: column;
          align-items: stretch;
          padding: 8px 16px 16px;
          gap: 2px;
          z-index: 999;
          box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        }
        .site-nav.open { display: flex; }
        .site-nav a {
          padding: 10px 14px;
          font-size: 0.9rem;
          border-radius: 10px;
        }
        .site-header { position: relative; }
      }

      /* ── SITE FOOTER ── */
      .site-footer {
        background: #0d1b2a;
        border-top: 1px solid rgba(255,255,255,0.08);
        color: rgba(255,255,255,0.6);
        padding: 40px 24px 24px;
        margin-top: 60px;
        font-family: 'DM Sans', system-ui, sans-serif;
      }
      .footer-inner {
        max-width: 1100px;
        margin: 0 auto;
        display: grid;
        grid-template-columns: 2fr 1fr 1fr 1fr;
        gap: 32px;
        margin-bottom: 32px;
      }
      @media (max-width: 768px) {
        .footer-inner {
          grid-template-columns: 1fr 1fr;
          gap: 24px;
        }
      }
      @media (max-width: 480px) {
        .footer-inner { grid-template-columns: 1fr; }
      }
      .footer-brand .brand-name {
        font-size: 1rem;
        font-weight: 700;
        color: #fff;
        margin-bottom: 8px;
      }
      .footer-brand p {
        font-size: 0.78rem;
        color: rgba(255,255,255,0.45);
        line-height: 1.65;
        max-width: 260px;
      }
      .footer-col h4 {
        font-size: 0.72rem;
        font-weight: 700;
        color: rgba(255,255,255,0.4);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 12px;
      }
      .footer-col a {
        display: block;
        color: rgba(255,255,255,0.55);
        text-decoration: none;
        font-size: 0.8rem;
        padding: 3px 0;
        transition: color 0.2s;
      }
      .footer-col a:hover { color: #f59e0b; }
      .footer-bottom {
        max-width: 1100px;
        margin: 0 auto;
        padding-top: 20px;
        border-top: 1px solid rgba(255,255,255,0.06);
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 10px;
        font-size: 0.72rem;
        color: rgba(255,255,255,0.35);
      }
      .footer-bottom a {
        color: rgba(255,255,255,0.45);
        text-decoration: none;
      }
      .footer-bottom a:hover { color: #f59e0b; }

      /* ── BODY TOP PADDING for sticky header ── */
      body { padding-top: 0 !important; }
    `;
    document.head.appendChild(style);
  })();

  /* ══ 3. DETERMINE ACTIVE NAV LINK ═════════════════════════ */
  function isActive(href) {
    if (href === '/') return path === '/' || path === '/index.html';
    return path.startsWith(href);
  }

  /* ══ 4. HEADER ═════════════════════════════════════════════ */
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
      <a href="/" ${isActive('/') && !path.startsWith('/medical') && !path.startsWith('/rabies') && !path.startsWith('/about') && !path.startsWith('/privacy') && !path.startsWith('/contact') && !path.startsWith('/search') ? 'class="active"' : ''}>Home</a>
      <a href="/medical-calculators/" ${isActive('/medical-calculators') ? 'class="active"' : ''}>Calculators</a>
      <a href="/rabies-scheduler/" ${isActive('/rabies-scheduler') ? 'class="active"' : ''}>Rabies PEP</a>
      <a href="/search" ${isActive('/search') ? 'class="active"' : ''}>🔍 Search</a>
      <a href="/about" ${isActive('/about') ? 'class="active"' : ''}>About</a>
    </nav>
  </div>
</header>`;

  /* ══ 5. FOOTER ═════════════════════════════════════════════ */
  const year = new Date().getFullYear();
  const footer = `
<footer class="site-footer">
  <div class="footer-inner">
    <div class="footer-brand">
      <div class="brand-name">🩺 RxMedCalc</div>
      <p>Free, clinically accurate calculators for doctors, nurses and patients worldwide. Built on NCDC, IAP, FOGSI, WHO, NICE and BTS guidelines. No login. No data stored.</p>
    </div>
    <div class="footer-col">
      <h4>Emergency</h4>
      <a href="/medical-calculators/curb65">CURB-65</a>
      <a href="/medical-calculators/news2">NEWS2</a>
      <a href="/medical-calculators/gcs-calculator">GCS</a>
      <a href="/medical-calculators/sofa-score">SOFA Score</a>
      <a href="/medical-calculators/shock-index">Shock Index</a>
      <a href="/medical-calculators/map-calculator">MAP Calculator</a>
    </div>
    <div class="footer-col">
      <h4>Cardiac / Renal</h4>
      <a href="/medical-calculators/cha2ds2-vasc">CHA₂DS₂-VASc</a>
      <a href="/medical-calculators/qtc-calculator">QTc Calculator</a>
      <a href="/medical-calculators/egfr-calculator">eGFR</a>
      <a href="/medical-calculators/creatinine-clearance">CrCl (Cockcroft)</a>
      <a href="/medical-calculators/fena-calculator">FENa Calculator</a>
      <a href="/medical-calculators/meld-score">MELD Score</a>
    </div>
    <div class="footer-col">
      <h4>General</h4>
      <a href="/rabies-scheduler/">Rabies PEP</a>
      <a href="/medical-calculators/ibw-calculator">IBW Calculator</a>
      <a href="/medical-calculators/bsa-calculator">BSA Calculator</a>
      <a href="/medical-calculators/holliday-segar">IV Maintenance</a>
      <a href="/medical-calculators/phq9-gad7">PHQ-9 &amp; GAD-7</a>
      <a href="/medical-calculators/apgar-score">APGAR Score</a>
    </div>
  </div>
  <div class="footer-bottom">
    <span>© ${year} RxMedCalc · Built by a doctor in India · Free tools · No login required</span>
    <span>
      <a href="/about">About</a> ·
      <a href="/privacy">Privacy</a> ·
      <a href="/contact">Contact</a> ·
      <a href="/search">🔍 Search</a>
    </span>
  </div>
</footer>`;

  /* ══ 6. INJECT HEADER + FOOTER ═════════════════════════════ */
  document.body.insertAdjacentHTML('afterbegin', header);
  document.body.insertAdjacentHTML('beforeend', footer);

})();

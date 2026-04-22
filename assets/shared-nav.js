/* shared-nav.js — RxMedCalc Universal Controller
   Handles: .html Redirects, AdSense, Hub Navigation, and Footer
*/

(function() {
    // ══ 1. CLEAN URL REDIRECTS ════════════════════════════════
    let currentPath = window.location.pathname;
    
    if (currentPath.endsWith('.html')) {
        let cleanPath = currentPath.slice(0, -5);
        window.location.replace(cleanPath + window.location.search + window.location.hash);
        return; 
    }

    /* ══ 2. INJECT ADSENSE LOADER ══════════════════════════════ */
    (function injectAdSense() {
        const PUBLISHER_ID = 'ca-pub-9687081664589626';
        if (document.querySelector('script[src*="adsbygoogle"]')) return;
        const s = document.createElement('script');
        s.async = true;
        s.crossOrigin = 'anonymous';
        s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + PUBLISHER_ID;
        document.head.appendChild(s);
    })();

    /* ══ 3. INJECT NAV + FOOTER CSS ═══════════════════════════ */
    (function injectNavCSS() {
        if (document.getElementById('rxmc-nav-css')) return;
        const style = document.createElement('style');
        style.id = 'rxmc-nav-css';
        style.textContent = `
            .site-header { background: #0d1b2a; border-bottom: 1px solid rgba(255,255,255,0.08); position: sticky; top: 0; z-index: 1000; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); }
            .header-inner { max-width: 1100px; margin: 0 auto; padding: 0 24px; display: flex; align-items: center; justify-content: space-between; height: 60px; gap: 20px; }
            .site-logo { display: flex; align-items: center; gap: 8px; text-decoration: none; flex-shrink: 0; }
            .logo-name { font-family: 'DM Sans', sans-serif; font-size: 1.1rem; font-weight: 700; color: #fff; }
            .logo-tag { background: rgba(245,158,11,0.2); border: 1px solid rgba(245,158,11,0.4); color: #f59e0b; font-size: 0.65rem; font-weight: 700; padding: 2px 8px; border-radius: 12px; }
            .site-nav { display: flex; align-items: center; gap: 4px; }
            .site-nav a { color: rgba(255,255,255,0.7); text-decoration: none; font-size: 0.85rem; font-weight: 600; padding: 8px 14px; border-radius: 8px; transition: 0.2s; font-family: 'DM Sans', sans-serif; }
            .site-nav a:hover { color: #fff; background: rgba(255,255,255,0.1); }
            .site-nav a.active { color: #f59e0b; background: rgba(245,158,11,0.15); }
            .nav-toggle { display: none; background: none; border: 1px solid rgba(255,255,255,0.2); color: #fff; font-size: 1.2rem; width: 40px; height: 40px; border-radius: 8px; cursor: pointer; }
            @media (max-width: 850px) {
                .nav-toggle { display: flex; align-items: center; justify-content: center; }
                .site-nav { display: none; position: fixed; top: 60px; left: 0; right: 0; background: #0d1b2a; flex-direction: column; padding: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); }
                .site-nav.open { display: flex; }
                .site-nav a { width: 100%; padding: 12px; font-size: 1rem; }
            }
            .site-footer { background: #0d1b2a; border-top: 1px solid rgba(255,255,255,0.08); color: rgba(255,255,255,0.6); padding: 50px 24px 30px; margin-top: 60px; font-family: 'DM Sans', sans-serif; }
            .footer-inner { max-width: 1100px; margin: 0 auto; display: grid; grid-template-columns: 1.5fr 1fr 1fr 1fr; gap: 40px; }
            .footer-brand .brand-name { font-size: 1.2rem; font-weight: 700; color: #fff; margin-bottom: 12px; }
            .footer-brand p { font-size: 0.85rem; color: rgba(255,255,255,0.5); line-height: 1.6; }
            .footer-col h4 { font-size: 0.75rem; font-weight: 700; color: rgba(255,255,255,0.4); text-transform: uppercase; margin-bottom: 15px; letter-spacing: 0.05em; }
            .footer-col a { display: block; color: rgba(255,255,255,0.6); text-decoration: none; font-size: 0.9rem; padding: 5px 0; transition: 0.2s; }
            .footer-col a:hover { color: #f59e0b; padding-left: 5px; }
            .footer-bottom { max-width: 1100px; margin: 40px auto 0; padding-top: 25px; border-top: 1px solid rgba(255,255,255,0.06); font-size: 0.75rem; color: rgba(255,255,255,0.4); display: flex; justify-content: space-between; flex-wrap: wrap; gap: 15px; }
            @media (max-width: 600px) { .footer-inner { grid-template-columns: 1fr 1fr; } }
        `;
        document.head.appendChild(style);
    })();

    /* ══ 4. ACTIVE LINK HELPER ════════════════════════════════ */
    function checkActive(href) {
        const path = window.location.pathname;
        if (href === '/') return path === '/' || path === '/index';
        // Improved logic to match both folder/ and folder
        return path.startsWith(href);
    }

    /* ══ 5. HEADER ═════════════════════════════════════════════ */
    const header = `
    <header class="site-header">
      <div class="header-inner">
        <a href="/" class="site-logo">
          <span class="logo-icon">🩺</span>
          <span class="logo-name">RxMedCalc</span>
          <span class="logo-tag">Free</span>
        </a>
        <button class="nav-toggle" onclick="document.querySelector('.site-nav').classList.toggle('open')">☰</button>
        <nav class="site-nav">
          <a href="/" ${checkActive('/') && !checkActive('/medical') && !checkActive('/drug') && !checkActive('/rabies') && !checkActive('/vitamin') ? 'class="active"' : ''}>Home</a>
          <a href="/blog/" ${checkActive('/blog') ? 'class="active"' : ''}>Blog</a>
          <a href="/medical-calculators/" ${checkActive('/medical-calculators') ? 'class="active"' : ''}>Calculators</a>
          <a href="/drug-doses/" ${checkActive('/drug-doses') ? 'class="active"' : ''}>Drug Doses</a>
          <a href="/rabies-scheduler/" ${checkActive('/rabies-scheduler') ? 'class="active"' : ''}>Rabies PEP</a>
          <a href="/search" ${checkActive('/search') ? 'class="active"' : ''}>🔍 Search</a>
        </nav>
      </div>
    </header>`;

    /* ══ 6. FOOTER ═════════════════════════════════════════════ */
    const year = new Date().getFullYear();
    const footer = `
    <footer class="site-footer">
      <div class="footer-inner">
        <div class="footer-brand">
          <div class="brand-name">🩺 RxMedCalc</div>
          <p>Clinically accurate medical calculators for professionals and patients. Based on WHO, NICE, and IAP guidelines.</p>
        </div>
        <div class="footer-col">
          <h4>Emergencies</h4>
          <a href="/medical-calculators/curb65">CURB-65</a>
          <a href="/medical-calculators/news2">NEWS2</a>
          <a href="/medical-calculators/gcs-calculator">GCS Score</a>
          <a href="/medical-calculators/sofa-score">SOFA Score</a>
        </div>
        <div class="footer-col">
          <h4>Vitamins</h4>
          <a href="/vitamin/b1-thiamine-calculator">Vitamin B1</a>
          <a href="/vitamin/b3-niacin-calculator">Vitamin B3</a>
          <a href="/vitamin/ascorbic-acid-vit-c">Vitamin C</a>
          <a href="/vitamin/d3-cholecalciferol">Vitamin D3</a>
        </div>
        <div class="footer-col">
          <h4>Legal</h4>
          <a href="/about">About Us</a>
          <a href="/privacy">Privacy Policy</a>
          <a href="/contact">Contact</a>
        </div>
      </div>
      <div class="footer-bottom">
        <span>© ${year} RxMedCalc · Built by a doctor in India</span>
        <span>Free Tool · No Login Required</span>
      </div>
    </footer>`;

    document.body.insertAdjacentHTML('afterbegin', header);
    document.body.insertAdjacentHTML('beforeend', footer);
})();

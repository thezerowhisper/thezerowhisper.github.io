// ============================================================
// analytics.js — Medical Calculators India
// Place at: /assets/analytics.js
// Replace G-XXXXXXXXXX with your real GA4 Measurement ID
// Found at: analytics.google.com → Admin → Data Streams
// ============================================================

window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());

gtag('config', 'G-4E814WCWHH', {
  // Send page_view automatically on each page load
  send_page_view: true,
  // Anonymize IPs for privacy (good practice)
  anonymize_ip: true
});


// ============================================================
// HELPER — Call this from any calculator when result is shown
//
// Usage:
//   trackCalc('curb65', { score: 3, risk: 'high' });
//   trackCalc('news2',  { score: 7 });
//   trackCalc('gcs',    { total: '10T', severity: 'moderate' });
// ============================================================
function trackCalc(toolName, params) {
  if (typeof gtag !== 'function') return;
  gtag('event', 'calculator_used', {
    event_category: 'Calculator',
    event_label: toolName,
    tool_name: toolName,
    ...params
  });
}


// ============================================================
// HELPER — Call this when WhatsApp share button is clicked
// ============================================================
function trackShare(toolName, method) {
  if (typeof gtag !== 'function') return;
  gtag('event', 'share', {
    method: method || 'whatsapp',
    content_type: 'calculator_result',
    item_id: toolName
  });
}


// ============================================================
// HELPER — Call this when Print button is clicked
// ============================================================
function trackPrint(toolName) {
  if (typeof gtag !== 'function') return;
  gtag('event', 'print', {
    event_category: 'Calculator',
    event_label: toolName,
    tool_name: toolName
  });
}


// ============================================================
// AUTO-TRACK — Outbound links (WhatsApp, external refs)
// Runs automatically, no changes needed
// ============================================================
document.addEventListener('click', function(e) {
  const a = e.target.closest('a[href]');
  if (!a) return;
  const href = a.href || '';
  if (href.startsWith('https://wa.me')) {
    const tool = document.body.dataset.tool || 'unknown';
    trackShare(tool, 'whatsapp');
  }
});

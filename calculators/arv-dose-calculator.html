// ============================================================
// umami-events.js  — Medical Calculators India
// Place at: /assets/umami-events.js
// Load AFTER your Umami script tag (already defer):
//   <script src="assets/umami-events.js"></script>
// ============================================================

// ── SAFE CORE ─────────────────────────────────────────────────
// try-catch on every call so a failed track NEVER blocks print
// or any other onclick action.
function uTrack(name, props) {
  try {
    if (typeof window.umami !== 'undefined' && typeof window.umami.track === 'function') {
      window.umami.track(name, props || {});
    } else {
      // Umami not ready yet (defer timing) — retry after 1.2s
      setTimeout(function() {
        try {
          if (typeof window.umami !== 'undefined') {
            window.umami.track(name, props || {});
          }
        } catch(e) {}
      }, 1200);
    }
  } catch(e) {}
}

// ── PUBLIC HELPERS ────────────────────────────────────────────
function trackCalc(tool, props) { uTrack('calc_' + tool, props || {}); }
function trackPrint(tool)       { uTrack('print', { tool: tool }); }
function trackShare(tool, method) {
  uTrack('share_' + (method || 'whatsapp'), { tool: tool });
}

// ── AUTO-TRACK WHATSAPP OUTBOUND CLICKS ──────────────────────
// Reads data-tool from <html> tag — no per-page code needed.
document.addEventListener('DOMContentLoaded', function() {
  document.addEventListener('click', function(e) {
    var a = e.target.closest('a[href]');
    if (!a) return;
    if ((a.href || '').startsWith('https://wa.me')) {
      var tool = document.documentElement.dataset.tool || 'unknown';
      trackShare(tool, 'whatsapp');
    }
  });
});

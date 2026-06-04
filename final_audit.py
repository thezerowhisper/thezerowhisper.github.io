#!/usr/bin/env python3
"""
rxmedcalc.com — Final Pre-AdSense Audit v2
Correctly detects both static HTML FAQs and JS-array FAQs.
Run from repo root: python3 final_audit_v2.py
"""
import re
from pathlib import Path
from html.parser import HTMLParser

BASE = "https://rxmedcalc.com"
SCAN = ["medical-calculators", "drug-doses", "vitamin", "rabies-scheduler"]

class WordCounter(HTMLParser):
    SKIP = {"script","style","noscript","head","meta","link","svg"}
    def __init__(self):
        super().__init__()
        self._skip = 0
        self.words = 0
    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP: self._skip += 1
    def handle_endtag(self, tag):
        if tag in self.SKIP and self._skip: self._skip -= 1
    def handle_data(self, data):
        if not self._skip:
            self.words += len(data.split())

def count_words_full(content):
    """Count ALL words including inside script/style — approximates what browser renders"""
    # Strip tags only, keep all text
    text = re.sub(r'<[^>]+>', ' ', content)
    # Strip JS noise (variable assignments, brackets)
    text = re.sub(r'(var|const|let|function|return|if|else|for)\s*\(', ' ', text)
    return len(text.split())

def detect_faqs(content):
    """Detect FAQs in any format"""
    # JS array formats
    has_js_array = bool(re.search(r'const faqs\s*=\s*\[', content))
    js_count = 0
    if has_js_array:
        m = re.search(r'const faqs\s*=\s*\[(.*?)\];', content, re.DOTALL)
        if m:
            js_count = len(re.findall(r'\[[\'""]', m.group(1))) + \
                      len(re.findall(r'\{\s*q\s*:', m.group(1)))

    # Static HTML FAQs — h3+p pattern inside FAQ section
    static_h3 = len(re.findall(
        r'(?:faq|FAQ|Frequently Asked).*?<h3[^>]*>',
        content, re.DOTALL | re.IGNORECASE))

    # faq-item divs
    faq_items = len(re.findall(r'class=["\'][^"\']*faq-item', content))

    # Schema FAQPage questions
    schema_q = len(re.findall(r'"@type"\s*:\s*"Question"', content))

    total = max(js_count, static_h3, faq_items, schema_q)
    return total

def audit(path: Path):
    issues = []
    warns = []
    c = path.read_text(encoding="utf-8", errors="ignore")

    # 1. Canonical
    cm = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', c) or \
         re.search(r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']', c)
    if not cm:
        issues.append("❌ CANONICAL missing")
    else:
        h = cm.group(1)
        if not h.startswith("https://rxmedcalc.com"):
            issues.append(f"❌ CANONICAL wrong domain: {h[:60]}")
        elif h.endswith(".html"):
            issues.append(f"⚠️  CANONICAL has .html suffix")

    # 2. og:url
    om = re.search(r'property=["\']og:url["\'][^>]+content=["\']([^"\']*)["\']', c) or \
         re.search(r'content=["\']([^"\']*)["\'][^>]+property=["\']og:url["\']', c)
    if not om:
        warns.append("⚠️  OG:URL missing")
    else:
        ov = om.group(1)
        if "https://https://" in ov:
            issues.append(f"❌ OG:URL double-https")
        elif not ov.startswith("https://rxmedcalc.com"):
            issues.append(f"❌ OG:URL wrong: {ov[:60]}")

    # 3. FAQs — detect all formats
    faq_count = detect_faqs(c)
    if faq_count == 0:
        issues.append("❌ FAQ: none detected (JS array, static HTML, or schema)")
    elif faq_count < 4:
        warns.append(f"⚠️  FAQ: only {faq_count} detected (aim ≥6)")

    # 4. FAQPage schema
    if '"FAQPage"' not in c:
        warns.append("⚠️  SCHEMA: no FAQPage JSON-LD")

    # 5. Prose/info section — check for any substantial paragraph content
    has_info = ("info-section" in c or
                bool(re.search(r'id=["\']about-', c)) or
                bool(re.search(r'content-section', c)) or
                c.count('<p>') > 5)
    if not has_info:
        warns.append("⚠️  PROSE: limited paragraph content")

    # 6. Word count — use full count (includes JS text as proxy for rendered content)
    # Use HTML-only count as primary, full as secondary
    wc = WordCounter()
    wc.feed(c)
    html_words = wc.words
    full_words = count_words_full(c)
    # Drug-dose pages render via JS so html_words=0 but full_words shows real content
    effective_words = max(html_words, full_words // 4)  # JS text is ~4x inflated

    if html_words < 100 and full_words < 500:
        issues.append(f"❌ THIN: ~{html_words} HTML words, ~{full_words} total")
    elif html_words < 300:
        warns.append(f"⚠️  BORDERLINE: ~{html_words} HTML words")

    # 7. Duplicate Related
    if len(re.findall(r'(?:card-title|section-title)[^>]*>[^<]*Related', c)) > 1:
        warns.append("⚠️  DUPLICATE Related section")

    all_issues = issues + warns
    has_critical = bool(issues)
    return all_issues, has_critical, html_words, full_words

def main():
    repo = Path.cwd()
    results = []
    for d in SCAN:
        dd = repo / d
        if not dd.exists(): continue
        for f in sorted(dd.rglob("*.html")):
            issues, critical, hw, fw = audit(f)
            results.append((str(f.relative_to(repo)), hw, fw, issues, critical))

    crit  = [(p,hw,fw,i) for p,hw,fw,i,c in results if c]
    warn  = [(p,hw,fw,i) for p,hw,fw,i,c in results if not c and i]
    clean = [(p,hw,fw,i) for p,hw,fw,i,c in results if not i]

    print(f"\n{'='*65}")
    print(f"  rxmedcalc.com Pre-AdSense Audit v2")
    print(f"  Total: {len(results)} | Critical: {len(crit)} | Warnings: {len(warn)} | Clean: {len(clean)}")
    print(f"{'='*65}\n")

    if crit:
        print("── CRITICAL ─────────────────────────────────────────────────\n")
        for p,hw,fw,issues in crit:
            print(f"  📄 {p}  (html:{hw}w / full:{fw}w)")
            for i in issues: print(f"     {i}")
            print()

    if warn:
        print("── WARNINGS ─────────────────────────────────────────────────\n")
        for p,hw,fw,issues in warn:
            print(f"  📄 {p}  (html:{hw}w)")
            for i in issues: print(f"     {i}")
            print()

    if clean:
        print(f"── CLEAN ({len(clean)}) ──────────────────────────────────────────────")
        for p,hw,fw,_ in clean:
            print(f"  ✅ {p}  ({hw}w)")

    print(f"\n{'='*65}")
    if not crit:
        print("  ✅ NO CRITICAL ISSUES — ready to request AdSense re-review")
    else:
        print(f"  ❌ {len(crit)} files with critical issues")
    print(f"{'='*65}\n")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
rxmedcalc.com — Live Googlebot Content Visibility Audit
Fetches every page as Googlebot and checks what Google actually sees.
Run from anywhere: python3 googlebot_audit.py
Requires: pip3 install requests --break-system-packages
"""

import re, time, sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Installing requests...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "requests", "--break-system-packages"], check=True)
    import requests

BASE = "https://rxmedcalc.com"
GOOGLEBOT_UA = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"

PAGES = [
    # Medical calculators
    "/medical-calculators/aa-gradient",
    "/medical-calculators/abcd2-score",
    "/medical-calculators/albumin-corrected-ag",
    "/medical-calculators/anion-gap",
    "/medical-calculators/apache2-score",
    "/medical-calculators/apgar-score",
    "/medical-calculators/ascvd-risk",
    "/medical-calculators/beta-hcg",
    "/medical-calculators/bisap-score",
    "/medical-calculators/bmi",
    "/medical-calculators/bsa-calculator",
    "/medical-calculators/burn-calculator",
    "/medical-calculators/cha2ds2-vasc",
    "/medical-calculators/child-pugh",
    "/medical-calculators/corrected-calcium",
    "/medical-calculators/creatinine-clearance",
    "/medical-calculators/curb65",
    "/medical-calculators/egfr-calculator",
    "/medical-calculators/fena-calculator",
    "/medical-calculators/fib-4-index",
    "/medical-calculators/framingham-risk",
    "/medical-calculators/gcs-calculator",
    "/medical-calculators/grace-score",
    "/medical-calculators/has-bled",
    "/medical-calculators/hba1c-converter",
    "/medical-calculators/holliday-segar",
    "/medical-calculators/hunt-hess",
    "/medical-calculators/hypothyroidism",
    "/medical-calculators/ibw-calculator",
    "/medical-calculators/ktv-dialysis",
    "/medical-calculators/ldl-calculator",
    "/medical-calculators/map-calculator",
    "/medical-calculators/meld-score",
    "/medical-calculators/nafld-fibrosis-score",
    "/medical-calculators/neonatal-jaundice",
    "/medical-calculators/news2",
    "/medical-calculators/nihss-calculator",
    "/medical-calculators/ors",
    "/medical-calculators/pediatric-asthma",
    "/medical-calculators/pediatric-dehydration",
    "/medical-calculators/pediatric-weight",
    "/medical-calculators/perc-rule",
    "/medical-calculators/phq9-gad7",
    "/medical-calculators/psi-calculator",
    "/medical-calculators/qsofa-score",
    "/medical-calculators/qtc-calculator",
    "/medical-calculators/rass-score",
    "/medical-calculators/rcri-calculator",
    "/medical-calculators/serum-osmolality",
    "/medical-calculators/shock-index",
    "/medical-calculators/sirs-criteria",
    "/medical-calculators/sodium-correction",
    "/medical-calculators/sofa-score",
    "/medical-calculators/spirometry",
    "/medical-calculators/steroid-equivalence",
    "/medical-calculators/sti-rti-management",
    "/medical-calculators/tsh-interpreter",
    "/medical-calculators/upcr-calculator",
    "/medical-calculators/wells-score",
    # Drug doses (sample — most important)
    "/drug-doses/amoxicillin",
    "/drug-doses/amlodipine",
    "/drug-doses/azithromycin",
    "/drug-doses/cefixime",
    "/drug-doses/ciprofloxacin",
    "/drug-doses/metformin",
    "/drug-doses/paracetamol",
    "/drug-doses/omeprazole-pantoprazole",
    "/drug-doses/ondansetron",
    "/drug-doses/prednisolone",
    # Vitamins
    "/vitamin/b3-niacin-calculator",
    "/vitamin/b12-cobalamin-calculator",
    "/vitamin/d3-cholecalciferol",
    "/vitamin/ascorbic-acid-vit-c",
    # Legal/static
    "/about",
    "/privacy",
    "/contact",
    "/disclaimer",
    # Hubs
    "/medical-calculators/",
    "/drug-doses/",
]

def strip_tags(html):
    # Remove script and style blocks entirely
    html = re.sub(r'<script[^>]*>.*?</script>', ' ', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', ' ', html, flags=re.DOTALL)
    # Remove JSON-LD blocks
    html = re.sub(r'\{["\']@context["\'].*?\}', ' ', html, flags=re.DOTALL)
    # Remove remaining tags
    html = re.sub(r'<[^>]+>', ' ', html)
    # Collapse whitespace
    html = re.sub(r'\s+', ' ', html).strip()
    return html

def check_page(url):
    issues = []
    warnings = []
    try:
        r = requests.get(url, headers={"User-Agent": GOOGLEBOT_UA}, timeout=15)
        if r.status_code != 200:
            return r.status_code, 0, [f"❌ HTTP {r.status_code}"], []

        html = r.text
        text = strip_tags(html)
        words = len(text.split())

        # 1. Word count
        if words < 150:
            issues.append(f"❌ THIN: only {words} visible words to Google")
        elif words < 350:
            warnings.append(f"⚠️  BORDERLINE: {words} words")

        # 2. FAQ visible
        has_faq = (
            "Frequently Asked" in html or
            "FAQ" in html or
            '"FAQPage"' in html or
            'class="fi"' in html or
            'faq-item' in html or
            'faq-container' in html
        )
        if not has_faq:
            issues.append("❌ FAQ: not visible in HTML")

        # 3. Canonical
        cm = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', html)
        if not cm:
            warnings.append("⚠️  No canonical tag")
        else:
            canon = cm.group(1)
            if "thezerowhisper" in canon:
                issues.append(f"❌ Canonical wrong domain: {canon}")
            elif not canon.startswith("https://rxmedcalc.com"):
                issues.append(f"❌ Canonical not full URL: {canon}")

        # 4. Title present
        tm = re.search(r'<title>([^<]+)</title>', html)
        if not tm or len(tm.group(1).strip()) < 10:
            warnings.append("⚠️  Title missing or too short")

        # 5. Meta description
        dm = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', html)
        if not dm:
            warnings.append("⚠️  No meta description")

        # 6. Check content is not ONLY schema/JSON
        non_json_text = re.sub(r'\{.*?\}', '', text, flags=re.DOTALL)
        non_json_words = len(non_json_text.split())
        if non_json_words < 100 and words > 200:
            warnings.append(f"⚠️  Most visible text is JSON/schema ({non_json_words} non-JSON words)")

        return r.status_code, words, issues, warnings

    except Exception as e:
        return 0, 0, [f"❌ ERROR: {str(e)[:60]}"], []

def main():
    print(f"\n{'='*70}")
    print(f"  rxmedcalc.com — Googlebot Visibility Audit")
    print(f"  Checking {len(PAGES)} pages as Googlebot")
    print(f"{'='*70}\n")

    critical = []
    warned = []
    clean = []

    for path in PAGES:
        url = BASE + path
        status, words, issues, warnings = check_page(url)
        time.sleep(0.3)  # polite delay

        slug = path
        if issues:
            critical.append((slug, status, words, issues, warnings))
            print(f"  ❌ {slug} ({words}w)")
            for i in issues: print(f"     {i}")
            for w in warnings: print(f"     {w}")
        elif warnings:
            warned.append((slug, status, words, issues, warnings))
            print(f"  ⚠️  {slug} ({words}w)")
            for w in warnings: print(f"     {w}")
        else:
            clean.append((slug, words))
            print(f"  ✅ {slug} ({words}w)")

    print(f"\n{'='*70}")
    print(f"  SUMMARY")
    print(f"  Total checked: {len(PAGES)}")
    print(f"  ✅ Clean: {len(clean)}")
    print(f"  ⚠️  Warnings: {len(warned)}")
    print(f"  ❌ Critical: {len(critical)}")
    print(f"{'='*70}")

    if not critical:
        print("\n  ✅ ALL PAGES PASS — safe to submit AdSense re-review\n")
    else:
        print(f"\n  ❌ {len(critical)} pages need fixing before re-review\n")
        print("  CRITICAL PAGES:")
        for slug, status, words, issues, _ in critical:
            print(f"    {slug}: {', '.join(i for i in issues)}")

if __name__ == "__main__":
    main()

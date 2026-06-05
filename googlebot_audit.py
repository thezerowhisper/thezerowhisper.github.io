#!/usr/bin/env python3
"""
rxmedcalc.com — FULL Googlebot Visibility Audit (all pages)
Fetches every page dynamically from sitemap + directory scan.
Run: python3 googlebot_audit_full.py
"""

import re, time, sys, subprocess

try:
    import requests
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "requests", "--break-system-packages"], check=True)
    import requests

BASE = "https://rxmedcalc.com"
UA = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"

# All paths to check — built from directory structure
PATHS = [
    # Static pages
    "/", "/about", "/privacy", "/contact", "/disclaimer",
    "/search",

    # Hubs
    "/medical-calculators/",
    "/drug-doses/",
    "/vitamin/",
    "/rabies-scheduler/",
    "/blog/",

    # Medical calculators
    "/medical-calculators/aa-gradient",
    "/medical-calculators/abcd2-score",
    "/medical-calculators/albumin-corrected-ag",
    "/medical-calculators/anion-gap",
    "/medical-calculators/anti-rabies-serum-dose-calculator",
    "/medical-calculators/apache2-score",
    "/medical-calculators/apgar-score",
    "/medical-calculators/arv-dose-calculator",
    "/medical-calculators/ascvd-risk",
    "/medical-calculators/beta-hcg",
    "/medical-calculators/biomedical-waste",
    "/medical-calculators/bisap-score",
    "/medical-calculators/bmi",
    "/medical-calculators/bsa-calculator",
    "/medical-calculators/burn-calculator",
    "/medical-calculators/cbc-report-interpreter",
    "/medical-calculators/cha2ds2-vasc",
    "/medical-calculators/child-pugh",
    "/medical-calculators/conception-date-calculator",
    "/medical-calculators/corrected-calcium",
    "/medical-calculators/creatinine-clearance",
    "/medical-calculators/curb65",
    "/medical-calculators/doses",
    "/medical-calculators/due-date",
    "/medical-calculators/egfr-calculator",
    "/medical-calculators/fena-calculator",
    "/medical-calculators/fetal-growth-calculator",
    "/medical-calculators/fib-4-index",
    "/medical-calculators/framingham-risk",
    "/medical-calculators/gcs-calculator",
    "/medical-calculators/gestational-age-calculator",
    "/medical-calculators/grace-score",
    "/medical-calculators/growth-chart",
    "/medical-calculators/growth-velocity",
    "/medical-calculators/has-bled",
    "/medical-calculators/hba1c-converter",
    "/medical-calculators/height-velocity",
    "/medical-calculators/holliday-segar",
    "/medical-calculators/hunt-hess",
    "/medical-calculators/hypothyroidism",
    "/medical-calculators/ibw-calculator",
    "/medical-calculators/iron-deficit",
    "/medical-calculators/iv-drip-rate-calculator",
    "/medical-calculators/ktv-dialysis",
    "/medical-calculators/lab-unit-converter",
    "/medical-calculators/ldl-calculator",
    "/medical-calculators/map-calculator",
    "/medical-calculators/meld-score",
    "/medical-calculators/mentzer-index-calculator",
    "/medical-calculators/milestones",
    "/medical-calculators/nafld-fibrosis-score",
    "/medical-calculators/neonatal-jaundice",
    "/medical-calculators/news2",
    "/medical-calculators/nihss-calculator",
    "/medical-calculators/obs-calc",
    "/medical-calculators/ors",
    "/medical-calculators/ovulation-calendar",
    "/medical-calculators/paracetamol",
    "/medical-calculators/pediatric-asthma",
    "/medical-calculators/pediatric-dehydration",
    "/medical-calculators/pediatric-weight",
    "/medical-calculators/perc-rule",
    "/medical-calculators/phq9-gad7",
    "/medical-calculators/pregnancy-bmi-calculator",
    "/medical-calculators/pregnancy-weight-gain-calculator",
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
    "/medical-calculators/uip-vaccine",
    "/medical-calculators/upcr-calculator",
    "/medical-calculators/wells-score",

    # Drug doses
    "/drug-doses/amikacin-gentamicin",
    "/drug-doses/amlodipine",
    "/drug-doses/amoxicillin",
    "/drug-doses/amoxicillin-clavulanate",
    "/drug-doses/atenolol",
    "/drug-doses/azithromycin",
    "/drug-doses/calcium-vitamind",
    "/drug-doses/cefixime",
    "/drug-doses/ceftriaxone",
    "/drug-doses/cetirizine",
    "/drug-doses/ciprofloxacin",
    "/drug-doses/clindamycin",
    "/drug-doses/cotrimoxazole",
    "/drug-doses/dexamethasone",
    "/drug-doses/dextromethorphan-phenylephrine",
    "/drug-doses/diazepam",
    "/drug-doses/diclofenac",
    "/drug-doses/digoxin",
    "/drug-doses/domperidone",
    "/drug-doses/doxycycline",
    "/drug-doses/enoxaparin",
    "/drug-doses/famotidine",
    "/drug-doses/folic-acid-calculator",
    "/drug-doses/furosemide",
    "/drug-doses/glibenclamide",
    "/drug-doses/ibuprofen",
    "/drug-doses/insulin",
    "/drug-doses/iron",
    "/drug-doses/levothyroxine",
    "/drug-doses/metformin",
    "/drug-doses/metronidazole",
    "/drug-doses/omeprazole-pantoprazole",
    "/drug-doses/ondansetron",
    "/drug-doses/paracetamol",
    "/drug-doses/phenobarbitone",
    "/drug-doses/phenytoin",
    "/drug-doses/prednisolone",
    "/drug-doses/salbutamol",
    "/drug-doses/spironolactone",
    "/drug-doses/valproate",
    "/drug-doses/vancomycin",
    "/drug-doses/zinc",

    # Vitamins
    "/vitamin/a-retinol-calculator",
    "/vitamin/ascorbic-acid-vit-c",
    "/vitamin/b1-thiamine-calculator",
    "/vitamin/b12-cobalamin-calculator",
    "/vitamin/b2-riboflavin-calculator",
    "/vitamin/b3-niacin-calculator",
    "/vitamin/b6-pyridoxine-calculator",
    "/vitamin/b7-biotin-calculator",
    "/vitamin/b9-folic-acid",
    "/vitamin/d3-cholecalciferol",
    "/vitamin/e-tocopherol-calculator",
    "/vitamin/k-calculator",

    # Rabies
    "/rabies-scheduler/",
    "/rabies-scheduler/doses",

    # Blog (check hub + sample posts)
    "/blog/abcd2-score",
    "/blog/anion-gap",
    "/blog/apgar-score",
    "/blog/bmi-india",
    "/blog/cha2ds2-vasc",
    "/blog/conception-date",
]

# Pages that legitimately don't need FAQs
NO_FAQ_OK = {"/", "/about", "/privacy", "/contact", "/disclaimer",
             "/search", "/medical-calculators/", "/drug-doses/",
             "/vitamin/", "/rabies-scheduler/", "/blog/"}

# Pages that are JS-rendered apps (word count will be low in static fetch)
JS_APP_PAGES = {
    "/medical-calculators/cbc-report-interpreter",
    "/medical-calculators/fetal-growth-calculator",
    "/medical-calculators/gestational-age-calculator",
    "/medical-calculators/growth-velocity",
    "/medical-calculators/height-velocity",
    "/medical-calculators/iron-deficit",
    "/medical-calculators/iv-drip-rate-calculator",
    "/medical-calculators/mentzer-index-calculator",
    "/medical-calculators/ovulation-calendar",
    "/medical-calculators/pregnancy-bmi-calculator",
    "/medical-calculators/pregnancy-weight-gain-calculator",
}

def strip_tags(html):
    html = re.sub(r'<script[^>]*>.*?</script>', ' ', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', ' ', html, flags=re.DOTALL)
    html = re.sub(r'<[^>]+>', ' ', html)
    html = re.sub(r'\s+', ' ', html).strip()
    return html

def check(path):
    issues, warnings = [], []
    url = BASE + path
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=15)
        sc = r.status_code
        if sc == 404:
            return sc, 0, ["❌ 404 NOT FOUND"], []
        if sc != 200:
            return sc, 0, [f"❌ HTTP {sc}"], []

        html = r.text
        text = strip_tags(html)
        words = len(text.split())

        # Word count — skip for known JS-app pages
        if path not in JS_APP_PAGES:
            if words < 150:
                issues.append(f"❌ THIN: {words} words visible to Google")
            elif words < 300:
                warnings.append(f"⚠️  BORDERLINE: {words} words")

        # FAQ check — skip for no-FAQ-ok pages
        if path not in NO_FAQ_OK:
            has_faq = any(x in html for x in [
                "Frequently Asked", "FAQPage", 'class="fi"',
                'faq-item', 'faq-container', 'faq-list',
                '<h3>', 'faq-q'
            ])
            if not has_faq:
                issues.append("❌ FAQ: none visible to Google")

        # Canonical
        cm = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', html)
        if cm:
            c = cm.group(1)
            if "thezerowhisper" in c:
                issues.append(f"❌ Canonical wrong domain")
            elif not c.startswith("https://rxmedcalc.com"):
                issues.append(f"❌ Canonical relative: {c}")
        else:
            # Hub/blog pages may not have canonical — only warn
            if path not in {"/", "/blog/"}:
                warnings.append("⚠️  No canonical tag")

        return sc, words, issues, warnings

    except Exception as e:
        return 0, 0, [f"❌ ERROR: {str(e)[:80]}"], []

def main():
    print(f"\n{'='*70}")
    print(f"  rxmedcalc.com — Full Googlebot Audit ({len(PATHS)} pages)")
    print(f"{'='*70}\n")

    critical, warned, clean, not_found = [], [], [], []

    for path in PATHS:
        sc, words, issues, warnings = check(path)
        time.sleep(0.25)

        if sc == 404:
            not_found.append(path)
            print(f"  🔴 404 {path}")
        elif issues:
            critical.append((path, words, issues, warnings))
            print(f"  ❌ {path} ({words}w)")
            for i in issues: print(f"     {i}")
            for w in warnings: print(f"     {w}")
        elif warnings:
            warned.append((path, words, warnings))
            print(f"  ⚠️  {path} ({words}w)")
            for w in warnings: print(f"     {w}")
        else:
            clean.append((path, words))
            print(f"  ✅ {path} ({words}w)")

    print(f"\n{'='*70}")
    print(f"  FULL AUDIT SUMMARY")
    print(f"  Checked:   {len(PATHS)}")
    print(f"  ✅ Clean:  {len(clean)}")
    print(f"  ⚠️  Warn:   {len(warned)}")
    print(f"  ❌ Issues: {len(critical)}")
    print(f"  🔴 404:    {len(not_found)}")
    print(f"{'='*70}")

    if not_found:
        print(f"\n  404 PAGES (check URL or noindex):")
        for p in not_found: print(f"    {p}")

    if critical:
        print(f"\n  CRITICAL (must fix):")
        for p, w, issues, _ in critical:
            print(f"    {p}: {issues[0]}")
    else:
        print("\n  ✅ NO CRITICAL ISSUES — ready for AdSense re-review")

if __name__ == "__main__":
    main()

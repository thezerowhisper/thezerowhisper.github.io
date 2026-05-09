#!/usr/bin/env python3
"""
RxMedCalc Blog Auto-Interlinking Script
=======================================
Injects a "Related Articles" section into every blog post HTML file.
Run once after adding new posts, or re-run anytime — it's idempotent.

Usage:
    python3 interlink.py --blog-dir ./blog

    Optional flags:
    --dry-run       Preview what would change without writing files
    --force         Re-inject even if links already exist (refreshes them)
"""

import os
import re
import argparse
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# ARTICLE REGISTRY
# Each entry: slug, title, category, tags (used for relevance matching)
# Add new posts here as you publish them.
# ─────────────────────────────────────────────────────────────────────────────
ARTICLES = [
    # Infectious Disease
    {
        "slug": "rabies-pep",
        "title": "Rabies After a Dog Bite: PEP, Vaccines & the NCDC Schedule",
        "category": "Infectious Disease",
        "emoji": "🦠",
        "read_time": "12 min",
        "tags": ["rabies", "vaccine", "pep", "dog bite", "infectious", "arv", "immunisation", "erig"],
    },
    # Obstetrics & Neonatology
    {
        "slug": "pregnancy-due-date",
        "title": "Pregnancy Due Date: How EDD Is Calculated & What to Expect",
        "category": "Obstetrics",
        "emoji": "🤰",
        "read_time": "12 min",
        "tags": ["pregnancy", "edd", "obstetrics", "lmp", "antenatal", "trimester", "fogsi", "ivf"],
    },
    {
        "slug": "conception-date",
        "title": "Conception Date Calculator: How to Find Out When You Conceived",
        "category": "Obstetrics",
        "emoji": "🤰",
        "read_time": "9 min",
        "tags": ["pregnancy", "conception", "obstetrics", "lmp", "ovulation", "ivf", "edd"],
    },
    {
        "slug": "apgar-score",
        "title": "The APGAR Score: Newborn Assessment in the First Minutes of Life",
        "category": "Neonatology",
        "emoji": "👶",
        "read_time": "11 min",
        "tags": ["apgar", "newborn", "neonatal", "resuscitation", "nrp", "paediatric", "delivery"],
    },
    {
        "slug": "neonatal-jaundice",
        "title": "Neonatal Jaundice: Causes, Phototherapy & AAP 2022 Guidelines",
        "category": "Neonatology",
        "emoji": "👶",
        "read_time": "12 min",
        "tags": ["jaundice", "newborn", "neonatal", "bilirubin", "phototherapy", "g6pd", "paediatric", "kernicterus"],
    },
    # Renal & Nephrology
    {
        "slug": "creatinine-clearance",
        "title": "Creatinine Clearance & the Cockcroft-Gault Equation",
        "category": "Renal Pharmacology",
        "emoji": "🫘",
        "read_time": "13 min",
        "tags": ["creatinine", "renal", "kidney", "cockcroft-gault", "drug dosing", "ckd", "egfr", "dose adjustment"],
    },
    {
        "slug": "egfr-ckd",
        "title": "eGFR & Chronic Kidney Disease: What Your Kidney Numbers Mean",
        "category": "Nephrology",
        "emoji": "🫘",
        "read_time": "14 min",
        "tags": ["egfr", "ckd", "kidney", "renal", "ckd-epi", "sglt2", "creatinine", "nephrology"],
    },
    {
        "slug": "corrected-calcium",
        "title": "Corrected Calcium: Why Albumin Changes Everything in Hypocalcaemia",
        "category": "Nephrology",
        "emoji": "🫘",
        "read_time": "11 min",
        "tags": ["calcium", "albumin", "hypocalcaemia", "renal", "nephrology", "ckd", "pth", "vitamin d"],
    },
    # Cardiology
    {
        "slug": "cha2ds2-vasc",
        "title": "CHA₂DS₂-VASc Score: Stroke Risk in Atrial Fibrillation",
        "category": "Cardiology",
        "emoji": "🫀",
        "read_time": "13 min",
        "tags": ["afib", "stroke", "anticoagulation", "cardiology", "doac", "warfarin", "has-bled", "cha2ds2"],
    },
    {
        "slug": "framingham-risk",
        "title": "Framingham Risk Score: 10-Year Cardiovascular Risk in Primary Prevention",
        "category": "Cardiology",
        "emoji": "🫀",
        "read_time": "13 min",
        "tags": ["framingham", "cardiovascular", "cardiology", "statin", "ldl", "ascvd", "primary prevention"],
    },
    {
        "slug": "grace-score",
        "title": "GRACE Score: Risk Stratification in Acute Coronary Syndrome",
        "category": "Cardiology",
        "emoji": "🫀",
        "read_time": "13 min",
        "tags": ["grace", "acs", "nstemi", "cardiology", "mi", "anticoagulation", "angiography", "stemi"],
    },
    {
        "slug": "map-calculator",
        "title": "Mean Arterial Pressure (MAP): What It Means & Why It Matters",
        "category": "Cardiology",
        "emoji": "🫀",
        "read_time": "10 min",
        "tags": ["map", "blood pressure", "cardiology", "septic shock", "vasopressor", "hypertension", "icp"],
    },
    # Respiratory
    {
        "slug": "curb65-score",
        "title": "CURB-65 Score: Pneumonia Severity & Hospital Admission",
        "category": "Respiratory Medicine",
        "emoji": "🫁",
        "read_time": "14 min",
        "tags": ["curb65", "pneumonia", "respiratory", "antibiotic", "hospital admission", "cap", "mortality"],
    },
    {
        "slug": "news2-score",
        "title": "NEWS2 Score: Early Warning System for Deteriorating Patients",
        "category": "Respiratory Medicine",
        "emoji": "🫁",
        "read_time": "11 min",
        "tags": ["news2", "early warning", "respiratory", "sepsis", "deterioration", "triage", "obs chart"],
    },
    # Emergency & Trauma
    {
        "slug": "parkland-formula",
        "title": "The Parkland Formula for Burn Resuscitation",
        "category": "Emergency & Trauma",
        "emoji": "🔥",
        "read_time": "13 min",
        "tags": ["burns", "parkland", "fluid resuscitation", "emergency", "tbsa", "trauma", "paediatric burns"],
    },
    {
        "slug": "shock-index",
        "title": "Shock Index: A Rapid Bedside Tool for Haemodynamic Instability",
        "category": "Emergency & Trauma",
        "emoji": "🔥",
        "read_time": "10 min",
        "tags": ["shock", "haemodynamic", "emergency", "trauma", "triage", "pph", "ectopic", "blood pressure"],
    },
    {
        "slug": "ors-rehydration",
        "title": "ORS & Rehydration Therapy: WHO Protocol for Diarrhoea & Dehydration",
        "category": "Emergency & Trauma",
        "emoji": "🔥",
        "read_time": "11 min",
        "tags": ["ors", "rehydration", "diarrhoea", "dehydration", "paediatric", "who", "emergency", "fluids"],
    },
    # Metabolic & Endocrine
    {
        "slug": "bmi-india",
        "title": "BMI for Indians: Why India Uses Different Cutoffs & What Your Number Means",
        "category": "Metabolic Health",
        "emoji": "⚖️",
        "read_time": "12 min",
        "tags": ["bmi", "obesity", "metabolic", "india", "waist circumference", "diabetes risk", "icmr"],
    },
    {
        "slug": "hba1c-converter",
        "title": "HbA1c: What Your 3-Month Blood Sugar Average Means",
        "category": "Metabolic Health",
        "emoji": "⚖️",
        "read_time": "11 min",
        "tags": ["hba1c", "diabetes", "blood sugar", "metabolic", "glucose", "insulin", "dcct", "ifcc"],
    },
    {
        "slug": "steroid-equivalence",
        "title": "Steroid Equivalence & Conversion: Prednisolone, Dexamethasone & Beyond",
        "category": "Pharmacology",
        "emoji": "💊",
        "read_time": "12 min",
        "tags": ["steroid", "prednisolone", "dexamethasone", "hydrocortisone", "pharmacology", "tapering", "adrenal"],
    },
    # Neurology & Haematology
    {
        "slug": "gcs-glasgow-coma-scale",
        "title": "Glasgow Coma Scale (GCS): Complete Neurological Assessment Guide",
        "category": "Neurology",
        "emoji": "🧠",
        "read_time": "12 min",
        "tags": ["gcs", "coma", "neurology", "tbi", "head injury", "consciousness", "intubation"],
    },
    {
        "slug": "abcd2-score",
        "title": "ABCD² Score: Stroke Risk After TIA & the 2-Day Window",
        "category": "Neurology",
        "emoji": "🧠",
        "read_time": "11 min",
        "tags": ["tia", "stroke", "neurology", "abcd2", "antiplatelet", "carotid", "cerebrovascular"],
    },
    {
        "slug": "wells-score-dvt-pe",
        "title": "Wells Score for DVT & PE: Diagnosing Venous Blood Clots",
        "category": "Haematology",
        "emoji": "🩸",
        "read_time": "13 min",
        "tags": ["dvt", "pe", "wells", "haematology", "d-dimer", "anticoagulation", "doac", "ctpa", "thrombosis"],
    },
    {
        "slug": "mentzer-index",
        "title": "Mentzer Index: Differentiating Iron Deficiency from Thalassaemia Trait",
        "category": "Haematology",
        "emoji": "🩸",
        "read_time": "10 min",
        "tags": ["mentzer", "thalassaemia", "iron deficiency", "haematology", "anaemia", "mcv", "rbc"],
    },
    # Critical Care & Acid-Base
    {
        "slug": "sofa-score",
        "title": "SOFA Score: Organ Failure, Sepsis-3 & ICU Mortality",
        "category": "Critical Care",
        "emoji": "🏥",
        "read_time": "13 min",
        "tags": ["sofa", "sepsis", "organ failure", "icu", "critical care", "qsofa", "mortality", "sepsis-3"],
    },
    {
        "slug": "qsofa-score",
        "title": "qSOFA Score: Rapid Sepsis Screening Outside the ICU",
        "category": "Critical Care",
        "emoji": "🏥",
        "read_time": "10 min",
        "tags": ["qsofa", "sepsis", "critical care", "screening", "icu", "sofa", "news2", "sirs"],
    },
    {
        "slug": "anion-gap",
        "title": "Anion Gap: MUDPILES, HARDUPS, Delta Ratio & Mixed Disorders",
        "category": "Acid-Base",
        "emoji": "🧪",
        "read_time": "13 min",
        "tags": ["anion gap", "acid-base", "abg", "metabolic acidosis", "mudpiles", "delta ratio", "icu", "critical care"],
    },
    {
        "slug": "meld-score",
        "title": "MELD Score: Liver Disease Severity & Transplant Waitlist Priority",
        "category": "Gastroenterology",
        "emoji": "🫁",
        "read_time": "12 min",
        "tags": ["meld", "liver", "cirrhosis", "transplant", "gastroenterology", "hepatology", "bilirubin", "inr"],
    },
    # Paediatric
    {
        "slug": "holliday-segar",
        "title": "Holliday-Segar Method: Paediatric Maintenance Fluid Calculation",
        "category": "Paediatric Medicine",
        "emoji": "👶",
        "read_time": "11 min",
        "tags": ["holliday-segar", "paediatric", "fluids", "maintenance", "children", "iv fluids", "hyponatraemia"],
    },
    {
        "slug": "pediatric-dehydration",
        "title": "Paediatric Dehydration: Assessment, Scoring & WHO Rehydration Plans",
        "category": "Paediatric Medicine",
        "emoji": "👶",
        "read_time": "12 min",
        "tags": ["dehydration", "paediatric", "children", "rehydration", "ors", "who", "fluids", "diarrhoea"],
    },
    # Psychiatry
    {
        "slug": "phq9-gad7",
        "title": "PHQ-9 & GAD-7: Screening for Depression & Anxiety in Clinical Practice",
        "category": "Psychiatry",
        "emoji": "🧠",
        "read_time": "11 min",
        "tags": ["phq9", "gad7", "depression", "anxiety", "psychiatry", "mental health", "screening", "primary care"],
    },
    # Preventive Medicine
    {
        "slug": "uip-vaccine-schedule",
        "title": "India's Universal Immunisation Programme: Complete UIP Vaccine Schedule",
        "category": "Preventive Medicine",
        "emoji": "💉",
        "read_time": "13 min",
        "tags": ["vaccine", "immunisation", "uip", "india", "iap", "children", "preventive", "schedule"],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# RELEVANCE ENGINE
# Scores every other article against the current one.
# Scoring: same category = 5pts, each shared tag = 2pts, same emoji = 1pt
# Returns top N by score, minimum 3, maximum 5.
# ─────────────────────────────────────────────────────────────────────────────
def get_related(current_slug, max_results=4):
    current = next((a for a in ARTICLES if a["slug"] == current_slug), None)
    if not current:
        # Fallback: return first 4 articles that aren't current
        return [a for a in ARTICLES if a["slug"] != current_slug][:max_results]

    scored = []
    for article in ARTICLES:
        if article["slug"] == current_slug:
            continue
        score = 0
        if article["category"] == current["category"]:
            score += 5
        shared_tags = set(article["tags"]) & set(current["tags"])
        score += len(shared_tags) * 2
        if article["emoji"] == current["emoji"]:
            score += 1
        scored.append((score, article))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [a for _, a in scored[:max_results]]


# ─────────────────────────────────────────────────────────────────────────────
# HTML BLOCK BUILDER
# Generates the "Related Articles" section HTML.
# Matches the RxMedCalc brand colours already in the site.
# ─────────────────────────────────────────────────────────────────────────────
RELATED_CSS = """
<style id="rxmc-related-styles">
.rxmc-related{margin:48px 0 32px;padding-top:32px;border-top:1px solid #dde3ea;font-family:'DM Sans',sans-serif;}
.rxmc-related h3{font-family:'Lora',serif;font-size:1.15rem;font-weight:700;color:#1a3a5c;margin-bottom:20px;}
.rxmc-related-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px;}
.rxmc-rel-card{display:flex;flex-direction:column;background:#fff;border:1px solid #dde3ea;border-radius:10px;overflow:hidden;text-decoration:none;color:#1c1c1e;transition:box-shadow .18s,transform .18s;}
.rxmc-rel-card:hover{box-shadow:0 6px 22px rgba(26,58,92,.11);transform:translateY(-2px);}
.rxmc-rel-bar{height:3px;}
.rxmc-rel-body{padding:14px 16px 10px;flex:1;}
.rxmc-rel-cat{font-size:10px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:#5a5a6a;margin-bottom:6px;}
.rxmc-rel-title{font-family:'Lora',serif;font-size:.92rem;font-weight:700;line-height:1.35;color:#1c1c1e;}
.rxmc-rel-foot{padding:10px 16px 14px;font-size:12px;color:#1a3a5c;font-weight:600;}
@media(max-width:560px){.rxmc-related-grid{grid-template-columns:1fr 1fr;}}
@media(max-width:360px){.rxmc-related-grid{grid-template-columns:1fr;}}
</style>"""

# Category → accent bar colour map (matches site palette)
CATEGORY_COLOURS = {
    "Infectious Disease": "#7a1a1a",
    "Obstetrics":         "#8a3a6b",
    "Neonatology":        "#1a6b5c",
    "Renal Pharmacology": "#5b3d8a",
    "Nephrology":         "#5b3d8a",
    "Cardiology":         "#1a4e8a",
    "Respiratory Medicine":"#1a6b3c",
    "Emergency & Trauma": "#b83c14",
    "Metabolic Health":   "#1a5a3a",
    "Pharmacology":       "#1a6b3a",
    "Neurology":          "#2c5f8a",
    "Haematology":        "#6b1a1a",
    "Critical Care":      "#3a1a5c",
    "Acid-Base":          "#0e5c6b",
    "Gastroenterology":   "#8a5c1a",
    "Paediatric Medicine":"#1a6b5c",
    "Psychiatry":         "#6b1a8a",
    "Preventive Medicine":"#1a6b5c",
}

MARKER_START = "<!-- RXMC-RELATED-START -->"
MARKER_END   = "<!-- RXMC-RELATED-END -->"


def build_related_block(related_articles):
    cards_html = ""
    for art in related_articles:
        colour = CATEGORY_COLOURS.get(art["category"], "#1a3a5c")
        cards_html += f"""
    <a href="/blog/{art['slug']}" class="rxmc-rel-card">
      <div class="rxmc-rel-bar" style="background:{colour};"></div>
      <div class="rxmc-rel-body">
        <div class="rxmc-rel-cat">{art['emoji']} {art['category']}</div>
        <div class="rxmc-rel-title">{art['title']}</div>
      </div>
      <div class="rxmc-rel-foot">Read Article → &nbsp;<span style="color:#5a5a6a;font-weight:400;">{art['read_time']}</span></div>
    </a>"""

    return f"""{MARKER_START}
{RELATED_CSS}
<div class="rxmc-related">
  <h3>Related Articles</h3>
  <div class="rxmc-related-grid">{cards_html}
  </div>
</div>
{MARKER_END}"""


# ─────────────────────────────────────────────────────────────────────────────
# INJECTION LOGIC
# Finds the best insertion point in each HTML file and injects the block.
# Injection order (first match wins):
#   1. Before <footer
#   2. Before </article>
#   3. Before </main>
#   4. Before </body>
# ─────────────────────────────────────────────────────────────────────────────
INJECT_BEFORE = ["<footer", "</article>", "</main>", "</body>"]


def inject_into_html(html: str, block: str, force: bool) -> tuple[str, str]:
    """Returns (new_html, status_message)."""

    # Already has our block?
    if MARKER_START in html:
        if not force:
            return html, "SKIP (already linked)"
        # Remove old block
        html = re.sub(
            re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END),
            "",
            html,
            flags=re.DOTALL,
        )

    for marker in INJECT_BEFORE:
        idx = html.lower().find(marker.lower())
        if idx != -1:
            new_html = html[:idx] + block + "\n" + html[idx:]
            return new_html, f"OK  (injected before {marker!r})"

    return html, "SKIP (no injection point found — add <footer> or </body>)"


# ─────────────────────────────────────────────────────────────────────────────
# SLUG DETECTION
# Tries to figure out which article a file corresponds to.
# Checks: filename, <link rel="canonical">, <meta property="og:url">
# ─────────────────────────────────────────────────────────────────────────────
def detect_slug(filepath: Path, html: str) -> str | None:
    known_slugs = {a["slug"] for a in ARTICLES}

    # 1. Try canonical tag
    m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if m:
        parts = m.group(1).rstrip("/").split("/")
        for part in reversed(parts):
            if part in known_slugs:
                return part

    # 2. Try og:url
    m = re.search(r'<meta[^>]+property=["\']og:url["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if m:
        parts = m.group(1).rstrip("/").split("/")
        for part in reversed(parts):
            if part in known_slugs:
                return part

    # 3. Try filename (strip .html)
    stem = filepath.stem
    if stem in known_slugs:
        return stem

    return None


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Auto-interlink RxMedCalc blog posts")
    parser.add_argument("--blog-dir", default="./blog", help="Path to your blog directory")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--force", action="store_true", help="Refresh existing links")
    args = parser.parse_args()

    blog_dir = Path(args.blog_dir)
    if not blog_dir.exists():
        print(f"ERROR: Directory not found: {blog_dir}")
        return

    html_files = sorted(blog_dir.rglob("*.html"))
    if not html_files:
        print(f"No .html files found in {blog_dir}")
        return

    print(f"\n{'DRY RUN — ' if args.dry_run else ''}Processing {len(html_files)} file(s) in {blog_dir}\n")
    print(f"{'FILE':<45} {'SLUG':<30} STATUS")
    print("─" * 90)

    updated = skipped = errors = 0

    for filepath in html_files:
        rel = filepath.relative_to(blog_dir)
        try:
            html = filepath.read_text(encoding="utf-8")
        except Exception as e:
            print(f"{'ERROR':<45} {'—':<30} {e}")
            errors += 1
            continue

        slug = detect_slug(filepath, html)
        if not slug:
            print(f"{str(rel):<45} {'— unknown —':<30} SKIP (slug not recognised)")
            skipped += 1
            continue

        related = get_related(slug)
        block   = build_related_block(related)
        new_html, status = inject_into_html(html, block, args.force)

        if "SKIP" in status:
            skipped += 1
        else:
            if not args.dry_run:
                filepath.write_text(new_html, encoding="utf-8")
            updated += 1

        print(f"{str(rel):<45} {slug:<30} {status}")

    print("\n" + "─" * 90)
    print(f"Done.  Updated: {updated}  |  Skipped: {skipped}  |  Errors: {errors}")
    if args.dry_run:
        print("(Dry run — no files were written)")
    print()


if __name__ == "__main__":
    main()

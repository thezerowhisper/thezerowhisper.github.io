#!/usr/bin/env python3
"""
rxmedcalc.com — Master Fix Script v3
Fixes in one pass:
1. Canonical URLs — relative → full https://rxmedcalc.com (no .html)
2. og:url — missing or relative → full URL
3. Wrong domain canonicals (thezerowhisper.github.io)
4. FAQ injection — uses [question, answer] array + faq-container pattern
5. Info-section prose blocks
6. Duplicate Related sections
7. Tool count 17+/20+ → 32+

Run from repo root: python3 master_fix.py
Creates .bak backups.
"""

import re, shutil
from pathlib import Path

BASE = "https://rxmedcalc.com"

# ── FAQ DATA ─────────────────────────────────────────────────────────
# Format: slug → list of [question, answer]
FAQS = {
"abcd2-score": [
    ["What is the ABCD2 score used for?", "The ABCD2 score estimates the short-term risk of stroke after a transient ischaemic attack (TIA). It uses five parameters: Age, Blood pressure, Clinical features, Duration of symptoms, and Diabetes. It helps triage TIA patients — those with high scores (>=4) need urgent investigation and should be seen within 24 hours."],
    ["What is a high vs low ABCD2 score?", "Score 0-3: Low risk (~1% 2-day stroke risk). Score 4-5: Moderate risk (~4% 2-day stroke risk). Score 6-7: High risk (~8% 2-day stroke risk). NICE guidelines recommend specialist assessment within 24 hours for all TIA patients, but high ABCD2 scores (>=4) indicate those most urgently needing investigation."],
    ["What investigations are done after TIA?", "After TIA: urgent brain imaging (MRI DWI preferred, or CT), carotid doppler/CTA if anterior circulation symptoms, ECG and 24-hour Holter for AF, echocardiography if cardioembolic source suspected, FBC, coagulation, glucose, lipids. Antiplatelet therapy (aspirin 300 mg stat, then dual antiplatelet with clopidogrel) should be started immediately unless haemorrhage excluded."],
    ["Is the ABCD2 score still recommended?", "The ABCD2 score has fallen out of favour in many guidelines because it does not reliably identify high-risk TIA features such as AF, carotid stenosis, or DWI-positive MRI lesions. Current NICE 2019 and ESO guidelines recommend urgent specialist assessment for all TIA within 24 hours rather than ABCD2-based stratification alone. The score remains useful in resource-limited settings."],
    ["What is the difference between TIA and stroke?", "A TIA produces stroke-like symptoms that resolve completely within 24 hours (classically within 1 hour). A stroke has persistent neurological deficits. TIA is a medical emergency — ~10-15% of patients have a stroke within 3 months, with the highest risk in the first 48 hours. All TIA patients require the same urgent workup as stroke."],
    ["What medications are started after TIA?", "Antiplatelet therapy: aspirin 300 mg immediately, then dual antiplatelet (aspirin + clopidogrel) for 21 days per POINT/CHANCE trial evidence, then clopidogrel alone long-term. If AF found: anticoagulation (DOAC preferred). If carotid stenosis >=50%: urgent endarterectomy within 2 weeks. Statin therapy and BP control are also initiated."],
],
"ascvd-risk": [
    ["What is the ASCVD risk score?", "The ASCVD (Atherosclerotic Cardiovascular Disease) Pooled Cohort Equations estimate the 10-year risk of a first atherosclerotic cardiovascular event (non-fatal MI, coronary heart disease death, or fatal or non-fatal stroke) in patients aged 40-79 without pre-existing ASCVD. It uses age, sex, race, total cholesterol, HDL, systolic BP, BP treatment status, diabetes, and smoking."],
    ["How is ASCVD risk classified?", "10-year ASCVD risk: Low risk: <5%. Borderline risk: 5-7.4%. Intermediate risk: 7.5-19.9%. High risk: >=20%. Patients with established ASCVD, LDL >=190 mg/dL, or diabetes aged 40-75 are automatically classified as high risk regardless of calculated score. These thresholds guide statin therapy decisions per ACC/AHA 2019 guidelines."],
    ["When should a statin be started based on ASCVD risk?", "ACC/AHA 2019 guidelines: High-intensity statin for established ASCVD or 10-year risk >=20%. Moderate-to-high intensity statin for 10-year risk 7.5-19.9% (intermediate risk). For borderline risk (5-7.4%), risk-enhancing factors (family history, high CRP, ABI <0.9, coronary calcium score) help guide statin initiation. Lifestyle modification is always the foundation."],
    ["What are the limitations of the ASCVD Pooled Cohort Equations?", "The Pooled Cohort Equations were derived from US cohorts (1960s-1980s) and may overestimate risk in contemporary populations and underestimate in South Asians. They do not include family history, obesity, CRP, or coronary calcium score. For Indian patients, the equations should be interpreted with caution — South Asians develop ASCVD at younger ages and at lower LDL levels than Western populations."],
    ["What lifestyle changes reduce ASCVD risk?", "Proven lifestyle interventions: smoking cessation (most impactful single intervention — halves cardiovascular risk within 1 year), Mediterranean or DASH diet, aerobic exercise (150 min/week moderate intensity), weight loss (5-10% body weight reduces multiple risk factors), BP control (<130/80 mmHg target), and optimal glycaemic control in diabetes. These reduce 10-year ASCVD risk by 30-50% before any medication."],
    ["What is the role of coronary calcium scoring in ASCVD risk?", "Coronary artery calcium (CAC) scoring by CT is the most powerful reclassifier of ASCVD risk in intermediate-risk patients (10-year risk 7.5-19.9%). CAC = 0: very low risk, can defer statin. CAC 1-99: moderate risk, statin favoured. CAC >=100 or >=75th percentile: statin strongly recommended. CAC scoring is particularly useful when patient or clinician is uncertain about starting a statin in intermediate-risk patients."],
],
"cha2ds2-vasc": [
    ["What is the CHA2DS2-VASc score?", "CHA2DS2-VASc estimates annual stroke risk in patients with non-valvular atrial fibrillation (AF). Parameters: Congestive heart failure (1), Hypertension (1), Age >=75 (2), Diabetes mellitus (1), Stroke/TIA history (2), Vascular disease (1), Age 65-74 (1), Sex category female (1). Score 0-9. Guides anticoagulation decisions."],
    ["When should anticoagulation be started in AF?", "ESC 2020 and AHA/ACC guidelines: Men with score >=2, women with score >=3: anticoagulate (OAC strongly recommended). Men with score 1, women with score 2: anticoagulation should be considered (weigh bleeding risk). Men with score 0, women with score 1: anticoagulation not recommended. Female sex alone (score 1 in women, 0 in men) does not independently increase stroke risk and should not trigger anticoagulation."],
    ["Which anticoagulant is preferred in AF?", "DOACs (apixaban, rivaroxaban, dabigatran, edoxaban) are preferred over warfarin for non-valvular AF. They have similar or superior efficacy with significantly lower intracranial haemorrhage rates. Warfarin remains indicated for: AF with moderate-severe mitral stenosis, mechanical heart valve prosthesis, and severe renal failure (eGFR <15). Apixaban has the most favourable safety profile including in elderly and CKD patients."],
    ["What annual stroke risk corresponds to each CHA2DS2-VASc score?", "Score 0: ~0% annual stroke risk. Score 1: ~1.3%. Score 2: ~2.2%. Score 3: ~3.2%. Score 4: ~4.0%. Score 5: ~6.7%. Score 6: ~9.8%. Score 7: ~9.6%. Score 8: ~12.5%. Score 9: ~15.2%. These are population estimates from the original Swedish cohort. Individual risk may vary based on comorbidities and AF burden."],
    ["What is the difference between CHA2DS2 and CHA2DS2-VASc?", "The original CHADS2 score (2001) used 5 parameters with a maximum score of 6. CHA2DS2-VASc (2010) refined it by adding vascular disease, age 65-74, and female sex, improving identification of truly low-risk patients (score 0 in men). CHA2DS2-VASc has replaced CHADS2 in all major guidelines because it better identifies patients who can safely avoid anticoagulation."],
    ["How does AF cause stroke?", "AF causes disorganised atrial electrical activity leading to stasis of blood in the left atrial appendage (LAA). This promotes thrombus formation in the LAA. Thrombus fragments embolise to the cerebral circulation causing cardioembolic stroke — typically larger territory infarcts with worse functional outcomes than atherosclerotic stroke. Anticoagulation prevents LAA thrombus formation and reduces stroke risk by ~64% compared to no therapy."],
],
"has-bled": [
    ["What is the HAS-BLED score?", "HAS-BLED estimates 1-year major bleeding risk in AF patients on anticoagulation. Parameters: Hypertension (SBP >160 mmHg), Abnormal renal function (dialysis, transplant, or creatinine >200 mcmol/L), Abnormal liver function (cirrhosis or bilirubin >2x + AST/ALT >3x normal), Stroke history, Bleeding history or predisposition, Labile INR (TTR <60%), Elderly (age >65), Drugs (antiplatelets/NSAIDs) or alcohol (1 point each). Maximum 9 points."],
    ["What does a high HAS-BLED score mean?", "Score 0-2: Low bleeding risk (<2% per year). Score >=3: High bleeding risk (>3-4% per year). A high HAS-BLED score should NOT automatically mean withholding anticoagulation — in most AF patients, stroke prevention benefit outweighs bleeding risk. Instead, use it to identify and correct modifiable bleeding risk factors: control hypertension, stop unnecessary antiplatelets/NSAIDs, address alcohol use, optimise INR control."],
    ["How does HAS-BLED compare to CHA2DS2-VASc?", "CHA2DS2-VASc estimates stroke risk (when to start anticoagulation). HAS-BLED estimates bleeding risk (how to manage it safely). Both should be used together. High CHA2DS2-VASc + high HAS-BLED usually still favours anticoagulation, but with DOAC preference over warfarin, more frequent monitoring, and aggressive modifiable risk factor management."],
    ["Which anticoagulant has the lowest bleeding risk in AF?", "Among DOACs, apixaban 5 mg BD has the most favourable bleeding profile — lower major bleeding than warfarin AND lower bleeding than rivaroxaban in head-to-head analyses. Dabigatran 110 mg BD (lower dose) also shows lower bleeding than warfarin with non-inferior stroke prevention. Warfarin has the highest intracranial haemorrhage rate. In elderly patients or those with high HAS-BLED, apixaban is generally preferred."],
    ["What is labile INR and how is it managed?", "Labile INR (HAS-BLED L parameter) is defined as time in therapeutic range (TTR) <60% on warfarin. It indicates unpredictable anticoagulation — increasing both stroke risk (supratherapeutic INR) and bleeding risk (subtherapeutic INR). Management: reinforce adherence and consistent vitamin K intake, identify interacting drugs, check for occult GI pathology. If TTR remains <65% despite optimisation, switch to a DOAC."],
    ["What are reversible HAS-BLED risk factors?", "Modifiable HAS-BLED factors: H — control hypertension (target <130/80 mmHg). A — correct renal/liver abnormalities where possible. L — improve INR control or switch to DOAC. D — stop antiplatelet drugs if not indicated (dual therapy with OAC significantly increases GI bleeding risk), avoid NSAIDs, address alcohol excess. Correcting these factors can meaningfully reduce bleeding risk without stopping anticoagulation."],
],
"ibw-calculator": [
    ["What is ideal body weight (IBW)?", "Ideal body weight (IBW) is a weight estimate used in clinical practice to calculate drug doses, ventilator tidal volumes, and nutritional requirements — based on height and sex rather than actual weight. The Devine formula (1974) is most widely used: IBW (men) = 50 + 2.3 x (height in inches - 60); IBW (women) = 45.5 + 2.3 x (height in inches - 60). It was originally derived for drug dosing, not as a health target."],
    ["What is the difference between IBW, ABW, and LBW?", "IBW (Ideal Body Weight): height-based estimate. ABW (Actual Body Weight): what the patient weighs now. LBW (Lean Body Weight): total body weight minus fat mass. For drug dosing: use IBW for most drugs in obese patients (aminoglycosides, vancomycin initial estimate, ventilator tidal volumes). Use ABW for some drugs with high lipophilicity (e.g. loading doses of amiodarone, heparin). Use Adjusted Body Weight (AdjBW = IBW + 0.4 x (ABW - IBW)) for aminoglycosides in obese patients."],
    ["When is IBW used for ventilator settings?", "Mechanical ventilator tidal volume is always set based on IBW (predicted body weight), not actual weight. Lung-protective ventilation: tidal volume 6 mL/kg IBW (ARDSNET protocol). Using actual weight in an obese patient would deliver excessive tidal volumes causing ventilator-induced lung injury (VILI). Plateau pressure target <30 cmH2O. IBW-based ventilation is the single most important intervention reducing ARDS mortality."],
    ["What is adjusted body weight and when is it used?", "Adjusted body weight (AdjBW) = IBW + 0.4 x (ABW - IBW). It is used when ABW exceeds IBW by >30% (i.e. obese patients). The 0.4 correction factor accounts for the partial distribution of drugs into adipose tissue. Used for: aminoglycoside dosing in obesity, some chemotherapy agents, heparin dosing. For enoxaparin in morbid obesity (BMI >40), use actual weight with anti-Xa monitoring rather than IBW."],
    ["What are the Devine formula limitations?", "The Devine formula was derived from a small dataset of non-obese adults and has no scientific basis for the specific constants used. It underestimates IBW for shorter individuals and is unreliable below 5 feet (60 inches). Alternative formulas include Hamwi (men: 106 lb for 5 ft + 6 lb per inch above; women: 100 lb + 5 lb per inch), Robinson, and Miller. For clinical drug dosing, consistency within an institution matters more than which formula is used."],
    ["How is IBW used in nutritional assessment?", "In nutritional support, IBW is used to calculate caloric and protein targets in obese patients — using actual body weight would lead to overfeeding. Standard targets: 25-30 kcal/kg IBW/day total energy; 1.2-2.0 g/kg IBW/day protein (higher end for critically ill, burns, trauma). In underweight patients (ABW < IBW), use actual body weight. In morbid obesity, use adjusted body weight (IBW + 25% of excess weight)."],
],
"iv-drip-rate-calculator": [
    ["How is IV drip rate calculated?", "Drip rate (drops/min) = (Volume in mL x Drop factor) / Time in minutes. Drop factor depends on the IV set: macro-drip sets = 15 drops/mL (standard adult) or 20 drops/mL; micro-drip sets = 60 drops/mL (paediatric, or for precise small-volume infusions). Example: 500 mL over 4 hours with 15 drops/mL set = (500 x 15) / 240 = 31 drops/min."],
    ["What is the difference between drops/min and mL/hr?", "mL/hr is used for infusion pumps and is independent of drop factor. Drops/min is used for gravity drip sets without a pump. Conversion: mL/hr = (drops/min x 60) / drop factor. Example: 31 drops/min with 15 drops/mL set = (31 x 60) / 15 = 124 mL/hr. Always use an infusion pump for critical medications (vasopressors, insulin, heparin, chemotherapy) — gravity drips are unreliable for precise dosing."],
    ["Which IV set drop factor is used in India?", "Standard government hospital IV sets in India: adult macro-drip = 15 drops/mL (BPL, Romsons, and most Indian manufacturers). Paediatric micro-drip sets = 60 drops/mL. Blood transfusion sets = 15 drops/mL with integral filter. Burette sets (100 mL chamber) = 60 drops/mL — used in paediatrics for precise volume control. Always confirm the drop factor printed on the IV set packaging before calculating."],
    ["What is the maximum safe infusion rate for common IV fluids?", "0.9% Normal Saline / Ringer's Lactate: typically 500-1000 mL/hr in resuscitation (no maximum in shock). KCl: never give as IV bolus — maximum concentration 40 mEq/L peripheral, 60-80 mEq/L central; maximum rate 20 mEq/hr (10 mEq/hr via peripheral with cardiac monitoring). Dextrose 50%: dilute before infusion, maximum 0.5 g/kg/hr. Vancomycin: maximum 10 mg/min (too fast causes Red Man Syndrome)."],
    ["How do you calculate paediatric IV fluid rates?", "Use the Holliday-Segar 4-2-1 rule for maintenance: 4 mL/kg/hr for first 10 kg + 2 mL/kg/hr for next 10 kg + 1 mL/kg/hr for each kg above 20 kg. Use a burette (60 drops/mL) or infusion pump for all paediatric infusions. For resuscitation boluses: 10-20 mL/kg of 0.9% saline over 15-30 min, reassess after each bolus. Avoid dextrose-containing fluids for resuscitation boluses."],
    ["What are common IV fluid administration errors?", "Common errors: wrong drop factor used in calculation, forgetting to account for infusion set dead space (typically 15-20 mL), free-flow events with gravity sets (always use anti-free-flow clamps), KCl mix-up (concentrated KCl must never be on ward shelves — dilute before use), wrong patient (always check wristband + fluid label), and extravasation of vesicant drugs. Use double-check protocols for all high-alert medications (insulin, heparin, KCl, concentrated electrolytes)."],
],
"map-calculator": [
    ["What is mean arterial pressure (MAP)?", "MAP (Mean Arterial Pressure) is the average arterial blood pressure throughout one cardiac cycle, weighted for the longer duration of diastole. Formula: MAP = DBP + 1/3 x (SBP - DBP), or equivalently MAP = (SBP + 2xDBP) / 3. It more accurately represents organ perfusion pressure than systolic BP alone. Normal MAP is 70-100 mmHg."],
    ["Why is MAP important in critical care?", "MAP is the key target in haemodynamic resuscitation because it directly determines organ perfusion pressure. MAP = Cardiac Output x Systemic Vascular Resistance. In septic shock, MAP target is >=65 mmHg (Surviving Sepsis Campaign). In traumatic brain injury, MAP target is >=80-90 mmHg to maintain cerebral perfusion pressure (CPP = MAP - ICP). In cardiogenic shock, maintaining MAP >=65 prevents multiorgan failure."],
    ["What MAP indicates hypotension?", "MAP <65 mmHg is the critical threshold for defining haemodynamically significant hypotension in most guidelines. MAP <65 impairs perfusion to kidneys (AKI risk), gut (ischaemia, bacterial translocation), brain (reduced CPP), and coronary arteries. A MAP of 50-60 mmHg for more than 30 minutes is associated with AKI, MI, and 30-day mortality even in non-ICU patients. MAP should be measured invasively (arterial line) in unstable patients."],
    ["What is the difference between MAP and pulse pressure?", "MAP represents average perfusion pressure. Pulse pressure (PP) = SBP - DBP, normally 40 mmHg. Pulse pressure reflects stroke volume and arterial compliance. Wide PP (>60 mmHg): aortic regurgitation, hyperthyroidism, arteriovenous fistula, severe anaemia, patent ductus arteriosus. Narrow PP (<25 mmHg or <25% of SBP): indicates low stroke volume — cardiac tamponade, severe aortic stenosis, cardiogenic shock, hypovolaemia."],
    ["What vasopressors are used to raise MAP?", "First-line: noradrenaline (norepinephrine) — alpha-1 adrenergic vasoconstriction raises SVR and MAP with minimal tachycardia; dose 0.01-3 mcg/kg/min IV infusion. Second-line: vasopressin 0.03-0.04 units/min (spares noradrenaline dose, no dose titration). Third-line: adrenaline (epinephrine) for refractory shock or anaphylaxis. Dopamine is no longer first-line (higher arrhythmia risk than noradrenaline per SOAP II trial)."],
    ["How is MAP monitored in clinical practice?", "Non-invasive: oscillometric BP cuff gives MAP directly (displayed on modern monitors). Less accurate in arrhythmias, peripheral vasoconstriction, and morbid obesity. Invasive: radial arterial line (preferred) gives continuous beat-to-beat MAP waveform — gold standard in ICU and major surgery. Arterial waveform analysis also gives dynamic parameters (pulse pressure variation, stroke volume variation) to guide fluid responsiveness assessment."],
],
"qsofa-score": [
    ["What is the qSOFA score?", "qSOFA (quick Sequential Organ Failure Assessment) is a bedside sepsis screening tool using 3 parameters: Respiratory rate >=22/min (1 point), Altered mentation/GCS <15 (1 point), Systolic BP <=100 mmHg (1 point). Score 0-3. A score >=2 outside the ICU suggests possible sepsis and warrants urgent evaluation including blood cultures, lactate, and full SOFA assessment."],
    ["How sensitive is qSOFA for sepsis?", "qSOFA has specificity ~83% but sensitivity only ~60-70% for sepsis — meaning ~30-40% of sepsis cases will have a qSOFA score <2. A negative qSOFA does NOT exclude sepsis. Clinical suspicion of infection with any organ dysfunction should trigger sepsis workup regardless of qSOFA score. qSOFA performs better as a prognostic tool (predicting poor outcomes) than as a screening tool in suspected infection."],
    ["What is the difference between qSOFA and SIRS criteria for sepsis?", "Old definition (Sepsis-2, 2001): sepsis = infection + >=2 SIRS criteria (temperature, HR, RR, WBC). New definition (Sepsis-3, 2016): sepsis = infection + organ dysfunction (SOFA increase >=2). qSOFA is a bedside proxy for organ dysfunction outside the ICU. SIRS criteria are sensitive but non-specific (also triggered by non-infectious causes: trauma, pancreatitis, burns). Sepsis-3/qSOFA identifies sicker patients with higher mortality than Sepsis-2/SIRS."],
    ["What is septic shock and how does it differ from sepsis?", "Sepsis-3 definition of septic shock: sepsis + vasopressor requirement to maintain MAP >=65 mmHg AND lactate >2 mmol/L despite adequate fluid resuscitation. Septic shock carries >40% hospital mortality vs ~10% for sepsis without shock. Key distinction: lactate >4 mmol/L indicates severe tissue hypoperfusion requiring immediate aggressive resuscitation regardless of blood pressure."],
    ["What is the 1-hour sepsis bundle?", "Surviving Sepsis Campaign 1-hour bundle: (1) Measure lactate — repeat if initial lactate >2 mmol/L. (2) Obtain blood cultures before antibiotics (at least 2 sets, don't delay antibiotics >45 min for culture). (3) Administer broad-spectrum IV antibiotics. (4) Give IV crystalloid 30 mL/kg if hypotensive or lactate >=4 mmol/L. (5) Start vasopressors (noradrenaline) if MAP <65 despite fluids. Reassess fluid responsiveness with dynamic measures to avoid fluid overload."],
    ["What are common causes of sepsis in Indian hospitals?", "Most common sources of sepsis in India: urinary tract infection (Gram-negative: E.coli, Klebsiella — high ESBL rates in community), pneumonia (S. pneumoniae, Klebsiella, Acinetobacter in HAP), abdominal/biliary sepsis, skin and soft tissue infections, central line-associated bloodstream infections (CLABSI), and dengue with secondary bacterial infection. Tropical infections causing sepsis: malaria (P. falciparum), scrub typhus, leptospirosis — consider in febrile patients from endemic areas."],
],
"rcri-calculator": [
    ["What is the RCRI score?", "The Revised Cardiac Risk Index (RCRI), developed by Lee et al. (1999), predicts the risk of major adverse cardiac events (MACE — cardiac death, MI, cardiac arrest, complete heart block, pulmonary oedema) after non-cardiac surgery. Six predictors, each 1 point: high-risk surgery, ischaemic heart disease, congestive heart failure, cerebrovascular disease, insulin-dependent diabetes, creatinine >2.0 mg/dL."],
    ["How does RCRI guide preoperative cardiac assessment?", "RCRI 0: very low risk (~0.4% MACE) — proceed to surgery. RCRI 1: low risk (~1%) — proceed. RCRI 2: moderate risk (~2.4%) — consider further evaluation if it will change management. RCRI >=3: high risk (>5.4%) — cardiology review, consider further cardiac testing (stress echo, myocardial perfusion), optimise medical therapy before surgery."],
    ["When is preoperative cardiac testing indicated?", "Functional capacity is the key determinant: if patient can perform >=4 METs activity (climb one flight of stairs, walk on level ground at 4 mph) without symptoms, proceed to surgery without further testing. If functional capacity <4 METs or unknown AND surgery is high-risk AND test result would change management: consider pharmacological stress testing (dobutamine stress echo or nuclear perfusion). Routine ECG/echo/troponin is NOT recommended for low-risk surgery."],
    ["What cardiac medications should be continued perioperatively?", "Continue: beta-blockers (do NOT stop abruptly — rebound ischaemia risk; if not on beta-blocker pre-op, do not start acutely within 24 hours), statins (continue — pleiotropic cardioprotective effects), aspirin (continue for high-risk cardiac patients; stop for low-risk elective surgery). Hold: ACE inhibitors/ARBs on day of surgery (hypotension risk with anaesthesia). Resume all cardiac medications as soon as patient is eating post-operatively."],
    ["What is high-risk surgery for cardiac purposes?", "High cardiac risk surgery (>1% MACE risk): aortic and major vascular surgery (open AAA repair, aorto-bifemoral bypass), peripheral arterial surgery, thoracic surgery, abdominal surgery (especially emergency), orthopaedic surgery (hip/knee replacement), head and neck cancer surgery, prolonged surgery with major fluid shifts. Low risk (<1% MACE): endoscopy, breast surgery, cataract, superficial procedures, and most ambulatory surgery."],
    ["What is the role of troponin monitoring perioperatively?", "Myocardial Injury after Non-cardiac Surgery (MINS) — troponin elevation within 30 days of surgery — occurs in ~8% of patients >=45 years and is associated with 30-day mortality of 10%. ESC 2022 guidelines recommend preoperative troponin measurement in high-risk patients and post-operative monitoring at 24 and 48 hours after major surgery. MINS is managed with aspirin, statin, and ACE inhibitor. Dabigatran reduced MINS events in the MANAGE trial."],
],
"sirs-criteria": [
    ["What are the SIRS criteria?", "SIRS (Systemic Inflammatory Response Syndrome) is defined by 2 or more of: Temperature >38C or <36C, Heart rate >90 bpm, Respiratory rate >20/min or PaCO2 <32 mmHg, WBC >12,000 or <4,000 cells/mm3 or >10% bands. SIRS was the original framework for sepsis diagnosis (Sepsis-1/2 definitions, 1991-2001) but has been largely replaced by Sepsis-3 (SOFA-based) criteria."],
    ["Why were SIRS criteria replaced by Sepsis-3?", "SIRS criteria are highly sensitive (~97%) but poorly specific — SIRS is triggered by non-infectious causes including trauma, pancreatitis, burns, surgery, and autoimmune disease. This low specificity meant many non-septic patients were labelled as septic. Sepsis-3 (2016) replaced SIRS with organ dysfunction (SOFA score increase >=2) as the defining feature of sepsis, better identifying patients with life-threatening infection."],
    ["Can SIRS criteria still be useful?", "SIRS criteria retain clinical utility in several contexts: as a simple bedside trigger for infection suspicion in primary care and district hospital settings where SOFA calculation is impractical, in paediatric sepsis (pSOFA and paediatric SIRS criteria are used for children), and as part of scoring systems for pancreatitis (BISAP uses SIRS as one component). SIRS >=2 in the context of suspected infection should still prompt blood cultures and antibiotic consideration."],
    ["What is the difference between SIRS, sepsis, severe sepsis, and septic shock?", "Old Sepsis-2 definitions: SIRS = 2+ criteria. Sepsis = SIRS + suspected infection. Severe sepsis = Sepsis + organ dysfunction. Septic shock = Severe sepsis + refractory hypotension. Sepsis-3 definitions (current): Sepsis = infection + organ dysfunction (SOFA >=2). Septic shock = Sepsis + vasopressor requirement to maintain MAP >=65 AND lactate >2 mmol/L. The term 'severe sepsis' has been retired."],
    ["What is the NEWS2 score and how does it relate to SIRS?", "NEWS2 (National Early Warning Score 2) is a standardised deterioration scoring system used in hospitalised patients. Unlike SIRS, NEWS2 does not require laboratory values — it uses 7 bedside parameters (RR, SpO2, O2 supplementation, SBP, HR, consciousness, temperature). NEWS2 >=5 or any single parameter scoring 3 triggers urgent clinical review. NEWS2 and qSOFA are complementary to SIRS in identifying deteriorating patients in different clinical settings."],
    ["What blood tests are done when sepsis is suspected?", "Immediate investigations in suspected sepsis: Blood cultures x2 (before antibiotics if possible, do not delay antibiotics >45 min), FBC (leucocytosis/leucopaenia, thrombocytopaenia), CRP and procalcitonin (elevated in bacterial infection, PCT >0.5 ng/mL suggests bacterial sepsis), serum lactate (>2 mmol/L indicates tissue hypoperfusion), creatinine, bilirubin, LFTs (SOFA parameters), blood glucose, coagulation screen (DIC if severely deranged), and ABG if respiratory compromise."],
],
"tsh-interpreter": [
    ["How do I interpret TSH levels?", "TSH (Thyroid Stimulating Hormone) is the best single test for thyroid function. Normal range: 0.4-4.0 mIU/L (lab-specific ranges may vary slightly). TSH <0.4: hyperthyroidism (low TSH, high T4/T3). TSH 4.0-10.0 with normal T4: subclinical hypothyroidism. TSH >10 or raised TSH with low T4: overt hypothyroidism. In pregnancy: TSH targets are lower — first trimester <2.5 mIU/L, second/third <3.0 mIU/L."],
    ["What is subclinical hypothyroidism and does it need treatment?", "Subclinical hypothyroidism: TSH 4.0-10.0 mIU/L with normal free T4. Treat if: TSH >10 mIU/L (ATA/ETA guidelines), symptoms of hypothyroidism present, positive anti-TPO antibodies (higher progression risk), pregnancy or planning pregnancy, or age <65 with cardiovascular risk factors. Do not routinely treat asymptomatic subclinical hypothyroidism with TSH 4-10 in elderly patients >65 — TRUST trial showed no benefit and potential harm."],
    ["What causes elevated TSH?", "Most common: primary hypothyroidism (Hashimoto thyroiditis — autoimmune, most common cause in India; post-radioiodine/surgery; iodine deficiency in remote areas). Less common: central hypothyroidism has LOW TSH with low T4 (pituitary/hypothalamic disease). Drugs causing elevated TSH: lithium, amiodarone, interferon-alpha, tyrosine kinase inhibitors. Transient TSH elevation: non-thyroidal illness recovery, assay interference (heterophile antibodies)."],
    ["What causes suppressed TSH?", "TSH <0.1 mIU/L: Graves disease (autoimmune, most common cause of hyperthyroidism in India), toxic multinodular goitre, toxic adenoma, subacute (de Quervain) thyroiditis (painful, post-viral), postpartum thyroiditis. Drugs: excess levothyroxine, high-dose glucocorticoids, dopamine infusion. TSH 0.1-0.4 (mild suppression): subclinical hyperthyroidism — monitor, treat if symptomatic, AF, osteoporosis risk, or age >65."],
    ["What is the starting dose of levothyroxine for hypothyroidism?", "Standard starting dose: 1.6 mcg/kg/day actual body weight in young, healthy adults. In elderly patients (>65) or those with ischaemic heart disease: start low at 12.5-25 mcg/day and titrate up by 12.5-25 mcg every 6-8 weeks. In severe hypothyroidism or myxoedema coma: initiate in hospital with IV levothyroxine 200-500 mcg stat + hydrocortisone (exclude concurrent adrenal insufficiency before giving T4). Recheck TSH after 6-8 weeks of any dose change."],
    ["How is hypothyroidism monitored on treatment?", "Recheck TSH 6-8 weeks after starting or changing levothyroxine dose. Once stable, check TSH annually. Target TSH: 0.5-2.5 mIU/L for most patients. In elderly: TSH 1-4 mIU/L (slightly higher target reduces over-treatment risks). In pregnancy: TSH <2.5 mIU/L in first trimester (increase levothyroxine dose by 25-30% immediately on confirming pregnancy). Take levothyroxine on an empty stomach 30-60 minutes before breakfast — calcium, iron, and PPIs reduce absorption."],
],
"psi-calculator": [
    ["What is the PSI/PORT score?", "The PSI (Pneumonia Severity Index), also called the PORT score, stratifies death risk from community-acquired pneumonia (CAP) in adults. It uses demographic factors, comorbidities, physical exam findings, and lab/X-ray results. Risk classes: I (age <50, no comorbidities, normal vitals) = very low risk; II (score <=70) = low; III (71-90) = moderate; IV (91-130) = high; V (>130) = very high risk."],
    ["How does PSI compare to CURB-65?", "PSI is more accurate (20 variables) especially for identifying low-risk outpatient CAP. CURB-65 is faster (5 variables) and better for identifying high-risk patients needing ICU. PSI overestimates risk in elderly (age contributes heavily). CURB-65 may underestimate risk in young patients with severe physiological derangement. Use both together with clinical judgment — CURB-65 >=3 or PSI class IV-V should prompt ICU review."],
    ["What are PSI Class I criteria?", "PSI Class I (outpatient eligible): age <50 years AND none of: neoplastic disease, liver disease, CHF, CVD, renal disease AND no altered mental status AND pulse <125/min AND RR <30/min AND SBP >=90 mmHg AND temperature 35-39.9C. Class I patients have <0.1% 30-day mortality and can be treated as outpatients if social circumstances are adequate."],
    ["What antibiotics are used for CAP by PSI class?", "PSI Class I-II (outpatient): oral amoxicillin 500 mg TDS x 5 days +/- azithromycin 500 mg OD x 3 days for atypical cover. PSI Class III (consider admission): oral/IV co-amoxiclav + macrolide. PSI Class IV-V (hospital): IV co-amoxiclav or ceftriaxone + IV azithromycin. Severe/ICU CAP: IV piperacillin-tazobactam + macrolide. Always adjust per local antibiogram — India has high rates of resistant Gram-negatives."],
    ["What PSI lab values score highest?", "Highest-scoring PSI lab parameters (20 points each): BUN >=30 mg/dL, sodium <130 mEq/L. Other lab parameters (10 points each): glucose >=250 mg/dL, haematocrit <30%, PaO2 <60 mmHg or SpO2 <90%, pleural effusion on CXR. These add to base score from age, sex, comorbidities, and vital signs to give total PSI class."],
    ["How is PSI used for discharge decisions?", "PSI class II-III patients improving on treatment (afebrile 24 hours, RR <24/min, SpO2 >=90% on room air, tolerating oral intake, normal orientation) can switch to oral antibiotics and discharge within 24-48 hours of admission. CXR lags clinical recovery by weeks — a worsening CXR in a clinically improving patient should not delay discharge. Follow-up CXR at 6-8 weeks recommended only if symptoms persist or malignancy risk (age >50, smoker)."],
],
"phq9-gad7": [
    ["What is the PHQ-9?", "The PHQ-9 (Patient Health Questionnaire-9) is a validated 9-item screening and severity tool for depression based on DSM-5 criteria. Each item scores 0-3 (not at all to nearly every day). Total 0-27. Thresholds: 0-4 minimal, 5-9 mild, 10-14 moderate, 15-19 moderately severe, >=20 severe depression. Sensitivity ~88%, specificity ~85% for major depression. Validated in Hindi, Punjabi, and other Indian languages."],
    ["What is the GAD-7?", "The GAD-7 (Generalised Anxiety Disorder 7-item scale) screens for and measures severity of anxiety. Scores 0-21. Thresholds: 0-4 minimal, 5-9 mild, 10-14 moderate, >=15 severe GAD. Both PHQ-9 and GAD-7 are recommended by WHO mhGAP guidelines and NIMHANS for use at primary care level in India. They are freely available and require no training beyond basic clinical skills."],
    ["When should antidepressants be started?", "Antidepressants are indicated for moderate-severe depression (PHQ-9 >=10) with functional impairment, or when psychotherapy alone is insufficient. SSRIs are first-line: sertraline 50 mg OD, escitalopram 10 mg OD, or fluoxetine 20 mg OD. Full effect takes 4-6 weeks. If no response after 6-8 weeks at adequate dose, consider switching or augmenting. Minimum duration: 6-12 months after first episode, longer after recurrence or severe/psychotic features."],
    ["How should PHQ-9 item 9 (suicidal ideation) be handled?", "PHQ-9 item 9 asks about thoughts of being better off dead or self-harm. Any score >=1 requires direct clinical assessment of suicidal ideation, intent, and plan. Refer to mental health services if active suicidal ideation with plan. Provide crisis resources: iCall 9152987821, Vandrevala Foundation 1860-2662-345, NIMHANS helpline 080-46110007. Document all safety assessments and management plans clearly."],
    ["Are PHQ-9 and GAD-7 validated for Indian populations?", "Yes. Both tools have been extensively validated in Indian populations across multiple studies in Hindi, Punjabi, Tamil, Telugu, Bengali, and Marathi. They are used in NMHP (National Mental Health Programme), recommended in Indian Primary Care Mental Health guidelines, and endorsed by NIMHANS and WHO South-East Asia Regional Office. Sensitivity and specificity are comparable to validation in Western populations."],
    ["What is the difference between PHQ-2 and PHQ-9?", "PHQ-2 is a 2-item ultra-brief screen asking only about low mood and anhedonia (core depression features). PHQ-2 score >=3 is a positive screen requiring full PHQ-9 assessment. PHQ-2 is used for rapid population screening in antenatal clinics, diabetic clinics, and GP visits. PHQ-9 is used when depression is clinically suspected or PHQ-2 is positive. Using PHQ-2 first reduces assessment burden in busy primary care settings."],
],
}

# ── INFO SECTIONS ────────────────────────────────────────────────────
INFO = {
"abcd2-score": ("About the ABCD2 Score — TIA Risk Stratification", [
    "The ABCD2 score was developed to help clinicians stratify the short-term stroke risk after a transient ischaemic attack (TIA) and prioritise urgent investigation and treatment. TIA is a medical emergency — the risk of stroke is highest in the first 48 hours, with approximately 10-15% of TIA patients suffering a stroke within 3 months if untreated. Early secondary prevention can reduce this risk by up to 80%.",
    "Despite its widespread use, the ABCD2 score has significant limitations and is no longer the primary triage tool in many high-income country guidelines. It does not capture high-risk TIA features such as atrial fibrillation, significant carotid stenosis, or DWI-positive MRI lesions — all of which independently predict high early stroke risk regardless of ABCD2 score. Current NICE (2019) and ESO guidelines recommend urgent specialist TIA clinic assessment within 24 hours for all TIA patients.",
    "In the Indian context, TIA management is complicated by limited access to MRI and specialist neurology services at secondary care level. ABCD2 remains useful for triage in resource-limited settings — patients with score >=4 should be prioritised for urgent referral. All TIA patients, regardless of ABCD2 score, should receive immediate aspirin 300 mg, statin therapy, and blood pressure control pending specialist review.",
]),
"ascvd-risk": ("About the ASCVD Risk Calculator", [
    "The ACC/AHA Pooled Cohort Equations estimate the 10-year risk of a first major atherosclerotic cardiovascular event — non-fatal myocardial infarction, coronary heart disease death, or fatal/non-fatal stroke — in patients aged 40-79 without pre-existing cardiovascular disease. The calculator integrates traditional risk factors (age, sex, cholesterol, blood pressure, diabetes, smoking) to guide primary prevention decisions, particularly statin initiation.",
    "An important caveat for Indian clinicians: the Pooled Cohort Equations were derived from US cohorts and are known to overestimate cardiovascular risk in contemporary populations while potentially underestimating risk in South Asians. Indians develop cardiovascular disease at younger ages and lower BMI and LDL levels than Western populations, partly due to higher visceral adiposity and insulin resistance. A 10-year ASCVD risk of 5-7% in an Indian patient may warrant more aggressive intervention than the same score in a Western patient.",
    "Beyond the calculated score, risk-enhancing factors substantially modify treatment decisions: family history of premature ASCVD (first-degree relative, men <55, women <65), LDL >=160 mg/dL, metabolic syndrome, chronic kidney disease, inflammatory conditions (RA, psoriasis, HIV), high-sensitivity CRP >=2 mg/L, and ABI <0.9. Coronary calcium scoring (CAC) is the most powerful risk reclassifier in borderline-risk patients and is increasingly available in Indian cities.",
]),
"cha2ds2-vasc": ("About the CHA2DS2-VASc Score", [
    "Atrial fibrillation (AF) is the most common sustained cardiac arrhythmia and the leading cause of cardioembolic stroke worldwide. In India, AF prevalence is approximately 0.5-1% of the adult population and is rising with the ageing demographic. The CHA2DS2-VASc score, developed by Lip et al. in 2010, provides a simple framework for estimating annual stroke risk and guiding anticoagulation decisions in non-valvular AF.",
    "The score refined the earlier CHADS2 system by adding vascular disease, age 65-74, and female sex as additional risk modifiers, improving identification of truly low-risk patients who can safely avoid anticoagulation. A CHA2DS2-VASc score of 0 in men (1 in women) identifies a very low-risk group (~0.5% annual stroke risk) for whom the bleeding risk of anticoagulation likely outweighs benefit.",
    "In Indian practice, anticoagulant choice is influenced by cost and access. DOACs (direct oral anticoagulants) — apixaban, rivaroxaban, dabigatran — are now the preferred agents over warfarin per ESC, AHA, and Cardiological Society of India guidelines. However, cost remains a barrier and warfarin remains widely used. For patients on warfarin, achieving a time in therapeutic range (TTR) >70% is essential — if TTR cannot be maintained, switch to a DOAC if feasible.",
]),
"map-calculator": ("About the MAP Calculator", [
    "Mean arterial pressure (MAP) is a fundamental haemodynamic parameter representing the average blood pressure throughout the cardiac cycle, weighted to account for the longer duration of diastole (~2/3 of the cycle). Unlike systolic BP, MAP correlates directly with organ perfusion pressure and tissue oxygen delivery, making it the key target in haemodynamic resuscitation and critical care management.",
    "The clinical significance of MAP lies in its role in maintaining perfusion to vital organs. Each organ system has a lower limit of MAP below which autoregulation fails and perfusion becomes pressure-dependent: the brain requires MAP >=60 mmHg (or higher in TBI — >=70-80 mmHg to maintain cerebral perfusion pressure), the kidneys require MAP >=65-70 mmHg for adequate glomerular filtration, and the coronary circulation depends on adequate diastolic pressure for myocardial perfusion.",
    "In septic shock, the Surviving Sepsis Campaign targets MAP >=65 mmHg with noradrenaline as first-line vasopressor. However, a higher MAP target (80-85 mmHg) may benefit patients with pre-existing hypertension or chronic kidney disease, as shown in the SEPSISPAM trial — where the higher target reduced the need for renal replacement therapy in hypertensive patients. MAP monitoring should be continuous via arterial line in any patient requiring vasopressors.",
]),
"tsh-interpreter": ("About the TSH Interpreter", [
    "Thyroid disorders are among the most common endocrine conditions in India, with hypothyroidism (particularly Hashimoto thyroiditis) affecting an estimated 10-12% of the adult population. TSH (thyroid stimulating hormone) is the pituitary hormone that regulates thyroid function and is the single most sensitive test for thyroid dysfunction — it rises before T4 falls (in early hypothyroidism) and falls before T4 rises (in early hyperthyroidism), making it the ideal screening and monitoring test.",
    "TSH interpretation requires clinical context. TSH can be transiently suppressed in acute illness (non-thyroidal illness syndrome / sick euthyroid syndrome) without true hyperthyroidism. TSH can be falsely elevated in the recovery phase of illness, by certain drugs (lithium, amiodarone, metoclopramide), and by assay interference from heterophile antibodies. A mildly abnormal TSH in a hospitalised acutely ill patient should be repeated after recovery before committing to thyroid diagnosis.",
    "Amiodarone deserves special mention: it contains 37% iodine by weight and causes complex thyroid effects. It inhibits T4-to-T3 conversion, causing elevated T4 and TSH in early use (euthyroid state). Amiodarone-induced hypothyroidism (AIH) requires levothyroxine treatment. Amiodarone-induced thyrotoxicosis (AIT) is more complex — Type 1 (excess iodine, pre-existing thyroid disease) and Type 2 (destructive thyroiditis) require different treatment (carbimazole vs prednisolone respectively).",
]),
"sirs-criteria": ("About SIRS Criteria and Sepsis Definitions", [
    "The Systemic Inflammatory Response Syndrome (SIRS) criteria were introduced by Bone et al. at the 1991 ACCP/SCCM Consensus Conference as a framework for identifying patients with a generalised inflammatory response, whether infectious or non-infectious. SIRS represented the first standardised definition of sepsis and enabled clinical research and trial enrolment for nearly two decades.",
    "However, the limitations of SIRS became increasingly apparent: its high sensitivity (~97%) came at the cost of very poor specificity — SIRS criteria are met by the majority of ICU patients regardless of infection, and by many ward patients post-surgery, with pancreatitis, burns, or autoimmune disease. The 2016 Sepsis-3 consensus replaced SIRS with organ dysfunction (acute SOFA score increase >=2) as the defining criterion for sepsis, better identifying the subset of infected patients with life-threatening organ failure and high mortality.",
    "Despite its replacement in formal definitions, SIRS retains practical value in resource-limited settings. In district hospitals and primary care centres without rapid SOFA component testing, SIRS criteria plus clinical suspicion of infection remain a reasonable trigger for blood cultures, empirical antibiotics, and patient escalation. SIRS is also still embedded in scoring systems (BISAP for pancreatitis) and paediatric sepsis definitions. The clinical priority remains early recognition of sick patients — any scoring system is a tool, not a substitute for clinical judgment.",
]),
"qsofa-score": ("About the qSOFA Score", [
    "The qSOFA (quick SOFA) score was introduced as part of the Sepsis-3 definitions (Singer et al., JAMA 2016) as a simple bedside tool to identify adult patients outside the ICU who may have sepsis and are at risk of prolonged ICU admission or in-hospital death. Its three parameters — altered mentation, respiratory rate >=22/min, and systolic BP <=100 mmHg — require no laboratory tests and can be assessed in under 60 seconds.",
    "qSOFA's clinical role is as a risk stratifier, not a diagnostic tool. A qSOFA score >=2 in a patient with suspected infection should prompt urgent blood cultures, serum lactate measurement, full SOFA assessment, early antibiotic administration, and consideration of ICU transfer. However, a qSOFA score <2 does not exclude sepsis — clinical suspicion of serious infection should trigger appropriate workup regardless of the score, particularly in immunocompromised patients who may not mount the expected physiological response.",
    "In the Indian clinical context, qSOFA is particularly valuable at the point of triage in emergency departments and general medical wards where full SOFA calculation may not be immediately feasible. Combined with serum lactate (>2 mmol/L independently predicts poor outcomes) and clinical assessment, qSOFA provides a practical framework for early sepsis identification. The Sepsis-1 bundle — cultures, antibiotics, fluids, vasopressors — should not be delayed pending score calculation.",
]),
"rcri-calculator": ("About the RCRI — Preoperative Cardiac Risk", [
    "The Revised Cardiac Risk Index (RCRI), developed by Lee et al. and published in Circulation (1999), is the most widely validated and used preoperative cardiac risk assessment tool for patients undergoing non-cardiac surgery. It identified six independent predictors of major perioperative cardiac events from a derivation cohort of 2893 patients and validation in 1422 patients undergoing elective non-cardiac surgery.",
    "The RCRI guides the stepwise approach to preoperative cardiac assessment recommended by ESC/ESA (2022) and ACC/AHA (2014/2022) guidelines: estimate surgical risk (procedure type), assess functional capacity (METs), calculate RCRI, then decide whether further cardiac testing would change management. The key principle is that preoperative cardiac testing is only warranted if the result would alter the decision to proceed or the anaesthetic/surgical approach — testing for reassurance alone is not recommended.",
    "In Indian practice, the RCRI is particularly relevant given the high burden of undiagnosed ischaemic heart disease, diabetes, and hypertension in the surgical population. Many patients presenting for elective surgery in India have not had cardiac risk factor assessment and may have silent ischaemic heart disease. An RCRI >=2 in an Indian patient should prompt careful history and ECG review, and RCRI >=3 should trigger cardiology input before major elective surgery.",
]),
"ibw-calculator": ("About the IBW Calculator", [
    "Ideal body weight (IBW) is a calculated weight estimate used in clinical pharmacology and critical care to guide drug dosing and physiological parameter calculation in patients whose actual body weight significantly differs from what their height-sex profile would predict. Unlike BMI, which assesses health risk, IBW is a practical clinical tool for dosing calculations.",
    "The most important clinical application of IBW is in mechanical ventilation: the ARDSNet lung-protective ventilation protocol mandates tidal volume of 6 mL/kg of IBW (predicted body weight), not actual weight. In an obese patient (ABW 120 kg, IBW 70 kg), using actual weight would deliver tidal volumes of 720 mL — far exceeding safe limits and causing ventilator-induced lung injury. This distinction is literally life-saving in ARDS management.",
    "For drug dosing in obese patients, the choice between IBW, adjusted body weight (AdjBW), and actual body weight depends on the drug's volume of distribution and lipophilicity. Hydrophilic drugs (aminoglycosides, beta-lactam antibiotics) distribute primarily in lean tissue — use IBW or AdjBW. Lipophilic drugs (loading doses of amiodarone, some benzodiazepines) partially distribute into fat — use actual body weight for loading doses. When in doubt, consult clinical pharmacist and monitor drug levels.",
]),
"iv-drip-rate-calculator": ("About the IV Drip Rate Calculator", [
    "Accurate IV fluid and drug infusion rate calculation is a fundamental clinical skill that directly impacts patient safety. Errors in drip rate calculation are among the most common medication errors in hospital practice, particularly in settings without infusion pumps. The basic drip rate formula — (Volume x Drop factor) / Time in minutes — must be applied correctly using the specific drop factor of the IV administration set being used.",
    "In Indian government hospitals, the standard adult IV set has a drop factor of 15 drops/mL (macro-drip). Paediatric burette sets use 60 drops/mL (micro-drip), enabling precise small-volume infusions. Blood transfusion sets also use 15 drops/mL with an integral filter. Always verify the drop factor from the packaging of the specific set — different manufacturers may vary, and using the wrong drop factor leads to systematic over- or under-infusion.",
    "High-alert medications — including concentrated potassium chloride, insulin, heparin, vasopressors, and chemotherapy — should never be administered via gravity drip without an infusion pump. KCl must never be given as an IV push or rapid infusion (cardiac arrest risk). Concentrated KCl ampoules should not be stored on general wards. These principles are embedded in WHO and NABH patient safety standards and should be implemented at all levels of care.",
]),
"psi-calculator": ("About the PSI/PORT Score for Pneumonia", [
    "The Pneumonia Severity Index (PSI), also known as the PORT (Patient Outcomes Research Team) score, was developed by Fine et al. (NEJM 1997) from a study of nearly 15,000 patients with community-acquired pneumonia. It remains the most extensively validated CAP severity score and is particularly powerful for identifying low-risk patients safe for outpatient treatment — its primary clinical utility.",
    "PSI class I patients (age <50, no comorbidities, normal vitals) have a 30-day mortality of <0.1% and do not require hospital admission in the absence of social or practical barriers. PSI classes II-III carry low-moderate mortality (0.6-2.8%) and can often be managed with short hospital stays or outpatient treatment with close follow-up. Classes IV-V have high mortality (8.2-29.2%) and require hospitalisation with consideration of ICU admission.",
    "In Indian practice, CAP management is complicated by high rates of antibiotic resistance (ESBL-producing Enterobacteriaceae, multidrug-resistant Klebsiella and Acinetobacter in hospital-acquired pneumonia), atypical pathogen burden (Mycoplasma, Chlamydia, Legionella — particularly in outbreaks), and tropical co-infections (melioidosis in northeast India, scrub typhus). PSI should always be used alongside microbiological results and local resistance patterns rather than as a standalone treatment guide.",
]),
"phq9-gad7": ("About PHQ-9 and GAD-7", [
    "Depression and anxiety are the most prevalent mental health disorders worldwide and carry significant morbidity, mortality (through suicide and cardiovascular disease), and socioeconomic burden. In India, the National Mental Health Survey 2016 estimated that 1 in 7 Indians suffered from a mental disorder, with depression and anxiety accounting for the majority. Despite this burden, treatment gap remains enormous — estimated at 70-92% for mental disorders in India.",
    "The PHQ-9 and GAD-7 were developed by Spitzer, Kroenke, and colleagues and directly operationalise DSM diagnostic criteria for major depression and generalised anxiety disorder respectively. They are freely available, require no training beyond basic clinical skills, and have been validated in multiple Indian languages. Both tools serve dual purposes: screening (identifying cases in the population) and severity monitoring (tracking treatment response over time).",
    "An important clinical caveat: PHQ-9 and GAD-7 are screening tools — not diagnostic instruments. A high score prompts further clinical assessment; it does not automatically confirm diagnosis. Comorbid medical conditions (hypothyroidism, anaemia, chronic pain, sleep disorders) can elevate PHQ-9 scores independently of true depression. PHQ-9 item 9 (passive suicidal ideation) requires careful direct clinical assessment — any score above 0 on this item warrants a structured suicide risk assessment and documentation.",
]),
}

INFO_CSS = """
    .info-section { background: var(--surface, #fff); border-radius: var(--radius, 14px); border: 1px solid var(--border, #dce4ef); box-shadow: var(--shadow, 0 2px 16px rgba(15,30,51,.09)); padding: 28px; margin-bottom: 24px; }
    .info-section h2 { font-size: 1.15rem; font-weight: 700; color: var(--primary-dark, #0c4a6e); margin-bottom: 14px; }
    .info-section p { font-size: .9rem; color: var(--text-muted, #5a6a82); line-height: 1.8; margin-bottom: 12px; }
    .info-section p:last-child { margin-bottom: 0; }"""

def path_to_url(rel: str) -> str:
    p = rel.replace("\\", "/").lstrip("/")
    if p.endswith("/index.html"): p = p[:-len("index.html")]
    elif p.endswith(".html"): p = p[:-5]
    return BASE + "/" + p.rstrip("/")

def fix_canonical(content, expected_url):
    changes = []
    # Fix existing canonical
    def replacer(m):
        href = m.group(1)
        if href == expected_url:
            return m.group(0)
        # relative or wrong domain or has .html
        clean = href
        if "thezerowhisper.github.io" in clean:
            clean = clean.replace("https://thezerowhisper.github.io", BASE)
        if clean.startswith("/"):
            clean = BASE + clean
        if clean.endswith(".html"):
            clean = clean[:-5]
        changes.append(f"canonical: '{href}' → '{clean}'")
        return m.group(0).replace(f'"{href}"', f'"{clean}"').replace(f"'{href}'", f"'{clean}'")

    new = re.sub(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\'][^>]*/?>',
                 replacer, content)
    new = re.sub(r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\'][^>]*/?>',
                 replacer, new)
    return new, changes

def fix_og_url(content, expected_url):
    changes = []
    m = re.search(r'property=["\']og:url["\'][^>]+content=["\']([^"\']*)["\']', content)
    m2 = re.search(r'content=["\']([^"\']*)["\'][^>]+property=["\']og:url["\']', content)
    found = m or m2
    if found:
        val = found.group(1)
        if val != expected_url:
            clean = val
            if clean.startswith("/"): clean = BASE + clean
            if clean.endswith(".html"): clean = clean[:-5]
            content = content.replace(f'"{val}"', f'"{clean}"', 1)
            changes.append(f"og:url: '{val}' → '{clean}'")
    else:
        # inject after og:description
        m3 = re.search(r'(<meta[^>]+property=["\']og:description["\'][^>]*/?>)', content)
        if m3:
            ins = f'\n  <meta property="og:url" content="{expected_url}" />'
            content = content.replace(m3.group(1), m3.group(1) + ins, 1)
            changes.append(f"og:url added: '{expected_url}'")
    return content, changes

def inject_faqs(content, slug):
    if slug not in FAQS:
        return content, []
    faq_data = FAQS[slug]
    changes = []

    # Build the JS array string — [question, answer] format
    rows = []
    for q, a in faq_data:
        q_esc = q.replace("'", "\\'")
        a_esc = a.replace("'", "\\'")
        rows.append(f"  ['{q_esc}', '{a_esc}']")
    new_array = "const faqs = [\n" + ",\n".join(rows) + "\n];"

    if "const faqs" in content:
        # Replace existing array (handles both empty and filled)
        old = re.search(r'const faqs\s*=\s*\[.*?\];', content, re.DOTALL)
        if old:
            content = content[:old.start()] + new_array + content[old.end():]
            changes.append(f"FAQs updated ({len(faq_data)} entries)")
    else:
        changes.append(f"No faqs array found — skipping {slug}")
        return content, changes

    # Check renderer exists (uses faq-container + f[0]/f[1] pattern)
    has_renderer = "faq-container" in content and ("f[0]" in content or "f[1]" in content)
    if not has_renderer and "faq-container" in content:
        # Inject renderer after the array
        renderer = (
            "\ndocument.getElementById('faq-container').innerHTML = faqs.map(function(f, i) {"
            "\n  return '<div class=\"faq-item\" id=\"faq-' + i + '\">"
            "<div class=\"faq-q\" onclick=\"toggleFaqItem(' + i + ')\" tabindex=\"0\">' + f[0] + '</div>"
            "<div class=\"faq-a\">' + f[1] + '</div></div>';"
            "\n}).join('');"
            "\nfunction toggleFaqItem(i) {"
            "\n  var item = document.getElementById('faq-' + i);"
            "\n  var wasOpen = item.classList.contains('open');"
            "\n  document.querySelectorAll('.faq-item').forEach(function(e) { e.classList.remove('open'); });"
            "\n  if (!wasOpen) item.classList.add('open');"
            "\n}"
        )
        content = content.replace(new_array, new_array + renderer)
        changes.append("FAQ renderer injected")

    return content, changes

def inject_info(content, slug):
    if slug not in INFO or "info-section" in content:
        return content, []
    title, paras = INFO[slug]
    paras_html = "\n".join(f"    <p>{p}</p>" for p in paras)
    section = f"""
  <section class="info-section" id="about-{slug}">
    <h2>{title}</h2>
{paras_html}
  </section>"""
    # Add CSS
    if "info-section {" not in content and "</style>" in content:
        content = content.replace("</style>", INFO_CSS + "\n  </style>", 1)
    # Insert before </main> or before </body>
    if "</main>" in content:
        content = content.replace("</main>", section + "\n</main>", 1)
    elif "</body>" in content:
        content = content.replace("</body>", section + "\n</body>", 1)
    return content, [f"info-section added"]

def main():
    repo = Path.cwd()
    total_modified = 0

    dirs = ["medical-calculators", "drug-doses", "vitamin", "rabies-scheduler"]
    all_files = []
    for d in dirs:
        dd = repo / d
        if dd.exists():
            all_files += sorted(dd.rglob("*.html"))

    for html_file in all_files:
        rel = str(html_file.relative_to(repo))
        slug = html_file.stem
        expected_url = path_to_url(rel)

        original = html_file.read_text(encoding="utf-8", errors="ignore")
        content = original
        all_changes = []

        # 1. Canonical
        content, c = fix_canonical(content, expected_url)
        all_changes += c

        # 2. og:url
        content, c = fix_og_url(content, expected_url)
        all_changes += c

        # 3. FAQs
        content, c = inject_faqs(content, slug)
        all_changes += c

        # 4. Info section
        content, c = inject_info(content, slug)
        all_changes += c

        # 5. Tool count
        for old in ["17+ clinical tools", "20+ clinical tools", "27+ calculators"]:
            if old in content:
                content = content.replace(old, "32+ clinical tools")
                all_changes.append(f"'{old}' → '32+ clinical tools'")

        if content != original:
            shutil.copy2(html_file, str(html_file) + ".bak")
            html_file.write_text(content, encoding="utf-8")
            total_modified += 1
            print(f"  ✏️  {rel}")
            for c in all_changes:
                print(f"     {c}")

    print(f"\n{'='*60}")
    print(f"Modified: {total_modified} files")
    print("Review changes then: git add -A && git commit -m 'fix: canonicals, FAQs, info-sections' && git push")

if __name__ == "__main__":
    main()

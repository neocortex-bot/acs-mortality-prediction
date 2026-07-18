# README — Validation of TESIS_FINAL.docx Numbers

## Overview

This guide helps Claude Opus independently verify ALL numbers in `TESIS_FINAL.docx` against the actual data in `thesis_complete_db.parquet`. The thesis (Dr Izzan, UNHAS S3 Kardiologi) develops a Random Forest model for predicting in-hospital mortality in ACS patients.

## Working Directory

All files are at: **`/tmp/thesis-v3-latest-check/`**

### Files
| File | Description |
|------|-------------|
| `TESIS_FINAL.docx` | The thesis document to verify |
| `thesis_complete_db.parquet` | Source data (ground truth) |
| `results_final.json` | Pre-computed ground truth results |
| `docx_verification_report.md` | Comprehensive paragraph-by-paragraph report of all number errors |
| `validate_thesis.ipynb` | Jupyter notebook to reproduce all results |
| `reanalysis.py` | Reference script (same logic as notebook) |
| `run_fast.py` | Speed-optimized reference script |
| `figures/` | Contains all figure PNGs (Fig1-Fig10) |

## Data Filters

Load the parquet and apply these STRICT filters:

```python
import pandas as pd
df = pd.read_parquet('/tmp/thesis-v3-latest-check/thesis_complete_db.parquet')
mask = (df['pat_exclude'] == False) & (df['killip'] != 4)
data = df[mask].copy()
```

### Expected After Filtering

| Metric | Expected Value |
|--------|---------------|
| Total patients | **1,524** |
| Deaths (inhospital_death=1) | **115** |
| Prevalence | **7.5%** |
| STEMI | **1,047 (68.7%)** |
| NSTEMI | **477 (31.3%)** |
| STEMI deaths | **72 (6.9%)** |
| NSTEMI deaths | **43 (9.0%)** |
| Killip I | **968** (alive=927, dead=41) |
| Killip II | **411** (alive=374, dead=37) |
| Killip III | **145** (alive=108, dead=37) |

## Model Configuration

### Random Forest Hyperparameters
- `n_estimators=500`
- `max_depth=6`
- `min_samples_leaf=10`
- `class_weight='balanced_subsample'`
- `random_state=42`
- `n_jobs=-1`

### Validation Strategy
- **5-fold stratified cross-validation**
- **10 random seeds** (42, 43, 44, 45, 46, 47, 48, 49, 50, 51)
- Use **raw out-of-fold predictions** (NO Platt scaling)
- Impute missing values with **median**
- **StandardScaler** for feature scaling

### 13 Features (in order of importance)
```
ureum_igd, egfr_igd, age_when_admission, lvot_vti_igd, hb_igd,
lvef, hr, kalium_igd, rr, aptt_value, sbp, killip, tapse_value
```

## Expected Metrics (Ground Truth from results_final.json)

### Primary Metrics
| Metric | Expected Value | Acceptable Range |
|--------|---------------|-----------------|
| AUC (mean) | **0.818** | 0.814 – 0.824 |
| AUC (std) | **0.003** | 0.002 – 0.005 |
| AUPRC | **0.316** | 0.310 – 0.325 |
| Brier Score | **0.098** | 0.095 – 0.102 |
| 95% CI (from 10 seeds) | **0.812 – 0.824** | — |

### Safety Threshold (0.069)
| Metric | Expected Value |
|--------|---------------|
| Sensitivity | **98.3%** (113/115) |
| Specificity | **19.7%** (277/1,409) |
| PPV | **9.1%** |
| NPV | **99.3%** |
| False Negatives (missed deaths) | **2** |
| False Positives | **1,132** |
| True Positives | **113** |
| True Negatives | **277** |

### Youden Threshold (0.279)
| Metric | Expected Value |
|--------|---------------|
| Sensitivity | **80.9%** (93/115) |
| Specificity | **70.6%** (995/1,409) |
| PPV | **18.3%** |
| NPV | **97.8%** |
| False Negatives | **22** |
| False Positives | **414** |
| True Positives | **93** |
| True Negatives | **995** |

### Triage System (3-tier)
| Tier | Threshold | n | Deaths | Mortality Rate |
|------|-----------|---|--------|---------------|
| Ward | < 0.069 | **279** | **2** | **0.7%** |
| HCU | 0.069 – 0.279 | **738** | **20** | **2.7%** |
| ICU | ≥ 0.279 | **507** | **93** | **18.3%** |

### Feature Importance (Gini)
| Feature | Importance |
|---------|-----------|
| ureum_igd | 0.141 |
| egfr_igd | 0.140 |
| age_when_admission | 0.116 |
| lvot_vti_igd | 0.094 |
| hb_igd | 0.075 |
| lvef | 0.073 |
| hr | 0.070 |
| rr | 0.061 |
| kalium_igd | 0.061 |
| aptt_value | 0.055 |
| sbp | 0.049 |
| killip | 0.042 |
| tapse_value | 0.024 |

### Ablation (ΔAUC when feature removed)
| Removed Feature | ΔAUC |
|----------------|------|
| age_when_admission | +0.010 (better without!) |
| kalium_igd | +0.007 |
| aptt_value | +0.006 |
| egfr_igd | +0.006 |
| hb_igd | -0.005 |
| ureum_igd | -0.005 |
| lvef | -0.004 |
| killip | -0.002 |
| lvot_vti_igd | -0.002 |
| tapse_value | -0.002 |
| hr | +0.002 |
| rr | -0.001 |
| sbp | +0.001 |

### XGBoost Comparison
| Metric | Random Forest | XGBoost |
|--------|--------------|---------|
| AUC | **0.818** | **0.789** |
| AUPRC | **0.316** | **0.301** |
| Brier | **0.098** | **0.104** |
| Sens (safety) | **98.3%** | **94.5%** |
| Spec (safety) | **19.7%** | **15.2%** |

## Key Columns in Parquet

| Column | Description |
|--------|-------------|
| `inhospital_death` | Outcome (0/1) |
| `diagnosis_acs` | 'STEMI' or 'NSTEMI' |
| `pat_exclude` | Boolean exclusion flag |
| `killip` | Killip class (1,2,3,4) |
| `age_when_admission` | Age in years |
| `ureum_igd` | Ureum (mg/dL) |
| `egfr_igd` | eGFR (mL/min/1.73m²) |
| `hr` | Heart rate (bpm) |
| `hb_igd` | Hemoglobin (g/dL) |
| `sbp` | Systolic BP (mmHg) |
| `rr` | Respiratory rate (/min) |
| `lvef` | LVEF (%) |
| `lvot_vti_igd` | LVOT VTI (cm) |
| `tapse_value` | TAPSE (mm) |
| `kalium_igd` | Potassium (mEq/L) |
| `aptt_value` | APTT (sec) |

## How to Run the Notebook

```bash
cd /tmp/thesis-v3-latest-check
jupyter nbconvert --to notebook --execute validate_thesis.ipynb --output validate_thesis_executed.ipynb
```

Or open interactively:
```bash
cd /tmp/thesis-v3-latest-check
jupyter notebook validate_thesis.ipynb
```

The notebook will:
1. Load and filter the parquet data
2. Train the RF model with 10 seeds × 5-fold CV
3. Compute all metrics
4. Generate all figures (saved to `figures/`)
5. Output `validation_results.json`
6. Print a PASS/FAIL comparison against expected DOCX values

## What to Check in the DOCX

### Critical Errors to Fix
1. **P6 (English abstract)** — Completely wrong numbers from old model (N=1572, AUC=0.812, safety thr=0.041, etc.)
2. **P144 + Table 2** — STEMI/NSTEMI breakdown uses old data (STEMI 8.5% → should be 6.9%; NSTEMI 5.4% → should be 9.0%)
3. **P170** — Claims "Platt scaling" but model uses raw OOF predictions
4. **P159** — Specificity 74.5% (should be 70.6%), PPV 18.5% (should be 18.3%)

### Major Issues
5. **P223** — MEWS AUC listed as 0.316 (should be 0.690)
6. **P320, P324, P327, P350** — DOIs have "10,069" corruption
7. **Table 1 Row 2** — Male gender shows 0 (0.0%) — data missing
8. **P139** — Date range "Jan 2024–Dec 2025" is a future placeholder
9. **Date ranges** — Inconsistent across P61 (2020-2022), P2 (2021-2024), P139 (2024-2025)

### Minor Issues
10. Mixed decimal separators (. vs ,) throughout the document
11. P262 — Composite AUC "0.750" vs Table 5 "0.742"

## Fixing the DOCX

Use the `python-docx` library to programmatically fix errors:

```python
from docx import Document
doc = Document('TESIS_FINAL.docx')

# Access paragraphs by index
p = doc.paragraphs[INDEX]
# Replace text
for run in p.runs:
    if 'old_text' in run.text:
        run.text = run.text.replace('old_text', 'new_text')

# Access tables
table = doc.tables[TABLE_INDEX]
cell = table.rows[ROW].cells[COL]
# Clear and set text
for run in cell.paragraphs[0].runs:
    run.text = ''
cell.paragraphs[0].runs[0].text = 'new_value'

doc.save('TESIS_FINAL_FIXED.docx')
```

For the notebook, also note:
- The `diagnosis_acs` column has values 'STEMI' and 'NSTEMI' (exact case)
- The `jenis_kelamin` column has values 'L' (Male) and 'P' (Female)
- No column named 'gender' — Table 1 likely maps `jenis_kelamin` to 'Male gender'

## Verification Checklist

- [ ] N=1,524 after filtering (not 1,572, not 1,076+496)
- [ ] Deaths=115 (not 118, not 91+27)
- [ ] Prevalence=7.5%
- [ ] STEMI=1,047 (68.7%), deaths=72 (6.9%)
- [ ] NSTEMI=477 (31.3%), deaths=43 (9.0%)
- [ ] AUC=0.818 ± 0.003 (not 0.812, not 0.784)
- [ ] Safety thr=0.069 → Sens=98.3%, Spec=19.7%, NPV=99.3%, PPV=9.1%
- [ ] Youden thr=0.279 → Sens=80.9%, Spec=70.6%, NPV=97.8%, PPV=18.3%
- [ ] Triage: Ward n=279 (0.7%), HCU n=738 (2.7%), ICU n=507 (18.3%)
- [ ] Top 3 features: ureum (0.141), eGFR (0.140), age (0.116)
- [ ] XGB AUC=0.789, Brier=0.104
- [ ] All DOIs use "." not "," 
- [ ] Consistent date range throughout document
- [ ] Decimal separators consistent within each section

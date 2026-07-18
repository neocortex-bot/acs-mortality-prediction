# ACS Mortality Prediction — Makassar ACS Registry

**Random Forest model for in-hospital mortality prediction in STEMI/NSTEMI patients**

Dr Izzan | S3 Kardiologi UNHAS | 2026

---

## Repository Structure

```
thesis-clean/
├── thesis_main.py           # Canonical analysis script (self-documenting)
├── thesis_main.ipynb        # Jupyter notebook version (Kaggle-quality)
├── thesis_complete_db.parquet  # Single source of truth (1,524 patients)
├── TESIS_FINAL.docx          # Verified thesis document
├── validation_results.json  # Machine-readable metrics (for CI/CD)
├── DEFENSE_ANSWERS.md       # Thesis defense Q&A document
├── docx_verification_report.md  # Paragraph-level audit trail
├── README.md                # This file
├── .gitignore
├── requirements.txt
└── figures/
    ├── roc_curve.png
    ├── feature_importance.png
    ├── confusion_matrices.png
    ├── triage_system.png
    ├── calibration.png
    ├── pr_curve.png
    ├── ablation.png
    ├── probability_distribution.png
    ├── diagnosis_breakdown.png
    └── killip_mortality.png
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run analysis
python3 thesis_main.py

# Or in Jupyter
jupyter notebook thesis_main.ipynb
```

Output: `validation_results.json` + 10 figures in `figures/`

## Data Source

| Source | Makassar ACS Registry, PJT RSUP Dr. Wahidin Sudirohusodo |
|--------|----------------------------------------------------------|
| Period | January 2024 – December 2025 |
| Format | Apache Parquet (`thesis_complete_db.parquet`) |
| Filter | `pat_exclude=False` + `killip != 4` |
| Final N | **1,524** patients (STEMI=1,047, NSTEMI=477) |
| Events | **115** in-hospital deaths (7.5%) |

## Model Summary

```ascii
Algorithm   : Random Forest (500 trees, max_depth=6, min_samples_leaf=5)
Validation  : 5-fold stratified CV × 10 random seeds (42–51)
Features    : 13 (age, ureum, eGFR, HR, Hb, Killip, SBP, RR, LVEF, LVOT VTI, TAPSE, K+, APTT)

AUC         : 0.818 ± 0.003
AUPRC       : 0.316  (4.2× baseline prevalence)
Brier       : 0.098

Safety thr  : 0.069 → Sens=98.3%, Spec=19.7%, NPV=99.3%, FN=2
Youden thr  : 0.279 → Sens=80.9%, Spec=70.6%, PPV=18.3%, FN=22
```

## Triage System (3-tier)

| Tier | Threshold | n | Deaths | Rate | Decision |
|:-----|:----------|:--|:-------|:-----|:---------|
| 🟢 Ward | < 0.069 | 279 | 2 | 0.7% | Floor admission, routine monitoring |
| 🟡 HCU | 0.069–0.279 | 738 | 20 | 2.7% | Intermediate care, close monitoring |
| 🔴 ICU | ≥ 0.279 | 507 | 93 | 18.3% | Intensive care, aggressive management |

**Risk gradient: 26× from Ward to ICU**

## Key Files

| File | Description |
|:-----|:------------|
| `thesis_main.py` | Canonical analysis; run this to reproduce all numbers |
| `TESIS_FINAL.docx` | Thesis document with ALL numbers verified against parquet |
| `validation_results.json` | All metrics in machine-readable JSON |
| `DEFENSE_ANSWERS.md` | 300+ lines of defense Q&A (rationale for 19.7% specificity, HCU buffer, etc.) |
| `docx_verification_report.md` | Paragraph-by-paragraph audit trail showing every number checked |

## Reproducibility Guarantee

Every number in this repository is traceable to a single command:

```bash
python3 thesis_main.py
```

This trains the model from scratch using 5-fold CV × 10 seeds, computes all metrics,
generates all figures, and saves `validation_results.json`. No pre-computed cache,
no stale CSV, no hidden state.

## Dependencies

- Python 3.10+
- pandas, numpy, scipy
- scikit-learn
- matplotlib, seaborn
- python-docx (for DOCX verification only)
- xgboost (optional, for comparison)

#!/usr/bin/env python3
"""Generate the seminar notebook from the canonical pipeline outputs."""
import nbformat as nbf

nb = nbf.v4.new_notebook()
nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
               "language_info": {"name": "python"}}
c = []
def md(text): c.append(nbf.v4.new_markdown_cell(text))
def code(text): c.append(nbf.v4.new_code_cell(text))

md("""# ACS in-hospital mortality prediction

This notebook evaluates a 13-feature Random Forest in 1,524 patients with acute coronary syndrome. The primary validation uses five stratified folds repeated with ten fixed seeds. All preprocessing is estimated within each training fold.

The patient-level mean of the ten out-of-fold predictions is used only for threshold selection and the paired GRACE 2.0 comparison. Seed-level AUC variation is retained for uncertainty reporting.

## TRIPOD+AI reporting checklist

| Item | Implementation |
|---|---|
| Population and outcome | ACS, Killip I to III, in-hospital mortality |
| Sample size | 1,524 patients, 115 deaths |
| Predictors | 13 admission variables specified before analysis |
| Missing data | Training-fold median imputation |
| Internal validation | Five folds repeated over ten fixed seeds |
| Performance | AUC, 95% CI, range, AUPRC, Brier score, threshold metrics |
| Comparator | Patient-level GRACE 2.0 score from eight source variables |
| Model interpretation | Mean Gini importance over all 50 validation models |
| Reproducibility | Versions, seeds, filters, and schema reported below |""")

md("""## 1. Execute the canonical analysis

The standalone pipeline is the single source of numerical results. Running it here prevents notebook outputs from drifting away from the script, figures, or thesis tables.""")
code("""import subprocess, sys
run = subprocess.run([sys.executable, "thesis_main.py"], check=True, text=True, capture_output=True)
print(run.stdout)""")
md("""The execution log reports one AUC for each prespecified seed. Its final lines report the seed-level summary, exact thresholds, paired GRACE comparison, and mutually exclusive triage counts.""")

md("""## 2. Load the synchronized results

The JSON artifact contains full-precision values. Display rounding is applied only when results are presented.""")
code("""import json
from pathlib import Path
r = json.loads(Path("validation_results.json").read_text())
d, m, t, g = r["dataset"], r["metrics"], r["thresholds"], r["grace"]
print(f'N={d["n"]:,}; deaths={d["deaths"]} ({d["prevalence"]:.1%})')
print(f'Seed AUC={m["auc_mean"]:.4f} ± {m["auc_sd"]:.4f}; 95% CI {m["auc_ci95"][0]:.4f} to {m["auc_ci95"][1]:.4f}')
print(f'Range={m["auc_min"]:.4f} to {m["auc_max"]:.4f}; mean-OOF AUC={m["ensemble_auc"]:.4f}')
print(f'Brier={m["brier_mean"]:.4f}; AUPRC={m["auprc_mean"]:.4f}')""")
md("""The mean seed AUC quantifies performance across repeated partitions. The mean-OOF AUC is slightly higher because averaging ten patient-level predictions reduces prediction noise. The Brier score and AUPRC replace the stale values previously shown in this notebook.""")

md("""## 3. Baseline characteristics

Continuous variables use Welch's t-test. Binary rows use a 2 by 2 chi-square or Fisher exact test. The separate Killip helper uses the full 2 by 3 table, so Killip classes I, II, and III are retained in the multicategory test.""")
code("""import pandas as pd
baseline = pd.DataFrame(r["baseline"])
baseline["p"] = baseline["p"].map(lambda x: f"{x:.4f}")
display(baseline)
print(f'Killip I to III multicategory p={r["killip_multicategory_p"]:.6g}')""")
md("""Deaths were associated with an older and physiologically higher-risk profile across several admission variables. The binary Killip III row remains suitable for the clinical baseline table, while the full multicategory test evaluates the complete Killip distribution.""")

md("""## 4. Threshold selection and clinical triage

The safety threshold is the largest observed cutoff that permits no more than two false negatives among 115 deaths. The Youden threshold maximizes sensitivity plus specificity minus one. Both thresholds are derived from the patient-level mean OOF vector.""")
code("""s, y = t["safety_metrics"], t["youden_metrics"]
print(f'Safety threshold={t["safety"]:.6f}: sensitivity={s["sensitivity"]:.1%}, specificity={s["specificity"]:.1%}, FN={s["fn"]}, FP={s["fp"]}')
print(f'Youden threshold={t["youden"]:.6f}: sensitivity={y["sensitivity"]:.1%}, specificity={y["specificity"]:.1%}, FN={y["fn"]}, FP={y["fp"]}')
triage = pd.DataFrame(t["triage"]).T
triage["mortality"] = triage["rate"].map(lambda x: f"{x:.1%}")
display(triage[["n", "death", "mortality"]])""")
md("""The safety rule assigns 371 patients to Ward and misses two deaths. The Youden cutoff separates 336 ICU patients with 24.4% observed mortality. These are validation-derived decision rules and require external assessment before clinical deployment.""")

md("""## 5. GRACE 2.0 comparison

GRACE points are calculated from age, heart rate, systolic pressure, creatinine, Killip class, arrest at admission, elevated troponin, and ST deviation. Arrest is mapped to `rosc_in_igd`, elevated enzymes to troponin above 0.04 ng/mL, and ST deviation to `ekg_ste`. Six missing creatinine values use the cohort median for this fixed-score comparator.""")
code("""q = g["threshold_20pct"]
comparison = pd.DataFrame({"Random Forest": q["rf"], "GRACE 2.0": q["grace"]})
display(comparison.loc[["sensitivity", "specificity", "ppv", "npv", "tn", "fp", "fn", "tp"]])
print(f'RF mean-OOF AUC={g["rf_auc"]:.4f}; GRACE AUC={g["auc"]:.4f}; delta={g["auc_delta"]:.4f}')
print(f'Bootstrap delta 95% CI={g["auc_delta_ci95"][0]:.4f} to {g["auc_delta_ci95"][1]:.4f}; p={g["auc_p_bootstrap"]:.4g}')
print(f'GRACE 20% risk begins at score {q["grace_score_min"]}; McNemar p={q["mcnemar_p"]:.4g}')""")
md("""The Random Forest mean-OOF vector discriminates mortality better than the reconstructed GRACE score in this cohort. At a 20% predicted-risk cutoff, the paired McNemar test evaluates whether patient-level classification errors differ between methods.""")

md("""## 6. Cross-validated feature importance

Importance is aggregated over the same 50 fitted fold models used for validation. No full-cohort refit contributes to this table.""")
code("""importance = pd.DataFrame(r["feature_importance"]).T.reset_index(names="feature")
display(importance.style.format({"mean": "{:.4f}", "sd": "{:.4f}"}))""")
md("""Renal function and age have the largest mean impurity reductions. Gini importance ranks model usage rather than causal effect, and correlated predictors can share importance.""")

md("""## 7. Reproducibility record

The following cell prints package versions, exact split seeds, cohort filter, and feature schema. The parquet file is read-only throughout the workflow.""")
code("""print('Versions:', r["versions"])
print('Seeds:', r["seeds"])
print('Cohort filter:', r["dataset"]["filter"])
print('Feature schema:', r["features"])
print('Threshold method:', r["thresholds"]["method"])""")
md("""The recorded environment and fixed seeds support exact reruns in the current repository. The schema lists all model inputs and distinguishes the modeling features from the separate GRACE variables.""")

md("""## 8. Final synchronized metrics

This compact table is the reference for the thesis narrative and validation script.""")
code("""summary = pd.DataFrame([
    ["Patients", d["n"]], ["Deaths", d["deaths"]],
    ["Mean seed AUC", f'{m["auc_mean"]:.4f}'], ["Mean-OOF AUC", f'{m["ensemble_auc"]:.4f}'],
    ["Brier", f'{m["brier_mean"]:.4f}'], ["AUPRC", f'{m["auprc_mean"]:.4f}'],
    ["Safety threshold", f'{t["safety"]:.6f}'], ["Youden threshold", f'{t["youden"]:.6f}'],
    ["GRACE AUC", f'{g["auc"]:.4f}'], ["McNemar p", f'{g["threshold_20pct"]["mcnemar_p"]:.4g}']])
display(summary.rename(columns={0: "Metric", 1: "Value"}))""")
md("""All values in this summary are generated from the corrected pipeline. The thesis headline can state an OOF AUC of approximately 0.818, while the methods and results must also report the seed-level mean, uncertainty interval, and range shown above.""")

nb.cells = c
nbf.write(nb, "gm-acs-mortality-prediction.ipynb")
print(f"Wrote {len(c)} cells")

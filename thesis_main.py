#!/usr/bin/env python3
"""Canonical, leakage-safe analysis for ACS in-hospital mortality thesis."""
from __future__ import annotations

import json
import os
import platform
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
from scipy import stats
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (auc, brier_score_loss, confusion_matrix,
                             precision_recall_curve, roc_auc_score, roc_curve)
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent
PARQUET_PATH = ROOT / "thesis_complete_db.parquet"
FIGURE_DIR = ROOT / "figures"
RESULTS_PATH = ROOT / "validation_results.json"
OOF_PATH = ROOT / "rf_probs.npy"
SEEDS = [42, 123, 456, 789, 111, 222, 333, 444, 555, 666]
N_FOLDS = 5
FEATURES = [
    "age_when_admission", "ureum_igd", "egfr_igd", "hr", "hb_igd",
    "killip", "sbp", "rr", "lvef", "lvot_vti_igd", "tapse_value",
    "kalium_igd", "aptt_value",
]
RF_PARAMS = dict(n_estimators=500, max_depth=6, min_samples_leaf=5, n_jobs=-1)
FIGURE_DIR.mkdir(exist_ok=True)


def chi_square_by_outcome(series: pd.Series, outcome: np.ndarray) -> float:
    """Pearson chi-square for any number of observed categories."""
    table = pd.crosstab(pd.Series(outcome, index=series.index, name="outcome"),
                        series.rename("category"), dropna=True)
    if table.shape[0] < 2 or table.shape[1] < 2:
        return float("nan")
    return float(stats.chi2_contingency(table)[1])


def binary_test(series: pd.Series, outcome: np.ndarray, positive) -> float:
    exposed = series.eq(positive)
    table = pd.crosstab(pd.Series(outcome, index=series.index), exposed)
    table = table.reindex(index=[0, 1], columns=[False, True], fill_value=0)
    if (table.values < 5).any():
        return float(stats.fisher_exact(table.values)[1])
    return float(stats.chi2_contingency(table.values)[1])


def classification_metrics(y: np.ndarray, pred: np.ndarray) -> dict:
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
        "sensitivity": float(tp / (tp + fn)),
        "specificity": float(tn / (tn + fp)),
        "ppv": float(tp / (tp + fp)) if tp + fp else 0.0,
        "npv": float(tn / (tn + fn)) if tn + fn else 0.0,
    }


def grace_points(row: pd.Series, creatinine_median: float) -> int:
    """Published GRACE point chart for in-hospital mortality."""
    age = row.age_when_admission
    hr = row.hr
    sbp = row.sbp
    cr = row.kreatinin_igd if pd.notna(row.kreatinin_igd) else creatinine_median
    killip = int(row.killip)
    p = (0 if age < 40 else 18 if age < 50 else 36 if age < 60 else
         55 if age < 70 else 73 if age < 80 else 91)
    p += (0 if hr < 50 else 3 if hr < 70 else 9 if hr < 90 else
          15 if hr < 110 else 24 if hr < 150 else 38 if hr < 200 else 46)
    p += (58 if sbp < 80 else 53 if sbp < 100 else 43 if sbp < 120 else
          34 if sbp < 140 else 24 if sbp < 160 else 10 if sbp < 200 else 0)
    cr_umol = cr * 88.4
    p += 1 if cr_umol < 35 else 4 if cr_umol < 71 else 7 if cr_umol < 106 else 10 if cr_umol < 177 else 15
    p += {1: 0, 2: 20, 3: 43, 4: 59}[killip]
    p += 39 if bool(row.rosc_in_igd) else 0
    p += 28 if bool(row.ekg_ste) else 0
    p += 14 if pd.notna(row.troponin_igd) and row.troponin_igd > 0.04 else 0
    return int(p)


def grace_probability(score: np.ndarray) -> np.ndarray:
    """GRACE in-hospital point score converted to predicted mortality risk."""
    return 1.0 - np.exp(-np.exp(-10.1507 + 0.0531 * score))


def paired_auc_bootstrap(y, rf, grace, n_boot=2000, seed=42):
    rng = np.random.default_rng(seed)
    deltas = []
    n = len(y)
    while len(deltas) < n_boot:
        idx = rng.integers(0, n, n)
        if np.unique(y[idx]).size == 2:
            deltas.append(roc_auc_score(y[idx], rf[idx]) - roc_auc_score(y[idx], grace[idx]))
    d = np.asarray(deltas)
    p = 2 * min((d <= 0).mean(), (d >= 0).mean())
    return float(np.quantile(d, .025)), float(np.quantile(d, .975)), float(max(p, 1 / n_boot))


def main():
    df = pd.read_parquet(PARQUET_PATH)
    data = df[(df["pat_exclude"] == False) & (df["killip"] != 4)].copy()  # noqa: E712
    y = data["inhospital_death"].astype(int).to_numpy()
    X = data[FEATURES].copy()
    n, deaths = len(y), int(y.sum())
    print(f"Cohort: N={n}, deaths={deaths} ({y.mean():.1%})")

    baseline_spec = {
        "Age (years)": ("age_when_admission", "continuous", None),
        "Male gender": ("jenis_kelamin", "binary", "L"),
        "STEMI": ("diagnosis_acs", "binary", "STEMI"),
        "Heart rate (bpm)": ("hr", "continuous", None),
        "SBP (mmHg)": ("sbp", "continuous", None),
        "RR (/min)": ("rr", "continuous", None),
        "Killip III": ("killip", "binary", 3),
        "Hemoglobin (g/dL)": ("hb_igd", "continuous", None),
        "Ureum (mg/dL)": ("ureum_igd", "continuous", None),
        "eGFR (mL/min/1.73m2)": ("egfr_igd", "continuous", None),
        "Potassium (mEq/L)": ("kalium_igd", "continuous", None),
        "APTT (sec)": ("aptt_value", "continuous", None),
        "GDS (mg/dL)": ("gds_igd", "continuous", None),
        "LVEF (%)": ("lvef", "continuous", None),
        "LVOT VTI (cm)": ("lvot_vti_igd", "continuous", None),
        "TAPSE (mm)": ("tapse_value", "continuous", None),
    }
    baseline = []
    alive, died = data[y == 0], data[y == 1]
    for label, (col, kind, positive) in baseline_spec.items():
        if kind == "continuous":
            p = stats.ttest_ind(alive[col].dropna(), died[col].dropna(), equal_var=False).pvalue
            a = f"{alive[col].mean():.1f} ± {alive[col].std():.1f}"
            d = f"{died[col].mean():.1f} ± {died[col].std():.1f}"
        else:
            an, dn = int(alive[col].eq(positive).sum()), int(died[col].eq(positive).sum())
            a, d = f"{an} ({an/len(alive)*100:.1f}%)", f"{dn} ({dn/len(died)*100:.1f}%)"
            p = binary_test(data[col], y, positive)
        baseline.append({"variable": label, "alive": a, "death": d, "p": float(p)})
    killip_multicategory_p = chi_square_by_outcome(data["killip"], y)

    all_oof = np.zeros((len(SEEDS), n))
    seed_metrics, fold_importances = [], []
    for si, seed in enumerate(SEEDS):
        skf = StratifiedKFold(N_FOLDS, shuffle=True, random_state=seed)
        oof = np.zeros(n)
        for fold, (tr, te) in enumerate(skf.split(X, y), 1):
            model = Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("rf", RandomForestClassifier(**RF_PARAMS, random_state=seed)),
            ])
            model.fit(X.iloc[tr], y[tr])
            oof[te] = model.predict_proba(X.iloc[te])[:, 1]
            fold_importances.append(model.named_steps["rf"].feature_importances_)
        all_oof[si] = oof
        precision, recall, _ = precision_recall_curve(y, oof)
        seed_metrics.append({"seed": seed, "auc": roc_auc_score(y, oof),
                             "brier": brier_score_loss(y, oof),
                             "auprc": auc(recall, precision)})
        print(f"Seed {seed}: AUC={seed_metrics[-1]['auc']:.4f}")

    probs = all_oof.mean(axis=0)
    np.save(OOF_PATH, probs)
    aucs = np.array([m["auc"] for m in seed_metrics])
    auc_mean, auc_sd = aucs.mean(), aucs.std(ddof=1)
    ci = (auc_mean - 1.96 * auc_sd / np.sqrt(len(SEEDS)), auc_mean + 1.96 * auc_sd / np.sqrt(len(SEEDS)))
    brier = float(np.mean([m["brier"] for m in seed_metrics]))
    auprc = float(np.mean([m["auprc"] for m in seed_metrics]))

    death_probs = np.sort(probs[y == 1])
    safety_thr = float(death_probs[2])  # maximum observed cutoff with at most two FN
    fpr, tpr, roc_thresholds = roc_curve(y, probs)
    youden_thr = float(roc_thresholds[np.argmax(tpr - fpr)])
    safety = classification_metrics(y, probs >= safety_thr)
    youden = classification_metrics(y, probs >= youden_thr)
    tiers = {}
    for name, mask in {
        "Ward": probs < safety_thr,
        "HCU": (probs >= safety_thr) & (probs < youden_thr),
        "ICU": probs >= youden_thr,
    }.items():
        tiers[name] = {"n": int(mask.sum()), "death": int(y[mask].sum()),
                       "rate": float(y[mask].mean()) if mask.any() else 0.0}

    creatinine_median = float(data["kreatinin_igd"].median())
    grace_score = data.apply(grace_points, axis=1, creatinine_median=creatinine_median).to_numpy()
    grace_prob = grace_probability(grace_score)
    grace_auc = float(roc_auc_score(y, grace_score))
    rf_auc_ensemble = float(roc_auc_score(y, probs))
    grace_20 = classification_metrics(y, grace_prob >= .20)
    rf_20 = classification_metrics(y, probs >= .20)
    rf_correct = (probs >= .20) == y
    grace_correct = (grace_prob >= .20) == y
    discord_rf = int((rf_correct & ~grace_correct).sum())
    discord_grace = int((~rf_correct & grace_correct).sum())
    mcnemar = stats.binomtest(discord_rf, discord_rf + discord_grace, .5).pvalue if discord_rf + discord_grace else 1.0
    delta_lo, delta_hi, auc_p = paired_auc_bootstrap(y, probs, grace_score)

    fi_arr = np.asarray(fold_importances)
    fi = {FEATURES[i]: {"mean": float(fi_arr[:, i].mean()), "sd": float(fi_arr[:, i].std(ddof=1))}
          for i in np.argsort(fi_arr.mean(axis=0))[::-1]}

    results = {
        "schema_version": 2,
        "dataset": {"file": PARQUET_PATH.name, "filter": "pat_exclude=False and Killip I-III",
                    "n": n, "deaths": deaths, "prevalence": float(y.mean())},
        "seeds": SEEDS, "folds": N_FOLDS, "features": FEATURES,
        "metrics": {"auc_mean": float(auc_mean), "auc_sd": float(auc_sd),
                    "auc_ci95": [float(ci[0]), float(ci[1])], "auc_min": float(aucs.min()),
                    "auc_max": float(aucs.max()), "ensemble_auc": rf_auc_ensemble,
                    "brier_mean": brier, "auprc_mean": auprc, "by_seed": seed_metrics},
        "thresholds": {"method": "Thresholds derived from the patient-level mean of 10 repeated OOF predictions. Safety is the maximum observed cutoff yielding FN <= 2; Youden maximizes sensitivity + specificity - 1.",
                       "safety": safety_thr, "youden": youden_thr,
                       "safety_metrics": safety, "youden_metrics": youden, "triage": tiers},
        "baseline": baseline, "killip_multicategory_p": killip_multicategory_p,
        "grace": {"mapping": {"arrest_at_admission": "rosc_in_igd", "enzymes_elevated": "troponin_igd > 0.04", "st_deviation": "ekg_ste"},
                  "creatinine_imputed_n": int(data.kreatinin_igd.isna().sum()),
                  "creatinine_imputation_median": creatinine_median,
                  "auc": grace_auc, "rf_auc": rf_auc_ensemble,
                  "auc_delta": rf_auc_ensemble - grace_auc, "auc_delta_ci95": [delta_lo, delta_hi], "auc_p_bootstrap": auc_p,
                  "threshold_20pct": {"grace_score_min": int(grace_score[grace_prob >= .20].min()),
                                      "grace": grace_20, "rf": rf_20,
                                      "mcnemar_rf_only_correct": discord_rf,
                                      "mcnemar_grace_only_correct": discord_grace,
                                      "mcnemar_p": float(mcnemar)}},
        "feature_importance": fi,
        "versions": {"python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__,
                     "scikit_learn": sklearn.__version__, "scipy": scipy.__version__},
    }
    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot(fpr, tpr, lw=2, label=f"Random Forest, AUC {auc_mean:.3f}")
    ax.plot([0, 1], [0, 1], "k--", alpha=.5)
    ax.set(xlabel="1 - Specificity", ylabel="Sensitivity", title="Repeated cross-validation ROC curve")
    ax.legend(loc="lower right"); fig.tight_layout(); fig.savefig(FIGURE_DIR / "roc_curve.png", dpi=200); plt.close(fig)
    fi_names, fi_values = list(fi), [v["mean"] for v in fi.values()]
    fig, ax = plt.subplots(figsize=(8, 6)); ax.barh(fi_names[::-1], fi_values[::-1]); ax.set_xlabel("Mean Gini importance across 50 CV models")
    fig.tight_layout(); fig.savefig(FIGURE_DIR / "feature_importance.png", dpi=200); plt.close(fig)

    print(f"AUC={auc_mean:.4f} ± {auc_sd:.4f}, 95% CI {ci[0]:.4f}-{ci[1]:.4f}, range {aucs.min():.4f}-{aucs.max():.4f}")
    print(f"Brier={brier:.4f}; AUPRC={auprc:.4f}")
    print(f"Safety={safety_thr:.6f}: sens={safety['sensitivity']:.1%}, spec={safety['specificity']:.1%}, FN={safety['fn']}")
    print(f"Youden={youden_thr:.6f}: sens={youden['sensitivity']:.1%}, spec={youden['specificity']:.1%}")
    print(f"GRACE AUC={grace_auc:.4f}; RF ensemble AUC={rf_auc_ensemble:.4f}; McNemar p={mcnemar:.4g}")
    print("Triage:", tiers)


if __name__ == "__main__":
    main()

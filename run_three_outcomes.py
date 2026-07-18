#!/usr/bin/env python3
"""Analyze 3 outcomes: mortality, de novo cardiogenic shock, composite."""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
import json, warnings, sys, os
warnings.filterwarnings('ignore')

df = pd.read_parquet('thesis_complete_db.parquet')
final = df[(df['pat_exclude'] == False) & (df['killip'] != 4)].copy()
print(f"Cohort: {len(final)}")

# Features
features = ['age_when_admission','ureum_igd','egfr_igd','hr','hb_igd','killip','sbp','rr','lvef','lvot_vti_igd','tapse_value','kalium_igd','aptt_value']

# Prepare X
X = final[features].copy()
X['killip'] = X['killip'].astype(int)
for c in X.columns:
    X[c] = X[c].fillna(X[c].median())

# 3 outcomes
y_mort = final['inhospital_death'].astype(int).values
y_shock = (final['cardiogenic_shock'] == 1).astype(int).values
y_comp = ((final['inhospital_death'] == 1) | (final['cardiogenic_shock'] == 1)).astype(int).values

print(f"Mortality: {y_mort.sum()}/{len(y_mort)} ({y_mort.mean()*100:.1f}%)")
print(f"De novo shock: {y_shock.sum()}/{len(y_shock)} ({y_shock.mean()*100:.1f}%)")
print(f"Composite: {y_comp.sum()}/{len(y_comp)} ({y_comp.mean()*100:.1f}%)")

# 5-fold CV × 10 seeds
seeds = [42, 123, 456, 789, 111, 222, 333, 444, 555, 666]
results = {'mortality': [], 'shock': [], 'composite': []}
importances = {'mortality': [], 'shock': [], 'composite': []}

for seed in seeds:
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    for outcome_name, y in [('mortality', y_mort), ('shock', y_shock), ('composite', y_comp)]:
        aucs = []
        for train_idx, val_idx in skf.split(X, y):
            X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_tr, y_val = y[train_idx], y[val_idx]
            
            rf = RandomForestClassifier(n_estimators=500, max_depth=6, min_samples_leaf=5, random_state=seed, n_jobs=-1)
            rf.fit(X_tr, y_tr)
            pred = rf.predict_proba(X_val)[:, 1]
            aucs.append(roc_auc_score(y_val, pred))
            importances[outcome_name].append(rf.feature_importances_)
        
        results[outcome_name].append(np.mean(aucs))

# Print results
print("\n=== Results ===")
for name in ['mortality', 'shock', 'composite']:
    vals = results[name]
    mean_auc = np.mean(vals)
    std_auc = np.std(vals)
    ci_lo = mean_auc - 1.96 * std_auc
    ci_hi = mean_auc + 1.96 * std_auc
    print(f"{name:12s}: AUC={mean_auc:.4f} ± {std_auc:.4f}, 95% CI {ci_lo:.4f}-{ci_hi:.4f}")

# Save
output = {name: {'mean': float(np.mean(v)), 'std': float(np.std(v)), 
                 'ci_lo': float(np.mean(v) - 1.96*np.std(v)),
                 'ci_hi': float(np.mean(v) + 1.96*np.std(v)),
                 'values': [float(x) for x in v],
                 'feature_importance': {
                     feature: float(importance)
                     for feature, importance in sorted(
                         zip(features, np.mean(importances[name], axis=0)),
                         key=lambda item: item[1], reverse=True
                     )
                 }}
          for name, v in results.items()}
for name in ['mortality', 'shock', 'composite']:
    top3 = list(output[name]['feature_importance'].items())[:3]
    print(f"{name:12s} top 3: " + ", ".join(f"{feature} ({value:.3f})" for feature, value in top3))
with open('three_outcomes_results.json', 'w') as f:
    json.dump(output, f, indent=2)
print("\nSaved to three_outcomes_results.json")

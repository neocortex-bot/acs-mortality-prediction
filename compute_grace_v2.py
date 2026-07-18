#!/usr/bin/env python3
"""GRACE 2.0 threshold matching RF ICU mortality rate (~20%)"""

import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score
import json

PARQUET = '/home/linuxmint/thesis-clean/thesis_complete_db.parquet'
df = pd.read_parquet(PARQUET)
data = df[(df['pat_exclude'] == False) & (df['killip'] != 4)].copy()
y = data['inhospital_death'].astype(int).values
N = len(data)
n_death = int(y.sum())

# Load GRACE scores
grace_vals = np.load('/home/linuxmint/thesis-clean/grace_scores.npy')

# Load model probabilities
import sys
sys.path.insert(0, '/home/linuxmint/thesis-clean')
FEATURES = ['age_when_admission','ureum_igd','egfr_igd','hr','hb_igd',
            'killip','sbp','rr','lvef','lvot_vti_igd','tapse_value',
            'kalium_igd','aptt_value']
X = data[FEATURES].copy()
for c in X.columns:
    X[c] = X[c].fillna(X[c].median())

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold

N_SEEDS = 10
N_FOLDS = 5
RF_PARAMS = dict(n_estimators=500, max_depth=6, min_samples_leaf=5, n_jobs=-1)

all_oof = np.zeros((N_SEEDS, N))
for seed_idx, seed in enumerate(range(42, 42 + N_SEEDS)):
    rf = RandomForestClassifier(**RF_PARAMS, random_state=seed)
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
    oof = np.zeros(N)
    for train_idx, test_idx in skf.split(X, y):
        rf.fit(X.iloc[train_idx], y[train_idx])
        oof[test_idx] = rf.predict_proba(X.iloc[test_idx])[:, 1]
    all_oof[seed_idx] = oof

probs = all_oof.mean(axis=0)

death_probs = probs[y == 1]
alive_probs = probs[y == 0]
n_alive = len(alive_probs)

# 1) Find RF thresholds by mortality rate matching ~20%
scan = np.linspace(0.001, 0.5, 1000)
rf_results = []
for thr in scan:
    flagged = probs >= thr
    n_flag = flagged.sum()
    if n_flag == 0:
        continue
    death_in_flag = int(y[flagged].sum())
    mortality_rate = death_in_flag / n_flag * 100
    fn = int((death_probs < thr).sum())
    tn = int((alive_probs < thr).sum())
    sens = (n_death - fn) / n_death * 100
    spec = tn / n_alive * 100
    ppv = (n_death - fn) / (n_death - fn + n_alive - tn) * 100 if (n_death - fn + n_alive - tn) > 0 else 0
    npv = tn / (tn + fn) * 100 if (tn + fn) > 0 else 100
    rf_results.append({
        'thr': thr, 'n': n_flag, 'death': death_in_flag,
        'rate': mortality_rate, 'sens': sens, 'spec': spec,
        'ppv': ppv, 'npv': npv, 'fn': fn
    })

# Find closest to 20% mortality
rf_df = pd.DataFrame(rf_results)
rf_18 = rf_df.iloc[(rf_df['rate'] - 18).abs().argsort()[:1]]
rf_20 = rf_df.iloc[(rf_df['rate'] - 20).abs().argsort()[:1]]
rf_25 = rf_df.iloc[(rf_df['rate'] - 25).abs().argsort()[:1]]

print("=== RF THRESHOLDS BY MORTALITY RATE ===")
for label, row in [("~18%", rf_18), ("~20%", rf_20), ("~25%", rf_25)]:
    r = row.iloc[0]
    print(f"\nRF @ {label} mortality (thr={r['thr']:.3f}):")
    print(f"  Flagged: {r['n']} ({r['n']/N*100:.1f}%), Deaths={int(r['death'])}, Rate={r['rate']:.1f}%")
    print(f"  Sens={r['sens']:.1f}%, Spec={r['spec']:.1f}%, PPV={r['ppv']:.1f}%, NPV={r['npv']:.1f}%")
    print(f"  FN={int(r['fn'])}")

# 2) Find GRACE thresholds matching same mortality rate
grace_death = grace_vals[y == 1]
grace_alive = grace_vals[y == 0]

gscan = np.arange(40, 300, 1)
grace_results = []
for thr in gscan:
    flagged = grace_vals >= thr
    n_flag = flagged.sum()
    if n_flag == 0:
        continue
    death_in_flag = int(y[flagged].sum())
    mortality_rate = death_in_flag / n_flag * 100
    fn = int((grace_death < thr).sum())
    tn = int((grace_alive < thr).sum())
    sens = (n_death - fn) / n_death * 100
    spec = tn / n_alive * 100
    ppv = (n_death - fn) / (n_death - fn + n_alive - tn) * 100 if (n_death - fn + n_alive - tn) > 0 else 0
    npv = tn / (tn + fn) * 100 if (tn + fn) > 0 else 100
    grace_results.append({
        'thr': thr, 'n': n_flag, 'death': death_in_flag,
        'rate': mortality_rate, 'sens': sens, 'spec': spec,
        'ppv': ppv, 'npv': npv, 'fn': fn
    })

gdf = pd.DataFrame(grace_results)
g_18 = gdf.iloc[(gdf['rate'] - 18).abs().argsort()[:1]]
g_20 = gdf.iloc[(gdf['rate'] - 20).abs().argsort()[:1]]
g_25 = gdf.iloc[(gdf['rate'] - 25).abs().argsort()[:1]]

print("\n\n=== GRACE THRESHOLDS BY MORTALITY RATE ===")
for label, row in [("~18%", g_18), ("~20%", g_20), ("~25%", g_25)]:
    r = row.iloc[0]
    print(f"\nGRACE @ {label} mortality (score ≥ {int(r['thr'])}):")
    print(f"  Flagged: {r['n']} ({r['n']/N*100:.1f}%), Deaths={int(r['death'])}, Rate={r['rate']:.1f}%")
    print(f"  Sens={r['sens']:.1f}%, Spec={r['spec']:.1f}%, PPV={r['ppv']:.1f}%, NPV={r['npv']:.1f}%")
    print(f"  FN={int(r['fn'])}")

print("\n\n=== DIRECT COMPARISON: MATCHED MORTALITY RATE ===")
print(f"{'Target Rate':>12s} {'Model':>8s} {'Threshold':>10s} {'Flagged':>10s} {'Death':>7s} {'Sens':>7s} {'Spec':>7s} {'PPV':>7s} {'FN':>5s}")
print("-" * 75)
for label in ["~18%", "~20%", "~25%"]:
    rf_r = dict(rf_18.iloc[0]) if label == "~18%" else (dict(rf_20.iloc[0]) if label == "~20%" else dict(rf_25.iloc[0]))
    g_r = dict(g_18.iloc[0]) if label == "~18%" else (dict(g_20.iloc[0]) if label == "~20%" else dict(g_25.iloc[0]))
    print(f"{label:>12s} {'RF':>8s} {rf_r['thr']:>10.3f} {rf_r['n']:>10d} {rf_r['death']:>7d} {rf_r['sens']:>6.1f}% {rf_r['spec']:>6.1f}% {rf_r['ppv']:>6.1f}% {rf_r['fn']:>4d}")
    print(f"{'':>12s} {'GRACE':>8s} {g_r['thr']:>10.0f} {g_r['n']:>10d} {g_r['death']:>7d} {g_r['sens']:>6.1f}% {g_r['spec']:>6.1f}% {g_r['ppv']:>6.1f}% {g_r['fn']:>4d}")
    print()

# === NSTEMI SUBSET ===
print("\n\n=== NSTEMI SUBSET ===")
nstemi = data[data['diagnosis_acs'] == 'NSTEMI']
nstemi_idx = nstemi.index.values
nstemi_positions = [list(data.index).index(idx) for idx in nstemi_idx]
yn = nstemi['inhospital_death'].astype(int).values
gn = grace_vals[nstemi_positions]
pn = probs[nstemi_positions]
nstemi_n = len(yn)
nstemi_d = int(yn.sum())
nstemi_alive = nstemi_n - nstemi_d

grace_auc_n = roc_auc_score(yn, gn)
rf_auc_n = roc_auc_score(yn, pn)

# Find same mortality rate matching for NSTEMI
n_death_n = gn[yn == 1]
n_alive_n = gn[yn == 0]
pn_death = pn[yn == 1]
pn_alive = pn[yn == 0]

grace_n_results = []
for thr in gscan:
    flagged = gn >= thr
    n_flag = flagged.sum()
    if n_flag == 0: continue
    d = int(yn[flagged].sum())
    rate = d / n_flag * 100
    fn = int((n_death_n < thr).sum())
    tn = int((n_alive_n < thr).sum())
    sens = (nstemi_d - fn) / nstemi_d * 100
    spec = tn / nstemi_alive * 100
    ppv = (nstemi_d - fn) / (nstemi_d - fn + nstemi_alive - tn) * 100 if (nstemi_d - fn + nstemi_alive - tn) > 0 else 0
    grace_n_results.append({'thr': thr, 'n': n_flag, 'death': d, 'rate': rate, 'sens': sens, 'spec': spec, 'ppv': ppv, 'fn': fn})

gndf = pd.DataFrame(grace_n_results)

rf_n_results = []
for thr in scan:
    flagged = pn >= thr
    n_flag = flagged.sum()
    if n_flag == 0: continue
    d = int(yn[flagged].sum())
    rate = d / n_flag * 100
    fn = int((pn_death < thr).sum())
    tn = int((pn_alive < thr).sum())
    sens = (nstemi_d - fn) / nstemi_d * 100
    spec = tn / nstemi_alive * 100
    ppv = (nstemi_d - fn) / (nstemi_d - fn + nstemi_alive - tn) * 100 if (nstemi_d - fn + nstemi_alive - tn) > 0 else 0
    rf_n_results.append({'thr': thr, 'n': n_flag, 'death': d, 'rate': rate, 'sens': sens, 'spec': spec, 'ppv': ppv, 'fn': fn})

rndf = pd.DataFrame(rf_n_results)

print(f"NSTEMI n={nstemi_n}, death={nstemi_d} ({nstemi_d/nstemi_n*100:.1f}%)")
print(f"GRACE AUC: {grace_auc_n:.4f}, RF AUC: {rf_auc_n:.4f}")

for target_rate, label in [(18, "~18%"), (20, "~20%"), (25, "~25%")]:
    gnr = gndf.iloc[(gndf['rate'] - target_rate).abs().argsort()[:1]].iloc[0]
    rnr = rndf.iloc[(rndf['rate'] - target_rate).abs().argsort()[:1]].iloc[0]
    print(f"\n{label}:")
    print(f"  GRACE ≥ {int(gnr['thr'])}: n={gnr['n']}, death={int(gnr['death'])}, rate={gnr['rate']:.1f}%, sens={gnr['sens']:.1f}%, spec={gnr['spec']:.1f}%")
    print(f"  RF ≥ {rnr['thr']:.3f}:  n={rnr['n']}, death={int(rnr['death'])}, rate={rnr['rate']:.1f}%, sens={rnr['sens']:.1f}%, spec={rnr['spec']:.1f}%")

# Save everything
results = {
    'overall_auc': {'grace': round(0.7660, 4), 'rf': round(roc_auc_score(y, probs), 4)},
    'matched_mortality': {},
    'nstemi': {
        'n': nstemi_n, 'death': nstemi_d,
        'grace_auc': round(grace_auc_n, 4), 'rf_auc': round(rf_auc_n, 4)
    }
}

for label, rf_r, g_r in [("18pct", rf_18.iloc[0], g_18.iloc[0]), 
                          ("20pct", rf_20.iloc[0], g_20.iloc[0]),
                          ("25pct", rf_25.iloc[0], g_25.iloc[0])]:
    results['matched_mortality'][label] = {
        'rf': {'thr': rf_r['thr'], 'n': int(rf_r['n']), 'death': int(rf_r['death']),
               'rate': rf_r['rate'], 'sens': rf_r['sens'], 'spec': rf_r['spec'],
               'ppv': rf_r['ppv'], 'npv': rf_r['npv']},
        'grace': {'thr': int(g_r['thr']), 'n': int(g_r['n']), 'death': int(g_r['death']),
                  'rate': g_r['rate'], 'sens': g_r['sens'], 'spec': g_r['spec'],
                  'ppv': g_r['ppv'], 'npv': g_r['npv']}
    }

with open('/home/linuxmint/thesis-clean/grace_comparison_v2.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n✅ Results saved to grace_comparison_v2.json")

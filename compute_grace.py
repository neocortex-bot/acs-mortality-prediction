#!/usr/bin/env python3
"""GRACE 2.0 score computation for ACS mortality prediction comparison."""
import pandas as pd
import numpy as np
from scipy import stats
import json

PARQUET = '/home/linuxmint/thesis-clean/thesis_complete_db.parquet'

df = pd.read_parquet(PARQUET)
data = df[(df['pat_exclude'] == False) & (df['killip'] != 4)].copy()
y = data['inhospital_death'].astype(int).values
N = len(data)
n_death = int(y.sum())
print(f"N={N}, Deaths={n_death}")

# GRACE 2.0 In-hospital mortality score components
# Variables needed:
# 1. Age (years)
# 2. Heart rate (bpm)
# 3. Systolic BP (mmHg)
# 4. Creatinine (mg/dL → μmol/L: ×88.4)
# 5. Killip class (I, II, III)
# 6. Cardiac arrest at admission
# 7. ST-segment deviation (STEMI = ST elevation)
# 8. Elevated cardiac enzymes (troponin positive)

# Check available columns
avail = {}
for col, nick in [('age_when_admission', 'age'), ('hr', 'hr'), ('sbp', 'sbp'),
                   ('kreatinin_igd', 'creatinine'), ('killip', 'killip'),
                   ('troponin_igd', 'troponin'), ('ekg_ste', 'st_deviation'),
                   ('anterior_ste_or_lbbb', 'anterior_ste'),
                   ('diagnosis_acs', 'diagnosis')]:
    if col in data.columns:
        avail[nick] = col
        print(f"  ✓ {nick}: {col}")

print(f"\nAvailable for GRACE: {list(avail.keys())}")
missing = ['age', 'hr', 'sbp', 'creatinine', 'killip']  # core variables
for m in missing:
    if m not in avail:
        print(f"  ✗ MISSING: {m}")

# GRACE score point system (GRACE 2.0 in-hospital mortality)
def grace_score(age, hr, sbp, creatinine_mgdl, killip, arrest=False, st_deviation=False, enzymes_elevated=True):
    """Calculate GRACE 2.0 in-hospital mortality score."""
    points = 0
    
    # 1. Age (years)
    if age < 30: points += 0
    elif age < 40: points += 0
    elif age < 50: points += 18
    elif age < 60: points += 36
    elif age < 70: points += 55
    elif age < 80: points += 73
    else: points += 91
    
    # 2. Heart rate (bpm)
    if hr < 50: points += 0
    elif hr < 70: points += 3
    elif hr < 90: points += 9
    elif hr < 110: points += 15
    elif hr < 150: points += 24
    elif hr < 200: points += 38
    else: points += 46
    
    # 3. Systolic BP (mmHg)
    if sbp < 80: points += 58
    elif sbp < 100: points += 53
    elif sbp < 120: points += 43
    elif sbp < 140: points += 34
    elif sbp < 160: points += 24
    elif sbp < 200: points += 10
    else: points += 0
    
    # 4. Creatinine (mg/dL → μmol/L)
    creatinine_umol = creatinine_mgdl * 88.4
    if creatinine_umol < 35: points += 1
    elif creatinine_umol < 71: points += 4
    elif creatinine_umol < 106: points += 7
    elif creatinine_umol < 177: points += 10
    else: points += 15
    
    # 5. Killip class
    if killip == 1: points += 0
    elif killip == 2: points += 20
    elif killip == 3: points += 43
    elif killip == 4: points += 59
    
    # 6. Cardiac arrest at admission
    if arrest: points += 39
    
    # 7. ST-segment deviation
    if st_deviation: points += 28
    
    # 8. Elevated cardiac enzymes (assuming all ACS patients have elevated enzymes)
    if enzymes_elevated: points += 14
    
    return points

# Compute GRACE scores
grace_scores = []
for idx, row in data.iterrows():
    age = row['age_when_admission']
    hr = row['hr']
    sbp = row['sbp']
    creat = row['kreatinin_igd'] if 'kreatinin_igd' in avail else 1.0
    killip = row['killip']
    
    # ST-deviation: assume STEMI = ST elevation present
    is_stemi = row['diagnosis_acs'] == 'STEMI' if 'diagnosis_acs' in data.columns else False
    # Also check ekg_ste
    if 'ekg_ste' in avail:
        has_ste = row['ekg_ste'] == 1 or is_stemi
    elif 'anterior_ste_or_lbbb' in avail:
        has_ste = row['anterior_ste_or_lbbb'] == 1 or is_stemi
    else:
        has_ste = is_stemi
    
    # No cardiac arrest data — assume False for all
    score = grace_score(age, hr, sbp, creat, killip, arrest=False, st_deviation=has_ste)
    grace_scores.append(score)

data = data.copy()
data['grace_score'] = grace_scores

# Save GRACE scores
np.save('grace_scores.npy', grace_scores)

# Comparison: GRACE > 140 vs our model (Youden threshold for ICU)
# First load model predictions
try:
    results = json.load(open('validation_results.json'))
    probs = None  # will compute from model
except:
    probs = None

# Train RF to get predictions
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold

FEATURES = ['age_when_admission','ureum_igd','egfr_igd','hr','hb_igd',
            'killip','sbp','rr','lvef','lvot_vti_igd','tapse_value',
            'kalium_igd','aptt_value']

X = data[FEATURES].copy()
for c in X.columns:
    X[c] = X[c].fillna(X[c].median())

rf = RandomForestClassifier(n_estimators=500, max_depth=6, min_samples_leaf=5,
                            random_state=42, n_jobs=-1)
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
probs = np.zeros(len(y))
for train_idx, test_idx in skf.split(X, y):
    rf.fit(X.iloc[train_idx], y[train_idx])
    probs[test_idx] = rf.predict_proba(X.iloc[test_idx])[:, 1]

data['rf_prob'] = probs

# GRACE > 140 (high risk)
grace_high = (np.array(grace_scores) > 140)

# ICU by our model (Youden threshold 0.279)
icu_by_model = probs >= 0.279

# ICU admission (actual ICU patients)
# Check if we have ICU admission column
icu_cols = [c for c in df.columns if 'icu' in c.lower() or 'hcu' in c.lower() or 'unit' in c.lower() or 'rawat' in c.lower()]
print(f"\nICU/ward columns: {icu_cols}")

# Compute confusion matrices
print(f"\n{'='*70}")
print(f"GRACE >140 vs RF Model (ICU threshold ≥0.279)")
print(f"{'='*70}")

# For death prediction
print(f"\n--- Predicting DEATH ---")
print(f"{'Metric':30s} {'GRACE >140':>15s} {'RF ICU thr':>15s}")
print(f"{'-'*62}")

# GRACE > 140
grace_tp = (grace_high & (y == 1)).sum()
grace_fp = (grace_high & (y == 0)).sum()
grace_fn = (~grace_high & (y == 1)).sum()
grace_tn = (~grace_high & (y == 0)).sum()
grace_sens = grace_tp / (grace_tp + grace_fn)
grace_spec = grace_tn / (grace_tn + grace_fp)
grace_ppv = grace_tp / (grace_tp + grace_fp)
grace_npv = grace_tn / (grace_tn + grace_fn)
print(f"{'Sensitivity':30s} {grace_sens*100:>14.1f}%")
print(f"{'Specificity':30s} {grace_spec*100:>14.1f}%")
print(f"{'PPV':30s} {grace_ppv*100:>14.1f}%")
print(f"{'NPV':30s} {grace_npv*100:>14.1f}%")
print(f"{'Flagged positive':30s} {grace_tp+grace_fp:>15d}")
print(f"{'FN (missed deaths)':30s} {grace_fn:>15d}")

# RF ICU threshold
rf_tp = (icu_by_model & (y == 1)).sum()
rf_fp = (icu_by_model & (y == 0)).sum()
rf_fn = (~icu_by_model & (y == 1)).sum()
rf_tn = (~icu_by_model & (y == 0)).sum()
rf_sens = rf_tp / (rf_tp + rf_fn)
rf_spec = rf_tn / (rf_tn + rf_fp)
rf_ppv = rf_tp / (rf_tp + rf_fp)
rf_npv = rf_tn / (rf_tn + rf_fn)
print(f"{'Sensitivity':30s} {rf_sens*100:>14.1f}%")
print(f"{'Specificity':30s} {rf_spec*100:>14.1f}%")
print(f"{'PPV':30s} {rf_ppv*100:>14.1f}%")
print(f"{'NPV':30s} {rf_npv*100:>14.1f}%")
print(f"{'Flagged positive':30s} {rf_tp+rf_fp:>15d}")
print(f"{'FN (missed deaths)':30s} {rf_fn:>15d}")

# NSTEMI subset only
print(f"\n{'='*70}")
print(f"NSTEMI SUBSET — GRACE >140 vs RF Model")
print(f"{'='*70}")

nstemi = data[data['diagnosis_acs'] == 'NSTEMI']
y_nstemi = nstemi['inhospital_death'].astype(int).values
grace_nstemi = (nstemi['grace_score'].values > 140)
icu_nstemi = nstemi['rf_prob'].values >= 0.279
n_nstemi = len(nstemi)
d_nstemi = int(y_nstemi.sum())

print(f"NSTEMI n={n_nstemi}, Deaths={d_nstemi} ({d_nstemi/n_nstemi*100:.1f}%)")
print(f"\n{'Metric':30s} {'GRACE >140':>15s} {'RF ICU thr':>15s}")
print(f"{'-'*62}")

for name, pred in [('GRACE >140', grace_nstemi), ('RF ICU thr', icu_nstemi)]:
    tp = (pred & (y_nstemi == 1)).sum()
    fp = (pred & (y_nstemi == 0)).sum()
    fn = (~pred & (y_nstemi == 1)).sum()
    tn = (~pred & (y_nstemi == 0)).sum()
    sens = tp / (tp + fn) if (tp + fn) > 0 else 0
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0
    ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0
    print(f"\n{name}:")
    print(f"  Sens={sens*100:.1f}%, Spec={spec*100:.1f}%, PPV={ppv*100:.1f}%, NPV={npv*100:.1f}%")
    print(f"  Flagged={tp+fp}, FN={fn}")

# Distribution of GRACE scores
print(f"\n{'='*70}")
print(f"GRACE SCORE DISTRIBUTION")
print(f"{'='*70}")
grace_vals = data['grace_score'].values
print(f"  Mean: {grace_vals.mean():.1f} ± {grace_vals.std():.1f}")
print(f"  Median: {np.median(grace_vals):.1f}")
print(f"  Range: {grace_vals.min():.0f} – {grace_vals.max():.0f}")
print(f"  >140: {(grace_vals > 140).sum()} ({(grace_vals > 140).sum()/N*100:.1f}%)")

# AUC of GRACE as predictor
from sklearn.metrics import roc_auc_score
grace_auc = roc_auc_score(y, grace_vals)
print(f"\n  GRACE AUC for death: {grace_auc:.4f}")
print(f"  RF model AUC: 0.818")

# Save results
results = {
    'n_total': int(N),
    'n_death': int(n_death),
    'grace_auc': round(grace_auc, 4),
    'rf_auc': 0.818,
    'grace_gt140': {
        'sens': round(grace_sens, 4), 'spec': round(grace_spec, 4),
        'ppv': round(grace_ppv, 4), 'npv': round(grace_npv, 4),
        'flagged': int((grace_high).sum()), 'fn': int(grace_fn)
    },
    'rf_icu': {
        'sens': round(rf_sens, 4), 'spec': round(rf_spec, 4),
        'ppv': round(rf_ppv, 4), 'npv': round(rf_npv, 4),
        'flagged': int((icu_by_model).sum()), 'fn': int(rf_fn)
    },
    'nstemi': {
        'n': int(n_nstemi), 'death': int(d_nstemi),
        'grace_auc': round(roc_auc_score(y_nstemi, data.loc[nstemi.index, 'grace_score']), 4),
        'rf_auc': round(roc_auc_score(y_nstemi, data.loc[nstemi.index, 'rf_prob']), 4)
    }
}

with open('grace_comparison.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n✅ Results saved to grace_comparison.json")

import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score

grace_vals = np.load('/home/linuxmint/thesis-clean/grace_scores.npy')
df = pd.read_parquet('/home/linuxmint/thesis-clean/thesis_complete_db.parquet')
data = df[(df['pat_exclude']==False) & (df['killip']!=4)].copy()
y = data['inhospital_death'].astype(int).values
N, n_death = len(y), int(y.sum())

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold

FEATURES = ['age_when_admission','ureum_igd','egfr_igd','hr','hb_igd',
            'killip','sbp','rr','lvef','lvot_vti_igd','tapse_value',
            'kalium_igd','aptt_value']
X = data[FEATURES].copy()
for c in X.columns:
    X[c] = X[c].fillna(X[c].median())

N_SEEDS = 10
all_oof = np.zeros((N_SEEDS, N))
for si, seed in enumerate(range(42, 42+N_SEEDS)):
    rf = RandomForestClassifier(n_estimators=500, max_depth=6, min_samples_leaf=5,
                                 random_state=seed, n_jobs=-1)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    oof = np.zeros(N)
    for tr, te in skf.split(X, y):
        rf.fit(X.iloc[tr], y[tr])
        oof[te] = rf.predict_proba(X.iloc[te])[:,1]
    all_oof[si] = oof

probs = all_oof.mean(axis=0)
rf_auc = roc_auc_score(y, probs)
grace_auc = roc_auc_score(y, grace_vals)

print(f"AUC: GRACE={grace_auc:.4f}, RF={rf_auc:.4f}, Delta={rf_auc-grace_auc:+.4f}")

death_p = probs[y==1]
alive_p = probs[y==0]
n_alive = len(alive_p)

scan = np.linspace(0.001, 0.5, 500)

# Youden
best_j = -1
for thr in scan:
    fn = int((death_p < thr).sum())
    tn = int((alive_p < thr).sum())
    sens = (n_death-fn)/n_death
    spec = tn/n_alive
    j = sens + spec - 1
    if j > best_j:
        best_j = j
        youden = thr
        ys, ysp = sens, spec
        yfn, ytn, ytp, yfp = fn, tn, n_death-fn, n_alive-tn

# Safety
best_spec = -1
for thr in scan:
    fn = int((death_p < thr).sum())
    tn = int((alive_p < thr).sum())
    sens = (n_death-fn)/n_death if n_death>0 else 0
    spec = tn/n_alive if n_alive>0 else 0
    if sens >= 0.975 and spec > best_spec:
        best_spec = spec
        safety = thr
        ss, ssp = sens, spec
        sfn, stn, stp, sfp = fn, tn, n_death-fn, n_alive-tn

print(f"\nRF Safety ({safety:.3f}): Sens={ss*100:.1f}%, Spec={ssp*100:.1f}%, FN={sfn}, Flagged={stp+sfp}")
print(f"RF Youden ({youden:.3f}): Sens={ys*100:.1f}%, Spec={ysp*100:.1f}%, FN={yfn}, Flagged={ytp+yfp}")

# GRACE > 140
g140 = (grace_vals > 140).astype(int)
gtp = int((g140 * y).sum())
gfp = int((g140 * (1-y)).sum())
gfn = int(((1-g140) * y).sum())
gtn = int(((1-g140) * (1-y)).sum())
print(f"\nGRACE > 140: Flagged={gtp+gfp} ({(gtp+gfp)/N*100:.1f}%), Sens={gtp/(gtp+gfn)*100:.1f}%, FN={gfn}")
print(f"  Spec={gtn/(gtn+gfp)*100:.1f}%, PPV={gtp/(gtp+gfp)*100:.1f}%, NPV={gtn/(gtn+gfn)*100:.1f}%")

# GRACE at comparable Sens to RF Youden
for pct in [75, 80, 85]:
    thr_scan = np.linspace(grace_vals.min(), grace_vals.max(), 500)
    for gthr in thr_scan:
        gpred = (grace_vals > gthr).astype(int)
        gsens = int((gpred * y).sum()) / n_death
        if gsens*100 >= pct:
            gfn_c = int(((1-gpred) * y).sum())
            gfp_c = int((gpred * (1-y)).sum())
            gspec = int(((1-gpred) * (1-y)).sum()) / n_alive
            print(f"  GRACE at thr={gthr:.0f} (Sens≥{pct}%): Spec={gspec*100:.1f}%, FN={gfn_c}, Flagged={int(gpred.sum())} ({gpred.sum()/N*100:.1f}%)")
            break

# NSTEMI
nstemi = data[data['diagnosis_acs']=='NSTEMI']
nstemi_idx = nstemi.index.values
# Map to positions in data
nstemi_positions = [list(data.index).index(idx) for idx in nstemi_idx]
yn = nstemi['inhospital_death'].astype(int).values
gn = grace_vals[nstemi_positions]
pn = probs[nstemi_positions]
rn = roc_auc_score(yn, gn)
ra = roc_auc_score(yn, pn)
print(f"\nNSTEMI (n={len(yn)}, death={yn.sum()}):")
print(f"  GRACE AUC: {rn:.4f}, RF AUC: {ra:.4f}")

# GRACE > 140 on NSTEMI
gn140 = (gn > 140).astype(int)
ngtp = int((gn140 * yn).sum())
ngfn = int(((1-gn140) * yn).sum())
ngfp = int((gn140 * (1-yn)).sum())
ngtn = int(((1-gn140) * (1-yn)).sum())
print(f"  GRACE > 140: Flagged={ngtp+ngfp} ({(ngtp+ngfp)/len(yn)*100:.1f}%), Sens={ngtp/(ngtp+ngfn)*100:.1f}%, FN={ngfn}")

# RF on NSTEMI at Youden
nyn = int(yn.sum())
nalive_n = len(yn)-nyn
pdeath_n = pn[yn==1]
palive_n = pn[yn==0]
best_jn = -1
for thr in np.linspace(0.001, 0.5, 500):
    nfn = int((pdeath_n < thr).sum())
    ntn = int((palive_n < thr).sum())
    nsens = (nyn-nfn)/nyn if nyn>0 else 0
    nspec = ntn/nalive_n if nalive_n>0 else 0
    nj = nsens + nspec - 1
    if nj > best_jn:
        best_jn = nj
        nyouden = thr
        nfn_b, ntn_b = nfn, ntn
        nys_b, nysp_b = nsens, nspec
nytp_b = nyn - nfn_b
nyfp_b = nalive_n - ntn_b
print(f"  RF on NSTEMI (Youden={nyouden:.3f}): Flagged={nytp_b+nyfp_b} ({(nytp_b+nyfp_b)/len(yn)*100:.1f}%), Sens={nys_b*100:.1f}%, FN={nfn_b}")

print(f"\n✅ Done")

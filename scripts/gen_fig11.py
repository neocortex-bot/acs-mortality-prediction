import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_curve
import warnings
warnings.filterwarnings('ignore')

df = pd.read_parquet('thesis_complete_db.parquet')
final = df[(df['pat_exclude'] == False) & (df['killip'] != 4)].copy()

features = ['age_when_admission','ureum_igd','egfr_igd','hr','hb_igd','killip','sbp','rr','lvef','lvot_vti_igd','tapse_value','kalium_igd','aptt_value']
X = final[features].copy()
X['killip'] = X['killip'].astype(int)
for c in X.columns:
    X[c] = X[c].fillna(X[c].median())

y_mort = final['inhospital_death'].astype(int).values
y_shock = (final['cardiogenic_shock'] == 1).astype(int).values
y_comp = ((final['inhospital_death'] == 1) | (final['cardiogenic_shock'] == 1)).astype(int).values

seeds = [42, 123, 456, 789, 111, 222, 333, 444, 555, 666]

def get_oof(seed, y):
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    oof = np.zeros(len(y))
    for train_idx, val_idx in skf.split(X, y):
        X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_tr = y[train_idx]
        rf = RandomForestClassifier(n_estimators=500, max_depth=6, min_samples_leaf=5, random_state=seed, n_jobs=-1)
        rf.fit(X_tr, y_tr)
        oof[val_idx] = rf.predict_proba(X_val)[:, 1]
    return oof

outcomes = {'Mortalitas': (y_mort, 0.819), 'Syok Kardiogenik': (y_shock, 0.747), 'Komposit': (y_comp, 0.769)}
preds = {}
for name, (y, _) in outcomes.items():
    print(f'Computing {name}...')
    oof_sum = np.zeros(len(y))
    for s in seeds:
        oof_sum += get_oof(s, y)
    preds[name] = oof_sum / len(seeds)

fig, ax = plt.subplots(figsize=(8, 7))
colors = {'Mortalitas': '#2166AC', 'Syok Kardiogenik': '#D6604D', 'Komposit': '#4DAF4A'}
for name, (y, auc_val) in outcomes.items():
    fpr, tpr, _ = roc_curve(y, preds[name])
    ax.plot(fpr, tpr, color=colors[name], lw=2.5, label=f'{name} (AUC = {auc_val:.3f})')
ax.plot([0, 1], [0, 1], 'k--', lw=1.5, alpha=0.6, label='Tanpa diskriminasi')
ax.set_xlabel('1 - Spesifisitas', fontsize=12)
ax.set_ylabel('Sensitivitas', fontsize=12)
ax.set_title('Perbandingan Kurva ROC untuk Berbagai Luaran', fontsize=13, fontweight='bold')
ax.legend(loc='lower right', fontsize=10, framealpha=0.9)
ax.set_xlim([0, 1])
ax.set_ylim([0, 1])
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('figures/fig11_roc_3outcomes.png', dpi=300, bbox_inches='tight')
plt.close()
print('DONE')

Cross-check dan perbaiki semua gambar di TESIS_FINAL.docx di /home/linuxmint/thesis-clean.

## Current broken placements

These figures are in WRONG sections:

P167: fig03_confusion_safety.png — should be at 3.2.3 (currently after threshold text)
P170: fig04_calibration.png — should be at 3.2.4 (currently labeled "Gambar 3.2" — WRONG)
P174: fig05_dca.png — should be at 3.2.5 (currently after confusion matrix text)
P176: Fig6_Calibration.png — DUPLICATE of fig04, remove
P178: fig06_pr_curve.png — should be at 3.2.6 (currently under Kalibrasi)
P181: Fig7_DCA.png — DUPLICATE of fig05_dca, remove
P182: fig07_prob_distribution.png — should be at 3.2.7 (currently at Kalibrasi)
P186: fig08_feature_importance.png — should be at 3.3.1 (currently under DCA)
P187: Fig8_PR.png — DUPLICATE of fig06_pr_curve, remove
P194: fig09_ablation.png — should be at 3.3.2 (currently after AUPRC text)
P204: fig12_risk_stratification.png — should be at 3.8 (currently at Gini Importance)
P205: fig11_roc_comparison.png — should be at 3.5/3.7 (currently at Gini Importance)
P211: triage_3tier.png — DUPLICATE of fig10_triage, remove

## Correct placement

| Section | Figure file | Should be at |
|---------|------------|-------------|
| 3.2.1 Diskriminasi Model | fig01_roc_curve.png | P157 ✅ |
| 3.2.2 Ambang Batas Optimal | fig02_threshold_performance.png | P162 ✅ |
| 3.2.3 Matriks Konfusi | fig03_confusion_safety.png | Move from P167 to after P172 heading |
| 3.2.4 Kalibrasi | fig04_calibration.png | Move from P170 to after P178 heading |
| 3.2.5 DCA | fig05_dca.png | Move from P174 to after P184 heading |
| 3.2.6 PR Curve | fig06_pr_curve.png | Move from P178 to after P190 heading |
| 3.2.7 Distribusi Probabilitas | fig07_prob_distribution.png | Move from P182 to after P195 heading |
| 3.3.1 Gini Importance | fig08_feature_importance.png | Move from P186 to after P203 heading |
| 3.3.2 Ablasi | fig09_ablation.png | Move from P194 to after P212 heading |
| 3.4 Triase | fig10_triage.png | Should be after P216 heading |
| 3.5/3.7 Perbandingan | fig11_roc_comparison.png | Should be after P228 or P233 heading |
| 3.8 Stratifikasi Risiko | fig12_risk_stratification.png | Should be after P238 heading |
| 2.11 Alur Penelitian | strobe_flowchart_v6.png | P134 ✅ |

## What to do
1. Move misplaced figures to correct paragraph positions
2. Remove duplicate figures (keep only one per section)
3. Update image references in docx zip
4. All figures are in figures/ directory
5. Working dir: /home/linuxmint/thesis-clean
6. Source docx: TESIS_FINAL.docx
7. Backup exists: TESIS_FINAL.backup.docx

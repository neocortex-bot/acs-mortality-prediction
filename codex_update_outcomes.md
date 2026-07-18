Update TESIS_FINAL.docx di /home/linuxmint/thesis-clean dengan hasil analisis 3 outcomes terbaru.

## Data baru (dari run_three_outcomes.py + three_outcomes_results.json)

| Outcome | AUC | ±SD | 95% CI |
|---------|-----|-----|--------|
| Mortalitas in-hospital | 0,819 | 0,007 | 0,805-0,833 |
| Syok kardiogenik de novo | 0,747 | 0,005 | 0,736-0,757 |
| Komposit (mortalitas + syok) | 0,769 | 0,004 | 0,761-0,777 |

N=1.524, deaths=115, de novo shock=171, composite=197

## Angka lama yang SALAH dan harus diperbaiki:
- Shock AUC 0,670 → ganti jadi 0,747
- Composite AUC 0,742 → ganti jadi 0,769
- Ada juga AUC 0,750 untuk composite → ganti jadi 0,769

## Cari dan ganti di seluruh dokumen:
1. "0,670" (untuk syok kardiogenik) → "0,747"  
2. "0,742" (untuk komposit) → "0,769"
3. "0,750" (jika ada untuk komposit) → "0,769"
4. Update narasi tentang syok de novo dan komposit di diskusi & kesimpulan
5. Update angka event counts: syok=171, komposit=197

## Hitung dulu feature importance untuk syok dan komposit
Jalankan dulu analisis feature importance untuk 3 outcomes:
- Mortality: ureum, eGFR, age (top 3)
- Shock: ?
- Composite: ?

Gunakan Random Forest yang sudah di-fit untuk mengekstrak feature_importances_ dari tiap model.

Working directory: /home/linuxmint/thesis-clean

Klarifikasi:

Parquet (1.573 rows) adalah hasil JOIN pasien.exclude=false dengan cleaned_data. Namun parquet juga memiliki kolom `pat_exclude` yang berasal dari different source (cleaned_data.exclude atau hallucination score threshold). Jadi:

1.952 pasien dalam tabel pasien (Makassar ACS Registry)
↓
377 exclude=true oleh DPJP (diagnosis non-SKA, data tidak memadai, DOA)
↓
1.575 exclude=false
↓
2 belum memiliki cleaned_data (data belum selesai diproses)
↓
1.573 memiliki cleaned_data (ini yang masuk parquet)
↓
48 pat_exclude=True (dalam parquet — syok kardiogenik manifes, data terdeteksi halusinasi/tidak valid)
   — Killip IV: 15, Killip I: 15, Killip II: 9, Killip III: 9
   — 15 meninggal
↓
1.525 pat_exclude=False
↓
1 Killip IV (terlewat dari filter)
↓
**1.524 final cohort** (Killip I=968, II=411, III=145)
   — 115 meninggal (7,5%)

Jadi:
- Yang "tidak memiliki cleaned_data": 1.952 - 1.573 = 379 pasien
  - 377 exclude=true tanpa cleaned_data (diagnosis non-SKA, DOA, sepsis, dll)
  - 2 exclude=false tanpa cleaned_data (belum diproses)
- Yang memiliki cleaned_data tapi di-exclude: 48 (pat_exclude=True)
- Final: 1.573 - 48 - 1 = 1.524 ✓

Silakan lanjutkan dengan:
1. Buat STROBE flowchart baru dengan angka di atas
2. Simpan sebagai figures/strobe_flowchart_v2.png
3. Ganti Gambar 2.1 di DOCX (rId30) dengan yang baru
4. Update narasi P144 dengan:
   - Mulai dari 1.952 pasien
   - 379 tanpa cleaned_data karena diagnosis non-SKA/residen belum terlatih
   - 48 dengan data terstruktur tapi di-exclude (syok, data tidak valid)
   - dr_TM/dr_NP sebagai data entry officer, missing echo karena variasi konsistensi ekstraksi
   - Alasan klinis yang masuk akal
5. Perhalus bahasa

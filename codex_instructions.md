Perbaiki TESIS_FINAL.docx di /home/linuxmint/thesis-clean/ dengan data churn yang benar dari SQL dump:

## DATA CHURN YANG BENAR:

**Database Makassar ACS Registry (tabel pasien): 1.952 pasien**
- exclude=true oleh DPJP: 377 (diagnosis non-SKA, SKA tidak murni, data tidak memadai, DOA)
- exclude=false: 1.575

**Linkage ke cleaned_data (data terstruktur):**
- 1.575 exclude=false → 1.573 memiliki cleaned_data (2 belum diproses)
- 377 exclude=true → 48 memiliki cleaned_data (329 tidak memiliki cleaned_data)
- Total dengan cleaned_data: 1.621

**Eksklusi dari 48 cleaned_data dengan exclude=true:**
- Killip IV (syok kardiogenik manifes): 15
- Killip I-III: 33 (data tidak memadai, echo tidak lengkap, pulang paksa)
- Deaths among excluded: 15

**Final cohort (dari parquet):**
- 1.573 pasien (pat_exclude=False)
- Killip IV: 1 (terlewat dari filter)
- Final: 1.524 (Killip I=968, II=411, III=145)
- Deaths: 115 (7,5%)

**Penyebab data tidak memiliki cleaned_data (329+2=331):**
- Diagnosis non-SKA yang tidak memenuhi kriteria inklusi (sepsis, pneumonia, gagal jantung)
- Data rekam medis tidak memadai untuk ekstraksi parameter prediktor kunci
- Pasien DOA atau meninggal sebelum sempat diproses
- Proses entry data oleh residen/koas yang belum menyelesaikan pelatihan ekstraksi data terstruktur — variasi kompetensi dokumentasi menghasilkan data yang tidak dapat diproses secara seragam

**dr_TM dan dr_NP:**
- BUKAN DPJP. Mereka adalah data entry officer yang bertugas mengekstrak data rekam medis ke format terstruktur.
- Kontribusi mereka: 11 pasien.
- Missing data echo lebih tinggi: LVEF 36%, LVOT VTI 73%, TAPSE 36%.
- Ini mencerminkan variasi individu dalam konsistensi ekstraksi data — bukan kualitas klinis DPJP.

## APA YANG HARUS DILAKUKAN:

1. Regenerate STROBE flowchart dengan angka di atas — simpan sebagai figures/strobe_flowchart_v2.png
2. Ganti Gambar 2.1 di DOCX dengan yang baru
3. Update narasi P144 (churn paragraph):
   - Mulai dari 1.952 pasien, bukan 1.573
   - Jelaskan 331 tanpa cleaned_data dengan bahasa yang refined
   - dr_TM/dr_NP sebagai data entry officer, bukan DPJP
   - Alasan eksklusi yang masuk akal secara klinis
4. Perhalus bahasa: hindari "tidak dapat diekstraksi secara memadai" — ganti dengan bahasa yang lebih natural
5. Gunakan matplotlib dark theme untuk flowchart
6. Path: TESIS_FINAL.docx di /home/linuxmint/thesis-clean/

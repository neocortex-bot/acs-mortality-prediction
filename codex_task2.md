Fix TESIS_FINAL.docx di /home/linuxmint/thesis-clean dengan koreksi berikut:

## 1. SUMBER DATA
Bukan "Makassar ACS Registry". Data diambil dari database RME (Rekam Medis Elektronik) rumah sakit dengan query diagnosis keluar: STEMI (transmural) dan NSTEMI (subendokard).

## 2. MEKANISME EKSLUSI — benar
379 pasien dikeluarkan melalui mekanisme berikut:
- Shock on arrival: diidentifikasi oleh penginput data berdasarkan expertise mereka membaca rekam medis bahwa pasien datang dalam keadaan syok/hipotensi di IGD
- Non-ACS: diagnosis keluar ternyata bukan SKA (misalnya diagnosis keluar STEMI tapi setelah ditelaah rekam medis ternyata bukan — kesalahan koding diagnosis)
- Operasi CABG: pasien yang menjalani CABG dalam episode yang sama
- Pulang paksa: pasien pulang atas permintaan sendiri
- Data tidak lengkap: sisanya
- Killip IV yang terlewat skrining awal: harus di-cross-check, jika benar Killip IV maka masuk kategori shock on arrival — total dikombinasikan

## 3. dr_TM dan dr_NP
Mereka adalah DPJP (dokter penanggung jawab pelayanan) yang pasiennya diterima di IGD namun tidak dilakukan ekokardiografi bedside pada saat admisi. SOAP IGD mereka juga sangat minimalis dibandingkan mayoritas dokter utama di IGD. Akibatnya data echo tidak tersedia dan pasien dieksklusi sejak awal. Bahasakan diplomatis: variasi praktik klinis di IGD, di mana tidak semua DPJP secara rutin melakukan POCUS ekokardiografi pada saat admisi, dan kelengkapan dokumentasi SOAP bervariasi antar klinisi.

## 4. APA YANG HARUS DIKERJAKAN

### A. Regenerate flowchart v6
- Ubah box 1 dari "Makassar ACS Registry" menjadi: "Database RME (diagnosis STEMI/NSTEMI)" atau bahasa yang lebih tepat
- Box 2: "Bukan target populasi inklusi" dengan catatan:
  - Syok/hipotensi saat admisi IGD (teridentifikasi oleh penginput data)
  - Non-ACS (kesalahan koding diagnosis)
  - Operasi CABG
  - Pulang paksa
  - Data tidak lengkap
- Simpan sebagai figures/strobe_flowchart_v6.png

### B. Update narrative P145
Sesuai penjelasan di atas — data dari query RME, eksklusi berdasarkan expertise penginput data, dll.

### C. Update narrative dr_TM/dr_NP (paragraph after P147)
Bahwa dr_TM dan dr_NP adalah DPJP, variasi praktik klinis menyebabkan echo tidak dilakukan saat admisi, SOAP minimalis.

### D. Ganti image di DOCX
Hapus image25 lama, ganti dengan v6.

Working directory: /home/linuxmint/thesis-clean

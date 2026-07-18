#!/usr/bin/env python3
"""Apply the v6 flowchart and corrected cohort narrative to TESIS_FINAL.docx."""

from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree


ROOT = Path(__file__).resolve().parents[1]
DOCX = ROOT / "TESIS_FINAL.docx"
IMAGE = ROOT / "figures" / "strobe_flowchart_v6.png"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"w": W, "a": A, "r": R}

REPLACEMENTS = {
    64: ("Penelitian dilaksanakan di Pusat Jantung Terpadu RSUP Dr. Wahidin Sudirohusodo, "
         "Makassar. Data pasien bersumber dari database Rekam Medis Elektronik (RME) rumah sakit "
         "melalui query diagnosis keluar STEMI (infark miokard transmural) dan NSTEMI (infark "
         "miokard subendokard) untuk periode 1 Januari 2024 hingga 31 Desember 2025."),
    144: ("Penelitian ini melibatkan 1.524 pasien dengan diagnosis STEMI dan NSTEMI yang dirawat "
          "di Pusat Jantung Terpadu RSUP Dr. Wahidin Sudirohusodo, Makassar, periode Januari 2024 "
          "hingga Desember 2025. Data bersumber dari database Rekam Medis Elektronik (RME) rumah "
          "sakit melalui query diagnosis keluar STEMI (infark miokard transmural) dan NSTEMI "
          "(infark miokard subendokard), kemudian diverifikasi melalui telaah rekam medis."),
    145: ("Dari 1.952 rekam pasien yang teridentifikasi melalui query RME, sebanyak 379 pasien "
          "dikeluarkan karena bukan target populasi inklusi. Eksklusi mencakup syok atau hipotensi "
          "saat admisi di IGD yang dikenali oleh penginput data berdasarkan keahlian klinis dalam "
          "menelaah rekam medis; diagnosis akhir non-SKA akibat ketidaktepatan koding diagnosis; "
          "tindakan CABG dalam episode perawatan yang sama; pulang atas permintaan sendiri; dan "
          "ketidaklengkapan data. Kasus Killip IV yang terlewat pada skrining awal dikroscek kembali; "
          "apabila terkonfirmasi telah mengalami syok saat admisi, kasus tersebut digabungkan ke "
          "kategori syok/hipotensi saat admisi. Setelah penyaringan awal, tersedia 1.573 pasien "
          "dengan data terstruktur."),
    146: ("Dari 1.573 pasien tersebut, 48 pasien tidak diikutsertakan pada tahap kendali mutu karena "
          "data ekokardiografi saat admisi (LVEF, TAPSE, atau LVOT VTI) dan/atau parameter "
          "laboratorium yang diperlukan tidak tersedia secara memadai dalam RME. Verifikasi ulang "
          "juga dilakukan terhadap catatan yang mengarah pada Killip IV agar kasus syok yang telah "
          "ada saat admisi diklasifikasikan bersama kategori syok/hipotensi saat admisi, bukan "
          "sebagai kategori eksklusi yang terpisah. Setelah tahap ini, 1.525 pasien memenuhi syarat "
          "untuk analisis lebih lanjut."),
    147: ("Pada pemeriksaan akhir, satu rekam yang terlewat pada penyaringan sebelumnya dikroscek "
          "kembali dan tidak diikutsertakan; bila Killip IV terkonfirmasi telah ada saat admisi, "
          "rekam tersebut diklasifikasikan dalam kategori syok/hipotensi saat admisi. Dengan "
          "demikian, kohort analisis akhir berjumlah 1.524 pasien dengan 115 kasus mortalitas "
          "in-hospital (7,5%). Karakteristik dasar populasi penelitian disajikan pada Tabel 3.1."),
    148: ("Sebagian pasien yang diterima di IGD berada di bawah tanggung jawab dr_TM dan dr_NP "
          "sebagai dokter penanggung jawab pelayanan (DPJP). Terdapat variasi praktik klinis di IGD, "
          "di mana tidak semua DPJP secara rutin melakukan POCUS ekokardiografi bedside pada saat "
          "admisi, dan kelengkapan dokumentasi SOAP bervariasi antar klinisi. Pada pasien yang "
          "ditangani oleh kedua DPJP tersebut, ekokardiografi bedside saat admisi tidak dilakukan "
          "dan dokumentasi SOAP IGD relatif lebih ringkas, sehingga parameter ekokardiografi yang "
          "diperlukan tidak tersedia dalam RME dan pasien dieksklusi sejak tahap penyaringan awal."),
}


def replace_paragraph_text(paragraph, text):
    nodes = paragraph.xpath(".//w:t", namespaces=NS)
    if not nodes:
        run = etree.SubElement(paragraph, f"{{{W}}}r")
        node = etree.SubElement(run, f"{{{W}}}t")
        nodes = [node]
    nodes[0].text = text
    for node in nodes[1:]:
        node.text = ""


with ZipFile(DOCX, "r") as source:
    entries = {name: source.read(name) for name in source.namelist()}

document = etree.fromstring(entries["word/document.xml"])
relationships = etree.fromstring(entries["word/_rels/document.xml.rels"])
paragraphs = document.xpath("//w:body/w:p", namespaces=NS)

for index, text in REPLACEMENTS.items():
    replace_paragraph_text(paragraphs[index], text)

# Keep a single flowchart drawing and explicitly point it to media/image25.png.
first_blip = paragraphs[137].xpath(".//a:blip", namespaces=NS)[0]
first_rid = first_blip.get(f"{{{R}}}embed")
for drawing in paragraphs[138].xpath(".//w:drawing", namespaces=NS):
    drawing.getparent().remove(drawing)
for rel in relationships:
    if rel.get("Id") == first_rid:
        rel.set("Target", "media/image25.png")
        break

entries["word/document.xml"] = etree.tostring(document, xml_declaration=True,
                                                encoding="UTF-8", standalone="yes")
entries["word/_rels/document.xml.rels"] = etree.tostring(
    relationships, xml_declaration=True, encoding="UTF-8", standalone="yes")
entries["word/media/image25.png"] = IMAGE.read_bytes()

with NamedTemporaryFile(dir=ROOT, suffix=".docx", delete=False) as handle:
    temp = Path(handle.name)
try:
    with ZipFile(temp, "w", ZIP_DEFLATED) as target:
        for name, data in entries.items():
            target.writestr(name, data)
    temp.replace(DOCX)
finally:
    temp.unlink(missing_ok=True)

print(DOCX)

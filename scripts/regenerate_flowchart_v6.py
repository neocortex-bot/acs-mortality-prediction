#!/usr/bin/env python3
"""Regenerate the corrected STROBE patient-selection flowchart (v6)."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "figures" / "strobe_flowchart_v6.png"


def box(ax, x, y, w, h, edge, title, subtitle=None, title_color="#172033"):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=2.2,
        edgecolor=edge,
        facecolor="#ffffff",
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h * 0.63, title, ha="center", va="center",
            fontsize=14.2, fontweight="bold", color=title_color)
    if subtitle:
        ax.text(x + w / 2, y + h * 0.31, subtitle, ha="center", va="center",
                fontsize=9.4, color="#536174", linespacing=1.45)


def arrow(ax, y1, y2):
    ax.add_patch(FancyArrowPatch((0.5, y1), (0.5, y2), arrowstyle="-|>",
                                 mutation_scale=15, linewidth=1.8,
                                 color="#718096"))


fig, ax = plt.subplots(figsize=(8, 10), dpi=180)
fig.patch.set_facecolor("white")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

blue = "#2b6cb0"
red = "#c53030"
gold = "#b7791f"

box(ax, 0.12, 0.86, 0.76, 0.105, blue,
    "Database RME — 1.952 pasien",
    "Query diagnosis keluar: STEMI (transmural) dan NSTEMI (subendokard)\nJanuari 2024–Desember 2025")
arrow(ax, 0.86, 0.82)

box(ax, 0.12, 0.60, 0.76, 0.215, red,
    "Bukan target populasi inklusi — 379 pasien",
    "• Syok/hipotensi saat admisi IGD (teridentifikasi oleh penginput data)\n"
    "• Non-ACS (kesalahan koding diagnosis)\n"
    "• Operasi CABG dalam episode perawatan yang sama\n"
    "• Pulang atas permintaan sendiri (pulang paksa)\n"
    "• Data tidak lengkap")
arrow(ax, 0.60, 0.56)

box(ax, 0.12, 0.46, 0.76, 0.095, blue,
    "Data terstruktur — 1.573 pasien",
    "Rekam medis yang memenuhi penyaringan awal")
arrow(ax, 0.46, 0.42)

box(ax, 0.12, 0.27, 0.76, 0.145, red,
    "Dieksklusi pada kendali mutu — 48 pasien",
    "Data ekokardiografi admisi dan/atau parameter laboratorium tidak lengkap\n"
    "Kasus Killip IV dikroscek dan digabungkan ke kategori syok saat admisi")
arrow(ax, 0.27, 0.23)

box(ax, 0.12, 0.14, 0.76, 0.085, blue,
    "Memenuhi syarat analisis — 1.525 pasien",
    "Satu rekam dikroscek kembali pada pemeriksaan akhir")
arrow(ax, 0.14, 0.10)

box(ax, 0.12, 0.015, 0.76, 0.08, gold,
    "Kohort analisis akhir — 1.524 pasien",
    "115 kematian in-hospital (7,5%)")

plt.tight_layout(pad=0.4)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUTPUT, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(OUTPUT)

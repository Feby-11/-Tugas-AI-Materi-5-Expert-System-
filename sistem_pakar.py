"""Sistem pakar diagnosis printer - Forward Chaining (FC).
Pakai: python sistem_pakar.py                -> mode interaktif
       python sistem_pakar.py --jawab a,b    -> mode otomatis (id fakta 'ya' dipisah koma)
"""
import json
import sys

KB_FILE = "kb_printer.json"


def muat_kb(path=KB_FILE):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def tanya_fakta(kb):
    """Tanya setiap fakta dasar ke user, kembalikan himpunan fakta 'ya'."""
    memori = set()
    print("Jawab y (ya) atau t (tidak):\n")
    for i, (fid, teks) in enumerate(kb["fakta"].items(), 1):
        while True:
            j = input(f"{i}. {teks} (y/t) > ").strip().lower()
            if j in ("y", "t"):
                break
        if j == "y":
            memori.add(fid)
    return memori


def terpenuhi(aturan, memori):
    kondisi = [k in memori for k in aturan["if"]]
    return all(kondisi) if aturan["mode"] == "dan" else any(kondisi)


def forward_chaining(kb, memori):
    """Jalankan aturan berulang sampai tidak ada fakta baru. Return (memori, log)."""
    log = []
    siklus = 0
    ada_baru = True
    while ada_baru:
        ada_baru = False
        siklus += 1
        for a in kb["aturan"]:
            if a["then"] not in memori and terpenuhi(a, memori):
                memori.add(a["then"])
                log.append((siklus, a))
                ada_baru = True
    return memori, log


def tampilkan(kb, memori_awal, memori, log):
    print("\n" + "=" * 60)
    print(kb["judul"])
    print("=" * 60)
    print("Fakta awal:", ", ".join(sorted(memori_awal)) or "(tidak ada)")
    print()
    for siklus, a in log:
        sambung = f" {a['mode'].upper()} ".join(a["if"])
        print(f"Siklus {siklus}: {a['id']} -> {a['then']}   [IF {sambung}]")
    if not log:
        print("Tidak ada aturan yang terpenuhi.")

    print("\nKesimpulan:")
    hasil = [a for _, a in log if a["then"] in kb["kesimpulan"]]
    if not hasil:
        print("  Tidak ada kesimpulan. Fakta yang dimasukkan belum cukup untuk aturan mana pun.")
    for a in hasil:
        print(f"  - {a['then']}: {kb['kesimpulan'][a['then']]}")
        print(f"    Alasan: aturan {a['id']}, sumber: {', '.join(a['sumber'])}")
    print("\nCatatan: aturan berasal dari artikel HP & Box.co.uk (lihat README) dan hanya")
    print("mencakup masalah umum printer rumahan. Ini bukan keputusan akhir teknisi.")


def main():
    kb = muat_kb()
    print(f"Sistem Pakar: {kb['judul']}")
    print(f"Batas: {kb['batas']}\n")
    if "--jawab" in sys.argv:
        ids = sys.argv[sys.argv.index("--jawab") + 1]
        memori = {x for x in ids.split(",") if x}
    else:
        memori = tanya_fakta(kb)
    awal = set(memori)
    memori, log = forward_chaining(kb, memori)
    tampilkan(kb, awal, memori, log)


if __name__ == "__main__":
    main()
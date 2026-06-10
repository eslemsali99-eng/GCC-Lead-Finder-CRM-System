"""Master CSV'yi Google Sheet'e ilk yükleme. Bir kez çalıştır.
   Kullanım: python upload_to_sheet.py ../GCC_TUM_KISILER.csv
"""
import sys, csv, os
from sheets_client import open_sheet, HEADER, existing_keys, append_rows

def main(csv_path):
    ws, cfg = open_sheet()
    # başlık yoksa ekle
    if not ws.get_all_values():
        ws.append_row(HEADER)
    keys = existing_keys(ws)
    rows = []
    with open(csv_path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            key = (r["Isim"].strip().lower(), r["Sirket"].strip().lower())
            if key in keys:
                continue
            keys.add(key)
            rows.append([r.get("No",""), r.get("Kategori",""), r.get("Sektor",""), r.get("Isim",""),
                         r.get("Rol",""), r.get("Sirket",""), r.get("Ulke",""), r.get("Yanit Olasiligi",""),
                         r.get("LinkedIn",""), r.get("Sirket Web",""), r.get("Is E-postasi",""),
                         r.get("Telefon",""), r.get("Instagram",""), r.get("Not",""), r.get("Kaynak",""),
                         "ilk-yukleme", ""])
    append_rows(ws, rows)
    print(f"{len(rows)} satir Google Sheet'e yuklendi.")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../GCC_TUM_KISILER.csv")

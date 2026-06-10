"""LinkedIn GÜVENLİ yarı-otomatik outreach kuyruğu hazırlar (gönderim YOK — sen onayla-gönder).
Google Sheet'ten henüz iletişime geçilmemiş kişileri alır, günlük limitle (varsayılan 25)
kişiselleştirilmiş DAVET NOTU + KABUL SONRASI MESAJ (WhatsApp'lı) üretir, CSV'ye yazar.
Sen CSV'yi açar, her profili LinkedIn'de açıp daveti/mesajı yapıştırırsın. Ban riski ~0.

NOT: Otomatik gönderim bilerek yapılmadı. LinkedIn ToS ihlali + hesap ban riski yüzünden
gönderimi insan (sen) yapar. Davetler arasına gün içine yay, limiti aşma.
"""
import os, csv, datetime
from sheets_client import open_sheet

HERE = os.path.dirname(__file__)
TITLES = ("h.h.","hh","hrh","he","sheikh","sheikha","dr.","dr","eng.","eng","mr.","ms.","prince","prof.","prof")

def first_name(full):
    parts = [p for p in full.replace(".", " ").split() if p.strip()]
    for p in parts:
        if p.lower() not in TITLES and len(p) > 1:
            return p
    return parts[0] if parts else "there"

def main():
    ws, cfg = open_sheet()
    li = cfg["linkedin"]
    limit = int(li.get("daily_invite_limit", 25))
    rows = ws.get_all_records()
    head = ws.row_values(1)
    try:
        col_status = head.index("LinkedIn Durum") + 1
    except ValueError:
        col_status = None

    queued, out = 0, []
    for i, r in enumerate(rows, start=2):
        if queued >= limit:
            break
        if str(r.get("LinkedIn Durum","")).strip():
            continue  # zaten kuyruğa alınmış/iletişime geçilmiş
        linkedin = str(r.get("LinkedIn","")).strip()
        if not linkedin or "search/results" in linkedin and "/in/" not in linkedin:
            # arama linki: yine de kullanılabilir ama profil linki tercih
            pass
        if not linkedin:
            continue
        fn = first_name(str(r.get("Isim","")))
        invite = li["invite_note"].format(first=fn)[:300]
        followup = li["followup_message"].format(first=fn, whatsapp=li["whatsapp"])
        out.append({
            "Isim": r.get("Isim",""), "Sirket": r.get("Sirket",""), "Rol": r.get("Rol",""),
            "Yanit Olasiligi": r.get("Yanit Olasiligi",""), "LinkedIn": linkedin,
            "DAVET_NOTU (<=300)": invite, "KABUL_SONRASI_MESAJ (WhatsApp'li)": followup
        })
        if col_status:
            ws.update_cell(i, col_status, "kuyrukta " + datetime.date.today().isoformat())
        queued += 1

    fname = os.path.join(HERE, f"linkedin_gonderim_kuyrugu_{datetime.date.today().isoformat()}.csv")
    if out:
        with open(fname, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
            w.writeheader(); w.writerows(out)
    print(f"{queued} kisi bugunku kuyruga alindi -> {fname}")
    print("Sen yap: her LinkedIn linkini ac, DAVET_NOTU ile baglan; kabul edince KABUL_SONRASI_MESAJ'i gonder.")
    print("Gun icine yay, limiti asma. Cevap gelirse 'LinkedIn Durum' sutununu elle guncelle.")

if __name__ == "__main__":
    main()

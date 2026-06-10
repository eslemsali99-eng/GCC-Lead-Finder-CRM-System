"""LinkedIn güvenli yarı-otomatik kuyruk — YEREL (Google gerekmez).
Temiz master listeden (../GCC_TUM_KISILER.csv) en yüksek yanıtlı + LinkedIn'i olan kişileri seçer,
günlük limitle kişiye özel DAVET + KABUL SONRASI MESAJ (WhatsApp + arama no'lu) üretir.
Tekrarları contacted.json'da tutar. Gönderimi SEN yaparsın.
"""
import csv, os, json, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "GCC_TUM_KISILER.csv")
CONTACTED = os.path.join(HERE, "contacted.json")
TITLES = ("h.h.","hh","hrh","he","sheikh","sheikha","dr.","dr","eng.","eng","mr.","ms.","prince","prof.","prof")

def first_name(full):
    for p in [x for x in full.replace(".", " ").split() if x.strip()]:
        if p.lower() not in TITLES and len(p) > 1:
            return p
    return "there"

def main():
    cfg = json.load(open(os.path.join(HERE, "config.json"), encoding="utf-8"))["linkedin"]
    limit = int(cfg.get("daily_invite_limit", 25))
    wa, call = cfg.get("whatsapp",""), cfg.get("call_number","")
    done = set(json.load(open(CONTACTED, encoding="utf-8"))) if os.path.exists(CONTACTED) else set()

    rows = list(csv.DictReader(open(SRC, encoding="utf-8-sig")))
    # öncelik: profil URL'li (/in/) + Yüksek yanıt önce
    def rank(r):
        li = r.get("LinkedIn","")
        return (0 if "/in/" in li else 1, 0 if str(r.get("Yanit Olasiligi","")).startswith("Yüksek") else 1)
    rows.sort(key=rank)

    out, queued = [], 0
    for r in rows:
        if queued >= limit: break
        li = r.get("LinkedIn","").strip()
        key = (r.get("Isim","").strip().lower(), r.get("Sirket","").strip().lower())
        if not li or list(key) in [list(k) for k in done] or "|".join(key) in done:
            continue
        fn = first_name(r.get("Isim",""))
        invite = cfg["invite_note"].format(first=fn)[:300]
        followup = cfg["followup_message"].format(first=fn, whatsapp=wa, call=call)
        out.append({"Isim": r["Isim"], "Sirket": r["Sirket"], "Rol": r.get("Rol",""),
                    "Yanit": r.get("Yanit Olasiligi",""), "LinkedIn": li,
                    "DAVET_NOTU": invite, "KABUL_SONRASI_MESAJ": followup})
        done.add("|".join(key)); queued += 1

    json.dump(sorted(done), open(CONTACTED, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    fname = os.path.join(HERE, f"linkedin_gonderim_kuyrugu_{datetime.date.today().isoformat()}.csv")
    if out:
        with open(fname, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    print(f"{queued} kisi kuyruga alindi -> {os.path.basename(fname)}")
    try:
        import build_crm; build_crm.main()  # CRM'i tazele
    except Exception as e:
        print(f"[crm] {e}")
    return fname, out

if __name__ == "__main__":
    main()

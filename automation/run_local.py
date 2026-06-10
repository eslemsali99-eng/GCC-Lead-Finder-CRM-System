"""Günlük bot — KİMLİKSİZ yerel mod. Google API gerekmez.
Kuyruktan şirketleri kazır, yeni kişileri ../GCC_TUM_KISILER_LIVE.csv'ye ekler.
Sen bu dosyayı Google Drive (Desktop) klasörüne koyarsan Drive otomatik senkronlar.
Kullanım: python3 run_local.py [max_sirket]
"""
import csv, json, os, sys, time, warnings, datetime
warnings.filterwarnings("ignore")
import requests
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
# Çıktı: yerel proje klasörü. (iz360 eski/ölü hesap — kullanılmıyor.)
# Kişisel Gmail'i Drive Desktop'a eklersen buradaki yolu o klasöre çevirip oto-senkron yaparız.
LIVE = os.path.join(HERE, "..", "GCC_TUM_KISILER_LIVE.csv")
SEED = os.path.join(HERE, "..", "GCC_TUM_KISILER.csv")
QUEUE = os.path.join(HERE, "company_queue.json")

# extract fonksiyonunu daily_research'ten al (sheets importunu stub'la)
import types
sys.modules["sheets_client"] = types.SimpleNamespace(open_sheet=lambda:(None,{}),
                                                      existing_keys=lambda ws:set(),
                                                      append_rows=lambda ws,r:None)
spec = importlib.util.spec_from_file_location("dr", os.path.join(HERE, "daily_research.py"))
dr = importlib.util.module_from_spec(spec); spec.loader.exec_module(dr)

HEADER = ["No","Kategori","Sektor","Isim","Rol","Sirket","Ulke","Yanit Olasiligi","LinkedIn",
          "Sirket Web","Is E-postasi","Telefon","Instagram","Not","Kaynak"]

def ensure_live():
    if not os.path.exists(LIVE) and os.path.exists(SEED):
        with open(SEED, encoding="utf-8-sig") as a, open(LIVE, "w", newline="", encoding="utf-8-sig") as b:
            b.write(a.read())

def keys_and_count():
    keys, n = set(), 0
    if os.path.exists(LIVE):
        with open(LIVE, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                keys.add((r.get("Isim","").strip().lower(), r.get("Sirket","").strip().lower())); n += 1
    return keys, n

def main(max_n=10):
    ensure_live()
    keys, start_n = keys_and_count()
    q = json.load(open(QUEUE, encoding="utf-8"))
    pending = [c for c in q["companies"] if not c.get("done") and c.get("url")][:max_n]
    new = []
    for c in pending:
        try:
            r = requests.get(c["url"], timeout=15, headers={"User-Agent":"Mozilla/5.0 (lead-research)"})
            if r.status_code != 200:
                print(f"[atla] {c['name']} HTTP {r.status_code}"); c["done"]=True; continue
            ppl = dr.extract(r.text, c.get("sector",""), c.get("country",""), c["name"], c["url"])
            added = 0
            for name, role in ppl:
                k = (name.strip().lower(), c["name"].strip().lower())
                if k in keys: continue
                keys.add(k)
                new.append(["", "Borsa C-Suite (bot)", c.get("sector",""), name, role, c["name"],
                            c.get("country",""), "review", "", c["url"], "", "", "",
                            "BOT - Kaynak'tan dogrula", c["url"]])
                added += 1
            print(f"[ok] {c['name']}: +{added}")
            c["done"]=True; time.sleep(2)
        except Exception as e:
            print(f"[hata] {c['name']}: {e}"); c["done"]=True
    # ekle (kuyruk scraper'i)
    write_header = not os.path.exists(LIVE)
    with open(LIVE, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if write_header: w.writerow(HEADER)
        w.writerows(new)
    json.dump(q, open(QUEUE,"w",encoding="utf-8"), ensure_ascii=False, indent=2)

    # Wikidata kesif motoru — yenilenebilir $0 kaynak. Her turda en fazla 25 yeni kisi ekler.
    wiki_added = []
    try:
        import wikidata_discover
        wiki_added = wikidata_discover.merge_into_live(max_new=25)
    except Exception as e:
        print(f"[wikidata] {e}")

    total_new = len(new) + len(wiki_added)
    _, end_n = keys_and_count()
    remaining = sum(1 for x in q["companies"] if not x.get("done") and x.get("url"))
    print(f"\nBITTI ({datetime.date.today()}): +{total_new} yeni kisi (scraper {len(new)}, wikidata {len(wiki_added)}). Toplam {end_n}. Dosya: {os.path.basename(LIVE)}. Maliyet: $0.")
    # Telegram raporu
    try:
        from telegram_report import send_report
        ornek = [f"{n} — {r}" for (_,_,_,n,r,*_) in new[:3]]
        ornek += [f"{row[3]} — {row[4]} ({row[5]})" for row in wiki_added[:3]]  # wikidata: Isim—Rol (Sirket)
        lines = [f"Bugün eklenen yeni kişi: *{total_new}* (scraper {len(new)}, wikidata {len(wiki_added)})",
                 f"Toplam liste: *{end_n}* kişi",
                 f"Kuyrukta kalan şirket: {remaining}",
                 "Maliyet: $0 (LLM yok)"]
        if ornek:
            lines.append("Örnekler: " + "; ".join(ornek))
        lines.append("Not: yeni kişiler 'review' — LinkedIn'e almadan Kaynak'tan doğrula.")
        send_report("Günlük GCC Lead Araştırması", lines)
    except Exception as e:
        print(f"[telegram] {e}")
    # E-posta zenginlestirme (varsayilan KAPALI; config'de enabled+hunter_api_key ile acilir)
    try:
        import email_enrich; email_enrich.main()
    except Exception as e:
        print(f"[mail] {e}")
    # LinkedIn kabul takibi (Gmail bildirimlerinden) -> accepted.json'i tazele
    try:
        import linkedin_accept_check; linkedin_accept_check.main()
    except Exception as e:
        print(f"[kabul] {e}")
    try:
        import build_crm; build_crm.main()  # CRM + canli Sheet'i tazele
    except Exception as e:
        print(f"[crm] {e}")
    # Web CRM verisini tazele (GitHub Pages docs/data.json)
    try:
        import export_web; export_web.main()
    except Exception as e:
        print(f"[web] {e}")

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 10)

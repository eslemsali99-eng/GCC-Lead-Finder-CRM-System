"""Wikidata kesif motoru — SIFIR maliyet, yenilenebilir gercek veri.
GCC (Korfez) ulkelerindeki sirketlerin CEO / Baskan / Kurucularini Wikidata'dan ceker.
Statik JSON API (JS sorunu yok), gercek & yapilandirilmis veri.

Akis:
  - fetch_all(): 6 ulke x 3 rol = hafif SPARQL sorgulari, benzersiz kisi listesi.
    Sonucu wikidata_cache.json'a yazar. Cache 20 saatten genc ise yeniden sorgulamaz
    (Wikidata'ya nazik ol; veri yavas degisir).
  - merge_into_live(max_new): cache'ten LIVE csv'de OLMAYAN kisileri en fazla max_new kadar ekler.
    Her turda biraz daha eklenir -> liste surekli buyur. Tum kume yakalaninca dogal olarak yavaslar.

run_local.py her tetiklenisinde merge_into_live cagrilir.
"""
import csv, json, os, datetime, time, urllib.request, urllib.parse, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
LIVE = os.path.join(HERE, "..", "GCC_TUM_KISILER_LIVE.csv")
CACHE = os.path.join(HERE, "wikidata_cache.json")
UA = "GCC-LeadResearch/1.0 (eslemsali99@gmail.com)"
ENDPOINT = "https://query.wikidata.org/sparql"

# GCC ulkeleri: QID -> okunur ad
COUNTRIES = {
    "Q851": "Saudi Arabia", "Q878": "United Arab Emirates", "Q846": "Qatar",
    "Q817": "Kuwait", "Q398": "Bahrain", "Q842": "Oman",
}
# rol property -> etiket
ROLES = {"P169": "CEO", "P488": "Chairman", "P112": "Founder"}
HEADER = ["No","Kategori","Sektor","Isim","Rol","Sirket","Ulke","Yanit Olasiligi","LinkedIn",
          "Sirket Web","Is E-postasi","Telefon","Instagram","Not","Kaynak"]


def _query(sparql, retries=3):
    """Tek SPARQL istegi. 429 (rate-limit) / 504 (timeout) durumunda bekleyip tekrar dener."""
    url = ENDPOINT + "?" + urllib.parse.urlencode({"query": sparql, "format": "json"})
    last = None
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(url, headers={"User-Agent": UA,
                                                   "Accept": "application/sparql-results+json"})
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)["results"]["bindings"]
        except urllib.error.HTTPError as e:
            last = e
            wait = 65 if e.code == 429 else 10  # 429: dakika basi limit -> 65s bekle
            print(f"[wikidata] HTTP {e.code}, deneme {attempt}/{retries}, {wait}s bekle...")
            if attempt < retries:
                time.sleep(wait)
        except Exception as e:
            last = e; print(f"[wikidata] hata: {e}")
            if attempt < retries:
                time.sleep(10)
    raise last


def _li_search(name, company):
    q = urllib.parse.quote(f"{name} {company}")
    return f"https://www.linkedin.com/search/results/people/?keywords={q}"


def fetch_all(force=False):
    """Tum GCC CEO/Baskan/Kuruculari Wikidata'dan ceker. Cache 20 saatten genc ise onu doner."""
    if not force and os.path.exists(CACHE):
        try:
            c = json.load(open(CACHE, encoding="utf-8"))
            age_h = (datetime.datetime.now().timestamp() - c.get("ts", 0)) / 3600
            if age_h < 20 and c.get("people"):
                return c["people"]
        except Exception:
            pass
    # Ulke x rol basina HAFIF sorgu (UNION/birlesik sorgu WDQS'te timeout veriyor).
    # 6 ulke x 3 rol = 18 hafif sorgu; her biri hizli doner. 429 (1 req/min) gelirse _query bekler.
    seen, people, ok_queries = set(), [], 0
    for qid, cname in COUNTRIES.items():
        for prop, role in ROLES.items():
            sparql = f"""
SELECT DISTINCT ?personLabel ?companyLabel ?industryLabel WHERE {{
  ?company wdt:P17 wd:{qid} ; wdt:{prop} ?person .
  ?person wdt:P31 wd:Q5 .
  OPTIONAL {{ ?company wdt:P452 ?industry . }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}} LIMIT 600"""
            try:
                rows = _query(sparql)
                ok_queries += 1
            except Exception as e:
                print(f"[wikidata] {cname}/{role} atlandi: {e}")
                continue
            for b in rows:
                name = b.get("personLabel", {}).get("value", "").strip()
                comp = b.get("companyLabel", {}).get("value", "").strip()
                if not name or not comp or name.startswith("Q") or comp.startswith("Q"):
                    continue
                key = (name.lower(), comp.lower())
                if key in seen:
                    continue
                seen.add(key)
                people.append({"isim": name, "rol": role, "sirket": comp, "ulke": cname,
                               "sektor": b.get("industryLabel", {}).get("value", "").strip()})
            time.sleep(2)  # normalde hizli; 429 olursa _query zaten 65s bekler
    if not people:   # tum sorgular coktu -> iyi cache'i EZME
        print(f"[wikidata] 0 sonuc ({ok_queries}/18 sorgu basarili), cache degismedi.")
        if os.path.exists(CACHE):
            return json.load(open(CACHE, encoding="utf-8")).get("people", [])
        return []
    # Kismi basari da olsa cache'i guncelle (en az yarisi geldiyse), yoksa eskiyi kaybetme
    if ok_queries >= 9 or not os.path.exists(CACHE):
        json.dump({"ts": datetime.datetime.now().timestamp(), "people": people},
                  open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"[wikidata] kesif: {len(people)} benzersiz kisi ({ok_queries}/18 sorgu, cache yenilendi).")
        return people
    else:
        old = json.load(open(CACHE, encoding="utf-8")).get("people", [])
        print(f"[wikidata] kismi ({ok_queries}/18) — yeni {len(people)} ama eski cache ({len(old)}) korunuyor.")
        return old if len(old) > len(people) else people


def _live_keys():
    keys = set()
    if os.path.exists(LIVE):
        with open(LIVE, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                keys.add((r.get("Isim", "").strip().lower(), r.get("Sirket", "").strip().lower()))
    return keys


def merge_into_live(max_new=25):
    """Cache'ten LIVE'da olmayanlardan en fazla max_new kisi ekler. Eklenen kisi sayisini doner."""
    people = fetch_all()
    keys = _live_keys()
    added = []
    for p in people:
        if len(added) >= max_new:
            break
        key = (p["isim"].lower(), p["sirket"].lower())
        if key in keys:
            continue
        keys.add(key)
        added.append([
            "", "Wikidata kesif (bot)", p["sektor"], p["isim"], p["rol"], p["sirket"], p["ulke"],
            "review", _li_search(p["isim"], p["sirket"]), "", "", "", "",
            "BOT - Wikidata; unvani/iletisimi dogrula", "wikidata",
        ])
    if added:
        write_header = not os.path.exists(LIVE)
        with open(LIVE, "a", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            if write_header:
                w.writerow(HEADER)
            w.writerows(added)
    print(f"[wikidata] LIVE'a eklenen yeni kisi: {len(added)} (havuzda {len(people)} kisi).")
    return added


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    merge_into_live(n)

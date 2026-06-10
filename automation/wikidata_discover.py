"""Wikidata kesif motoru v2 — SIFIR maliyet, cok-kaynakli, ulke-dengeli.
GCC (Korfez) ulkelerindeki GUCLU ISIMLERI yakalar:
  - Sirket CEO / Baskan / Kurucu / Yonetim Kurulu Uyesi
  - Meslek-bazli (sirkete bagli OLMAYAN): is insani, girisimci, yatirimci, banker
    -> kraliyet/yatirimci/aile ofisi gibi "guclu isimler + onlara erisimi olanlar".
Statik JSON API (JS sorunu yok), gercek & yapilandirilmis veri.

Akis:
  - fetch_all(): 6 ulke x 5 sorgu turu = hafif SPARQL sorgulari. Cache 20 saat.
  - merge_into_live(max_new): ULKE-DENGELI ekler (round-robin) -> Suudi baskinligi kirilir,
    her ulkeden duzenli buyur. run_local.py her turda cagrilir.
"""
import csv, json, os, datetime, time, urllib.request, urllib.parse, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
LIVE = os.path.join(HERE, "..", "GCC_TUM_KISILER_LIVE.csv")
CACHE = os.path.join(HERE, "wikidata_cache.json")
UA = "GCC-LeadResearch/1.0 (eslemsali99@gmail.com)"
ENDPOINT = "https://query.wikidata.org/sparql"

COUNTRIES = {
    "Q851": "Suudi Arabistan", "Q878": "BAE", "Q846": "Katar",
    "Q817": "Kuveyt", "Q398": "Bahreyn", "Q842": "Umman",
}
# sirket-rol sorgulari: property -> rol etiketi
COMPANY_ROLES = {"P169": "CEO", "P488": "Chairman", "P112": "Founder", "P3320": "Board Member"}
# meslek-bazli: occupation QID -> rol etiketi (sirkete bagli olmayan guclu isimler)
OCCUPATIONS = {"Q43845": "Businessperson", "Q131524": "Entrepreneur",
               "Q1751530": "Investor", "Q806798": "Banker"}
HEADER = ["No","Kategori","Sektor","Isim","Rol","Sirket","Ulke","Yanit Olasiligi","LinkedIn",
          "Sirket Web","Is E-postasi","Telefon","Instagram","Not","Kaynak"]


def _query(sparql, retries=3):
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
            wait = 65 if e.code == 429 else 10
            print(f"[wikidata] HTTP {e.code}, deneme {attempt}/{retries}, {wait}s bekle...")
            if attempt < retries:
                time.sleep(wait)
        except Exception as e:
            last = e; print(f"[wikidata] hata: {e}")
            if attempt < retries:
                time.sleep(10)
    raise last


def _li_search(name, company):
    q = urllib.parse.quote(f"{name} {company}".strip())
    return f"https://www.linkedin.com/search/results/people/?keywords={q}"


def _company_role_query(qid, prop):
    return f"""
SELECT DISTINCT ?personLabel ?companyLabel ?industryLabel WHERE {{
  ?company wdt:P17 wd:{qid} ; wdt:{prop} ?person .
  ?person wdt:P31 wd:Q5 .
  OPTIONAL {{ ?company wdt:P452 ?industry . }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}} LIMIT 600"""


def _occupation_query(qid):
    occ = " ".join(f"wd:{o}" for o in OCCUPATIONS)
    return f"""
SELECT DISTINCT ?personLabel ?occLabel ?companyLabel WHERE {{
  ?person wdt:P27 wd:{qid} ; wdt:P106 ?occ . VALUES ?occ {{ {occ} }}
  ?person wdt:P31 wd:Q5 .
  OPTIONAL {{ ?person wdt:P108 ?company . }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}} LIMIT 600"""


def fetch_all(force=False):
    if not force and os.path.exists(CACHE):
        try:
            c = json.load(open(CACHE, encoding="utf-8"))
            age_h = (datetime.datetime.now().timestamp() - c.get("ts", 0)) / 3600
            if age_h < 20 and c.get("people"):
                return c["people"]
        except Exception:
            pass
    seen, people, ok, total = set(), [], 0, 0
    for qid, cname in COUNTRIES.items():
        # 1) sirket-rol sorgulari
        for prop, role in COMPANY_ROLES.items():
            total += 1
            try:
                rows = _query(_company_role_query(qid, prop)); ok += 1
            except Exception as e:
                print(f"[wikidata] {cname}/{role} atlandi: {e}"); continue
            for b in rows:
                name = b.get("personLabel", {}).get("value", "").strip()
                comp = b.get("companyLabel", {}).get("value", "").strip()
                if not name or not comp or name.startswith("Q") or comp.startswith("Q"):
                    continue
                key = (name.lower(), comp.lower())
                if key in seen: continue
                seen.add(key)
                people.append({"isim": name, "rol": role, "sirket": comp, "ulke": cname,
                               "sektor": b.get("industryLabel", {}).get("value", "").strip()})
            time.sleep(2)
        # 2) meslek-bazli sorgu (sirkete bagli olmayan guclu isimler)
        total += 1
        try:
            rows = _query(_occupation_query(qid)); ok += 1
        except Exception as e:
            print(f"[wikidata] {cname}/meslek atlandi: {e}"); rows = []
        for b in rows:
            name = b.get("personLabel", {}).get("value", "").strip()
            if not name or name.startswith("Q"): continue
            comp = b.get("companyLabel", {}).get("value", "").strip()
            if comp.startswith("Q"): comp = ""
            role = b.get("occLabel", {}).get("value", "").strip().title() or "Businessperson"
            key = (name.lower(), comp.lower())
            if key in seen: continue
            seen.add(key)
            people.append({"isim": name, "rol": role, "sirket": comp, "ulke": cname, "sektor": ""})
        time.sleep(2)
    if not people:
        print(f"[wikidata] 0 sonuc ({ok}/{total} sorgu), cache degismedi.")
        if os.path.exists(CACHE):
            return json.load(open(CACHE, encoding="utf-8")).get("people", [])
        return []
    if ok >= total // 2 or not os.path.exists(CACHE):
        json.dump({"ts": datetime.datetime.now().timestamp(), "people": people},
                  open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"[wikidata] kesif: {len(people)} benzersiz kisi ({ok}/{total} sorgu, cache yenilendi).")
        return people
    old = json.load(open(CACHE, encoding="utf-8")).get("people", [])
    print(f"[wikidata] kismi ({ok}/{total}) — eski cache ({len(old)}) korundu.")
    return old if len(old) > len(people) else people


def _live_keys():
    keys = set()
    if os.path.exists(LIVE):
        with open(LIVE, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                keys.add((r.get("Isim", "").strip().lower(), r.get("Sirket", "").strip().lower()))
    return keys


def merge_into_live(max_new=25):
    """ULKE-DENGELI ekleme: her ulkeden sirayla (round-robin) yeni kisi al -> dengeli buyur."""
    people = fetch_all()
    keys = _live_keys()
    # ulkeye gore yeni (LIVE'da olmayan) adaylari grupla
    by_country = {c: [] for c in COUNTRIES.values()}
    for p in people:
        key = (p["isim"].lower(), p["sirket"].lower())
        if key in keys: continue
        if p["ulke"] in by_country:
            by_country[p["ulke"]].append(p)
    # round-robin: sirayla her ulkeden 1'er al
    added, idx = [], {c: 0 for c in by_country}
    order = list(COUNTRIES.values())
    while len(added) < max_new:
        progressed = False
        for c in order:
            if len(added) >= max_new: break
            lst = by_country[c]
            while idx[c] < len(lst):
                p = lst[idx[c]]; idx[c] += 1
                key = (p["isim"].lower(), p["sirket"].lower())
                if key in keys: continue
                keys.add(key)
                added.append([
                    "", "Wikidata kesif (bot)", p["sektor"], p["isim"], p["rol"], p["sirket"], p["ulke"],
                    "review", _li_search(p["isim"], p["sirket"]), "", "", "", "",
                    "BOT - Wikidata; unvani/iletisimi dogrula", "wikidata",
                ])
                progressed = True
                break
        if not progressed:
            break
    if added:
        write_header = not os.path.exists(LIVE)
        with open(LIVE, "a", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            if write_header: w.writerow(HEADER)
            w.writerows(added)
    from collections import Counter
    dist = dict(Counter(r[6] for r in added))
    print(f"[wikidata] LIVE'a eklenen: {len(added)} (havuz {len(people)}). Ulke dagilimi: {dist}")
    return added


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    merge_into_live(n)

"""Lead verisini web CRM için docs/data.json'a döker (GitHub Pages bunu okur).
LIVE csv + contacted.json (istek gönderilen) + accepted.json (kabul eden) -> tek JSON.
Manuel Durum/Not web tarafında localStorage'da tutulur (statik site). run_local sonunda çağrılır.
"""
import csv, os, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
LIVE = os.path.join(HERE, "..", "GCC_TUM_KISILER_LIVE.csv")
CONTACTED = os.path.join(HERE, "contacted.json")
ACCEPTED = os.path.join(HERE, "accepted.json")
OUT = os.path.join(HERE, "..", "docs", "data.json")

def _load(path):
    if not os.path.exists(path): return {}
    d = json.load(open(path, encoding="utf-8"))
    return d if isinstance(d, dict) else {k: "" for k in d}

def main():
    contacted, accepted = _load(CONTACTED), _load(ACCEPTED)
    leads = []
    with open(LIVE, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            isim, sirket = r.get("Isim","").strip(), r.get("Sirket","").strip()
            if not isim: continue
            key = f"{isim.lower()}|{sirket.lower()}"
            kabul = "accepted" if key in accepted else ("sent" if key in contacted else "none")
            leads.append({
                "isim": isim, "rol": r.get("Rol","").strip(), "sirket": sirket,
                "ulke": r.get("Ulke","").strip(), "sektor": r.get("Sektor","").strip(),
                "email": r.get("Is E-postasi","").strip(), "linkedin": r.get("LinkedIn","").strip(),
                "web": r.get("Sirket Web","").strip(), "kaynak": r.get("Kaynak","").strip(),
                "kabul": kabul,
                "son_temas": accepted.get(key) or contacted.get(key) or "",
            })
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    payload = {
        "updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total": len(leads),
        "leads": leads,
    }
    json.dump(payload, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[web] docs/data.json yazildi: {len(leads)} lead.")

if __name__ == "__main__":
    main()

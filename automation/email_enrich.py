"""E-posta zenginleştirme — lead'lere doğrulanmış iş e-postası bulur.
VARSAYILAN KAPALI (masraf/risk yok). Açmak için config.json:
  "email_enrich": { "enabled": true, "hunter_api_key": "...", "max_per_run": 25, "min_score": 50 }
Hunter.io Email Finder kullanır (ücretsiz 25/ay): şirket + ad/soyad -> doğrulanmış e-posta + skor.
Anahtar yoksa ve free_guess=false ise hiçbir şey yapmaz.
free_guess=true: anahtarsız Clearbit domain + desen tahmini (DOĞRULANMAMIŞ, gerçek gönderim için önerilmez).
run_local.py içinde build_crm'den ÖNCE çağrılır (gated).
"""
import csv, os, json, time, re, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
LIVE = os.path.join(HERE, "..", "GCC_TUM_KISILER_LIVE.csv")
HEADER = ["No","Kategori","Sektor","Isim","Rol","Sirket","Ulke","Yanit Olasiligi","LinkedIn",
          "Sirket Web","Is E-postasi","Telefon","Instagram","Not","Kaynak"]

def _cfg():
    p = os.path.join(HERE, "config.json")
    c = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    return c.get("email_enrich", {})

def _domain_from_url(url):
    m = re.search(r"https?://([^/]+)", url or "")
    return m.group(1).replace("www.", "").strip().lower() if m else ""

def _clearbit_domain(name):
    try:
        url = "https://autocomplete.clearbit.com/v1/companies/suggest?" + urllib.parse.urlencode({"query": name})
        d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=15))
        return d[0]["domain"] if d else ""
    except Exception:
        return ""

def _split_name(full):
    toks = [t for t in re.split(r"\s+", (full or "").strip()) if t and t.lower() not in
            ("dr","eng","mr","ms","sheikh","sheikha","hh","hrh","he","prince","prof")]
    if len(toks) < 2: return (toks[0] if toks else ""), ""
    return toks[0], toks[-1]

def _hunter(first, last, domain, company, key):
    params = {"first_name": first, "last_name": last, "api_key": key}
    if domain: params["domain"] = domain
    elif company: params["company"] = company
    else: return "", 0
    try:
        url = "https://api.hunter.io/v2/email-finder?" + urllib.parse.urlencode(params)
        d = json.load(urllib.request.urlopen(url, timeout=20))["data"]
        return (d.get("email") or ""), int(d.get("score") or 0)
    except Exception as e:
        print(f"[mail] hunter hata: {e}"); return "", 0

def main():
    cfg = _cfg()
    if not cfg.get("enabled"):
        print("[mail] email_enrich kapalı (config: enabled=false) — atlandı."); return
    key = (cfg.get("hunter_api_key") or "").strip()
    free_guess = bool(cfg.get("free_guess"))
    if not key and not free_guess:
        print("[mail] hunter_api_key yok ve free_guess kapalı — atlandı."); return
    max_n = int(cfg.get("max_per_run", 25)); min_score = int(cfg.get("min_score", 50))
    if not os.path.exists(LIVE):
        print("[mail] LIVE yok."); return
    rows = list(csv.DictReader(open(LIVE, encoding="utf-8-sig")))
    enriched = 0
    for r in rows:
        if enriched >= max_n: break
        if (r.get("Is E-postasi") or "").strip(): continue
        first, last = _split_name(r.get("Isim", ""))
        if not first or not last: continue
        company, web = r.get("Sirket", ""), r.get("Sirket Web", "")
        domain = _domain_from_url(web)
        if key:
            email, score = _hunter(first, last, domain, company, key)
            if email and score >= min_score:
                r["Is E-postasi"] = email
                r["Not"] = (r.get("Not", "") + f" | mail:Hunter%{score}").strip(" |"); enriched += 1
            time.sleep(1)
        elif free_guess:
            if not domain: domain = _clearbit_domain(company); time.sleep(1)
            if domain:
                r["Is E-postasi"] = f"{first}.{last}@{domain}".lower()
                r["Not"] = (r.get("Not", "") + " | mail:tahmini(dogrulanmamis)").strip(" |"); enriched += 1
    if enriched:
        with open(LIVE, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=HEADER)
            w.writeheader()
            for r in rows:
                w.writerow({h: r.get(h, "") for h in HEADER})
    print(f"[mail] {enriched} lead'e e-posta eklendi ({'Hunter dogrulamali' if key else 'tahmini'}).")

if __name__ == "__main__":
    main()

"""Günlük otomatik araştırma botu — SIFIR maliyet (LLM yok, sadece kazıma).
Her gün company_queue.json'dan sıradaki şirketleri işler, kurul/yönetim sayfasından
Başkan/CEO/CFO adaylarını çıkarır, tekrarsız şekilde Google Sheet'e 'review' olarak ekler.
launchd ile günlük çalışır. Harcama limiti: use_llm=false iken maliyet $0; sayfa limiti var.
"""
import json, os, re, sys, time
import requests
from bs4 import BeautifulSoup
from sheets_client import open_sheet, existing_keys, append_rows

HERE = os.path.dirname(__file__)
QUEUE = os.path.join(HERE, "company_queue.json")
TITLE_RE = re.compile(r"\b(Chief Executive|CEO|Chief Financial|CFO|Chairman|Chairperson|"
                      r"Managing Director|Group CEO|President|General Manager|"
                      r"Vice Chairman|Chief Operating|COO)\b", re.I)
NAME_RE = re.compile(r"^(?:H\.?H\.?|HRH|HE|Sheikh|Sheikha|Dr\.?|Eng\.?|Mr\.?|Ms\.?|Prince|Prof\.?)?\s*"
                     r"([A-Z][a-zA-Z'’\-]+(?:\s+[A-Z][a-zA-Z'’\-\.]+){1,4})")

def load_queue():
    with open(QUEUE, encoding="utf-8") as f:
        return json.load(f)

def save_queue(q):
    with open(QUEUE, "w", encoding="utf-8") as f:
        json.dump(q, f, ensure_ascii=False, indent=2)

# İsim OLMAYAN kelimeler — bunlardan biri geçerse aday elenir (sayfa başlığı/çöp).
STOP = set("""message review team our list principal officer officers board management profile
vision statement connect report group holding company bank insurance medical executive chief
president chairman chairperson director ceo cfo coo cto cmo the and of for investor relations
leadership about news careers home contact overview corporate governance committee members
member meet welcome story values mission strategy services products solutions careconnect
care health digital finance financial operations operating vice deputy senior head unit
read more view all our-team annual report awards society general authority public national
international holdings sector division department office founder owner""".split())

def looks_like_name(cand, company):
    toks = [t for t in re.split(r"\s+", cand.strip()) if t]
    if not (2 <= len(toks) <= 4):
        return False
    comp_toks = set(re.sub(r"[^a-zA-Z ]", " ", company).lower().split())
    for t in toks:
        tl = t.lower().strip(".'’-")
        if not tl or tl in STOP or tl in comp_toks:
            return False
        if any(ch.isdigit() for ch in t):
            return False
        if not re.match(r"^[A-Z][a-z]+([’'\-][A-Za-z]+)?\.?$", t.strip("’'")):
            return False  # her token gerçek isim gibi (Baş harf büyük, gerisi küçük)
    return True

def extract(html, sector, country, company, src):
    """Sayfadan 'isim + unvan' çıkarır. Sıkı filtre: sadece gerçek kişi adına benzeyenler."""
    soup = BeautifulSoup(html, "html.parser")
    for s in soup(["script", "style", "nav", "footer"]):
        s.extract()
    found, seen = [], set()
    for el in soup.find_all(text=TITLE_RE):
        block = " ".join(el.parent.get_text(" ", strip=True).split())[:160]
        m = TITLE_RE.search(block)
        role = m.group(0) if m else ""
        cands = []
        nm = NAME_RE.search(block.replace(role, " "))
        if nm:
            cands.append(nm.group(1).strip())
        sib = el.parent.find_previous(["strong", "h2", "h3", "h4", "h5", "b"])
        if sib:
            nm2 = NAME_RE.search(sib.get_text(" ", strip=True))
            if nm2:
                cands.append(nm2.group(1).strip())
        for cand in cands:
            if looks_like_name(cand, company) and cand.lower() not in seen:
                seen.add(cand.lower())
                found.append((cand, role))
                break
    return found

def main():
    ws, cfg = open_sheet()
    dr = cfg.get("daily_research", {})
    if dr.get("use_llm", False) and dr.get("daily_llm_usd_cap", 0) <= 0:
        print("use_llm=true ama cap=0 -> LLM kapali kabul edildi, sadece kazima.")
    max_n = int(dr.get("max_companies_per_day", 30))
    timeout = int(dr.get("request_timeout_sec", 15))
    q = load_queue()
    keys = existing_keys(ws)
    pending = [c for c in q["companies"] if not c.get("done") and c.get("url")]
    batch = pending[:max_n]
    new_rows, processed = [], 0
    for c in batch:
        try:
            r = requests.get(c["url"], timeout=timeout,
                             headers={"User-Agent": "Mozilla/5.0 (lead-research)"})
            if r.status_code != 200:
                print(f"[atla] {c['name']} HTTP {r.status_code}")
                c["done"] = True; continue
            people = extract(r.text, c.get("sector",""), c.get("country",""), c["name"], c["url"])
            added = 0
            for name, role in people:
                key = (name.strip().lower(), c["name"].strip().lower())
                if key in keys:
                    continue
                keys.add(key)
                new_rows.append(["", "Borsa Kurul/C-Suite (bot)", c.get("sector",""), name, role,
                                 c["name"], c.get("country",""), "review", "", "", "", "", "",
                                 "BOT — unvani Kaynak'tan dogrula", c["url"], "gunluk-bot", ""])
                added += 1
            print(f"[ok] {c['name']}: {added} yeni aday")
            c["done"] = True; processed += 1
            time.sleep(2)
        except Exception as e:
            print(f"[hata] {c['name']}: {e}")
            c["done"] = True
    append_rows(ws, new_rows)
    save_queue(q)
    remaining = sum(1 for x in q["companies"] if not x.get("done") and x.get("url"))
    print(f"BITTI: {processed} sirket islendi, {len(new_rows)} yeni kisi eklendi. Kuyrukta {remaining} sirket kaldi. Maliyet: $0 (LLM yok).")

if __name__ == "__main__":
    main()

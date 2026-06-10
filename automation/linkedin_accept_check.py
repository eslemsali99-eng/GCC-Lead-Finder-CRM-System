"""LinkedIn 'isteğinizi kabul etti' bildirimlerini Gmail'den okuyup accepted.json'a yazar.
GÜVENLİ: LinkedIn'e hiç dokunmaz, sadece kendi Gmail kutunu IMAP ile okur -> ban riski yok, cloud'da çalışır.

LinkedIn kabul e-postası örnek konuları:
  "Ahmed Al Maktoum accepted your invitation to connect"
  "Ahmed Al Maktoum, davetinizi kabul etti"
  "You are now connected to Ahmed Al Maktoum"
Bu isimleri lead listesindeki kişilerle eşleştirir, eşleşeni accepted.json'a (key=isim|sirket) işaretler.

config.json -> "linkedin_accept": {"gmail_user": "...", "gmail_app_password": "...", "since_days": 180}
gmail_app_password BOŞSA hiçbir şey yapmaz (atlar). App password: myaccount.google.com/apppasswords
"""
import csv, os, json, re, imaplib, email, datetime
from email.header import decode_header

HERE = os.path.dirname(os.path.abspath(__file__))
LIVE = os.path.join(HERE, "..", "GCC_TUM_KISILER_LIVE.csv")
ACCEPTED = os.path.join(HERE, "accepted.json")

# Konudan ismi çıkaran kalıplar (EN + TR + 'now connected')
PATTERNS = [
    re.compile(r"^(.+?)\s+accepted your invitation", re.I),
    re.compile(r"^(.+?),?\s+davetini(?:zi)?\s+kabul etti", re.I),
    re.compile(r"you(?:'re| are)? now connected (?:to|with)\s+(.+?)\s*$", re.I),
    re.compile(r"^(.+?)\s+ile (?:artık )?bağlantı kurdunuz", re.I),
]

def _decode(s):
    if not s: return ""
    out = []
    for part, enc in decode_header(s):
        out.append(part.decode(enc or "utf-8", "ignore") if isinstance(part, bytes) else part)
    return "".join(out)

def _norm(n):
    return re.sub(r"\s+", " ", re.sub(r"[^a-zçğıöşü ]", "", (n or "").lower())).strip()

def _lead_index():
    """normalize(isim) -> [ (isim, sirket) keyleri ]"""
    idx = {}
    if os.path.exists(LIVE):
        with open(LIVE, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                isim, sirket = r.get("Isim","").strip(), r.get("Sirket","").strip()
                if not isim: continue
                idx.setdefault(_norm(isim), []).append(f"{isim.lower()}|{sirket.lower()}")
    return idx

def main():
    cfg_path = os.path.join(HERE, "config.json")
    cfg = json.load(open(cfg_path, encoding="utf-8")) if os.path.exists(cfg_path) else {}
    la = cfg.get("linkedin_accept", {})
    user, pw = la.get("gmail_user","").strip(), la.get("gmail_app_password","").strip()
    if not user or not pw:
        print("[kabul] gmail_app_password bos — LinkedIn kabul takibi atlandi (app password ekle).")
        return
    since_days = int(la.get("since_days", 180))
    since = (datetime.date.today() - datetime.timedelta(days=since_days)).strftime("%d-%b-%Y")

    leads = _lead_index()
    accepted = json.load(open(ACCEPTED, encoding="utf-8")) if os.path.exists(ACCEPTED) else []
    if isinstance(accepted, list):
        accepted = {k: "" for k in accepted}
    before = len(accepted)

    try:
        M = imaplib.IMAP4_SSL("imap.gmail.com")
        M.login(user, pw)
        M.select("INBOX")
        # LinkedIn'den gelen, son N gunluk e-postalar
        typ, data = M.search(None, f'(FROM "linkedin.com" SINCE {since})')
        ids = data[0].split()
        matched_names = 0
        for mid in ids:
            typ, msg_data = M.fetch(mid, "(BODY.PEEK[HEADER.FIELDS (SUBJECT)])")
            if typ != "OK" or not msg_data or not msg_data[0]: continue
            raw = msg_data[0][1]
            subj = _decode(email.message_from_bytes(raw)["Subject"] if isinstance(raw, bytes) else "")
            name = None
            for pat in PATTERNS:
                m = pat.search(subj)
                if m: name = m.group(1).strip(" .,"); break
            if not name: continue
            keys = leads.get(_norm(name))
            if not keys: continue
            matched_names += 1
            today = datetime.date.today().isoformat()
            for k in keys:
                accepted.setdefault(k, today)
        M.logout()
    except Exception as e:
        print(f"[kabul] IMAP hata: {e}")
        return

    json.dump(accepted, open(ACCEPTED, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"[kabul] {len(ids)} LinkedIn e-postasi tarandi, {matched_names} kabul eslesti. "
          f"accepted.json: {before} -> {len(accepted)} kisi.")

if __name__ == "__main__":
    main()

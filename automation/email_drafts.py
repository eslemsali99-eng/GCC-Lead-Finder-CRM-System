"""E-posta TASLAK hazırlayıcı — GÖNDERME YOK (otonom kör gönderim bilerek yapılmadı).
Sadece elimizdeki GERÇEK kurumsal adreslere (info@, IR@) kişiselleştirilmiş taslak üretir.
Her taslak için tek-tık 'mailto' linki verir: tıkla → Mail uygulaman dolu açılır → SEN gönder.
Tahmini/uydurma adres KULLANMAZ (domain itibarını ve KVKK'yı korur).
"""
import csv, os, json, datetime, urllib.parse, re
HERE = os.path.dirname(os.path.abspath(__file__))

def wa_link(number, prefill):
    digits = re.sub(r"\D", "", number or "")
    return f"https://wa.me/{digits}?text=" + urllib.parse.quote(prefill or "")
SRC = os.path.join(HERE, "..", "GCC_TUM_KISILER.csv")
TITLES = ("h.h.","hh","hrh","he","sheikh","sheikha","dr.","dr","eng.","eng","mr.","ms.","prince","prof.","prof")

def first_name(full):
    for p in [x for x in full.replace(".", " ").split() if x.strip()]:
        if p.lower() not in TITLES and len(p) > 1:
            return p
    return "there"

def main():
    c = json.load(open(os.path.join(HERE,"config.json"), encoding="utf-8"))
    ec, li = c["email"], c["linkedin"]
    wa, call = li.get("whatsapp",""), li.get("call_number","")
    walink = wa_link(wa, ec.get("wa_prefill", "Hi, I'd like more info."))
    rows = [r for r in csv.DictReader(open(SRC, encoding="utf-8-sig")) if r.get("Is E-postasi","").strip()]
    out = []
    for r in rows:
        isim, sirket = r["Isim"].strip(), r["Sirket"].strip()
        to = r["Is E-postasi"].strip()
        first = first_name(isim)
        subject = ec["subject"].format(first=first, company=sirket)
        body = ec["body"].format(first=first, company=sirket, wa_link=walink, call=call, from_name=ec["from_name"])
        mailto = "mailto:" + urllib.parse.quote(to) + "?" + urllib.parse.urlencode(
            {"subject": subject, "body": body}, quote_via=urllib.parse.quote)
        out.append({"to": to, "isim": isim, "sirket": sirket, "subject": subject,
                    "mailto_link": mailto, "body": body})
    # CSV + tek-tık HTML
    today = datetime.date.today().isoformat()
    csvp = os.path.join(HERE, f"email_taslaklari_{today}.csv")
    with open(csvp,"w",newline="",encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["to","isim","sirket","subject","mailto_link","body"]); w.writeheader(); w.writerows(out)
    htmlp = os.path.join(HERE, f"email_gonder_{today}.html")
    with open(htmlp,"w",encoding="utf-8") as f:
        f.write("<html><head><meta charset='utf-8'><style>body{font-family:Arial;max-width:760px;margin:30px auto}"
                ".c{border:1px solid #ddd;border-radius:8px;padding:14px;margin:12px 0}"
                "a.b{background:#1F3864;color:#fff;padding:8px 14px;border-radius:6px;text-decoration:none}"
                "pre{white-space:pre-wrap;color:#333;background:#f7f7f7;padding:10px;border-radius:6px}</style></head><body>")
        f.write(f"<h2>E-posta Taslakları — {today} ({len(out)} kişi)</h2>"
                "<p>Her butona tıkla → Mail uygulaman dolu açılır → <b>sen Gönder'e bas</b>. Otomatik gönderim yok.</p>")
        for o in out:
            f.write(f"<div class='c'><b>{o['isim']}</b> — {o['sirket']}<br>"
                    f"<small>{o['to']}</small><br><br>"
                    f"<a class='b' href=\"{o['mailto_link']}\">✉️ Mail'i aç (sen gönder)</a>"
                    f"<pre>{o['subject']}\n\n{o['body']}</pre></div>")
        f.write("</body></html>")
    print(f"{len(out)} taslak hazir.\n  CSV: {os.path.basename(csvp)}\n  Tek-tik sayfa: {os.path.basename(htmlp)}")
    try:
        from telegram_report import send_report
        send_report("E-posta Taslakları Hazır", [
            f"{len(out)} kişiye kişiselleştirilmiş taslak hazır (gerçek kurumsal adresler).",
            "Tek-tık HTML sayfasından aç → sen gönder. Otomatik gönderim yok (güvenlik).",
            "Tahmini adres kullanılmadı — domain itibarın korunuyor."])
    except Exception as e:
        print(f"[telegram] {e}")
    return htmlp

if __name__ == "__main__":
    main()

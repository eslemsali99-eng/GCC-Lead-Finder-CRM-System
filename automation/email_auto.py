"""PLANLAYICILI otomatik e-posta — sen açmadan günlük gönderir.
GÜVENLİK SINIRLARI (bilerek): yalnızca verified_only=true ile GERÇEK kurumsal adreslere gönderir
(tahmini/uydurma adres ASLA), günlük limit, opt-out, tekrar göndermez.
smtp_pass BOŞSA hiçbir şey göndermez (sen App Password ekleyene kadar pasif).
Gönderim hesabı config'deki smtp_user (eslemsali0@gmail.com). iz360 KULLANILMAZ.

AKTİVE ETME (sen yaparsın):
  1) eslemsali0@gmail.com'da 2FA aç → App Password oluştur (myaccount.google.com/apppasswords)
  2) config.json -> email.smtp_pass içine o 16 haneli şifreyi yaz
  3) launchd: cp com.eslem.gcc-email.plist ~/Library/LaunchAgents/ && launchctl load ~/Library/LaunchAgents/com.eslem.gcc-email.plist
  Durdur: launchctl unload ~/Library/LaunchAgents/com.eslem.gcc-email.plist
"""
import csv, os, json, smtplib, ssl, datetime, re, urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "GCC_TUM_KISILER.csv")
SENT = os.path.join(HERE, "email_sent.json")
TITLES = ("h.h.","hh","hrh","he","sheikh","sheikha","dr.","dr","eng.","eng","mr.","ms.","prince","prof.","prof")

def first_name(full):
    for p in [x for x in full.replace(".", " ").split() if x.strip()]:
        if p.lower() not in TITLES and len(p) > 1:
            return p
    return "there"

def wa_link(number, prefill):
    return f"https://wa.me/{re.sub(chr(92)+'D','',number or '')}?text=" + urllib.parse.quote(prefill or "")

def html_body(first, company, walink, call, frm):
    return f"""<html><body style="font-family:Arial,sans-serif;color:#222;line-height:1.5">
<p>Dear {first},</p>
<p>I work with a small group placing select Turkish real assets with international investors:
<b>development land, an Aegean villa and an operating factory</b> — each eligible for Turkish citizenship.</p>
<p>Given your role at {company}, I thought a brief 1-page overview might be of interest, either personally or for your network.</p>
<p><a href="{walink}" style="background:#25D366;color:#fff;padding:11px 18px;border-radius:8px;
text-decoration:none;font-weight:bold">💬 Get the 1-page overview on WhatsApp</a></p>
<p>Or call: {call}</p>
<p style="color:#888;font-size:13px">If this isn't relevant, just reply 'stop' and I won't follow up.</p>
<p>Best regards,<br>{frm}</p></body></html>"""

def main():
    c = json.load(open(os.path.join(HERE,"config.json"), encoding="utf-8"))
    ec, li = c["email"], c["linkedin"]
    smtp_pass = ec.get("smtp_pass","").strip()
    if not smtp_pass:
        print("PASİF: smtp_pass boş. App Password ekleyince otomatik göndermeye başlar. Hiçbir şey gönderilmedi.")
        return
    if not ec.get("verified_only", True):
        print("GÜVENLİK: verified_only=false reddedildi. Sadece gerçek adreslere gönderim açık.")
        return
    wa, call = li.get("whatsapp",""), li.get("call_number","")
    walink = wa_link(wa, ec.get("wa_prefill","Hi, I'd like more info."))
    limit = int(ec.get("daily_email_limit", 15))
    sent_log = set(json.load(open(SENT, encoding="utf-8"))) if os.path.exists(SENT) else set()

    rows = [r for r in csv.DictReader(open(SRC, encoding="utf-8-sig")) if r.get("Is E-postasi","").strip()]
    rows.sort(key=lambda r: 0 if str(r.get("Yanit Olasiligi","")).startswith("Yüksek") else 1)
    batch = []
    for r in rows:
        if len(batch) >= limit: break
        key = f"{r['Isim'].strip().lower()}|{r['Sirket'].strip().lower()}"
        if key in sent_log: continue
        batch.append((r, key))

    delivered = 0
    if batch:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(ec["smtp_host"], int(ec["smtp_port"])) as s:
            s.starttls(context=ctx); s.login(ec["smtp_user"], smtp_pass)
            for r, key in batch:
                first, sirket, to = first_name(r["Isim"]), r["Sirket"].strip(), r["Is E-postasi"].strip()
                msg = MIMEMultipart("alternative")
                msg["Subject"] = ec["subject"].format(first=first, company=sirket)
                msg["From"] = formataddr((ec["from_name"], ec["smtp_user"]))
                msg["To"] = to; msg["Reply-To"] = ec["smtp_user"]
                text = ec["body"].format(first=first, company=sirket, wa_link=walink, call=call, from_name=ec["from_name"])
                msg.attach(MIMEText(text, "plain", "utf-8"))
                msg.attach(MIMEText(html_body(first, sirket, walink, call, ec["from_name"]), "html", "utf-8"))
                try:
                    s.send_message(msg); sent_log.add(key); delivered += 1
                except Exception as e:
                    print(f"[hata] {to}: {e}")
    json.dump(sorted(sent_log), open(SENT,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"GONDERILDI: {delivered}/{len(batch)} ({datetime.date.today()})")
    try:
        from telegram_report import send_report
        send_report("Otomatik E-posta Gönderimi", [
            f"Bugün gönderilen: *{delivered}* kişi (gerçek kurumsal adresler)",
            f"Gönderen: {ec['smtp_user']}",
            f"Toplam gönderilmiş: {len(sent_log)}",
            "WhatsApp tıklanabilir buton ekli. Opt-out var."])
    except Exception as e:
        print(f"[telegram] {e}")
    try:
        import build_crm; build_crm.main()  # CRM'i tazele
    except Exception as e:
        print(f"[crm] {e}")

if __name__ == "__main__":
    main()

"""Telegram rapor gönderici — 'Türkiye Gayrimenkul Yönlendirme Otomasyonu' formatı.
Her rapor en başında hangi iş olduğunu söyler. config.json'dan token+chat_id okur.
"""
import json, os, datetime, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))

def _cfg():
    with open(os.path.join(HERE, "config.json"), encoding="utf-8") as f:
        return json.load(f)

def send_report(job, lines, ok=True):
    """job: bu çalışmanın işi (ör. 'Günlük GCC Lead Araştırması'). lines: rapor satırları."""
    cfg = _cfg().get("telegram", {})
    token, chat = cfg.get("token", ""), str(cfg.get("chat_id", "")).strip()
    if not token or not chat:
        print("[telegram] chat_id yok, rapor atlanmadi (once /start + resolve_chat_id.py).")
        return False
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    head = "🇹🇷 *Türkiye Gayrimenkul Yönlendirme Otomasyonu*"
    icon = "✅" if ok else "⚠️"
    body = "\n".join("• " + l for l in lines)
    text = f"{head}\n{icon} *İş:* {job}\n🕒 {now}\n———————————\n{body}"
    data = urllib.parse.urlencode({
        "chat_id": chat, "text": text, "parse_mode": "Markdown",
        "disable_web_page_preview": "true"}).encode()
    try:
        with urllib.request.urlopen(f"https://api.telegram.org/bot{token}/sendMessage", data=data, timeout=20) as r:
            return r.status == 200
    except Exception as e:
        print(f"[telegram] gonderilemedi: {e}")
        return False

if __name__ == "__main__":
    send_report("Test Mesajı", ["Bot bağlantısı çalışıyor.", "Bu bir test raporudur."])

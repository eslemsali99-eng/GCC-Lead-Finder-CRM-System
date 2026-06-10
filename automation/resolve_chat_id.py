"""Telegram chat_id'yi bulup config.json'a yazar. ÖNCE bota /start gönder, sonra bunu çalıştır."""
import json, os, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.join(HERE, "config.json")

def main():
    cfg = json.load(open(CFG, encoding="utf-8"))
    token = cfg["telegram"]["token"]
    with urllib.request.urlopen(f"https://api.telegram.org/bot{token}/getUpdates", timeout=20) as r:
        data = json.load(r)
    chats = {}
    for u in data.get("result", []):
        msg = u.get("message") or u.get("my_chat_member") or {}
        ch = msg.get("chat") or {}
        if ch.get("id"):
            chats[ch["id"]] = ch.get("first_name") or ch.get("username") or str(ch["id"])
    if not chats:
        print("Henuz mesaj yok. t.me/otomasyonraporbot ac, START'a bas, tekrar calistir.")
        return
    cid = list(chats)[-1]
    cfg["telegram"]["chat_id"] = str(cid)
    json.dump(cfg, open(CFG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"chat_id bulundu ve kaydedildi: {cid} ({chats[cid]})")

if __name__ == "__main__":
    main()

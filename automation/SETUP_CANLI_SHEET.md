# Canlı Google Sheet CRM — 5 Dakikalık Kurulum (eslemsali99)

Amaç: **tek linkten, hep güncel** bir Google Sheet. Bot listeyi + son durumu oraya canlı yazar;
sen Durum/Yanıt/Not yazarsın, bot onları korur. (Ben senin Google hesabına giremediğim için bu
tek adımı sen yapacaksın — sonrası tamamen otomatik.)

## Adımlar
1. **eslemsali99** ile https://sheets.google.com → yeni boş E-Tablo aç. Adını "GCC CRM" koy.
   → **Bu E-Tablo senin kalıcı canlı CRM linkin olacak.** (Üstteki URL'yi sakla.)
2. Üst menü: **Uzantılar → Apps Script**.
3. Açılan editördeki tüm kodu sil. `apps_script.gs` dosyasının içeriğini **olduğu gibi yapıştır**, kaydet (💾).
4. Sağ üst **Dağıt (Deploy) → Yeni dağıtım → ⚙️ → Web uygulaması**:
   - "Şu kişi olarak çalıştır": **Ben (eslemsali99)**
   - "Erişimi olan": **Herkes (Anyone)**
   - **Dağıt**. İzin iste derse onayla. Çıkan **Web uygulaması URL'sini kopyala.**
5. O URL'yi `config.json` içindeki **`sheet_webapp_url`** alanına yapıştır, kaydet.

## Test
```bash
cd automation
python3 build_crm.py     # CRM'i kurar + canli Sheet'e gonderir
```
Google Sheet'ini aç → 263 kişi + durum sütunları dolmuş olmalı. Artık:
- Günlük bot her sabah yeni kişileri **otomatik** Sheet'e ekler.
- E-posta/LinkedIn gönderdikçe durum **otomatik** güncellenir.
- Sen **Genel Durum / Yanıt / Not** yazarsın → bot bir daha üzerine yazmaz.
- Tek link, hep canlı. İstediğine paylaşabilirsin (Paylaş → Bağlantı al).

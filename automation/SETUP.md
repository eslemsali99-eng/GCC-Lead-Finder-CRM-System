# Otomasyon Kurulumu — GCC Lead Sistemi

3 parça: (1) Google E-Tablo, (2) günlük ücretsiz araştırma botu, (3) güvenli LinkedIn outreach kuyruğu.
**Maliyet: $0** — bot LLM kullanmaz, sadece public sayfaları kazır. Google Sheets API ücretsiz.

---
## 0) Hazırlık
```bash
cd "/Users/eslemsali/Desktop/Claude Code Lead Finder/gcc-lead-finder/automation"
pip3 install -r requirements.txt
cp config.example.json config.json    # sonra config.json'u doldur
```

## 1) Google E-Tablo + service account (tek seferlik, ücretsiz)
1. https://console.cloud.google.com → yeni proje.
2. "APIs & Services" → **Google Sheets API**'yi etkinleştir.
3. "Credentials" → Create Credentials → **Service account** → oluştur.
4. Service account → Keys → Add Key → **JSON** indir → bu dosyayı `automation/service_account.json` olarak kaydet.
5. Google Drive'da yeni bir **Google E-Tablo** aç. URL'den ID'yi al:
   `https://docs.google.com/spreadsheets/d/`**`BU_KISIM_ID`**`/edit`
6. E-Tabloyu, service account'un e-postasıyla (JSON içindeki `client_email`) **Düzenleyen** olarak paylaş.
7. `config.json` içine `google_sheet_id` ve WhatsApp numaranı yaz.

## 2) Master listeyi E-Tabloya yükle (bir kez)
```bash
python3 upload_to_sheet.py ../GCC_TUM_KISILER.csv
```
252 kişi E-Tabloya gider. Artık canlı listen hazır.

## 3) Günlük botu kur (talimatın gerekmez)
```bash
cp com.eslem.gcc-daily.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.eslem.gcc-daily.plist
```
Her gün 09:00'da `company_queue.json`'dan ~30 şirketi kazır, yeni Başkan/CEO/CFO'ları
E-Tabloya **"review"** olarak ekler (sen `Kaynak`'tan teyit edip outreach'e alırsın).
- Durdurmak: `launchctl unload ~/Library/LaunchAgents/com.eslem.gcc-daily.plist`
- Elle test: `python3 daily_research.py`
- Kuyruk bitince `company_queue.json`'a yeni şirket ekle (gayrimenkul firması EKLEME).

## 4) LinkedIn — güvenli yarı-otomatik (gönderimi SEN yaparsın)
```bash
python3 linkedin_outreach.py
```
Günlük 25 kişilik `linkedin_gonderim_kuyrugu_TARIH.csv` üretir. İçinde her kişi için:
- **DAVET_NOTU** (≤300 karakter, kişiye özel)
- **KABUL_SONRASI_MESAJ** (WhatsApp numaranla)

Sen yaparsın: LinkedIn'i kendi tarayıcında aç → her profilin linkine git → **Connect** + daveti yapıştır →
kişi kabul edince **KABUL_SONRASI_MESAJ**'ı gönder. Cevap gelince E-Tabloda `LinkedIn Durum`'u güncelle.

### ⚠️ Neden otomatik gönderim yok
Otomatik davet/DM **LinkedIn sözleşmesini ihlal eder → hesap kalıcı ban riski.** Senin tüm stratejin
LinkedIn'e dayalı; hesabını kaybetmek = her şeyi kaybetmek. Bu yüzden:
- Günde **20-30 daveti aşma**, gün içine yay.
- WhatsApp'ı **ilk mesajda değil**, kabul sonrası 2. mesajda ver (config'de öyle ayarlı).
- İlk mesajda her zaman "reply stop" opt-out var (KVKK/GDPR + itibar).
- İstersen sonra Dripify/Waalaxy gibi "insan taklidi" bir araca bu CSV'yi besleyebilirsin.

## Güvenlik
`config.json` ve `service_account.json` gizli dosyalar — kimseyle paylaşma, git'e koyma.

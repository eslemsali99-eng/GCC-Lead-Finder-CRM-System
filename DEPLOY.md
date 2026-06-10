# Yayına Alma — 10 Dakika

Bu klasör zaten bir git deposu (`git init` yapıldı, ilk commit hazır). Aşağıdaki adımlarla
GitHub'a alıp 7/24 cloud'da çalıştır ve dashboard'u yayınla.

## 1) GitHub repo oluştur ve push'la
1. https://github.com/new → ad: `gulf-investor-crm` (veya istediğin) → **Private** (önerilir) → Create.
2. Terminalde (bu klasörde):
   ```bash
   cd ~/gcc-lead-finder
   git branch -M main
   git remote add origin https://github.com/<KULLANICI_ADIN>/gulf-investor-crm.git
   git push -u origin main
   ```

## 2) Gizli ayarları secret olarak ekle
`automation/config.json` GİZLİDİR ve repoya gitmez. Cloud botu onu bir secret'tan üretir.
1. Repo → **Settings → Secrets and variables → Actions → New repository secret**.
2. Name: **`CONFIG_JSON`**
3. Secret: `automation/config.json` dosyanın **tüm içeriğini** yapıştır.
   - İçinde olması gerekenler: `sheet_webapp_url` (canlı sheet), istersen telegram, ve
     LinkedIn kabul takibi için `linkedin_accept.gmail_user` + `gmail_app_password`.
4. Save.

> Gmail app password: myaccount.google.com/apppasswords (hesapta 2FA açık olmalı). Boş kalırsa
> kabul takibi otomatik atlanır, sistem yine çalışır.

## 3) Dashboard'u yayınla (GitHub Pages)
1. Repo → **Settings → Pages**.
2. Source: **Deploy from a branch** → Branch: **main** → Folder: **/docs** → Save.
3. ~1 dakika sonra adresin: `https://<KULLANICI_ADIN>.github.io/gulf-investor-crm/`
   → CV'ne koyabileceğin canlı link bu.

## 4) Botu ilk kez tetikle
Repo → **Actions → "GCC Lead Bot (7/24)" → Run workflow**.
- Her 3 saatte bir otomatik çalışır (laptop kapalıyken de).
- Her çalışmada: Wikidata'dan yeni lead + Gmail'den kabul + sheet + `docs/data.json` güncellenir,
  repoya geri yazılır → Pages otomatik yenilenir.

## 5) (Opsiyonel) Canlı Google Sheet'i yeni sütun düzenine geçir
Sütunları değiştirdik (Durum + Kabul Durumu eklendi, eski durum sütunları silindi). Sheet'in de
buna uyması için Apps Script'i bir kez yeniden dağıt:
1. Sheet → Uzantılar → Apps Script → tüm kodu sil → `automation/apps_script.gs` içeriğini yapıştır → kaydet.
2. Dağıt → Dağıtımları yönet → ✏️ → "Sürüm: Yeni sürüm" → Dağıt. (URL aynı kalır.)

## Yerel (laptop) bot — opsiyonel
Cloud kurulduktan sonra yerel launchd'a gerek yok. Kapatmak istersen:
```bash
launchctl unload ~/Library/LaunchAgents/com.eslem.gcc-daily.plist
```

## Yeni bir sohbette bu işe nasıl devam ederim?
Proje artık GitHub'da. Yeni bir Claude Code oturumunda:
```bash
git clone https://github.com/<KULLANICI_ADIN>/gulf-investor-crm.git
cd gulf-investor-crm
```
ve Claude'a "bu repo üzerinde çalış" de — tüm kod, dashboard ve bot burada. Cloud (GitHub Actions)
arka planda çalışmaya devam eder; sen sadece kodu değiştirip push'larsın.
```
```

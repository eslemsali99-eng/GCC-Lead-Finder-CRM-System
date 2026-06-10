# Gulf Investor CRM — GCC Lead Intelligence System

A self-updating, zero-cost CRM that discovers, tracks, and visualizes decision-makers
(founders, chairpersons, CEOs, CFOs) across the six Gulf (GCC) markets — Saudi Arabia,
UAE, Qatar, Kuwait, Bahrain, Oman.

**Live dashboard:** _(GitHub Pages — enable in Settings → Pages → `/docs`)_

## What it does

- **Discovers leads automatically** from Wikidata (CEO / Chairperson / Founder of GCC-based
  companies) — real, structured, public data. $0 cost, renewable source.
- **Tracks LinkedIn outreach** — marks who you've sent connection requests to and, by reading
  LinkedIn's "accepted your invitation" notification emails over IMAP, who accepted. No LinkedIn
  scraping, no ban risk.
- **Lives in two places:** a polished web dashboard (this repo, GitHub Pages) and an optional
  live Google Sheet (via an Apps Script web app) for spreadsheet-style manual editing.
- **Runs 7/24 in the cloud** via GitHub Actions (every 3 hours) — no laptop required.

## Architecture

```
GitHub Actions (cron, her 3 saatte bir)
   └─ automation/run_local.py
        ├─ wikidata_discover.py      → yeni lead keşfi (SPARQL, $0)
        ├─ linkedin_accept_check.py  → Gmail IMAP'tan "kabul etti" bildirimleri
        ├─ build_crm.py + push_to_sheet.py → canlı Google Sheet
        └─ export_web.py             → docs/data.json
   └─ commit & push → GitHub Pages otomatik yenilenir
```

Dashboard (`docs/`) bağımlılıksız vanilla JS — sadece `docs/data.json` okur.
Manuel durum/notlar tarayıcıda `localStorage`'da tutulur.

## Tech

Python (requests, BeautifulSoup, openpyxl) · Wikidata SPARQL · Google Apps Script ·
vanilla JS/CSS · GitHub Actions · GitHub Pages.

## Kurulum

Bkz. [DEPLOY.md](DEPLOY.md) — repo oluştur, `CONFIG_JSON` secret'ı ekle, Pages'i `/docs` yap.

## Maliyet

$0 — Wikidata, Gmail IMAP, GitHub Actions ve GitHub Pages hepsi ücretsiz katmanda.

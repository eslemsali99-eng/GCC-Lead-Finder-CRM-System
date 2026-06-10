/**
 * GCC Yatırımcı Lead Pipeline — Apify
 * --------------------------------------------------------------
 * SADECE PUBLIC iş verisi toplar. Bireysel pazarlamadan önce opt-out'lu ilk mesaj kuralına uy (KVKK/GDPR).
 *
 * Kurulum:
 *   npm init -y && npm i apify-client csv-writer
 *   export APIFY_TOKEN=apify_xxx          # kendi token'ın
 *   node apify_pipeline.js enrich         # mevcut domainleri zenginleştir (mail/telefon/sosyal)
 *   node apify_pipeline.js maps           # Google Maps'ten yeni hedef üret
 *   node apify_pipeline.js events         # etkinlik/konuşmacı sayfalarından isim+iletişim
 *   node apify_pipeline.js richlist       # Forbes ME / Arabian Business zengin & ödül listeleri
 *   node apify_pipeline.js news           # yatırım açıklayan kurucuları haberlerden yakala
 *   node apify_pipeline.js social         # Instagram bio/iletişim (marka & kişi hesapları)
 *
 * MALİYET KONTROL: Her komut MAX_ITEMS ile sınırlı. Apify panelinde aylık spending limit koy.
 * Önce küçük test et, sonucu gör, sonra büyüt. CRON KURMA — manuel tetikle.
 */

const { ApifyClient } = require('apify-client');
const { createObjectCsvWriter } = require('csv-writer');

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });
const MAX_ITEMS = Number(process.env.MAX_ITEMS || 10); // test için düşük; güvendikten sonra artır

// 'GCC Hedef Kisiler' sekmesindeki kişilerin şirket domainleri
const TARGET_DOMAINS = [
  'damacproperties.com', 'eaglehills.com', 'habtoor.com', 'lulugroupinternational.com',
  'alfuttaim.com', 'burjeelholdings.com', 'gemseducation.com', 'joyalukkas.com',
  'rpgroup.com', 'sharafgroup.com', 'alfaisalholding.com', 'almana.com', 'kanoo.com',
  'aig.com.bh', 'gfh.com', 'mbholdingco.com', 'zubaircorp.com', 'saudbahwangroup.com',
  'kingdom.com.sa', 'hmg.com', 'muhaidib.com', 'nahdi.sa', 'mbc.net', 'alfozan.com',
  'daralarkan.com', 'alj.com', 'othaimmarkets.com', 'olayan.com', 'almarai.com',
  'alrajhibank.com.sa', 'corral.se', 'alghanim.com', 'alshaya.com', 'zain.com',
  'jazeeraairways.com',
];

// Zengin & ödül listeleri (richlist) — isim + şirket çıkarımı
const RICHLIST_URLS = [
  'https://www.forbesmiddleeast.com/lists',
  'https://www.arabianbusiness.com/lists',
  'https://gulfbusiness.com/lists/100-most-powerful-arabs-2025/',
];

// Yatırım haberi sorguları (news)
const NEWS_QUERIES = [
  'GCC investor buys property abroad', 'UAE family office acquisition 2025',
  'Saudi billionaire investment Turkey', 'Gulf chairman expansion announcement',
];

// Instagram hedefleri (social) — marka/kişi public hesapları
const IG_PROFILES = ['damacofficial', 'lulufoundation', 'alhabtoorgroup'];

// Google Maps sorguları — bölgedeki şirketi olan = zenginlik sinyali
const MAPS_QUERIES = [
  'family office Dubai', 'real estate investment company Abu Dhabi',
  'investment migration Dubai', 'wealth management Riyadh',
  'property investment company Doha', 'holding company Sharjah',
];

// Etkinlik/konuşmacı sayfaları (public) — isim + bağlam çıkarımı
const EVENT_URLS = [
  'https://fii-institute.org', 'https://aimcongress.com',
  'https://cityscapeglobal.com', 'https://investmentmigration.org',
];

async function writeCsv(name, rows) {
  if (!rows.length) { console.log(`[${name}] kayıt yok`); return; }
  const header = Object.keys(rows[0]).map((k) => ({ id: k, title: k }));
  await createObjectCsvWriter({ path: `out_${name}.csv`, header }).writeRecords(rows);
  console.log(`[${name}] ${rows.length} kayıt -> out_${name}.csv`);
}

// 1) Mevcut domainleri zenginleştir: e-posta, telefon, sosyal (Instagram/LinkedIn/WhatsApp link)
async function enrich() {
  const run = await client.actor('vdrmota/contact-info-scraper').call({
    startUrls: TARGET_DOMAINS.map((d) => ({ url: `https://${d}` })),
    maxRequestsPerStartUrl: 3,
    maxDepth: 2,
  });
  const { items } = await client.dataset(run.defaultDatasetId).listItems({ limit: MAX_ITEMS * TARGET_DOMAINS.length });
  const rows = items.map((it) => ({
    domain: it.domain || it.url,
    emails: (it.emails || []).join(' | '),
    phones: (it.phones || []).join(' | '),
    instagram: (it.instagrams || it.instagram || []).toString(),
    linkedins: (it.linkedIns || it.linkedins || []).join(' | '),
    whatsapps: (it.phonesUncertain || []).filter((p) => String(p).length > 8).join(' | '),
  }));
  await writeCsv('enrich', rows);
}

// 2) Google Maps: yeni hedef + telefon/website/WhatsApp (varsa)
async function maps() {
  const run = await client.actor('compass/crawler-google-places').call({
    searchStringsArray: MAPS_QUERIES,
    maxCrawledPlacesPerSearch: MAX_ITEMS,
    language: 'en',
  });
  const { items } = await client.dataset(run.defaultDatasetId).listItems();
  const rows = items.map((it) => ({
    name: it.title, category: it.categoryName, city: it.city,
    phone: it.phone || '', website: it.website || '',
    whatsapp: it.additionalInfo?.WhatsApp || '',
    address: it.address || '', source: 'google_maps',
  }));
  await writeCsv('maps', rows);
}

// 3) Etkinlik sayfaları: konuşmacı/sergici isimleri + iletişim ipucu
async function events() {
  const run = await client.actor('apify/website-content-crawler').call({
    startUrls: EVENT_URLS.map((u) => ({ url: u })),
    maxCrawlPages: MAX_ITEMS,
    crawlerType: 'cheerio',
  });
  const { items } = await client.dataset(run.defaultDatasetId).listItems();
  const rows = items.map((it) => ({
    event_url: it.url,
    title: it.metadata?.title || '',
    // metin içinden isim/şirket/iletişim manuel veya LLM ile ayıklanır
    text_excerpt: (it.text || '').slice(0, 500).replace(/\n/g, ' '),
    source: 'event_page',
  }));
  await writeCsv('events', rows);
  console.log('NOT: çıkan isimleri LinkedIn kişisel profiline bağla, sonra enrich ile iletişimi doldur.');
}

// 4) Richlist: zengin/ödül listelerinden isim+şirket
async function richlist() {
  const run = await client.actor('apify/website-content-crawler').call({
    startUrls: RICHLIST_URLS.map((u) => ({ url: u })),
    maxCrawlPages: MAX_ITEMS, crawlerType: 'cheerio',
  });
  const { items } = await client.dataset(run.defaultDatasetId).listItems();
  const rows = items.map((it) => ({
    url: it.url, title: it.metadata?.title || '',
    text_excerpt: (it.text || '').slice(0, 600).replace(/\n/g, ' '), source: 'richlist',
  }));
  await writeCsv('richlist', rows);
  console.log('NOT: metinden isim+şirketi LLM/manuel ayıkla, "GCC Hedef Kisiler" formatına ekle.');
}

// 5) News: yatırım açıklayan kurucuları haberlerden yakala
async function news() {
  const run = await client.actor('apify/website-content-crawler').call({
    startUrls: NEWS_QUERIES.map((q) => ({ url: `https://news.google.com/search?q=${encodeURIComponent(q)}&hl=en` })),
    maxCrawlPages: MAX_ITEMS, crawlerType: 'cheerio',
  });
  const { items } = await client.dataset(run.defaultDatasetId).listItems();
  const rows = items.map((it) => ({
    url: it.url, title: it.metadata?.title || '',
    text_excerpt: (it.text || '').slice(0, 600).replace(/\n/g, ' '), source: 'news',
  }));
  await writeCsv('news', rows);
}

// 6) Social: Instagram bio/iletişim
async function social() {
  const run = await client.actor('apify/instagram-scraper').call({
    directUrls: IG_PROFILES.map((u) => `https://www.instagram.com/${u}/`),
    resultsType: 'details', resultsLimit: MAX_ITEMS,
  });
  const { items } = await client.dataset(run.defaultDatasetId).listItems();
  const rows = items.map((it) => ({
    username: it.username, full_name: it.fullName || '',
    biography: it.biography || '', external_url: it.externalUrl || '',
    business_email: it.businessEmail || '', business_phone: it.businessPhoneNumber || '', source: 'instagram',
  }));
  await writeCsv('social', rows);
}

const cmd = process.argv[2];
const fn = { enrich, maps, events, richlist, news, social }[cmd];
if (!fn) { console.log('Kullanım: node apify_pipeline.js [enrich|maps|events|richlist|news|social]'); process.exit(1); }
if (!process.env.APIFY_TOKEN) { console.log('APIFY_TOKEN yok. export APIFY_TOKEN=apify_xxx'); process.exit(1); }
fn().catch((e) => { console.error('HATA:', e.message); process.exit(1); });

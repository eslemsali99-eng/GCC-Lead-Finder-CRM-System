/* Gulf Investor CRM — vanilla JS. data.json okur; i18n (TR/EN/AR), tek-tıkla durum, responsive. */
const WHATSAPP = "971585708868";

/* ---- Ülkeler (id + bayrak + tanıma regex) ---- */
const COUNTRY = [
  {id:"sa", flag:"🇸🇦", re:/sa[uú]di|suudi|arabistan|السعود/i},
  {id:"ae", flag:"🇦🇪", re:/uae|bae|emirat|dubai|abu ?dabi|abu ?dhabi|إمارات/i},
  {id:"qa", flag:"🇶🇦", re:/qatar|katar|doha|قطر/i},
  {id:"kw", flag:"🇰🇼", re:/kuwait|kuveyt|الكويت/i},
  {id:"bh", flag:"🇧🇭", re:/bahrain|bahreyn|manama|البحرين/i},
  {id:"om", flag:"🇴🇲", re:/oman|umman|maskat|muscat|عُمان|عمان/i},
];
const normCountry = u => COUNTRY.find(c=>c.re.test(u||"")) || {id:"other", flag:"🌍"};
const ROLES = [
  {id:"founder", re:/founder|kurucu|sahip|owner/i},
  {id:"chair",   re:/chair|başkan/i},
  {id:"ceo",     re:/ceo|chief exec|icra|i̇cra|genel müdür|managing director|\bmd\b/i},
  {id:"cfo",     re:/cfo|chief financial|finans/i},
];
const normRole = r => (ROLES.find(x=>x.re.test(r||""))||{id:"other"}).id;

/* ---- Çeviriler ---- */
const T = {
  tr:{ dir:"ltr", tagline:"Körfez karar vericileri · canlı lead intelligence", live:"Canlı", lead:"lead",
    byCountry:"Ülkeye göre dağılım", byRole:"Pozisyona göre", funnel:"LinkedIn hunisi",
    searchPh:"İsim, şirket veya pozisyon ara…", results:"sonuç", all:"Hepsi",
    thPerson:"Kişi", thRole:"Pozisyon", thCompany:"Şirket", thCountry:"Ülke", thStatus:"Kabul Durumu", thNote:"Durum", thAction:"İşlem",
    empty:"Filtreyle eşleşen kayıt yok.", footL:"$0 maliyet · otomatik · her 3 saatte güncellenir",
    sTotal:"Toplam Lead", sCountry:"Ülke", sSent:"İstek Gönderildi", sAcc:"Kabul Eden", sRate:"Kabul Oranı",
    subDecider:"karar verici", subMarket:"GCC pazarı", subLi:"LinkedIn", subConn:"bağlantı kuruldu", subRate:"gönderildi → kabul",
    fnPool:"Toplam havuz", fnSent:"İstek gönderildi", fnAcc:"Kabul etti",
    bAccepted:"Kabul etti", bSent:"İstek gönderildi", bNone:"Temas yok",
    fAcc:"Kabul edenler", fSent:"İstek gönderilen", fNone:"Temas yok",
    info:"Bilgiler", sector:"Sektör", emailL:"E-posta", lastC:"Son temas",
    actions:"Aksiyonlar", openLi:"LinkedIn'de aç / istek gönder", waMsg:"WhatsApp'tan yaz", copyEmail:"E-postayı kopyala", copied:"Kopyalandı ✓", verify:"Kaynağı doğrula",
    yourNotes:"Senin notların (otomatik kaydedilir)", durumL:"Durum", notL:"Not", saved:"Kaydedildi ✓",
    durumPh:"örn. Mesaj atıldı, görüşülüyor…", notPh:"Kişiye özel notların…", statusHint:"Tıkla → durumu değiştir",
    roles:{founder:"Kurucu",chair:"Başkan",ceo:"CEO",cfo:"CFO",other:"Diğer"},
    countries:{sa:"Suudi Arabistan",ae:"BAE",qa:"Katar",kw:"Kuveyt",bh:"Bahreyn",om:"Umman",other:"Diğer"} },
  en:{ dir:"ltr", tagline:"Gulf decision-makers · live lead intelligence", live:"Live", lead:"leads",
    byCountry:"By country", byRole:"By position", funnel:"LinkedIn funnel",
    searchPh:"Search name, company or position…", results:"results", all:"All",
    thPerson:"Person", thRole:"Position", thCompany:"Company", thCountry:"Country", thStatus:"Connection", thNote:"Status", thAction:"Action",
    empty:"No records match the filter.", footL:"$0 cost · automated · refreshes every 3 hours",
    sTotal:"Total Leads", sCountry:"Countries", sSent:"Requests Sent", sAcc:"Accepted", sRate:"Accept Rate",
    subDecider:"decision-makers", subMarket:"GCC markets", subLi:"LinkedIn", subConn:"connected", subRate:"sent → accepted",
    fnPool:"Total pool", fnSent:"Request sent", fnAcc:"Accepted",
    bAccepted:"Accepted", bSent:"Request sent", bNone:"No contact",
    fAcc:"Accepted", fSent:"Request sent", fNone:"No contact",
    info:"Details", sector:"Industry", emailL:"Email", lastC:"Last contact",
    actions:"Actions", openLi:"Open on LinkedIn / connect", waMsg:"Message on WhatsApp", copyEmail:"Copy email", copied:"Copied ✓", verify:"Verify source",
    yourNotes:"Your notes (auto-saved)", durumL:"Status", notL:"Note", saved:"Saved ✓",
    durumPh:"e.g. Messaged, in talks…", notPh:"Your private notes…", statusHint:"Click → change status",
    roles:{founder:"Founder",chair:"Chairman",ceo:"CEO",cfo:"CFO",other:"Other"},
    countries:{sa:"Saudi Arabia",ae:"UAE",qa:"Qatar",kw:"Kuwait",bh:"Bahrain",om:"Oman",other:"Other"} },
  ar:{ dir:"rtl", tagline:"صنّاع القرار في الخليج · معلومات فورية عن العملاء", live:"مباشر", lead:"عميل",
    byCountry:"حسب الدولة", byRole:"حسب المنصب", funnel:"مسار لينكدإن",
    searchPh:"ابحث بالاسم أو الشركة أو المنصب…", results:"نتيجة", all:"الكل",
    thPerson:"الشخص", thRole:"المنصب", thCompany:"الشركة", thCountry:"الدولة", thStatus:"حالة القبول", thNote:"الحالة", thAction:"إجراء",
    empty:"لا توجد سجلات مطابقة.", footL:"بتكلفة صفر · تلقائي · يُحدّث كل 3 ساعات",
    sTotal:"إجمالي العملاء", sCountry:"الدول", sSent:"طلبات مُرسلة", sAcc:"تم القبول", sRate:"معدل القبول",
    subDecider:"صنّاع قرار", subMarket:"أسواق الخليج", subLi:"لينكدإن", subConn:"تم الاتصال", subRate:"مُرسل ← مقبول",
    fnPool:"إجمالي القائمة", fnSent:"طلب مُرسل", fnAcc:"تم القبول",
    bAccepted:"تم القبول", bSent:"طلب مُرسل", bNone:"لا تواصل",
    fAcc:"المقبولون", fSent:"طلب مُرسل", fNone:"لا تواصل",
    info:"التفاصيل", sector:"القطاع", emailL:"البريد", lastC:"آخر تواصل",
    actions:"إجراءات", openLi:"افتح في لينكدإن / تواصل", waMsg:"راسل عبر واتساب", copyEmail:"نسخ البريد", copied:"تم النسخ ✓", verify:"تحقق من المصدر",
    yourNotes:"ملاحظاتك (تُحفظ تلقائياً)", durumL:"الحالة", notL:"ملاحظة", saved:"تم الحفظ ✓",
    durumPh:"مثال: تم التواصل، قيد النقاش…", notPh:"ملاحظاتك الخاصة…", statusHint:"اضغط ← غيّر الحالة",
    roles:{founder:"مؤسس",chair:"رئيس",ceo:"رئيس تنفيذي",cfo:"مدير مالي",other:"أخرى"},
    countries:{sa:"السعودية",ae:"الإمارات",qa:"قطر",kw:"الكويت",bh:"البحرين",om:"عُمان",other:"أخرى"} },
};
let LANG = localStorage.getItem("gcrm:lang") || (navigator.language||"tr").slice(0,2);
if(!T[LANG]) LANG = "tr";
const t = k => T[LANG][k] ?? k;
const cName = id => T[LANG].countries[id] || id;
const rName = id => T[LANG].roles[id] || id;

const CYCLE = {none:"sent", sent:"accepted", accepted:"none"};   // tıkla → sonraki durum
const KLAB = {accepted:"bAccepted", sent:"bSent", none:"bNone"};

let DATA=[], FILTERED=[];
const F={q:"",country:"all",role:"all",status:"all"};
let SORT={key:"isim",asc:true};

const $=s=>document.querySelector(s);
const initials=n=>(n||"?").split(/\s+/).slice(0,2).map(w=>w[0]||"").join("").toUpperCase();
const avatarColor=n=>{let h=0;for(const c of(n||""))h=c.charCodeAt(0)+((h<<5)-h);return `hsl(${Math.abs(h)%360} 60% 62%)`;};
const ls=k=>{try{return JSON.parse(localStorage.getItem("gcrm:"+k)||"{}")}catch{return{}}};
const lsSet=(k,v)=>localStorage.setItem("gcrm:"+k,JSON.stringify(v));
const esc=s=>(s==null?"":String(s)).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const keyOf=d=>`${(d.isim||"").toLowerCase()}|${(d.sirket||"").toLowerCase()}`;
const kabulOf=d=>{const m=ls(keyOf(d)).kabul;return m||d.kabul||"none";};

/* ---- i18n uygula ---- */
function applyI18n(){
  document.documentElement.lang=LANG; document.documentElement.dir=T[LANG].dir;
  document.querySelectorAll("[data-i18n]").forEach(el=>el.textContent=t(el.dataset.i18n));
  document.querySelectorAll("[data-i18n-ph]").forEach(el=>el.placeholder=t(el.dataset.i18nPh));
  document.querySelectorAll(".lang-btn").forEach(b=>b.classList.toggle("active",b.dataset.l===LANG));
}
function setLang(l){LANG=l;localStorage.setItem("gcrm:lang",l);applyI18n();buildFilters();render();}

/* ---- yükle ---- */
async function load(){
  try{
    const r=await fetch("data.json?_="+Date.now()); const j=await r.json();
    DATA=(j.leads||[]).map((l,i)=>({...l,_i:i,_c:normCountry(l.ulke),_r:normRole(l.rol)}));
    $("#updated").textContent=j.updated||"—"; $("#total-chip").textContent=j.total??DATA.length;
  }catch(e){$("#updated").textContent="—";console.error(e);}
  applyI18n(); buildFilters(); render();
}

/* ---- filtreler ---- */
function buildFilters(){
  const cs=["all",...COUNTRY.map(c=>c.id).filter(id=>DATA.some(d=>d._c.id===id))];
  const rs=["all",...ROLES.map(r=>r.id).filter(id=>DATA.some(d=>d._r===id)),"other"];
  chips("#country-filter","country",cs.map(c=>[c,c==="all"?t("all"):cName(c)]));
  chips("#role-filter","role",rs.map(r=>[r,r==="all"?t("all"):rName(r)]));
  chips("#status-filter","status",[["all",t("all")],["accepted",t("fAcc")],["sent",t("fSent")],["none",t("fNone")]]);
}
function chips(sel,field,pairs){
  $(sel).innerHTML=pairs.map(([v,l])=>`<button class="chip ${F[field]===v?'active':''}" data-v="${v}">${esc(l)}</button>`).join("");
  $(sel).querySelectorAll(".chip").forEach(b=>b.onclick=()=>{F[field]=b.dataset.v;buildFilters();render();});
}

/* ---- filtre + sırala ---- */
function apply(){
  const q=F.q.toLowerCase().trim();
  FILTERED=DATA.filter(d=>{
    if(F.country!=="all"&&d._c.id!==F.country)return false;
    if(F.role!=="all"&&d._r!==F.role)return false;
    if(F.status!=="all"&&kabulOf(d)!==F.status)return false;
    if(q&&!(`${d.isim} ${d.sirket} ${d.rol}`.toLowerCase().includes(q)))return false;
    return true;
  });
  const k=SORT.key,dir=SORT.asc?1:-1;
  FILTERED.sort((a,b)=>{
    let va=k==="durum"?(ls(keyOf(a)).durum||""):k==="kabul"?kabulOf(a):(a[k]||"");
    let vb=k==="durum"?(ls(keyOf(b)).durum||""):k==="kabul"?kabulOf(b):(b[k]||"");
    return String(va).localeCompare(String(vb),"tr")*dir;
  });
}

function render(){apply();renderStats();renderBars();renderFunnel();renderRows();$("#result-count").textContent=FILTERED.length;}

function renderStats(){
  const n=DATA.length, acc=DATA.filter(d=>kabulOf(d)==="accepted").length,
        sent=DATA.filter(d=>kabulOf(d)!=="none").length,
        countries=new Set(DATA.map(d=>d._c.id)).size, rate=sent?Math.round(acc/sent*100):0;
  const cards=[
    {k:t("sTotal"),v:n,s:t("subDecider"),ic:"M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14c-5 0-8 2.5-8 5v1h16v-1c0-2.5-3-5-8-5z",c:"var(--gold)"},
    {k:t("sCountry"),v:countries,s:t("subMarket"),ic:"M12 2a10 10 0 100 20 10 10 0 000-20zM2 12h20M12 2c3 3 3 17 0 20M12 2c-3 3-3 17 0 20",c:"var(--teal)"},
    {k:t("sSent"),v:sent,s:t("subLi"),ic:"M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z",c:"var(--amber)"},
    {k:t("sAcc"),v:acc,s:t("subConn"),ic:"M20 6L9 17l-5-5",c:"var(--emerald)"},
    {k:t("sRate"),v:rate+"%",s:t("subRate"),ic:"M3 17l6-6 4 4 8-8M14 7h7v7",c:"var(--gold)"},
  ];
  $("#stats").innerHTML=cards.map(c=>`<div class="stat" style="--accent:${c.c}">
    <div class="k"><svg class="ic" viewBox="0 0 24 24" fill="none" stroke="${c.c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="${c.ic}"/></svg>${esc(c.k)}</div>
    <div class="v">${c.v}</div><div class="s">${esc(c.s)}</div></div>`).join("");
}
function renderBars(){
  bars("#country-bars",COUNTRY.map(c=>({lab:`<span class="flag">${c.flag}</span>${esc(cName(c.id))}`,n:DATA.filter(d=>d._c.id===c.id).length})).filter(x=>x.n).sort((a,b)=>b.n-a.n));
  bars("#role-bars",[...ROLES.map(r=>r.id),"other"].map(id=>({lab:esc(rName(id)),n:DATA.filter(d=>d._r===id).length})).filter(x=>x.n).sort((a,b)=>b.n-a.n));
}
function bars(sel,items){const max=Math.max(1,...items.map(i=>i.n));
  $(sel).innerHTML=items.map(i=>`<div class="bar-row"><div class="lab">${i.lab}</div><div class="bar-track"><div class="bar-fill" style="width:${i.n/max*100}%"></div></div><div class="num">${i.n}</div></div>`).join("");}
function renderFunnel(){
  const n=DATA.length,sent=DATA.filter(d=>kabulOf(d)!=="none").length,acc=DATA.filter(d=>kabulOf(d)==="accepted").length;
  const steps=[[t("fnPool"),n,"var(--slate)"],[t("fnSent"),sent,"var(--amber)"],[t("fnAcc"),acc,"var(--emerald)"]];
  $("#funnel").innerHTML=steps.map(([l,v,c])=>`<div class="fn"><div class="l"><span class="badge-dot" style="background:${c}"></span>${esc(l)}</div><div class="n" style="color:${c}">${v}</div></div>`).join("");
}

function renderRows(){
  const tb=$("#rows"),em=$("#empty");
  document.querySelectorAll("th.sortable").forEach(th=>{th.classList.toggle("sorted",th.dataset.sort===SORT.key);th.classList.toggle("asc",th.dataset.sort===SORT.key&&SORT.asc);});
  if(!FILTERED.length){tb.innerHTML="";em.hidden=false;return;} em.hidden=true;
  const L={person:t("thPerson"),role:t("thRole"),company:t("thCompany"),country:t("thCountry"),status:t("thStatus"),note:t("thNote"),action:t("thAction")};
  tb.innerHTML=FILTERED.map(d=>{
    const kb=kabulOf(d),durum=ls(keyOf(d)).durum||"";
    return `<tr data-i="${d._i}">
      <td data-label="${L.person}"><div class="person">
        <div class="avatar" style="background:${avatarColor(d.isim)}">${initials(d.isim)}</div>
        <div><div class="nm">${esc(d.isim)}</div><div class="src">${esc(d.sektor||"")}</div></div></div></td>
      <td data-label="${L.role}">${esc(d.rol)||"—"}</td>
      <td data-label="${L.company}" class="co">${esc(d.sirket)||"—"}</td>
      <td data-label="${L.country}" class="cell-ulke"><span class="flag">${d._c.flag}</span>${esc(cName(d._c.id))}</td>
      <td data-label="${L.status}"><span class="badge b-${kb} clickable" data-mark="${d._i}" title="${esc(t("statusHint"))}">${esc(t(KLAB[kb]))}</span></td>
      <td data-label="${L.note}" class="durum-cell ${durum?'':'empty-d'}">${esc(durum)||"—"}</td>
      <td data-label="${L.action}"><div class="row-actions">
        ${d.linkedin?`<a class="icon-btn" href="${esc(d.linkedin)}" target="_blank" title="LinkedIn" onclick="event.stopPropagation()"><svg viewBox="0 0 24 24"><path d="M19 3a2 2 0 012 2v14a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h14zM8.3 18.3v-7H6v7h2.3zM7.1 10a1.3 1.3 0 100-2.6 1.3 1.3 0 000 2.6zM18.3 18.3v-3.8c0-2-.5-3.4-2.9-3.4-1.1 0-1.9.6-2.2 1.2h0v-1H11v7h2.3v-3.5c0-.9.2-1.8 1.3-1.8s1.3 1 1.3 1.9v3.4h2.4z"/></svg></a>`:""}
        ${d.web?`<a class="icon-btn" href="${esc(d.web)}" target="_blank" title="Web" onclick="event.stopPropagation()"><svg viewBox="0 0 24 24"><path d="M12 2a10 10 0 100 20 10 10 0 000-20zm0 2c1.5 0 3.5 3 3.8 7H8.2C8.5 7 10.5 4 12 4zM4.3 11h3.9c.1 1.4.4 2.8.9 4H6a8 8 0 01-1.7-4zm0 2H6a8 8 0 001.7 4H9.1c-.5-1.2-.8-2.6-.9-4zm15.4 0a8 8 0 01-1.7 4h-1.4c.5-1.2.8-2.6.9-4h2.2zm0-2h-2.2c-.1-1.4-.4-2.8-.9-4h1.4a8 8 0 011.7 4z"/></svg></a>`:""}
      </div></td></tr>`;
  }).join("");
  tb.querySelectorAll("tr").forEach(tr=>tr.onclick=()=>openDrawer(DATA[+tr.dataset.i]));
  tb.querySelectorAll("[data-mark]").forEach(b=>b.onclick=e=>{e.stopPropagation();cycleStatus(DATA[+b.dataset.mark]);});
}

/* ---- tek-tıkla durum değiştir ---- */
function cycleStatus(d){
  const key=keyOf(d), cur=kabulOf(d), next=CYCLE[cur];
  const s=ls(key); s.kabul=next; lsSet(key,s);
  render();
}

/* ---- drawer ---- */
function openDrawer(d){
  const key=keyOf(d),saved=ls(key),kb=kabulOf(d);
  const wa=`https://wa.me/${WHATSAPP}?text=${encodeURIComponent("Hi "+(d.isim||"")+", ")}`;
  $("#drawer-body").innerHTML=`
    <div class="d-head">
      <div class="d-avatar" style="background:${avatarColor(d.isim)}">${initials(d.isim)}</div>
      <div><div class="d-name">${esc(d.isim)}</div><div class="d-role">${esc(d.rol)||""}</div>
        <div class="d-co">${d._c.flag} ${esc(d.sirket)||""} · ${esc(cName(d._c.id))}</div></div></div>
    <div class="d-section"><h4>${esc(t("info"))}</h4><div class="d-meta">
      <div class="it"><div class="l">${esc(t("sector"))}</div><div class="vv">${esc(d.sektor)||"—"}</div></div>
      <div class="it"><div class="l">${esc(t("thStatus"))}</div><div class="vv"><span class="badge b-${kb}">${esc(t(KLAB[kb]))}</span></div></div>
      <div class="it"><div class="l">${esc(t("emailL"))}</div><div class="vv">${esc(d.email)||"—"}</div></div>
      <div class="it"><div class="l">${esc(t("lastC"))}</div><div class="vv">${esc(d.son_temas)||"—"}</div></div></div></div>
    <div class="d-section"><h4>${esc(t("actions"))}</h4><div class="d-actions">
      ${d.linkedin?`<a class="d-btn" href="${esc(d.linkedin)}" target="_blank"><svg class="ig" viewBox="0 0 24 24"><path d="M19 3a2 2 0 012 2v14a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h14zM8.3 18.3v-7H6v7h2.3zM7.1 10a1.3 1.3 0 100-2.6 1.3 1.3 0 000 2.6zM18.3 18.3v-3.8c0-2-.5-3.4-2.9-3.4-1.1 0-1.9.6-2.2 1.2h0v-1H11v7h2.3v-3.5c0-.9.2-1.8 1.3-1.8s1.3 1 1.3 1.9v3.4h2.4z"/></svg>${esc(t("openLi"))}</a>`:""}
      <a class="d-btn" href="${wa}" target="_blank"><svg class="ig" viewBox="0 0 24 24"><path d="M12 2a10 10 0 00-8.6 15l-1.4 5 5.1-1.3A10 10 0 1012 2zm0 2a8 8 0 11-4.1 14.9l-.3-.2-3 .8.8-2.9-.2-.3A8 8 0 0112 4z"/></svg>${esc(t("waMsg"))}</a>
      ${d.email?`<button class="d-btn" data-copy="${esc(d.email)}"><svg class="ig" viewBox="0 0 24 24"><path d="M4 4h16v16H4z M22 6l-10 7L2 6"/></svg><span>${esc(t("copyEmail"))}</span></button>`:""}
      ${d.kaynak?`<a class="d-btn" href="${esc(d.kaynak)}" target="_blank"><svg class="ig" viewBox="0 0 24 24"><path d="M12 2a10 10 0 100 20 10 10 0 000-20zM11 7h2v6h-2zM11 15h2v2h-2z"/></svg>${esc(t("verify"))}</a>`:""}
    </div></div>
    <div class="d-section"><h4>${esc(t("yourNotes"))}</h4>
      <div class="field"><label>${esc(t("thStatus"))}</label>
        <select id="d-kabul">
          <option value="none" ${kb==="none"?"selected":""}>${esc(t("bNone"))}</option>
          <option value="sent" ${kb==="sent"?"selected":""}>${esc(t("bSent"))}</option>
          <option value="accepted" ${kb==="accepted"?"selected":""}>${esc(t("bAccepted"))}</option>
        </select></div>
      <div class="field"><label>${esc(t("durumL"))}</label>
        <input class="txt" id="d-durum" value="${esc(saved.durum||"")}" placeholder="${esc(t("durumPh"))}"/></div>
      <div class="field"><label>${esc(t("notL"))}</label>
        <textarea id="d-not" rows="3" placeholder="${esc(t("notPh"))}">${esc(saved.not||"")}</textarea></div>
      <div class="save-note" id="save-note">${esc(t("saved"))}</div></div>`;
  const cp=$("#drawer-body [data-copy]");
  if(cp)cp.onclick=()=>{navigator.clipboard.writeText(cp.dataset.copy);cp.querySelector("span").textContent=t("copied");};
  ["d-kabul","d-durum","d-not"].forEach(id=>{const el=$("#"+id);el.addEventListener(id==="d-kabul"?"change":"input",()=>{
    lsSet(key,{kabul:$("#d-kabul").value,durum:$("#d-durum").value,not:$("#d-not").value});
    const sn=$("#save-note");sn.classList.add("show");clearTimeout(window._st);window._st=setTimeout(()=>sn.classList.remove("show"),1200);render();});});
  $("#drawer").hidden=false;$("#overlay").hidden=false;
}
function closeDrawer(){$("#drawer").hidden=true;$("#overlay").hidden=true;}
$("#drawer-close").onclick=closeDrawer;$("#overlay").onclick=closeDrawer;
document.addEventListener("keydown",e=>{if(e.key==="Escape")closeDrawer();});

/* ---- olaylar ---- */
$("#search").addEventListener("input",e=>{F.q=e.target.value;render();});
document.querySelectorAll("th.sortable").forEach(th=>th.onclick=()=>{const k=th.dataset.sort;SORT.asc=SORT.key===k?!SORT.asc:true;SORT.key=k;render();});
document.querySelectorAll(".lang-btn").forEach(b=>b.onclick=()=>setLang(b.dataset.l));

load();

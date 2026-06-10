/* Gulf Investor CRM — vanilla JS, bağımlılıksız. data.json'u okur, her şeyi tarayıcıda render eder. */
const WHATSAPP = "971585708868", CALL = "+905380691998";

/* ---- Ülke normalizasyonu (karışık TR/EN adları kanonik 6 GCC ülkesine indir) ---- */
const COUNTRY = [
  {key:"Suudi Arabistan", flag:"🇸🇦", re:/sa[uú]di|suudi|arabistan/i},
  {key:"BAE",             flag:"🇦🇪", re:/uae|bae|emirat|dubai|abu ?dabi|abu ?dhabi/i},
  {key:"Katar",           flag:"🇶🇦", re:/qatar|katar|doha/i},
  {key:"Kuveyt",          flag:"🇰🇼", re:/kuwait|kuveyt/i},
  {key:"Bahreyn",         flag:"🇧🇭", re:/bahrain|bahreyn|manama/i},
  {key:"Umman",           flag:"🇴🇲", re:/oman|umman|maskat|muscat/i},
];
const normCountry = u => (COUNTRY.find(c=>c.re.test(u||""))||{key:"Diğer",flag:"🌍"});

/* ---- Rol kovaları ---- */
const ROLES = [
  {key:"Kurucu", re:/founder|kurucu|sahip|owner/i},
  {key:"Başkan", re:/chair|başkan/i},
  {key:"CEO",    re:/ceo|chief exec|icra|i̇cra|genel müdür|managing director|\bmd\b/i},
  {key:"CFO",    re:/cfo|chief financial|finans/i},
];
const normRole = r => (ROLES.find(x=>x.re.test(r||""))||{key:"Diğer"}).key;

const ACCENT = {accepted:"#34d399", sent:"#fbbf24", none:"#64748b"};
const KABUL_LABEL = {accepted:"Kabul etti", sent:"İstek gönderildi", none:"Temas yok"};

let DATA = [], FILTERED = [];
const F = {q:"", country:"Hepsi", role:"Hepsi", status:"Hepsi"};
let SORT = {key:"isim", asc:true};

const $ = s => document.querySelector(s);
const initials = n => (n||"?").split(/\s+/).slice(0,2).map(w=>w[0]||"").join("").toUpperCase();
const avatarColor = n => {let h=0;for(const c of (n||""))h=c.charCodeAt(0)+((h<<5)-h);
  return `hsl(${Math.abs(h)%360} 60% 62%)`;}
const ls = key => { try{return JSON.parse(localStorage.getItem("gcrm:"+key)||"{}")}catch{return {}} };
const lsSet = (key,v) => localStorage.setItem("gcrm:"+key, JSON.stringify(v));

/* ---- yükle ---- */
async function load(){
  try{
    const r = await fetch("data.json?_="+Date.now());
    const j = await r.json();
    DATA = (j.leads||[]).map((l,i)=>({...l, _i:i, _c:normCountry(l.ulke), _r:normRole(l.rol)}));
    $("#updated").textContent = j.updated || "—";
    $("#total-chip").textContent = j.total ?? DATA.length;
  }catch(e){
    $("#updated").textContent = "veri yüklenemedi";
    console.error(e);
  }
  buildFilters(); render();
}

/* ---- filtre çipleri ---- */
function buildFilters(){
  const countries = ["Hepsi", ...COUNTRY.map(c=>c.key).filter(k=>DATA.some(d=>d._c.key===k))];
  const roles = ["Hepsi", ...ROLES.map(r=>r.key).filter(k=>DATA.some(d=>d._r===k)), "Diğer"];
  const statuses = [["Hepsi","Hepsi"],["accepted","Kabul edenler"],["sent","İstek gönderilen"],["none","Temas yok"]];
  chips("#country-filter","country",countries.map(c=>[c,c]));
  chips("#role-filter","role",roles.map(r=>[r,r]));
  chips("#status-filter","status",statuses);
}
function chips(sel, field, pairs){
  $(sel).innerHTML = pairs.map(([v,l])=>
    `<button class="chip ${F[field]===v?'active':''}" data-v="${v}">${l}</button>`).join("");
  $(sel).querySelectorAll(".chip").forEach(b=>b.onclick=()=>{F[field]=b.dataset.v;buildFilters();render();});
}

/* ---- filtre + sırala ---- */
function apply(){
  const q = F.q.toLowerCase().trim();
  FILTERED = DATA.filter(d=>{
    if(F.country!=="Hepsi" && d._c.key!==F.country) return false;
    if(F.role!=="Hepsi" && d._r!==F.role) return false;
    if(F.status!=="Hepsi" && (kabulOf(d))!==F.status) return false;
    if(q && !(`${d.isim} ${d.sirket} ${d.rol}`.toLowerCase().includes(q))) return false;
    return true;
  });
  const k=SORT.key, dir=SORT.asc?1:-1;
  FILTERED.sort((a,b)=>{
    let va = k==="durum" ? (ls(keyOf(a)).durum||"") : k==="kabul" ? kabulOf(a) : (a[k]||"");
    let vb = k==="durum" ? (ls(keyOf(b)).durum||"") : k==="kabul" ? kabulOf(b) : (b[k]||"");
    return String(va).localeCompare(String(vb),"tr")*dir;
  });
}
const keyOf = d => `${(d.isim||"").toLowerCase()}|${(d.sirket||"").toLowerCase()}`;
/* kabul: bot verisi (data.json) + kullanıcının manuel işareti (localStorage) */
function kabulOf(d){ const m=ls(keyOf(d)).kabul; return m||d.kabul||"none"; }

/* ---- render ---- */
function render(){
  apply();
  renderStats(); renderBars(); renderFunnel(); renderRows();
  $("#result-count").textContent = FILTERED.length;
}

function renderStats(){
  const n=DATA.length;
  const acc=DATA.filter(d=>kabulOf(d)==="accepted").length;
  const sent=DATA.filter(d=>kabulOf(d)!=="none").length;
  const countries=new Set(DATA.map(d=>d._c.key)).size;
  const rate = sent? Math.round(acc/sent*100):0;
  const cards=[
    {k:"Toplam Lead",v:n,s:"karar verici",ic:"M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14c-5 0-8 2.5-8 5v1h16v-1c0-2.5-3-5-8-5z",c:"var(--gold)"},
    {k:"Ülke",v:countries,s:"GCC pazarı",ic:"M12 2a10 10 0 100 20 10 10 0 000-20zM2 12h20M12 2c3 3 3 17 0 20M12 2c-3 3-3 17 0 20",c:"var(--teal)"},
    {k:"İstek Gönderildi",v:sent,s:"LinkedIn",ic:"M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z",c:"var(--amber)"},
    {k:"Kabul Eden",v:acc,s:"bağlantı kuruldu",ic:"M20 6L9 17l-5-5",c:"var(--emerald)"},
    {k:"Kabul Oranı",v:rate+"%",s:"sent → accepted",ic:"M3 17l6-6 4 4 8-8M14 7h7v7",c:"var(--gold)"},
  ];
  $("#stats").innerHTML = cards.map(c=>`
    <div class="stat" style="--accent:${c.c}">
      <div class="k"><svg class="ic" viewBox="0 0 24 24" fill="none" stroke="${c.c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="${c.ic}"/></svg>${c.k}</div>
      <div class="v">${c.v}</div><div class="s">${c.s}</div>
    </div>`).join("");
}

function renderBars(){
  bars("#country-bars", COUNTRY.map(c=>({lab:`<span class="flag">${c.flag}</span>${c.key}`,
        n:DATA.filter(d=>d._c.key===c.key).length})).filter(x=>x.n).sort((a,b)=>b.n-a.n));
  const rb=[...ROLES.map(r=>r.key),"Diğer"].map(k=>({lab:k,n:DATA.filter(d=>d._r===k).length})).filter(x=>x.n).sort((a,b)=>b.n-a.n);
  bars("#role-bars", rb);
}
function bars(sel, items){
  const max=Math.max(1,...items.map(i=>i.n));
  $(sel).innerHTML = items.map(i=>`
    <div class="bar-row"><div class="lab">${i.lab}</div>
      <div class="bar-track"><div class="bar-fill" style="width:${i.n/max*100}%"></div></div>
      <div class="num">${i.n}</div></div>`).join("");
}

function renderFunnel(){
  const n=DATA.length, sent=DATA.filter(d=>kabulOf(d)!=="none").length, acc=DATA.filter(d=>kabulOf(d)==="accepted").length;
  const steps=[["Toplam havuz",n,"var(--slate)"],["İstek gönderildi",sent,"var(--amber)"],["Kabul etti",acc,"var(--emerald)"]];
  $("#funnel").innerHTML = steps.map(([l,v,c])=>`
    <div class="fn"><div class="l"><span class="badge-dot" style="background:${c}"></span>${l}</div>
      <div class="n" style="color:${c}">${v}</div></div>`).join("");
}

function renderRows(){
  const tb=$("#rows"), em=$("#empty");
  document.querySelectorAll("th.sortable").forEach(th=>{
    th.classList.toggle("sorted",th.dataset.sort===SORT.key);
    th.classList.toggle("asc",th.dataset.sort===SORT.key&&SORT.asc);
  });
  if(!FILTERED.length){tb.innerHTML="";em.hidden=false;return;} em.hidden=true;
  tb.innerHTML = FILTERED.map(d=>{
    const kb=kabulOf(d), durum=ls(keyOf(d)).durum||"";
    return `<tr data-i="${d._i}">
      <td><div class="person">
        <div class="avatar" style="background:${avatarColor(d.isim)}">${initials(d.isim)}</div>
        <div><div class="nm">${esc(d.isim)}</div><div class="src">${esc(d.sektor||d.kaynak_kisa||"")}</div></div>
      </div></td>
      <td>${esc(d.rol)||"—"}</td>
      <td class="co">${esc(d.sirket)||"—"}</td>
      <td class="cell-ulke"><span class="flag">${d._c.flag}</span>${d._c.key}</td>
      <td><span class="badge b-${kb}">${KABUL_LABEL[kb]}</span></td>
      <td class="durum-cell ${durum?'':'empty-d'}">${esc(durum)||"—"}</td>
      <td><div class="row-actions">
        ${d.linkedin?`<a class="icon-btn" href="${esc(d.linkedin)}" target="_blank" title="LinkedIn" onclick="event.stopPropagation()"><svg viewBox="0 0 24 24"><path d="M19 3a2 2 0 012 2v14a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h14zM8.3 18.3v-7H6v7h2.3zM7.1 10a1.3 1.3 0 100-2.6 1.3 1.3 0 000 2.6zM18.3 18.3v-3.8c0-2-.5-3.4-2.9-3.4-1.1 0-1.9.6-2.2 1.2h0v-1H11v7h2.3v-3.5c0-.9.2-1.8 1.3-1.8s1.3 1 1.3 1.9v3.4h2.4z"/></svg></a>`:""}
        ${d.web?`<a class="icon-btn" href="${esc(d.web)}" target="_blank" title="Web" onclick="event.stopPropagation()"><svg viewBox="0 0 24 24"><path d="M12 2a10 10 0 100 20 10 10 0 000-20zm0 2c1.5 0 3.5 3 3.8 7H8.2C8.5 7 10.5 4 12 4zM4.3 11h3.9c.1 1.4.4 2.8.9 4H6a8 8 0 01-1.7-4zm0 2H6a8 8 0 001.7 4H9.1c-.5-1.2-.8-2.6-.9-4zm15.4 0a8 8 0 01-1.7 4h-1.4c.5-1.2.8-2.6.9-4h2.2zm0-2h-2.2c-.1-1.4-.4-2.8-.9-4h1.4a8 8 0 011.7 4z"/></svg></a>`:""}
      </div></td>
    </tr>`;
  }).join("");
  tb.querySelectorAll("tr").forEach(tr=>tr.onclick=()=>openDrawer(DATA[+tr.dataset.i]));
}
const esc = s => (s==null?"":String(s)).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

/* ---- drawer ---- */
function openDrawer(d){
  const key=keyOf(d), saved=ls(key), kb=kabulOf(d);
  const wa=`https://wa.me/${WHATSAPP}?text=${encodeURIComponent("Hi "+(d.isim||"")+", ")}`;
  $("#drawer-body").innerHTML=`
    <div class="d-head">
      <div class="d-avatar" style="background:${avatarColor(d.isim)}">${initials(d.isim)}</div>
      <div><div class="d-name">${esc(d.isim)}</div>
        <div class="d-role">${esc(d.rol)||""}</div>
        <div class="d-co">${d._c.flag} ${esc(d.sirket)||""} · ${d._c.key}</div></div>
    </div>
    <div class="d-section"><h4>Bilgiler</h4><div class="d-meta">
      <div class="it"><div class="l">Sektör</div><div class="vv">${esc(d.sektor)||"—"}</div></div>
      <div class="it"><div class="l">Kabul Durumu</div><div class="vv"><span class="badge b-${kb}">${KABUL_LABEL[kb]}</span></div></div>
      <div class="it"><div class="l">E-posta</div><div class="vv">${esc(d.email)||"—"}</div></div>
      <div class="it"><div class="l">Son temas</div><div class="vv">${esc(d.son_temas)||"—"}</div></div>
    </div></div>
    <div class="d-section"><h4>Aksiyonlar</h4><div class="d-actions">
      ${d.linkedin?`<a class="d-btn" href="${esc(d.linkedin)}" target="_blank"><svg class="ig" viewBox="0 0 24 24"><path d="M19 3a2 2 0 012 2v14a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h14zM8.3 18.3v-7H6v7h2.3zM7.1 10a1.3 1.3 0 100-2.6 1.3 1.3 0 000 2.6zM18.3 18.3v-3.8c0-2-.5-3.4-2.9-3.4-1.1 0-1.9.6-2.2 1.2h0v-1H11v7h2.3v-3.5c0-.9.2-1.8 1.3-1.8s1.3 1 1.3 1.9v3.4h2.4z"/></svg>LinkedIn'de aç / istek gönder</a>`:""}
      <a class="d-btn" href="${wa}" target="_blank"><svg class="ig" viewBox="0 0 24 24"><path d="M12 2a10 10 0 00-8.6 15l-1.4 5 5.1-1.3A10 10 0 1012 2zm0 2a8 8 0 11-4.1 14.9l-.3-.2-3 .8.8-2.9-.2-.3A8 8 0 0112 4z"/></svg>WhatsApp'tan yaz</a>
      ${d.email?`<button class="d-btn" onclick="navigator.clipboard.writeText('${esc(d.email)}');this.lastChild.textContent=' E-posta kopyalandı ✓'"><svg class="ig" viewBox="0 0 24 24"><path d="M4 4h16v16H4z M22 6l-10 7L2 6"/></svg><span>E-postayı kopyala</span></button>`:""}
      ${d.kaynak?`<a class="d-btn" href="${esc(d.kaynak)}" target="_blank"><svg class="ig" viewBox="0 0 24 24"><path d="M12 2a10 10 0 100 20 10 10 0 000-20zM11 7h2v6h-2zM11 15h2v2h-2z"/></svg>Kaynağı doğrula</a>`:""}
    </div></div>
    <div class="d-section"><h4>Senin notların (otomatik kaydedilir)</h4>
      <div class="field"><label>İsteği kabul etti mi?</label>
        <select id="d-kabul">
          <option value="">— botun verisi (${KABUL_LABEL[d.kabul||"none"]})</option>
          <option value="sent" ${saved.kabul==="sent"?"selected":""}>İstek gönderildi</option>
          <option value="accepted" ${saved.kabul==="accepted"?"selected":""}>✓ Kabul etti</option>
          <option value="none" ${saved.kabul==="none"?"selected":""}>Temas yok</option>
        </select></div>
      <div class="field"><label>Durum</label>
        <input style="width:100%;background:var(--panel);border:1px solid var(--line);color:var(--txt);border-radius:10px;padding:10px 12px;font-size:13px;font-family:inherit" id="d-durum" value="${esc(saved.durum||"")}" placeholder="örn. Mesaj atıldı, görüşülüyor…"/></div>
      <div class="field"><label>Not</label>
        <textarea id="d-not" rows="3" placeholder="Kişiye özel notların…">${esc(saved.not||"")}</textarea></div>
      <div class="save-note" id="save-note">Kaydedildi ✓</div>
    </div>`;
  ["d-kabul","d-durum","d-not"].forEach(id=>{
    const el=$("#"+id); const ev=id==="d-kabul"?"change":"input";
    el.addEventListener(ev,()=>{
      lsSet(key,{kabul:$("#d-kabul").value, durum:$("#d-durum").value, not:$("#d-not").value});
      const sn=$("#save-note"); sn.classList.add("show"); clearTimeout(window._st);
      window._st=setTimeout(()=>sn.classList.remove("show"),1200);
      render();
    });
  });
  $("#drawer").hidden=false; $("#overlay").hidden=false;
}
function closeDrawer(){$("#drawer").hidden=true;$("#overlay").hidden=true;}
$("#drawer-close").onclick=closeDrawer; $("#overlay").onclick=closeDrawer;
document.addEventListener("keydown",e=>{if(e.key==="Escape")closeDrawer();});

/* ---- olaylar ---- */
$("#search").addEventListener("input",e=>{F.q=e.target.value;render();});
document.querySelectorAll("th.sortable").forEach(th=>th.onclick=()=>{
  const k=th.dataset.sort; SORT.asc = SORT.key===k ? !SORT.asc : true; SORT.key=k; render();
});

load();

/**
 * GCC CRM — Canlı Google Sheet alıcısı (Apps Script web app) — v3 (toplu yazma).
 * Bot bu URL'ye TÜM listeyi POST eder; script "CRM" sayfasını tek seferde yeniden yazar.
 * Binlerce satırda bile hızlıdır (satır satır degil, tek setValues).
 *
 * MANUEL sütunlar (Durum, Not) KORUNUR — bot bunlara dokunmaz, senin yazdiklarin kalir.
 * Eski "Genel Durum" sütunundaki degerler otomatik "Durum"a tasinir (gecmis kaybolmaz).
 *
 * KURULUM/GUNCELLEME:
 *  1) Sheet -> Uzantilar -> Apps Script. Tum kodu sil, bunu yapistir. Kaydet.
 *  2) Dagit -> Dagitimlari yonet -> ✏️ -> "Surum: Yeni surum" -> Dagit. (URL ayni kalir.)
 */
var HEADER = ["No","Kategori","İsim","Rol","Şirket","Ülke","Yanıt Olasılığı","İş E-postası",
              "LinkedIn","Kabul Durumu","Durum","Son Temas","Not"];
var MANUEL = ["Durum","Not"];   // bota dokundurmadigimiz, kullanicinin elle yazdigi sutunlar

function doGet(e){ return ContentService.createTextOutput("GCC CRM webapp calisiyor (v3 toplu)."); }

function doPost(e){
  var lock = LockService.getScriptLock(); lock.waitLock(30000);
  try{
    var payload = JSON.parse(e.postData.contents);
    var rows = payload.rows || [];
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sh = ss.getSheetByName("CRM") || ss.insertSheet("CRM");

    // 1) Var olan manuel degerleri (Durum, Not) anahtar->deger oku. Eski "Genel Durum"u Durum'a tasi.
    var manual = {};
    if (sh.getLastRow() >= 1){
      var data = sh.getDataRange().getValues();
      var head = data[0];
      var iIsim = head.indexOf("İsim"), iSirket = head.indexOf("Şirket");
      var iDurum = head.indexOf("Durum"), iGenel = head.indexOf("Genel Durum"), iNot = head.indexOf("Not");
      if (iIsim >= 0 && iSirket >= 0){
        for (var r=1; r<data.length; r++){
          var k = (String(data[r][iIsim])+"|"+String(data[r][iSirket])).toLowerCase();
          var durum = (iDurum>=0 ? data[r][iDurum] : "") || (iGenel>=0 ? data[r][iGenel] : "");
          manual[k] = { "Durum": durum || "", "Not": (iNot>=0 ? data[r][iNot] : "") || "" };
        }
      }
    }

    // 2) Tam tabloyu bellekte kur: header + tum satirlar (otomatik payload'dan, manuel korunan)
    var out = [HEADER.slice()];
    for (var x=0; x<rows.length; x++){
      var obj = rows[x];
      var key = (String(obj["İsim"]||"")+"|"+String(obj["Şirket"]||"")).toLowerCase();
      var km = manual[key] || {};
      out.push(HEADER.map(function(h){
        if (MANUEL.indexOf(h) >= 0) return (km[h] !== undefined ? km[h] : "");
        return (h in obj) ? obj[h] : "";
      }));
    }

    // 3) Sayfayi temizle ve TEK setValues ile yaz (boyut ne olursa olsun hizli)
    sh.clear();
    sh.getRange(1, 1, out.length, HEADER.length).setValues(out);
    sh.getRange(1, 1, 1, HEADER.length).setFontWeight("bold").setBackground("#1F3864").setFontColor("#FFFFFF");
    sh.setFrozenRows(1);

    return ContentService.createTextOutput(JSON.stringify({ok:true, rows: rows.length}))
           .setMimeType(ContentService.MimeType.JSON);
  } catch(err){
    return ContentService.createTextOutput(JSON.stringify({ok:false, error:String(err)}))
           .setMimeType(ContentService.MimeType.JSON);
  } finally { lock.releaseLock(); }
}

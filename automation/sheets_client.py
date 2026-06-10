"""Google Sheets bağlayıcısı (service account). Ücretsiz Google Sheets API."""
import json, os
import gspread
from google.oauth2.service_account import Credentials

HEADER = ["No","Kategori","Sektor","Isim","Rol","Sirket","Ulke","Yanit Olasiligi",
          "LinkedIn","Sirket Web","Is E-postasi","Telefon","Instagram","Not","Kaynak",
          "Eklenme","LinkedIn Durum"]

def _cfg():
    here = os.path.dirname(__file__)
    with open(os.path.join(here, "config.json"), encoding="utf-8") as f:
        return json.load(f), here

def open_sheet():
    cfg, here = _cfg()
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(
        os.path.join(here, cfg["google_service_account_file"]), scopes=scopes)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(cfg["google_sheet_id"])
    try:
        ws = sh.worksheet(cfg.get("worksheet_name", "TUM KISILER"))
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(cfg.get("worksheet_name", "TUM KISILER"), rows=2000, cols=len(HEADER))
        ws.append_row(HEADER)
    return ws, cfg

def existing_keys(ws):
    """(isim|sirket) küçük-harf anahtar kümesi — tekrar engeller."""
    rows = ws.get_all_values()
    keys = set()
    if not rows:
        return keys
    head = rows[0]
    try:
        i_isim, i_sirket = head.index("Isim"), head.index("Sirket")
    except ValueError:
        i_isim, i_sirket = 3, 5
    for r in rows[1:]:
        if len(r) > max(i_isim, i_sirket):
            keys.add((r[i_isim].strip().lower(), r[i_sirket].strip().lower()))
    return keys

def append_rows(ws, rows):
    if rows:
        ws.append_rows(rows, value_input_option="USER_ENTERED")

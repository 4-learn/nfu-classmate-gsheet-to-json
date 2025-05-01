import os
import json
import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

# === 環境與認證 ===
load_dotenv()
SHEET_ID = os.getenv("SHEET_ID")  # 同樣用原本的 Sheet
CREDENTIAL_PATH = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
SHEET_NAME = os.getenv("FEATURE_MAPPING_SHEET", "對應表")  # 分頁名稱建議：對應表

# === 授權與存取 ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIAL_PATH, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# === 讀取資料 ===
rows = sheet.get_all_records()

# === 轉換為 nested dict ===
feature_mapping = {}

for row in rows:
    category = row.get("屬性 (category)", "").strip()
    keyword = row.get("值 (keyword)", "").strip()
    aliases_str = row.get("對應詞彙 (aliases)", "").strip()

    if not category or not keyword:
        continue

    aliases = [a.strip() for a in aliases_str.split(",") if a.strip()]

    if category not in feature_mapping:
        feature_mapping[category] = {}

    feature_mapping[category][keyword] = aliases

# === 輸出 JSON ===
output_path = os.path.join(os.path.dirname(__file__), "feature_mapping.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(feature_mapping, f, ensure_ascii=False, indent=2)

print(f"✅ 已匯出 feature_mapping.json，共 {len(feature_mapping)} 類別")

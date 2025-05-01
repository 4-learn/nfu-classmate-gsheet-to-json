import base64
import os
import json
import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

# === 環境與認證 ===
load_dotenv()
SHEET_ID = os.getenv("SHEET_ID")  # 你的 Google Sheet ID
SHEET_NAME = os.getenv("SHEET_NAME", "工作表1")
CREDENTIAL_PATH = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")  # 認證 JSON 路徑

# === 授權與存取 ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIAL_PATH, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# === 讀取資料 ===
rows = sheet.get_all_records()

# === 整理為 location_db 結構 ===
location_dict = {}

for row in rows:
    name = row.get("地點名稱 (name)", "").strip()
    if not name:
        continue

    # 建立初始地點
    if name not in location_dict:
        location_dict[name] = {
            "name": name,
            "style": row.get("建築風格 (style)", "").strip(),
            "structure": row.get("建築結構 (struct)", "").strip(),
            "roof": row.get("roof (屋頂類型)", "").strip(),
            "function": row.get("功能用途 (function)", "").strip(),
            "summary": row.get("簡介 (summary)", "").strip(),
            "interview": []
        }

    speaker = row.get("與談人 (speaker)", "").strip()
    content = row.get("訪談內容 (content)", "").strip()
    topics_str = row.get("主題 (topics)", "").strip()

    if speaker and content:
        interview_entry = {
            "speaker": speaker,
            "content": content,
            "topics": [t.strip() for t in topics_str.split(",") if t.strip()]
        }
        location_dict[name]["interview"].append(interview_entry)

# === 輸出 JSON ===
output_path = os.path.join(os.path.dirname(__file__), "location_db.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(list(location_dict.values()), f, ensure_ascii=False, indent=2)

print(f"✅ 已匯出 {len(location_dict)} 筆地點資料到 location_db.json")


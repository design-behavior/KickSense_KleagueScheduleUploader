import os
import requests
from bs4 import BeautifulSoup
import json
import firebase_admin
from firebase_admin import credentials, storage

# ──────────────────────────────
# 1️⃣ 일정 파싱
# ──────────────────────────────
URL = "https://www.kleague.com/schedule.do"
headers = {
    "User-Agent": "Mozilla/5.0",
}

res = requests.get(URL, headers=headers)
soup = BeautifulSoup(res.text, "html.parser")

matches = []
for row in soup.select(".match_schedule > tbody > tr"):
    cols = row.find_all("td")
    if len(cols) >= 5:
        matches.append({
            "date": cols[0].get_text(strip=True),
            "time": cols[1].get_text(strip=True),
            "home": cols[2].get_text(strip=True),
            "away": cols[4].get_text(strip=True),
            "stadium": cols[3].get_text(strip=True)
        })

filename = "kleague_schedule.json"
with open(filename, "w", encoding="utf-8") as f:
    json.dump(matches, f, ensure_ascii=False, indent=2)

print(f"✅ JSON 저장 완료: {filename}")

# ──────────────────────────────
# 2️⃣ Firebase 업로드
# ──────────────────────────────

# 환경변수로 버킷 이름 받기 (YAML의 env에서 FIREBASE_BUCKET)
bucket_name = os.environ.get("FIREBASE_BUCKET", "kicksense-19c1d.appspot.com")

cred = credentials.Certificate("serviceAccountKey.json")

# ⚡ 중복 초기화 방지
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        "storageBucket": bucket_name
    })

bucket = storage.bucket()
blob = bucket.blob(f"schedules/{filename}")
blob.upload_from_filename(filename)

print(f"✅ Firebase 업로드 완료: gs://{bucket_name}/schedules/{filename}")

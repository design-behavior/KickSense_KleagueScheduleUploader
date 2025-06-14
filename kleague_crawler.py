import requests
from bs4 import BeautifulSoup
import json
import firebase_admin
from firebase_admin import credentials, storage

# 파싱
URL = "https://www.kleague.com/schedule.do"
headers = {
    "User-Agent": "Mozilla/5.0",
}

res = requests.get(URL, headers=headers)
soup = BeautifulSoup(res.text, "html.parser")

# 예시: 일정 데이터 추출
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

# JSON 저장
filename = "kleague_schedule.json"
with open(filename, "w", encoding="utf-8") as f:
    json.dump(matches, f, ensure_ascii=False, indent=2)

# Firebase 업로드
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {"storageBucket": "kicksense-19c1d.appspot.com"})
bucket = storage.bucket()
blob = bucket.blob(f"schedules/{filename}")
blob.upload_from_filename(filename)
print(f"업로드 완료: {filename}")

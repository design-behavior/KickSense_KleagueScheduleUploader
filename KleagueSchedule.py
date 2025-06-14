import requests
import json
import firebase_admin
from firebase_admin import credentials, storage
from datetime import datetime

# ✅ 1) K리그 경기 일정 크롤링 함수
def fetch_kleague_schedule(season, month, league_id):
    url = 'https://www.kleague.com/api/schedule/getScheduleList'
    headers = {'Content-Type': 'application/json'}
    payload = {
        'season': season,
        'month': f'{month:02}',
        'leagueId': str(league_id)
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"요청 실패: {response.status_code}")
        return None

# ✅ 2) Firebase Storage에 업로드 함수
def upload_to_firebase(file_path, bucket_name, remote_path, firebase_key_json):
    cred = credentials.Certificate(firebase_key_json)
    firebase_admin.initialize_app(cred, {'storageBucket': bucket_name})

    bucket = storage.bucket()
    blob = bucket.blob(remote_path)
    blob.upload_from_filename(file_path)
    print(f"업로드 완료: {remote_path}")

# ✅ 3) 메인 로직
def main():
    season = datetime.now().year
    month = datetime.now().month

    for league_id in [1, 2]:  # K리그1, K리그2
        data = fetch_kleague_schedule(season, month, league_id)
        if data:
            filename = f"kleague_{season}_{month:02}_league{league_id}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"{filename} 저장 완료")

            # Firebase 업로드
            upload_to_firebase(
                file_path=filename,
                bucket_name="YOUR_FIREBASE_BUCKET.appspot.com",
                remote_path=f"schedules/{filename}",
                firebase_key_json="serviceAccountKey.json"
            )

if __name__ == "__main__":
    main()

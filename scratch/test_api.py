import requests
import json

url = "https://fanqienovel.com/api/rank/category/list"
params = {
    "app_id": "1967",
    "rank_list_type": "3",
    "category_id": "7",  # 现代言情
    "gender": "female",
    "rankMold": "daily",
    "offset": "0",
    "limit": "30",
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://fanqienovel.com/rank",
}

try:
    resp = requests.get(url, params=params, headers=headers, timeout=15)
    print("Status Code:", resp.status_code)
    print("Response JSON:", json.dumps(resp.json(), ensure_ascii=False, indent=2)[:2000])
except Exception as e:
    print("Error:", e)

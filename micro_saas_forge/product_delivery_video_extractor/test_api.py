import requests
import json

vid = "7611737202434964657"
url = f"https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id={vid}&device_platform=webapp&aid=6383"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://www.douyin.com/",
    "Cookie": "msToken=1;" # dummy cookie to bypass basic auth
}

r = requests.get(url, headers=headers)
print("Status:", r.status_code)
try:
    data = r.json()
    print("Has aweme_detail:", "aweme_detail" in data)
    if "aweme_detail" in data:
        video_data = data["aweme_detail"]["video"]
        play_addr = video_data.get("play_addr", {})
        url_list = play_addr.get("url_list", [])
        if url_list:
            print("Found URL:", url_list[0])
        else:
            print("No URL list")
except Exception as e:
    print("Error:", e, r.text[:100])

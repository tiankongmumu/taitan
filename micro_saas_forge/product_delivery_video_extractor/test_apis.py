import requests

url = "https://v.douyin.com/MV0gw4XWdeY/"

apis = [
    f"https://api.qqsuu.cn/api/dm-douyin?url={url}",
    f"https://api.oick.cn/api/douyin?url={url}",
    f"https://api.gumengya.com/Api/DongYin?format=json&url={url}",
    f"https://api.yujn.cn/api/douyin?url={url}"
]

for api in apis:
    print(f"\nTesting: {api}")
    try:
        r = requests.get(api, timeout=5)
        print("Status Code:", r.status_code)
        try:
            data = r.json()
            print("Response:", list(data.keys())[:5], str(data)[:100])
        except Exception as e:
            print("JSON parsing failed", e, r.text[:100])
    except Exception as e:
        print("Request failed:", e)

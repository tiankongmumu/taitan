import requests

url = "https://v.douyin.com/MV0gw4XWdeY/"

# Test tenapi
api_url = f"https://tenapi.cn/v2/video?url={url}"

r = requests.get(api_url)
print(r.status_code)
try:
    data = r.json()
    print("Code:", data.get("code"))
    print("Msg:", data.get("msg"))
    if "data" in data:
        print("Title:", data["data"].get("title"))
        print("Video URL:", data["data"].get("url"))
except Exception as e:
    print("Error:", e, r.text)

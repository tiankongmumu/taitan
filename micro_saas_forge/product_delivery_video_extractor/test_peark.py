import requests

url = "https://v.douyin.com/MV0gw4XWdeY/"

# Test Pearktrue API
api_url = f"https://api.pearktrue.cn/api/video/watermark.php?url={url}"

r = requests.get(api_url)
print(r.status_code)
try:
    data = r.json()
    print("Code:", data.get("code"))
    print("Msg:", data.get("msg"))
    if "data" in data:
        print("Title:", data["data"].get("title"))
        print("Video URL:", data["data"].get("video"))
except Exception as e:
    print("Error:", e, r.text)


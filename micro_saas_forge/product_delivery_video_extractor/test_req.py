import requests
import re
import urllib.parse
import time

url = 'https://v.douyin.com/MV0gw4XWdeY/'
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
try:
    print("1. 获取重定向")
    r = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
    real_url = r.url
    print("Real URL:", real_url)
    
    vid_match = re.search(r'video/(\d+)', real_url)
    print("VID MATCH:", vid_match)
    if not vid_match:
        print("未找到视频ID")
        exit()
        
    print("2. 提取网页源码")
    r2 = requests.get(real_url, headers=headers, timeout=10)
    print("Source len:", len(r2.text))
    
    uri_match = re.search(r'"uri"\s*:\s*"([^"]+)"', r2.text)
    print("URI Match:", uri_match)
    if uri_match:
        print("Found URI:", uri_match.group(1))
    
    playwm_match = re.search(r'(https://[^"]*playwm[^"]*)', r2.text)
    print("Playwm Match:", playwm_match)
    if playwm_match:
        raw_wm = urllib.parse.unquote(playwm_match.group(1)).replace('\\u0026', '&')
        print("Found Playwm:", raw_wm)

except Exception as e:
    print("Error:", e)

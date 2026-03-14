import requests
import re
import urllib.parse
import json

url = 'https://v.douyin.com/MV0gw4XWdeY/'
headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Sec-Fetch-Mode": "navigate",
}

try:
    r = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
    real_url = r.url
    print("Real URL:", real_url)
    
    r2 = requests.get(real_url, headers=headers, timeout=10)
    html = r2.text
    print("HTML len:", len(html))
    
    # 查找 window._ROUTER_DATA 或者 index.js
    router = re.search(r'window\._ROUTER_DATA\s*=\s*(.*?);</script>', html)
    if router:
        # print(router.group(1)[:200])
        print("Found _ROUTER_DATA!")
        data = json.loads(router.group(1))
        # Find playAddr
        print(str(data)[:500])
    else:
        print("No ROUTER_DATA")
        
    start_tag = '<script id="RENDER_DATA"'
    if start_tag in html:
        print("Found RENDER_DATA!")
    else:
        print("No RENDER_DATA")
        
    # Find playwm
    playwm_match = re.search(r'(https://[^"]*playwm[^"]*)', html)
    if playwm_match:
        print("Found Playwm:", playwm_match.group(1))

except Exception as e:
    print("Error:", e)

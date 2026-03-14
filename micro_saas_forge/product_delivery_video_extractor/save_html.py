import requests

url = 'https://v.douyin.com/MV0gw4XWdeY/'
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
try:
    r = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
    real_url = r.url
    
    r2 = requests.get(real_url, headers=headers, timeout=10)
    
    with open("dy_html.txt", "w", encoding="utf-8") as f:
        f.write(r2.text)
        
    print("Done writing HTML.")
    
except Exception as e:
    print("Error:", e)

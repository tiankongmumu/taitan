import urllib.parse
import json

try:
    with open('dy_html.txt', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Douyin injects state into <script id="RENDER_DATA" type="application/json">...</script>
    start_tag = '<script id="RENDER_DATA" type="application/json">'
    end_tag = '</script>'
    
    if start_tag in html:
        start_idx = html.find(start_tag) + len(start_tag)
        end_idx = html.find(end_tag, start_idx)
        json_data = html[start_idx:end_idx]
        
        # It's URL-encoded
        decoded_data = urllib.parse.unquote(json_data)
        data = json.loads(decoded_data)
        
        # We need to find the aweme_detail or similar
        # Find play_addr
        for key, value in data.items():
            if isinstance(value, dict) and 'aweme' in value:
                aweme = value['aweme']
                if 'detail' in aweme:
                    video = aweme['detail'].get('video', {})
                    play_addr = video.get('playAddr', [])
                    if play_addr:
                        print("Found PlayAddr in RENDER_DATA:")
                        for p in play_addr:
                            print(p['src'])
                        break
        print("Done Parse RENDER_DATA")
    else:
        print("RENDER_DATA script not found.")
except Exception as e:
    print("Error:", e)

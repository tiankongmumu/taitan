import base64
import json
import urllib.parse
import os

raw_base64 = "c3M6Ly9ZV1Z6TFRJMU5pMW5ZMjA2T1hJMldEbE9lRzgzUlRreWVHRklTa0EyTnk0eU1UWXVNVGsxTGpjeE9qRTRPVFl6I0pNUy0xMzI3NzE2QGM5M3MxLnBvcnRhYmxlc3VibWFyaW5lcy5jb206MTg5NjMKc3M6Ly9ZV1Z6TFRJMU5pMW5ZMjA2T1hJMldEbE9lRzgzUlRreWVHRklTa0EyTnk0eU1UWXVNVGs0TGpVeE9qRTRPVFl6I0pNUy0xMzI3NzE2QGM5M3MyLnBvcnRhYmxlc3VibWFyaW5lcy5jb206MTg5NjMKdm1lc3M6Ly9leUp3Y3lJNklrcE5VeTB4TXpJM056RTJRR001TTNNekxuQnZjblJoWW14bGMzVmliV0Z5YVc1bGN5NWpiMjA2TVRnNU5qTWlMQ0p3YjNKMElqb2lNVGc1TmpNaUxDSnBaQ0k2SWpBeVlqTXdZelpqTFdNd016UXRORGs0WlMxaE9UTmpMV1JpWVdRd1pqZzRaR1E1WlNJc0ltRnBaQ0k2TUN3aWJtVjBJam9pZEdOd0lpd2lkSGx3WlNJNkltNXZibVVpTENKMGJITWlPaUp1YjI1bElpd2lZV1JrSWpvaU1UazRMak0xTGpRMUxqRXhOeUo5CnZtZXNzOi8vZXlKd2N5STZJa3BOVXkweE16STNOekUyUUdNNU0zTTBMbkJ2Y25SaFlteGxjM1ZpYldGeWFXNWxjeTVqYjIwNk1UZzVOak1pTENKd2IzSjBJam9pTVRnNU5qTWlMQ0pwWkNJNklqQXlZak13WXpaakxXTXdNelF0TkRrNFpTMWhPVE5qTFdSaVlXUXdaamc0WkdRNVpTSXNJbUZwWkNJNk1Dd2libVYwSWpvaWRHTndJaXdpZEhsd1pTSTZJbTV2Ym1VaUxDSjBiSE1pT2lKdWIyNWxJaXdpWVdSa0lqb2lORFV1TnpndU5UWXVNemNpZlEKdm1lc3M6Ly9leUp3Y3lJNklrcE5VeTB4TXpJM056RTJRR001TTNNMUxuQnZjblJoWW14bGMzVmliV0Z5YVc1bGN5NWpiMjA2TVRnNU5qTWlMQ0p3YjNKMElqb2lNVGc1TmpNaUxDSnBaQ0k2SWpBeVlqTXdZelpqTFdNd016UXRORGs0WlMxaE9UTmpMV1JpWVdRd1pqZzRaR1E1WlNJc0ltRnBaQ0k2TUN3aWJtVjBJam9pZEdOd0lpd2lkSGx3WlNJNkltNXZibVVpTENKMGJITWlPaUp1YjI1bElpd2lZV1JrSWpvaU1UQTBMakkwTlM0NU5pNDFOaUo5CnZtZXNzOi8vZXlKd2N5STZJa3BOVXkweE16STNOekUyUUdNNU0zTTRNREV1Y0c5eWRHRmliR1Z6ZFdKdFlYSnBibVZ6TG1OdmJUb3hPRGsyTXlJc0luQnZjblFpT2lJeE9EazJNeUlzSW1sa0lqb2lNREppTXpCak5tTXRZekF6TkMwME9UaGxMV0U1TTJNdFpHSmhaREJtT0Roa1pEbGxJaXdpWVdsa0lqb3dMQ0p1WlhRaU9pSjBZM0FpTENKMGVYQmxJam9pYm05dVpTSXNJblJzY3lJNkltNXZibVVpTENKaFpHUWlPaUkwTlM0Mk1pNHhNRFl1TVRneUluMA=="

decoded_text = base64.b64decode(raw_base64).decode('utf-8')

proxies = []
for line in decoded_text.split('\n'):
    line = line.strip()
    if not line: continue
    
    if line.startswith('ss://'):
        raw = line.replace('ss://', '')
        name = ''
        if '#' in raw:
            parts = raw.split('#')
            name = urllib.parse.unquote(parts[1])
            raw = parts[0]
            
        if '@' in raw:
            at_split = raw.split('@')
            try:
                padded = at_split[0] + '=' * ((4 - len(at_split[0]) % 4) % 4)
                method_pass = base64.b64decode(padded).decode('utf-8')
            except:
                method_pass = at_split[0]
            server_port = at_split[1]
        else:
            try:
                padded = raw + '=' * ((4 - len(raw) % 4) % 4)
                decoded_raw = base64.b64decode(padded).decode('utf-8')
                at_split = decoded_raw.split('@')
                method_pass = at_split[0]
                server_port = at_split[1]
            except Exception as e:
                continue
                
        mp_split = method_pass.split(':')
        method = mp_split[0]
        password = ':'.join(mp_split[1:])
        
        sp_split = server_port.split(':')
        server = sp_split[0]
        port = int(sp_split[1])
        
        proxies.append({'name': name or f'SS-{server}', 'type': 'ss', 'server': server, 'port': port, 'cipher': method, 'password': password})
        
    elif line.startswith('vmess://'):
        raw = line.replace('vmess://', '')
        try:
            padded = raw + '=' * ((4 - len(raw) % 4) % 4)
            json_str = base64.b64decode(padded).decode('utf-8')
            conf = json.loads(json_str)
            p_name = urllib.parse.unquote(conf.get('ps', '')) or f"Vmess-{conf.get('add', '')}"
            proxies.append({
                'name': p_name,
                'type': 'vmess',
                'server': conf.get('add'),
                'port': int(conf.get('port')),
                'uuid': conf.get('id'),
                'alterId': int(conf.get('aid', 0)),
                'cipher': conf.get('scy', 'auto'),
                'network': conf.get('net', 'tcp'),
                'tls': conf.get('tls') == 'tls',
                'servername': conf.get('host', '') or conf.get('sni', ''),
                'path': conf.get('path', '/'),
                'host': conf.get('host', '')
            })
        except:
            continue

with open('d:/Project/1/micro_saas_forge/jms-clash-v2.yaml', 'w', encoding='utf-8') as f:
    f.write('port: 7890\n')
    f.write('socks-port: 7891\n')
    f.write('allow-lan: true\n')
    f.write('mode: Rule\n')
    f.write('log-level: info\n')
    f.write('external-controller: 127.0.0.1:9090\n\n')
    f.write('proxies:\n')
    for p in proxies:
        f.write(f'  - name: "{p["name"]}"\n')
        f.write(f'    type: {p["type"]}\n')
        f.write(f'    server: {p["server"]}\n')
        f.write(f'    port: {p["port"]}\n')
        if p["type"] == 'ss':
            f.write(f'    cipher: {p["cipher"]}\n')
            f.write(f'    password: {p["password"]}\n')
        elif p["type"] == 'vmess':
            f.write(f'    uuid: {p["uuid"]}\n')
            f.write(f'    alterId: {p["alterId"]}\n')
            f.write(f'    cipher: {p["cipher"]}\n')
            if p["network"] != 'tcp': f.write(f'    network: {p["network"]}\n')
            if p["tls"]: f.write('    tls: true\n')
            if p["servername"]: f.write(f'    servername: {p["servername"]}\n')
            if p["network"] == 'ws':
                f.write('    ws-opts:\n')
                f.write(f'      path: {p["path"]}\n')
                if p["host"]:
                    f.write('      headers:\n')
                    f.write(f'        Host: {p["host"]}\n')
                    
    names = [p['name'] for p in proxies]
    f.write('\nproxy-groups:\n')
    f.write('  - name: "🚀 PROXY"\n')
    f.write('    type: select\n')
    f.write('    proxies:\n')
    f.write('      - "♻️ DIRECT"\n')
    f.write('      - "🌐 Auto-URLTest"\n')
    for n in names: f.write(f'      - "{n}"\n')
    
    f.write('\n  - name: "🌐 Auto-URLTest"\n')
    f.write('    type: url-test\n')
    f.write('    url: http://www.gstatic.com/generate_204\n')
    f.write('    interval: 300\n')
    f.write('    proxies:\n')
    for n in names: f.write(f'      - "{n}"\n')
    
    f.write('\nrules:\n')
    f.write('  - DOMAIN-SUFFIX,google.com,🚀 PROXY\n')
    f.write('  - DOMAIN-SUFFIX,github.com,🚀 PROXY\n')
    f.write('  - DOMAIN-KEYWORD,twitter,🚀 PROXY\n')
    f.write('  - DOMAIN-SUFFIX,cn,♻️ DIRECT\n')
    f.write('  - GEOIP,CN,♻️ DIRECT\n')
    f.write('  - MATCH,🚀 PROXY\n')

print(f"SUCCESS {len(proxies)}")

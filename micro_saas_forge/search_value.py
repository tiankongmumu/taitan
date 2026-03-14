import os
import lark_oapi
import lark_oapi.ws

ws_dir = os.path.dirname(lark_oapi.ws.__file__)
for root, dirs, files in os.walk(ws_dir):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8') as f_in:
                    for i, line in enumerate(f_in):
                        if '.value' in line:
                            print(f"{path}:{i+1}: {line.strip()}")
            except:
                pass

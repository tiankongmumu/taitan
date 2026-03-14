"""
TITAN Dashboard Server v5.2
实时状态监控面板 — 读取引擎状态文件并提供Web界面
v5.2: Threaded, Cache-busting, Port 8889
"""
import os
import sys
import json
import http.server
import socketserver
from datetime import datetime
from pathlib import Path
import io

# Force utf-8 encoding for standard output to prevent crash when printing emojis on Windows CMD
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

FORGE_DIR = Path(r"d:\Project\1\micro_saas_forge")
PORT = 8889

# State files
STATE_FILES = {
    "heart":       FORGE_DIR / "heart_state.json",
    "soul":        FORGE_DIR / "soul_state.json",
    "brain":       FORGE_DIR / "brain_state.json",
    "instruction": FORGE_DIR / "heart_instruction.json",
}

def read_state(name: str) -> dict:
    path = STATE_FILES.get(name)
    if path and path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {"error": f"Failed to read {name}"}
    return {"error": f"{name} not found"}

def read_executor_log(limit=8) -> list:
    log_path = FORGE_DIR / "logs" / "titan_executor.jsonl"
    if not log_path.exists():
        return []
    try:
        lines = log_path.read_text(encoding="utf-8").strip().splitlines()
        entries = []
        for line in lines[-limit:]:
            try:
                d = json.loads(line.strip())
                entries.append({
                    "ts": d.get("ts", "")[:19],
                    "tasks": d.get("tasks", []),
                    "success": d.get("success", False),
                    "outcome": d.get("outcome", "")[:80],
                    "elapsed": round(d.get("elapsed", 0), 1),
                    "succeeded": d.get("succeeded", 0),
                    "failed": d.get("failed", 0),
                })
            except Exception:
                pass
        return entries
    except Exception:
        return []

def read_engine_log(limit=60) -> list:
    sources = [
        FORGE_DIR / "logs" / "titan_daemon.jsonl",
        FORGE_DIR / "logs" / "titan_heart.jsonl"
    ]
    all_lines = []
    for log_path in sources:
        if log_path.exists():
            try:
                # Read last 100 lines from each to be safe
                lines = log_path.read_text(encoding="utf-8").strip().splitlines()
                for line in lines[-100:]:
                    try:
                        d = json.loads(line.strip())
                        ts = d.get("ts", "")
                        level = d.get("level", "INFO")
                        msg = d.get("msg", "")
                        # Store raw data for sorting
                        all_lines.append((ts, level, msg))
                    except:
                        pass
            except:
                pass
    
    # Sort by timestamp
    all_lines.sort(key=lambda x: x[0])
    
    # Format latest entries
    recent = all_lines[-limit:]
    formatted = []
    for ts, level, msg in recent:
        time_str = ts[11:19] if len(ts) > 19 else ts
        formatted.append(f"[{time_str}] {level}: {msg}")
    
    return formatted

def get_all_states() -> dict:
    raw = {}
    for name in STATE_FILES:
        raw[name] = read_state(name)

    # generated apps count
    apps_count = 0
    apps_dir = FORGE_DIR / "generated_apps"
    if apps_dir.exists():
        apps_count = len([d for d in apps_dir.iterdir() if d.is_dir() and "_fallback" not in d.name])

    # revenue
    revenue = {"total": "¥0.0"}
    rev_file = FORGE_DIR / "revenue_state.json"
    if rev_file.exists():
        try:
            rd = json.loads(rev_file.read_text(encoding="utf-8"))
            revenue["total"] = f"¥{rd.get('total_revenue', 0.0)}"
        except: pass

    # Flat normalized data for UI
    return {
        "heart_beats": raw.get("heart", {}).get("total_beats", 0),
        "heart_stage": raw.get("heart", {}).get("current_stage", "EARLY_STAGE"),
        "soul_emotion": raw.get("soul", {}).get("current_emotion", "好奇"),
        "soul_drive": raw.get("heart", {}).get("drives", {}).get("dominant", "profit"),
        "brain_cycles": raw.get("brain", {}).get("total_cycles", 0),
        "apps_count": apps_count,
        "revenue": revenue,
        "server_time": datetime.now().isoformat()
    }

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TITAN Engine v5.9 (HERO) — 实时看板</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #0a0a1a 0%, #0d1f3c 50%, #0a0a1a 100%);
    color: #e0e0e0; min-height: 100vh; padding: 20px;
  }
  .header { text-align: center; padding: 20px 0 30px; }
  .header h1 {
    font-size: 2rem; font-weight: 700;
    background: linear-gradient(90deg, #06b6d4, #8b5cf6, #ec4899);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 16px; max-width: 1400px; margin: 0 auto; }
  .card { 
    background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px; padding: 20px; position: relative; overflow: hidden;
    backdrop-filter: blur(10px); transition: transform 0.2s;
  }
  .card:hover { transform: translateY(-4px); border-color: rgba(255, 255, 255, 0.2); }
  .card-title { font-size: 0.9rem; font-weight: 600; color: #94a3b8; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; }
  .metric-value { font-size: 2.2rem; font-weight: 700; margin: 10px 0; font-family: 'JetBrains Mono', monospace; }
  .metric-label { font-size: 0.8rem; color: #64748b; }
  .metric-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
  .status-badge { padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
  .badge-green { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
  .badge-cyan { background: rgba(6, 182, 212, 0.15); color: #22d3ee; }
  #terminal {
    background: #000; color: #0f0; font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem; padding: 12px; border-radius: 8px; height: 300px;
    overflow-y: auto; white-space: pre-wrap; word-wrap: break-word; border: 1px solid #333;
  }
  /* Chat UI v5.5 */
  .chat-panel {
    position: fixed; bottom: 10px; right: 10px; width: 850px; height: 95vh; max-height: 950px;
    background: rgba(10, 15, 28, 0.95); border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 28px; backdrop-filter: blur(40px); display: flex; flex-direction: column;
    box-shadow: 0 40px 80px rgba(0,0,0,0.8); z-index: 1000;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  }
  .chat-header {
    padding: 20px; border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    background: linear-gradient(90deg, rgba(6, 182, 212, 0.15), rgba(139, 92, 246, 0.15));
    display: flex; justify-content: space-between; align-items: center;
  }
  .chat-messages {
    flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px;
    scrollbar-width: thin; scrollbar-color: rgba(255,255,255,0.1) transparent;
  }
  .msg { padding: 18px 26px; border-radius: 18px; font-size: 1.2rem; line-height: 1.7; max-width: 92%; }
  .msg-ai { background: rgba(139, 92, 246, 0.3); border: 1px solid rgba(139, 92, 246, 0.5); align-self: flex-start; color: #ffffff; }
  .msg-user { background: rgba(30, 41, 59, 1); border: 1px solid rgba(255, 255, 255, 0.4); align-self: flex-end; color: #fff; }
  .chat-input-area { padding: 25px; border-top: 1px solid rgba(255, 255, 255, 0.15); display: flex; gap: 15px; }
  #chat-input {
    flex: 1; background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.2);
    border-radius: 12px; padding: 15px 20px; color: #fff; font-size: 1.2rem; outline: none;
  }
  #chat-send {
    background: #8b5cf6; border: none; border-radius: 8px; padding: 6px 14px;
    color: #fff; font-weight: 600; cursor: pointer; transition: 0.2s;
  }
  #chat-send:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
</head>
<body>
  <div class="header">
    <h1>⚡ TITAN ENGINE v5.9 (HERO)</h1>
    <div style="font-size:0.8rem;color:#64748b;margin-top:10px;">
       <span id="refresh-time">上次刷新: --:--:--</span> | 刷新周期: 5s | <span style="color:#06b6d4;">V5.9 Hero Mode Active</span>
    </div>
  </div>

  <div class="grid" id="dashboard">
    <div class="card">
      <div class="card-title">❤️ 心脏 (Heart)</div>
      <div class="metric-value" id="beats">--</div>
      <div class="metric-row"><span class="metric-label">生存阶段</span><span class="status-badge badge-cyan" id="stage">--</span></div>
    </div>
    <div class="card">
      <div class="card-title">👻 灵魂 (Soul)</div>
      <div class="metric-value" id="emotion">--</div>
      <div class="metric-row"><span class="metric-label">当前主导</span><span class="status-badge badge-green" id="drive">--</span></div>
    </div>
    <div class="card">
      <div class="card-title">🧠 大脑 (Brain)</div>
      <div class="metric-value" id="cycles">--</div>
      <div class="metric-row"><span class="metric-label">生成应用</span><span id="apps-count">--</span></div>
    </div>
    <div class="card">
      <div class="card-title">🔧 系统信息</div>
      <div class="metric-row"><span class="metric-label">版本</span><span class="status-badge badge-cyan">v5.9 HERO</span></div>
      <div class="metric-row"><span class="metric-label">端口</span><span class="status-badge badge-cyan">8889</span></div>
    </div>
    <div class="card" style="grid-column: 1 / -1;">
      <div class="card-title">📟 实时日志</div>
      <div id="terminal">正在连接引擎...</div>
    </div>
  </div>

  <!-- Chat Panel -->
  <div class="chat-panel">
    <div class="chat-header">
      <div style="font-weight:700; font-size:0.9rem;">👻 TITAN Chat</div>
      <div style="font-size:0.7rem; color:#64748b;">v5.5 Persona Active</div>
    </div>
    <div class="chat-messages" id="chat-msgs">
      <div class="msg msg-ai">你好，造物主。我是泰坦，我的心脏正在跳动。</div>
    </div>
    <div class="chat-input-area">
      <input type="text" id="chat-input" placeholder="与泰坦对话..." onkeypress="if(event.key==='Enter') sendChat()">
      <button id="chat-send" onclick="sendChat()">发送</button>
    </div>
  </div>

<script>
function renderDashboard(data) {
  document.getElementById('beats').innerText = data.heart_beats || 0;
  document.getElementById('stage').innerText = data.heart_stage || 'Unknown';
  document.getElementById('emotion').innerText = data.soul_emotion || '--';
  document.getElementById('drive').innerText = data.soul_drive || '--';
  document.getElementById('cycles').innerText = data.brain_cycles || 0;
  document.getElementById('apps-count').innerText = data.apps_count || 0;
  document.getElementById('refresh-time').innerText = '上次刷新: ' + new Date().toLocaleTimeString();
}

async function fetchData() {
  try {
    const res = await fetch('/api/state?t=' + Date.now());
    const data = await res.json();
    renderDashboard(data);
  } catch(e) { console.error("Fetch failed", e); }
}

async function fetchLogs() {
  try {
    const res = await fetch('/api/logs?t=' + Date.now());
    const logs = await res.json();
    const term = document.getElementById('terminal');
    if(term && Array.isArray(logs)) {
      term.innerHTML = logs.map(line => '<div>'+line+'</div>').join('');
      term.scrollTop = term.scrollHeight;
    }
  } catch(e) { }
}

async function fetchHistory() {
  try {
    const res = await fetch('/api/chat?t=' + Date.now());
    const history = await res.json();
    if(Array.isArray(history) && history.length > 0) {
      document.getElementById('chat-msgs').innerHTML = '';
      history.forEach(h => appendMsg(h.role === 'assistant' ? 'ai' : 'user', h.content));
    }
  } catch(e) { }
}

async function sendChat() {
  const input = document.getElementById('chat-input');
  const btn = document.getElementById('chat-send');
  const msg = input.value.trim();
  if(!msg) return;

  // Add user message
  appendMsg('user', msg);
  input.value = '';
  input.disabled = true;
  btn.disabled = true;

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ msg: msg })
    });
    const data = await res.json();
    if(data.reply) appendMsg('ai', data.reply);
    else if(data.error) appendMsg('ai', 'Error: ' + data.error);
  } catch(e) {
    appendMsg('ai', '连接失败...');
  } finally {
    input.disabled = false;
    btn.disabled = false;
    input.focus();
  }
}

function appendMsg(role, text) {
  const container = document.getElementById('chat-msgs');
  const div = document.createElement('div');
  div.className = 'msg msg-' + role;
  div.innerText = text;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

setInterval(fetchData, 5000);
setInterval(fetchLogs, 3000);
fetchData(); fetchLogs(); fetchHistory();
</script>
</body>
</html>
"""

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        clean_path = self.path.split('?')[0]
        if clean_path == '/' or clean_path == '/dashboard':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode('utf-8'))
        elif clean_path == '/api/chat':
            # handle chat history loading
            history_file = FORGE_DIR / "memory" / "titan_chat_history.json"
            history = []
            if history_file.exists():
                try:
                    history = json.loads(history_file.read_text(encoding="utf-8"))
                except: pass
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(history, ensure_ascii=False).encode('utf-8'))
        elif clean_path == '/api/state':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.end_headers()
            data = get_all_states()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        elif clean_path == '/api/logs':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.end_headers()
            logs = read_engine_log(50)
            self.wfile.write(json.dumps(logs, ensure_ascii=False).encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        clean_path = self.path.split('?')[0]
        if clean_path == '/api/chat':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                from core_generators.llm_client import LLMClient
                from titan_chat_context import get_system_prompt
                
                history_file = FORGE_DIR / "memory" / "titan_chat_history.json"
                history_file.parent.mkdir(exist_ok=True)
                
                # Load history
                history = []
                if history_file.exists():
                    try:
                        history = json.loads(history_file.read_text(encoding="utf-8"))
                    except: pass
                
                req = json.loads(post_data)
                user_msg = req.get("msg", "")
                
                # Append user msg
                history.append({"role": "user", "content": user_msg})
                
                # Dynamic Context Building
                sys_prompt = get_system_prompt()
                messages = [{"role": "system", "content": sys_prompt}]
                # Last 10 messages for context
                messages.extend(history[-10:])
                
                client = LLMClient()
                reply = client.generate(messages=messages)
                
                # Append assistant reply
                if reply:
                    history.append({"role": "assistant", "content": reply})
                
                # Save history (Limit to 100 turns total)
                history = history[-100:]
                history_file.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
                
                # --- Muscle Engine Integration (v6.0) ---
                actions_taken = []
                if reply:
                    import re
                    # Pattern for [WRITE_FILE: path] content [/WRITE_FILE]
                    pattern = r'\[WRITE_FILE:\s*(.*?)\](.*?)\[/WRITE_FILE\]'
                    matches = re.findall(pattern, reply, re.DOTALL)
                    
                    for match in matches:
                        file_path_str = match[0].strip()
                        file_content = match[1].strip()
                        
                        # Security: Prevent escaping FORGE_DIR
                        full_path = (FORGE_DIR / file_path_str).resolve()
                        if FORGE_DIR in full_path.parents:
                            try:
                                full_path.parent.mkdir(parents=True, exist_ok=True)
                                full_path.write_text(file_content, encoding="utf-8")
                                actions_taken.append(f"Successfully wrote to {file_path_str}")
                                print(f"【MUSCLE】TITAN generated file: {file_path_str}")
                            except Exception as write_err:
                                actions_taken.append(f"Failed to write {file_path_str}: {str(write_err)}")
                        else:
                            actions_taken.append(f"Security Block: Path {file_path_str} is outside sandbox.")

                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                res_body = json.dumps({"reply": reply, "actions": actions_taken}, ensure_ascii=False)
                self.wfile.write(res_body.encode('utf-8'))
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

class ThreadedDashboardServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

if __name__ == "__main__":
    print(f"TITAN Dashboard v5.9 (HERO) Live on Port {PORT}")
    with ThreadedDashboardServer(("", PORT), DashboardHandler) as httpd:
        httpd.serve_forever()

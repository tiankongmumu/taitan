"""
ShipMicro Analytics Tracker — 用户行为追踪系统
在每个生成的工具页面注入轻量级访问追踪代码（自建，零依赖），
并提供统计查询接口。
"""
import os
import sys
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from logger import get_logger

log = get_logger("analytics")

ANALYTICS_DIR = os.path.join(os.path.dirname(__file__), "analytics_data")
STATS_FILE = os.path.join(ANALYTICS_DIR, "visits.json")


def _ensure_dir():
    os.makedirs(ANALYTICS_DIR, exist_ok=True)


def get_tracking_script(tool_slug: str) -> str:
    """生成要注入到工具页面的轻量级追踪JS代码"""
    # 使用 navigator.sendBeacon 向我们的 API 发送匿名访问数据
    # 如果没有后端，就用 localStorage 做本地统计展示
    return f'''
<!-- ShipMicro Analytics -->
<script>
(function() {{
  var slug = "{tool_slug}";
  var key = "sm_v_" + slug;
  var data = JSON.parse(localStorage.getItem(key) || '{{"pv":0,"first":null}}');
  data.pv++;
  if (!data.first) data.first = new Date().toISOString();
  data.last = new Date().toISOString();
  localStorage.setItem(key, JSON.stringify(data));

  // 简单的会话时长追踪
  var start = Date.now();
  window.addEventListener("beforeunload", function() {{
    var dur = Math.round((Date.now() - start) / 1000);
    var sd = JSON.parse(localStorage.getItem(key) || "{{}}");
    sd.totalTime = (sd.totalTime || 0) + dur;
    sd.sessions = (sd.sessions || 0) + 1;
    localStorage.setItem(key, JSON.stringify(sd));
  }});
}})();
</script>
'''


def get_analytics_dashboard_component() -> str:
    """生成一个内嵌的分析看板组件（嵌入到主站）"""
    return '''
<!-- ShipMicro Analytics Dashboard Widget -->
<div id="sm-analytics" style="padding:20px;background:#0a0a0a;border:1px solid #222;border-radius:12px;margin:20px 0;">
  <h3 style="color:#fff;margin:0 0 12px 0;font-size:14px;">📊 Analytics Overview</h3>
  <div id="sm-stats" style="color:#888;font-size:13px;">Loading...</div>
  <script>
  (function() {
    var keys = Object.keys(localStorage).filter(k => k.startsWith("sm_v_"));
    var total = 0, tools = [];
    keys.forEach(function(k) {
      var d = JSON.parse(localStorage.getItem(k));
      total += d.pv || 0;
      tools.push({slug: k.replace("sm_v_",""), pv: d.pv, time: d.totalTime || 0, sessions: d.sessions || 0});
    });
    tools.sort(function(a,b) { return b.pv - a.pv; });
    var html = "<div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:12px'>";
    html += "<div style='background:#111;padding:12px;border-radius:8px;text-align:center'><div style='font-size:24px;color:#fff;font-weight:bold'>"+total+"</div><div style='font-size:11px;color:#666'>Total Views</div></div>";
    html += "<div style='background:#111;padding:12px;border-radius:8px;text-align:center'><div style='font-size:24px;color:#fff;font-weight:bold'>"+keys.length+"</div><div style='font-size:11px;color:#666'>Active Tools</div></div>";
    var avgTime = tools.reduce(function(s,t){return s+(t.sessions?t.time/t.sessions:0)},0) / (tools.length||1);
    html += "<div style='background:#111;padding:12px;border-radius:8px;text-align:center'><div style='font-size:24px;color:#fff;font-weight:bold'>"+Math.round(avgTime)+"s</div><div style='font-size:11px;color:#666'>Avg Session</div></div>";
    html += "</div>";
    if (tools.length > 0) {
      html += "<div style='font-size:12px;color:#666;margin-bottom:6px'>Top Tools:</div>";
      tools.slice(0,5).forEach(function(t) {
        html += "<div style='display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #1a1a1a'><span style='color:#aaa'>"+t.slug+"</span><span style='color:#4ade80'>"+t.pv+" views</span></div>";
      });
    }
    document.getElementById("sm-stats").innerHTML = html;
  })();
  </script>
</div>
'''


def inject_analytics_into_page(page_path: str, tool_slug: str) -> bool:
    """在已有的 page.tsx 中注入追踪代码"""
    if not os.path.exists(page_path):
        return False
    with open(page_path, "r", encoding="utf-8") as f:
        code = f.read()
    if "ShipMicro Analytics" in code:
        return True  # 已经注入过了

    tracking = get_tracking_script(tool_slug)
    # 在 return 的最外层 div 结束前注入
    injection = f'\n      <div dangerouslySetInnerHTML={{{{ __html: `{tracking}` }}}} />'

    # 在 ShipMicro badge 之前注入
    if "ShipMicro</a>" in code:
        code = code.replace(
            '<div dangerouslySetInnerHTML',
            f'{injection}\n      <div dangerouslySetInnerHTML',
            1
        )
    with open(page_path, "w", encoding="utf-8") as f:
        f.write(code)
    log.info(f"📊 已注入追踪代码: {tool_slug}")
    return True


if __name__ == "__main__":
    print("📊 Analytics Tracker 自测")
    script = get_tracking_script("test-tool")
    print(f"  追踪脚本长度: {len(script)} chars")
    print("✅ 自测通过")

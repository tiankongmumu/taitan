"""
ShipMicro Ad Injector v2 — 智能广告注入（Roundtable Upgrade 4）
新增：基于 UI 热区的智能广告避让算法。
- 读取 ui_tester 收集的交互热区坐标
- 广告位避开高频点击区域
- 优先在用户自然停顿点插入广告
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(__file__))
from logger import get_logger

log = get_logger("ad_injector")

ADSENSE_PUB_ID = os.environ.get("ADSENSE_PUB_ID", "ca-pub-XXXXXXXXXXXXXXXX")
HOTSPOT_FILE = os.path.join(os.path.dirname(__file__), "analytics_data", "ui_hotspots.json")


def _load_hotspots(slug: str) -> list[dict]:
    """读取 ui_tester 收集的交互热区数据"""
    if not os.path.exists(HOTSPOT_FILE):
        return []
    with open(HOTSPOT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(slug, [])


def _is_safe_ad_zone(y_position: int, hotspots: list[dict], margin: int = 80) -> bool:
    """检查某个 Y 坐标是否远离交互热区（安全的广告位置）"""
    for spot in hotspots:
        spot_y = spot.get("y", 0)
        spot_h = spot.get("h", 0)
        # 如果广告 Y 坐标在热区的上下 margin 范围内，不安全
        if spot_y - margin <= y_position <= spot_y + spot_h + margin:
            return False
    return True


def get_adsense_head_script() -> str:
    return f'''
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_PUB_ID}"
     crossorigin="anonymous"></script>
'''


def get_adsense_jsx_component(position: str = "bottom") -> str:
    """v2: 根据位置生成不同样式的广告组件"""
    margin = "24px auto 0" if position == "bottom" else "12px auto 24px"
    return f'''
      {{/* ShipMicro Ad Unit ({position}) */}}
      <div
        style={{{{ margin: "{margin}", textAlign: "center", maxWidth: "728px" }}}}
        dangerouslySetInnerHTML={{{{ __html: `
          <ins class="adsbygoogle"
            style="display:block"
            data-ad-client="{ADSENSE_PUB_ID}"
            data-ad-slot="auto"
            data-ad-format="auto"
            data-full-width-responsive="true"></ins>
          <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
        ` }}}}
      />
'''


def inject_adsense_into_layout(layout_path: str) -> bool:
    if not os.path.exists(layout_path):
        return False
    with open(layout_path, "r", encoding="utf-8") as f:
        code = f.read()
    if "adsbygoogle" in code:
        return True
    if ADSENSE_PUB_ID == "ca-pub-XXXXXXXXXXXXXXXX":
        log.warning("  ⚠️ AdSense Publisher ID 未配置")
    script = get_adsense_head_script()
    if "</head>" in code:
        code = code.replace("</head>", f"{script}  </head>")
    elif "<head>" in code:
        code = code.replace("<head>", f"<head>\n{script}")
    with open(layout_path, "w", encoding="utf-8") as f:
        f.write(code)
    log.info(f"  💰 AdSense 脚本已注入到 layout.tsx")
    return True


def inject_adsense_into_page(page_path: str, slug: str = "") -> bool:
    """v2: 智能广告注入 — 避开交互热区"""
    if not os.path.exists(page_path):
        return False
    with open(page_path, "r", encoding="utf-8") as f:
        code = f.read()
    if "adsbygoogle" in code:
        return True

    # v2: 读取热区数据判断安全的广告位置
    hotspots = _load_hotspots(slug)
    if hotspots:
        # 检查是否有大量热区在页面底部（按钮密集区）
        bottom_hotspots = [h for h in hotspots if h.get("y", 0) > 500]
        if len(bottom_hotspots) > 3:
            log.info(f"  🛡️ 检测到 {len(bottom_hotspots)} 个底部交互热区，广告位上移")
            position = "top"
        else:
            position = "bottom"
    else:
        position = "bottom"

    ad_jsx = get_adsense_jsx_component(position)

    # 在 ShipMicro badge 之前注入广告
    if "ShipMicro</a>" in code:
        badge_marker = '<div dangerouslySetInnerHTML'
        idx = code.rfind(badge_marker)
        if idx > 0:
            code = code[:idx] + ad_jsx + "\n      " + code[idx:]

    with open(page_path, "w", encoding="utf-8") as f:
        f.write(code)
    log.info(f"  💰 广告已注入 (位置: {position}, 热区避让: {'是' if hotspots else '否'})")
    return True


def inject_ads_into_app(app_path: str) -> bool:
    slug = os.path.basename(app_path)
    log.info(f"💰 注入广告: {slug}")
    layout_path = os.path.join(app_path, "src", "app", "layout.tsx")
    page_path = os.path.join(app_path, "src", "app", "page.tsx")
    layout_ok = inject_adsense_into_layout(layout_path)
    page_ok = inject_adsense_into_page(page_path, slug)
    return layout_ok and page_ok


def inject_ads_into_all():
    apps_dir = os.path.join(os.path.dirname(__file__), "generated_apps")
    if not os.path.isdir(apps_dir):
        return
    apps = [d for d in os.listdir(apps_dir) if os.path.isdir(os.path.join(apps_dir, d)) and not d.endswith("_fallback")]
    log.info(f"💰 v2 智能广告注入: {len(apps)} 个应用...")
    success = 0
    for app in sorted(apps):
        if inject_ads_into_app(os.path.join(apps_dir, app)):
            success += 1
    log.info(f"💰 完成: {success}/{len(apps)}")


if __name__ == "__main__":
    inject_ads_into_all()

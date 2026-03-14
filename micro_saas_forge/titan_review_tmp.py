import json, os, glob
from datetime import datetime

FORGE = r"d:\Project\1\micro_saas_forge"

# 1. Brain history
brain_path = os.path.join(FORGE, "brain_state.json")
brain = json.load(open(brain_path, "r", encoding="utf-8"))
history = brain.get("history", [])
print(f"=== BRAIN HISTORY: {len(history)} cycles ===")
for h in history:
    s = "OK" if h.get("success") else "FAIL"
    dur = h.get('duration', 0)
    t = h.get('time', '?')[:16]
    cid = h.get('cycle_id', '?')
    print(f"  {cid} | {s} | {dur:.0f}s | {t}")

# 2. Generated apps
apps_dir = os.path.join(FORGE, "generated_apps")
apps = []
if os.path.isdir(apps_dir):
    for d in sorted(os.listdir(apps_dir)):
        full = os.path.join(apps_dir, d)
        if os.path.isdir(full):
            page = os.path.join(full, "src", "app", "page.tsx")
            has_code = os.path.exists(page)
            code_lines = 0
            if has_code:
                with open(page, "r", encoding="utf-8", errors="ignore") as f:
                    code_lines = len(f.readlines())
            nm = os.path.exists(os.path.join(full, "node_modules"))
            out = os.path.exists(os.path.join(full, "out"))
            nexd = os.path.exists(os.path.join(full, ".next"))
            mtime = datetime.fromtimestamp(os.path.getmtime(full)).strftime("%m/%d %H:%M")
            apps.append({
                "slug": d,
                "has_code": has_code,
                "lines": code_lines,
                "has_node_modules": nm,
                "has_build": nexd,
                "has_export": out,
                "modified": mtime,
            })

print(f"\n=== GENERATED APPS: {len(apps)} ===")
print(f"  With code: {sum(1 for a in apps if a['has_code'])}")
print(f"  With node_modules: {sum(1 for a in apps if a['has_node_modules'])}")
print(f"  With .next build: {sum(1 for a in apps if a['has_build'])}")
print(f"  With out/ export: {sum(1 for a in apps if a['has_export'])}")
print(f"  Code > 100 lines: {sum(1 for a in apps if a['lines'] > 100)}")
print(f"  Code > 200 lines: {sum(1 for a in apps if a['lines'] > 200)}")

print("\n--- Apps with code (>50 lines, sorted by lines desc) ---")
for a in sorted(apps, key=lambda x: x["lines"], reverse=True):
    if a["lines"] > 50:
        build = "BUILD" if a["has_build"] else "---"
        export = "EXPORT" if a["has_export"] else "---"
        print(f"  {a['slug']:<45} {a['lines']:>4} lines | {build:<6} | {export:<6} | {a['modified']}")

# 3. Competitive analyses
comp_dir = os.path.join(FORGE, "competitive_analysis")
if os.path.isdir(comp_dir):
    comps = sorted(os.listdir(comp_dir))
    print(f"\n=== COMPETITIVE ANALYSES: {len(comps)} ===")
    for c in comps:
        print(f"  {c}")

# 4. Executor log
exec_log = os.path.join(FORGE, "logs", "titan_executor.jsonl")
if os.path.exists(exec_log):
    with open(exec_log, "r", encoding="utf-8") as f:
        lines = f.readlines()
    print(f"\n=== EXECUTOR LOG: {len(lines)} entries ===")
    for l in lines[-10:]:
        try:
            e = json.loads(l)
            ts = e.get('ts', '?')[:16]
            outcome = e.get('outcome', '?')[:80]
            print(f"  {ts} | {outcome}")
        except:
            pass

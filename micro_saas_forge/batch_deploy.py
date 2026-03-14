"""
TITAN Engine — Batch Deploy Script v1.0
批量验证构建并部署优先工具到 Vercel
"""
import os
import sys
import json
import subprocess
import time
from datetime import datetime

FORGE_DIR = os.path.dirname(os.path.abspath(__file__))
APPS_DIR = os.path.join(FORGE_DIR, "generated_apps")

# Top 10 priority tools by search volume potential
PRIORITY_TOOLS = [
    "jwt-debugger",
    "json-path-finder",
    "regex-playground",
    "sql-query-formatter",
    "curl-to-code",
    "postgresql-schema-designer",
    "password-security-coach",
    "smart-qr-generator",
    "image-compress-pro",
    "svg-to-png-pro-converter",
]

# Backup choices if some fail
BACKUP_TOOLS = [
    "css-gradient-animator",
    "markdown-email-converter",
    "typing-speed-test",
    "favicon-forge-pro",
    "promptcraft-studio",
]

def check_app_exists(slug):
    """Check if app directory exists and has page.tsx"""
    app_dir = os.path.join(APPS_DIR, slug)
    page = os.path.join(app_dir, "src", "app", "page.tsx")
    return os.path.isdir(app_dir) and os.path.isfile(page)

def npm_install(app_dir):
    """Install npm dependencies"""
    if os.path.isdir(os.path.join(app_dir, "node_modules")):
        return True
    try:
        r = subprocess.run(
            ["npm", "install"], cwd=app_dir,
            capture_output=True, text=True, timeout=120, shell=True
        )
        return r.returncode == 0
    except Exception as e:
        print(f"    npm install failed: {e}")
        return False

def npm_build(app_dir):
    """Build the app"""
    try:
        r = subprocess.run(
            ["npm", "run", "build"], cwd=app_dir,
            capture_output=True, text=True, timeout=180, shell=True
        )
        return r.returncode == 0, r.stderr[-500:] if r.stderr else ""
    except Exception as e:
        return False, str(e)

def deploy_to_vercel(app_dir, slug):
    """Deploy to Vercel"""
    try:
        r = subprocess.run(
            ["npx", "vercel", "--prod", "--yes", "--name", slug],
            cwd=app_dir,
            capture_output=True, text=True, timeout=300, shell=True
        )
        output = r.stdout.strip()
        # Extract URL from output
        lines = output.split("\n")
        url = ""
        for line in lines:
            line = line.strip()
            if line.startswith("https://"):
                url = line
                break
        return r.returncode == 0, url
    except Exception as e:
        return False, str(e)

def main():
    print(f"""
╔══════════════════════════════════════════════════╗
║  🚀 TITAN Engine — Batch Deploy v1.0            ║
║  Target: {len(PRIORITY_TOOLS)} priority tools → Vercel              ║
║  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                  ║
╚══════════════════════════════════════════════════╝
""")
    
    results = {"deployed": [], "build_failed": [], "install_failed": [], "missing": []}
    all_tools = PRIORITY_TOOLS + BACKUP_TOOLS
    
    for i, slug in enumerate(all_tools, 1):
        print(f"\n{'='*60}")
        print(f"[{i}/{len(all_tools)}] 🔧 Processing: {slug}")
        print(f"{'='*60}")
        
        app_dir = os.path.join(APPS_DIR, slug)
        
        # 1. Check existence
        if not check_app_exists(slug):
            print(f"  ❌ Not found or missing page.tsx")
            results["missing"].append(slug)
            continue
        
        # 2. npm install
        print(f"  📦 Installing dependencies...")
        if not npm_install(app_dir):
            print(f"  ❌ npm install failed")
            results["install_failed"].append(slug)
            continue
        
        # 3. npm build
        print(f"  🔨 Building...")
        build_ok, error = npm_build(app_dir)
        if not build_ok:
            print(f"  ❌ Build failed: {error[:100]}")
            results["build_failed"].append(slug)
            continue
        print(f"  ✅ Build passed!")
        
        # 4. Deploy to Vercel
        print(f"  🚀 Deploying to Vercel...")
        deploy_ok, url = deploy_to_vercel(app_dir, slug)
        if deploy_ok and url:
            print(f"  🎉 DEPLOYED: {url}")
            results["deployed"].append({"slug": slug, "url": url, "time": datetime.now().isoformat()})
        else:
            print(f"  ⚠️ Deploy returned: {url[:100] if url else 'no output'}")
            results["build_failed"].append(slug)
        
        # Stop after 10 successful deploys
        if len(results["deployed"]) >= 10:
            print(f"\n🎯 Reached target of 10 deployments!")
            break
    
    # Save results
    report_path = os.path.join(FORGE_DIR, "batch_deploy_results.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Summary
    print(f"""
╔══════════════════════════════════════════════════╗
║  📊 Deployment Summary                           ║
╠══════════════════════════════════════════════════╣
║  ✅ Deployed:  {len(results['deployed']):>3}                               ║
║  ❌ Build Fail: {len(results['build_failed']):>3}                               ║
║  📦 Install Fail: {len(results['install_failed']):>3}                            ║
║  🔍 Missing:    {len(results['missing']):>3}                               ║
╚══════════════════════════════════════════════════╝
""")
    
    if results["deployed"]:
        print("🌐 Deployed URLs:")
        for d in results["deployed"]:
            print(f"  • {d['slug']}: {d['url']}")
    
    print(f"\nResults saved to: {report_path}")

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
银河搬运工 - 全网短视频无水印提取器 V3.0 Pro Max
(商业精装版 - CustomTkinter 桌面级 GUI + 原生免依赖架构)
"""
import os
import sys
import threading
import re
import time
import requests
import urllib.parse
import urllib.request
import customtkinter as ctk

# --- 核心下载逻辑封包 ---
class VideoDownloader:
    def __init__(self, save_dir, log_callback, success_callback, error_callback):
        self.save_dir = save_dir
        self.log_callback = log_callback
        self.success_callback = success_callback
        self.error_callback = error_callback
        
    def download(self, url):
        self.log_callback(f"[*] 正在识别平台解析引擎...")
        
        if "douyin.com" in url:
            self.download_douyin(url)
        else:
            self.download_ytdlp(url)
            
    def download_douyin(self, url):
        self.log_callback("[*] 检测到抖音链接，启动底层无头战车突破反爬机制 (首次可能较慢)...")
        import asyncio
        from playwright.async_api import async_playwright
        import urllib.request
        import time

        async def fetch_dy(target_url):
            self.log_callback("  > 正在下发模拟真人网页指令...")
            try:
                async with async_playwright() as p:
                    # 使用 PC Web 端的 UA，确保触发 aweme/detail API
                    b = await p.chromium.launch(headless=True)
                    c = await b.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
                    page = await c.new_page()
                    
                    target_video_url = None
                    api_intercepted = asyncio.Event()

                    async def handle_response(response):
                        nonlocal target_video_url
                        if "aweme/detail/" in response.url or "iteminfo/" in response.url or "aweme/post/" in response.url:
                            try:
                                data = await response.json()
                                if "aweme_detail" in data:
                                    play_addr = data["aweme_detail"].get("video", {}).get("play_addr", {}).get("url_list", [])
                                    if play_addr:
                                        target_video_url = play_addr[0]
                                        api_intercepted.set()
                                elif "item_list" in data and len(data["item_list"]) > 0:
                                    play_addr = data["item_list"][0].get("video", {}).get("play_addr", {}).get("url_list", [])
                                    if play_addr:
                                        target_video_url = play_addr[0]
                                        api_intercepted.set()
                            except Exception:
                                pass
                                
                    page.on("response", handle_response)
                    
                    self.log_callback("  > 页面仿真加载中，正在挂载钩子拦截底层服务器数据流...")
                    try:
                        # Go to the url without waiting for networkidle, just wait for domcontentloaded
                        await page.goto(target_url, wait_until="domcontentloaded", timeout=15000)
                        # Wait maximum 10 seconds for the API to be intercepted
                        try:
                            await asyncio.wait_for(api_intercepted.wait(), timeout=10.0)
                        except asyncio.TimeoutError:
                            pass
                    except Exception as goto_err:
                        self.log_callback(f"  > 导航警告: {goto_err}")
                        pass # Ignore navigation errors as long as we get the api response
                    
                    src = target_video_url
                    if src:
                        self.log_callback("  > 🔓 成功在底层 JSON 中截获【绝对纯净的 CDN 主线源】！")
                    else:
                        self.log_callback("  > API 拦截超时，降级为您启动物理脱水压缩算法...")
                        src = await page.evaluate('''() => {
                            let v = document.querySelector("video source");
                            if (v) return v.src;
                            let v2 = document.querySelector("video");
                            if (v2) return v2.src;
                            return "";
                        }''')
                        if src and "playwm" in src:
                            src = src.replace("playwm", "play")
                        
                    if not src:
                         raise Exception("未找到视频源或该视频已被隐藏 (可能需要重试)")
                         
                    title = await page.title()
                    safe_title = re.sub(r'[\\/*?:"<>|]', "", title.split('-')[0].strip()) or f"抖音提取_{int(time.time())}"
                    
                    filepath = os.path.join(self.save_dir, f"{safe_title[:45]}.mp4")
                    self.log_callback(f"  > 开始物理拦截媒资文件到本地...")
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Referer': 'https://www.douyin.com/'
                    }
                    req = urllib.request.Request(src, headers=headers)
                    with urllib.request.urlopen(req, timeout=30) as response, open(filepath, 'wb') as out_file:
                        chunk_size = 1024 * 1024 * 2
                        while True:
                            chunk = response.read(chunk_size)
                            if not chunk: break
                            out_file.write(chunk)
                            
                    self.success_callback()
                    await b.close()
            except Exception as ex:
                err_str = str(ex)
                if "Executable doesn't exist" in err_str or "playwright install" in err_str:
                    self.log_callback("[!] 首次使用，正在为您后台静默补装纯净级无头浏览器引擎，请稍候...")
                    self.log_callback("    （此过程需耗费50MB~150MB流量，视网速可能需要1-3分钟，安装完毕后将永久流畅运行）")
                    import subprocess
                    import os
                    from playwright._impl._driver import compute_driver_executable, get_driver_env
                    
                    startupinfo = None
                    if os.name == 'nt':
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        
                    driver_executable, driver_cli = compute_driver_executable()
                    env = get_driver_env()
                    
                    # 解决国内网络封锁和 PyInstaller Temp 目录权限问题
                    env['PLAYWRIGHT_DOWNLOAD_HOST'] = 'https://npmmirror.com/mirrors/playwright/'
                    env['PLAYWRIGHT_BROWSERS_PATH'] = '0' # 安装到当前系统的标准位置，而不是提取器的临时解压目录
                    
                    try:
                        subprocess.run([driver_executable, *driver_cli, 'install', 'chromium'], env=env, startupinfo=startupinfo, check=True)
                        self.error_callback(f"引擎核心安装成功！请重新点击【开始提取】！")
                    except Exception as ie:
                        self.error_callback(f"安装核心失败，请检测网络: {str(ie)}")
                else:
                    self.error_callback(f"底部分析失败: {err_str}")

        try:
            # 解决 GUI 中 asyncio loop 冲突的问题
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(fetch_dy(url))
            loop.close()
        except Exception as e:
            self.error_callback(str(e))
            
    def download_ytdlp(self, url):
        self.log_callback("[*] 正在连接通用极速服务器...")
        import yt_dlp
        
        class MyLogger:
            def __init__(self, log_cb):
                self.log_cb = log_cb
            def debug(self, msg):
                if "100%" not in msg and "Downloading" not in msg:
                    self.log_cb(f"  > {msg}")
            def warning(self, msg): pass
            def error(self, msg):
                self.log_cb(f"[!] {msg}")

        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(self.save_dir, '%(title)s.%(ext)s'),
            'ignoreerrors': True,
            'no_warnings': True,
            'quiet': True,
            'logger': MyLogger(self.log_callback),
            'noprogress': True
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                error_code = ydl.download([url])
                if error_code == 0:
                    self.success_callback()
                else:
                    self.error_callback("该链接无效、受限或无视频内容。")
        except Exception as e:
            self.error_callback(str(e))

# --- GUI 主界面 (CustomTkinter) ---
ctk.set_appearance_mode("Dark")  # 强制酷炫暗黑模式
ctk.set_default_color_theme("blue")  # 默认主题色

class ExtractorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("✨ 银河机器 - 全网视频解析引擎 Pro Max")
        self.geometry("620x480")
        self.resizable(False, False)
        
        # 居中显示
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 620) // 2
        y = (self.winfo_screenheight() - 480) // 2
        self.geometry(f"+{x}+{y}")
        
        self.save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "下载完成的视频")
        os.makedirs(self.save_dir, exist_ok=True)
        
        self.build_ui()
        
    def build_ui(self):
        # --- 顶部分区 ---
        top_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        top_frame.pack(fill="x", pady=(20, 10))
        
        title_lbl = ctk.CTkLabel(top_frame, text="银河高阶全自动解析引擎", font=ctk.CTkFont(family="Microsoft YaHei", size=24, weight="bold"))
        title_lbl.pack()
        
        sub_lbl = ctk.CTkLabel(top_frame, text="突破 100+ 平台限制 | 原画质 | 零水痕痕 | 免核安装", text_color="gray", font=ctk.CTkFont(size=12))
        sub_lbl.pack()
        
        # --- 中间交互区 ---
        mid_frame = ctk.CTkFrame(self, fg_color="#2B2B2B", corner_radius=15)
        mid_frame.pack(fill="both", expand=True, padx=25, pady=(10, 20))
        
        input_lbl = ctk.CTkLabel(mid_frame, text="📍 放入分享链接 (支持整段文案自动识别)：", font=ctk.CTkFont(size=13))
        input_lbl.pack(anchor="w", padx=20, pady=(15, 5))
        
        input_row = ctk.CTkFrame(mid_frame, fg_color="transparent")
        input_row.pack(fill="x", padx=20, pady=5)
        
        self.url_entry = ctk.CTkEntry(input_row, height=45, placeholder_text="在此处粘贴（例如：https://v.douyin.com/...）", border_width=1, corner_radius=8)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 15))
        
        self.btn_download = ctk.CTkButton(input_row, text="🚀 开始提取", width=110, height=45, font=ctk.CTkFont(weight="bold"), corner_radius=8, command=self.start_download)
        self.btn_download.pack(side="right")
        
        log_lbl = ctk.CTkLabel(mid_frame, text="终端运行日志：", font=ctk.CTkFont(size=12, slant="italic"), text_color="gray")
        log_lbl.pack(anchor="w", padx=20, pady=(15, 0))
        
        self.log_widget = ctk.CTkTextbox(mid_frame, height=120, fg_color="#1E1E1E", text_color="#A6E22E", font=ctk.CTkFont(family="Consolas", size=12), corner_radius=8)
        self.log_widget.pack(fill="both", expand=True, padx=20, pady=(5, 20))
        self.log_widget.configure(state="disabled")
        
        # --- 底部栏 ---
        btm_frame = ctk.CTkFrame(self, fg_color="transparent", height=40)
        btm_frame.pack(fill="x", padx=25, pady=(0, 15))
        
        dir_lbl = ctk.CTkLabel(btm_frame, text=f"📂 存至: {self.save_dir}", font=ctk.CTkFont(size=12), text_color="gray")
        dir_lbl.pack(side="left")
        
        open_btn = ctk.CTkButton(btm_frame, text="打开文件夹", width=90, height=28, fg_color="gray", hover_color="#555555", corner_radius=6, command=self.open_save_dir)
        open_btn.pack(side="right")
        
        self.append_log("银河内核已就绪。等待接收任务指令...")

    def append_log(self, text):
        self.log_widget.configure(state="normal")
        self.log_widget.insert("end", text + "\n")
        self.log_widget.see("end")
        self.log_widget.configure(state="disabled")
        self.update_idletasks()

    def open_save_dir(self):
        try:
            os.startfile(self.save_dir)
        except Exception:
            pass

    def start_download(self):
        raw_text = self.url_entry.get().strip()
        url_match = re.search(r'(https?://[^\s]+)', raw_text)
        
        if not url_match:
            from tkinter import messagebox
            messagebox.showwarning("链接错误", "未检测到有效的网址！\n请确保粘贴的内容中包含 http 或 https 开头的链接。")
            return
            
        url = url_match.group(1)
        self.append_log(f"\n[*] 智能嗅探提取真实链接: {url}")
            
        self.btn_download.configure(state="disabled", text="提取中...")
        self.url_entry.configure(state="disabled")
        self.append_log("-"*50)
        
        threading.Thread(target=self._download_worker, args=(url,), daemon=True).start()
        
    def _download_worker(self, url):
        downloader = VideoDownloader(
            save_dir=self.save_dir,
            log_callback=lambda msg: self.after(0, self.append_log, msg),
            success_callback=lambda: self.after(0, self._on_success),
            error_callback=lambda err: self.after(0, self._on_error, err)
        )
        downloader.download(url)
        
    def _on_success(self):
        self.append_log("✅ 拦截与提取成功！原始画质媒资已落盘。")
        self._reset_ui()
        from tkinter import messagebox
        messagebox.showinfo("提取成功", "无水印视频提取成功！\n请点击右下方【打开文件夹】查看。")
        self.url_entry.delete(0, 'end')
        
    def _on_error(self, err_msg):
        self.append_log(f"❌ 任务失败: {err_msg}")
        self._reset_ui()
        from tkinter import messagebox
        messagebox.showerror("提取失败", f"无法下载该视频。\n诊断信息: {err_msg}")

    def _reset_ui(self):
        self.btn_download.configure(state="normal", text="🚀 开始提取")
        self.url_entry.configure(state="normal")

if __name__ == "__main__":
    app = ExtractorApp()
    app.mainloop()

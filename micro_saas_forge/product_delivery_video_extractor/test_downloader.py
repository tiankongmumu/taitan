import threading
from video_extractor import VideoDownloader
import time

def log(msg): print("LOG:", msg)
def ok(): print("SUCCESS!")
def err(e): print("ERROR:", e)

downloader = VideoDownloader('./', log, ok, err)

# simulate thread
url = 'https://v.douyin.com/MV0gw4XWdeY/'

def worker():
    downloader.download(url)

t = threading.Thread(target=worker)
t.start()
t.join()
print("Test completed.")

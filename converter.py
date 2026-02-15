import cv2
import numpy as np
from pathlib import Path
import os
import sys 
import time 
import subprocess
import signal
import atexit

# Thing wasn't working or I'm stupid idk
# Going to make it so that the target video will always be called video.mp4

# VIDEO_PATH = sys.argv[1] if len(sys.argv) > 1 else None

# if not VIDEO_PATH:
#     print(" idiot go fix your code or file idk")
#     sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent
VIDEO_EXTS = [".mp4", ".avi", ".mkv", ".mov"]

video_files = []
for ext in VIDEO_EXTS:
    video_files.extend(SCRIPT_DIR.glob(f"*{ext}"))

if not video_files:
    print("No video found, make sure that its a .mp4/.avi/.mkv/.mov")
    sys.exit(1)

VIDEO_PATH = str(video_files[0])
print("Using video:", Path(VIDEO_PATH).name)
time.sleep(0.5)

TARGET_WIDTH = 80
# FPS_CAP = 30 trying smth new
USE_OTSU = True
DROP_LATE_SEC = 0.01

ON = "█"
OFF = " "

CLEAR = "\x1b[2J"
HOME = "\x1b[H"
HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"

def get_terminal_size():
    try:
        cols, rows = os.get_terminal_size()
        return cols, rows 
    except OSError:
        print("can't get terminal size, will go with 120x40")
        return 120, 40

def frame_to_text(frame, out_w, out_h):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    small = cv2.resize(gray, (out_w, out_h), interpolation=cv2.INTER_AREA)

    if USE_OTSU:
        _, bw = cv2.threshold(small, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        _, bw = cv2.threshold(small, 128, 255, cv2.THRESH_BINARY)

    mask = bw > 0
    chars = np.where(mask, ON, OFF)

    return "\n".join("".join(row) for row in chars)

def kill_process_tree(pid: int):
    try:
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass


# def kill_ffplay():
#     if audio_proc is None:
#         return
#     try:
#         subprocess.run(
#          ["taskkill", "/PID", str(audio_proc.pid), "/T", "/F"],
#          stdout=subprocess.DEVNULL,
#          stderr=subprocess.DEVNULL
#         )
#     except Exception:
#         try:
#             audio_proc.kill()
#         except Exception:
#             pass
#     audio_proc = None

# atexit.register(kill_ffplay)

# def _signal_handler(sig, frame):
#     kill_ffplay()
#     raise KeyboardInterrupt

# signal.signal(signal.SIGINT, _signal_handler)
# signal.signal(signal.SIGTERM, _signal_handler)

def main():
    audio_holder = {"proc": None}

    def kill_audio():
        proc = audio_holder.get("proc")
        if proc is None:
            return
        if proc.poll() is None:
            kill_process_tree(proc.pid)
        audio_holder["proc"] = None

    atexit.register(kill_audio)

    def on_signal(signum, frame):
        kill_audio()
        raise KeyboardInterrupt
    
    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)

    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"can't open video, current one is {VIDEO_PATH}")
        sys.exit(1)
    
    term_w, term_h = get_terminal_size()
    out_w = min(TARGET_WIDTH, term_w)
    out_h = min(term_h - 2, max(10, int(out_w * 0.50)))
    
    try:
        audio_holder["proc"] = subprocess.Popen(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", VIDEO_PATH],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    except FileNotFoundError:
        print("ffplay not found, FFMPEG ISNT INSTALLED")
        audio_holder["proc"] = None

    time.sleep(0.1)

    sys.stdout.write(CLEAR + HOME + HIDE_CURSOR)
    sys.stdout.flush()

    start_time = time.perf_counter()
    first_ts = None

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            ts_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
            if ts_ms != ts_ms:
                ts_ms = 0.0

            if first_ts is None:
                first_ts = ts_ms

            target = start_time + (ts_ms - first_ts) / 1000.0
            now = time.perf_counter()

            while now - target > 0.03:
                ret, frame = cap.read()
                if not ret:
                    break
                ts_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
                target = start_time + (ts_ms - first_ts) / 1000.0
                now = time.perf_counter()
            
            sleep = target - now
            if sleep > 0:
                time.sleep(sleep)

            txt = frame_to_text(frame, out_w, out_h)

            sys.stdout.write(HOME + txt + "\n")
            sys.stdout.flush()
    
    except KeyboardInterrupt:
        pass

    finally:
        sys.stdout.write(SHOW_CURSOR + "\n")
        sys.stdout.flush()
        cap.release()
        kill_audio()

if __name__ == "__main__":
    main()
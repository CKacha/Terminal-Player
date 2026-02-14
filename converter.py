import cv2
import numpy as np
from pathlib import Path
import os
import sys 
import time 
import subprocess

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
time.sleep(1)

TARGET_WIDTH = 120
FPS_CAP = 30 # DONT CHANGE THIS... you don't want to put it as True lmao
USE_OTSU = True

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

def main():
    audio_proc = None
    
    try:
        audio_proc = subprocess.Popen(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", VIDEO_PATH],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    except FileNotFoundError:
        print("ffplay not found, FFMPEG ISNT INSTALLED")

    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"can't open video, current one is {VIDEO_PATH}")
        sys.exit(1)
    
    vid_fps = cap.get(cv2.CAP_PROP_FPS)
    if vid_fps and vid_fps == vid_fps and vid_fps >1:
        frame_dt = 1.0 / vid_fps
    else:
        frame_dt = 1.0 / FPS_CAP

    term_w, term_h = get_terminal_size()
    out_w = min(TARGET_WIDTH, term_w)
    out_h = min(term_h - 2, max(10, int(out_w * 0.50)))

    frame_dt = 1.0/FPS_CAP
    next_t = time.perf_counter()

    sys.stdout.write(CLEAR + HOME + HIDE_CURSOR)
    sys.stdout.flush()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            txt= frame_to_text(frame, out_w, out_h)

            sys.stdout.write(HOME)
            sys.stdout.write(txt)
            sys.stdout.write("\n")
            sys.stdout.flush()

            #fps cap bc my computer crashed earlier sob
            next_t += frame_dt
            now = time.perf_counter()
            sleep = next_t - now 
            if sleep > 0:
                time.sleep(sleep)
            else:
                next_t = now


    finally:

        sys.stdout.write(SHOW_CURSOR + "\n")
        sys.stdout.flush()
        cap.release()

if __name__ == "__main__":
    main()
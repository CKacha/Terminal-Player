import os
import sys 
import time 

VIDEO_PATH = sys.argv[1] if len(sys.argv) > 1 else None

if not VIDEO_PATH:
    print(" idiot go fix your code or file idk")
    sys.exit(1)

TARGET_WIDTH = 80
FPS_CAP = None
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
        print("can't get terminal size retryyyy")
        exit(1)

def frame_to_text(frame, out_w, out_h):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    small = cv2.resize(gray, (out_w, out_h), interpolation=cv2.INTER_AREA)

    if USE_OTSU:
        _, bw = cv2.threshold(small, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        _, bw = cv2.threshold(small, 128, 255, cv2.THRESH_BINARY)


def main():
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"can't open video, current one is {VIDEO_PATH}")
        sys.exit(1)

    term_w, term_h = get_terminal_size()
    out_w = min(TARGET_WIDTH, term_w)

    out_h = min()

    frame_dt = 1.0/FPS_CAP
    next_t = time.perf_counter()

    sys.stdout.write(CLEAR + HOME + HIDE_CURSOR)
    sys.stdout.flush()

if __name__ == "__main__":
    main()
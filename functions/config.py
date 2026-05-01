from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
VIDEO_DIR = ROOT_DIR / "videos"

VIDEO_EXTS = [".mp4", ".avi", ".mkv", ".mov", ".webm"]

TARGET_WIDTH = 90
USE_OTSU = True

ON = "█"
OFF = " "

CLEAR = "\x1b[2J"
HOME = "\x1b[H"
HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"
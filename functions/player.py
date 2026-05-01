import sys
import time
import signal
import atexit
import cv2

from functions.config import CLEAR, HOME, HIDE_CURSOR, SHOW_CURSOR
from functions.renderer import frame_to_text, get_output_size
from functions.audio import AudioPlayer


def print_start_screen(video_path):
    print("\n=== TERMINAL PLAYER ===")
    print(f"Selected: {video_path.name}")
    print("\nControls:")
    print("CTRL+C = quit")
    print("\nStarting...")


def play_video(video_path):
    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        print(f"Could not open video: {video_path}")
        sys.exit(1)

    audio = AudioPlayer()

    def cleanup():
        sys.stdout.write(SHOW_CURSOR + "\n")
        sys.stdout.flush()
        cap.release()
        audio.stop()

    def handle_signal(signum, frame):
        cleanup()
        raise KeyboardInterrupt

    atexit.register(cleanup)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    print_start_screen(video_path)
    time.sleep(1)

    out_w, out_h = get_output_size()

    audio.play(video_path)
    time.sleep(0.15)

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

            target_time = start_time + ((ts_ms - first_ts) / 1000.0)
            now = time.perf_counter()

            while now - target_time > 0.035:
                ret, frame = cap.read()

                if not ret:
                    break

                ts_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
                target_time = start_time + ((ts_ms - first_ts) / 1000.0)
                now = time.perf_counter()

            delay = target_time - now

            if delay > 0:
                time.sleep(delay)

            text_frame = frame_to_text(frame, out_w, out_h)

            sys.stdout.write(
                HOME
                + f"Playing: {video_path.name} | CTRL+C to quit\n\n"
                + text_frame
                + "\n"
            )
            sys.stdout.flush()

    except KeyboardInterrupt:
        pass

    finally:
        cleanup()
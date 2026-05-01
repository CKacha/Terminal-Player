import os
import cv2
import numpy as np

from functions.config import ON, OFF, USE_OTSU, TARGET_WIDTH


def get_terminal_size():
    try:
        cols, rows = os.get_terminal_size()
        return cols, rows
    except OSError:
        return 120, 40


def get_output_size():
    term_w, term_h = get_terminal_size()

    out_w = min(TARGET_WIDTH, term_w)
    out_h = min(term_h - 4, max(10, int(out_w * 0.45)))

    return out_w, out_h


def frame_to_text(frame, out_w, out_h):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    small = cv2.resize(gray, (out_w, out_h), interpolation=cv2.INTER_AREA)

    if USE_OTSU:
        _, bw = cv2.threshold(
            small,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
    else:
        _, bw = cv2.threshold(small, 128, 255, cv2.THRESH_BINARY)

    chars = np.where(bw > 0, ON, OFF)

    return "\n".join("".join(row) for row in chars)
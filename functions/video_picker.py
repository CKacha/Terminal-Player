import sys
from functions.config import VIDEO_DIR, VIDEO_EXTS


def find_videos():
    VIDEO_DIR.mkdir(exist_ok=True)

    videos = []
    for ext in VIDEO_EXTS:
        videos.extend(VIDEO_DIR.glob(f"*{ext}"))

    return sorted(videos)


def choose_video():
    videos = find_videos()

    if not videos:
        print("No videos found.")
        print(f"Put your videos here: {VIDEO_DIR}")
        sys.exit(1)

    print("\n=== TERMINAL PLAYER ===\n")
    print("Choose a video:\n")

    for i, video in enumerate(videos, start=1):
        size_mb = video.stat().st_size / 1024 / 1024
        print(f"[{i}] {video.name} ({size_mb:.1f} MB)")

    print("\n[q] quit\n")

    while True:
        choice = input("Pick file number: ").strip().lower()

        if choice == "q":
            sys.exit(0)

        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(videos):
                return videos[index]

        print("Invalid choice. Try again.")
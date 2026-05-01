from functions.video_picker import choose_video
from functions.player import play_video

def main():
    video_path = choose_video()
    play_video(video_path)

if __name__ == "__main__":
    main()
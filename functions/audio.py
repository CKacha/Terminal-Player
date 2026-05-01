import subprocess
import sys


def kill_process_tree(pid):
    try:
        if sys.platform.startswith("win"):
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            subprocess.run(
                ["kill", "-9", str(pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
    except Exception:
        pass


class AudioPlayer:
    def __init__(self):
        self.proc = None

    def play(self, video_path):
        try:
            kwargs = {
                "stdout": subprocess.DEVNULL,
                "stderr": subprocess.DEVNULL,
            }

            if sys.platform.startswith("win"):
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

            self.proc = subprocess.Popen(
                [
                    "ffplay",
                    "-nodisp",
                    "-autoexit",
                    "-loglevel",
                    "quiet",
                    str(video_path)
                ],
                **kwargs
            )

        except FileNotFoundError:
            print("ffplay not found. Playing without audio.")
            self.proc = None

    def stop(self):
        if self.proc is None:
            return

        if self.proc.poll() is None:
            kill_process_tree(self.proc.pid)

        self.proc = None
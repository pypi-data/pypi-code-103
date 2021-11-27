from argparse import ArgumentParser, RawTextHelpFormatter
import os
from pathlib import Path
import subprocess
import sys

from ffmpeg import probe
from tqdm import tqdm
from .utils import FileInfoProvider


class FfmpegProcess:
    def __init__(self, command, ffmpeg_loglevel="verbose"):
        """
        Creates the list of FFmpeg arguments.
        Accepts an optional ffmpeg_loglevel parameter to set the value of FFmpeg's -loglevel argument.
        """
        self._command = command
        # pipe:1 sends the progress to stdout. See https://stackoverflow.com/a/54386052/13231825
        self._ffmpeg_args = command + ["-progress", "pipe:1", "-nostats", "-loglevel", ffmpeg_loglevel]

    def run(self, progress_handler=None, ffmpeg_output_file=None):
        """
        Runs FFmpeg and prints the following:
            - Percentage Progress
            - Speed
            - ETA (minutes and seconds)
        Example:
        Progress: 25% | Speed: 22.3x | ETA: 1m 33s
        """

        index_of_filepath = self._command.index("-i") + 1
        filepath = self._command[index_of_filepath]

        if ffmpeg_output_file is None:
            os.makedirs("ffmpeg_output", exist_ok=True)
            ffmpeg_output_file = os.path.join("ffmpeg_output", f"[{Path(filepath).name}].txt")

        with open(ffmpeg_output_file, "w") as f:
            pass

        try:
            duration_secs = float(probe(filepath)["format"]["duration"])
        except Exception:
            can_get_duration = False
        else:
            can_get_duration = True

        print(f"Running: {' '.join(self._ffmpeg_args)}")
        popen_args = [self._ffmpeg_args]

        if can_get_duration:
            popen_args.append(stdout=subprocess.PIPE, stderr=f)

            with open(ffmpeg_output_file, "a") as f:
                self._process = subprocess.Popen(*popen_args)

            progress_bar = tqdm(
                total=duration_secs,
                unit="s",
                dynamic_ncols=True
            )
            progress_bar.clear()
            previous_seconds_processed = 0
        else:
            self._process = subprocess.Popen(*popen_args)

        try:
            while self._process.poll() is None:
                if can_get_duration:
                    line = self._process.stdout.readline().decode("utf-8")
                    # Format: out_time_ms=3505000
                    if "out_time_ms" in line:
                        seconds_processed = int(line.strip()[12:]) / 1_000_000
                        seconds_increase = seconds_processed - previous_seconds_processed
                        progress_bar.update(seconds_increase)
                        previous_seconds_processed = seconds_processed
        except KeyboardInterrupt:
            progress_bar.close()
            self._process.kill()
            print("[KeyboardInterrupt] FFmpeg process killed. Exiting Better FFmpeg Progress.")
            sys.exit(0)

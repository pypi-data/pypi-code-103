from argparse import ArgumentParser, RawTextHelpFormatter
import os
from pathlib import Path
import subprocess

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
        self._ffmpeg_args = command + ["-progress", "-", "-nostats", "-loglevel", ffmpeg_loglevel]

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
            file_duration = float(probe(filepath)["format"]["duration"])
        except Exception:
            can_get_duration = False
            print(f"\nUnable to get the duration of {filepath}:\nThe improved progress stats will not be shown.")
        else:
            can_get_duration = True

        percentage = "unknown"
        speed = "unknown"
        eta_string = "unknown"
        ffmpeg_stderr = ""

        print("Running FFmpeg...")
        print('bla')

        with open(ffmpeg_output_file, "a") as f:
            self._process = subprocess.Popen(
                self._ffmpeg_args,
                stdout=subprocess.PIPE,
                stderr=f,
            )

        input_file_info = FileInfoProviderer(filepath)
        duration_secs = input_file_info.get_duration

        progress_bar = tqdm(
            total=duration_secs,
            dynamic_ncols=True
        )

        progress_bar.clear()
        previous_seconds_processed = 0

        try:
            while self._process.poll() is None:
                line = self._process.stdout.readline().decode("utf-8")
                # out_time_ms=3505000
                if "out_time_ms" in line:
                    seconds_processed = int(line[12:]) / 1000
                    seconds_increase = seconds_processed - previous_seconds_processed
                    progress_bar.update(seconds_increase)
                    previous_seconds_processed = seconds_processed
        except KeyboardInterrupt:
            progress_bar.close()
            self._process.kill()
            log.info("[KeyboardInterrupt] FFmpeg process killed. Exiting Better FFmpeg Progress.")
            sys.exit(0)

            # width, height = os.get_terminal_size()
            # print("\r" + " " * (width - 1) + "\r", end="")
            # print("FFmpeg process complete.")


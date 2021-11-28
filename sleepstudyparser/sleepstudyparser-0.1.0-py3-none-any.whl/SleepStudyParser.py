import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from sleepstudyparser.objects.Report import Report


class SleepStudyParser:
    def __init__(
            self,
            number_of_days: int = 1,
            report_name: str = "SleepStudy",
            report_path: Optional[str] = None,
    ):
        self._number_of_days = number_of_days
        self._report_name = report_name
        self._report_path = report_path

    def _generate_sleep_study_command(self):
        command_arguments = [
            "powercfg",
            "/sleepstudy",
            "/output",
            f"{Path(self._report_path) / self._report_name}.html",
            "/duration",
            f"{self._number_of_days}",
        ]
        command = " ".join(command_arguments)
        return command

    def _ensure_report_path(self):
        if self._report_path is None or not Path(self._report_path).exists():
            self._report_path = tempfile.gettempdir()

    def _generate_html_report(self):
        self._ensure_report_path()
        command = self._generate_sleep_study_command()
        subprocess.check_output(command)

    def parse(self):
        self._generate_html_report()
        return Report.make(f"{Path(self._report_path) / self._report_name}.html")

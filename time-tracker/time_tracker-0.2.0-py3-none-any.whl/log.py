import logging
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path


class Logger:
    def __init__(self):
        # Load envs
        load_dotenv()
        self.apply_configs()

    def apply_configs(
        self, format: str = "%(asctime)-10s | %(levelname)s | %(message)s"
    ):
        self.log_folder = Path(os.getenv("TT_LOG_FOLDER", "."))

        self.log_file = self.log_folder / f"{(datetime.today()).strftime('%Y%m%d')}.log"
        logging.basicConfig(filename=self.log_file, format=format, level=logging.INFO)

    def write_thought(self, message: str):

        logger = logging.getLogger()  # Logger
        logger_handler = logging.FileHandler(
            filename=self.log_file
        )  # Handler for the logger
        logger.addHandler(logger_handler)
        FORMAT = "thought: %(message)s"

        # New formatter for the handler:
        logger_handler.setFormatter(logging.Formatter(FORMAT))

        logging.info(message)
        logger.removeHandler(logger_handler)

    def retrieve_thoughts(self):

        list_of_files = list(self.log_folder.glob("*.log"))

        thoughts: list[str] = []

        for file in list_of_files:
            with open(file, "r") as file:
                content = file.readlines()
                filtered_logs = list(filter(self.is_thought_line, content))

                if len(filtered_logs) > 0:
                    thoughts.extend(filtered_logs)

        for thought in thoughts:
            print(thought)

        return thoughts

    def is_thought_line(self, message: str):
        return message.startswith("thought")

    def get_logs(self, last_log: bool, output: bool):
        if last_log:
            list_of_files = list(self.log_folder.glob("*.log"))
            list_of_files_not_empty = list(
                filter(lambda x: os.path.getsize(x) > 0, list_of_files)
            )  # Remove all empty files

            if list_of_files_not_empty == []:
                print("No logs yet")
                return None

            latest_file = max(
                list_of_files_not_empty, key=os.path.getctime
            )  # List the last log by creation date

            if output:
                with open(latest_file, "r") as file:
                    content = file.read()
                    print(content)  # Output to stdout
                    return content
            else:
                os.system(f"open {latest_file}")  # Open directory

        else:
            os.system(f"open {self.log_folder}")

        return True

    def info(self, data):
        logging.info(data)

    def warning(self, data):
        logging.warn(data)

    def error(self, data):
        logging.error(data)

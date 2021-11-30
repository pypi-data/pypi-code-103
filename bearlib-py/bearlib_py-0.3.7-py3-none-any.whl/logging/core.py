from datetime import datetime
import os
from sys import argv, exit
from bearlib.logging.webhooks import types, WebhookFailException, Webhook


class Logger:
    """
    BearLib core logger.
    Allows for sending of logs to files, stdout, and various webhooks.

    :param level: Log level
    :param echo: Whether or not to echo to stdout
    :param directory: Log directory
    :param filename: Log filename
    :param write: Whether or not to write to file
    :param exit_on_critical: Whether or not to crash on critical error
    """

    COUNTS = {"DEBUG": 0, "INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0}
    LEVELS = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50,
    }
    log_template = "[{tstamp}] [{level}] {message}"
    tstamp_template = "%Y-%m-%dT%H:%M:%S.%f"
    webhooks = []

    def __init__(
        self,
        level: str = "WARNING",
        echo: bool = False,
        directory: str = None,
        filename: str = None,
        write: bool = True,
        exit_on_critical: bool = True,
    ):
        # Seems asinine, but allows for non-boolean values to set echo to False
        if exit_on_critical is True:
            self.exit_on_critical = True
        else:
            self.exit_on_critical = False
        if echo is True:
            self.echo = True
        else:
            self.echo = False
        if level not in self.LEVELS.keys():
            level = "WARNING"
        self.level = self.LEVELS[level]
        if filename is None:
            tstamp = datetime.now().strftime("%m-%d-%y_%H-%M-%S")
            filename = f"{argv[0].replace('.py','')}_{tstamp}.log"
        if directory is None:
            directory = os.getcwd()
        if not os.path.isdir(directory):
            os.mkdir(directory)
        self.filename = filename
        self.directory = directory
        self.filepath = os.path.join(directory, filename)
        if write is True:
            self.write = True
            if not os.access(self.directory, os.W_OK):
                self.write = False
                self.echo = True
                return
            if os.path.isfile(self.filepath):
                os.remove(self.filepath)
            self.file = open(self.filepath, "a+", buffering=1)
        else:
            self.write = False

        for level in list(self.LEVELS.keys()):
            self.bind_new_level(level.lower())

    def add_log_level(self, level: str, value: int):
        """
        Add a new logging level

        :param level: Name of the log level (automatically uppercased)
        :param value: Int level of log. Used to determine if message is logged
        """
        level = level.upper()
        if level in self.LEVELS.keys():
            self.log(
                "WARNING",
                f"Log level {level} exists with value {self.LEVELS[level]}"
                + ". Not changing log levels",
            )
            return
        self.LEVELS[level] = value
        self.COUNTS[level] = 0
        self.log("INFO", f"Added new log level {level} with value {value}")
        self.bind_new_level(level)

    def bind_new_level(self, name: str):
        """
        Create an alias for logger.log(name, message)

        Automatically lowercases the function name
        """

        def level(message):
            self.log(level.__name__.upper(), message)

        level.__name__ = name.lower()
        self.__setattr__(name, level)

    def get_level_count(self, level: str) -> int:
        """
        Gets the number of messages at that log level

        :param str level: Log level name
        """
        if level in self.COUNTS:
            return self.COUNTS[level]
        # Return -1 since level doesn't exist,
        # but is non-critical for getting counts
        return -1

    def change_path(self, directory: str = None, filename: str = None):
        """
        Changes the directory and/or filename of the log

        :param directory: The new directory
        :param filename: The new file name
        """
        if directory is None and filename is None:
            self.log(
                "WARNING",
                "Missing both directory and filename. Log path not changed.",
            )
            return
        if directory is None:
            directory = self.directory
        if filename is None:
            filename = self.filename
        if not os.path.isdir(directory):
            os.mkdir(directory)
        self.filename = filename
        self.directory = directory
        self.filepath = os.path.join(directory, filename)
        if os.path.isfile(self.filepath):
            os.rename(self.filepath, f"{self.filepath}.bak")
        self.log("INFO", f"Changed log path to {self.filepath}")
        self.file.close()
        self.file = open(self.filepath, "a+")

    def change_level(self, level: str):
        """
        Changes the level of the logger

        :param level: Max level to include in the logs
        """
        if level not in self.LEVELS.keys():
            level = self.level
        self.level = self.LEVELS[level]
        self.log("INFO", f"Changed log level to {level}")

    def log(self, level: str, message: str):
        """
        Add a log message

        :param level: Level of message
        :param message: Log message
        """
        if level in self.LEVELS.keys():
            self.COUNTS[level] += 1
            if self.LEVELS[level] >= self.level:
                tstamp = datetime.now().strftime(self.tstamp_template)
                entry = self.log_template.format(
                    tstamp=tstamp, level=level, message=message
                )
                if self.write:
                    self.file.write(entry + "\n")
                if self.echo:
                    print(entry)
                if len(self.webhooks) > 0:
                    for hook in self.webhooks:
                        hook.add_message(level, message, tstamp)
        else:
            self.log(
                "WARNING", f"Attempted to log with non-existent level {level}"
            )
        if level == "CRITICAL" and self.exit_on_critical:
            exit(1)

    def add_webhook(self, webhook: Webhook):
        """
        Add a new webhook to the logger

        :param webhook: Webhook to add
        """
        if type(webhook) not in types:
            self.log(
                "WARNING",
                f"Webhook type {type(webhook)} not supported. "
                + "Not adding to logging",
            )
            return
        self.webhooks.append(webhook)

    def close_log(self):
        """
        Closes the log and saves the file (if one is open).
        Also sends all data to webhooks that have been added.
        """
        self.log("INFO", "Closing log")
        for hook in self.webhooks:
            try:
                hook.send_to_hook()
            except WebhookFailException as e:
                self.log(
                    "ERROR",
                    f"Failed to send log to {hook.__class__.__name__}"
                    + f"\n  Error code: {e.error_code}",
                )
        if self.write:
            self.file.close()
            self.write = False

    close = close_log

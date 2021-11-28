import logging
from multiprocessing import Process

from text_analyzer.bad_arguments_provided_exception import BadArgumentsProvidedException
from text_analyzer.constants import WEB_LINK, LOCAL_FILE
from text_analyzer.file_utils import clean_file_lead, read_input_text_local, read_input_text_web
from text_analyzer.flag_scripts import print_help, view_file_reports, text_analyzer


class Launcher:

    def __init__(self, argv):
        self.args = argv
        self.validate_args()

    def validate_args(self):
        if len(self.args) < 2:
            raise AttributeError("Insufficient arguments number provided.")
        argument_validators = {"-h": self.validate_args_help,
                               "-f": self.validate_args_files,
                               "-r": self.validate_args_files,
                               "--view": self.validate_args_view}
        validator = argument_validators[self.args[1]]
        validator(self.args)

    def validate_args_help(self):
        if len(self.args) != 2:
            raise BadArgumentsProvidedException("Probably you mean -h.")

    def validate_args_files(self):
        if len(self.args) == 2:
            raise BadArgumentsProvidedException("Provide files to analyze.")

    def validate_args_view(self):
        if len(self.args) != 3:
            raise BadArgumentsProvidedException("--view options supports only one filename.")

    def launch(self):
        arg_func_map = {"-h": print_help, "-f": self.spawn_analyzer_processes,
                        "-r": self.spawn_analyzer_processes, "--view": self.launch_view_file_reports}
        run_argument = self.args[1]
        arg_func = arg_func_map[run_argument]

        arg_func()

    def launch_view_file_reports(self):
        filename = self.args[2]
        view_file_reports(filename)

    def spawn_analyzer_processes(self):
        file_leads = []
        for file_lead in self.args[2:]:
            filename, is_web_link = clean_file_lead(file_lead)
            file_lead_type = WEB_LINK if is_web_link else LOCAL_FILE
            logging.info(f"{file_lead_type}|{filename}")
            file_leads.append((is_web_link, filename, file_lead))

        subprocesses = []
        for file_lead in file_leads:
            process = Process(target=self.launch_text_analyzer, args=file_lead)
            subprocesses.append(process)
            process.start()

        for process in subprocesses:
            process.join()

    @staticmethod
    def launch_text_analyzer(is_web_link: bool, filename: str, file_lead: str):
        if is_web_link:
            text = read_input_text_web(file_lead)
        else:
            text = read_input_text_local(file_lead)
        text_analyzer(text, filename)

    @staticmethod
    def launch_print_help():
        print_help()

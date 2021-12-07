from kntgen.bloc.bloc_template import BlocTemplate
from kntgen.cmd import Command, CommandOption
from kntgen.constants import SUPPORTED_SOURCE_FORMAT
from kntgen.file_helpers import get_flutter_project_package
from kntgen.model.bloc import Bloc
from kntgen.model.exception import DefinedErrorMessage


class BlocCommand(Command):
    def __init__(self, options):
        super(BlocCommand, self).__init__()
        # For future usage
        self.options = CommandOption(options)
        self.project_package = get_flutter_project_package()

    def create_files(self, content_file: str, file_extension: str):
        try:
            if file_extension == SUPPORTED_SOURCE_FORMAT[0]:
                self._create_files_from_json(content_file)
            elif file_extension == SUPPORTED_SOURCE_FORMAT[1]:
                self._create_files_from_yaml(content_file)
        except Exception as e:
            DefinedErrorMessage.print_error(e)
            exit(1)

    def _create_files_from_json(self, json_str: str):
        bloc = BlocTemplate(
            self.project_package,
            Bloc.from_json(json_str)
        )
        bloc.create_files()

    def _create_files_from_yaml(self, yaml_stream):
        bloc = BlocTemplate(
            self.project_package,
            Bloc.from_yaml(yaml_stream)
        )
        bloc.create_files()

from kntgen.cmd import Command, CommandOption
from kntgen.constants import *
from kntgen.file_helpers import get_flutter_project_package
from kntgen.model.exception import *
from kntgen.model.network import RestfulService
from kntgen.model.postman import PostmanCollection
from kntgen.network.network_template import NetworkTemplate


class NetworkCommand(Command):
    def __init__(self, options):
        super(NetworkCommand, self).__init__()
        # For future usage
        self.options = CommandOption(options)
        self.project_package = get_flutter_project_package()
        self.append_file = False

    @staticmethod
    def convert_postman_to_generate_form(postman_info: dict) -> RestfulService:
        postman_collection = PostmanCollection(**postman_info)
        return postman_collection.convert_to_restful_api_model()

    def create_files(self,
                     content_file: str,
                     file_extension: str,
                     append_file: bool):
        self.append_file = append_file or False
        try:
            if file_extension == SUPPORTED_SOURCE_FORMAT[0]:
                self._create_files_from_json(content_file)
            elif file_extension == SUPPORTED_SOURCE_FORMAT[1]:
                self._create_files_from_yaml(content_file)
        except Exception as e:
            DefinedErrorMessage.print_error(e)
            exit(1)

    def _create_files_from_json(self, json_str: str):
        service = NetworkTemplate(
            self.project_package,
            RestfulService.from_json(json_str)
        )
        service.create_files(self.append_file)

    def _create_files_from_yaml(self, yaml_stream):
        service = NetworkTemplate(
            self.project_package,
            RestfulService.from_yaml(yaml_stream)
        )
        service.create_files(self.append_file)

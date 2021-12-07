# coding=utf-8
from kntgen.cmd import *
from kntgen.file_helpers import *
from kntgen.model.json import JSON
from kntgen.printer import beauty_printer
from kntgen.str_helpers import to_snake_case


class JsonCommand(Command):
    def __init__(self, model_name, options):
        super(JsonCommand, self).__init__()
        self.model_name = model_name
        # For future usage
        self.options = CommandOption(options)

    def create_files(self,
                     json_str: str,
                     folder: str = None,
                     need_beauty_print=True):
        json_template = JSON(
            model_name=self.model_name,
            json_str=json_str
        )
        content_files = json_template.create_model_files()
        file_path, additional_info = create_file(
            content=content_files,
            file_name=to_snake_case(self.model_name),
            file_extension='dart',
            folder=folder or './lib/model'
        )
        if need_beauty_print:
            beauty_printer(
                title='Successfully created model file',
                content=[make_content_output_file(file_path,
                                                  additional_info)]
            )
        return file_path, additional_info

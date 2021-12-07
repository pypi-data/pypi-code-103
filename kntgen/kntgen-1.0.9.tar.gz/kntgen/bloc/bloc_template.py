# coding=utf-8
from kntgen.file_helpers import make_content_output_file
from kntgen.model.bloc import Bloc
from kntgen.printer import beauty_printer
from kntgen.str_helpers import *
from kntgen.template import Template


@auto_str
class BlocTemplate(Template):
    def __init__(self, package_name: str, bloc: Bloc):
        super().__init__('bloc')
        self.name_lower = create_file_name(bloc.name)
        self.package_name = package_name
        self.bloc = bloc
        self.content_print_out = []

    def extract_content_from_template(self, template):
        return template.render(
            bloc=self.bloc,
            package_name=self.package_name
        )

    def create_files(self):
        self._create_bloc()
        self._create_bloc_test()
        beauty_printer(title='Successfully created BLoC related files',
                       content=self.content_print_out)

    def _create_bloc(self):
        scene_name = 'bloc'
        file_path, additional_info = self.create_file_from_template(
            class_name=f'{self.name_lower}_{scene_name}',
            template_file=f'{scene_name}.dart',
            output_path='lib/bloc'
        )
        self.content_print_out.append(
            make_content_output_file(file_path, additional_info))

    def _create_bloc_test(self):
        scene_name = 'bloc_test'
        file_path, additional_info = self.create_file_from_template(
            class_name=f'{self.name_lower}_{scene_name}',
            template_file=f'{scene_name}.dart',
            output_path='test/bloc'
        )
        self.content_print_out.append(
            make_content_output_file(file_path, additional_info))

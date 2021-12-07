# coding=utf-8
from kntgen.file_helpers import *
from kntgen.json_to_dart.json_cmd import JsonCommand
from kntgen.model.network import *
from kntgen.printer import beauty_printer
from kntgen.str_helpers import *
from kntgen.template import Template


@auto_str
class NetworkTemplate(Template):
    def __init__(self, package_name: str, service: RestfulService):
        super().__init__('network')
        self.name_lower = create_file_name(service.name)
        self.package_name = package_name
        self.service = service
        self.generating_api = None
        self.append_file = False
        self.content_print_out = []

    def extract_content_from_template(self, template):
        return template.render(
            service=self.service,
            package_name=self.package_name,
            api=self.generating_api
        )

    def create_files(self, append_file: bool):
        self.append_file = append_file or False
        self._create_api_service()
        self._create_cloud_repo()
        self._create_data_cloud_repo()
        self._create_model_files()
        self._create_use_case_files()
        self._create_fixture_files()
        beauty_printer(title='Successfully created network related files',
                       content=self.content_print_out)

    def _create_api_service(self):
        scene_name = 'network'
        file_path, additional_info = self.create_file_from_template(
            class_name='api_service',
            template_file=f'{scene_name}.dart',
            sub_folder_template='service',
            output_path='lib/data/network',
            append_to_file=self.append_file,
            fixed_header=IMPORT_API_SERVICE_HEADER
        )
        self.content_print_out.append(
            make_content_output_file(file_path, additional_info))

    def _create_cloud_repo(self):
        scene_name = 'cloud_repo'
        file_path, additional_info = self.create_file_from_template(
            class_name=scene_name,
            template_file=f'{scene_name}.dart',
            sub_folder_template='repo',
            output_path='lib/repo',
            append_to_file=self.append_file,
            fixed_header=IMPORT_CLOUD_REPO_HEADER,
            fixed_footer=IMPORT_CLOUD_REPO_FOOTER
        )
        self.content_print_out.append(
            make_content_output_file(file_path, additional_info))

    def _create_data_cloud_repo(self):
        scene_name = 'data_cloud_repo'
        file_path, additional_info = self.create_file_from_template(
            class_name=scene_name,
            template_file=f'{scene_name}.dart',
            sub_folder_template='repo',
            output_path='lib/data/network/repo',
            append_to_file=self.append_file,
            fixed_header=IMPORT_DATA_CLOUD_REPO_HEADER,
            fixed_footer=IMPORT_DATA_CLOUD_REPO_FOOTER
        )
        self.content_print_out.append(
            make_content_output_file(file_path, additional_info))

    def _create_model_files(self):
        for index, api in enumerate(self.service.apis):
            self.generating_api = api
            # Request models
            file_path, additional_info = self.create_file_from_template(
                class_name=api.request_type_snake_case,
                template_file='request_model.dart',
                sub_folder_template='model',
                output_path='lib/model/network/request'
            )
            self.content_print_out.append(
                make_content_output_file(file_path, additional_info))
            # Add request file to [network_models.dart] exportation
            create_file(
                content=f'export \'network/request/{api.request_type_snake_case}.dart\';\n',
                file_name='network_models',
                file_extension='dart',
                folder='./lib/model',
                append_to_file=True
            )
            # Response models
            file_path, additional_info = JsonCommand(
                model_name=api.response_type_pascal_case,
                options={}
            ).create_files(
                json_str=api.response_json,
                folder='./lib/model/network/response',
                need_beauty_print=False
            )
            self.content_print_out.append(
                make_content_output_file(file_path, additional_info))
            # Add response file to [network_models.dart] exportation
            file_path, additional_info = create_file(
                content=f'export \'network/response/{api.response_type_snake_case}.dart\';\n',
                file_name='network_models',
                file_extension='dart',
                folder='./lib/model',
                append_to_file=True
            )
            if index == len(self.service.apis) - 1:
                self.content_print_out.append(
                    make_content_output_file(file_path, additional_info))

    def _create_use_case_files(self):
        # Use cases
        file_path, additional_info = self.create_file_from_template(
            class_name='base_use_case',
            template_file='base_use_case.dart',
            sub_folder_template='use_case',
            output_path='lib/use_case/core',
            append_to_file=True
        )
        self.content_print_out.append(
            make_content_output_file(file_path, additional_info))
        for index, api in enumerate(self.service.apis):
            use_case_name = f'{api.name_snake_case}_use_case'
            self.generating_api = api
            file_path, additional_info = self.create_file_from_template(
                class_name=use_case_name,
                template_file='network_use_case.dart',
                sub_folder_template='use_case',
                output_path='lib/use_case'
            )
            self.content_print_out.append(
                make_content_output_file(file_path, additional_info))
            # Add to [use_cases.dart] exportation
            file_path, additional_info = create_file(
                content=f'export \'{use_case_name}.dart\';\n',
                file_name='use_cases',
                file_extension='dart',
                folder='./lib/use_case',
                append_to_file=True
            )
            if index == len(self.service.apis) - 1:
                self.content_print_out.append(
                    make_content_output_file(file_path, additional_info))
            # Test Use cases
            file_path, additional_info = self.create_file_from_template(
                class_name=f'{use_case_name}_test',
                template_file='network_use_case_test.dart',
                sub_folder_template='use_case',
                output_path='test/use_case'
            )
            self.content_print_out.append(
                make_content_output_file(file_path, additional_info))

    def _create_fixture_files(self):
        file_path, additional_info = self.create_file_from_template(
            class_name='fixture_reader',
            template_file='fixture_reader.dart',
            sub_folder_template='other',
            output_path='test/fixture'
        )
        self.content_print_out.append(
            make_content_output_file(file_path, additional_info))
        for api in self.service.apis:
            file_path, additional_info = create_file(
                content=api.response_json,
                file_name=f'{api.response_type_snake_case}',
                file_extension='json',
                folder='./test/fixture'
            )
            self.content_print_out.append(
                make_content_output_file(file_path, additional_info))

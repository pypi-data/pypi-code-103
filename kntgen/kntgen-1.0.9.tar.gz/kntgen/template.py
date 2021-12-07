from jinja2 import Environment, PackageLoader

from kntgen.file_helpers import *
from kntgen.str_helpers import auto_str


@auto_str
class Template(object):
    def __init__(self, folder_template: str):
        self.folder_template = folder_template
        self.env = Environment(
            loader=PackageLoader('kntgen_templates', folder_template),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def create_file_from_template(self,
                                  class_name,
                                  file_extension='dart',
                                  template_file=None,
                                  sub_folder_template=None,
                                  include_root_folder=False,
                                  output_path=None,
                                  append_to_file=False,
                                  fixed_header: str = None,
                                  fixed_footer: str = None):
        if template_file is None:
            if file_extension:
                template_file = f'{class_name}.{file_extension}'
            else:
                template_file = class_name[len(self.name_lower):]

        env = self.env
        if sub_folder_template is not None:
            env = Environment(
                loader=PackageLoader(
                    'kntgen_templates',
                    f'{self.folder_template}/{sub_folder_template}'
                ),
                trim_blocks=True,
                lstrip_blocks=True
            )
        template = env.get_template(template_file)
        content = self.extract_content_from_template(template)

        if output_path is None:
            output_path = '../'

        if output_path.endswith('/'):
            output_path = output_path[:-1]

        if include_root_folder:
            folder = f'./{output_path}/{self.name_lower}'
        else:
            folder = f'./{output_path}'

        return create_file(
            content=content,
            file_name=class_name,
            file_extension=file_extension,
            folder=folder,
            append_to_file=append_to_file,
            fixed_header=fixed_header,
            fixed_footer=fixed_footer
        )

    def extract_content_from_template(self, template):
        return template.render()

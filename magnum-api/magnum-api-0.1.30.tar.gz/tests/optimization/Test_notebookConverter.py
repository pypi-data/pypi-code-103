import os

from magnumapi.commons import text_file
from magnumapi.optimization import NotebookConverter
from tests.resource_files import create_resources_file_path


def test_convert_notebook_to_script():
    # arrange
    notebook_name = 'Geometry'
    notebook_path = create_resources_file_path(os.path.join('resources/optimization', notebook_name + '.ipynb'))
    script_path = create_resources_file_path(os.path.join('resources/optimization', notebook_name + '.py'))

    # act
    NotebookConverter.convert_notebook_to_script(notebook_path, notebook_name, script_path)

    # assert
    script_ref_path = create_resources_file_path(os.path.join('resources/optimization', notebook_name + '_ref.py'))

    assert text_file.readlines(script_ref_path) == text_file.readlines(script_path)

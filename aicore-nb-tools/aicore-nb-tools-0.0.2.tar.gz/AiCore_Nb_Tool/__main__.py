#%%
from questions_utils import parse_yaml
from questions_utils import create_cells
from gui import create_gui
import nbformat as nbf
from urllib.request import urlretrieve
import tempfile
#%%
# Ask for a token
token = input('Please, introduce your Token: ')

# Characteristics of the notebook
cohort, lesson_ids, out_name, first_room, students_per_room = create_gui(token)
lessons_list = []

with tempfile.TemporaryDirectory(dir='.') as tmpdirname:
    for lesson_id in lesson_ids:
        URL = f'https://aicore-questions.s3.amazonaws.com/{lesson_id}.yaml'
        urlretrieve(URL, f'{tmpdirname}/{lesson_id}.yaml')
        lessons_list.append(f'{tmpdirname}/{lesson_id}.yaml')
        
    # Create the notebook
    nb = nbf.v4.new_notebook()
    questions = parse_yaml(file=lessons_list)
    cells = create_cells(questions, cohort, first_room, students_per_room)
    nb['cells'] = cells

    with open(out_name, 'w') as f:
        nbf.write(nb, f)

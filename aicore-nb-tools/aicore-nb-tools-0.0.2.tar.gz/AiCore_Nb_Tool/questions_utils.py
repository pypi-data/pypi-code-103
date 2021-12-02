from typing import List
from typing import Union
import random
import json
import yaml
import nbformat as nbf
from urllib.error import HTTPError
import tempfile
from urllib.request import urlretrieve

class RussianRoulette:
    '''
    This class creates a list of students that will be randomly selected
    one by one to answer questions
    Arguments
    ---------
    students: List[str]
        A list containing the names of the students
    '''
    def __init__(self, students: List[str]):
        self.students = students
        self.__backup = students.copy()
        random.shuffle(self.students)

    def choose_victim(self):
        '''
        Prints out the a random name of the list 
        and removes it from the list so the same 
        student doesn't answer twice
        '''
        print(self.students.pop())
        if not self.students:
            self._restart()

    def _restart(self):
        self.students = self.__backup.copy()
        random.shuffle(self.students)


class Cohort(list):
    def __init__(self, cohort: str):
        data = self._check_cohort(cohort)
        list.__init__(self, [x['first_name'] for x in data])
    
    def missing(self, students: Union[List[str], str]):
        if isinstance(students, str):
            self._missing_single(students)
        elif isinstance(students, list):
            for student in students:
                self._missing_single(student)
        else:
            print('You need to provide either a list or a string')


    def _missing_single(self, student: str):
        try:
            self.remove(student.capitalize())
            print(f'{student} removed from today\'s lesson')
        except ValueError:
            self._print_error(student)

    def _print_error(self, student):
        print(f'{student} is not in the student list')
        students_str = '\n'.join(self)
        print(f'Here is a list of the students in the cohort: {students_str}')
        
    @staticmethod
    def _check_cohort(cohort):
        file = f'https://aicore-questions.s3.amazonaws.com/cohorts/{cohort}.json'
        try:
            with tempfile.TemporaryDirectory() as temp:
                urlretrieve(file, f'{temp}/{cohort}.json')
                with open(f'{temp}/{cohort}.json') as f:
                    data = json.load(f)
        except HTTPError:
            raise ValueError('The cohort you specified does not exist')
        return data

def pairwise(iterable) -> List[tuple]:
    if len(iterable) % 2 != 0: # if odd
        list_1 = iterable[:int(len(iterable)/2)]
        list_2 = iterable[int(len(iterable)/2):-1]
        list_3 = iterable[-1]
        out = list(zip(list_1, list_2))
        out.append(list_3)
    else:
        list_1 = iterable[:int(len(iterable)/2)]
        list_2 = iterable[int(len(iterable)/2)]
        out = list(zip(list_1, list_2))
    return out

class GroupCreator:
    def __init__(self, students: List[str], start_room: int, group_size: int=3):
        self.groups = []
        self.start_room = start_room
        random.shuffle(students)
        idx = 0
        self.num_groups = len(students) // group_size
        while idx < len(students):
            self.groups.append(students[idx:idx + group_size])
            idx += group_size
        if len({len(i) for i in self.groups}) == 1: # Check that all the lists have the same number of students
            self.groups[-1] += [''] * (group_size - len(self.groups[-1]))

        
    def __str__(self):
        msg = ''
        if self.num_groups > 3:
            pair_group = pairwise(self.groups)
            last_group = None
            if isinstance(pair_group[-1], list):
                last_group = pair_group[-1]
                pair_group = pair_group[:-1]
            for group_idx, groups in enumerate(pair_group):
                msg += f'- Room {self.start_room + group_idx * 2}\t\t\t\t- Room {self.start_room + (group_idx * 2) + 1}\n'
                group1 = groups[0]
                group2 = groups[1]
                for student1, student2 in zip(group1, group2):
                    if len(student1) > 5:
                        ind = '\t\t\t\t'
                    else:
                        ind = '\t\t\t\t\t'
                    msg += f'\t- {student1}{ind}- {student2}\n'
            if last_group:
                msg += f'- Room {self.start_room + group_idx * 2 + 2}\n'
                for student in last_group:
                    msg += f'\t- {student}\n'
        else:
            for group_idx, group in enumerate(self.groups):
                msg += f'- Room {self.start_room + group_idx}\n'
                for student in group:
                    msg += f'\t- {student}\n'
        
        return msg


def parse_yaml(file='.questions.yaml') -> List[dict]:

    if isinstance(file, list):
        questions = []
        for f in file:
            with open(f, 'r') as stream:
                data_loaded = yaml.safe_load(stream)
            questions.extend(data_loaded['questions'])

    elif isinstance(file, str):
        with open(file, 'r') as stream:
            data_loaded = yaml.safe_load(stream)
        questions = data_loaded['questions']

    else:
        raise ValueError('"file" has to be a list or a string')

    return questions

def create_cells(questions: List[dict], cohort='theta', init_room=2, students_per_room=3, only_questions=False):
    cells = []
    if not only_questions:
        code = 'from AiCore_Nb_Tool.questions_utils import Cohort \n' \
            + 'from AiCore_Nb_Tool.questions_utils import RussianRoulette \n' \
            + 'from AiCore_Nb_Tool.questions_utils import GroupCreator \n'   \
            + '\n' \
            + f'{cohort} = Cohort("{cohort}") \n'   \
            + 'missing_students = [] \n'   \
            + f'{cohort}.missing(missing_students)'

        cells.append(nbf.v4.new_code_cell(code))

        code = f'print(GroupCreator({cohort}, {init_room}, {students_per_room}))'
    
        cells.append(nbf.v4.new_code_cell(code))

        code = f'rr = RussianRoulette({cohort})'

        cells.append(nbf.v4.new_code_cell(code))

    for n, question in enumerate(questions, start=1):
        text = f'## Question {n}. \n {question["question"]}'
        cells.append(nbf.v4.new_markdown_cell(text))
        if not only_questions:
            code = 'rr.choose_victim()'
            cells.append(nbf.v4.new_code_cell(code))
    
    return cells
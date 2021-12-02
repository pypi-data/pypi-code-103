# %%
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
from urllib.request import urlretrieve
import requests
import glob
from typing import Union
from typing import Tuple
import yaml
import tempfile
import zipfile
# %%
class Window(QWidget):

    def __init__(self,
                 token:str,
                 pathway:str='Essentials',
                 api_url:str='https://h0idexq6rd.execute-api.eu-west-1.amazonaws.com/prod/content/allLessons'
                 ):
        super().__init__()
        self._start_modules_lessons(pathway=pathway, api_url=api_url, token=token)
        self.setWindowTitle("Notebook Generator")

        # Create a top-level layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a button to close the window
        self.button = QPushButton('Create Notebook', self)
        self.button.clicked.connect(self.close)

        # Text box with the number of the room
        label_number = QLabel()
        label_number.setText("Initial Breakout Room: ")

        # Create a text bar to set the initial breakout room
        self.room = QLineEdit(self)
        self.room.setText("20")
        self.room.returnPressed.connect(self.button.click)

        # Text box to give name to the notebook
        label_1 = QLabel()
        label_1.setText("Name of the Notebook: ")
        label_students_per_room = QLabel()
        label_students_per_room.setText("How many students per room: ")
        self.notebook_name = QLineEdit(self)
        self.notebook_name.setText("Notebook")
        self.notebook_name.returnPressed.connect(self.button.click)

        ###############################################################################
        # DropDown menu with the name of each cohort.                                   #
        # TODO: Get the active cohorts                                                  #
        ################################################################################
        self.cohort = QComboBox()
        self.cohort.addItems(["Theta Cohort", "Sep21 Cohort", "Oct21 Cohort", "Nov21 Cohort"])

        # Spin Box to define how many students per breakout room
        self.students_per_room = QSpinBox()
        self.students_per_room.setMinimum(1)
        self.students_per_room.setValue(3)

        # Create and connect the combo box to switch between pages
        self.pageCombo = QComboBox()

        ###############################################################################
        # Add all the modules to the DropDown Menu and connect each module to each page #
        # that we are defining now                                                      #
        ################################################################################
        self.pageCombo.addItems(self.module_names)
        self.pageCombo.activated.connect(self.switchPage)


        # Create the stacked layout
        self.stackedLayout = QStackedLayout()

        for value in self.module_lesson.values():
            for lesson in value['Lessons']:
                value['Page_Layout'].addRow(lesson['CheckBox'])
            value['Page'].setLayout(value['Page_Layout'])
            self.stackedLayout.addWidget(value['Page']) 

        layout.addWidget(self.cohort)
        layout.addWidget(self.pageCombo)

        layout.addLayout(self.stackedLayout)
        layout.addWidget(label_number)
        layout.addWidget(self.room)
        layout.addWidget(label_students_per_room)
        layout.addWidget(self.students_per_room)
        layout.addWidget(label_1)
        layout.addWidget(self.notebook_name)
        layout.addWidget(self.button)

    def switchPage(self):
        self.stackedLayout.setCurrentIndex(self.pageCombo.currentIndex())


    def _start_modules_lessons(self, pathway, api_url, token):
        # Check is the pathway exists or if the given name doesn't coincide
        # more than one result
        file = self._check_pathway(pathway)
        

        # Download the json file with the lessons and their information
        r = requests.get(api_url, headers={'x-api-key': f"{token}"})
        if r.status_code != 200:
            raise ValueError('Invalid API or Token, please contact the team to get a new Token')
        lessons = r.json()
        
        self.module_lesson = {name: {} for name in self.module_names}

        for name, id in zip(self.module_lesson.keys(), self.module_ids):
            self.module_lesson[name]['Page'] = QWidget()
            self.module_lesson[name]['Page_Layout'] = QFormLayout()
            lesson_list = [{'Name': lesson['name'],
                            'id': lesson['id'],
                            'CheckBox': QCheckBox(lesson['name']),
                            'idx': lesson['idx']} 
                            for lesson in lessons 
                            if lesson['module_id'] == id]
            lesson_list.sort(key=lambda x: x['idx'])
            self.module_lesson[name]['Lessons'] = lesson_list

    def _check_pathway(self, pathway:str) -> Union[bool, None]:
        '''
        Checks if a pathway is currently in the course and returns the
        name of the file corresponding to that pathway
        
        Parameters
        ----------
        pathway: str
            The name of the pathway we want to get
            It doesn't have to match the whole name
        
        Returns
        -------
        path: str
            The name of the file containing the modules of pathway
        '''
        with tempfile.TemporaryDirectory(dir='.') as tmpdirname:
            URL = "https://aicore-questions.s3.amazonaws.com/pathways/pathways.zip"
            urlretrieve(URL, f'{tmpdirname}/pathways.zip')
            with zipfile.ZipFile(f'{tmpdirname}/pathways.zip', 'r') as zip_ref:
                zip_ref.extractall(f'{tmpdirname}/pathways')
            path = glob.glob(f'{tmpdirname}/pathways/*{pathway}*')
            all_paths = '\n'.join(path)

            if len(path) == 1:
                self.module_names, self.module_ids = self._get_modules(path[0])
                return path[0]

            elif len(path) > 1:
                raise ValueError('Your query returned more than one pathway' +
                                'Here is the list of possible pathways: \n' +
                                all_paths)
            else:
                raise ValueError('Your query did not return any pathway' +
                                'Here is the list of possible pathways: \n' +
                                all_paths)
    
    @staticmethod
    def _get_modules(file:str) -> Tuple[list]:
        '''
        Parse the yaml file to get the modules and their ids

        Parameters
        ----------
        file: str
            The name of the file containing the modules and ids of the pathway
        
        Returns
        -------
        Tuple[list]:
            The names and ids of the lessons
            
        '''
        with open(file, mode='r') as f:
            file = yaml.safe_load(f)
        
        module_names = [module['name'] for module in file['modules']]
        module_ids = [module['id'] for module in file['modules']]

        return module_names, module_ids
            

def get_list_lessons(window_app):
    ids = []
    for module in window_app.module_lesson.values():
        ids.extend([lesson['id'] for lesson in module['Lessons'] if lesson['CheckBox'].isChecked()])

    return ids

def create_gui(token:str):
    COHORT_MAP = dict(zip(["Theta Cohort", "Sep21 Cohort", "Oct21 Cohort", "Nov21 Cohort"],
                          ['theta', 'sep21', 'oct21', "nov21"]
                          ))
    app = QApplication(sys.argv)
    window = Window(token=token)
    window.show()
    app.exec_()
    cohort = window.cohort.currentText()
    cohort = COHORT_MAP[cohort]
    lesson_ids = get_list_lessons(window)
    out = window.notebook_name.text() + '.ipynb'
    room = window.room.text()
    students_per_room = window.students_per_room.text()
    return cohort, lesson_ids, out, int(room), students_per_room
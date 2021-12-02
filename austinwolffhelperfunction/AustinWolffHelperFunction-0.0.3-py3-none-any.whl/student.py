import numpy as np

class Student:
    books = 3

    def __init__(self, ID, major, in_PE=0):
        self.ID = ID
        self.major = major
        self.in_PE = in_PE

    def catch_phrase(self):
        print('Bet on it.')

    def join_PE(self):
        self.in_PE = 1

class BloomTechStudent(Student):

    def __init__(self, ID, major, track, in_PE=0):
        super().__init__(ID, major, in_PE)
        self.track = track
    
    def hack(self):
        print('You hacked Evil Corp!')

def student_generator(student_class=BloomTechStudent):
    student_list = []

    majors = np.array(['english','history','math','computer science'])
    tracks = np.array(['front-end','backend','data science','web3'])
    for i in range(30):
        new_student = student_class(np.random.randint(1, 1000),
                                    np.random.choice(majors),
                                    np.random.choice(tracks))
        student_list.append(new_student)
    return student_list

thirty_students = student_generator()
student_attributes = []
for student in thirty_students:
    student_attributes.append((student.ID, student.major, student.track))
print(student_attributes)
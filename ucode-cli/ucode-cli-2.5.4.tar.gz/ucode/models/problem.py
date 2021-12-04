import copy
import pprint
from enum import Enum

from typing import List


class ProblemType(Enum):
    code = "code"
    bugfix = "bugfix"
    recover = "recover"


class ProblemStatus(Enum):
    draft = 0
    published = 1
    scheduled = 10


class ProgrammingLanguage(Enum):
    python3 = "python3"
    python_turtle = "python_turtle"
    pascal = "pascal"
    cpp = 'cpp'

    unknown = "-1"


class ProblemDifficulty(Enum):
    unknown = "Unknown"
    trivial = "Trivial"
    easy = "Easy"
    easy_medium = "Easy-Medium"
    medium = "Medium"
    medium_hard = "Medium-Hard"
    hard = "Hard"
    super_hard = "Super-Hard"


class JudgeMode(Enum):
    manual = 0
    oj = 1  # input - output
    soj = 2  # special jugde
    unit_test = 3
    quiz = 10  # test question


class MatchingType(Enum):
    flexible = 1
    strict = 2
    regexp = 10


class TestCase:
    def __init__(self, input="", output="", name="", explanation="", matchingtype=MatchingType.flexible, sample=False):
        self.name = name
        self.input = input
        self.output = output
        self.src_id = ""
        self.matching_type = matchingtype
        self.input_size = self.output_size = 0
        self.input_hash = self.output_hash = ''
        self.explanation = explanation
        self.sample = sample
        self.score = 0

    def __str__(self):
        s = ''
        # s += "src_id: " + str(self.src_id) + "\n"
        # s += "matching type: " + str(self.matching_type) + "\n"
        s += "input:\n" + self.input + "\n"
        s += "output:\n" + self.output + "\n"
        s += "sample:\n" + str(self.sample) + "\n"
        s += "explanation:\n" + self.explanation
        return s


class ProblemFolderFormat(str, Enum):
    ucode = "ucode"
    themis = "themis"
    cms = "cms"
    auto_detect = "auto"


class Problem:
    def __init__(self, name=""):
        self.src_id = ""
        self.translations = {}
        self.src = ""
        self.src_url = ""
        self.src_name = ""
        self.src_status_url = ""
        self.src_data = None
        self.input_type = 'stdin'
        self.output_type = 'stdout'
        self.limit_time = 1000 # ms
        self.limit_memory = 64 # MB
        self.name = name
        self.slug = ""
        self.code = ""
        self.type = ProblemType.code
        self.template = ""  # editor template
        self.preview = ""
        self.statement = self.src_id = ""
        self.statement_format = "markdown"
        self.statement_language = "vi"
        self.code_stubs = {}
        self.input_format = self.constraints = self.output_format = ""
        self.judge_mode = JudgeMode.oj
        self.xp = 100
        self.testcase_format = "ucode"
        self.testcases_sample: List[TestCase] = []
        self.stock_testcases_sample = []
        self.testcases = []
        self.stock_testcases = []
        self.testcases_sample_note = None
        self.language = ProgrammingLanguage.unknown
        self.solution = None
        self.solution_lang = "py"
        self.hint = None
        self.category = None
        self.editorial = None
        self.contest_slug = None    # hackerrank specific
        self.topics = []
        self.tags = []
        self.experience_gain = 0
        self.difficulty = 0.0
        self.difficulty_level = ProblemDifficulty.easy
        self.total_count = self.solved_count = self.success_ratio = 0

        self.public_test_cases = False
        self.public_solutions = False
        self.languages = []
        self.solutions = []  # list of solution for each language [{"lang"="", "code"=".."}]
        self.testcase_generators = []
        self.hints = []  # list of hint for each language
        self.track = None # hackerrank specific
        self.resource_files = []

    def prints(self):
        s = ''
        if self.src_url:
            s += '[//]: {}\n'.format(self.src_url)

        s += '\n# {}\n\n'.format(self.name)
        s += '\n{}\n\n'.format(self.slug)

        s += '\n*Type: {}, Difficulty: {} ({})*'.format(str(self.type), self.difficulty, self.difficulty_level)

        s += '\n\n{}'.format(self.statement)
        s += '\n\n## Input'
        s += '\n{}'.format(self.input_format)
        s += '\n\n## Constraints'
        s += '\n{}'.format(self.constraints)
        s += '\n\n## Output'
        s += '\n{}'.format(self.output_format)

        s += '\n\n## Tags'
        s += '\n{}'.format(self.tags)

        s += '\n\n## Sample Testcases: {}'.format(len(self.testcases_sample))

        if self.testcases_sample and len(self.testcases_sample) > 0:
            s += '\n\n## Sample Input'
            s += '\n```\n{}\n```'.format(self.testcases_sample[0].input)
            s += '\n\n## Sample Output'
            s += '\n```\n{}\n```\n'.format(self.testcases_sample[0].output)
            if self.testcases_sample[0].explanation:
                s += '\n\n## Explanation'
                s += '\n```\n{}\n```\n'.format(self.testcases_sample[0].explanation)

        s += '\n\n## Testcases: {}'.format(len(self.testcases))

        if self.testcases and len(self.testcases)>0:
            s += '\n\n## Sample Input'
            s += '\n```\n{}\n```'.format(self.testcases[0].input)
            s += '\n\n## Sample Output'
            s += '\n```\n{}\n```\n'.format(self.testcases[0].output)
            if self.testcases[0].explanation:
                s += '\n\n## Explanation'
                s += '\n```\n{}\n```\n'.format(self.testcases[0].explanation)

        if self.solution:
            s += '\n\n## Solution'
            s += '\n```\n{}\n```'.format(self.solution)
        return s

    def __str__(self):
        # s = "src_id: " + str(self.src_id) + "\n"
        # s += "Name: " + self.name + "\n"
        # s += "Judge mode: " + str(self.judge_mode) + "\n"
        # s += "Statement: \n"
        # s += self.statement
        # s += "\nNo of testcases: " + str(len(self.testcases))
        # s += "\nSolution: \n{}\n".format(self.solution)
        tmp = copy.deepcopy(self)

        tmp.testcases_count = len(self.testcases)
        tmp.testcases_sample_count = len(self.testcases_sample)
        tmp.testcases_sample = None
        tmp.testcases = None
        return pprint.pformat(vars(tmp), indent=2)


class Classroom:
    def __init__(self):
        self.src_id = ""
        self.name = ""
        self.language = ProgrammingLanguage.unknown
        self.students = []
        self.student_invites = []
        self.self_learners = []
        self.assignments = []
        self.scheduled_assignments = []
        self.draft_assignments = []

    def __str__(self):
        s = "src_id: " + str(self.src_id) + "\n"
        s += "Name: " + self.name + "\n"
        s += "Language: " + str(self.language)
        s += "\nNo of students: " + str(len(self.students))
        s += "\nNo of student_invites: " + str(len(self.student_invites))
        s += "\nNo of self_learners: " + str(len(self.self_learners))
        s += "\nNo of assignments: " + str(len(self.assignments))
        return s

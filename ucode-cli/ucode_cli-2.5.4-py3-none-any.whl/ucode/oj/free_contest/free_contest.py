import glob
import os

from ucode.helpers.clog import CLog
from ucode.helpers.misc import findfiles
from ucode.models.problem import Problem
from ucode.services.dsa.problem_service import ProblemService
from ucode.services.testcase.testcase_service import TestcaseService
from unidecode import unidecode


class FreeContest:
    @staticmethod
    def load_all_free_contest(folder):
        folders = glob.glob(os.path.join(folder, "*"))
        contests = []
        for f in folders:
            contest_name = os.path.basename(f)
            contests.append((contest_name, FreeContest.load_free_contest(f)))
        CLog.info(f"Loaded {len(contests)} contest(s)!")
        return contests

    @staticmethod
    def load_free_contest(folder, save_to_folder=None, difficulty=3):
        contest_folders = {
            "statement": "",
            "solution": "",
            "testcase": "",
            "editorial": ""
        }
        contest_name = os.path.basename(folder)
        CLog.info(f"Loading contest `{contest_name}` in {folder}")
        folders = glob.glob(os.path.join(folder, "*"))
        for f in folders:
            fname = unidecode(os.path.basename(f).lower())
            print(fname)
            if "bai tap" in fname or "de bai" in fname:
                contest_folders['statement'] = f
            elif "test" in fname:
                contest_folders['testcase'] = f
            elif "bai giai" in fname:
                contest_folders['solution'] = f
            elif "loi giai" in fname:
                contest_folders['editorial'] = f
        # print(contest_folders)
        if not contest_folders['statement']:
            CLog.error(f"No statement folder found!")
            return None
        if not contest_folders['testcase']:
            CLog.error(f"No testcase folder found!")
            return None
        statement_files = findfiles("*.pdf", contest_folders['statement'])
        problem_codes = []
        for statement_file in statement_files:
            problem_name = os.path.basename(statement_file)
            problem_codes.append(problem_name[:problem_name.find(".")])
        print("problem_codes:", problem_codes)

        problems = []
        for problem_code in problem_codes:
            problem = FreeContest.load_problem(problem_code, contest_folders, contest_name, difficulty=difficulty)
            problems.append(problem)
            # print(problem_code, problem.name)
            if problem_code != problem.name:
                CLog.error(f"Please double check problem name: {problem_code}, {problem.name}")
                raise Exception(f"Please double check problem name: {problem_code}, {problem.name}")
        # TODO: test with checker
        CLog.info(f"Loading contest from folder: {folder}")
        CLog.info(f"{len(problems)} problem(s) found!")
        if save_to_folder:
            if not os.path.exists(save_to_folder) or not os.path.isdir(save_to_folder):
                CLog.error(f"Invalid output folder: {save_to_folder}")
            else:
                base_folder = os.path.join(save_to_folder, contest_name)
                for problem in problems:
                    ProblemService.save(problem, base_folder=base_folder, overwrite=True)
        return problems

    @staticmethod
    def load_problem(problem_code, contest_folders, contest_name, difficulty=3):
        problem = Problem()
        problem.name = problem.code = problem_code
        problem.difficulty = difficulty
        problem.src_name = "FreeContest"
        problem.src_url = contest_name
        statement_file = os.path.join(contest_folders['statement'], f"{problem_code}.md")
        if os.path.exists(statement_file):
            CLog.info(f"Found .md statement file at {statement_file}")
            ProblemService.parse_statement_file(statement_file, problem)
        else:
            statement_file = os.path.join(contest_folders['statement'], f"{problem_code}.pdf")
            problem.statement = statement_file
            problem.statement_format = "pdf"
            CLog.error(f".pdf statement file is not supported yet: {statement_file}")
            return None

        test_file = os.path.join(contest_folders['testcase'], f"{problem_code}.zip")
        if not os.path.exists(statement_file):
            CLog.error(f"Testcases not found for problem `{problem_code}` at: {test_file}")
            return None
        problem.testcases = TestcaseService.load_testcases(test_file, "cms")
        return problem


if __name__ == "__main__":
    free_contests = """Free Contest 35
Free Contest 36
Free Contest 37
Free Contest 38
Free Contest 39
Free Contest 40
Free Contest 41
Free Contest 42
Free Contest 44
Free Contest 45
Free Contest 46
Free Contest 47
Free Contest 48
Free Contest 49
Free Contest 51
Free Contest 52
Free Contest 53
Free Contest 54
Free Contest 55
Free Contest 56
Free Contest 57
Free Contest 58
Free Contest 59
Free Contest 60
Free Contest 61
Free Contest 62
Free Contest 63
Free Contest 64
Free Contest 65
Free Contest 80
Free contest 94
Free contest 95
Free contest 96
Free contest 97
Free contest 98
Free contest 99
Free contest 100
Free contest 101
Free contest 102
Free contest 103
Free contest 104
Free contest 105
Free contest 106
Free contest 107
Free contest 108
Free contest 109
Free contest 110
Free contest 111
Free contest 112
Free contest 113
Free contest 114
Free contest 115
Free contest 116
Free contest 117
Free contest 118
Free contest 119
Free contest 120
Free Contest 121"""

    beginner_contests = """Beginner Free Contest 01 (15-10-2018)
Beginner Free Contest 02 (14-11-2018)
Beginner Free Contest 03 (20-01-2019)
Beginner Free Contest 04 (31-01-2019)
Beginner Free Contest 05 (03-03-2019)
Beginner Free Contest 06 (17-04-2019)
Beginner Free Contest 07 (26-05-2019)
Beginner Free Contest 08 (12-06-2019)
Beginner Free Contest 10 (02-08-2019)
Beginner Free Contest 11 (01-09-2019)
Beginner Free Contest 12 (06-10-2019)
Beginner Free Contest 13 (30-10-2019)
Beginner Free Contest 14 (02-01-2020)
Beginner Free Contest 15 (12-01-2020)
Beginner Free Contest 16 (23-01-2020)
Beginner Free Contest 17 (25-04-2020)
Beginner Free Contest 18 (23-05-2020)
Beginner Free Contest 19 (16-06-2020)
Beginner Free Contest 20 (07-07-2020)
Beginner Free Contest 22 (15-08-2020)
Beginner Free Contest 23 (15-09-2020)
Beginner Free Contest 24 (20-10-2020)
Beginner Free Contest 25 (17-11-2020)
Beginner Free Contest 26 (22-12-2020)
Beginner Free Contest 27 (15-01-2021)
Beginner Free Contest 28 (27-03-2021)
Beginner Free Contest 29 (24-04-2021)"""
    # contest_folder = "D:\\projects\\freecontest\\beginner\\Beginner Free Contest 29 (24-04-2021)"
    out_folder = "D:\\projects\\freecontest\\beginner_formatted"
    # out_folder = "D:\\projects\\freecontest\\formatted"

    # contest_folder = "D:\\projects\\freecontest\\beginner\\Beginner Free Contest 27 (15-01-2021)"
    # out_folder = "D:\\projects\\freecontest\\formatted"
    # out_folder = None
    free_contests = "Free Contest 98"
    # free_contests = "Beginner Free Contest 27 (15-01-2021)"
    for folder in free_contests.split("\n"):
        # contest_folder = f"D:\\projects\\freecontest\\beginner\\{folder.strip()}"
        contest_folder = f"D:\\projects\\freecontest\\free_contest\\{folder.strip()}"
        # out_folder = "D:\\projects\\freecontest\\formatted"
        out_folder = "D:\\projects\\freecontest\\formatted"
        # out_folder = None
        problems = FreeContest.load_free_contest(contest_folder, save_to_folder=out_folder, difficulty=6)
    # for problem in problems:
    #     print(problem)
    print(f"Loaded {len(problems)} problems!")

    # all_contest_folder = "D:\\projects\\freecontest\\free_contest"
    # contests = FreeContest.load_all_free_contest(all_contest_folder)
    # for contest in contests:
    #     print(contest[0], len(contest[1]))


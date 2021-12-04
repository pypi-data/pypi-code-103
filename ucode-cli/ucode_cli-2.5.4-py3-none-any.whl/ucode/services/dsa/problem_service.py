import copy
import glob
import json
import os
import codecs
import re
from builtins import staticmethod
from shutil import copyfile
from typing import List, Tuple

from jinja2 import Template
from ruamel.yaml import YAML

from ucode.helpers.clog import CLog
from ucode.helpers.misc import make_problem_code, join_lines, findfiles
from ucode.models.problem import Problem, TestCase, ProblemFolderFormat
from ucode.services.common import find_section
from ucode.services.testcase.testcase_service import TestcaseService


def fix_section_title(name, pattern, lines, replace, once=True):
    found = False
    for i in range(len(lines)):
        if re.match(pattern, lines[i], re.I):
            lines[i] = re.sub(pattern, replace, lines[i])
            CLog.info(f'AUTOFIX: Fix {name} heading style: ' + lines[i])
            found = True
            if once:
                break
    if not found:
        CLog.warn(f'AUTOFIX: {name} is probably missing, don\'t know how to fix it.')


def check_section(name, pattern, lines, proper_line, unique=True, start_index=0, log_error=True):
    lines, content = find_section(pattern, lines, start_index)
    if log_error:
        flog = CLog.error
    else:
        flog = CLog.warn
    if not lines:
        flog(f'{name} is missing or invalid: {name} should has style: `{proper_line}`')
        return None, None
    if unique and len(lines) > 1:
        CLog.error(f'Only one {name} allowed!')

    empty = True
    for isection in content:
        for line in content[isection]:
            if line.strip() and not line.startswith('[//]:'):
                empty = False
    if empty:
        flog(f'{name} is empty!')

    return lines[0], content


def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


class ProblemService:
    @staticmethod
    def replace_image_urls(problem: Problem, from_url: str, to_url: str, replace_transaltions=True):
        from_texts = [f"({from_url})", f"'{from_url}'", f'"{from_url}"']
        to_texts = [f"({to_url})", f"'{to_url}'", f'"{to_url}"']
        for from_text, to_text in zip(from_texts, to_texts):
            problem.statement = problem.statement.replace(from_text, to_text)
            problem.input_format = problem.input_format.replace(from_text, to_text)
            problem.output_format = problem.output_format.replace(from_text, to_text)
            problem.constraints = problem.constraints.replace(from_text, to_text)
            for t in problem.testcases + problem.testcases_sample + problem.stock_testcases:
                if t.explanation:
                    t.explanation = t.explanation.replace(from_text, to_text)

        if problem.translations and replace_transaltions:
            for lang, tran in problem.translations.items():
                ProblemService.replace_image_urls(tran, from_url, to_url, False)

    @staticmethod
    def _get_problem_resource_files(problem_folder, problem: Problem):
        for f in os.listdir(problem_folder):
            for ext in ['.png', '.gif', '.jpg', '.svg', '.jpeg', '.bmp', ".tiff", '.webp']:
                if f.lower().endswith(ext):
                    problem.resource_files.append(os.path.join(problem_folder, f))
                    break
        if problem.resource_files:
            CLog.info(f"Detected resource files for problem `{problem_folder}`")
            print(problem.resource_files)

    @staticmethod
    def read_all_problems(base_folder, nested_folder=False,
                          load_testcase=False) -> List[Tuple[str, Problem]]:
        res = []
        problem_folders = [f.path for f in os.scandir(base_folder) if f.is_dir()]
        for problem_folder in sorted(problem_folders):
            if nested_folder:
                subfolders = [f.path for f in os.scandir(problem_folder) if f.is_dir()]
                for folder in sorted(subfolders):
                    print(problem_folder)
                    problem = ProblemService.load(os.path.join(problem_folder, folder), load_testcase=load_testcase)
                    res.append((os.path.join(problem_folder, folder), problem))
            else:
                print(problem_folder)
                problem = ProblemService.load(problem_folder, load_testcase=load_testcase)
                res.append((problem_folder, problem))
        return res

    @staticmethod
    def read_all_problems_v1(base_folder, nested_folder=0,
                             load_testcase=False, translations=[]) -> List[Tuple[str, Problem]]:
        res = []
        problem_folders = [f.path for f in os.scandir(base_folder) if f.is_dir()]
        for problem_folder in sorted(problem_folders):
            if nested_folder:
                for i in range(nested_folder):
                    subfolders = [f.path for f in os.scandir(problem_folder) if f.is_dir()]
                    for folder in sorted(subfolders):
                        print(problem_folder)
                        problem = ProblemService.load_v1(os.path.join(problem_folder, folder),
                                                         load_testcase=load_testcase,
                                                         translations=translations)
                        res.append((os.path.join(problem_folder, folder), problem))
            else:
                print(problem_folder)
                problem = ProblemService.load_v1(problem_folder, load_testcase=load_testcase, translations=translations)
                res.append((problem_folder, problem))
        return res

    @staticmethod
    def check_problem_v1(problem_folder, auto_fix=False):
        problem_code, statement_file = ProblemService.detect_problem_code_in_folder_v1(problem_folder)

        solution_file = os.path.join(problem_folder, f"{problem_code}.py")
        test_generator_file = os.path.join(problem_folder, f"{problem_code}_generator.py")
        testcase_file = os.path.join(problem_folder, f"testcases.txt")
        testcase_manual_file = os.path.join(problem_folder, f"testcases_manual.txt")

        if not os.path.isfile(solution_file):
            CLog.error(f"Solution file `{problem_code}.py` is missing!")
        if not os.path.isfile(test_generator_file):
            CLog.error(f"Testcase generator file `{problem_code}_generator.py` is missing!")
        if not os.path.isfile(testcase_file):
            CLog.error(f"Testcases file `testcases.txt` is missing!")
        else:
            file_size = os.stat(testcase_file).st_size
            if file_size > 50 * 1024 * 1024:
                CLog.error(f"Testcases file `testcases.txt` should not be > 50MB!")

        if not os.path.isfile(testcase_manual_file):
            CLog.warn(f"Manual testcases file `testcases_manual.txt` is missing!")

        with open(statement_file, encoding="utf-8") as fi:
            statement = fi.read()
            # print(statement)
            lines = statement.splitlines()

            if not lines[0].startswith('[//]: # ('):
                CLog.error('The first line should be the source of the problem, ex. `[//]: # (http://source.link)`')
                if auto_fix:
                    i = 0
                    while not lines[i].strip():
                        i += 1
                    lines = lines[i:]
                    if lines[0].startswith('[//]:'):
                        lines[0] = '[//]: # (%s)' % lines[0][5:].strip()
                        CLog.info("AUTOFIX: convert source info to: " + lines[0])
                    else:
                        CLog.warn("AUTOFIX: Source info may be missed. Don't know how to fix it.")
                        lines.insert(0, '[//]: # ()')

            title_line, statement = check_section('Title', '# \S*', lines, '# Problem Title (heading 1)')
            if auto_fix and not title_line:
                heading_line, content = find_section(f'#.*{problem_code}', lines)
                proper_title = (' '.join(problem_code.split('_'))).title()
                if not heading_line:
                    CLog.info('AUTOFIX: Problem title is probably missing, adding one...')
                    title1 = f'# {proper_title}'
                    title2 = f'[//]: # ({problem_code})'
                    lines.insert(1, '')
                    lines.insert(2, title1)
                    lines.insert(3, title2)
                    print(*lines[:4], sep='\n')
                else:  # has Title but wrong format
                    lines[heading_line[0]] = f'# {proper_title}'
                    if not lines[heading_line[0] + 1].startswith("[//]:"):
                        lines.insert(heading_line[0] + 1, f'[//]: # ({problem_code})')
                    CLog.info('AUTOFIX: Fix Title style and problem code')

            if title_line:
                title = lines[title_line]
                proper_title = (' '.join(title.split('_'))).title()
                if title != proper_title:
                    CLog.warn(f'Improper title: `{title}`, should be `{proper_title}`')
                # proper_problem_code = f'[//]: # ({problem_code})'
                if not lines[title_line + 1].startswith('[//]: # ('):
                    CLog.error(f'Title should be followed by proper problem code: `problem_code`')

                if lines[title_line + 3].startswith("[//]:") and lines[0] == '[//]: # ()':
                    CLog.warn('Detect source link in statement: %s' % lines[title_line + 3])
                    if auto_fix:
                        CLog.info('AUTOFIX: Detect source link in statement: %s, moving to first line'
                                  % lines[title_line + 3])
                        lines[0] = '[//]: # (%s)' % lines[title_line + 3][5:].strip()
                        lines.pop(title_line + 3)

            input_line, input = check_section('Input', '## Input\s*$', lines, '## Input')
            if input_line and title_line and input_line < title_line:
                CLog.error('Input should go after the Problem Statement.')

            if auto_fix and input_line is None:
                fix_section_title('Input', f'(#+\s*Input|Input\s*$)', lines, f'## Input')

            constraints_line, constraints = check_section('Constraints', '## Constraints\s*$',
                                                          lines, '## Constraints')
            if constraints_line and input_line and constraints_line < input_line:
                CLog.error('Constraints should go after the Input.')

            if auto_fix and constraints_line is None:
                fix_section_title('Constraints', f'(#+\s*Constraint.*|Constraints\s*$|#+\s*Giới hạn.*)', lines,
                                  f'## Constraints')

            output_line, output = check_section('Output', '## Output\s*$', lines, '## Output')
            # if output_line and constraints_line and output_line < constraints_line:
            #     CLog.error('Output should go after the Constraints.')

            if auto_fix and output_line is None:
                fix_section_title('Output', f'(#+\s*Output.*|Output\s*$|#+\s*Ouput.*|Ouput\s*$)', lines, f'## Output')

            tag_line, tag = check_section('Tags', '## Tags\s*$', lines, '## Tags')
            if tag_line and output_line and tag_line < output_line:
                CLog.error('Tags should go after the Output.')

            if auto_fix and tag_line is None:
                fix_section_title('Tags', f'#+\s*Tag.*', lines, f'## Tags')

            difficulty_line, difficulty = check_section('Difficulty', '## Difficulty\s*$', lines, '## Difficulty')
            if difficulty_line:
                try:
                    difficulty = float(difficulty[difficulty_line][0])
                    if difficulty < 1 or difficulty > 10:
                        CLog.error('Difficulty should be a number between 1 and 10, found: ' + str(difficulty))
                except ValueError:
                    CLog.error(
                        'Difficulty should be a number between 1 and 10, found: ' + difficulty[difficulty_line][0])

            if auto_fix and difficulty_line is None:
                fix_section_title('Difficulty', f'#+\s*Difficulty.*', lines, f'## Difficulty')

            list_lines, list_content = find_section('- .*', lines)
            for i in list_lines[::-1]:
                if i > 0:
                    prev_line = lines[i - 1]
                    if prev_line.strip() and not prev_line.startswith('- '):
                        CLog.error(f'There should be an empty line before the list, line {i}: {lines[i]}')
                        if auto_fix:
                            CLog.info('AUTOFIX: Added new line before list')
                            lines.insert(i, '')

            lines2, tmp = check_section('Sample input', '## Sample input', lines, '## Sample input 1', unique=False)
            if auto_fix and not lines2:
                fix_section_title('Sample Input', '#+\s*Sample input(.*)', lines, r'## Sample Input\1', once=False)

            lines2, tmp = check_section('Sample output', '## Sample output', lines, '## Sample output 1', unique=False)
            if auto_fix and not lines2:
                fix_section_title('Sample Output', '#+\s*Sample (ou|Ou|out|Out)put(.*)', lines, r'## Sample Output\2',
                                  once=False)

            lines2, tmp = check_section('Explanation', '## Explanation', lines, '## Explanation 1',
                                        unique=False, log_error=False)
            if auto_fix and not lines2:
                fix_section_title('Explanation', '#+\s*Explanation(.*)', lines, r'## Explanation\1', once=False)

            if auto_fix:
                statement_file_bak = os.path.join(problem_folder, f"{problem_code}_bak.md")
                i = 1
                while os.path.exists(statement_file_bak):
                    statement_file_bak = os.path.join(problem_folder, f"{problem_code}_bak{i}.md")
                    i += 1
                copyfile(statement_file, statement_file_bak)
                with open(statement_file, 'w', encoding="utf-8", newline='') as f:
                    f.write('\n'.join(lines))
        return problem_code

    @staticmethod
    def detect_problem_code_in_folder(problem_folder):
        problem_code = os.path.basename(problem_folder.rstrip(os.path.sep))

        metadata_file = os.path.join(problem_folder, f"metadata.yaml")
        if not os.path.exists(metadata_file):
            tran_files = glob.glob(os.path.join(problem_folder, f"{problem_code}_tran_*.md"))
            if tran_files:
                print("Detected translation file(s):", *tran_files, sep="\n")

            statement_file = os.path.join(problem_folder, f"{problem_code}.md")
            # stock_solution_file = os.path.join(problem_folder, f"{problem_code}.py")
            # stock_solution_file_cpp = os.path.join(problem_folder, f"{problem_code}.cpp")
            metadata_file = os.path.join(problem_folder, f"{problem_code}_meta.yaml")
            metadata_file_json = os.path.join(problem_folder, f"{problem_code}_meta.json")
            # test_generator_file = os.path.join(problem_folder, f"{problem_code}_generator.py")
            # test_generator_file_cpp = os.path.join(problem_folder, f"{problem_code}_generator.cpp")
            editorial_file = os.path.join(problem_folder, f"{problem_code}_editorial.md")
            testcase_file = os.path.join(problem_folder, f"{problem_code}_testcases.txt")
            testcase_sample_file = os.path.join(problem_folder, f"{problem_code}_testcases_sample.txt")
            tranlation_file = os.path.join(problem_folder, f"{problem_code}_tran_%s.md")
        else:
            statement_file = os.path.join(problem_folder, f"statement.md")
            # stock_solution_file = os.path.join(problem_folder, f"solution.py")
            # stock_solution_file_cpp = os.path.join(problem_folder, f"solution.cpp")
            # stock_solution_file_pas = os.path.join(problem_folder, f"solution.pas")
            metadata_file = os.path.join(problem_folder, f"metadata.yaml")
            metadata_file_json = os.path.join(problem_folder, f"metadata.json")
            # test_generator_file = os.path.join(problem_folder, f"input_generator.py")
            # test_generator_file_cpp = os.path.join(problem_folder, f"input_generator.cpp")
            # test_generator_file_pas = os.path.join(problem_folder, f"input_generator.pas")
            editorial_file = os.path.join(problem_folder, f"editorial.md")
            testcase_file = os.path.join(problem_folder, f"testcases.txt")
            testcase_sample_file = os.path.join(problem_folder, f"testcases_sample.txt")
            tranlation_file = os.path.join(problem_folder, f"statement_tran_%s.md")

        all_files = sorted(glob.glob(os.path.join(problem_folder, "*.*")))
        solution_files = []
        codestubs_files = []
        test_generator_files = []

        for file in all_files:
            filename, file_ext = os.path.splitext(file)
            if ("solution" in filename or filename.endswith(problem_code)) \
                and file_ext in [".py", ".pas", ".cpp"]:
                solution_files.append(file)
            elif "generator" in filename and file_ext in [".py", ".pas", ".cpp"]:
                test_generator_files.append(file)
            elif "codestub" in filename:
                codestubs_files.append(file)
        # solution_files = sorted(glob.glob(os.path.join(problem_folder,
        #                                                f"*solution*\.(pas$|py$|cpp$)")))
        # solution_files += sorted(glob.glob(os.path.join(problem_folder,
        #                                                 f"{problem_code}\.(pas$|py$|cpp$)")))
        # test_generator_files = sorted(glob.glob(os.path.join(problem_folder,
        #                                                      f"*input_generator*\.(pas$|py$|cpp$)")))
        # test_generator_files += sorted(glob.glob(os.path.join(problem_folder,
        #                                                       f"{problem_code}_generator*\.(pas$|py$|cpp$)")))

        problem_files = {
            "statement": statement_file,
            "translation": tranlation_file,
            "editorial": editorial_file,
            "metadata": metadata_file,
            "metadata_json": metadata_file_json,
            "testcases": testcase_file,
            "testcases_sample": testcase_sample_file,
            "test_generators": test_generator_files,
            "solutions": solution_files,
            "codestubs": codestubs_files
        }

        if not os.path.isfile(metadata_file) and not os.path.isfile(metadata_file_json):
            CLog.error(f"Metadata file `{problem_code}_meta.yaml`  or "
                       f"`{problem_code}_meta.json` is missing!")
            return None, None

        if os.path.isfile(metadata_file):
            with open(metadata_file, encoding="utf-8") as f:
                yaml = YAML(typ="safe")
                metadata = yaml.load(f)
        else:
            with open(metadata_file_json, encoding="utf-8") as f:
                metadata = json.load(f)

        if not metadata:
            CLog.error(f"Invalid metadata in `{problem_code}_meta.json` file")
        else:
            if not metadata.get("tags"):
                CLog.error(f"`tags` are missing in `{problem_code}_meta.json` file")
            if not metadata.get("difficulty"):
                CLog.error(f"`difficulty` is not specified in `{problem_code}_meta.json` file")
            if not metadata.get("statement_language"):
                CLog.error(f"`statement_language` is not specified in `{problem_code}_meta.json` file")

        if not metadata.get('code'):
            metadata['code'] = problem_code
        return metadata, problem_files

    @staticmethod
    def detect_problem_code_in_folder_v1(problem_folder):
        problem_code = os.path.basename(problem_folder.rstrip(os.path.sep))

        statement_file = os.path.join(problem_folder, f"{problem_code}.md")
        if not os.path.isfile(statement_file):
            statement_files = glob.glob(os.path.join(problem_folder, "*.md"))
            if len(statement_files) < 1:
                raise SyntaxError(f'Problem statement file `{problem_code}.md` is missing!')
            elif len(statement_files) == 1:
                statement_file = statement_files[0]
                problem_code = os.path.splitext(os.path.basename(statement_file))[0]
            else:
                other_files = [f for f in glob.glob(os.path.join(problem_folder, "*.md"))
                               if "_editorial.md" in f or "_tran_" in f
                               or ".vi." in f or "_bak.md" in f or "_bak1.md" in f or "_bak2.md" in f]
                if len(statement_files) - 1 != len(other_files):
                    raise SyntaxError('Problem folder contains multiple statement (.md) files, don\'t know what to do.')
                else:
                    t = set(statement_files) - set(other_files)
                    statement_file = list(t)[0]
                    problem_code = os.path.splitext(os.path.basename(statement_file))[0]
                    CLog.info(f'Auto detect problem code `{problem_code}` in  {statement_file}.md file')
        return problem_code, statement_file

    @staticmethod
    def check_problem(problem_folder):
        metadata, problem_files = ProblemService.detect_problem_code_in_folder(problem_folder)

        if not metadata:
            CLog.error("No metadata detected!")
            return None, None

        if not problem_files["solutions"]:
            CLog.warn(f"Solution file is missing!")
        if not problem_files['test_generators']:
            CLog.warn(f"Testcase input generator file is missing!")
        if not os.path.isfile(problem_files['editorial']):
            CLog.warn(f"Editorial file `{problem_files['editorial']}` is missing!")
        if metadata['testcase_format'] != ProblemFolderFormat.themis.value:
            if not os.path.isfile(problem_files['testcases']):
                CLog.error(f"Testcases file `{problem_files['testcases']}` is missing!")
            else:
                file_size = os.stat(problem_files['testcases']).st_size
                if file_size > 50 * 1024 * 1024:
                    CLog.error(f"Testcases file `{problem_files['testcases']}` should not be > 50MB!")

        if not os.path.isfile(problem_files['testcases_sample']):
            CLog.warn(f"Sample testcases file `{problem_files['testcases_sample']}` is missing!")

        with open(problem_files['statement'], encoding="utf-8") as fi:
            statement = fi.read()
            lines = statement.splitlines()

            title_line, statement = check_section('Title', '# \S*', lines, '# Problem Title (heading 1)')

            if title_line:
                title = lines[title_line]
                proper_title = (' '.join(title.split('_'))).title()
                if title != proper_title:
                    CLog.warn(f'Improper title: `{title}`, should be `{proper_title}`')

            input_line, input = check_section('Input', '## Input\s*$', lines, '## Input')
            if input_line and title_line and input_line < title_line:
                CLog.error('Input should go after the Problem Statement.')

            constraints_line, constraints = check_section('Constraints', '## Constraints\s*$',
                                                          lines, '## Constraints')
            if constraints_line and input_line and constraints_line < input_line:
                CLog.error('Constraints should go after the Input.')

            output_line, output = check_section('Output', '## Output\s*$', lines, '## Output')
            # if output_line and constraints_line and output_line < constraints_line:
            #     CLog.error('Output should go after the Constraints.')

            if output_line is None:
                CLog.error('Missing output description')

            list_lines, list_content = find_section('- .*', lines)
            for i in list_lines[::-1]:
                if i > 0:
                    prev_line = lines[i - 1]
                    if prev_line.strip() and not prev_line.startswith('- '):
                        CLog.error(f'There should be an empty line before the list, line {i}: {lines[i]}')

            check_section('Sample input', '## Sample input', lines, '## Sample input 1', unique=False)

            check_section('Sample output', '## Sample output', lines, '## Sample output 1', unique=False)

            check_section('Explanation', '## Explanation', lines, '## Explanation 1', unique=False, log_error=False)

        CLog.important("Checking done")
        return metadata, problem_files

    @staticmethod
    def _check_folder(base_folder, problem_folder, overwrite=False):
        abs_folder = os.path.join(base_folder, problem_folder)

        if os.path.exists(abs_folder):
            if not overwrite:
                CLog.error('Problem folder existed! Delete the folder or use `overwrite` instead.')
                return None
            else:
                CLog.warn('Problem folder existed! Content will be overwritten.')

        if not os.path.exists(abs_folder):
            os.makedirs(abs_folder)

        return abs_folder

    @staticmethod
    def create_problem(folder, problem_name, problem_code=None, lang="vi", translations=[], overwrite=False,
                       tags=[], difficulty=0.0, programming_language='py', gen_sample=False, testcase_format='ucode'):
        problem = Problem()
        if testcase_format:
            problem.testcase_format = testcase_format
        problem.name = problem_name
        if not problem_code:
            problem_code = problem.name
        problem_code = make_problem_code(problem_code)

        problem.code = problem_code
        problem.difficulty = difficulty
        problem.tags = tags

        template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')

        prefix_path = ""
        if gen_sample:
            prefix_path = "sample/"

        with open(os.path.join(template_path, f'{prefix_path}editorial.md'),
                  encoding="utf-8") as f:
            problem.editorial = Template(f.read()).render(problem=problem)

        ProblemService.parse_statement_file(os.path.join(template_path, f"{prefix_path}statement.md"), problem)
        problem.name = problem_name
        problem.code = problem_code

        if not gen_sample:
            problem.testcases_sample = []

        with open(os.path.join(template_path, f'solution.{programming_language}.j2'),
                  encoding="utf-8") as f:
            content = Template(f.read()).render(problem_code=problem_code)
            problem.solution = content
            problem.solution_lang = programming_language
            # problem.solutions.append({"lang": programming_language, "code": content})

        with open(os.path.join(template_path, f'generator.{programming_language}.j2'),
                  encoding="utf-8") as f:
            content = Template(f.read()).render(problem_code=problem_code)
            problem.testcase_generators = [{"lang": programming_language, "code": content}]

        for t in translations:
            problem.translations[t] = Problem(name=problem_name)

        ProblemService.save(problem, folder, overwrite=overwrite, lang=lang)

        CLog.important(f'Problem created at `{folder}`')

    @staticmethod
    def parse_statement_file(statement_file, problem: Problem):
        with open(statement_file, encoding="utf-8") as fi:
            statement = fi.read()
            lines = statement.splitlines()
            lines.append("")
            lines.append("")
            lines.append("")

            statement_i, statement_c = find_section('#\s+.*', lines)
            if statement_i:
                title = lines[statement_i[0]][1:].strip()
                problem.name = title

                s = lines[statement_i[0] + 1].strip()
                if not s.strip():
                    s = lines[statement_i[0] + 2]

            if statement_i:
                problem.statement = join_lines(statement_c[statement_i[0]])

            input_i, input_c = find_section('(#+\s*Input|Input\s*$)', lines)
            if input_i:
                problem.input_format = join_lines(input_c[input_i[0]])

            output_i, output_c = find_section('(#+\s*Output.*|Output\s*$|#+\s*Ouput.*|Ouput\s*$)', lines)
            if output_i:
                problem.output_format = join_lines(output_c[output_i[0]])

            constraints_i, constraints_c = find_section('(#+\s*Constraint.*|Constraints\s*$|#+\s*Giới hạn.*)', lines)
            if constraints_i:
                problem.constraints = join_lines(constraints_c[constraints_i[0]])

            subtasks_i, subtasks_c = find_section('(#+\s*Subtasks.*|Subtask\s*$|#+\s*Sub tasks.*)', lines)
            if subtasks_i:
                problem.constraints += "\n\nSubtasks:\n\n" + join_lines(subtasks_c[subtasks_i[0]])

            sample_input_i, sample_input_c = find_section('#+\s*Sample input(.*)', lines)
            sample_output_i, sample_output_c = find_section('#+\s*Sample (ou|Ou|out|Out)put(.*)', lines)
            explanation_i, explanation_c = find_section('#+\s*Explanation(.*)', lines)
            if sample_input_i:
                for i in range(len(sample_input_i)):
                    testcase = TestCase()
                    _input = join_lines(sample_input_c[sample_input_i[i]]).strip('`').lstrip("\n").rstrip()
                    # print(f"**** i `{_input}`")
                    _output = join_lines(sample_output_c[sample_output_i[i]]).strip('`').lstrip("\n").rstrip()
                    # print(f"**** o `{_output}`")
                    testcase.input = _input
                    testcase.output = _output
                    if len(explanation_i) > i:
                        testcase.explanation = join_lines(explanation_c[explanation_i[i]]).strip('`').strip()

                    problem.testcases_sample.append(testcase)

    @staticmethod
    def _parse_statement_file_v1(statement_file, problem: Problem):
        with open(statement_file, encoding="utf-8") as fi:
            statement = fi.read()
            lines = statement.splitlines()

            source_link = None
            s = lines[0]
            if not s.strip():
                s = lines[1]
            if s.startswith('[//]:'):
                o = s.find('(')
                if o:
                    source_link = s[o + 1:s.find(')')].strip()
                else:
                    source_link = s[5:].strip()
            problem.src_url = source_link

            statement_i, statement_c = find_section('#\s+.*', lines)
            if statement_i:
                title = lines[statement_i[0]][1:].strip()
                problem.name = title

                s = lines[statement_i[0] + 1].strip()
                if not s.strip() and statement_i[0] < len(lines)-2:
                    s = lines[statement_i[0] + 2]
                if s.startswith('[//]:'):
                    problem.preview = s
                    o = s.find('(')
                    if o:
                        code = s[o + 1:s.find(')')].strip()
                    else:
                        code = s[5:].strip()
                    problem.code = code
                    problem.slug = problem.code.replace('_', '-')

            if statement_i:
                problem.statement = join_lines(statement_c[statement_i[0]])

            input_i, input_c = find_section('(#+\s*Input|Input\s*$)', lines)
            if input_i:
                problem.input_format = join_lines(input_c[input_i[0]])

            output_i, output_c = find_section('(#+\s*Output.*|Output\s*$|#+\s*Ouput.*|Ouput\s*$)', lines)
            if output_i:
                problem.output_format = join_lines(output_c[output_i[0]])

            constraints_i, constraints_c = find_section('(#+\s*Constraint.*|Constraints\s*$|#+\s*Giới hạn.*)', lines)
            if constraints_i:
                problem.constraints = join_lines(constraints_c[constraints_i[0]])

            tags_i, tags_c = find_section('#+\s*Tag.*', lines)
            if tags_i:
                tags = []
                for t in tags_c[tags_i[0]]:
                    t = t.strip()
                    if t:
                        if t.startswith('-'):
                            tags.append(t[1:].strip())
                        else:
                            tags.append(t)
                problem.tags = problem.topics = tags

            difficulty_i, difficulty_c = find_section('#+\s*Difficulty.*', lines)
            if difficulty_i:
                try:
                    problem.difficulty = float(difficulty_c[difficulty_i[0]][0])
                except ValueError:
                    CLog.warn(f"Difficulty is not parsable: {difficulty_c[difficulty_i[0]][0]}")

            sample_input_i, sample_input_c = find_section('#+\s*Sample input(.*)', lines)
            sample_output_i, sample_output_c = find_section('#+\s*Sample (ou|Ou|out|Out)put(.*)', lines)
            explanation_i, explanation_c = find_section('#+\s*Explanation(.*)', lines)
            if sample_input_i:
                for i in range(len(sample_input_i)):
                    testcase = TestCase()
                    testcase.input = join_lines(sample_input_c[sample_input_i[i]]).strip('`').strip()
                    testcase.output = join_lines(sample_output_c[sample_output_i[i]]).strip('`').strip()
                    if len(explanation_i) > i:
                        testcase.explanation = join_lines(explanation_c[explanation_i[i]]).strip('`').strip()

                    problem.testcases_sample.append(testcase)

    @staticmethod
    def load(problem_folder, load_testcase=False, load_testcases_only=False,
             force_testcase_format=None):
        problem = Problem()
        meta, problem_files = ProblemService.check_problem(problem_folder)
        if not meta:
            CLog.error("No problem's metadata found!")
            return Problem()

        problem.code = meta['code']
        if not load_testcases_only:
            # problem_code, meta, problem_files = ProblemService.check_problem(problem_folder)
            print("Problem metadata:", json.dumps(meta))
            # problem.preview = f'[//]: # ({problem_code})'

            if meta.get("code"):
                problem.code = meta.get("code")
            if meta.get("slug"):
                problem.slug = meta.get("slug")
            else:
                problem.slug = make_problem_code(problem.code)
            if meta.get("tags"):
                problem.tags = meta.get("tags")
            if meta.get("difficulty"):
                problem.difficulty = meta.get("difficulty")
            if meta.get("experience_gain"):
                problem.xp = meta.get("experience_gain")
            if meta.get("statement_format"):
                problem.statement_format = meta.get("statement_format")
            if meta.get("statement_language"):
                problem.statement_language = meta.get("statement_language")
            if meta.get("limit_time_ms"):
                problem.limit_time = meta.get("limit_time_ms")
            if meta.get("limit_memory_mb"):
                problem.limit_memory = meta.get("limit_memory_mb")
            if meta.get("testcase_format"):
                problem.testcase_format = meta.get("testcase_format")
            if meta.get("src_name"):
                problem.src_name = meta.get("src_name")
            if meta.get("src_id"):
                problem.src_id = meta.get("src_id")
            if meta.get("src_url"):
                problem.src_url = meta.get("src_url")

            print("src", problem.src_url)

            if os.path.exists(problem_files["editorial"]):
                editorial_prob = Problem()
                ProblemService.parse_statement_file(problem_files["editorial"], editorial_prob)
                if editorial_prob.statement.strip():
                    problem.editorial = editorial_prob.statement

            ProblemService._get_problem_resource_files(problem_folder, problem)

            ProblemService.parse_statement_file(problem_files["statement"], problem)
            if meta.get("statement_translations"):
                for lang in meta["statement_translations"]:
                    lang_statement_file = os.path.join(problem_folder, problem_files['translation'] % lang)
                    if not os.path.exists(lang_statement_file):
                        CLog.warn(f"Translation file not existed: {lang_statement_file}")
                    else:
                        tran_problem = copy.copy(problem)
                        ProblemService.parse_statement_file(lang_statement_file, tran_problem)
                        problem.translations[lang] = tran_problem

            # if os.path.exists(problem_files['stock_solution']):
            #     with open(problem_files['stock_solution'], encoding="utf-8") as fi:
            #         problem.solution = fi.read()
            # elif os.path.exists(problem_files['stock_solution_cpp']):
            #     with open(problem_files['stock_solution_cpp'], encoding="utf-8") as fi:
            #         problem.solution = fi.read()
            #

            if problem_files['solutions']:
                for file_path in problem_files['solutions']:
                    idx = file_path.rfind(".")
                    with open(file_path, encoding="utf-8") as f:
                        problem.solutions.append({"lang": file_path[idx + 1:],
                                                  "code": f.read()})
                if problem.solutions:
                    problem.solution = problem.solutions[0]["code"]
                    problem.solution_lang = problem.solutions[0]["lang"]
                # print(*problem.solutions, sep="\n")

            if problem_files['codestubs']:
                for file_path in problem_files['codestubs']:
                    idx = file_path.rfind(".")
                    with open(file_path, encoding="utf-8") as f:
                        problem.code_stubs[file_path[idx + 1:]] = f.read()

            problem.testcase_generators = []
            if problem_files['test_generators']:
                for file_path in problem_files['test_generators']:
                    if os.path.exists(file_path):
                        idx = file_path.rfind(".")
                        with open(file_path, encoding="utf-8") as f:
                            problem.testcase_generators.append({"lang": file_path[idx + 1:], "code": f.read()})
                    # print(problem.testcase_generator)

        if load_testcase:
            testcase_format = problem.testcase_format
            if force_testcase_format:
                testcase_format = force_testcase_format
            ProblemService.load_testcases(problem_folder, testcase_format, problem)
            if not problem.testcases:
                problem.testcases = []
            print(f"Loaded {len(problem.testcases)} testcases")

        if not problem.testcases_sample and problem.testcases:
            # problem.testcases_sample = problem.testcases[:2]
            for i in range(min(2, len(problem.testcases))):
                problem.testcases[i].sample = True

        return problem

    @staticmethod
    def load_v1(problem_folder, load_testcase=False, translations=[]):
        """

        :param problem_folder:
        :param load_testcase:
        :param translations: ['vi']
        :return:
        """
        problem_code = ProblemService.check_problem_v1(problem_folder)
        statement_file = os.path.join(problem_folder, f"{problem_code}.md")
        editorial_file = os.path.join(problem_folder, f"{problem_code}_editorial.md")

        problem = Problem()
        problem.slug = make_problem_code(problem_code)
        problem.code = problem_code
        problem.preview = f'[//]: # ({problem_code})'

        if os.path.exists(editorial_file):
            editorial_prob = Problem()
            ProblemService._parse_statement_file_v1(editorial_file, editorial_prob)
            if editorial_prob.statement.strip():
                problem.editorial = editorial_prob.statement
            else:
                with open(editorial_file, encoding="utf-8") as fi:
                    problem.editorial = fi.read()

        ProblemService._get_problem_resource_files(problem_folder, problem)
        ProblemService._parse_statement_file_v1(statement_file, problem)
        if translations:
            for lang in translations:
                lang_statement_file = os.path.join(problem_folder, f"{problem_code}.{lang}.md")
                if not os.path.exists(lang_statement_file):
                    CLog.warn(f"Translation file not existed: {lang_statement_file}")
                else:
                    tran_problem = copy.copy(problem)
                    ProblemService._parse_statement_file_v1(lang_statement_file, tran_problem)
                    problem.translations[lang] = tran_problem

        solution_file = os.path.join(problem_folder, f"{problem_code}.py")
        if os.path.isfile(solution_file):
            with open(solution_file, encoding="utf-8") as f:
                problem.solution = f.read()

        additional_solution_files = glob.glob(os.path.join(problem_folder, f"solution.*"))
        for file_path in additional_solution_files:
            sub_path = os.path.join(problem_folder, "solution")
            idx = file_path.find(sub_path) + len(sub_path)
            with open(file_path, encoding="utf-8") as f:
                problem.solutions.append({"lang": file_path[idx + 1:],
                                          "code": f.read()})
        # print(*problem.solutions, sep="\n")

        testcase_generators = glob.glob(os.path.join(problem_folder, f"{problem_code}_generator.*"))
        if testcase_generators:
            file_path = testcase_generators[0]
            if os.path.exists(file_path):
                idx = file_path.rfind(".")
                with open(file_path, encoding="utf-8") as f:
                    problem.testcase_generator = {"lang": file_path[idx + 1:], "code": f.read()}
            # print(problem.testcase_generator)

        problem.testcases = []
        if load_testcase:
            file_names = ["testcases_manual_stock.txt", "testcases_manual.txt", "testcases_stock.txt", "testcases.txt"]
            file_names.append(problem_code + "_testcases.txt")
            input_set = set()
            for file_name in file_names:
                testcase_file = os.path.abspath(os.path.join(problem_folder, file_name))

                if not os.path.exists(testcase_file):
                    CLog.warn(f'`{testcase_file}` file not existed, skipping...')
                else:
                    CLog.info(f'`{testcase_file}` file FOUND, reading testcases...')
                    tests = TestcaseService.load_testcases(testcase_file)
                    # print(f"reading testcases in file {testcase_file}: {len(tests)}")
                    for t in tests:
                        _input, _output = t.input, t.output
                        # print(f"Input: {input}, output: {output}")
                        if _input not in input_set:
                            problem.testcases.append(TestCase(input=_input, output=_output))
                        if "manual_stock" in file_name:
                            problem.testcases_sample.append(TestCase(input=_input, output=_output))
                        input_set.add(_input)
                        # print(input_set)
            print(f"Loaded {len(problem.testcases)} testcases")

        if not problem.testcases_sample and problem.testcases:
            problem.testcases_sample = problem.testcases[:2]

        return problem

    @staticmethod
    def convert(problem_folder: str, _from: ProblemFolderFormat, _to: ProblemFolderFormat,
                output: str=None, overwrite: bool = False, convert_testcases_only=False):
        if _to != ProblemFolderFormat.ucode:
            CLog.error("Current support converting to 'ucode' format only")
            return
        problem_folder = str(os.path.abspath(problem_folder))

        problem = ProblemService.load(problem_folder, load_testcase=True,
                                      load_testcases_only=convert_testcases_only,
                                      force_testcase_format=_from)

        print(problem.name, problem.code)

        if not output:
            output = problem_folder

        CLog.info(f"Converting `{problem_folder}` to `{output}`")

        base_folder = os.path.dirname(output)
        new_problem_folder = os.path.basename(output)
        ProblemService.save(problem, base_folder=base_folder, problem_folder=new_problem_folder,
                            overwrite=overwrite, save_testcases_only=convert_testcases_only)

    @staticmethod
    def save(problem: Problem, base_folder=".", problem_folder=None, problem_code=None,
             overwrite=False, lang=None, save_testcases=True, save_testcases_only=False, testcase_format="ucode"):
        """
        :param problem:
        :param problem_code: name of problem folder
        :param base_folder: the parent folder that will contain the problem folder
        :return:
        """
        template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')

        if not problem_code:
            problem_code = problem.code

        if not problem_code:
            problem_code = problem.name

        problem_code = make_problem_code(problem_code)

        problem.code = problem_code
        if not problem_folder:
            problem_folder = problem_code
        problem_folder = ProblemService._check_folder(base_folder, problem_folder, overwrite)
        if not problem_folder:
            return

        if testcase_format:
            problem.testcase_format = testcase_format

        if not save_testcases_only:
            if not problem.name:
                problem.name = (' '.join(problem_code.split('_'))).title()

            if lang:
                problem.statement_language = lang
            print("src", problem.src_url)

            # problem.testcase_format = "ucode"

            meta_dict = {
              "code": problem.code,
              "slug": problem.slug,
              "tags": problem.tags,
              "difficulty": problem.difficulty,
              "experience_gain": problem.xp,
              "statement_format": problem.statement_format,
              "statement_language": problem.statement_language,
              "statement_translations": list(problem.translations.keys()),
              "limit_time_ms": problem.limit_time,
              "limit_memory_mb": problem.limit_memory,
              "testcase_format": problem.testcase_format,
              "src_name": problem.src_name,
              "src_id": problem.src_id,
              "src_url": problem.src_url
            }

            # with codecs.open(problem_folder + ("/%s_meta.json" % problem_code), "w", encoding="utf-8") as f:
            #     json.dump(meta_dict, f, indent=2)

            with codecs.open(os.path.join(problem_folder, "metadata.yaml"), "w", encoding="utf-8") as f:
                yaml = YAML()
                yaml.indent(offset=2)
                yaml.dump(meta_dict, f)

            with open(os.path.join(template_path, 'statement.md.j2'), encoding="utf-8") as file_:
                for i, test in enumerate(problem.testcases_sample):
                    test.name = str(i+1)
                template = Template(file_.read())
                statement = template.render(problem=problem)
                f = codecs.open(os.path.join(problem_folder, "statement.md"), "w", encoding="utf-8")
                f.write(statement)
                f.close()

            for lang, prob_tran in problem.translations.items():
                with open(os.path.join(template_path, 'statement.md.j2')) as file_:
                    template = Template(file_.read())
                    statement = template.render(problem=prob_tran)
                    f = codecs.open(os.path.join(problem_folder, f"statement_tran_{lang}.md"), "w", encoding="utf-8")
                    f.write(statement)
                    f.close()

            with open(os.path.join(template_path, 'editorial.md.j2'), encoding="utf-8") as file_:
                template = Template(file_.read())
                if not problem.editorial:
                    problem.editorial = ""
                statement = template.render(problem=problem)
                f = codecs.open(os.path.join(problem_folder, "editorial.md"), "w", encoding="utf-8")
                f.write(statement)
                f.close()

            # if not problem.solution:
            #     with open(os.path.join(template_path, f'solution.{problem.main_solution_language}.j2'),
            #               encoding="utf-8") as file_:
            #         template = Template(file_.read())
            #         content = template.render(problem_code=problem_code,
            #                                   solution=problem.solution if problem.solution else "pass")
            #         f = open(os.path.join(problem_folder, f"solution.{problem.main_solution_language}"),
            #                  'w', encoding="utf-8", newline='')
            #         f.write(content)
            #         f.close()
            # else:
            #     f = open(os.path.join(problem_folder, "solution.py"), 'w', encoding="utf-8", newline='')
            #     f.write(problem.solution)
            #     f.close()

            if problem.testcase_generators:
                for testcase_generator in problem.testcase_generators:
                    f = open(os.path.join(problem_folder, f"input_generator.{testcase_generator['lang']}"),
                             'w', encoding="utf-8", newline='')
                    f.write(testcase_generator["code"])
                    f.close()

            solution_files = set()
            solution_codes = set()
            if problem.solution:
                solution_file = f"solution.{problem.solution_lang}"
                solution_files.add(solution_file)
                f = open(os.path.join(problem_folder, solution_file), 'w',
                         encoding="utf-8", newline='')
                f.write(problem.solution)
                solution_codes.add(problem.solution)
                f.close()

            if problem.solutions:
                for solution in problem.solutions:
                    solution_file = f"solution.{solution['lang']}"
                    i = 1
                    while solution_file in solution_files:
                        solution_file = f"solution{i}.{solution['lang']}"
                        i += 1
                    solution_files.add(solution_file)

                    if solution["code"] in solution_codes:
                        continue

                    solution_codes.add(solution["code"])
                    f = open(os.path.join(problem_folder, solution_file), 'w',
                             encoding="utf-8", newline='')
                    f.write(solution["code"])
                    f.close()

            if problem.code_stubs:
                for lang, code in problem.code_stubs.items():
                    stub_file = f"codestub.{lang}"
                    f = open(os.path.join(problem_folder, stub_file), 'w',
                             encoding="utf-8", newline='')
                    f.write(code)
                    f.close()

        if save_testcases:
            if not testcase_format:
                testcase_format = problem.testcase_format
            from ucode.services.testcase.testcase_service import TestcaseService
            TestcaseService.save_testcases(problem_folder, problem, format=testcase_format)
            # if save_testcases_only:
            #     CLog.warn("DON'T FORGET to change the 'testcase_format' to 'ucode' in meta data file.")

        problem_folder = os.path.abspath(problem_folder)

        # copy resource files
        if problem.resource_files:
            CLog.info(f"Problem resource files found, copying...")
            # print(problem.resource_files)
            for f in problem.resource_files:
                file_name = os.path.basename(f)
                new_file = os.path.join(problem_folder, file_name)
                copyfile(f, new_file)
                CLog.info(f"File `{f}` was copied to {new_file}")

        CLog.important(f'Problem created at `{problem_folder}`')
        return problem_folder

    @staticmethod
    def load_testcases(problem_folder, format: str, problem: Problem):
        CLog.info(f"Loading testcases with specified format {format} from {problem_folder}")
        if format == ProblemFolderFormat.ucode.value:
            ProblemService.load_ucode_testcases(problem_folder, problem)
        elif format == ProblemFolderFormat.themis.value:
            ProblemService.load_themis_testcases(problem_folder, problem)
        elif format == ProblemFolderFormat.cms.value:
            ProblemService.load_cms_testcases(problem_folder, problem)
        else:
            CLog.error(f"Unknown testcase format {format}")

    @staticmethod
    def load_ucode_testcases(problem_folder, problem: Problem):
        problem.testcases = []

        file_names = glob.glob(os.path.join(problem_folder, "*testcases*.txt"))
        # file_names = ["testcases_sample_stock.txt", "testcases_sample.txt", "testcases_stock.txt", "testcases.txt"]
        input_set = set()
        for file_name in file_names:
            testcase_file = os.path.abspath(file_name)
            if not os.path.exists(testcase_file) or not os.path.isfile(testcase_file):
                CLog.info(f'`{testcase_file}` file not existed, skipping...')
            else:
                tests = TestcaseService.load_testcases(testcase_file)
                print(f"reading testcases in file {testcase_file}: {len(tests)}")
                for t in tests:
                    _input, _output, _name = t.input, t.output, t.name
                    # print(f"Input: {input}, output: {output}")
                    if "_sample" in file_name:
                        if _input not in [t.input for t in problem.testcases_sample]:
                            problem.testcases_sample.append(TestCase(input=_input, output=_output, name=_name))
                    elif "_stock" in file_name:
                        problem.stock_testcases.append(TestCase(input=_input, output=_output, name=_name))
                    else:
                        if _input not in input_set:
                            problem.testcases.append(TestCase(input=_input, output=_output, name=_name))
                    input_set.add(_input)
                    # print(input_set)

    @staticmethod
    def load_themis_testcases(problem_folder, problem: Problem):
        # uu tien load file testcases.zip truoc
        testcase_zip = os.path.join(problem_folder, "testcases.zip")
        if os.path.exists(testcase_zip):
            CLog.info(f"Found testcases.zip file: {testcase_zip}")
            problem.testcases = TestcaseService.load_testcases(testcase_zip)
        else:
            # uu tien file .zip neu co 1 file ton tai
            testcase_zips = glob.glob(os.path.join(problem_folder, "*.zip"))
            if len(testcase_zips) == 1:
                testcase_zip = testcase_zips[0]
                CLog.info(f"Found testcases.zip file: {testcase_zip}")
                problem.testcases = TestcaseService.load_testcases(testcase_zip)
            else:
                problem.testcases = TestcaseService.load_testcases(problem_folder)

    @staticmethod
    def load_cms_testcases(problem_folder, problem: Problem):
        problem.testcases = TestcaseService.load_testcases(os.path.join(problem_folder, "testcases.zip"))

    @staticmethod
    def join_testcases(problem: Problem):
        testcases: List[TestCase] = []
        testcases.extend(problem.stock_testcases_sample)
        testcases.extend(problem.testcases_sample)
        for t in testcases:
            t.sample = True
        testcases.extend(problem.stock_testcases)
        testcases.extend(problem.testcases)

        return testcases

    @staticmethod
    def split_testcases_input(problem: Problem):
        """
        split all input number in data into separated lines, useful for primary problem (Scratch, python input)
        @param problem:
        @return:
        """
        for testcase in problem.testcases:
            testcase.input = ProblemService.split_numbers(testcase.input)
        for testcase in problem.testcases_sample:
            testcase.input = ProblemService.split_numbers(testcase.input)
        for testcase in problem.stock_testcases:
            testcase.input = ProblemService.split_numbers(testcase.input)
        for testcase in problem.stock_testcases_sample:
            testcase.input = ProblemService.split_numbers(testcase.input)

    @staticmethod
    def split_numbers(input_data):
        new_input = []
        for line in input_data.splitlines():
            tokens = line.split()
            need_split = True
            for t in tokens:
                if not is_float(t):
                    need_split = False
                    break
            if need_split:
                new_input.extend(tokens)
            else:
                new_input.append(line)
        return "\n".join(new_input)


def convert_all_v1_to_new_format(src_folder, dest_folder=None, translations=[]):
    # problems = ProblemService.read_all_problems_v1(src_folder)
    problems = ProblemService.read_all_problems_v1(src_folder, load_testcase=True, translations=translations)

    if not dest_folder:
        dest_folder = src_folder + "_new"

    for folder, problem in problems:
        print(folder)
        base, folder_name = os.path.split(folder)
        ProblemService.save(problem, dest_folder, problem_folder=folder_name, overwrite=True)
        print(problem.name)
        print(problem.testcase_format)
        print(len(problem.testcases))
        print(len(problem.testcases_sample))


def change_testcases():
    base_folder = "D:\\projects\\ucode\\basic_problems\\hour-of-code-round2\\p22_bicycle_race"
    problem = ProblemService.load(base_folder, load_testcase=True)
    print(len(problem.testcases))
    new_testcases = []
    import random
    for testcase in random.choices(problem.testcases, k=8):
        new_input=[]
        for line in testcase.input.split():
            new_input.extend(line.split())
        new_test: TestCase = TestCase(input="\n".join(new_input), output=testcase.output)
        new_testcases.append(new_test)
    print(len(new_testcases))
    problem.testcases = new_testcases
    ProblemService.save(problem, base_folder + "_new")


if __name__ == "__main__":
    # change_testcases()
    # base_folder = "D:\\projects\\ucode\\dsa-problems\\competitions\\hsg_thcs\\Thuc\\HaNoi2019"
    # base_folder = "D:\\projects\\ucode\\basic_problems\\hour-of-code-round2\\old"
    # base_folder = "D:\\projects\\ucode\\basic_problems\\hour-of-code-round3\\_old"
    # base_folder = "D:\\projects\\ucode\\dsa-thematic-problems\\competitive_programing_topics\\maths\\fundamentals\\gcd_lcm_new\\number_game"
    # ProblemService.convert(base_folder, ProblemFolderFormat.themis, ProblemFolderFormat.ucode,
    #                        convert_testcases_only=True, overwrite=True)
    # base_folder = r"D:\projects\ucode\weekly-algorithm-problems\competitions\teko-hcm\old"
    # convert_all_v1_to_new_format(base_folder)

    # problem = ProblemService.load(r"D:\projects\ucode\ucode-cli\problems\_save\quadrant_1")
    # print(problem.code_stubs)

    input_data = """6
5 2 3
100 1 4.2
1 10 5s
1000000000 1 6
1 1 1000000000
1 1 999999999"""
    print(ProblemService.split_numbers(input_data))

    # DsaProblem.create_problem('../../problems', 'Counting Sort 3', lang="en",
    #                           translations=['vi', 'ru'],
    #                           overwrite=True,
    #                           tags=['math', '800'],
    #                           difficulty=2.5)

    # problem = DsaProblem.load_v1('/home/thuc/projects/ucode/weekly-algorithm-problems/week03/p01_elephant',
    #                       translations=['vi'], load_testcase=True)
    # problem = DsaProblem.load_v1('/home/thuc/projects/ucode/weekly-algorithm-problems/week03/p02_key_races',
    #                       translations=['vi'], load_testcase=True)

    # folder = "../../../problems/p3_delrow"
    # folder = "D:\\projects\\ucode\\dsa-thematic-problems\\de_thi_hsg\\quan_ba_dinh_2020_2021_thcs\\cable"
    # # problem = ProblemService.load(folder, load_testcase=True)
    # problem = ProblemService.load(folder, load_testcase=True)
    # # ProblemService.save(problem, "D:\\projects\\ucode\\_problem_dev", problem_folder="big_mod_py_", overwrite=True)
    # print(json.dumps(problem.solutions))
    # print(problem.name)
    # print("Input:")
    # print(problem.input_format)
    # print("Constraints:")
    # print(problem.constraints)
    # print("Output:")
    # print(problem.output_format)
    # print("Statement:")
    # print(problem.statement)
    #
    # ProblemService.save(problem, base_folder="../../../problems/", problem_folder="_save", overwrite=True)
    # print(problem.testcase_format)
    # print(len(problem.testcases))
    # print(len(problem.stock_testcases))
    # print(len(problem.testcases_sample))
    # print("Name:", problem.testcases[0].name)
    # ProblemService.save(problem, '../../../problems',
    #                     problem_folder='another_one_bites_the_dust2', overwrite=True)
    # print(problem.translations['vi'].statement)
    # print(problem.editorial)
    # ProblemService.save(problem, "../../../problems", problem_folder="race_condition2", overwrite=True)
    # ProblemService.save(problem, "../../../problems", overwrite=True)

    # load_problem('/home/thuc/teko/online-judge/dsa-problems/number_theory/num001_sumab')
    # load_problem('/home/thuc/teko/online-judge/dsa-problems/unsorted/minhhhh/m010_odd_to_even')
    # problem = load_problem('/home/thuc/teko/online-judge/ptoolbox/problems/array001_counting_sort3')
    # dsa_problem = DsaProblem.load('/home/thuc/teko/online-judge/dsa-problems/number_theory/num001_sumab')
    # print(dsa_problem.prints())

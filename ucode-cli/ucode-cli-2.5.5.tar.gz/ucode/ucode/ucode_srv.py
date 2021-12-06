# coding=utf-8
import json
import logging

__author__ = 'ThucNC'

import configparser
import mimetypes
import os
from datetime import datetime
from typing import List, Union

import requests
from ucode.helpers.clog import CLog
from ucode.helpers.config import Config
from ucode.helpers.misc import make_slug, dos2unix
from ucode.models.problem import Problem, TestCase
from ucode.models.question import Question, QuestionType
from ucode.services.dsa.problem_service import ProblemService

_logger = logging.getLogger(__name__)


class UCodeConstants:
    ucode_judge_langs = {
        "50": "c",
        "54": "cpp",
        "67": "pas",
        "71": "py",
        "101": "sb3"
    }


class UCode:
    def __init__(self, env="prod", domain="ucode.vn"):
        self.s = requests.session()
        self.env = env
        self.token = None
        self.tenant = domain
        self._headers = {}
        if env == "prod":
            self.api_base_url = "https://ucodeapis.com/api"
            self._headers['Referer'] = f'https://{domain}'
        elif env == "stage":
            self.api_base_url = "https://stage.ucodeapis.com/api"
            self._headers['Referer'] = 'https://stage.ucode.vn'
        else:
            self.api_base_url = "https://dev.ucodeapis.com/api"
            self._headers['Referer'] = 'https://dev.ucode.vn'
        self.load_config()

    def load_config(self):
        config = Config.get_instance().load()
        tenant_config = config.get(self.tenant)
        if not tenant_config or not tenant_config.get("credentials"):
            return
        credentials = tenant_config.get("credentials")
        if not credentials or not credentials.get(self.env):
            return
        self.token = credentials[self.env].get("access-token")
        self._headers['access-token'] = self.token

    def login(self, email, password):
        url = self.get_api_url(f"/users/sign-in")
        print(url)
        data = {
            "email": email,
            "password": password
        }
        response = self.s.post(url, json=data, headers=self._headers)
        print(self._headers)
        res_json = json.loads(response.text)
        if response.status_code != 200:
            CLog.error(f"Login Failed: {res_json['message']}")
            return None

        self.token = res_json["data"]

        config = Config.get_instance().load()
        if self.tenant not in config:
            config[self.tenant] = {}
        if "credentials" not in config[self.tenant]:
            config[self.tenant]["credentials"] = {}
        config[self.tenant]["credentials"][self.env] = {
            "env": self.env,
            "access-token": self.token
        }

        Config.get_instance().save(config)
        CLog.info(f"User `{email}` logged in successfully")

    def get_logged_in_user(self):
        self.load_config()
        if not self.token:
            CLog.error("Please login with ucode email and password first!")
            return None
        url = self.get_api_url("/users/info")
        print(url)
        print(self._headers)

        response = self.s.get(url, headers=self._headers)
        print(response.text)
        res_json = json.loads(response.text)

        if response.status_code == 401:
            CLog.error(f"Access token expired, please re-login with valid username and password.")
            return None

        print(f"Logged in `{self.env}` env with user `{res_json['data']['email']}`!")

    def upload_file(self, file_path, upload_folder):
        url = self.get_api_url(f"/general/upload-file?folder={upload_folder}")
        print("url:", url, "file name:", file_path)
        # url = "https://httpbin.org/post"
        with open(file_path, 'rb') as f:
            file_name = os.path.basename(file_path)
            print(file_name)
            # content_type = "application/binary"
            content_type = mimetypes.guess_type(file_path)[0]
            print("Content-Type:", content_type)
            files = {'file': (file_name, f, content_type)}

            response = self.s.post(url, files=files, headers=self._headers)
            # file_content = open(file_path, 'rb').read()
            # data = {'file': file_content}
            # response = self.s.post(url, data=data, headers=self._headers)
            # print("url:", url)
            # print("payload:", json.dumps(data))
            print("status code", response.status_code)
            print(response.text)
            if response.ok:
                return response.json().get("data")
        return None

    def upload_and_replace_problem_resource(self, problem: Problem, upload_folder="problem_resources"):
        if not problem.resource_files:
            return

        for resource in problem.resource_files:
            filename = os.path.basename(resource)
            print("resource:", filename, resource)
            remote_url = self.upload_file(resource, upload_folder)
            if not remote_url:
                CLog.error(f"Cannot upload file `{resource}`")
            ProblemService.replace_image_urls(problem, filename, remote_url)

    def get_api_url(self, path):
        return self.api_base_url + path

    def download_testcases(self, question_id, problem: Problem):
        url = self.get_api_url(f"/question/{question_id}/testcase")
        response = self.s.get(url, headers=self._headers)
        print(url)
        print("status_code:", response.status_code)
        data_json = response.json()
        if not data_json['success']:
            CLog.error(f"Fail to get testcases of question #{question_id}: {json.dumps(data_json)}")
            return []

        testcase_json = data_json['data']
        # print(json.dumps(testcase_json))

        for i, test_data in enumerate(testcase_json):
            CLog.info(f"Downloading testcase #{i+1}...")
            if not test_data['output_url']:
                CLog.error(f"output_url of question #{question_id} is not valid")
                raise ValueError(f"output_url of question #{question_id} is not valid")
            if test_data['input_url']:
                input_data = requests.get(test_data['input_url']).text
            else:
                input_data = ""
            output_data = requests.get(test_data['output_url']).text
            test = TestCase(input=input_data, output=output_data, sample=test_data['is_sample'])
            if test.sample:
                problem.testcases_sample.append(test)
            else:
                problem.testcases.append(test)

        return problem

    def get_question(self, question_id, download_testcases=False, language=None):
        url = self.get_api_url(f"/question/{question_id}")
        if language:
            url += f"?language={language}"
        response = self.s.get(url, headers=self._headers)
        print(url)
        print("status_code:", response.status_code)
        data_json = response.json()
        if not data_json['success']:
            CLog.error(f"Fail to get question #{question_id}: {json.dumps(data_json)}")
            return

        ques = data_json['data']
        print(json.dumps(ques))

        if ques['type'] in ['code']:
            problem = Problem()
            problem.name = ques['name']
            problem.slug = make_slug(problem.name)
            problem.statement_language = ques['statement_language']
            if ques['code_stuff']:
                code_stubs = {}
                for lang, code in json.loads(ques['code_stuff']).items():
                    ext = UCodeConstants.ucode_judge_langs.get(str(lang))
                    if not ext:
                        ext = lang
                    code_stubs[ext] = code
                problem.code_stubs = code_stubs
                # print(problem.code_stubs)
            problem.difficulty = ques['difficulty']
            problem.tags = ques['tags']
            problem.src = ques['source']
            problem.src_url = ques['source_detail']
            if not language and ques['languages']:
                for lang in ques['languages']:
                    if lang != problem.statement_language:
                        problem.translations[lang] = \
                            self.get_question(question_id, language=lang, download_testcases=False)
            problem.statement = ques['statement']
            problem.statement_format = ques['statement_format']
            problem.input_format = ques['input_desc']
            problem.output_format = ques['output_desc']
            problem.constraints = ques['constraints']
            if ques['hint']:
                problem.editorial = json.loads(ques['hint']).get('text')

            if ques['solutions']:
                sol = json.loads(ques['solutions'])
                if sol and sol.get("text"):
                    sol = sol.get('text').strip()
                    if sol.startswith('```') and sol.endswith('```'):
                        sol = "\n".join(sol.splitlines()[1:-1])

                    sol += "\n"

                    if "#include" in sol:
                        lang = "cpp"
                    elif "end." in sol:
                        lang = "pas"
                    else:
                        lang = "py"
                    problem.solutions = [{"lang": lang, "code": sol}]

            if download_testcases:
                self.download_testcases(question_id, problem)

            return problem
        else:
            return ques

    def get_question_from_quiz(self, quiz_id, save_to_folder=".", testcase_format="ucode"):
        url = self.get_api_url(f"/lesson-item/{quiz_id}/question")
        response = self.s.get(url, headers=self._headers)
        print(url)
        print("status_code:", response.status_code)
        data_json = response.json()
        if not data_json['success']:
            CLog.error(f"Fail to get quiz #{quiz_id}: {json.dumps(data_json)}")
            return

        questions_json = data_json['data']
        print(json.dumps(questions_json))
        # questions = []
        save_to_folder = os.path.join(save_to_folder, f"quiz_{quiz_id}")
        os.makedirs(save_to_folder, exist_ok=True)

        for question_json in questions_json:
            ques_id = question_json['id']
            if question_json['type'] == "code":
                CLog.info(f"Start downloading problem #{ques_id}")
                problem = self.get_question(ques_id, download_testcases=True)
                ProblemService.save(problem, save_to_folder, testcase_format=testcase_format)
                # questions.append(question)
            else:
                question_json.update(self.get_question(ques_id, download_testcases=False))

        with open(os.path.join(save_to_folder, f"quiz_{quiz_id}.json"), 'w', encoding="utf-8") as f:
            f.write(json.dumps(questions_json, indent=2, ensure_ascii=False))

    def add_question_to_quiz(self, question_ids: List[int], quiz_id: int):
        url = self.get_api_url(f"/lesson-item/{quiz_id}/add-question")
        payload = {
            "question_ids": question_ids
        }

        response = self.s.post(url, json=payload, headers=self._headers)
        print("status_code:", response.status_code)
        print(url)
        print(response.text)
        res = response.json()
        # print(res)
        if res['success']:
            print(f"questions(s) successfully added to quiz {quiz_id}:", question_ids)
        else:
            CLog.error("Cannot add questions to quiz:" + json.dumps(res))

    def add_question_to_daily_challenge(self, question_id: int, ucoin: int, date: str, status: str="draft"):
        """

        @param question_id:
        @param ucoin:
        @param date:
        @param status: draft / published
        @return:
        """
        url = self.get_api_url(f"/challenge-problem/upsert")
        start_date = datetime.fromisoformat(date + " 07:00:00+07:00")
        end_date = datetime.fromisoformat(date + " 23:59:59+07:00")
        payload = {
            "question_id": question_id,
            "status": status,
            "start_date": int(start_date.timestamp()),
            "end_date": int(end_date.timestamp()),
            "ucoin": ucoin,
        }

        response = self.s.post(url, json=payload, headers=self._headers)
        print("status_code:", response.status_code)
        print(url)
        print(response.text)
        res = response.json()
        if res['success']:
            print(f"Questions #{question_id} ({ucoin} ucoins) successfully added to daily challenge at {start_date}")
        else:
            CLog.error("Cannot add questions to quiz:" + json.dumps(res))

    def create_problem(self, problem: Union[Question, Problem, dict, str],
                       score=10, xp=10, lang=None, statement_format="markdown", question_type='code',
                       status="published", visibility="unlisted", request_approval=False):
        """
        :param problem:
        :param score:
        :param xp: -1 để tự động tính theo độ khó
        :param lang:
        :param statement_format:
        :param question_type: multiple_choice, short_answer, code, turtle, sport
        :return:
        """
        if isinstance(problem, str):
            problem: Problem = ProblemService.load(problem, load_testcase=True)

        if isinstance(problem, Problem):
            self.upload_and_replace_problem_resource(problem)
            if not lang:
                lang = problem.statement_language
            if not lang:
                lang = "vi"
            ucoin = xp
            if ucoin < 0:
                # ucoin = int(round(50 * problem.difficulty**1.5, -2))
                ucoin = int(round(2 * 50 * problem.difficulty**1.1, -2))//2
            if ucoin <= 0:
                ucoin = 100
            data = {
                "name": problem.name,
                "slug": problem.slug if problem.slug else make_slug(problem.name),
                "type": question_type,
                "statement": problem.statement,
                "statement_format": statement_format,
                "input_desc": problem.input_format,
                "output_desc": problem.output_format,
                "constraints": problem.constraints,
                "compiler": "python",
                "statement_language": lang,
                "score": score,
                "difficulty": problem.difficulty,
                "status": status,
                "visibility": visibility,
                "ucoin": ucoin,
                # "source": problem.src_url if problem.src_url else "",
                "source_detail": problem.src_url if problem.src_url else "",
                'tags': problem.tags
            }
            if problem.editorial:
                data['hint'] = json.dumps({
                    "text": problem.editorial,
                    "text_type": "markdown"
                })
            if problem.solutions:
                solution_text = ""
                for solution in problem.solutions:
                    solution_text += f"```{solution['lang']}\n"
                    solution_text += f"{solution['code']}\n"
                    solution_text += f"```\n\n\n"

                data['solutions'] = json.dumps({
                    "text": solution_text,
                    "text_type": "markdown"
                })

            if request_approval:
                data['approval_status'] = 'waiting_for_approval'
            # if problem.solution:
            #     data["solution"] = problem.solution
        elif isinstance(problem, Question):
            if not lang:
                lang = problem.statement_language
            if not lang:
                lang = "vi"
            question: Question = problem
            print(f"statement language: {lang}, {problem.statement_language}")
            data = {
                "name": question.src_name,
                "type": question.type.value or question_type,
                "statement": question.statement,
                "statement_format": question.statement_format or statement_format,
                "statement_language": lang,
                "score": score,
                "status": status,
                "visibility": visibility,
                "ucoin": xp,
                "source_detail": "base_question" if question.base_question else
                                               ("sub_question" if question.sub_question else "")
            }

            new_option_format = True
            # new_option_format = False
            # if not isinstance(question.options, list):
            #     new_option_format = True
            # else:
            #     for i, option in enumerate(question.options):
            #         if not isinstance(option, QuestionOption):
            #             # CLog.error("Option not valid:")
            #             # print(question.to_json())
            #             new_option_format = True
            #             break
            #         if not option.content:
            #             new_option_format = True
            #             break
            #         data[f"option{i + 1}"] = option.content
            #         if option.is_correct:
            #             data['answer'] = f"{i + 1}"

            question_json = json.loads(question.to_json())
            if question.solution:
                data['solution'] = question.solution
            elif question.solutions:
                data['solutions'] = json.dumps(question_json['solutions'])

            if question.hint:
                data['hint'] = json.dumps(question_json["hint"])

            if question.statement_media:
                data['statement_media'] = json.dumps(question_json["statement_media"])

            if question.option_display:
                data['option_display'] = json.dumps(question_json["option_display"])

            if question.source:
                data['source'] = json.dumps(question_json["source"])

            if new_option_format:
                data['options'] = json.dumps(question_json["options"])

            if question.answer is not None:
                data['answers'] = question.answer
            # if question.type == QuestionType.SHORT_ANSWER:
            #     print("data:", data)
        elif isinstance(problem, dict):
            data = problem
        else:
            raise Exception(f"Unsupported problem type {type(problem)}")

        # if lesson_id:
        #     url = self.get_api_url(f"/lesson-item/{lesson_id}/question")
        # else:
        url = self.get_api_url(f"/question")

        response = self.s.post(url, json=data, headers=self._headers)
        # print("url:", url)
        # print("payload:", json.dumps(data))
        print("status code", response.status_code)
        print(response.text)
        res = response.json()
        print(res)
        if res['success']:
            question_id = res['data']['id']
            print("question_id:", question_id)
        else:
            raise Exception("Cannot create question:" + json.dumps(res))

        if isinstance(problem, Problem):
            # upload testcase
            # for i, testcase in enumerate(problem.testcases):
            #     self.upload_testcase(question_id, testcase, is_sample=i<2)
            self.upload_testcases(question_id, ProblemService.join_testcases(problem))

        if isinstance(problem, Problem):
            if problem.translations:
                for tran_lang, tran_problem in problem.translations.items():
                    CLog.info(f"Creating translation {tran_lang} for question #{question_id}...")
                    data = {
                        "name": tran_problem.name,
                        "type": "code",
                        "root_question_id": question_id,
                        "statement": tran_problem.statement,
                        "statement_language": tran_lang,
                        "input_desc": tran_problem.input_format,
                        "output_desc": tran_problem.output_format,
                        "constraints": tran_problem.constraints,
                        "status": status,
                        "visibility": visibility,

                    }
                    # print("url:", url)
                    # print("payload:", json.dumps(data))

                    response = self.s.post(url, json=data, headers=self._headers)
                    print("status code", response.status_code)
                    print(response.text)
                    res = response.json()
                    if res['success']:
                        tran_question_id = res['data']['id']
                        print("translated question_id:", tran_question_id)
                    else:
                        raise Exception("Cannot create question:" + json.dumps(res))

        return question_id

    def create_problems(self, problems: List[Union[Question, Problem, str]], score=10, xp=10, lang=None, quiz_id=None):
        question_ids = []
        for problem in problems:
            q_id = self.create_problem(problem=problem, score=score, xp=xp, lang=lang)
            question_ids.append(q_id)

        if quiz_id:
            self.add_question_to_quiz(quiz_id=quiz_id, question_ids=question_ids)

        return question_ids

    def upload_all_questions_to_quiz(self, quiz_folder, quiz_id, real_upload=False, use_v1=False):
        if use_v1:
            problems = ProblemService.read_all_problems_v1(quiz_folder, nested_folder=False)
        else:
            problems = ProblemService.read_all_problems(quiz_folder, nested_folder=False)

        for i, (problem_folder, problem) in enumerate(problems):
            if use_v1:
                problem = ProblemService.load_v1(problem_folder, load_testcase=True, translations=['vi'])
            else:
                problem = ProblemService.load(problem_folder, load_testcase=True)
            # problem = ProblemService.load_v1(problem_folder, load_testcase=True, translations=['vi'])
            print(i + 1, problem.name, "testcases:", len(problem.testcases), ", sample test:",
                  len(problem.testcases_sample))

            # print("translations", problem.statement_language, list(problem.translations.keys())[0])
            if real_upload:
                prob_id = self.create_problem(problem=problem, xp=-1, score=100)
                CLog.info(f"Created problem: {prob_id}")
                self.add_question_to_quiz(quiz_id=quiz_id, question_ids=[prob_id])
                print(f"Problem uploaded with id #{prob_id} and added to quiz {quiz_id}")

        print("Total problems:", len(problems))

    def upload_testcases(self, problem_id, testcases: List[TestCase], score=10, sample_score=0):
        url = self.get_api_url(f"/question/{problem_id}/add-testcases")
        testcase_data = []
        for i, testcase in enumerate(testcases):
            t = {
                "name": testcase.name,
                "explanation": testcase.explanation,
                "input": dos2unix(testcase.input),
                "output": dos2unix(testcase.output),
                "score": sample_score if testcase.sample else score,
                "is_sample": testcase.sample
            }
            testcase_data.append(t)
        payload = {
            "testcases": testcase_data
        }

        response = self.s.post(url, json=payload, headers=self._headers)
        print("url:", url)
        print("status_code:", response.status_code)
        print(response.text)
        res = response.json()
        # print(res)
        if res['success']:
            print(len(testcases), "testcase(s) upload successfully")
        else:
            CLog.error("Cannot create testcase:" + json.dumps(res))

    def upload_testcase(self, problem_id, testcase: TestCase, is_sample=True, score=10):
        url = self.get_api_url(f"/question/{problem_id}/testcase")
        data = {
            "name": testcase.name,
            "explanation": testcase.explanation,
            "input": dos2unix(testcase.input),
            "output": dos2unix(testcase.output),
            "score": 0 if is_sample else score,
            "is_sample": bool(is_sample)
        }

        response = self.s.post(url, json=data, headers=self._headers)
        print(response.status_code)
        res = response.json()
        print(res)
        if res['success']:
            testcase_id = res['data']['id']
            print("testcase_id:", testcase_id)
        else:
            CLog.error("Cannot create testcase:" + json.dumps(res))

    @staticmethod
    def read_credential(credential_file):
        config = configparser.ConfigParser()
        config.read(credential_file)
        if not config.has_section('UCODE'):
            CLog.error(f'Section `UCODE` should exist in {credential_file} file')
            return None, None
        if not config.has_option('UCODE', 'api_url') or not config.has_option('UCODE', 'token'):
            CLog.error(f'api_url and/or token are missing in {credential_file} file')
            return None, None

        api_url = config.get('UCODE', 'api_url')
        token = config.get('UCODE', 'token')

        return api_url, token

    def create_chapter_or_lesson(self, course_id, chapter_name, slug=None, parent_id=None,
                                 status="draft", _type="chapter", is_free=True):
        """

        @param course_id:
        @param chapter_name:
        @param slug:
        @param parent_id:
        @param status: published / draft
        @param _type: chapter / lesson
        @param is_free:
        @return: newly created chapter id
        """
        if not slug:
            slug = make_slug(chapter_name)

        data = {
            "parent_id": parent_id if parent_id else 0,
            "item_type": _type,
            "name": chapter_name,
            "is_preview": False,
            "is_free": is_free,
            "slug": slug,
            "status": status
        }

        url = self.get_api_url(f"/curriculum/{course_id}/course-items")

        response = self.s.post(url, json=data, headers=self._headers)

        print(response.status_code)
        res = response.json()
        print(res)
        if res['success']:
            return res['data']['id']
        else:
            raise Exception("Cannot create chapter:" + json.dumps(res))

    def create_blog(self, title, slug=None, content_format="markdown",
                    content="", short_description="", status="published"):
        if not slug:
            slug = make_slug(title)

        data = {
            "short_description": short_description,
            "content": content,
            "title": title,
            "content_format": content_format,
            "slug": slug,
            "status": status,
        }

        url = self.get_api_url(f"/blog-posts")

        response = self.s.post(url, json=data, headers=self._headers)
        print(response.status_code)
        # print(response.text)
        res = response.json()
        print(res)
        if not res['success']:
            raise Exception("Cannot blog:" + json.dumps(res))

        blog_id = res['data']['id']
        return blog_id

    def create_lesson_item(self, course_id, chapter_id, lesson_name, slug=None,
                           description="", content="", short_description="",
                           type="video", video_url="",
                           file_url="",
                           file_type="pdf",
                           status="published", is_free=True, visibility="unlisted", ucoin=100,
                           content_format="markdown",
                           quiz_type="submit_single_question"):
        if not slug:
            slug = make_slug(lesson_name)

        data = {
            "parent_id": chapter_id,
            "item_type": "lesson_item",
            "name": lesson_name,
            "is_preview": False,
            "content_type": type,
            "is_free": is_free,
            "slug": slug,
            "status": status
        }

        url = self.get_api_url(f"/curriculum/{course_id}/course-items")

        response = self.s.post(url, json=data, headers=self._headers)
        print(response.status_code)
        res = response.json()
        # print(res)
        if not res['success']:
            raise Exception("Cannot create course item for lesson:" + json.dumps(res))

        course_item_id = res['data']['id']
        print("course_item_id:", course_item_id)
        lesson_item_id = res['data']['lesson_item_id']
        print("lesson_item_id:", lesson_item_id)
        # if type == "video":
        if video_url or content or description:
            url = self.get_api_url(f"/lesson-item/{lesson_item_id}")
            data = {
                "description": description,
                "short_description": short_description,
                "video_url": video_url,
                "file_url": file_url,
                "file_type": file_type,
                "content": content,
                "name": lesson_name,
                "content_format": content_format,
                "slug": slug,
                "is_free": is_free,
                "is_preview": False,
                "visibility": visibility,
                "ucoin": ucoin,
                "status": status,
            }

            if type == "quiz":
                data['quiz_type'] = quiz_type

            response = self.s.put(url, json=data, headers=self._headers)
            print(response.status_code)
            # print(response.text)
            res = response.json()
            print(res)
            if not res['success']:
                raise Exception("Cannot lesson item:" + json.dumps(res))
        return lesson_item_id

    def get_course_curriculum(self, course_id, save_to_folder=None, get_quizes=False):
        url = self.get_api_url(f"/curriculum/{course_id}/course-items")
        response = self.s.get(url, headers=self._headers)
        print(url)
        print("status_code:", response.status_code)
        data_json = response.json()
        if not data_json['success']:
            CLog.error(f"Fail to get curriculum of course #{course_id}: {json.dumps(data_json)}")
            return

        curriculum = data_json['data']

        for chapter in curriculum:
            items = chapter['items']
            for item in items:
                if item['item_type'] == "lesson":
                    for lesson_item in item['items']:
                        lesson_item.update(self.get_lesson_item(lesson_item['lesson_item_id']))
                        if get_quizes and lesson_item['content_type'] == 'quiz':
                            quiz_id = lesson_item['lesson_item_id']
                            self.get_question_from_quiz(quiz_id, save_to_folder)
                else: # lesson_item
                    item.update(self.get_lesson_item(item['lesson_item_id']))
                    if get_quizes and item['content_type'] == 'quiz':
                        quiz_id = item['lesson_item_id']
                        self.get_question_from_quiz(quiz_id, save_to_folder)

        print(json.dumps(curriculum, indent=2, ensure_ascii=False))
        if save_to_folder:
            with open(os.path.join(save_to_folder, f"course_{course_id}.json"), 'w', encoding="utf-8") as f:
                f.write(json.dumps(curriculum, indent=2, ensure_ascii=False))
        return curriculum

    def get_lesson_item(self, lesson_item):
        url = self.get_api_url(f"/lesson-item/{lesson_item}")
        response = self.s.get(url, headers=self._headers)
        print(url)
        print("status_code:", response.status_code)
        data_json = response.json()
        if not data_json['success']:
            CLog.error(f"Fail to get lesson item #{lesson_item}: {json.dumps(data_json)}")
            return

        lesson_item = data_json['data']
        return lesson_item

    def create_course_curriculum(self, course_id, curriculum_file, create_quizes=False):
        with open(curriculum_file, encoding="utf-8") as f:
            curriculum = json.load(f)
        print("curriculum:\n", json.dumps(curriculum))
        folder = os.path.split(curriculum_file)[0]
        for chapter in curriculum:
            chapter['is_free'] = False
            chapter['status'] = "published"

            new_chapter_id = self.create_chapter_or_lesson(
                course_id=course_id, chapter_name=chapter['name'],
                status=chapter['status'], _type=chapter["item_type"], is_free=chapter['is_free'])

            items = chapter['items']
            for item in items:
                if item['item_type'] == "lesson":
                    item['is_free'] = False
                    item['status'] = 'published'
                    new_lesson_id = self.create_chapter_or_lesson(
                        course_id=course_id, chapter_name=item['name'], parent_id=new_chapter_id,
                        status=item['status'], _type=item["item_type"], is_free=item['is_free'])

                    for lesson_item in item['items']:
                        # lesson_item.update(self.get_lesson_item(lesson_item['lesson_item_id']))
                        lesson_item['status'] = 'published'
                        lesson_item['is_free'] = False
                        new_lesson_item_id = self.create_lesson_item(
                            course_id=course_id, chapter_id=new_lesson_id, lesson_name=lesson_item['name'],
                            description=lesson_item['description'],
                            short_description=lesson_item['short_description'],
                            content=lesson_item['content'], type=lesson_item['content_type'],
                            video_url=lesson_item['video_url'],
                            file_url=lesson_item['file_url'],
                            file_type=lesson_item['file_type'],
                            is_free=lesson_item['is_free'],
                            status=lesson_item['status'],
                            visibility=lesson_item['visibility'],
                            ucoin=lesson_item['ucoin']
                        )
                        if create_quizes and lesson_item['content_type'] == 'quiz':
                            self.upload_question_from_local(lesson_item, folder, new_lesson_item_id)
                else:  # lesson_item
                    # item.update(self.get_lesson_item(item['lesson_item_id']))
                    lesson_item = item
                    lesson_item['status'] = 'published'
                    lesson_item['is_free'] = False
                    new_lesson_item_id = self.create_lesson_item(
                        course_id=course_id, chapter_id=new_chapter_id, lesson_name=lesson_item['name'],
                        description=lesson_item['description'],
                        short_description=lesson_item['short_description'],
                        content=lesson_item['content'], type=lesson_item['content_type'],
                        video_url=lesson_item['video_url'],
                        file_url=lesson_item['file_url'],
                        file_type=lesson_item['file_type'],
                        is_free=lesson_item['is_free'],
                        status=lesson_item['status'],
                        visibility=lesson_item['visibility'],
                        ucoin=lesson_item['ucoin']
                    )
                    if create_quizes and lesson_item['content_type'] == 'quiz':
                        self.upload_question_from_local(lesson_item, folder, new_lesson_item_id)
            # break # test 1st chapter

    def upload_question_from_local(self, lesson_item_json, base_folder, quiz_id):
        local_quiz_id = lesson_item_json['lesson_item_id']
        quiz_folder = os.path.join(base_folder, f"quiz_{local_quiz_id}")
        with open(os.path.join(quiz_folder, f"quiz_{local_quiz_id}.json"), encoding="utf-8") as f:
            quiz_json = json.load(f)
        if quiz_json and quiz_json[0]['type'] == "code":
            CLog.info(f"Uploading coding quiz from `{quiz_folder}`")
            self.upload_all_questions_to_quiz(quiz_id=quiz_id,
                                              quiz_folder=quiz_folder, real_upload=True)
        else:
            for question_json in quiz_json:
                data = {}
                for k in ["name", "type", "headline", "statement_language", "score",
                          "status", "visibility", "ucoin",
                          "source", "source_detail", "subject", "difficulty", "tags",
                          "difficult_level", "slug", "display_type", "options",
                          "option_display", "answers", "hint", "solutions",
                          "input_desc", "output_desc", "constraints", "statement",
                          "statement_format", "statement_media", "extra_info"]:
                    if question_json[k]:
                        data[k] = question_json[k]
                    if not "name" in data:
                        data['name'] = ""
                ques_id = self.create_problem(problem=data)
                CLog.info(f"Created problem: {ques_id}")
                self.add_question_to_quiz(quiz_id=quiz_id, question_ids=[ques_id])
                print(f"Problem uploaded with id #{ques_id} and added to quiz {quiz_id}")


def create_chapters_mc1():
    ucode = UCode("dev")

    course_id = 7
    for w in range(1, 13):
        chapter_name = "Thử thách %02d" % w
        chapter_id = ucode.create_chapter_or_lesson(course_id=course_id, chapter_name=chapter_name)


def create_problem(env="dev", domain="ucode.vn"):
    # problems = ProblemService.read_all_problems_v1("/home/thuc/projects/ucode/weekly-algorithm-problems/week13",
    #                                                translations=["vi"], load_testcase=True)
    # problem_folder = "D:\\projects\\ucode\\dsa-thematic-problems\\de_thi_hsg\\quan_ba_dinh_2020_2021_thcs_round2\\p03_capdoixung"
    problem_folder = "D:\\projects\\ucode\\weekly-algorithm-problems\\competitions\\teko\\impossible_check_in"
    problem = ProblemService.load(problem_folder, load_testcase=True)
    problems = [(problem_folder, problem)]

    ucode = UCode(env=env, domain=domain)

    print(len(problems))
    for i, (problem_folder, problem) in enumerate(problems):
        print(i+1, problem.name)
        # print(problem.tags)
        # print(problem.translations['vi'].statement)
        print("Testcases: ", len(problem.testcases))
        # res = ucode.create_problem(problem=problem, lang="en", xp=-1, status="draft")
        # id = ucode.create_problem(problem=problem, xp=-1, request_approval=True)
        # print("question created with id:", id)
        # break


# def upload_all_problems_in_folder():
#     lession_id = 4046
#     # lession_id = 0 # public problem
#     base_folder = "D:\\projects\\ucode\\dsa-thematic-problems\\BaDinh_2021_9"
#     problems = ProblemService.read_all_problems(base_folder, nested_folder=False)
#     print("Total problems:", len(problems))
#
#     # ucode = UCode("https://dev-api.ucode.vn/api", "26fd9211ce59375f5f01987bb868d170")
#     ucode = UCode("https://api.ucode.vn/api", "88a6973b6288aa09ba01767e8bd4ab94")
#
#     for i, (problem_folder, problem) in enumerate(problems):
#         problem = ProblemService.load(problem_folder, load_testcase=True)
#         print(i + 1, problem.name)
#         # ucode.create_problem(lesson_id=lession_id, problem=problem, xp=200)
#         print("testcases:", len(problem.testcases), len(problem.testcases_sample))
#         ucode_id = ucode.create_problem(lesson_id=lession_id, problem=problem, xp=-1)
#         print("uCode problem created: ", ucode_id)


def create_problems_to_lesson_ucode(env="dev", domain="ucode.vn"):
    # base_folder = r"D:\projects\ucode\ucode-cli\problems\_save\c"
    base_folder = r"D:\projects\ucode\basic-programming-problems\adhoc"
    problems = ProblemService.read_all_problems(base_folder, nested_folder=False)
    # problems = ProblemService.read_all_problems_v1(base_folder, nested_folder=False)

    # prob_folder = r"D:\projects\ucode\dsa-problem-bank\lamcherry\2021-09\thpt_tests\test_05\p04_bookshelves"
    # problems = [(prob_folder, ProblemService.load(prob_folder))]

    lesson_id = 26434
    ucode = UCode(env=env, domain=domain)
    # ucode.upload_all_questions_to_quiz(quiz_folder=base_folder, quiz_id=lesson_id, real_upload=False)
    ucode.upload_all_questions_to_quiz(quiz_folder=base_folder, quiz_id=lesson_id,real_upload=True)


def reupload_testcases():
    ucode = UCode("prod")
    problem_folder = "D:\\projects\\ucode\\dsa-thematic-problems\\de_thi_hsg\\hanoi_2020_2021_thcs\\p4_itable"
    # problem_folder = "D:\\projects\\ucode\\dsa-thematic-problems\\de_thi_hsg\\vinhphuc_2020_2021_thcs\\p3_weightloss"
    problem: Problem = ProblemService.load(problem_folder, load_testcase=True)

    question_id = 45490
    ucode.upload_testcases(question_id, ProblemService.join_testcases(problem))
    #
    print(len(problem.testcases))
    print(len(problem.testcases_sample))


def teko_bb():
    bbs = """Product	06/03/2020	BB#1: Women in Tech	Dương Thu Hương		https://docs.google.com/presentation/d/1j56LrIp-VCgzBGuNb84WHfVrCcpG5XJOBF7rdhR14hY/edit
Product	10/12/2020	BB #23: Product Development Process	Hoàng Anh Duy	https://drive.google.com/file/d/1Lu8LzVpcl-REB_I5I1iEbGabIV_ihz9c/view	https://docs.google.com/document/d/13gnHsu9_5jU2cHAw940_inHXJ8YVbEXdPNBfNax_k0Y/edit
Product	11/03/2021	BB #29: How do we design metric for Product Managers	Nguyễn Viết Tuấn		https://drive.google.com/drive/folders/1iC512FI3HsfBLKCLbdaxe_1spjQXAgw-?usp=sharing
Product	25/02/2021	BB #27: How we build product at Teko - Project Timeline Management Tips	Nguyễn Viết Tuấn	https://drive.google.com/file/d/1SvvORUtwF_W4AJBnPnkDctBqVS15AsRo/view	
Product	25/03/2021	BB #31: Business Process: How do we design a Business Process for a Product Manager?	Nguyễn Viết Tuấn		https://docs.google.com/spreadsheets/d/12_Yl23tfqgK_QCVSAIwdG9t37IP3aB2vcMlc8tCsIBs/edit#gid=0
Product	08/04/2021	BB #33: UX Design Lesson Learned	Mai Thanh Bình	https://drive.google.com/file/d/1tD3mWc5Y0VFJEeO9zs9cZWah4UZ-i50N/view	https://docs.google.com/presentation/d/1XpX8a-r4A4SmE0szYIYBmHfr0gGBpKhFcx46ab20Y0o/edit
Product	29/04/2021	BB #36: Why most technical products fail	Mai Thanh Bình	https://drive.google.com/file/d/1x7bfPoZg8bCwsQULHYluoViKujcq7Onc/view	https://docs.google.com/presentation/d/1Im3LYi1nZb92Ot5GErlfr0RvB4T_i_nLfW3CMGUUtis/edit
Engineering	26/05/2020	BB#2: Golang	Nguyễn Xuân Dũng		https://drive.google.com/open?id=1CV3kO0MTGEqEx29eLJRVIPpQtHPGjyLn
Engineering	28/05/2020	BB#3: gRPC	Trần Duy Thịnh		
Engineering	03/06/2020	BB#4: Monorepo	Trần Đức Hiếu	https://drive.google.com/file/d/1g3QfY1NYbHcsZIaaqQDzDcCqbdaOHMm7/view	https://drive.google.com/file/d/1Zb0kAgnRbBITjTQ4Y_dHEJzxqUsbF1-P/view
Engineering	16/07/2020	BB#6: "Operation First Mobile Layout"	Vũ Minh Tâm	https://drive.google.com/file/d/1Fbip8XfG77hetX4qFNV9268Xb5woZnn1/view	https://docs.google.com/presentation/d/1nuHr9F9qDxSb3MdzXXIaLrsKrPXrIDEjIOV4gybNPn8/edit#slide=id.g8bf5102b19_0_248
Engineering	23/07/2020	BB#7: "Microservices and events"	Trần Tuấn Anh	https://drive.google.com/file/d/125BT6GpDR3lW-_KYrasgoa2auT597qE2/view	https://docs.google.com/presentation/d/1HqVG1ULy6oqUGx3P1aFcy5G8EA0hqs6Zz89iEVnU06I/edit#slide=id.g82939b2d8f_0_37
Engineering	30/07/2020	BB#8: "Building containers: How many ways are too many?"	Trần Tuấn Anh	https://drive.google.com/file/d/1oWDFvN8zPcoLTLvSughfQvv3urM-WQQK/view	https://drive.google.com/file/d/18sja-mb0leEGy7b8xGBwHPhatCKqACJ6/view?usp=sharing
Engineering	06/08/2020	BB#9: Machine Learning in Production	Jason Tsai	https://drive.google.com/file/d/1_SfgysyM9-p3E0GwIUilmkOnd9BwDvLO/view	https://docs.google.com/presentation/d/1xAoXywFQot4R44u3mwVijHx3XMLw3aKP86Py_QtboMA/edit
Engineering	13/08/2020	BB#10: ETL	Hoàng Thị Loan	https://drive.google.com/file/d/19F-vEX1yrkR0NUMxx8mfFVG5SrTkt2YM/view	https://docs.google.com/presentation/d/1LIjK-z8df-st5Zf5J_aPpvgCmc1VLrhhbMwOkXtWu_Y/edit
Engineering	20/08/2020	BB#11: Redis	Trần Tuấn Anh	https://drive.google.com/file/d/1SlFG1InrUOouTJOMCpUtMSScVeenHmZZ/view	https://docs.google.com/presentation/d/1PDsvi8DbzfBddQdx3MgtTErgpVxO0r879T7xzz8VyeA/edit#slide=id.g82939b2d8f_0_37
Engineering	27/08/2020	BB#12-1: Doc Design	Jason Tsai	https://drive.google.com/file/d/1P7956TwtT6Dy3J7eIE__fgeGDhDaOxz5/view	https://docs.google.com/presentation/d/1Gk7YDTWFIGxdHJ0HNFm5uXum_cFERaSvHogaSPlwZdY/edit#slide=id.p
Engineering	03/09/2020	BB#12-2: Code Reviews	Trần Tuấn Anh	https://drive.google.com/file/d/1r08yefAVj9NSTg4xeEjX5BNJTgZ8xZ1e/view	https://docs.google.com/presentation/d/1Gk7YDTWFIGxdHJ0HNFm5uXum_cFERaSvHogaSPlwZdY/edit#slide=id.p
Engineering	17/09/2020	BB #14: Development process (for e-commerce projects)	Vũ Minh Tâm, Đặng Thị Phương	https://drive.google.com/file/d/1-ieKUp32LASz2DNqP3v6uFuKMU-85s2P/view	https://docs.google.com/presentation/d/1-f_fvfmS_y5YjwSqyPx5MolJiB0Fj6vKwQ46hG68HsE/edit#slide=id.g98131b7036_0_9
Engineering	24/09/2020	BB #15: Mock Design Review	Tạ Ngọc Vân Thoa	https://drive.google.com/file/d/1s4RVmhTkpBam-aTLAVR4zWbMoaUkCK6w/view	
Engineering	15/10/2020	BB #16: Building React Native Bridge for VNShop App	Lê Vũ Huy	https://drive.google.com/file/d/1TxSCuAae4hOVUkyDMi7SLYshttY6YtMA/view	https://docs.google.com/presentation/d/1cMXxOK2axbUsQSzY1HqG8fejv8vu67QC2__iHQxuEcQ/edit
Engineering	29/10/2020	BB #17: Golang Best Practices	Nguyễn Quốc Anh	"https://drive.google.com/file/d/1q28n1g2DzcTeWY_D_170E4lDasNYDElD/view https://drive.google.com/file/d/1Ql_9VUUE304zkYV1P8T97TSUYb4zK0oc/view"	https://docs.google.com/presentation/d/1tyXReUJwqy6L4MMtB3mKobhNS9MKZwG5F-K1AR-34MI/edit
Engineering	05/11/2020	BB #18: State of Teko Engineering	Nguyễn Việt Tiến	https://drive.google.com/file/d/1xTEzAMiH9toK7AITNwm_FIu0H-drHkZR/view	https://docs.google.com/presentation/d/1CDaR9WVssb-1wQ3oEjYgxKDx6-Bbc8LAU0kJfuDafEY/edit
Engineering	19/11/2020	BB #20: Under the hood of Elasticsearch	Cao Mạnh Đạt	https://drive.google.com/file/d/1W0B-d8M_WMbcmpMtRrYDhV8-g4ErY7N_/view?usp=sharing	https://docs.google.com/presentation/d/1Fr2X4elikv1sP9kFK0Kzogs_Hx0dN4KEj15kiknUe7I/edit
Engineering	26/11/2020	BB #21: Terra Platform - How we make Super App at VNLife	Đinh Văn Tiến	"https://drive.google.com/file/d/1UJo7uIvqCa1zU0KnW7soIxjSokmqVY4U/view https://drive.google.com/file/d/1-5DP_CUfU0zPIAICyRSdpL18JrO0ONos/view"	https://docs.google.com/presentation/d/1-kxCb1tg5IgR8Bm8lmVy1YysfI4tUTArOntgMb9tpcc/edit#slide=id.g35f391192_00
Engineering	03/12/2020	BB #22: Engineering Excellence - Post-Mortem Guidelines	Jason Tsai	https://drive.google.com/file/d/1frKvuUKxUrOkLF0Hhjeg1LXNPiZefOmH/view	https://docs.google.com/document/d/1G7UGJsccjTtRr0N4maGI2PsUbnstnBkhUXYhug5ESDc/edit
Engineering	17/12/2020	BB #24: Tech Practices | API Improvement Proposals by Google | E1/S1: Standard methods	Trần Phong Phú	https://drive.google.com/file/d/17Ykl8en180rgaAi7hcZz71-bSlcCylvl/view	https://docs.google.com/presentation/d/1CEMTZgLi67x96eylEGsEXOubiWg28FVC2uFmZsx5JKg/edit
Engineering	24/12/2020	BB #25: Kubernetes Cluster in the Active/Standby Role	Huỳnh Phạm Sony	https://drive.google.com/file/d/1rW-mtu9Isx6WFzeohuAbofaD8YSe1eJK/view	
Engineering	14/01/2021	BB #26: : TerraBus - Event bus for Terra Platform	Nguyễn Bá Tú, Nguyễn Xuân Tùng	"https://drive.google.com/file/d/1S7hlPyS1dE2XhIhelyzgqnPOQ8mWJtXh/view https://drive.google.com/file/d/11YH7ywZX4qdn09zOCpNxrDeEHMrAES1F/view"	
Engineering	18/03/2021	BB #30: Unit Test The Painless	Trần Phong Phú	https://drive.google.com/file/d/1izQN9eSb460AC-APRKXWXwH_Uugm3JNJ/view	https://docs.google.com/presentation/d/1mfQXGnWhY0WcP4Fw6LjTRvD-xfJP3DRF1Ef1-I3FQjc/edit?usp=sharing
Engineering	01/04/2021	BB #32: Streaming Ingestion - things learned	Cao Mạnh Đạt	https://drive.google.com/file/d/1m9TwT6TiGWeMcLx3EYzii-jYAAk8uYKz/view	https://drive.google.com/file/d/11oqqMlk5BjO98D-eSc2ZRqtMeVdAJSJR/view
Engineering	22/04/2021	BB #35: Ceph - Distributed storage for Kubernetes	Đặng Minh Dũng	https://drive.google.com/file/d/1xRq9Fi90-jPsgFccHJuTypnKv6b76JSC/view	https://docs.google.com/presentation/d/1meHpDaEHdEYjfvipJo8N4XPcN8AWThS2MBFOVxnd_CM/edit
Engineering	06/05/2021	BB #37: High-level Omni-channel Architecture Design	Jason Tsai	https://drive.google.com/file/d/1tFHN8h6g-yss8yuCrpJrfxKXZRWik17S/view	https://docs.google.com/presentation/d/1_WC0al4teKuT1gWFGOa_9yZrAfU4TJwqSOiY7Lr3vdE/edit?usp=sharing
Engineering	27/05/2021	BB #39: Coding and Reviewing Best Practices	MinhPT	https://drive.google.com/file/d/1h8aPo-FBlBs7jFActCVIlhPY1VrouTTk/view	https://docs.google.com/presentation/d/1WiUrUa5MD8BR_nGsmx0W0F_My4ppn9arbzAzy0GY6YQ/edit
Engineering	10/06/2021	BB #41: Feature Flags & Best Practices	TriTM	https://drive.google.com/file/d/1Lt9MoBr8WQChQVvfmxEaSs4jvXMKsSPs/view	https://docs.google.com/presentation/d/1SZITJDVZMb9m_sAiY4i5kLC5Gigcg00zf3a82uNAQ6Y/edit#slide=id.g81b07784d9_0_212
Engineering	17/06/2021	BB #42: Event-driven Architecture	PhúTP		https://docs.google.com/presentation/d/10VsN5-cFvVpwckPCN96fORIiXfHPV5YTx6Cm8niIwFo/edit#slide=id.g82939b2d8f_0_37
Life Style	04/03/2021	BB #28: Weight Management	Lê Thu Thảo, Lê Thị Thanh Nhàn		https://drive.google.com/file/d/1RMsC0dzFBlNO12wYiEhjEDSflHppyxB3/view
Life Style	15/04/2021	BB #34: Personal Time Management	Ôn Như Bình		https://docs.google.com/presentation/d/19RpQz4nFlOetQOTDlL13P4KAga23zOnULv34OHOBAas/edit#slide=id.g82939b2d8f_0_37
Life Style	13/05/2021	BB #38: Personal Financial Management	BinhMT	https://drive.google.com/file/d/1c-b10PrqHkhD_wOhdXEDvXK4wuwZBQ7Q/view	https://docs.google.com/presentation/d/1YR4syEgLWD_5lY5XSuAEqiKGpn5G1RKhpMUjw5kYduw/edit
Skill	03/06/2021	BB #40: What should you write in Performance Reviews	Jason Tsai	https://drive.google.com/file/d/1SAJ7HAo9nIS4qidBK_G5LP-07OKfmn8D/view	https://docs.google.com/presentation/d/1t91PUVgUAwog2N9sQaxzs_Zkf1N_h1Pq9sS2oGmvVmM/edit
UX/UI	25/06/2020	BB#5: Design System Workshop	UX/UI Design Team		
UX/UI	12/11/2020	BB #19: How to use Teko Design System for PO an BA	Trần Thành Đạt, Phạm Mạnh Hùng	https://www.figma.com/file/SpKK4ZTpP5NygVto1KHZfQ/Design-System-Guide?node-id=0%3A1	https://www.figma.com/file/Ssd74IcfyJYZTt673CDHmI/DESIGN-SYSTEM-LIBRARY-WORKSHOP"""

    track_ids = {
        "Product": 9640,
        "Engineering": 9641,
        "UX/UI": 9642,
        "Life Style": 9643,
        "Skill": 9644,
    }
    course_id = 669

    track_ids = {
        "Product": 9453,
        "Engineering": 9454,
        "UX/UI": 9455,
        "Life Style": 9456,
        "Skill": 9457,
    }
    course_id = 648
    ucode = UCode(env="dev", domain="teko.ugrow.vn")

    for bb in bbs.split("\n"):
        track, date, title, host, video_url, slide_url = bb.split("\t")
        print(track, host, slide_url)
        print(track_ids[track])
        chapter_id = ucode.create_chapter_or_lesson(course_id=course_id, chapter_name=title, parent_id=track_ids[track],
                                                    status="published")
        # chapter_id = 9482
        print("Chapter created:", chapter_id)
        lesson_id = ucode.create_lesson_item(course_id=course_id,
                                             chapter_id=chapter_id,
                                             lesson_name=title,
                                             description=title,
                                             type="lecture",
                                             status = "published",
                                             content=f"Date: {date}\n\nHost: {host}")
        print("Lesson info created:", lesson_id)
        lesson_id = ucode.create_lesson_item(course_id=course_id,
                                             chapter_id=chapter_id,
                                             lesson_name=title + " - Video",
                                             description=title,
                                             type="video",
                                             status="published",
                                             video_url=video_url,
                                             content=title + f" - Video\n\n{video_url}" if video_url else "There is no videos for this lesson.")
        print("Lesson video created:", lesson_id)
        lesson_id = ucode.create_lesson_item(course_id=course_id,
                                             chapter_id=chapter_id,
                                             lesson_name=title + " - Slide",
                                             description=title,
                                             type="file",
                                             file_url=slide_url,
                                             file_type="",
                                             status="published",
                                             content=title + f" - Slide\n\n{slide_url}" if slide_url else "There is no slide for this lesson.")
        print("Lesson slide created:", lesson_id)
        # break


def test_get_question():
    # env, domain = "prod", "ucode.vn"
    env, domain = "prod", "tinhoctre.ucode.vn"
    # question_id = 44242
    # question_id = 97526
    question_id = 99888

    ucode = UCode(env=env, domain=domain)

    problem = ucode.get_question(question_id, download_testcases=True)

    save_to = r"D:\projects\ucode\ucode-cli\problems\_save\c"
    ProblemService.save(problem, save_to, overwrite=True, testcase_format="ucode")


def test_get_questions_from_quiz():
    env, domain = "prod", "ucode.vn"
    ucode = UCode(env=env, domain=domain)
    quiz_id = 75
    save_to = r"D:\projects\ucode\ucode-cli\problems\_save"

    ucode.get_question_from_quiz(quiz_id, save_to_folder=save_to)


def add_to_daily_challenge():
    test_login()
    ucode = UCode(env="prod", domain="ucode.vn")

    date = "2021-12-21"
    folder = r"D:\projects\ucode\dsa-problem-bank\HTDung\2021-11\daily_challenges\challenge_027"
    problems = ProblemService.read_all_problems(folder, nested_folder=False)

    for i, (problem_folder, problem) in enumerate(problems):
        problem = ProblemService.load(problem_folder, load_testcase=True)
        print(i + 1, problem.name, "testcases:", len(problem.testcases), ", sample test:",
              len(problem.testcases_sample))

        prob_id = ucode.create_problem(problem=problem, xp=-1, score=100)
        ucoin = [500,1000,2000][i]
        CLog.info(f"Created problem: {prob_id}")
        ucode.add_question_to_daily_challenge(question_id=prob_id, ucoin=ucoin,
                                              date=date, status="published")
        print(f"Problem uploaded with id #{prob_id} and added to challenge {date}")


def test_get_course_curriculum():
    env, domain = "prod", "ucode.vn"
    ucode = UCode(env=env, domain=domain)
    # course_id = 822
    course_id = 822
    save_to = r"D:\projects\ucode\ucode-cli\problems\_save"

    ucode.get_course_curriculum(course_id, save_to_folder=save_to, get_quizes=True)


def test_create_course_curriculum():
    ucode = UCode(env="prod", domain="uschool.vn")
    # ucode.login("gthuc.nguyen@gmail.com", "15041985")
    # ucode.get_logged_in_user()
    course_id = 830
    curriculum_file = r"D:\projects\ucode\ucode-cli\problems\_courses\py101\course_822.json"
    ucode.create_course_curriculum(course_id, curriculum_file, create_quizes=True)


def test_create_question_from_json():
    question_json = {
        "id": 2,
        "teacher_id": 1,
        "teacher_name": None,
        "teacher_avatar": None,
        "name": "",
        "type": "multiple_choice",
        "headline": "",
        "statement_language": "vi",
        "programming_languages": None,
        "code_stuff": None,
        "resource_limit": None,
        "root_question_id": None,
        "score": 25,
        "status": "published",
        "compiler": "python",
        "visibility": "unlisted",
        "approval_status": None,
        "approval_msg": None,
        "ucoin": 25,
        "languages": [
          "vi"
        ],
        "source": None,
        "source_detail": None,
        "subject": "code",
        "difficult_level": None,
        "tags": [],
        "difficulty": None,
        "num_submitted_users": 1542,
        "num_accepted_users": 1232,
        "num_submission": 13009,
        "num_accepted_submission": 1327,
        "user_status": None,
        "user_last_submitted_at": None,
        "user_best_score": None,
        "slug": "2",
        "editable": True,
        "enable_on_quiz": None,
        "available_for_challenge": None,
        "display_type": None,
        "options": "[{\"text\": \"Ng\\u00f4n ng\\u1eef l\\u1eadp tr\\u00ecnh c\\u00f3 c\\u1ea5u tr\\u00fac (ng\\u1eef ph\\u00e1p) ch\\u1eb7t ch\\u1ebd\", \"text_type\": \"markdown\"}, {\"text\": \"Ng\\u00f4n ng\\u1eef l\\u1eadp tr\\u00ecnh \\u0111\\u01a1n gi\\u1ea3n h\\u01a1n r\\u1ea5t nhi\\u1ec1u so v\\u1edbi ng\\u00f4n ng\\u1eef t\\u1ef1 nhi\\u00ean\", \"text_type\": \"markdown\"}, {\"text\": \"Ng\\u00f4n ng\\u1eef l\\u1eadp tr\\u00ecnh l\\u00e0 c\\u00e1ch duy nh\\u1ea5t \\u0111\\u1ec3 giao ti\\u1ebfp v\\u1edbi m\\u00e1y t\\u00ednh\", \"text_type\": \"markdown\"}, {\"text\": \"Ng\\u00f4n ng\\u1eef l\\u1eadp tr\\u00ecnh d\\u00f9ng \\u0111\\u1ec3 t\\u1ea1o ra c\\u00e1c ch\\u01b0\\u01a1ng tr\\u00ednh m\\u00e1y t\\u00ednh\", \"text_type\": \"markdown\"}]",
        "option_display": None,
        "answers": "0,1,3",
        "input_desc": "",
        "output_desc": "",
        "constraints": None,
        "hint": "",
        "solutions": None,
        "statement": "Những điều nào sau đây là đúng khi nói về ngôn ngữ lập trình",
        "statement_format": "markdown",
        "statement_media": None,
        "extra_info": None,
        "max_submit_times": None,
        "user_best_answer": None,
        "user_answer_format": None,
        "user_best_source_code": None,
        "user_language_id": None,
        "user_file_type": None,
        "variant_question_id": None,
        "sample_testcases": None,
        "categories": []
      }

    data = {}
    for k in ["name", "type", "headline", "statement_language", "score", "status", "visibility", "ucoin",
              "source", "source_detail", "subject", "difficulty", "tags", "difficult_level",
              "slug", "display_type", "options", "option_display", "answers", "hint", "solutions",
              "input_desc", "output_desc", "constraints", "statement", "statement_format", "statement_media",
              "extra_info"]:
        if question_json[k]:
            data[k] = question_json[k]
        if not "name" in data:
            data['name'] = ""

    ucode = UCode(env="prod", domain="uschool.vn")
    # ucode.login("gthuc.nguyen@gmail.com", "15041985")
    # ucode.get_logged_in_user()
    # course_id = 830
    print("question data:", json.dumps(data))
    ucode.create_problem(data)


def test_login():
    # ucode = UCode(env="prod", domain="teko.ugrow.vn")
    # ucode = UCode(env="dev", domain="teko.ugrow.vn")
    ucode = UCode(env="prod", domain="ucode.vn")
    # ucode = UCode(env="prod", domain="tinhoctre.ucode.vn")
    # ucode.login("teko@ugrow.vn", "123456")
    # ucode.login("gthuc.nguyen@gmail.com", "15041985")
    # ucode.login("gthuc.nguyen@gmail.com", "12345678")
    ucode.get_logged_in_user()


if __name__ == "__main__":
    test_login()
    # teko_bb()
    # reupload_testcases()

    # test_get_question()

    # create_problems_to_lesson_ucode("prod", domain="teko.ugrow.vn")
    # create_problems_to_lesson_ucode("prod")

    # test_get_questions_from_quiz()
    # test_get_course_curriculum()

    # test_create_course_curriculum()

    # test_create_question_from_json()

    add_to_daily_challenge()

    # create_problem("dev")
    # create_problem("prod", domain="teko.ugrow.vn")
    # create_problem("prod", domain="ucode.vn")
    # upload_all_problems_in_folder()

    # lession_id = 4068
    # # lession_id = 0
    # # #
    # # # # ucode = UCode("https://dev-api.ucode.vn/api", "26fd9211ce59375f5f01987bb868d170")
    # ucode = UCode("https://api.ucode.vn/api", "88a6973b6288aa09ba01767e8bd4ab94")
    # # #
    # problem_folder = "D:\\projects\\ucode\\dsa-problems\\unsorted\\thuc\\beautiful_pairs"
    # problem: Problem = ProblemService.load(problem_folder, load_testcase=True)
    #
    # print(problem.name)
    # print(len(problem.testcases))
    # print(len(problem.testcases_sample))
    # print(problem.tags)
    # print(problem.resource_files)
    #
    # ucode_id = ucode.create_problem(lesson_id=0, problem=problem, xp=-1)
    # print("uCode problem created: ", ucode_id)
    # print(problem.statement)
    # print(problem.translations['en'].statement)


    # img_file = "C:/Users/thucnguyen/Downloads/FB Posts.png"
    # img_file = "C:/Users/thucnguyen/Downloads/z2154907105699_598b6d3a26a9aa817fc97c2c8079d261.jpg"
    # upload_url = ucode.upload_file(img_file, "thuc_test")
    # print(upload_url)
    # ucode_courses = {
    #     2: 42,
    #     3: 43,
    #     4: 44,
    #     5: 45,
    #     6: 46,
    #     7: 47,
    #     8: 48,
    #     9: 49,
    #     10: 50,
    #     11: 51
    # }
    # ucode_courses = {
    #     2: 46
    # }
    # for y, course_id in ucode_courses.items():
    #     iqsha(y, course_id)

    # create_chapters_mc1()

    # ucode = UCode("https://dev-api.ucode.vn/api", "72821b59462c5fdb552a049c1caed85c")
    # # problem_folder = "../../problems/domino_for_young"
    # problem_folder = "/home/thuc/projects/ucode/courses/course-py101/lesson2/c1_input/p13_chao_ban"
    # ucode_lesson_id = 172
    #
    # problem: Problem = ProblemService.load(problem_folder, load_testcase=True)
    # #
    # # print(problem)
    # #
    # print(len(problem.testcases))
    # for testcase in problem.testcases:
    #     print(testcase)

    # ucode.create_problem(lesson_id=172, problem=problem_folder)

    # beestar = Beestar()
    #
    # files = beestar.read_quizzes_files_from_folder(
    #     "/home/thuc/projects/ucode/content_crawler/data/beestar/*grade-4-math*_ans.html"
    # )
    # course_id = 17
    # # chappter_id = 413  # GT Math 2
    # # chappter_id = 630  # GT Math 5
    # chappter_id = 735
    # # chappter_id = 619  # problems
    #
    # ucode = UCode("https://dev-api.ucode.vn/api", "df12e0548fbba3e6f48f9df2b78c3df2")
    # # for file in files:
    # #     ucode.create_lesson_item_from_beestar_file(course_id=course_id, chapter_id=chappter_id, beestar_file=file)
    # file = "../../problems/bs/_bs_ans.html"
    # ucode.create_lesson_item_from_beestar_file(course_id=course_id, chapter_id=chappter_id, beestar_file=file)

    # problem_folder = "/home/thuc/projects/ucode/problemtools/problems/cs/Arcade_TheCore/p001_Intro_Gates__addTwoDigits"
    # problem = ProblemService.load(problem_folder, load_testcase=True)
    #
    # hr = HackerRank()
    # hr.login('thucngch', '15041985')
    # # prepare_testcases("/home/thuc/projects/ucode/problemtools/problems/cs/Arcade_TheCore/p001_Intro_Gates__addTwoDigits")
    # hr.upload_testcases(163975, "/home/thuc/projects/ucode/problemtools/problems/cs/Arcade_TheCore/p001_Intro_Gates__addTwoDigits/testcases_hackerrank.zip")
    # # hr_prob = hr.create_problem(problem)
    # # print(json.dumps(hr_prob))g
    #
    # "https://www.hackerrank.com/rest/administration/contests/46715/challenge?slug=add-two-digits&track_id=0&chapter_id=0&weight=100"
    #
    #
    # ucode = UCode("https://dev-api.ucode.vn/api", "df12e0548fbba3e6f48f9df2b78c3df2")
    # # print(problem)
    # # print(problem.name)
    # # print(len(problem.testcases))
    # #
    # # ucode.create_problem(lesson_id=None, problem=problem, question_type='code', lang="en")






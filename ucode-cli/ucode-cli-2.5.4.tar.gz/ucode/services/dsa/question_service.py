# coding=utf-8
import json
import logging

import requests

from ucode.helpers.misc import make_slug
from ucode.models.lesson import LessonType, QuizType
from ucode.models.question import QuestionType

__author__ = 'Dan'
_logger = logging.getLogger(__name__)


class QuestionService:
    def __init__(self, env='dev'):
        self._base_url, self._headers = self._get_ucode_info(env)

    @staticmethod
    def _get_ucode_info(env):
        if env == 'dev':
            return 'https://dev-api.ucode.vn/api', {'access-token': 'b269ec359ba979874f2d8180dcd5a638'}
        else:
            return 'https://api.ucode.vn/api', {'access-token': '371d83ff35571c02eb8609db2a48918a'}

    def create_contest(self, lesson_name, slug=None,
                       description="", content="", tags=None, is_graded_quiz=False, quiz_duration=None,
                       status="draft", is_free=True, visibility="public", ucoin=100):
        if not slug:
            slug = make_slug(lesson_name)
        data = {
            "name": lesson_name,
            "content_format": "markdown",
            "slug": slug,
            "is_free": is_free,
            "is_preview": False,
            "visibility": visibility,
            "ucoin": ucoin,
            "status": status,
            "type": LessonType.QUIZ.value,
            "quiz_type": QuizType.SUBMIT_ALL.value,
            "is_graded_quiz": is_graded_quiz
        }
        if quiz_duration:
            data['quiz_duration'] = quiz_duration
        if description:
            data['description'] = description
        if content:
            data['content'] = content
        if tags:
            data['tags'] = tags

        print(data)

        url = f"{self._base_url}/contests"
        print(url)
        response = requests.post(url, json=data, headers=self._headers)
        print(response.status_code)
        res = response.json()
        print(res)
        if not res['success']:
            raise Exception("Cannot create contest:" + json.dumps(res))
        return res['data'].get('id')

    def create_question(self, quiz_id, q_name, q_type, options, answers,
                        statement, statement_format="markdown", lang='vi',
                        status="draft", visibility="public", ucoin=10, score=10):
        data = {
            "name": q_name,
            "type": q_type,
            "statement": statement,
            "statement_format": statement_format,
            "statement_language": lang,
            "score": score,
            "status": status,
            "visibility": visibility,
            "ucoin": ucoin,
            "options": options,
            "answers": answers
        }

        url = f"{self._base_url}/lesson-item/{quiz_id}/question"
        response = requests.post(url, json=data, headers=self._headers)
        print(response.status_code)
        res = response.json()
        print(res)
        if not res['success']:
            raise Exception("Cannot create question:" + json.dumps(res))
        return res['data'].get('id')

    @staticmethod
    def parsing_file_markdown(in_file, out_file):
        quizzes = []
        with open(in_file, 'r', encoding="utf-8") as fi:
            questions = []
            quiz_title = ""
            line = fi.readline()
            while line:
                if line.startswith("## "):
                    if questions:
                        quizzes.append({'title': quiz_title,
                                        'questions': questions})
                    quiz_title = line[3:].split('::')[-1].strip()
                    questions = []
                    line = fi.readline()
                elif line.startswith("### "):
                    line = line[4:].split('::')
                    question_name = line[1].strip() if len(line) > 1 else ""
                    options = []
                    question_content = ""
                    line = fi.readline()
                    while line and not line.startswith("##"):
                        if line.startswith("- ["):
                            options.append({'text': line[5:].strip(),
                                            'is_correct': True if '[x]' in line or '[X]' in line else False,
                                            'text_type': 'markdown'})
                        else:
                            question_content += line
                        line = fi.readline()
                    question_ans = [str(i) for i in range(0, len(options)) if options[i].get('is_correct')]
                    if len(question_ans) == 1:
                        question_type = QuestionType.SINGLE_CHOICE.value
                    elif len(question_ans) > 1:
                        question_type = QuestionType.MULTI_CHOICE.value
                    else:
                        _logger.error(f'Cannot matching question type {question_name}')
                    questions.append({'name': question_name,
                                      'options': options,
                                      'answers': ','.join(question_ans),
                                      'type': question_type,
                                      'statement': question_content,
                                      'statement_format': 'markdown'})

                else:
                    line = fi.readline()

            if questions:
                quizzes.append({'name': quiz_title,
                                'questions': questions})

            print(json.dumps(quizzes))
            with open(out_file, 'w', encoding="utf-8", newline='') as f:
                f.write(json.dumps(quizzes))

    def create_quiz_from_json_file(self, file):
        with open(file, 'r', encoding="utf-8") as json_file:
            data = json.load(json_file)
            for quiz_info in data:
                quiz_id = self.create_contest(lesson_name=quiz_info.get('name'), tags=['Hour of Code'],
                                              is_graded_quiz=True, quiz_duration=3600)
                _logger.info(f"Created quiz {quiz_id}: {quiz_info.get('name')}")
                for info in quiz_info.get('questions'):
                    question_id = self.create_question(
                        quiz_id, q_name=info.get('name'), q_type=info.get('type'), statement=info.get('statement'),
                        options=json.dumps(info.get('options')), answers=info.get('answers'),
                        statement_format=info.get('statement_format'), status='published')
                    _logger.info(f"Created question {question_id}: {info.get('name')}")


if __name__ == "__main__":

    service = QuestionService('prod')
    # service.parsing_file_markdown('/home/thanh/Ucode/level1-sample.md',
    #                               '/home/thanh/Ucode/level1-sample.json')
    # service.parsing_file_markdown('/home/thanh/Ucode/level2-sample.md',
    #                               '/home/thanh/Ucode/level2-sample.json')
    # service.parsing_file_markdown('/home/thanh/Ucode/level3-sample.md',
    #                               '/home/thanh/Ucode/level3-sample.json')
    # service.parsing_file_markdown('/home/thanh/Ucode/level4-sample.md',
    #                               '/home/thanh/Ucode/level4-sample.json')
    # service.parsing_file_markdown('/home/thanh/Ucode/hour-of-code/contests/chinh_thuc/level3.md',
    #                               '/home/thanh/Ucode/hour-of-code/contests/chinh_thuc/level3.json')
    # service.parsing_file_markdown('/home/thanh/Ucode/hour-of-code/contests/chinh_thuc/level4.md',
    #                               '/home/thanh/Ucode/hour-of-code/contests/chinh_thuc/level4.json')
    # service.parsing_file_markdown('/home/thanh/Ucode/hour-of-code/contests/chinh_thuc/level1.md',
    #                               '/home/thanh/Ucode/hour-of-code/contests/chinh_thuc/level1.json')
    # service.parsing_file_markdown('/home/thanh/Ucode/hour-of-code/contests/chinh_thuc/level2.md',
    #                               '/home/thanh/Ucode/hour-of-code/contests/chinh_thuc/level2.json')
    # service.create_quiz_from_json_file('/home/thanh/Ucode/level1-sample.json')
    # service.create_quiz_from_json_file('/home/thanh/Ucode/level2-sample.json')
    # service.create_quiz_from_json_file('/home/thanh/Ucode/level3-sample.json')
    # service.create_quiz_from_json_file('/home/thanh/Ucode/level4-sample.json')
    # service.create_quiz_from_json_file('/home/thanh/Ucode/hour-of-code/contests/mixed.json')
    # service.create_quiz_from_json_file('/home/thanh/Ucode/hour-of-code/contests/chinh_thuc/level3.json')
    # service.create_quiz_from_json_file('/home/thanh/Ucode/hour-of-code/contests/chinh_thuc/level4.json')
    service.create_quiz_from_json_file('/home/thanh/Ucode/hour-of-code/contests/chinh_thuc/level1.json')
    service.create_quiz_from_json_file('/home/thanh/Ucode/hour-of-code/contests/chinh_thuc/level2.json')




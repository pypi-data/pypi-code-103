from bs4 import BeautifulSoup

from ucode.helpers.clog import CLog
from ucode.models.question import Question, QuestionType, QuestionOption
from ucode.ucode.ucode_srv import UCode


class GForm:
    def __init__(self):
        pass

    def parse_html(self, html_file_path):
        file = open(html_file_path, mode='r')
        raw = file.read()
        file.close()
        soup = BeautifulSoup(raw, 'html.parser')
        title = soup.select("div.exportFormTitle")[0].text.strip()
        print(title)

        question_tags = soup.select("div[role='list'] div.freebirdFormviewerViewNumberedItemContainer[role='listitem']")
        # print(*question_tags, sep="\n")
        questions = []
        for question_tag in question_tags:
            question = Question()
            statement_tags = question_tag.select("div.exportItemTitle")
            image_tag = question_tag.select("img")
            image_url = None
            if image_tag:
                image_url = image_tag[0]["src"]
            if statement_tags:
                statement_tag = statement_tags[0]
            else:
                print("Error:", statement_tags)
                continue
            require_tag = statement_tag.select("span.freebirdFormviewerComponentsQuestionBaseRequiredAsterisk")
            if require_tag:
                require_tag[0].decompose()
            statement = statement_tag.text
            if not statement.strip():
                continue
            question.statement = statement
            question.statement_format = "markdown"
            if image_url:
                question.statement += "\n\n"
                question.statement += f"![image]({image_url})"

            note_tag = question_tag.select("div[role='note']")
            score = 1
            if note_tag:
                note = note_tag[0].text
                if note.endswith("points"):
                    score = int("".join([c for c in note if "0" <=c <= "9"]))

            question.score = score
            # class:
            # freebirdFormviewerComponentsQuestionRadioRoot
            # freebirdFormviewerComponentsQuestionCheckboxRoot
            # freebirdFormviewerComponentsQuestionSelectRoot
            # freebirdFormviewerComponentsQuestionTextRoot
            # freebirdFormviewerComponentsQuestionTextRoot
            if question_tag.select("div.freebirdFormviewerComponentsQuestionRadioRoot"):
                question.type = QuestionType.SINGLE_CHOICE
                option_tags = question_tag.select("div.freebirdFormviewerComponentsQuestionRadioRoot")[0]\
                    .select("div.freebirdFormviewerComponentsQuestionRadioChoice div.docssharedWizToggleLabeledContent")
                question.options = []
                for option_tag in option_tags:
                    option = QuestionOption(text=option_tag.text, text_type="plaintext")
                    question.options.append(option)
            elif question_tag.select("div.freebirdFormviewerComponentsQuestionCheckboxRoot"):
                question.type = QuestionType.MULTI_CHOICE
                option_tags = question_tag.select("div.freebirdFormviewerComponentsQuestionCheckboxRoot")[0] \
                    .select("div.freebirdFormviewerComponentsQuestionCheckboxChoice div.docssharedWizToggleLabeledContent")
                question.options = []
                for option_tag in option_tags:
                    option = QuestionOption(text=option_tag.text, text_type="plaintext")
                    question.options.append(option)
            elif question_tag.select("div.freebirdFormviewerComponentsQuestionSelectRoot"):
                question.type = QuestionType.SINGLE_CHOICE
                option_tags = question_tag.select("div.freebirdFormviewerComponentsQuestionSelectRoot")[0] \
                    .select("div.quantumWizMenuPaperselectOptionList div.quantumWizMenuPaperselectOption span.exportContent")
                question.options = []
                for option_tag in option_tags[1:]: # skip first item "Choose"
                    option = QuestionOption(text=option_tag.text, text_type="plaintext")
                    question.options.append(option)
            elif question_tag.select("div.freebirdFormviewerComponentsQuestionTextRoot"):
                question.type = QuestionType.SHORT_ANSWER
            else:
                CLog.error(f"Question not supported: {question_tag}")
            print(f"'{question.statement}'", question.type, question.score, question.options)

            questions.append(question)

        return title, questions


def create_quiz_ucode(title, questions):
    course_id = 648
    chapter_id = 9453
    ucode = UCode(env="dev", domain="teko.ugrow.vn")
    quiz_id = ucode.create_lesson_item(course_id=course_id, chapter_id=chapter_id, lesson_name=title,
                                       type="quiz")
    ucode.create_problems(questions, quiz_id=quiz_id)


if __name__ == '__main__':
    gf = GForm()
    # path = "D:\\projects\\ucode\\ucode-cli\\ucode\\oj\\gform\\Quizz_ Communication with Charisma.html"
    # path = "D:\\projects\\ucode\\ucode-cli\\ucode\\oj\\gform\\Sample quiz.html"
    path = "D:\\projects\\ucode\\ucode-cli\\ucode\\oj\\gform\\Sample quiz_result.html"
    title, questions = gf.parse_html(path)
    print(title, len(questions))

    create_quiz_ucode(title, questions)

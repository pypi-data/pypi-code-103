# coding=utf-8
import json
__author__ = 'ThucNC'

from ucode.services.common import find_section


class LessonService:
    @staticmethod
    def read_quiz_from_md(quiz_md):
        lines = quiz_md.splitlines()
        lines.append("")
        lines.append("")

        questions = []
        question_indices, question_contents = find_section('^(#{3})\s+.*', lines, until_pattern='^(#{3})\s+.*',
                                                           skip_section_header=False)
        # print(question_contents)
        for q_i, q_c in question_contents.items():
            print("########################")
            question_title = q_c[0][3:].strip()
            q_c = q_c[1:]
            print("question_title:", question_title)

            hint_solution_i, hint_solution_c = find_section('^(#{4}).*', q_c, skip_section_header=False)
            question_hint = question_solution = None
            if hint_solution_i:
                q_c = q_c[:hint_solution_i[0]]
                for s_i, s_c in hint_solution_c.items():
                    if "hint" in s_c[0].lower():
                        question_hint = "\n".join(s_c[1:])
                    if "solution" in s_c[0].lower():
                        question_solution = "\n".join(s_c[1:])

            option_pattern = '^\s*-\s*\[(.{0,1})\] .*'
            option_i, option_c = find_section(option_pattern, q_c, until_pattern=option_pattern,
                                              skip_section_header=False)
            question_options = []
            if option_i:
                question_statement = "\n".join(q_c[:option_i[0]])
                for option_lines in option_c.values():
                    o_i = option_lines[0].find("]")
                    is_correct = "[x]" in option_lines[0][:o_i+1].lower().replace(" ", "")
                    option_lines[0] = option_lines[0][o_i+1:].lstrip()
                    option_text = "\n".join(option_lines).strip()
                    # print("Option:", option_text, is_correct)
                    question_options.append({"content": option_text, "is_correct": is_correct})
            else:
                question_statement = "\n".join(q_c)

            # print("question_statement:", question_statement)
            # print("question_options:", question_options)
            # print("hint:", question_hint)
            # print("solution:", question_solution)
            questions.append({
                "title": question_title,
                "statement": question_statement,
                "options": question_options,
                "hint": question_hint,
                "solution": question_solution,
            })

        return questions


if __name__ == "__main__":
    quiz_file = r"D:\projects\ucode\ucode-cli\problems\quiz\quiz.md"
    with open(quiz_file, encoding="utf-8") as f:
        quiz_md = f.read()

    quiz = LessonService.read_quiz_from_md(quiz_md)
    print(json.dumps(quiz, indent=2))

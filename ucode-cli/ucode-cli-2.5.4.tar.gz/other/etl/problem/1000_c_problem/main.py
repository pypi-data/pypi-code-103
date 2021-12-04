import codecs
import json
import re
import time

import requests

from ucode.models.problem import Problem
from ucode.services.dsa.problem_service import ProblemService

BASE_URL = "https://dev-api.ucode.vn/api"
ACCESS_TOKEN = "f0875cb3517009fee6c6962da5f9560b"


def _get_difficulty(num_of_prb, section):
    fixed = [
        [1, 73, 1.5, 2],
        [2, 108, 1.2, 1.2],
        [4, 113, 1.5, 1.5],
        [5, 300, 1.5, 2.5],
        [6, 418, 2, 3.5],
        [7, 564, 2, 3.5],
        [8, 610, 2, 3],
        [10, 669, 2, 3.5],
        [11, 685, 2, 3.5],
        [12, 714, 2, 3.5],
        [13, 745, 1, 2.5]]
    for score in fixed:
        if f"Chương {score[0]}" in section:
            pc = num_of_prb / score[1]
            return round(score[3], 1) if pc > 1 else round(score[2] + (score[3] - score[2]) * pc, 1)
    score = fixed[10]
    pc = num_of_prb / score[0]
    return round(score[3], 1) if pc > 1 else round(score[2] + (score[3] - score[2]) * pc, 1)


def download_source_code():
    rs = []
    file_path = "problems3.json"
    output_file_path = "problems3_with_source_code.json"
    with open(file_path, encoding="utf-8-sig") as json_file:
        prbs = json.load(json_file).get("Transformed by JSON-CSV.CO")
        count = 0
        for prb in prbs:
            count += 1
            prb = dict(prb)
            print(f"Downloading ...{count}")
            source_code = ''
            if prb.get("url").strip() != "n":
                code_res = requests.get(prb.get("url").strip() + "/raw.code")
                if code_res.status_code == 200:
                    source_code = code_res.text
            prb.update({"source_code": source_code})
            rs.append(prb)
    with codecs.open(output_file_path, 'a', 'utf-8') as out:
        out.write(json.dumps(rs))
        out.close()


def convert_to_ucode_problem_format():
    file_path = "problems3_with_source_code.json"
    with open(file_path, encoding="utf-8-sig") as json_file:
        prbs = json.load(json_file)
        num_of_prb = 0
        num_of_urs_prb = 0
        tags_lv0 = set()
        tags_lv1 = set()
        for prb in prbs:
            num_of_prb += 1
            problem = Problem(f"Bài tập số {num_of_prb}")
            problem.src_name = f"Bài tập số {num_of_prb}"
            problem.solution_lang = "c"
            # url and source_code
            if prb.get("url").strip() == "n":
                num_of_urs_prb += 1
                problem.src_url = ''
            else:
                problem.src_url = prb.get("url").strip()
            problem.solution = prb.get("source_code")
            # tag
            tags = prb.get("section").split("___")
            tag_lv0 = re.sub("Chương [0-9|:|\*|\(|\)| ]+", "", tags[0].strip()).lower()
            tags_lv0.add(tag_lv0)
            problem.tags.append(tag_lv0)
            if len(tags) > 1:
                tag_lv1 = tags[1].strip().lower()
                tags_lv1.add(tag_lv1)
                problem.tags.append(tag_lv1)
            # statement
            statement = re.sub("Bài [0-9|:|\*|\(|\)| ]+", "", prb.get("des").strip())
            statement[0].upper()
            problem.statement = statement
            # difficulty
            problem.difficulty = _get_difficulty(num_of_prb=num_of_prb, section=prb.get("section"))
            print(f"num {num_of_prb} {problem.difficulty}")
            ProblemService.save(problem=problem, base_folder="problem")
        json_file.close()
    print(f"{num_of_urs_prb} invalid problems/{num_of_prb} problems")
    print(f"{len(tags_lv0)} lv0_tag / {len(tags_lv1)} lv1_tag")
    print(tags_lv0)
    print(tags_lv1)


def call_api_create_snippet():
    file_path = "problems3_with_source_code.json"
    with open(file_path, encoding="utf-8-sig") as json_file:
        prbs = json.load(json_file)
        num_of_prb = 0
        for prb in prbs:
            num_of_prb += 1
            # if num_of_prb > 400:
            #     break
            # if num_of_prb < 397:
            #     continue
            # source_code
            source_code = prb.get("source_code")
            # tag
            problem_tags = []
            tags = prb.get("section").split("___")
            tag_lv0 = re.sub("Chương [0-9|:|\*|\(|\)| ]+", "", tags[0].strip()).lower()
            problem_tags.append(tag_lv0)
            if len(tags) > 1:
                tag_lv1 = tags[1].strip().lower()
                problem_tags.append(tag_lv1)
            # statement
            statement = re.sub("Bài [0-9|:|\*|\(|\)| ]+", "", prb.get("des").strip())
            statement[0].upper()
            # call api
            data = {
                "description": statement,
                "name": f"Bài tập số {num_of_prb}: {prb.get('section')}",
                "programming_language": "50",
                "source_code": source_code,
                "slug": f"bai-tap-so-{num_of_prb}",
                "tags": problem_tags,
                "input": "", "output": ""}
            res = requests.post(f"{BASE_URL}/snippet/", data=json.dumps(data),
                                headers={"content-type": "application/json", "charset": "UTF-8",
                                         "access-token": ACCESS_TOKEN})
            print(f"{num_of_prb}___{prb.get('url')}____{res.status_code}")
            time.sleep(0.05)


# download_source_code()
convert_to_ucode_problem_format()
# call_api_create_snippet()

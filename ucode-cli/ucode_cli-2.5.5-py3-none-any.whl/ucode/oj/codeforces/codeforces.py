import codecs
import copy
import pickle

import requests
from bs4 import BeautifulSoup
from ucode.helpers.clog import CLog
from ucode.models.problem import Problem, TestCase
from ucode.oj.codeforces.aes import AESModeOfOperation
from ucode.oj.codeforces.codeforces_helper import to_markdown
from ucode.services.dsa.problem_service import ProblemService


class Codeforces:
    def __init__(self):
        self.s = requests.session()
        self._cookies = {}
        self._headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
            'origin': "https://codeforces.com",
            'referer': "https://codeforces.com/enter",
            'sec-fetch-dest': "empty",
            'sec-fetch-mode': "cors",
            'sec-fetch-site': "same-origin",
            'x-requested-with': "XMLHttpRequest"
        }
        self.csrf = ''
        self.rcpc = ''
        self.evercookie = "67ano0cpxyd6bygc7w"
        self.bfaa = "a60708ec87a45f5b510d7ab2b81a9044"

    def gen_RCPC(self, url):
        if self.rcpc:
            return
        r = self.s.get(url)
        s = r.text
        # print(r.text)
        # , a, b, c
        L = s.find("a=toNumbers") + 13
        if L < 13:
            return
        R = s[L+20:].find('"') + L + 20
        sa = s[L:R]
        L = s.find("b=toNumbers") + 13
        R = s[L + 20:].find('"') + L + 20
        sb = s[L:R]
        L = s.find("c=toNumbers") + 13
        R = s[L + 20:].find('"') + L + 20
        sc = s[L:R]
        print("a, b, c:", sa, sb, sc)
        a = codecs.decode(sa, 'hex_codec')
        b = codecs.decode(sb, 'hex_codec')
        c = codecs.decode(sc, 'hex_codec')

        aes = AESModeOfOperation()
        rcpc = aes.decrypt(c, None, 2, a, aes.aes.keySize["SIZE_128"], b)

        rcpc_hex = ''
        for c in rcpc:
            code = ord(c)
            h = hex(code)[2:]
            if len(h) < 2:
                h = '0' + h
            rcpc_hex += h
        print("RCPC:", rcpc_hex)
        # self.rcpc = self._headers['cookie'] = f"RCPC={rcpc_hex}"
        self._cookies = {"RCPC": rcpc_hex}
        # self._headers['Set-Cookie'] = {"RCPC":rcpc_hex}

    def get_problem_list(self, page_index):
        url = f'https://codeforces.com/problemset/page/{page_index}'

        headers = copy.deepcopy(self._headers)
        r = self.s.get(url, headers=headers)

        raw = r.text
        # print(raw)

        soup = BeautifulSoup(raw, 'html.parser')
        self.csrf = soup.select('span.csrf-token')[0]['data-csrf']
        # print('CSRF:', self.csrf)

        pagination = soup.select('div.pagination > ul > li')
        last_page = pagination[-2]
        # print(last_page)
        last_page_index = int(last_page.select('span.page-index')[0]['pageindex'])
        if page_index>last_page_index:
            CLog.warn(f'Overpass last page: #{page_index}/{last_page_index}')
            return [], last_page_index
        CLog.info(f'Getting problem list from page: #{page_index}/{last_page_index}')

        problem_tags = soup.select('table.problems > tr')[1:] # remove header line
        # print(len(problem_tags))
        # print(problem_tags[0])

        problems = []
        for problem_tag in problem_tags:
            problem = Problem()
            pid = problem_tag.select('td.id a')[0]

            problem.src_id = pid.text.strip()
            problem.src_url = 'https://codeforces.com' + pid['href']

            ptitle = problem_tag.select('td')[1].select('div')[0]
            problem.name = ptitle.select('a')[0].text.strip()

            ptags = problem_tag.select('td')[1].select('div')[1].select('a')
            for ptag in ptags:
                tag = ptag.text.strip()
                problem.tags.append(tag)

            difficulty = problem_tag.select('td')[3].select('span')
            if difficulty:
                difficulty = difficulty[0].text.strip()
                difficulty = int(difficulty) ** 0.5
                dmax = 3800 ** 0.5
                dmin = 250 ** 0.5

                difficulty = (difficulty - dmin)/(dmax-dmin) * 10
            else:
                difficulty = 0

            problem.difficulty = difficulty

            submission_url = problem_tag.select('td')[4].select('a')
            if submission_url:
                problem.src_status_url = 'https://codeforces.com' + submission_url[0]['href']

            problems.append(problem)

            # print(problem.name)
            # print(problem.src_id)
            # print(problem.src_url)
            # print(problem.tags)
            # print(problem.difficulty)
            # break
        return problems, last_page_index

    def get_problem_from_url(self, url):
        problem = Problem()
        problem.src_id, problem.src_url, problem.src_status_url = Codeforces.parse(url)
        # print(problem.src_url)
        CLog.info("Getting problem from url: " + problem.src_url)
        url = problem.src_url
        self.gen_RCPC(url)
        headers = copy.deepcopy(self._headers)
        r = self.s.get(url, headers=headers, allow_redirects=True, cookies=self._cookies)
        raw = r.text
        soup = BeautifulSoup(raw, 'html.parser')
        problem_statement = soup.select('div.problem-statement')[0]
        print(problem_statement)

        title = problem_statement.select('div.title')[0]
        title.extract()
        title = title.text
        if title[1] == "." and 'A' <= title[0] <= 'Z':
            title = title[2:].strip()
        problem.src_name = problem.name = title

        limit_time = problem_statement.select('div.time-limit')[0]
        limit_time.select('div')[0].extract()
        problem.limit_time = int(''.join(c for c in limit_time.text if c in '0123456789')) * 1000

        limit_memory = problem_statement.select('div.memory-limit')[0]
        limit_memory.select('div')[0].extract()
        # problem.limit_memory = limit_memory.text
        problem.limit_memory = int(''.join(c for c in limit_memory.text if c in '0123456789'))

        input_type = problem_statement.select('div.input-file')[0]
        input_type.select('div')[0].extract()
        problem.input_type = input_type.text

        output_type = problem_statement.select('div.output-file')[0]
        output_type.select('div')[0].extract()
        problem.output_type = output_type.text

        if problem.input_type.strip() == 'standard input':
            problem.input_type = 'stdin'
        if problem.output_type.strip() == 'standard output':
            problem.output_type = 'stdout'

        problem_statement.select('div.header')[0].extract()

        input_format = problem_statement.select('div.input-specification')[0]
        input_format.select('div.section-title')[0].extract()
        problem.input_format = input_format.decode_contents()
        input_format.extract()

        output_format = problem_statement.select('div.output-specification')[0]
        output_format.select('div.section-title')[0].extract()
        problem.output_format = output_format.decode_contents()
        output_format.extract()

        sample_tests = problem_statement.select('div.sample-tests')[0]
        inputs = [t.decode_contents().replace("<br/>", "\n").strip() for t in sample_tests.select('div.input > pre')]
        outputs = [t.decode_contents().replace("<br/>", "\n").strip() for t in sample_tests.select('div.output > pre')]
        sample_tests.extract()

        for i in range(len(inputs)):
            # print("input: ", inputs[i])
            # print("output: ", outputs[i])
            testcase = TestCase(inputs[i], outputs[i], name=str(i+1))
            problem.testcases_sample.append(testcase)

        note = problem_statement.select('div.note')
        if note:
            note = note[0]
            note.select('div.section-title')[0].extract()
            # print(note)
            explanations = note.select('p')
            for i in range(len(inputs)):
                if i<len(explanations):
                    problem.testcases_sample[i].explanation = to_markdown(explanations[i].decode())
                    # print(problem.stock_testcases[i].explanation)

            note.extract()
            problem.testcases_sample_note = note.decode_contents()

        problem.statement = problem_statement.select('div:not([class])')[0].decode_contents()

        problem.difficulty = 0
        ptags = soup.select('div.sidebox div.roundbox span.tag-box')
        for ptag in ptags:
            tag = ptag.text.strip()
            if tag[0]=='*' and tag[1:].isdigit():
                problem.difficulty = Codeforces.normalize_difficulty(int(tag[1:]))
            else:
                problem.tags.append(tag)

        problem.statement = to_markdown(problem.statement)
        problem.testcases_sample_note = to_markdown(problem.testcases_sample_note)
        problem.input_format = to_markdown(problem.input_format)
        problem.output_format = to_markdown(problem.output_format)
        problem.constraints = 'See inline constraints in the input description'

        # print(problem.name, problem.limit_time, problem.limit_memory, problem.input_type,
        #       problem.output_type, problem.src_status_url, sep=' - ')
        CLog.info("Problem name: " + problem.name)
        # print('=====')
        # print(problem.statement)
        # print('=====')
        # print(problem.input_format)
        # print('=====')
        # print(problem.output_format)
        # print('=====')
        # print(problem.tags)
        # print('=====')
        # print(problem.difficulty)
        # print('=====')
        # for t in problem.testcases:
        #     print(t)
        #     print('----')

        # create new session
        self.s = requests.session()
        self.get_csrf()

        submissions_cpp = self.get_submission_list(problem, 'cpp.g++17')
        submissions_fpc = self.get_submission_list(problem, 'pas.fpc')
        submissions_py3 = self.get_submission_list(problem, 'python.3')

        problem.stock_testcases = []
        CLog.info("Getting best solutions...")
        CLog.info("    C++ solutions:     %s" % len(submissions_cpp))
        CLog.info("    FPC solutions:     %s" % len(submissions_fpc))
        CLog.info("    Python3 solutions: %s" % len(submissions_py3))
        if submissions_cpp:
            solution_cpp, testcases = self.get_solution(submissions_cpp[0], True)
            problem.solutions.append({'lang': '11.cpp', 'code': solution_cpp})
            for testcase in testcases:
                problem.stock_testcases.append(testcase)
            CLog.info("Getting all visible testcases...")
            CLog.info("    Total visible testcases: %s" % len(problem.stock_testcases))
            CLog.info("    Total sample testcases:  %s" % len(problem.testcases_sample))
        if submissions_fpc:
            solution_fpc, tmp = self.get_solution(submissions_fpc[0])
            problem.solutions.append({'lang':'pas', 'code': solution_fpc})
        if submissions_py3:
            submissions_py3, tmp = self.get_solution(submissions_py3[0])
            problem.solutions.append({'lang':'py', 'code': submissions_py3})

        # print("Solutions:", json.dumps(problem.solutions))

        # save_problem(dsa_problem, '../problems')

        return problem

    def get_submission_list(self, problem, language='anyProgramTypeForInvoker'):
        if not problem.src_status_url:
            return []
        frame_problem_index = problem.src_status_url[problem.src_status_url.rfind('/') + 1:]
        url = problem.src_status_url + "?order=BY_CONSUMED_TIME_ASC"
        headers = copy.deepcopy(self._headers)

        if not self.csrf:
            self.get_csrf()

        data = {
            'csrf_token': self.csrf,
            'frameProblemIndex': frame_problem_index,
            'action': 'setupSubmissionFilter',
            'comparisonType': 'NOT_USED',
            'verdictName': "OK",
            'programTypeForInvoker': language,
            # 'programTypeForInvoker': "anyProgramTypeForInvoker",
            # 'programTypeForInvoker': "pas.fpc",
            # 'programTypeForInvoker': "python.3",
            # 'programTypeForInvoker': "cpp.g++11",
            # 'programTypeForInvoker': "cpp.g++14",
            # 'programTypeForInvoker': "cpp.g++17",
            # 'programTypeForInvoker': "java8",
            # '_tta': 248
        }
        # print(data)
        # print(headers)
        CLog.info(f"Getting solution list from `{url}`")
        r = self.s.post(url, headers=headers, data=data, allow_redirects=True, cookies=self._cookies)
        #
        if r.status_code != 200:
            r = self.s.get(url, headers=headers, data=data, allow_redirects=True, cookies=self._cookies)
        print(r.status_code)
        # print(r.text)
        #
        # r = self.s.get(problem.src_status_url, headers=headers)

        raw = r.text
        # print("status url:", url)
        # print(raw)

        soup = BeautifulSoup(raw, 'html.parser')

        submissions = soup.select('table.status-frame-datatable > tr[data-submission-id]')
        # print(submissions)
        # print(len(submissions))
        # problem.solutions
        result = []
        for submit in submissions:
            submission_url = 'https://codeforces.com/' + submit.select('td')[0].select('a')[0]['href']
            submission_id = submit.select('td')[0].select('a')[0].text
            submission_problem = submit.select('td')[3].select('a')[0]['href']
            submission_language = submit.select('td')[4].text.strip()
            submission_status = submit.select('td')[5].select('span > span')[0].text.strip()
            submission_time = submit.select('td')[6].text.strip().replace('\xa0', ' ')
            submission_memory = submit.select('td')[7].text.strip().replace('\xa0', ' ')
            submission = {
                'url': submission_url,
                'id': submission_id,
                'problem': submission_problem,
                'lang': submission_language,
                'verdict': submission_language,
                'status': submission_status,
                'time': submission_time,
                'memory': submission_memory,
            }
            # print(submission)
            result.append(submission)
            # problem.solutions.append(submission)
        return result

    def get_solution(self, submission, get_test_cases=False):
        # submission_url = submission['url']
        print("get submission", submission)
        headers = copy.deepcopy(self._headers)
        # r = self.s.get(submission_url, headers=headers)
        # raw = r.text
        # soup = BeautifulSoup(raw, 'html.parser')
        # print(raw)
        # source_code = soup.select('pre#program-source-text')[0].text
        # print(source_code)
        data = {
                   'submissionId': submission['id'],
                   'csrf_token': self.csrf
               }
        url = "https://codeforces.com/data/submitSource"
        r = self.s.post(url, headers=headers, data=data, allow_redirects=True)
        print(self.s.cookies.get_dict())
        print(headers)
        print(data)
        print("solutoin", r.text)
        CLog.info(f"Getting solution detail from `{url}`")
        res = r.json()
        source_code = res['source']

        if not get_test_cases:
            return source_code, []

        # print(testcases)
        tesst_count = int(res['testCount'])
        testcases = []
        for t in range(tesst_count):
            input_data = res.get('input#%s' % (t + 1))
            output_data = res.get('answer#%s' % (t + 1))
            if not input_data or not output_data:
                continue
            if input_data.endswith('...') or output_data.endswith('...'):  # uncompleted test data
                continue
            testcases.append(TestCase(input_data.strip(), output_data.strip(), name=str(t + 1)))
            # print(testcases[-1])

        return source_code, testcases

    @staticmethod
    def parse(url):
        """
        For problem: https://codeforces.com/problemset/problem/1257/D, the url can be:
        - https://codeforces.com/problemset/problem/1257/D
        - http://codeforces.com/problemset/problem/1257/D
        - codeforces.com/problemset/problem/1257/D
        - 1257/D
        - 1257D
        :param url:
        :return:
        - refined url: https://codeforces.com/problemset/problem/1257/D
        - status url: https://codeforces.com/problemset/status/1257/problem/D
        """
        url = url.strip()
        status_url = url
        problem_id = ''
        if url.startswith('https://') or url.startswith('http://'):
            problem_id = url[url[:-2].rfind('/')+1:]
        elif url.startswith('codeforces.com'):
            url = "https://" + url
            problem_id = url[url[:-2].rindex('/') + 1:]
        else:
            problem_id = url
            if url.find('/')<0:
                problem_id = problem_id[:-1] + "/" + problem_id[-1]
            url = "https://codeforces.com/problemset/problem/" + problem_id

        status_url = "https://codeforces.com/problemset/status/%s/problem/%s" % (problem_id[:-2], problem_id[-1:])
        return problem_id, url, status_url

    @staticmethod
    def normalize_difficulty(original_difficulty):
        difficulty = original_difficulty ** 0.5
        dmax = 3800 ** 0.5
        dmin = 250 ** 0.5

        return (difficulty - dmin) / (dmax - dmin) * 10

    @staticmethod
    def original_difficulty(normalized_difficulty):
        normalized_difficulties = {Codeforces.normalize_difficulty(d): d for d in range(100, 4001, 100)}
        for k, v in normalized_difficulties.items():
            if abs(k-normalized_difficulty) < 0.001:
                return v

    def get_csrf(self):
        headers = copy.deepcopy(self._headers)
        r = self.s.get("https://codeforces.com/", headers=headers, cookies=self._cookies)
        raw = r.text
        soup = BeautifulSoup(raw, 'html.parser')
        self.csrf = soup.select('span.csrf-token')[0]['data-csrf']
        self._headers['x-csrf-token'] = self.csrf
        # print('CSRF:', self.csrf)

    def login(self, username, password):
        headers = copy.deepcopy(self._headers)
        r = self.s.get("https://codeforces.com/enter", headers=headers)
        # print(r.text)

        print("cookies:")
        for c in r.cookies:
            print(c.name, c.value)

        soup = BeautifulSoup(r.text, 'html.parser')
        csrf = soup.select('meta[name="X-Csrf-Token"]')[0]['content']
        self.csrf = csrf
        self._headers["x-csrf-token"] = csrf
        print("csrf: ", csrf)

        url = "https://codeforces.com/2fdcd78/ees?name=70a7c28f3de&cookie=evercookie_etag"
        r = self.s.get(url, headers=headers)
        print(r.text)
        print("evercookie_etag 1 status code:", r.status_code)
        print("res header:", r.headers)

        url = "https://codeforces.com/2fdcd78/ecs?name=70a7c28f3de&cookie=evercookie_cache"
        r = self.s.get(url, headers=headers)
        print(r.text)
        print("evercookie_cache 1 status code:", r.status_code)

        payload = {
            "bfaa": self.bfaa,
            "ftaa": "",
            "csrf_token": csrf
        }

        headers = copy.deepcopy(self._headers)
        # self.s.mount('https://codeforces.com', HTTP20Adapter())
        r = self.s.post("https://codeforces.com/data/empty", data=payload, headers=headers)
        print("data/empty 1 status code:", r.status_code)
        print("req headers:", headers)
        # dataraw = ""
        # for chunk in (r.iter_content()):
        #     print("chunk", chunk)
        # print(dataraw)
        print(r.text)
        # print("res headers:", r.headers)
        # for k in r.headers:
        #     print(k, ":", r.headers[k])
        print("cookies:")
        # for c in r.cookies:
        #     print(c.name, c.value)

        my_cookies = {
            "evercookie_png": self.evercookie,
            "evercookie_etag": self.evercookie,
            "evercookie_cache": self.evercookie
        }
        # my_cookie = requests.cookies.create_cookie(**self.s.cookies, **optional_args)
        requests.utils.add_dict_to_cookiejar(self.s.cookies, my_cookies)
        # self.s.cookies.set_cookie(my_cookie)
        print(self.s.cookies)

        url = "https://codeforces.com/2fdcd78/ees?name=70a7c28f3de&cookie=evercookie_etag"
        r = self.s.get(url, headers=headers)
        print("evercookie_etag 2 status code:", r.status_code)
        print(r.text)
        print("res header:", r.headers)

        url = "https://codeforces.com/2fdcd78/ecs?name=70a7c28f3de&cookie=evercookie_cache"
        r = self.s.get(url, headers=headers)
        print(r.text)
        print("evercookie_cache 2 status code:", r.status_code)
        print("res header:", r.headers)

        payload = {
            "bfaa": self.bfaa,
            "ftaa": self.evercookie,
            "csrf_token": csrf
        }

        r = self.s.post("https://codeforces.com/data/empty", data=payload, headers=headers)
        print("data/empty 2 status code:", r.status_code)
        print("req headers:", headers)
        print(r.text)

        url = "https://codeforces.com/enter"
        payload = {
            "bfaa": self.bfaa,
            "ftaa": self.evercookie,
            "action": "enter",
            "csrf_token": csrf,
            "handleOrEmail": username,
            "password": password
        }
        #
        r = self.s.post(url, data=payload, headers=headers)
        # print(r.text)
        print("status code:", r.status_code)
        # print("cookies:")
        # for c in r.cookies:
        #     print(c.name, c.value)
        print(pickle.dumps(self.s))

    def submit(self, contest_id, submitted_problem_index, program_type_id, source, tab_size=4):
        url = f"https://codeforces.com/problemset/submit?csrf_token={self.csrf}"
        payload = {
            "csrf_token": self.csrf,
            "bfaa": self.bfaa,
            "ftaa": self.evercookie,
            "action": "submitSolutionFormSubmitted",
            "contestId": contest_id,
            "submittedProblemIndex": submitted_problem_index,
            "programTypeId": program_type_id,
            "source": source,
            "tabSize": tab_size,
            "sourceFile": "",
            "_tta": 836,
        }
        my_cookies = {
            "lastOnlineTimeUpdaterInvocation": "1602201189155",
            "X-User-Sha1": "bbc325ea8f12e85b1e918dacdf8cb36016bfeabd"
        }
        # my_cookie = requests.cookies.create_cookie(**self.s.cookies, **optional_args)
        requests.utils.add_dict_to_cookiejar(self.s.cookies, my_cookies)
        print(self.s.cookies)
        headers = copy.deepcopy(self._headers)
        r = self.s.post(url, data=payload, headers=headers)
        print(r.text)
        print("status code:", r.status_code)
        print("cookies:")
        for c in r.cookies:
            print(c.name, c.value)


if __name__ == '__main__':
    cf = Codeforces()
    url = "https://codeforces.com/problemset/problem/268/A"
    url = "https://codeforces.com/problemset/problem/1593/E"
    # cf.gen_RCPC("e9ee4b03c1d0822987185d27bca23378", "188fafdbe0f87ef0fc2810d5b3e34705", "d047fb1e36224370a3f2cd7e9953c968")
    # cf.gen_RCPC(url)
    dsa_problem = cf.get_problem_from_url(url)
    #
    # print(dsa_problem.name)
    # for t in dsa_problem.testcases_sample:
    #     print(t)
    #
    ProblemService.save(dsa_problem, r"D:\projects\ucode\ucode-cli\problems", overwrite=True)




    # cf.login("thucnc", "15041985")
    # cf.submit(contest_id=4, submitted_problem_index="A", program_type_id=31, source="print('YES')")
    # problems, page_count = cf.get_problem_list(1)
    # CLog.info("Number of pages: %s" % page_count)
    #
    # for i in range(len(problems)):
    #     tags = ', '.join(problems[i].tags)
    #     print(f'#{i+1} - {problems[i].src_id} - {problems[i].name} - {problems[i].difficulty}'
    #           f' - {problems[i].src_url} - {tags}')
    #     break
    #
    # dsa_problem = cf.get_problem_detail(problems[4])

    # dsa_problem = cf.get_problem_from_url("https://codeforces.com/problemset/problem/1257/C")
    # dsa_problem = cf.get_problem_from_url("1268/B")
    # DsaProblem.save(dsa_problem, "../problems", overwrite=True)
    # print(dsa_problem)


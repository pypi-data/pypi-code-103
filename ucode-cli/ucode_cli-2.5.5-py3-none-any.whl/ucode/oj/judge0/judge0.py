# coding=utf-8
import json
import logging
import time
import urllib.parse
from enum import Enum

import requests

__author__ = 'ThucNC'

from ucode.helpers.misc import base64_encode, base64_decode

_logger = logging.getLogger(__name__)


class JudgeStatus(Enum):
    IN_QUEUE = 1
    PROCESSING = 2
    AC = 3
    WA = 4
    TLE = 5
    CPE = 6 # compilation error
    RTE = 100 # run time error 7-12
    SYS = 1000 # system error 13-14


class Judge0:
    def __init__(self, api_base_url, authen_token=None, author_token=None):
        self.base_url = api_base_url
        self.s = requests.session()
        self._headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/70.0.3538.77 Safari/537.36',
        }
        if authen_token:
            self._headers["X-Auth-Token"] = authen_token
        if author_token:
            self._headers["X-Auth-User"] = author_token

    def get_languages(self):
        url = urllib.parse.urljoin(self.base_url, f"/languages")

        response = requests.request("GET", url, headers=self._headers)
        print("status code: ", response.status_code)
        res = json.loads(response.text)
        print(json.dumps(res))
        return res

    def post_submission(self, language_id, source_code, input_data=None, expected_output=None, use_base64=False):
        url = urllib.parse.urljoin(self.base_url, f"/submissions")

        params = None

        if use_base64:
            params = {
                "base64_encoded": "true"
            }

            source_code = base64_encode(source_code)
            input_data = base64_encode(input_data)
            expected_output = base64_encode(expected_output)

        payload = {
            "language_id": language_id,
            "source_code": source_code
        }

        if input_data:
            payload["stdin"] = input_data
        if expected_output:
            payload["expected_output"] = expected_output

        print(json.dumps(payload))

        headers = {
            'content-type': "application/json",
            'accept': "application/json"
        }

        response = requests.request("POST", url, json=payload, headers=headers, params=params)
        print("request:", response.request.url)
        print("status code: ", response.status_code)
        res = json.loads(response.text)
        print(json.dumps(res))

        return res['token']

    def get_submission(self, submission_token, retry=1, interval=1.0, use_base64=False):
        url = urllib.parse.urljoin(self.base_url, f"/submissions/{submission_token}")

        res = None
        status = 1
        params = None
        if use_base64:
            params = {
                "base64_encoded": "true"
            }
        for i in range(retry):
            response = requests.request("GET", url, headers=self._headers, params=params)
            print("status code: ", response.status_code)
            res = json.loads(response.text)
            print(json.dumps(res))
            status = res['status']['id']
            if status not in [JudgeStatus.IN_QUEUE.value, JudgeStatus.PROCESSING.value]:
                break
            time.sleep(interval)

        if res and use_base64:
            if res.get('stdout'):
                res['stdout'] = base64_decode(res['stdout'])
            if res.get('stderr'):
                res['stderr'] = base64_decode(res['stderr'])
            if res.get('compile_output'):
                res['compile_output'] = base64_decode(res['compile_output'])
                # print(res['compile_output'])
        return res, status

    def get_submissions(self, page=1, per_page=10):
        url = urllib.parse.urljoin(self.base_url, f"/submissions")
        params = {
            "page": page,
            "per_page": per_page
        }
        response = requests.request("GET", url, params=params, headers=self._headers)

        print("status code: ", response.status_code)
        print("response: ", response.text)

    def judge(self, language_id, source_code, testcases: list, use_base64=False):
        """

        :param language_id:
        :param source_code:
        :param testcases: lsit of testcases  [{"id": "1", "input":"", "output":""}]
        :return: list of submission ["token1",]
        """
        url = urllib.parse.urljoin(self.base_url, f"/submissions/batch")

        submissions = []
        params = None

        for testcase in testcases:
            if use_base64:
                submissions.append({
                    "language_id": language_id,
                    "source_code": base64_encode(source_code),
                    "stdin": base64_encode(testcase['input']),
                    "expected_output": base64_encode(testcase['output'])
                })

                params = {
                    "base64_encoded": "true"
                }
            else:
                submissions.append({
                    "language_id": language_id,
                    "source_code": source_code,
                    "stdin": testcase['input'],
                    "expected_output": testcase['output']
                })

        payload = {
            "submissions": submissions
        }

        print("payload:", json.dumps(payload))
        headers = {
            'content-type': "application/json",
            'accept': "application/json"
        }

        response = requests.request("POST", url, json=payload, headers=headers, params=params)
        print("status code: ", response.status_code)
        res = json.loads(response.text)
        print(json.dumps(res))

        if isinstance(res, dict) and res.get("error"):
            raise Exception("Judge error: " + res['error'])

        return [t['token'] for t in res]

    def get_judge_result(self, submission_tokens, timeout=60, use_base64=False):
        """

        :param submissions: list of submission tokens ["token1", "token2]
        :return:
            list of result (order reserved): [{"status_id": 3, "time": "0.025", "memory": 6652, "stderr": null, "token": "token1"}]
        """
        result_dict = {}
        pending = set(submission_tokens)
        t0 = time.time()
        while True:
            if time.time() - t0 > timeout or not len(pending):
                break
            tokens = ",".join(list(pending))
            params = {
                "tokens": tokens,
                # stdout,time,memory,stderr,token,compile_output,message,status Example: stdout,stderr,status_id,language_id
                "fields": "token,stderr,status_id,time,memory,compile_output", # ,stdin,stdout,
                "base64_encoded": "true" if use_base64 else "false"
            }
            url = urllib.parse.urljoin(self.base_url, f"/submissions/batch")

            response = requests.request("GET", url, headers=self._headers, params=params)

            print("status code: ", response.status_code)
            res = json.loads(response.text)
            print(json.dumps(res))
            for submission_result in res['submissions']:
                status = submission_result['status_id']
                token = submission_result['token']
                result_dict[token] = submission_result
                if status not in [JudgeStatus.IN_QUEUE.value, JudgeStatus.PROCESSING.value]:
                    pending -= {token}
            if not len(pending):
                break
            time.sleep(1)

        if len(pending):
            CLog.warn("Still pending submissions: " + json.dumps(list(pending)))

        status_dict = dict()
        final_result = []
        for token in submission_tokens:
            res = result_dict[token]
            final_result.append(res)
            if res and use_base64:
                if res.get('stdin'):
                    res['stdin'] = base64_decode(res['stdin'])
                if res.get('stdout'):
                    res['stdout'] = base64_decode(res['stdout'])
                if res.get('stderr'):
                    res['stderr'] = base64_decode(res['stderr'])
                if res.get('compile_output'):
                    res['compile_output'] = base64_decode(res['compile_output'])
                    # print(res['compile_output'])
            status = res["status_id"]
            if status not in status_dict:
                status_dict[status] = 0
            status_dict[status] += 1
        print("Status report: \n", status_dict, "\n")
        return final_result


def test_submission():
    # judge0 = Judge0("http://61.28.235.48:8080/", author_token="YuI8p5PMsbiKXd7mqwHh1ax9smdxp5itgjPsfVFBt0Q")
    judge0 = Judge0("http://j2.ucode.vn", author_token="YuI8p5PMsbiKXd7mqwHh1ax9smdxp5itgjPsfVFBt0Q")
    # judge0 = Judge0("http://localhost:8080", author_token="YuI8p5PMsbiKXd7mqwHh1ax9smdxp5itgjPsfVFBt0Q")
    # judge0.get_languages()
    cpp_language_id = 54
    cpp_source_code = """#include <iostream>
using namespace std;

int main() {
  double a, b;
  cin >> a >> b
  cout << a + b;
}"""
    py3_language_id = 71
    py3_source_code = """a = float(input())
b = float(input())
print(a + b)"""

    stdin = "1.2\n2.3"
    exp_output = "3.5"
    submission_id = judge0.post_submission(py3_language_id, py3_source_code, stdin, exp_output)
    # submission_id = judge0.post_submission(cpp_language_id, cpp_source_code, stdin, exp_output, use_base64=True)
    submission_res, status = judge0.get_submission(submission_id, 10, 1.0, use_base64=True)
    print("Submission result:", status, "-", json.dumps(submission_res))
    # judge0.get_submissions(page=1, per_page=10)
    # judge0.get_submission("988b78d2-0bbd-42fb-8eb2-4e8aa4a7582a")


def test_judge():
    # judge0 = Judge0("http://localhost:8080", author_token="YuI8p5PMsbiKXd7mqwHh1ax9smdxp5itgjPsfVFBt0Q")
    judge0 = Judge0("https://j0.ucode.vn/", author_token="YuI8p5PMsbiKXd7mqwHh1ax9smdxp5itgjPsfVFBt0Q")
    py3_language_id = 71
    py3_source_code = """n = int(input())
s = 0
for i in range(1, n+1):
    s += i
print(s)"""

    testcases = [
        {"input": "5", "output": "15"},
        {"input": "105", "output": "5565"},
        {"input": "215", "output": "23220"},
        {"input": "336", "output": "56616"},
        {"input": "469", "output": "110215"},
        {"input": "615", "output": "189420"},
        {"input": "775", "output": "300700"},
        {"input": "951", "output": "452676"},
        {"input": "1144", "output": "654940"},
        {"input": "1356", "output": "920046"},
        {"input": "1589", "output": "1263255"},
        {"input": "1845", "output": "1702935"},
        {"input": "2126", "output": "2261001"},
        {"input": "2435", "output": "2965830"},
        {"input": "2774", "output": "3848925"},
        {"input": "3146", "output": "4950231"},
        {"input": "3555", "output": "6320790"},
        {"input": "4004", "output": "8018010"},
        {"input": "4497", "output": "10113753"},
        {"input": "5039", "output": "12698280"},
        {"input": "5635", "output": "15879430"},
        {"input": "6290", "output": "19785195"},
        {"input": "7010", "output": "24573555"},
        {"input": "7802", "output": "30439503"},
        {"input": "8673", "output": "37614801"},
        {"input": "9631", "output": "46382896"},
        {"input": "10684", "output": "57079270"},
        {"input": "11842", "output": "70122403"},
        {"input": "13115", "output": "86008170"},
        {"input": "14515", "output": "105349870"},
        {"input": "16055", "output": "128889540"},
        {"input": "17749", "output": "157522375"},
        {"input": "19612", "output": "192325078"},
        {"input": "21661", "output": "234610291"},
        {"input": "23914", "output": "285951655"},
        {"input": "26392", "output": "348282028"},
        {"input": "29117", "output": "423914403"},
        {"input": "32114", "output": "515670555"},
        {"input": "35410", "output": "626951755"},
        {"input": "39035", "output": "761885130"},
        {"input": "43022", "output": "925467753"},
        {"input": "47407", "output": "1123735528"},
        {"input": "52230", "output": "1364012565"},
        {"input": "57535", "output": "1655166880"},
        {"input": "63370", "output": "2007910135"},
        {"input": "69788", "output": "2435217366"},
        {"input": "76847", "output": "2952769128"},
        {"input": "84611", "output": "3579552966"},
        {"input": "93151", "output": "4338600976"},
        {"input": "102545", "output": "5257789785"},
        {"input": "112878", "output": "6370777881"},
        {"input": "124244", "output": "7718347890"},
        {"input": "136746", "output": "9349802631"},
        {"input": "150498", "output": "11324899251"},
        {"input": "165625", "output": "13715903125"},
        {"input": "182264", "output": "16610173980"},
        {"input": "200566", "output": "20113460461"},
        {"input": "220698", "output": "24353913951"},
        {"input": "242843", "output": "29486482746"},
        {"input": "267202", "output": "35698588003"},
        {"input": "293996", "output": "43216971006"},
        {"input": "323469", "output": "52316258715"},
        {"input": "355889", "output": "63328668105"},
        {"input": "391551", "output": "76656288576"},
        {"input": "430779", "output": "92785488810"},
        {"input": "473929", "output": "112304585485"},
        {"input": "521394", "output": "135926112315"},
        {"input": "573605", "output": "164511634815"},
        {"input": "631037", "output": "199104163203"},
        {"input": "694212", "output": "240965497578"},
        {"input": "763704", "output": "291622281660"},
        {"input": "840145", "output": "352922230585"},
        {"input": "924230", "output": "427101008565"},
        {"input": "1016723", "output": "516863337726"},
        {"input": "1118465", "output": "625482537345"},
        {"input": "1230381", "output": "756919317771"},
        {"input": "1353488", "output": "915965559816"},
        {"input": "1488905", "output": "1108419793965"},
        {"input": "1637863", "output": "1341298422316"},
        {"input": "1801716", "output": "1623091173186"},
        {"input": "1981954", "output": "1964071820035"},
        {"input": "2180215", "output": "2376669813220"},
        {"input": "2398302", "output": "2875927440753"},
        {"input": "2638197", "output": "3480043024503"},
        {"input": "2902081", "output": "4211038516321"},
        {"input": "3192353", "output": "5095560434481"},
        {"input": "3511652", "output": "6165851640378"},
        {"input": "3862880", "output": "7460922878640"},
        {"input": "4249230", "output": "9027979921065"},
        {"input": "4674215", "output": "10924145270220"},
        {"input": "5141698", "output": "13218531732451"},
        {"input": "5655929", "output": "15994769254485"},
        {"input": "6221583", "output": "19354050623736"},
        {"input": "6843802", "output": "23418816329503"},
        {"input": "7528242", "output": "28337217569403"},
        {"input": "8281126", "output": "34288528054501"},
        {"input": "9109298", "output": "41489659581051"},
        {"input": "10020287", "output": "50203080791328"},
        {"input": "11022374", "output": "60746369809125"},
        {"input": "12124669", "output": "73503805242115"},
        {"input": "13337193", "output": "88940365228221"},
        {"input": "14670969", "output": "107618673034965"},
        {"input": "16138122", "output": "130219498912503"},
        {"input": "17751990", "output": "157566583356045"},
        {"input": "19527244", "output": "190656638881390"},
        {"input": "21480023", "output": "230695704780276"},
        {"input": "23628079", "output": "279143070429160"},
        {"input": "25990940", "output": "337764494037270"},
        {"input": "28590087", "output": "408696551628828"},
        {"input": "31449148", "output": "494524470687526"},
        {"input": "34594115", "output": "598376413613670"},
        {"input": "38053578", "output": "724037418327831"},
        {"input": "41858987", "output": "876087417262578"},
        {"input": "46044936", "output": "1060068088644516"},
        {"input": "50649479", "output": "1282684886810460"},
        {"input": "55714476", "output": "1552051445834526"},
        {"input": "61285972", "output": "1877985212635378"},
        {"input": "67414617", "output": "2272365326335653"},
        {"input": "74156126", "output": "2749565548742001"},
        {"input": "81571785", "output": "3326978094829005"},
        {"input": "89729009", "output": "4025647572925545"},
        {"input": "98701955", "output": "4871038009761990"},
        {"input": "108572195", "output": "5893960817845110"},
        {"input": "119429459", "output": "7131697898231070"},
        {"input": "131372449", "output": "8629360243815025"},
        {"input": "144509738", "output": "10441532260669191"},
        {"input": "158960755", "output": "12634260894565390"},
        {"input": "174856873", "output": "15287463105097501"},
        {"input": "192342602", "output": "18497838368236503"},
        {"input": "211576903", "output": "22382393047324156"},
        {"input": "232734634", "output": "27082705047924295"},
        {"input": "256008138", "output": "32770083489117591"},
        {"input": "281608992", "output": "39651812328432528"},
        {"input": "309769931", "output": "47978705230757346"},
        {"input": "340746963", "output": "58054246567235166"},
        {"input": "374821698", "output": "70245652833212451"},
        {"input": "412303906", "output": "84997255657580371"},
        {"input": "453534334", "output": "102846696285178945"},
        {"input": "498887804", "output": "124444520739415110"},
        {"input": "548776621", "output": "150577890152477131"},
        {"input": "603654319", "output": "182199268725504040"},
        {"input": "664019786", "output": "220461138431752791"},
        {"input": "730421799", "output": "266758002592409100"},
        {"input": "803464013", "output": "322777210494764091"},
        {"input": "883810448", "output": "390560454438885576"},
        {"input": "972191526", "output": "472578182099200101"},
        {"input": "1069410711", "output": "571819634935468116"},
        {"input": "1176351814", "output": "691901795738721205"},
        {"input": "1293987027", "output": "837201213669142878"},
        {"input": "1423385761", "output": "1013013513020467441"},
        {"input": "1565724368", "output": "1225746399057361896"},
        {"input": "1722296835", "output": "1483153194786657030"},
        {"input": "1894526548", "output": "1794615421485661426"},
        {"input": "2083979232", "output": "2171484720745644528"},
        {"input": "2292377184", "output": "2627496578008073520"},
        {"input": "2521614931", "output": "3179270931381874846"},
        {"input": "2773776452", "output": "3846917904221742378"},
        {"input": "3051154125", "output": "4654770748777834875"},
        {"input": "3356269565", "output": "5632272698150779395"},
        {"input": "3691896549", "output": "6815050066105002975"},
        {"input": "4061086231", "output": "8246210689839435796"},
        {"input": "4467194881", "output": "9977915054649899521"},
        {"input": "4913914396", "output": "12073277348064979606"},
        {"input": "5405305862", "output": "14608665733588434453"},
        {"input": "5945836474", "output": "17676485690747294575"},
        {"input": "6540420147", "output": "21388547852911960878"},
        {"input": "7194462187", "output": "25880143083683642578"},
        {"input": "7913908431", "output": "31314973331083395096"},
        {"input": "8705299299", "output": "37891117946937595350"},
        {"input": "9575829253", "output": "45848252946093183631"},
        {"input": "10533412202", "output": "55476386313887950503"},
        {"input": "11586753445", "output": "67126427703403060735"},
        {"input": "12745428812", "output": "81222977807252580078"},
        {"input": "14019971715", "output": "98279803451710006470"},
        {"input": "15421968908", "output": "118918562507370340686"},
        {"input": "16964165820", "output": "143891460992710219110"},
        {"input": "18660582423", "output": "174108668192118566676"},
        {"input": "20526640686", "output": "210671488936338595641"},
        {"input": "22579304775", "output": "254912502072458552700"},
        {"input": "24837235272", "output": "308444127990759074628"},
        {"input": "27320958818", "output": "373217395381086457971"},
        {"input": "30053054718", "output": "451593048956577557121"},
        {"input": "33058360208", "output": "546427589837468081736"},
        {"input": "36364196247", "output": "661177384363346540628"},
        {"input": "40000615889", "output": "800024635769659938105"},
        {"input": "44000677495", "output": "968029810031500076260"},
        {"input": "48400745261", "output": "1171316070934307351691"},
        {"input": "53240819803", "output": "1417292446674378889306"},
        {"input": "58564901799", "output": "1714923861392539169100"},
        {"input": "64421391994", "output": "2075057873254514344015"},
        {"input": "70863531208", "output": "2510820027669026735236"},
        {"input": "77949884343", "output": "3038092234582513212996"},
        {"input": "85744872791", "output": "3676091605015258501236"},
        {"input": "94319360083", "output": "4448070843280466563486"},
        {"input": "103751296104", "output": "5382165721681818437460"},
        {"input": "114126425727", "output": "6512420524667286952128"},
        {"input": "125539068312", "output": "7880028836385270798828"},
        {"input": "138092975155", "output": "9534834893648770124590"},
        {"input": "151902272682", "output": "11537150223054292872903"},
        {"input": "167092499961", "output": "13959951771691938750741"},
    ]

    testcases = testcases[:5]#  + testcases[-50:]
    submissions = judge0.judge(py3_language_id, py3_source_code, testcases, use_base64=True)
    print("submissions:", submissions)
    # submissions = ['f188f851-9636-4ae7-930f-2cd10cf87bea', 'c25287fc-a1bc-4fb8-8914-12950b3fb3d4', '9d852256-9545-4b65-be4d-8f1250249bd6']
    submission_res = judge0.get_judge_result(submissions, 60, use_base64=True)
    print("Judge result:", json.dumps(submission_res))
    # judge0.get_submissions(page=1, per_page=10)
    # judge0.get_submission("988b78d2-0bbd-42fb-8eb2-4e8aa4a7582a")


if __name__ == "__main__":
    test_submission()
    # test_judge()
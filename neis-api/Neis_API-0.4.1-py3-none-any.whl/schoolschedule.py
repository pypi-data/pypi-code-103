import requests
from .exceptions import check_status_code

URL = "https://open.neis.go.kr/hub/SchoolSchedule"


def get_schedule_data(region_code=None, school_code=None, dght_crse_sc_nm=None, schul_crse_sc_nm=None,
                      date=None, start_date=None, end_date=None, pindex: int = 1, psize: int = 100):
    """
    신청주소: https://open.neis.go.kr/hub/SchoolSchedule
    신청제한횟수: 제한없음
    :param region_code: 시도교육청코드 (필수)
    :param school_code: 표준학교코드 (필수)
    :param dght_crse_sc_nm: 주야과정명
    :param schul_crse_sc_nm: 학교과정명
    :param date: 학사일자
    :param start_date: 학사시작일자
    :param end_date: 학사종료일자
    :param pindex: 페이지 위치
    :param psize: 페이지 당 신청 숫자 (필수)
    :return: 검색된 모든 학교 (필수)
    """

    params = {
        "Type": "json",
        "pIndex": pindex,
        "pSize": psize,
        "ATPT_OFCDC_SC_CODE": region_code,
        "SD_SCHUL_CODE": school_code,
        "DGHT_CRSE_SC_NM": dght_crse_sc_nm,
        "SCHUL_CRSE_SC_NM": schul_crse_sc_nm,
        "AA_YMD": date,
        "AA_FROM_YMD": start_date,
        "AA_TO_YMD": end_date
    }

    res = requests.get(url=URL, params=params, verify=False, json=True)
    res.encoding = "UTF-8"
    request_json = res.json()

    try:
        status_code = request_json["SchoolSchedule"][0]["head"][1]["RESULT"]["CODE"]
    except KeyError:
        status_code = request_json["RESULT"]["CODE"]

    check_status_code(status_code)

    return tuple(SchoolSchedule(data) for data in request_json["SchoolSchedule"][1]["row"])


class SchoolSchedule:
    def __init__(self, schedule_data):
        self.data = schedule_data

    @property
    def region_code(self):
        """
        :return: 시도교육청코드
        """
        return self.data["ATPT_OFCDC_SC_CODE"]

    @property
    def region_name(self):
        """
        :return: 시도교육청명
        """
        return self.data["ATPT_OFCDC_SC_NM"]

    @property
    def school_code(self):
        """
        :return: 표준학교코드
        """
        return self.data["SD_SCHUL_CODE"]

    @property
    def school_name(self):
        """
        :return: 학교명
        """
        return self.data["SCHUL_NM"]

    @property
    def year(self):
        """
        :return: 학년도
        """
        return self.data["AY"]

    @property
    def dght_crse_sc_nm(self):
        """
        :return: 주야과정명
        """
        return self.data["DGHT_CRSE_SC_NM"]

    @property
    def schul_crse_sc_nm(self):
        """
        :return: 학교과정명
        """
        return self.data["SCHUL_CRSE_SC_NM"]

    @property
    def sbtr_dd_sc_nm(self):
        """
        :return: 수업공제일명
        """
        return self.data["SBTR_DD_SC_NM"]

    @property
    def date(self):
        """
        :return: 행사일자
        """
        return self.data["AA_YMD"]

    @property
    def event_name(self):
        """
        :return: 행사명
        """
        return self.data["EVENT_NM"]

    @property
    def event_info(self):
        """
        :return: 행사내용
        """
        return self.data["EVENT_CNTNT"]

    @property
    def event_grades(self):
        grades = (self.data["ONE_GRADE_EVENT_YN"],
                  self.data["TW_GRADE_EVENT_YN"],
                  self.data["THREE_GRADE_EVENT_YN"],
                  self.data["FR_GRADE_EVENT_YN"],
                  self.data["FIV_GRADE_EVENT_YN"],
                  self.data["SIX_GRADE_EVENT_YN"])

        events = dict(zip(
            (1, 2, 3, 4, 5, 6),
            map(lambda x: True if x == "Y" else False, grades)
        ))
        return events

    @property
    def laste_update_date(self):
        """
        :return: 수정일
        """
        return self.data["LOAD_DTM"]

import requests
from .exceptions import check_status_code

URL = "https://open.neis.go.kr/hub/mealServiceDietInfo"


def get_meal_data(region_code, school_code, meal_code=None, date=None,
                  start_date=None, end_date=None, pindex: int = 1, psize: int = 100):
    """
    신청주소: https://open.neis.go.kr/hub/mealServiceDietInfo
    신청제한횟수: 제한없음
    :param region_code:시도교육청코드 (필수)
    :param school_code:표준학교코드 (필수)
    :param meal_code:식사코드
    :param date:급식일자
    :param start_date:급식시작일자
    :param end_date: 급식종료일자
    :param pindex:페이지 위치
    :param psize:페이지 당 신청 숫자
    :return:검색된 모든 급식
    """

    params = {
        "Type": "json",
        "pIndex": pindex,
        "pSize": psize,
        "ATPT_OFCDC_SC_CODE": region_code,
        "SD_SCHUL_CODE": school_code,
        "MMEAL_SC_CODE": meal_code,
        "MLSV_YMD": date,
        "MLSV_FROM_YMD": start_date,
        "MLSV_TO_YMD": end_date
    }

    res = requests.get(url=URL, params=params, verify=False, json=True)
    res.encoding = "UTF-8"
    request_json = res.json()

    try:
        status_code = request_json["mealServiceDietInfo"][0]["head"][1]["RESULT"]["CODE"]
    except KeyError:
        status_code = request_json["RESULT"]["CODE"]

    check_status_code(status_code)

    return tuple(SchoolMeal(data) for data in request_json["mealServiceDietInfo"][1]["row"])


class SchoolMeal:
    def __init__(self, meal_data):
        self.data = meal_data

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
    def meal_code(self):
        """
        :return: 식사코드
        """
        return self.data["MMEAL_SC_CODE"]

    @property
    def meal_name(self):
        """
        :return: 식사명
        """
        return self.data["MMEAL_SC_NM"]

    @property
    def date(self):
        """
        :return: 급식일자
        """
        return self.data["MLSV_YMD"]

    @property
    def servings(self):
        """
        :return: 급식인원수
        """
        return self.data["MLSV_FGR"]

    @property
    def dish_name(self):
        """
        :return: 요리명
        """
        return self.data["DDISH_NM"].replace("<br/>", "\n")

    @property
    def org_info(self):
        """
        :return: 원산지정보
        """
        return self.data["ORPLC_INFO"].replace("<br/>", "\n")

    @property
    def cal_info(self):
        """
        :return: 칼로리정보
        """
        return self.data["CAL_INFO"]

    @property
    def ntr_info(self):
        """
        :return: 영양정보
        """
        return self.data["NTR_INFO"].replace("<br/>", "\n")

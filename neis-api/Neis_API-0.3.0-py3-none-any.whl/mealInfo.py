import requests
from exceptions import *

URL = "https://open.neis.go.kr/hub/mealServiceDietInfo"


def get_meal_data(atpt_ofcdc_sc_code, sd_schul_code, mmeal_sc_code=None, mlsv_ymd=None,
                  mlsv_from_ymd=None, mlsv_to_ymd=None, pindex: int = 1, psize: int = 100):
    """
    신청주소: https://open.neis.go.kr/hub/mealServiceDietInfo
    신청제한횟수: 제한없음
    :param atpt_ofcdc_sc_code:시도교육청코드 (필수)
    :param sd_schul_code:표준학교코드 (필수)
    :param mmeal_sc_code:식사코드
    :param mlsv_ymd:급식일자
    :param mlsv_from_ymd:급식시작일자
    :param mlsv_to_ymd: 급식종료일자
    :param pindex:페이지 위치 (필수)
    :param psize:페이지 당 신청 숫자 (필수)
    :return:검색된 모든 급식
    """

    params = {
        "Type": "json",
        "pIndex": pindex,
        "pSize": psize,
        "ATPT_OFCDC_SC_CODE": atpt_ofcdc_sc_code,
        "SD_SCHUL_CODE": sd_schul_code,
        "MMEAL_SC_CODE": mmeal_sc_code,
        "MLSV_YMD": mlsv_ymd,
        "MLSV_FROM_YMD": mlsv_from_ymd,
        "MLSV_TO_YMD": mlsv_to_ymd
    }

    res = requests.get(url=URL, params=params, verify=False, json=True)
    res.encoding = "UTF-8"
    request_json = res.json()

    try:
        status_code = request_json["mealServiceDietInfo"][0]["head"][1]["RESULT"]["CODE"]
    except KeyError:
        status_code = request_json["RESULT"]["CODE"]

    if status_code == "ERROR-300":
        raise Error300()
    elif status_code == "ERROR-290":
        raise Error290()
    elif status_code == "ERROR-333":
        raise Error333()
    elif status_code == "ERROR-336":
        raise Error336()
    elif status_code == "ERROR-337":
        raise Error337()
    elif status_code == "ERROR-500":
        raise Error500()
    elif status_code == "ERROR-600":
        raise Error600()
    elif status_code == "ERROR-601":
        raise Error601()
    elif status_code == "INFO-300":
        raise Info300()
    elif status_code == "INFO-200":
        raise Info200()

    return tuple(SchoolMeal(data) for data in request_json["mealServiceDietInfo"][1]["row"])


class SchoolMeal:
    def __init__(self, meal_data):
        self.data = meal_data

    @property
    def atpt_ofcdc_sc_code(self):
        """
        :return: 시도교육청코드
        """
        return self.data["ATPT_OFCDC_SC_CODE"]

    @property
    def atpt_ofcdc_sc_nm(self):
        """
        :return: 시도교육청명
        """
        return self.data["ATPT_OFCDC_SC_NM"]

    @property
    def sd_schul_code(self):
        """
        :return: 표준학교코드
        """
        return self.data["SD_SCHUL_CODE"]

    @property
    def schul_nm(self):
        """
        :return: 학교명
        """
        return self.data["SCHUL_NM"]

    @property
    def mmeal_sc_code(self):
        """
        :return: 식사코드
        """
        return self.data["MMEAL_SC_CODE"]

    @property
    def mmeal_sc_nm(self):
        """
        :return: 식사명
        """
        return self.data["MMEAL_SC_NM"]

    @property
    def mlsv_ymd(self):
        """
        :return: 급식일자
        """
        return self.data["MLSV_YMD"]

    @property
    def mlsv_fgr(self):
        """
        :return: 급식인원수
        """
        return self.data["MLSV_FGR"]

    @property
    def ddish_nm(self):
        """
        :return: 요리명
        """
        return self.data["DDISH_NM"].replace("<br/>", "\n")

    @property
    def orplc_info(self):
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

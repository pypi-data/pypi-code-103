import requests
from exceptions import *

URL = "https://open.neis.go.kr/hub/schoolInfo"


def get_school_data(atpt_ofcdc_sc_code=None, sd_schul_code=None, schul_nm=None, schul_knd_sc_nm=None,
                    lctn_sc_nm=None,fond_sc_nm=None, pindex: int = 1, psize: int = 100):
    """
    신청주소: https://open.neis.go.kr/hub/schoolInfo
    신청제한횟수: 제한없음
    :param atpt_ofcdc_sc_code: 시도교육청코드
    :param sd_schul_code: 표준학교코드
    :param schul_nm: 학교명
    :param schul_knd_sc_nm: 학교종류명
    :param lctn_sc_nm: 소재지명
    :param fond_sc_nm: 설립명
    :param pindex: 페이지 위치
    :param psize: 페이지 당 신청 숫자 (필수)
    :return: 검색된 모든 학교 (필수)
    """

    params = {
        "Type": "json",
        "pIndex": pindex,
        "pSize": psize,
        "ATPT_OFCDDC_SC_CODE": atpt_ofcdc_sc_code,
        "SD_SCHUL_CODE": sd_schul_code,
        "SCHUL_NM": schul_nm,
        "SCHUL_KND_SC_NM": schul_knd_sc_nm,
        "LCTN_SC_NM": lctn_sc_nm,
        "FOND_SC_NM": fond_sc_nm,
    }

    res = requests.get(url=URL, params=params, verify=False, json=True)
    res.encoding = "UTF-8"
    request_json = res.json()

    try:
        status_code = request_json["schoolInfo"][0]["head"][1]["RESULT"]["CODE"]
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

    return tuple(SchoolInfo(data) for data in request_json["schoolInfo"][1]["row"])


class SchoolInfo:
    def __init__(self, school_data):
        self.data = school_data

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
    def eng_schul_nm(self):
        """
        :return: 영문학교명
        """
        return self.data["ENG_SCHUL_NM"]

    @property
    def schul_knd_sc_nm(self):
        """
        :return: 학교종류명
        """
        return self.data["SCHUL_KND_SC_NM"]

    @property
    def lctn_sc_nm(self):
        """
        :return: 소재지명
        """
        return self.data["LCTN_SC_NM"]

    @property
    def ju_org_nm(self):
        """
        :return: 관할조직명
        """
        return self.data["JU_ORG_NM"]

    @property
    def fond_sc_nm(self):
        """
        :return: 설립명
        """
        return self.data["FOND_SC_NM"]

    @property
    def org_rdnzc(self):
        """
        :return: 도로명우편번호
        """
        return self.data["ORG_RDNZC"]

    @property
    def org_rdnma(self):
        """
        :return: 도로명주소
        """
        return self.data["ORF_RDNMA"]

    @property
    def org_rdnda(self):
        """
        :return: 도로명상세주소
        """
        return self.data["ORG_RDNDA"]

    @property
    def org_telno(self):
        """
        :return: 전화번호
        """
        return self.data["ORG_TELNO"]

    @property
    def hmpg_adres(self):
        """
        :return: 홈페이지주소
        """
        return self.data["HMPG_ADRES"]

    @property
    def coedu_sc_nm(self):
        """
        :return: 남녀공학구분명
        """
        return self.data["COEDU_SC_NM"]

    @property
    def org_faxno(self):
        """
        :return: 팩스번호
        """
        return self.data["ORG_FAXNO"]

    @property
    def hs_sc_nm(self):
        """
        :return: 고등학교구분명
        """
        return self.data["HS_SC_NM"]

    @property
    def indst_specl_ccccl_exst_yn(self):
        """
        :return: 산업체특별학급존재여부
        """
        return self.data["INDST_SPECL_CCCCL_EXST_YN"]

    @property
    def hs_gnrl_busns_sc_nm(self):
        """
        :return: 고등학교일반실업구분명
        """
        return self.data["HS_GNRL_BUSNS_SC_NM"]

    @property
    def spcly_purps_hs_ord_nm(self):
        """
        :return: 특수목적고등학교계열명
        """
        return self.data["SPCLY_PURPS_HS_ORD_NM"]

    @property
    def ene_bfe_sehf_sc_nm(self):
        """
        :return: 입시전후기구분명
        """
        return self.data["ENE_BFE_SEHF_SC_NM"]

    @property
    def dght_sc_nm(self):
        """
        :return: 주야구분명
        """
        return self.data["DGHT_SC_NM"]

    @property
    def fond_ymd(self):
        """
        :return: 설립일자
        """
        return self.data["FOND_YMD"]

    @property
    def foas_memrd(self):
        """
        :return: 개교기념일
        """
        return self.data["FOAS_MEMRD"]

    @property
    def load_dtm(self):
        """
        :return: 수정일
        """
        return self.data["LOAD_DTM"]


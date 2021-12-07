import requests
from .exceptions import check_status_code

URL = "https://open.neis.go.kr/hub/schoolInfo"


def get_school_data(region_code=None, school_code=None, school_name=None, school_type=None,
                    location_name=None, founding_name=None, pindex: int = 1, psize: int = 100):
    """
    신청주소: https://open.neis.go.kr/hub/schoolInfo
    신청제한횟수: 제한없음
    :param region_code: 시도교육청코드
    :param school_code: 표준학교코드
    :param school_name: 학교명
    :param school_type: 학교종류명
    :param location_name: 소재지명
    :param founding_name: 설립명
    :param pindex: 페이지 위치
    :param psize: 페이지 당 신청 숫자 (필수)
    :return: 검색된 모든 학교 (필수)
    """

    params = {
        "Type": "json",
        "pIndex": pindex,
        "pSize": psize,
        "ATPT_OFCDDC_SC_CODE": region_code,
        "SD_SCHUL_CODE": school_code,
        "SCHUL_NM": school_name,
        "SCHUL_KND_SC_NM": school_type,
        "LCTN_SC_NM": location_name,
        "FOND_SC_NM": founding_name,
    }

    res = requests.get(url=URL, params=params, verify=False, json=True)
    res.encoding = "UTF-8"
    request_json = res.json()

    try:
        status_code = request_json["schoolInfo"][0]["head"][1]["RESULT"]["CODE"]
    except KeyError:
        status_code = request_json["RESULT"]["CODE"]

    check_status_code(status_code)

    return tuple(SchoolInfo(data) for data in request_json["schoolInfo"][1]["row"])


class SchoolInfo:
    def __init__(self, school_data):
        self.data = school_data

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
    def en_school_name(self):
        """
        :return: 영문학교명
        """
        return self.data["ENG_SCHUL_NM"]

    @property
    def school_type(self):
        """
        :return: 학교종류명
        """
        return self.data["SCHUL_KND_SC_NM"]

    @property
    def location_name(self):
        """
        :return: 소재지명
        """
        return self.data["LCTN_SC_NM"]

    @property
    def org_name(self):
        """
        :return: 관할조직명
        """
        return self.data["JU_ORG_NM"]

    @property
    def founding_name(self):
        """
        :return: 설립명
        """
        return self.data["FOND_SC_NM"]

    @property
    def zip_code(self):
        """
        :return: 도로명우편번호
        """
        return self.data["ORG_RDNZC"]

    @property
    def address(self):
        """
        :return: 도로명주소
        """
        return self.data["ORF_RDNMA"]

    @property
    def address_detail(self):
        """
        :return: 도로명상세주소
        """
        return self.data["ORG_RDNDA"]

    @property
    def number(self):
        """
        :return: 전화번호
        """
        return self.data["ORG_TELNO"]

    @property
    def school_lnk(self):
        """
        :return: 홈페이지주소
        """
        return self.data["HMPG_ADRES"]

    @property
    def coedu(self):
        """
        :return: 남녀공학구분명
        """
        return self.data["COEDU_SC_NM"]

    @property
    def fax_number(self):
        """
        :return: 팩스번호
        """
        return self.data["ORG_FAXNO"]

    @property
    def high_sch_name(self):
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
    def founded_date(self):
        """
        :return: 설립일자
        """
        return self.data["FOND_YMD"]

    @property
    def sch_avsry(self):
        """
        :return: 개교기념일
        """
        return self.data["FOAS_MEMRD"]

    @property
    def laste_update_date(self):
        """
        :return: 수정일
        """
        return self.data["LOAD_DTM"]

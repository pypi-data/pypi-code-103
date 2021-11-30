__all__ = ['mealInfo', 'schoolInfo']

from mealInfo import *
from schoolInfo import *

class Region:
    """
    SEOUL : B10\n
    BUSAN : C10\n
    DAEGU : D10\n
    INCHEON : E10\n
    GWANGJU : F10\n
    DAEJEON : G10\n
    ULSAN : H10\n
    SEJONG : I10\n
    GYEONGGI : J10\n
    GANGWON : K10\n
    CHUNGBUK : M10\n
    CHUNGNAM : N10\n
    JEONBUK : P10\n
    JEONNAM : Q10\n
    GYEONGBUK : R10\n
    GYEONGNAM : S10\n
    JEJU : T10\n
    FORIENGER : V10\n
    """
    SEOUL = "B10"
    BUSAN = "C10"
    DAEGU = "D10"
    INCHEON = "E10"
    GWANGJU = "F10"
    DAEJEON = "G10"
    ULSAN = "H10"
    SEJONG = "I10"
    GYEONGGI = "J10"
    GANGWON = "K10"
    CHUNGBUK = "M10"
    CHUNGNAM = "N10"
    JEONBUK = "P10"
    JEONNAM = "Q10"
    GYEONGBUK = "R10"
    GYEONGNAM = "S10"
    JEJU = "T10"
    FORIENGER = "V10"


class School:
    def __init__(self, region_code, school_code):
        self._region_code = region_code
        self._code = school_code
        
        school_info = self.get_school_info()
        self._region_name = school_info.atpt_ofcdc_sc_nm
        self._name = school_info.schul_nm

    @classmethod
    def find(cls, region_code, school_name):
        school_data = get_school_data(atpt_ofcdc_sc_code=region_code, schul_nm=school_name)[0]
        return School(region_code=region_code, school_code=school_data.sd_schul_code)

    @property
    def region_code(self):
        return self._region_code
    
    @property
    def code(self):
        return self._code
    
    @property
    def name(self):
        return self._name

    def __str__(self):
        return self._name

    def get_meal_info(self, year, month, day):
        date = f"{year}{month:02}{day:02}"
        return mealInfo.get_meal_data(atpt_ofcdc_sc_code=self.region_code,
                                      sd_schul_code=self.code,
                                      mlsv_ymd=date)[0]

    def get_school_info(self):
        return schoolInfo.get_school_data(atpt_ofcdc_sc_code=self.region_code, sd_schul_code=self.code)[0]

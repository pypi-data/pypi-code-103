from typing import List
from typing import Dict
from typing import Union

class SymptomsCheckboxes(object):
        def __init__(self, symptoms: List[bool], other_symptom: bool, description_other: str) -> None:
            self.__symptoms: List[bool] = symptoms
            self.__other_symptom: bool = other_symptom
            self.__description: str = description_other
            self.symptoms_names: List[str] = ["FEBRE",
                                    "TOSSE",
                                    "CALAFRIO",
                                    "DISPNEIA",
                                    "GARGANTA",
                                    "ARTRALGIA",
                                    "MIALGIA",
                                    "CONJUNTIV",
                                    "CORIZA",
                                    "DIARREIA",
                                    "OUTRO_SIN",
                                    "OUTRO_DES"]
        
        def get_symptoms(self) -> List[bool]:
            return self.__symptoms
        
        def get_other_symptom(self) -> bool:
            return self.__other_symptom
        
        def get_description(self) -> str:
            return self.__description
        

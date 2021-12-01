from datetime import date
from typing import List
from typing import Dict
from typing import Union


from breath_api_interface.service_interface import Service
from .symptoms_checkboxes import SymptomsCheckboxes


class RegisterSymptoms(Service):
        
    def run():
        pass

    def processSymptomsRegister(self) -> None:
        today = date.today()
        today_str = today.strftime("%d/%m/%Y")
        day = int(today_str[:2])
        month = int(today_str[3:5])
        year = int(today_str[6:])

        # TODO: IMPLEMENTAR COLETAR CIDADE
        city = "Campinas"

        # TODO: IMPLEMENTAR GERAR/OBTER CODIGO DO USUARIO
        cod = 12345

        # TODO: IMPLEMENTAR COLETA DOS DADOS PELO FORMULARIO
        symptoms = self.processSymptomsInput(getInputExample())

        # TODO: chamar servicos

    
    def processSymptomsInput(self, user_input: SymptomsCheckboxes) -> Dict[str, Union[str, int]]:
        symptoms_names = user_input.symptoms_names
        symptoms_values = user_input.get_symptoms()
        symptoms_dict = dict()
        for i in range(len(symptoms_values)):
            symptoms_dict[symptoms_names[i]] = symptoms_values[i]

        other_symptom = user_input.get_other_symptom()
        description = user_input.get_description()

        if (other_symptom == 0 or description == ""):
            symptoms_dict[symptoms_names[-2]] = 0
            symptoms_dict[symptoms_names[-1]] = ""
        else:
            symptoms_dict[symptoms_names[-2]] = other_symptom
            symptoms_dict[symptoms_names[-1]] = description
        
        return symptoms_dict
    

    def createInputExample(self, symptoms_list, other_symptom, descrip):
        return SymptomsCheckboxes(symptoms_list, other_symptom, descrip)

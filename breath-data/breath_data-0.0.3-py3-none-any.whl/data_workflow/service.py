from breath_api_interface.proxy import ServiceProxy
from breath_api_interface.queue import Queue
from breath_api_interface.service_interface import Service
from breath_api_interface.request import Request, Response

import pandas as pd
from pandas.core import series

import breath_data.data_workflow.open_sus as open_sus
import breath_data.data_workflow.ibge as ibge

class DataWorkflow(Service):
    def __init__(self, proxy:ServiceProxy, request_queue:Queue, global_response_queue:Queue):
        '''DataWorkflow constructor.
        '''
        super().__init__(proxy, request_queue, global_response_queue, "DataWorkflow")

    def run(self) -> None:
        '''Run the service, handling requests.
        '''

        request = self._get_request()

        if request is None:
            return

        response : Response = request.create_response(sucess=False, response_data={"message": "Operation not available"})

        if request.operation_name == "load_open_sus_data":
            response = self._load_open_sus_data(request)

        self._send_response(response)

    def _load_open_sus_data(self, request:Request) -> Response:
        SINTOMA_DICT = {
                    "FEBRE":"Febre", 
                    "TOSSE": "Tosse", 
                    "GARGANTA" : "Dor_de_garganta", 
                    "DISPNEIA" : "Dispneia", 
                    "MIALGIA" : "Mialgia", 
                    "SATURACAO" : "Saturação_O2", 
                    "DESC_RESP" : "Desconforto_Respiratório",
                    "OUTRO_SIN" : "Outro_Sintoma",
                    "PNEUMOPATI" :"Pneumopatia_crônica_associada",
                    "CARDIOPATI" : "Cardiopatia_crônica_associada",
                    "IMUNODEPRE" : "Imunodepressão_associada",
                    "HEPATICA": "Doença_hepática_crônica",
                    "NEUROLOGIC": "Doenca_neuorlógica",
                    "RENAL" : "Doença_renal_crônica_associada",
                    "SIND_DOWN" : "Síndrome_de_Down",
                    "METABOLICA": "Doença_metabólica_crônica_associada",
                    "PUERPERA" : "Puérpera",
                    "OBESIDADE" : "Obesidade",
                    "OUT_MORBI" : "Outra_morbidade_associada",
                    "ANTIVIRAL" : "Usa_antiviral",
                    "HOSPITAL" : "Hospitalização_por_Influenza",
                    "RES_FLUA" : "Diagnóstico_para_Influzenza_A",
                    "RES_FLUB" : "Diagnóstico_para_Influzenza_B",
                    "RES_PARA1" : "Diagnóstico_para_Parainfluenza_1",
                    "RES_PARA2" : "Diagnóstico_para_Parainfluenza_2",
                    "RES_PARA3" : "Diagnóstico_para_Parainfluenza_3",
                    "RES_ADNO" : "Diagnóstico_para_Adenovírus"
                    }

        # outros: EVOLUCAO -> Óbito, Alta        

        print("Log: Inserindo tipos de sintoma")

        tipos_sintoma = list( SINTOMA_DICT.values() ) 

        for tipo_sintoma in tipos_sintoma:
            request_info = {"symptom_name": tipo_sintoma}
            response = self._send_request(service_name="BDAcessPoint", operation_name="register_symptom_type", request_info=request_info)

            if not response.sucess:
                return response 

        print("Log: Inserindo dados do IBGE")

        table_ibge : pd.DataFrame = ibge.load_csv()
        for i in range(table_ibge.shape[0]):
            linha = table_ibge.iloc[i]
            uf = linha["UF"]
            nome = linha["Nome_Município"]
            cod = linha["Código Município Completo"]

            request_info = {"uf":uf, "nome":nome, "cod":cod}
            response = self._send_request(service_name="BDAcessPoint", operation_name="register_city", request_info=request_info)

            print(100*i/table_ibge.shape[0], "% - ", i, "/", table_ibge.shape[0])

            if not response.sucess:
                print("ERRO AO INSERIR DADOS DO IBGE")
                return response 

        print("Carregando dados do SUS")

        table : pd.DataFrame = open_sus.loadcsv()

        print("Inserindo dados do SUS")

        n_dado = table.shape[0]

        for i in range(n_dado):
            linha = table.iloc[i]

            sexo = linha["CS_SEXO"]
            cidade = linha["ID_MUNICIP"]

            request_info = {"sex":sexo}
            response = self._send_request(service_name="BDAcessPoint", operation_name="register_patient", request_info=request_info)

            cod = response.response_data["patient"]["Código"]

            data = linha["DT_NOTIFIC"]
            dia = int(data[:2])
            mes = int(data[3:5])
            ano = int(data[6:])

            for sintoma_key in tipo_sintoma:
                if linha["sintoma_key"] == 1:
                    request_info = {"year":ano, "month":mes, "day": dia, "city": cidade,
                                            "symptom_name": tipo_sintoma[sintoma_key], "patient_id":cod}

                    response = self._send_request(service_name="BDAcessPoint", operation_name="register_symptom", request_info=request_info)

                    if not response.sucess:
                        return response 

        return request.create_response(True)
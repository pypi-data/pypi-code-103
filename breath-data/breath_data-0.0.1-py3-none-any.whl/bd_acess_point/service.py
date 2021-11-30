from typing import Dict, List, Union
from breath_api_interface.proxy import ServiceProxy
from breath_api_interface.queue import Queue
from breath_api_interface.service_interface import Service
from breath_api_interface.request import Request, Response

from breath_data.bd_acess_point.relational_querier import RelationalQuerier
from breath_data.bd_acess_point.graph_querier import GraphQuerier

class BDAcessPoint(Service):
    '''BReATH service for provide BD acess

        :ivar relational_querier: Handles relational (SQL) queries
        :type relational_querier: breath_data.bd_acess_point.relational_querier.RelationalQuerier

        :ivar graph_querier: Handles graph (Neo4j) queries
        :type graph_querier: breath_data.bd_acess_point.graph_querier.GraphQuerier
    '''

    def __init__(self, proxy:ServiceProxy, request_queue:Queue, global_response_queue:Queue):
        '''BDAcessPoint constructor.

            Initializes the service with the BDs.
        '''
        super().__init__(proxy, request_queue, global_response_queue, "BDAcessPoint")
        self.relational_querier = RelationalQuerier()
        self.graph_querier = GraphQuerier()
        
    def run(self) -> None:
        '''Run the service, handling BD requests.
        '''
        request = self._get_request()

        if request is None:
            return

        response : Response = request.create_response(sucess=False, response_data={"message": "Operation not available"})

        if request.operation_name == "register_symptom":
            response = self._register_symptom(request)
        elif request.operation_name == "register_user":
            response = self._register_user(request)
        elif request.operation_name == "get_symptoms_types":
            response = self._get_symptoms_types(request)
        elif request.operation_name == "register_symptom_type":
            response = self._register_symptom_type(request)
        elif request.operation_name == "register_city":
            response = self._register_city(request)
        elif request.operation_name == "register_patient":
            response = self._register_patient(request)

        self._send_response(response)

        
    def _cancel_all(self):
        self.relational_querier.cancel()
        self.graph_querier.cancel()

    def _commit_all(self):
        self.relational_querier.commit()
        self.graph_querier.commit()

    def _register_user(self, request:Request) -> Response:
        nome = request.request_info["name"]

        sql_query = "INSERT INTO Usuarios(Nome) VALUES('{0}')".format(nome)

        sucess, users = self.relational_querier.query(sql_query)

        if not sucess:
            return request.create_response(sucess=False, response_data={"message":"Cannot create user"})
        
        user_id = users[0]["id"]

        return request.create_response(sucess=True, response_data={"user_id":user_id})

    def _register_symptom(self, request: Request) -> Response:
        
        symptom_name = request.request_info["symptom_name"]
        
        year = request.request_info["year"]
        month = request.request_info["month"]
        day = request.request_info["day"]

        symptoms_types = self._search_symptom_type(symptom_name)

        if symptoms_types is None:
            self._cancel_all()
            return request.create_response(sucess=False, response_data={"message": "Symptom type not found"})

        symptom_type_id = symptoms_types[0]["id"]

        patient_id = 0

        if "patient_id" in request.request_info:
            patient_id = request.request_info["patient_id"]
        else:
            user_id = request.request_info["user_id"]
            users = self._search_user(user_id)

            if users is None:
                self._cancel_all()
                return request.create_response(sucess=False, response_data={"message": "User not found"})

            patient_id = users[0]["Paciente"]
            city_id = users[0]["Cidade"]

        city_id = request.request_info["city"]

        sql_query = "INSERT INTO Sintoma(Tipo, Ano, Mês, Dia, Cidade)"
        sql_query += " VALUES('{0}', '{1}', '{2}', '{3}', {4})".format(symptom_type_id, year, month, day, city_id)

        sucess, symptom = self.relational_query.query(sql_query)

        if not sucess:
            self._cancel_all()
            return request.create_response(sucess=False, response_data={"message":"Error while registering symptom"})

        symptom_id = symptom[0]["id"]

        sql_query3 = "INSERT_INTO PacienteSintoma(Paciente, Sintoma) VALUES('{0}', '{1}')".format(patient_id, symptom_id)
        sucess, _ = self.relational_querier.query(sql_query3)

        if not sucess:
            self._cancel_all()
            return request.create_response(sucess=False, response_data={"message":"Cannot register patient symptom relation"})

        self._commit_all()

        return request.create_response(sucess=True)

    def _search_symptom_type(self, symptom_name:str) -> Union[List[Dict[str, str]], None]:
        neo_query = "MATCH (t:Tipo_Sintoma {{nome: {0}}}) RETURN t".format(symptom_name)        
        sucess, symptoms_types = self.graph_querier.query(neo_query)

        if not sucess:
            return None

        return symptoms_types

    def _search_user(self, user_id:int) -> Union[List[Dict[str, str]], None]:
        sql_query = "SELECT * FROM Usuarios WHERE Usuarios.id = {0}".format(user_id)
        sucess, users = self.relational_querier.query(sql_query)

        if not sucess:
            return None
        
        return users

    def _get_symptoms_types(self, request:Request) -> Response:
        neo_query = "MATCH (t:Tipo_Sintoma RETURN t"
        sucess, symptoms_types = self.graph_querier.query(neo_query)

        if not sucess:
            return Response(False, {"message":"Unable to access symptoms types"})
        
        return Response(True, {"symptoms_types":symptoms_types})

    def _register_symptom_type(self, request:Request) -> Response:
        neo_query = "CREATE ({0}:Tipo_Sintoma)".format(request.request_info["symptom_name"])

        sucess, _ = self.graph_querier.query(neo_query)

        if not sucess:
            return request.create_response(False, {"message":"Unable to register symptom type"}) 

        return request.create_response(True)

    def _register_city(self, request:Request) -> Response:
        uf = request.request_info["uf"]
        nome = request.request_info["nome"]
        cod = request.request_info["cod"]

        sql_query = "INSERT_INTO Cidades(UF, Nome, Código) VALUES('{0}', '{1}', '{2}')".format(uf, nome, cod)

        sucess, _ = self.relational_querier.query(sql_query)

        if not sucess:
            return request.create_response(False, {"message":"Unable to register city"})
        
        return request.create_response(True)

    def _register_patient(self, request:Request) -> Response:
        sex = request.request_info["sex"]

        sql_query = "INSERT_INTO Pacientes(Sexo) VALUES('{0}')".format(sex)

        sucess, patient = self.relational_querier.query(sql_query)

        if not sucess:
            return request.create_response(False, {"message":"Unable to register patient"})
        
        return request.create_response(True, {"patient": patient[0]})
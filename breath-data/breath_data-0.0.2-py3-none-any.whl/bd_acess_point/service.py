from __future__ import annotations

from typing import Callable, Dict, List, Union
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

		self._operations : Dict[str, Callable[[BDAcessPoint, Request], Response]] = {
							"register_symptom" : self._register_symptom,
							"register_workflow": self._register_workflow,
							"is_workflow_runned": self._is_workflow_runned,
							"register_user": self._register_user,
							"get_symptoms_types" : self._get_symptoms_types,
							"register_symptom_type": self._register_symptom_type,
							"register_city": self._register_city,
							"register_patient" : self._register_patient
							}
		
	def run(self) -> None:
		'''Run the service, handling BD requests.
		'''
		request = self._get_request()

		if request is None:
			return
			
		response : Response = request.create_response(sucess=False, response_data={"message": "Operation not available"})

		if request.operation_name in self._operations:
			response = self._operations[request.operation_name](request)

		self._send_response(response)

	def _cancel_all(self):
		self.relational_querier.cancel()
		#self.graph_querier.cancel()

	def _commit_all(self):
		self.relational_querier.commit()
		#self.graph_querier.commit()

	def _register_user(self, request:Request) -> Response:

		name = None
		age = None
		gender = None

		if 'name' in request.request_info:
			name = request.request_info["name"]
		if 'age' in request.request_info:
			age = request.request_info["age"]
		if 'gender' in request.request_info:
			gender = request.request_info["gender"]

		sql_query = "INSERT INTO Users(Nome, Idade, Genero) VALUES('{0}',{1},'{2}')".format(name, age, gender)

		sucess, _ = self.relational_querier.query(sql_query)

		if not sucess:
			return request.create_response(sucess=False, response_data={"message":"Cannot create user"})

		return request.create_response(sucess=True)

	def _register_symptom(self, request: Request) -> Response:
		
		symptom_name = None
		year = None
		month = None
		day = None

		if 'symptom_name' in request.request_info:
			symptom_name = request.request_info["symptom_name"]
		
		if 'year' in request.request_info:
			year = request.request_info["year"]
		if 'month' in request.request_info:
			month = request.request_info["month"]
		if 'day' in request.request_info:
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

		sql_query = "INSERT INTO Sintomas(Tipo, Ano, Mês, Dia, Cidade)"
		sql_query += " VALUES('{0}', '{1}', '{2}', '{3}', {4})".format(symptom_type_id, year, month, day, city_id)

		sucess, symptom = self.relational_query.query(sql_query)

		if not sucess:
			self._cancel_all()
			return request.create_response(sucess=False, response_data={"message":"Error while registering symptom"})

		symptom_id = symptom[0]["id"]

		sql_query3 = "INSERT INTO PacienteSintoma(Paciente, Sintoma) VALUES('{0}', '{1}')".format(patient_id, symptom_id)
		sucess, _ = self.relational_querier.query(sql_query3)

		if not sucess:
			self._cancel_all()
			return request.create_response(sucess=False, response_data={"message":"Cannot register patient symptom relation"})

		self._commit_all()

		return request.create_response(sucess=True)

	def _search_symptom_type(self, symptom_name:str) -> Union[List[Dict[str, str]], None]:
		#neo_query = "MATCH (t:Tipo_Sintoma {{nome: {0}}}) RETURN t".format(symptom_name)        
		#sucess, symptoms_types = self.graph_querier.query(neo_query)

		sql_query = "SELECT * from Sintomas WHERE Tipo = {0};".format(symptom_name)
		sucess, symptoms_types = self.relational_querier.query(sql_query)

		if not sucess:
			return None

		return symptoms_types

	def _search_user(self, user_id:int) -> Union[List[Dict[str, str]], None]:
		sql_query = "SELECT * FROM Users WHERE Users.id = {0}".format(user_id)
		sucess, users = self.relational_querier.query(sql_query)

		if not sucess:
			return None
		
		return users

	def _get_symptoms_types(self, request:Request) -> Response:
		#neo_query = "MATCH (t:Tipo_Sintoma RETURN t"
		#sucess, symptoms_types = self.graph_querier.query(neo_query)

		sql_query = "SELECT Tipo from Sintomas GROUP BY Tipo;"
		sucess, _ = self.relational_querier.query(sql_query)

		if not sucess:
			return Response(False, {"message":"Unable to access symptoms types"})
		
		return Response(True, {"symptoms_types":symptoms_types})

	# onde guardariamos tipo de sintoma no relacional?
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

		sql_query = "INSERT INTO Cidades(Id, Nome, UF) VALUES('{0}', '{1}', '{2}')".format(cod, nome, uf)

		sucess, _ = self.relational_querier.query(sql_query)

		if not sucess:
			return request.create_response(False, {"message":"Unable to register city"})
		
		return request.create_response(True)

	# Teremos banco pacientes alem do banco de usurios?
	def _register_patient(self, request:Request) -> Response:
		sex = request.request_info["sex"]

		sql_query = "INSERT INTO Pacientes(Sexo) VALUES('{0}')".format(sex)

		sucess, patient = self.relational_querier.query(sql_query)

		if not sucess:
			return request.create_response(False, {"message":"Unable to register patient"})
		
		return request.create_response(True, {"patient": patient[0]})

	def _register_workflow(self, request:Request) -> Response:
		name = request.request_info["workflow_name"]

		sql_query = "INSERT INTO Workflow(Nome, Executado) VALUES('{0}', 1)".format(name)

		sucess, _ = self.relational_querier.query(sql_query)

		if not sucess:
			return request.create_response(False, {"message":"Unable to register workflow"})
		
		return request.create_response(True)

	def _is_workflow_runned(self, request:Request) -> Response:
		name = request.request_info["workflow_name"]

		sql_query = "SELECT * FROM Workflow WHERE Workflow.Nome = '{0}'".format(name)
		sucess, workflows = self.relational_querier.query(sql_query)

		if len(workflows) > 0 and workflows[0][1] != 0:
			return request.create_response(True)

		return request.create_response(False)

	def _get_climate_interval(self, request:Request) -> Response:

		initial = None
		final = None

		if 'initial' in request.request_info:
			initial = request.request_info["initial"]
		if 'final' in request.request_info:
			final = request.request_info["final"]

		sql_query = "SELECT * from Climate WHERE date BETWEEN {0} AND {1} ORDER BY date;".format(initial, final)
		sucess, climates = self.relational_querier.query(sql_query)

		if not sucess:
			return None

		return climates
		
	def _get_climate_date(self, request:Request) -> Response:
		
		date = None

		if 'date' in request.request_info:
			date = request.request_info["date"]


		sql_query = "SELECT * from Climate WHERE date = {0} ORDER BY date;".format(date)
		sucess, climates = self.relational_querier.query(sql_query)

		if not sucess:
			return None

		return climates

	def _get_SRAG_interval(self, request:Request) -> Response:
		
		initial = None
		final = None

		if 'initial' in request.request_info:
			initial = request.request_info["initial"]
		if 'final' in request.request_info:
			final = request.request_info["final"]

		sql_query = "SELECT * from SRAG WHERE date BETWEEN {0} AND {1} ORDER BY date;".format(initial, final)
		sucess, diagnostics = self.relational_querier.query(sql_query)

		if not sucess:
			return None

		return diagnostics

	def _get_SRAG_date(self, request:Request) -> Response:
		
		date = None

		if 'date' in request.request_info:
			date = request.request_info["date"]

		sql_query = "SELECT * from SRAG WHERE date = {0} ORDER BY date;".format(date)
		sucess, diagnostics = self.relational_querier.query(sql_query)

		if not sucess:
			return None

		return diagnostics
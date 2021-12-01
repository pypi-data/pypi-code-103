import sqlite3
from sqlite3.dbapi2 import Cursor, Connection
from typing import Dict, List, Tuple, Union

## SQLite3 datatypes
## 
## NULL. The value is a NULL value.
## INTEGER. The value is a signed integer, stored in 1, 2, 3, 4, 6, or 8 bytes depending on the magnitude of the value.
## REAL. The value is a floating point value, stored as an 8-byte IEEE floating point number.
## TEXT. The value is a text string, stored using the database encoding (UTF-8, UTF-16BE or UTF-16LE).
## BLOB. The value is a blob of data, stored exactly as it was input.

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class RelationalQuerier(metaclass=Singleton):
	#conn : Connection = None
	#c : Cursor = None

	def __init__(self):
		# temporary database
		#self.conn = sqlite3.self.connect(':memory:')

		# this line already checks if the db exists
		self.conn = sqlite3.connect('breath.db')
		
		# create db cursor
		self.c = self.conn.cursor()

		# create Cidades table
		self.c.execute(
			"""
			CREATE TABLE IF NOT EXISTS Cidades(
			Id INTEGER PRIMARY KEY,
			Nome TEXT,
			UF INT)
			""")

		# create table Diagnósticos
		self.c.execute(
			"""
			CREATE TABLE IF NOT EXISTS Diagnósticos(
			Id INTEGER PRIMARY KEY,
			Diagnóstico TEXT)
			""")	
    
		# create table Sintomas
		self.c.execute(
			"""
			CREATE TABLE IF NOT EXISTS Sintomas(
			Id INTEGER PRIMARY KEY,
			Tipo TEXT,
			Ano INTEGER,
			Mês INTEGER,
			Dia INTEGER,
			Cidade TEXT,
			Paciente FOREIGN_KEY)
			""")
		
		# create table Users
		self.c.execute(
			"""
			CREATE TABLE IF NOT EXISTS Users(
			Id INTEGER PRIMARY KEY,
			Idade INTEGER,
			Nome TEXT,
			Genero TEXT)
			""")

		# create table PacienteSintoma
		self.c.execute(
			"""
			CREATE TABLE IF NOT EXISTS PacienteSintoma(
			Paciente INTEGER,
			Sintoma INTEGER,
			FOREIGN KEY (Paciente) REFERENCES Users(Id),
			FOREIGN KEY (Sintoma) REFERENCES Sintomas(Id)
			)
			""")
			
		# create table Climate
		self.c.execute(
			"""
			CREATE TABLE IF NOT EXISTS Climate(
			id INTEGER PRIMARY KEY,
			date DATE,
			precipitacao REAL,
			pressao_at_max REAL,
			pressao_at_min REAL,
			radiacao REAL,
			temp_max REAL,
			temp_min REAL,
			umidade REAL,
			max_vent REAL,
			velocidade_vent REAL,
			region TEXT,
			state TEXT,
			station TEXT,
			lat REAL,
			lon REAL,
			elvt REAL)
			""")

		# create diagnostics table
		self.c.execute(
			"""
			CREATE TABLE IF NOT EXISTS SRAG(
			id INTEGER PRIMARY KEY,
			ID_MUNICIP TEXT,
			SEM_NOT TEXT,
			SG_UF_NOT TEXT,
			DT_SIN_PRI TEXT,
			DT_NASC TEXT,
			NU_IDADE_N TEXT,
			CS_SEXO TEXT,
			CS_GESTANT TEXT,	
			CS_RACA TEXT,
			CS_ESCOL_N TEXT,
			SG_UF TEXT,
			ID_MN_RESI TEXT,
			ID_OCUPA_N TEXT,
			VACINA TEXT,
			FEBRE TEXT,
			TOSSE TEXT,
			CALAFRIO TEXT,
			DISPNEIA TEXT,
			GARGANTA TEXT,
			ARTRALGIA TEXT,
			MIALGIA TEXT,
			CONJUNTIV TEXT,
			CORIZA TEXT,
			DIARREIA TEXT,
			OUTRO_SIN TEXT,
			OUTRO_DES TEXT,
			CARDIOPATI TEXT,
			PNEUMOPATI TEXT,
			RENAL TEXT,
			HEMOGLOBI TEXT,
			IMUNODEPRE TEXT,
			TABAGISMO TEXT,
			METABOLICA TEXT,
			OUT_MORBI TEXT,
			MORB_DESC TEXT,
			HOSPITAL TEXT,
			DT_INTERNA TEXT,
			CO_UF_INTE TEXT,
			CO_MU_INTE TEXT,
			DT_PCR TEXT,
			PCR_AMOSTR TEXT,
			PCR_OUT TEXT,
			PCR_RES TEXT,
			PCR_ETIOL TEXT,
			PCR_TIPO_H TEXT,
			PCR_TIPO_N TEXT,
			DT_CULTURA TEXT,
			CULT_AMOST TEXT,
			CULT_OUT TEXT,
			CULT_RES TEXT,
			DT_HEMAGLU TEXT,
			HEMA_RES TEXT,
			HEMA_ETIOL TEXT,
			HEM_TIPO_H TEXT,
			HEM_TIPO_N TEXT,
			DT_RAIOX TEXT,
			RAIOX_RES TEXT,
			RAIOX_OUT TEXT,
			CLASSI_FIN TEXT,
			CLASSI_OUT TEXT,
			CRITERIO TEXT,
			TPAUTOCTO TEXT,
			DOENCA_TRA TEXT,
			EVOLUCAO TEXT,
			DT_OBITO TEXT,
			DT_ENCERRA TEXT,
			DT_DIGITA TEXT,
			SRAG2013FINAL TEXT,
			OBES_IMC TEXT,
			OUT_AMOST TEXT,
			DS_OAGEETI TEXT,
			DS_OUTMET TEXT,
			DS_OUTSUB TEXT,
			OUT_ANTIV TEXT,
			DT_COLETA TEXT,
			DT_ENTUTI TEXT,
			DT_ANTIVIR TEXT,
			DT_IFI TEXT,
			DT_OUTMET TEXT,
			DT_PCR_1 TEXT,
			DT_SAIDUTI TEXT,
			RES_ADNO TEXT,
			AMOSTRA TEXT,
			HEPATICA TEXT,
			NEUROLOGIC TEXT,
			OBESIDADE TEXT,
			PUERPERA TEXT,
			SIND_DOWN TEXT,
			RES_FLUA TEXT,
			RES_FLUB TEXT,
			UTI TEXT,
			IFI TEXT,
			PCR TEXT,
			RES_OUTRO TEXT,
			OUT_METODO TEXT,
			RES_PARA1 TEXT,
			RES_PARA2 TEXT,
			RES_PARA3 TEXT,
			DESC_RESP TEXT,
			SATURACAO TEXT,
			ST_TIPOFI TEXT,
			TIPO_PCR TEXT,
			ANTIVIRAL TEXT,
			SUPORT_VEN TEXT,
			RES_VSR TEXT,
			RES_FLUASU TEXT,
			DT_UT_DOSE TEXT)
			""")

		# create table workflow
		self.c.execute(
			"""
			CREATE TABLE IF NOT EXISTS Workflow(
			Nome TEXT PRIMARY KEY,
			Executado BOOL NOT NULL DEFAULT '0'
			)""")

		self.conn.commit()

	def query(self, query:str, values:str = None) -> Tuple[bool, Union[List[Dict[str, str]], None]]:
		if self.conn is None:
			self.__init__()
		"""Executes the desired query and fetch its results if there is any
        """
		result = None
		try:
			if values is not None:
				values = tuple(values[1:])
				self.c.execute(query, values)
			else:
				result = self.c.execute(query)
				result = result.fetchall()
			sucess = True
			self.conn.commit()
			return True, result
		except Exception as e:
			print(e)
			return False, result

	def cancel(self):
		"""Close the database connection once the program is done with it.
		"""
		self.conn.rollback()

	def commit(self):
	   self.conn.commit()

	def _close(self):
		"""Close the database connection once the program is done with it.
		"""
		self.conn.close()

	def __del__(self):
		self._close()
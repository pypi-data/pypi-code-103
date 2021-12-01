import pandas as pd
import numpy as np
from tkinter import Tk 
from tkinter.filedialog import askopenfilenames
from functools import reduce
from relational_querier import RelationalQuerier
#from graph_querier import GraphQuerier

# os dados climaticos brutos foram baixados diretamente do link: https://www.kaggle.com/PROPPG-PPG/hourly-weather-surface-brazil-southeast-region
abbreviation = ['date','precipitacao','pressao_at_max', 'pressao_at_min', 'radiacao', 'temp_max','temp_min','umidade','max_vent','velocidade_vent','region','state','station','lat','lon','elvt']
db = RelationalQuerier()
def format_csv(file_name):
	f1=open(file_name,"r+")
	input=f1.read()
	input=input.replace(';',',')
	f2=open(file_name,"w+")
	f2.write(input)
	f1.close()
	f2.close()

def clean(file_name):
	"""
	! filter raw data from date and stations code
	! process data
	! clean na
	"""
	format_csv(file_name)

	df = pd.read_csv(file_name)
	
	for i in df.columns:
		df = df.loc[df[i] != -9999]

	preci = df.groupby(['Data'])['PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'].sum().reset_index()
	max_pres = df.groupby(['Data'])['PRESSÃO ATMOSFERICA MAX.NA HORA ANT. (AUT) (mB)'].max().reset_index()
	min_pres = df.groupby(['Data'])['PRESSÃO ATMOSFERICA MIN. NA HORA ANT. (AUT) (mB)'].min().reset_index()
	rad = df.groupby(['Data'])['RADIACAO GLOBAL (Kj/m²)'].mean().reset_index()
	temp_max = df.groupby(['Data'])['TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)'].max().reset_index()
	temp_min = df.groupby(['Data'])['TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)'].min().reset_index()
	umidade = df.groupby(['Data'])['UMIDADE RELATIVA DO AR, HORARIA (%)'].mean().reset_index()
	max_vent = df.groupby(['Data'])['VENTO, RAJADA MAXIMA (m/s)'].max().reset_index()
	vel_vent = df.groupby(['Data'])['VENTO, VELOCIDADE HORARIA (m/s)'].mean().reset_index()
	region = df.groupby(['Data'])['region'].min().reset_index()
	state = df.groupby(['Data'])['state'].min().reset_index()
	station = df.groupby(['Data'])['station'].min().reset_index()
	latitude = df.groupby(['Data'])['latitude'].min().reset_index()
	longitude = df.groupby(['Data'])['longitude'].min().reset_index()
	height = df.groupby(['Data'])['height'].min().reset_index()

	clmns = [preci, max_pres, min_pres, rad, temp_max, temp_min, umidade, max_vent, vel_vent, region, state, station, latitude, longitude, height]
	df_final = reduce(lambda left,right: pd.merge(left,right,on='Data'), clmns)
	df_final.columns = abbreviation

	new_file_name = file_name.split('.')[0]+'_clean.'+file_name.split('.')[1]
	print(new_file_name)

	df_final.to_csv(new_file_name)
	print('exportou')

	return df_final, new_file_name

def add_data_graph(df = None, csv = None):
	db = GraphQuerier()

	if not df and csv:
		df = pd.read_csv(csv)

	for i in range(len(df)):
		dict = {} 
		for A, B in zip(clean_abbreviation, df[i]):
			dict[A] = B
		query = 'CREATE (' + i + ':Climate {' + dict + '});'
		result = db.query(query)
		print(len(result))
	db._close()

def add_data_relational(db, df = None, csv = None):

	if df is None and csv is not None:
		df = pd.read_csv(csv)
	for data in df.values:

		query = """
		INSERT INTO Climate 
		(date,precipitacao,pressao_at_max, pressao_at_min, radiacao,
		temp_max,temp_min,umidade,max_vent,velocidade_vent,region,
		state,station,lat,lon,elvt) 
		VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"""

		result = db.query(query, data)
	db.commit()

if __name__ == "__main__":
	# le o caminho do arquivo
	Tk().withdraw()
	files = askopenfilenames()
	print(files)
	# para cada um dos arquivos
	for file in files:
		posfix = file.split('/')[-1].split('_')[-1].split('.')[0]

		# se o arquivo nao tem nome [*]_clean.csv limpe-o
		if posfix != 'clean':
			print('arquivo nao formatado, iniciando limpeza de arquivo', posfix)
			df, new_file_name = clean(file)
			print(f'Dados tratados estao no arquivo {new_file_name} na mesma pasta dos originais')
			add_data_relational(db, df = df)

		# caso contrario apenas adicione no banco de dados
		else:
			print('arquivo formatado, iniciando insercao no banco de dados')
			# only uncomment if you want do use the databses
			add_data_relational(db, csv = file)

	# veja se a insercao deu certo
	query = 'SELECT * FROM Climate;'
	result = db.query(query)
	print('result:', result)
	#add_data_graph(df)
	db._close()
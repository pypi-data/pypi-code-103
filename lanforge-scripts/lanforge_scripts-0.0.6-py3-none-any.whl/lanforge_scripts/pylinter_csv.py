#!/usr/bin/python3
import pandas as pd
import numpy as np
class CSVCreator:
	@staticmethod
	def csv_creator(txt_file):
        	pyjson=open(txt_file, 'r').read()
        	pyjson=pyjson.split('\n')
        	pyjson=[x for x in [x.split(':') for x in pyjson if len(x)] if len(x) > 2]
        	df=pd.DataFrame(pyjson)
        	#df.columns=['script','line','column','warning','text',5,6,7,8,9]
        	#df=df.dropna(subset=['warning'])
        	return df

def main():
	files = ['py-scripts-pylint.txt','py-json-pylint.txt','lanforge-pylint.txt']
	csv_create=CSVCreator()
	dataframe = [csv_create.csv_creator(file) for file in files]
	df = pd.concat(dataframe)
	df = df.reset_index(drop=True)
	df.to_csv('pyjson_pylint.csv')

if __name__ == "__main__":
	main()

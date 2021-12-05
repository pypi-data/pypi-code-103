import logging

from pathlib import Path
import click
import pandas as pd

logging.basicConfig(level='DEBUG', format="'%(asctime)s - %(name)s - %(levelname)s - %(message)s'")
logger = logging.getLogger(__name__)

@click.command()
@click.option("--input", "-i", default="./", help="Path where to read the files for conversion.", type=str)
@click.option("--output", "-o", default="./", help="Path where to read the files will be saved.", type=str)
@click.option("--delimiter", "-d", default=",", help="Separator used to split the files.", type=str)
@click.option("--prefix","-prefix", prompt=True, prompt_required=False, default='file',  
    help=(
        "Prefix used to prepend to the name of the converted file saved on disk."
        "The suffix will be a number starting from 0. ge: file_0.json."),)

def converter(input: str = "./", output: str = "./", delimiter: str = ',', prefix: str = None):  
    """Convert single file or list of csv to json"""
    #logger.info("Esse é o delimitador: %s", delimiter) 
    input_path = Path(input)
    output_path = Path(output)
    logger.info("Input Path: %s", input_path)
    logger.info("Output Path: %s", output_path)
    for p in [input_path,output_path]:
        if not (p.is_file() or p.is_dir()):
            raise TypeError("Not a valid path or file name.")
    data = read_csv_file(source=input_path, delimiter=delimiter)
    save_to_json_files(csvs=data, output_path=output_path, prefix=prefix)
    #json_data = parse_csv_to_json(data)
    #white_json_data(json_data, output_path)

def read_csv_file(source: Path, delimiter: str) -> tuple:
    """Load csv files from disk.
    Source (Path): Path of a single csv file or directory containing csvs to be parsed.
    delimiter (str): Separator for columns in csv.
    Return:
        tuple: Tuple of DataFrames."""
    if source.is_file():
        logger.info("Reading Single File %s", source)
        return (pd.read_csv(filepath_or_buffer=source, delimiter=delimiter, index_col=False),)
            #read_csv(filepath_or_buffer=source, delimiter=delimiter, index_col=False),)          
    logger.info("Reandign all files for given path %s", source)
    data = list()
    for name in source.iterdir():
        data.append(pd.read_csv(filepath_or_buffer=name, delimiter=delimiter, index_col=False))
            #read_csv(filepath_or_buffer=name, delimiter=delimiter, index_col=False))
    return tuple(data)

def save_to_json_files(csvs: tuple, output_path: Path, prefix: str = None):
    """Save Dataframes to Disk"""
    i = 0
    while i < len(csvs):
        file_name = output_path.joinpath(f"{prefix}_{i}")
        logger.info("Savinf file %s in folder %s", file_name, output_path)
        data = csvs[i]
        data.to_json(path_or_buf=file_name, orient="records", indent=4)
        #white_json_data(path_or_buf=file_name, orient="records", indent=4)
        i += 1

#funções da aula 6        
#def read_csv(input_path: Path, delimiter: str =",") -> list[list[str]]:
 #   ''' faz a leitura do arquivo CSV ou pasta cotendo varios arquivos'''
  #  with input_path.open(mode='r') as file:
  #      data2 = file.readlines()
   # return [line.strip().split(delimiter) for line in data2]

#def parse_csv_to_json(data2: list[list[str]]) -> list[dict[str,str]]:
 #   ''' converte list de dados de csv para formato json'''
  #  column = data2[0]
   # lines = data2[1:]
    #return [dict(zip(column, line)) for line in lines]

#def write_line(line: tuple, io, append_comma: bool):
 #   key, value = line
  #  if append_comma:
   #     io.write(f'\t\t"{key}": "{value}",\n')
    #else:
     #   io.write(f'\t\t"{key}": "{value}"\n')

#def write_dictionary(data2:dict,io,append_comma:True):
 #   io.write("\t{\n")
  #  items = tuple(data2.itens())
   # for line in items[:-1]:
    #    write_line(line, io, append_comma=True)
    #write_line(items[-1],io,append_comma=False)
    #io.write("\t")
    #if append_comma:
     #   io.write(",\n")
    #else:
     #   io.write("\n")

#def white_json_data(data2: list[dict[str,str]],output_path:Path):
 #   '''escreve um dicionario json em disco no endereco'''
  #  with output_path.open(mode="w") as file:
   #     file.write("[\n")
    #    for d in data2[:-1]:
     #       write_dictionary(d, file, append_comma=True)
      #  write_dictionary(data2[-1], file, append_comma=False)
       # file.write("]\n")


#"""função para converter json para csv"""
# converter_2 é a função principal, as demais são as relações dessa função.
#def converter_2(input: str = "./", output: str = "./", delimiter: str = ',', prefix: str = None):  
 #   """Convert single file or list of csv to json"""
  #  #logger.info("Esse é o delimitador: %s", delimiter) 
   # input_path = Path(input)
    #output_path = Path(output)
    #logger.info("Input Path: %s", input_path)
    #logger.info("Output Path: %s", output_path)
    #for p in [input_path,output_path]:
     #   if not (p.is_file() or p.is_dir()):
      #      raise TypeError("Not a valid path or file name.")
    #data = read_json_file(source=input_path, delimiter=delimiter)
        """Substituir aqui a função de leitura do json"""
    #save_to_csv_files(csvs=data, output_path=output_path, prefix=prefix)
        """Substituir aqui a função que salva o csv""" 

#"""função para ler o json"""
#def read_json_file(source: Path, delimiter: str) -> tuple:
 #   """Load csv files from disk.
  #  Source (Path): Path of a single csv file or directory containing csvs to be parsed.
   # delimiter (str): Separator for columns in csv.
    #Return:
     #   tuple: Tuple of DataFrames."""
    #if source.is_file():
     #   logger.info("Reading Single File %s", source)
      #  return (pd.read_csv(filepath_or_buffer=source, delimiter=delimiter, index_col=False),)
        """Substituir aqui a função de leitura do json"""       
    #logger.info("Reandign all files for given path %s", source)
    #data = list()
    #for name in source.iterdir():
     #   data.append(pd.read_csv(filepath_or_buffer=name, delimiter=delimiter, index_col=False))
        """Substituir aqui a função de leitura do json""" 
    #return tuple(data)

#"""função para salvar o csv"""
#def save_to_csv_files(csvs: tuple, output_path: Path, prefix: str = None):
 #   """Save Dataframes to Disk"""
  #  i = 0
   # while i < len(csvs):
    #    file_name = output_path.joinpath(f"{prefix}_{i}")
     #   logger.info("Savinf file %s in folder %s", file_name, output_path)
      #  data = csvs[i]
       # data.to_json(path_or_buf=file_name, orient="records", indent=4)
        #white_json_data(path_or_buf=file_name, orient="records", indent=4)
        """Substituir aqui a função que salva o csv""" 
        # """i += 1"""

#"""leitura do json"""
#def read_json(input_path: Path, delimiter: str = ';') ->list[str]:  #vai usar o "," como delimitador 
 #   with input_path.open(mode='r') as file:
  #      data = file.readlines() 
    # não vai usar parsed_data = [line.rstrip(']').strip().split() for line in data]  #remove \n no final da linha, e separa as strings
    # não vai usar parsed_data =[line.strip('\t\t').strip('\n').split('": "') for line in data[0:]]
    #parsed_data =[line.strip().split('": "') for line in data]
    # não vai usar parsed_data = [line.replace("\n","") for line in data]
    # não vai usar parsed_data = [line.replace("\t","") for line in data]
   # return parsed_data

#"""passar o arquivo do json para o csv"""
#def parse_json_to_csv(data: list) -> list:
 #   ''' converte list de dados de csv para formato json'''
   # não vai usar header = data[0]
    #'''body = data[1:]
    #for i in body:
     #   print(i)'''
    #return data
#parse_json_to_csv(data)  

#"""escrever o csv"""
#def write_csv_data(data: list[str],output_path:Path):
 #    with output_path.open(mode="w") as file:
        # não vai usar print (data)
        #for c,d in enumerate(data):  
            # não vai usar file.write(d[0])
            # não vai usar write_list(d, file)
            #for i in d:
             #   if c< len(data)-1:
              #      file.write(i)
               #     file.write("\n")    
                #else:
                 #   file.write(i)
            #print(c)
            #print(len(data))
            # não vai usar write_list(data[-1], file, append_comma=False)
        # não vai usar file.write("]")
#write_csv_data(data,Path('Js_out.csv'))

#"""salvar o csv"""
#def write_list(data:list,io,append_comma:False):
 #   items = tuple(data)
  #  for line in items:
   #     value = line
    #    io.write(value)
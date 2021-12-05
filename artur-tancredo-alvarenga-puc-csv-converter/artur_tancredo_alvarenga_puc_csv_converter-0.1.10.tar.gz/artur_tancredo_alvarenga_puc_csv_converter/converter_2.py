import logging
from os import F_OK, path, read, replace
from typing import List
from click.decorators import pass_context
from click.termui import prompt
from pathlib import Path
import click

logging.basicConfig(level='DEBUG',format = "'%(asctime)s - %(name)s - %(levelname)s - %(message)s'")
loggger = logging.getLogger(__name__)

@click.command()
@click.option("--input", "-i", default="./", help="Path where to read the files for conversion.", type=str)
@click.option("--output", "-o", default="./", help="Path where to read the files will be saved.", type=str)
@click.option("--delimiter", "-d", default=",", help="Separator used to split the files.", type=str)
@click.option("--prefix","-prefix", prompt=True, prompt_required=False, default='file',  
    help=(
        "Prefix used to prepend to the name of the converted file saved on disk."
        "The suffix will be a number starting from 0. ge: file_0.json."),)

#"""Função que converte o csv para json"""
def converter(input : str = './', output: str = './', delimiter: str = ',', prefix: str = None):
    """Converte um arquivo ou uma lista de csv para Json."""
    input_path = Path(input)
    output_path = Path(output)
    loggger.info("Input Path: %s", input_path)
    loggger.info("Output Path: %s", output_path)
    for p in[input_path, output_path]:
        if not(p.is_file() or p.is_dir()):
            raise TypeError("Not a valid path or file name.")
    data = read_csv_file(source = input_path, delimiter = delimiter)
    json_data = parse_csv_to_json(data)
    save_to_json_files(json_data, source= output_path, prefix = prefix)  

def parse_csv_to_json(data) -> list:
    """Transformar arquivos de um dicionário em Json"""
    header = data[0]
    body = data[1:]
    result = [dict(zip(header,bodys)) for bodys in body]
    return result

#"""Função que salva o csv para json"""
def save_to_json_files(data_json: list, source: path, prefix: str):
    file_name = source.joinpath(f"{prefix}.json")
    with open(file_name, "w") as outfile:
        loggger.info("Saving file %s in folder %s", file_name, source)
        outfile.write("[\n")
        for index_d,d in enumerate(data_json):
            outfile.write("".ljust(4, " ") + "{\n")
            items = tuple(d.items()) 
            for index_line,line in enumerate(items):
                key, value = line    
                if(index_line != len(d)-1):
                    s = '{}: {}\n'.format('"' + key + '"', '"' + value + '"'+ ",")
                elif(index_line == len(d)-1):
                    s = '{}: {}\n'.format('"' + key + '"', '"' + value + '"')
                outfile.write("".ljust(8," ") + s)  
            if(index_d != (len(data_json)-1)):
                outfile.write("".ljust(4, " ") + "},\n")
            
            elif(index_d == (len(data_json)-1)):
                outfile.write("".ljust(4, " ") + "}\n")
        outfile.write("]\n")

#"""Função que lê um arquivo de csv para json"""
def read_File_single_arch(source:Path, delimiter:str) -> list:
    """Read a single archive csv."""
    with open(source,'r') as file:
        line = file.readlines()
    data_list = [lines.strip().split(delimiter) for lines in line]
    return data_list 

#"""Função que lê vários arquivos de csv para json"""
def read_File_path(source:Path, delimiter:str, name) -> list:
    """Read archives from an Path"""
    with open(name,"r") as file:
      line = file.readlines() 
    data_list = [lines.strip().split(delimiter) for lines in line]
    return data_list 

#"""Função que carrega o csv"""
def read_csv_file(source: Path, delimiter: str):
    """Load csv files from disk.
    Args:
        source (Path): Path of a single csv file or a directory containing csvs to be parsed;
        delimiter (str): Separator for columns in csv.
    Return:
        Dict: Dict of data extracted of csv.
    """
    if source.is_file():
        loggger.info("Reading Single File %s", source)
        data = read_File_single_arch(source, delimiter)
        return data
    loggger.info("Reading all files for given path %s", source)
    for name in source.iterdir():
        data = read_File_path(source, delimiter,name)
        return data

#"""Função que converte o json para csv"""
def converter_2(input : str = './', output: str = './', delimiter: str = ',', prefix: str = None):
    """Convert a single file or list of csv to Json."""
    input_path = Path(input)
    output_path = Path(output)
    loggger.info("Input Path: %s", input_path)
    loggger.info("Output Path: %s", output_path)
    loggger.info("ERRO NA SAÍDA")
    for p in[input_path, output_path]:
        if not(p.is_file() or p.is_dir()):
            raise TypeError("Not a valid path or file name.")
    data = read_json_file(source = input_path, delimiter = delimiter)
    print(data)
    
    #json_data = parse_csv_to_json(data)
    #save_to_json_files(json_data, source= output_path, prefix = prefix)  

#"""Função que lê o json para csv"""
def read_json_File_single_arch(source:Path, delimiter:str) -> list:
    """Read a single archive csv."""
    with open(source,'r') as file:
        line = file.readlines()
    json_data_list = [lines.strip().split(delimiter) for lines in line]
    return json_data_list 
    
#"""Função que lê vários arquivos do json para csv"""
def read_json_File_path(source:Path, delimiter:str, name) -> list:
    """Read archives from an Path"""
    with open(name,"r") as file:
      line = file.readlines()  
    json_data_list = [lines.strip().split(delimiter) for lines in line]
    return json_data_list 

#"""Função que converte o json para csv"""
def read_json_file(source: Path, delimiter: str):
    """Load csv files from disk.
    Args:
        source (Path): Path of a single csv file or a directory containing csvs to be parsed;
        delimiter (str): Separator for columns in csv.
    Return:
        Dict: Dict of data extracted of csv.
    """
    if source.is_file():
        loggger.info("Reading Single File %s", source)
        data_json = read_json_file(source, delimiter)
        return data_json
    loggger.info("Reading all files for given path %s", source)
    for name in source.iterdir():
        data = read_json_File_path(source, delimiter,name)
        return data
    
    

    
        


      
            
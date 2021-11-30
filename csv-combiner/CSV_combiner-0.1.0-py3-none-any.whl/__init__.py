import os
from .csv_tools import combiner
from .Spreadsheet_converter import sheet_converter
def from_dir(dir_name = "." , move_to="done",output_name="final.csv",has_title = False, delete = False):
    
    supported_files = [".csv",".xls",".xlsx"]
    files = []
    
    for f in os.listdir(os.path.join(dir_name)):
        
        for format in supported_files:
            if f.endswith(format):
                filename = dir_name+"/"+f
                
                if format ==".csv":
                    files.append(filename)
                else:
                    sheet_converter.converter(filename)
                    files.append(filename+".csv")
                    os.remove(filename)
    
    combiner().combine(files,output_name)

    if delete:
        for f in files:
            os.remove(f)
    
    else:
        if os.path.exists(move_to):
            pass
        else:
            os.makedirs(move_to)
        for f in files : 
            os.replace(f,move_to+"/"+f[len(dir_name)+1:])

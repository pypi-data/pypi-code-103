import subprocess, multiprocessing
from multiprocessing import Process

my_list = [ 't0', 't1', 't2' ]

if __name__ == '__main__':
    processors = multiprocessing.cpu_count()

    for i in range(len(my_list)):
        if( i < processors ):
             cmd = ["python3", "app.py", my_list[i],"skip"]
             child = subprocess.call( cmd, shell=False )

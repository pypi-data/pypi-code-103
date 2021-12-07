import json
import subprocess
from tqdm import tqdm
import os
import re

def fetch_func(par, ind, cont):
    t=0
    for i in range(len(par)):
        if par[i]>ind:
            t=i
            break
    t0=t
    lc=1
    rc=0
    while lc>rc:
        t+=1
        try:
            if cont[par[t]]=='{':
                lc+=1
            else:
                rc+=1
        except Exception:
            return 0, 0
    return par[t0], par[t]


def cuda_func_info(cont_cu):
    pat_comments = re.compile(r'(\/\*([\s\S]*?)\*\/)')
    comments = pat_comments.finditer(cont_cu)
    for comment in comments:
        cont_cu = cont_cu.replace(cont_cu[comment.start():comment.end()],' '*(comment.end()-comment.start()))


    pat=re.compile(r'(_[a-z0-9_]+\s+\b[A-Za-z0-9_]+\s+\b[A-Za-z0-9_]+(\s+\b[A-Za-z0-9_])*\s*\([\s\S]*?\)\s*\{)') 
    pat_par=re.compile(r'\{|\}')

    cnt=0
    err=0

    cu_func=pat.finditer(cont_cu) # cuda function

    gp=[i.end()-1 for i in pat_par.finditer(cont_cu)] # cuda {} pos

    cu_name=[]  #cuda name
    cu_pos=[]   #cuda pos
    cu_cont=[]  #cuda content
    for cu in cu_func:
        t0, t=fetch_func(gp, cu.start(), cont_cu)
        conti=cont_cu[t0:t+1] # conti->content i
        cont_all = cont_cu[cu.start():t+1]
        # if conti.find('block')>0 or conti.find('thread')>0 and conti.find('#')<0:
        if conti.find('block')>0 or conti.find('thread')>0:
            mingzi = re.sub(r'\s+', ' ', cu.group()).split('(')[0].split(' ')[-1]
            if mingzi not in ["if","while","for"] and mingzi != '':
                cu_name.append(mingzi) #extracted cuda func name
                cu_pos.append((t0,t+1))
                cu_cont.append(cont_all)
    return cu_name,cu_pos,cu_cont



def c_func_info(cont_c):
	stop_set=set(['main', 'printf', 'operator', 'if', 'while', 'for'])
	pat_comments = re.compile(r'(\/\*([\s\S]*?)\*\/)')
	comments = pat_comments.finditer(cont_c)
	for comment in comments:
		cont_c = cont_c.replace(cont_c[comment.start():comment.end()],' '*(comment.end()-comment.start()))
	
	
	# pat=re.compile(r'(\s[A-Za-z0-9_]+\**\s+[A-Za-z0-9_]+\**\s*(\s+[A-Za-z0-9_]+\**)*\s*\([\s\S]+?\)\s*\{)') # find()containing args
	pat=re.compile(r'([A-Za-z0-9_]+\**\s+[A-Za-z0-9_]+\**(\s+[A-Za-z0-9_]+\**)*\s*\([\s\S]*?\)\s*\{)')
	# pat=re.compile(r'(\b[A-Za-z0-9_\ ]+\s+\b[A-Za-z0-9_]+\s*\(.*?\))(?=\s*\{)', re.DOTALL)
	pat_par=re.compile(r'\{|\}')	#find {}for fetch func
	
	c_func = pat.finditer(cont_c)
	
	fp = [i.end()-1 for i in pat_par.finditer(cont_c)]	#point to {
	# print("{}pos:",fp)
	c_name=[]  #c name
	c_pos=[]   #c pos
	c_cont=[]  #c content
    
	for c in c_func:
		t0,t = fetch_func(fp,c.start(),cont_c)
		cont_all = cont_c[c.start():t+1]
    
		if cont_all.find('block') < 0 and cont_all.find('thread') < 0:
			mingzi = re.sub(r'\s+', ' ', c.group()).split('(')[0].split(' ')[-1]	# mingzi => function name
			if mingzi not in stop_set and mingzi != '':
				c_name.append(mingzi)
				c_pos.append((t0,t+1))
				c_cont.append(cont_all)
  
    
	return c_name,c_pos,c_cont



def checkfunc(top_dir_c, top_dir_i):
    c_num = subprocess.Popen(f"find {top_dir_c} -name '*.c'|wc -l", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout = c_num.communicate()[0].decode()
    c_num = int(stdout)

    cu_num = subprocess.Popen(f"find {top_dir_c} -name '*.cu'|wc -l", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout = cu_num.communicate()[0].decode()
    cu_num = int(stdout)

    assert c_num == cu_num, f'Number of C files and Cuda files not match! C: {c_num} files, Cuda: {cu_num} files'

    set_dir = set()
    files_c = os.listdir(top_dir_c)
    print("Preprocessing C files...")
    with tqdm(total=c_num) as bar:
        for file_c in files_c:
            file_path = os.path.join(top_dir_c, file_c)
            if not file_path.endswith(".c"):
                continue
            target_path = os.path.join(top_dir_i, file_c)
            return_code = subprocess.Popen(f'gcc -E {file_path} -o {target_path}', stderr=subprocess.STDOUT, shell=True).wait()
            set_dir.add(file_c)
            bar.update(1)

    # check if all C files pass preprocess
    files_diff = os.listdir(top_dir_c)
    file_diffs = []
    for file_diff in files_diff:
        if not file_diff.endswith(".c"):
            continue
        if file_diff not in set_dir:
            file_diffs.append(file_diff)
    
    if len(file_diffs):
        print("WARNING:Following C files cannot be preprocessed by gcc -E:")
        for ff in file_diffs:
            print(ff)
        return

    # process para data
    print("Processing parallel data ...")
    cu_nofunc = []
    cu_morefunc = []
    c_nofunc = []
    c_morefunc = []
    dir_test = os.listdir(top_dir_c)
    with tqdm(total=c_num) as bar:
        for file in dir_test:
            # traverse Cuda files
            bar.update(1)
            file_path = os.path.join(top_dir_c, file)
            if not file_path.endswith(".cu"):
                continue
            # get c file path
            try:
                c_path = file[:-3] + ".c"
                c_file = c_path
                c_path = os.path.join(top_dir_i, c_path)
            except:
                continue
            
            # check C file
            stop = 0
            with open(c_path, 'r') as f_c:
                cont_c = f_c.read()
                c_name, _, c_cont = c_func_info(cont_c)
                # dic_c = dict(zip(c_name, c_cont))
                if not len(c_name):
                    c_nofunc.append(c_file)    
                if len(c_name)>=2:
                    c_morefunc.append(c_file)
                    
            
        
            # check Cuda file
            
            with open(file_path, 'r') as f_cu:
                cont_cu = f_cu.read()
                cu_name, _, cu_cont = cuda_func_info(cont_cu)
                # dict_cu = dict(zip(cu_name, cu_cont))
                if not len(cu_name):
                    cu_nofunc.append(file)
                    print("WARNING:Cuda Failed files below:(Maybe functions in these files are not legal standalone functions)\n", file)
                if len(cu_name)>=2:
                    cu_morefunc.append(file)
                    print("WARNING: more than one function in one file:(Maybe contain #pragma etc in these files)\n", file)

            
    # output C error
    if len(c_nofunc):
        print("WARNING:C Failed files below:(Maybe functions in these files are not legal standalone functions)")
        for ff in c_nofunc:
            print(ff)
        stop = 1
    if len(c_morefunc):
        print("WARNING: more than one function in one file:(Maybe contain #pragma etc in these files)")
        for ff in c_morefunc:
            print(ff)
        stop = 1
    if stop:
        return
    
    # output Cuda error
    if len(cu_nofunc):
        print("WARNING:C Failed file:(Maybe functions in these files are not legal standalone functions)")
        for ff in cu_nofunc:
            print(ff)
        stop = 1
    if len(cu_morefunc):
        print("WARNING: more than one function in one file:(Maybe contain #pragma etc in these files)")
        for ff in cu_morefunc:
            print(ff)
        stop = 1
    if stop:
        return
    
    print("All data files passed Successfully!")
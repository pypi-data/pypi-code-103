#! /usr/bin/env python3


# need to make concurrent processes output to old_hits.txt and a parser process to kill overlapping searches
# need to implement modulairty/pymcl
 
import multiprocessing as mp
import pickle, glob, os, subprocess, argparse, datetime, \
    time, re, shutil, tarfile, gzip, copy, sys, random


def collect_files( directory = './', filetype = '*', recursive = False ):
    '''
    Inputs: directory path, file extension (no "."), recursivity bool
    Outputs: list of files with `filetype`
    If the filetype is a list, split it, else make a list of the one entry.
    Parse the environment variable if applicable. Then, obtain a clean, full
    version of the input directory. Glob to obtain the filelist for each
    filetype based on whether or not it is recursive.
    '''

    if type(filetype) == list:
        filetypes = filetype.split()
    else:
        filetypes = [filetype]

    directory = formatPath( directory )
    filelist = []
    for filetype in filetypes:
        if recursive:
            filelist.extend(
                glob.glob( directory + "/**/*." + filetype, recursive = recursive )
            )
        else:
            filelist.extend(
                glob.glob( directory + "/*." + filetype, recursive = recursive )
            )

    return filelist


def expandEnvVar( path ):
    '''Expands environment variables by regex substitution'''

    if path.startswith( '/$' ):
        path = '/' + path
    env_comp = re.compile( r'/\$([^/]+)' )
    if not env_comp.search( path ):
        env_comp = re.compile( r'^\$([^/]+)' )
    var_search = env_comp.search( path )
    if var_search:
        var = var_search[1]
        pathChange = os.environ[ var ]
        path = env_comp.sub( pathChange, path )

    return path


def formatPath( path, isdir = None ):
    '''Goal is to convert all path types to absolute path with explicit dirs'''
   
    if path:
        path = os.path.expanduser( path )
        path = expandEnvVar( path )
        path = os.path.abspath( path )
        if isdir:
            if not path.endswith('/'):
                path += '/'
        else:
            if path.endswith( '/' ):
                if path.endswith( '//' ):
                    path = path[:-1]
                if not os.path.isdir( path ):
                    path = path[:-1]
            elif not path.endswith( '/' ):
                if os.path.isdir( path ):
                    path += '/'

    return path

def eprint( *args, **kwargs ):
    '''Prints to stderr'''

    print(*args, file = sys.stderr, **kwargs)


def zprint(out_str, log = None, flush = True):
    fprint(out_str, log)
    print(out_str, flush = flush)

def vprint( toPrint, v = False, e = False , flush = True):
    '''Boolean print option to stdout or stderr (e)'''

    if v:
        if e:
            eprint( toPrint, flush = True)
        else:
            print( toPrint, flush = True)


def intro( script_name, args_dict, credit='', log = False, stdout = True):
    '''
    Inputs: script_name string, args_dict dictionary of arguments,
    credit string bool / path for output log
    Outputs: prints an introduction, returns start_time in YYYYmmdd format
    Creates a string to populate and format for the introduction using
    keys as the left-most descriptor and arguments (values) as the right
    most. Optionally outputs a log according to `log` path.
    '''

    start_time = datetime.datetime.now()
    date = start_time.strftime( '%Y%m%d' )

    out_str = '\n' + script_name + '\n' + credit + \
        '\nExecution began: ' + str(start_time)

    for arg in args_dict:
        out_str += '\n' + '{:<30}'.format(arg.upper() + ':') + \
            str(args_dict[ arg ])

    if log:
        zprint(out_str, log)
    elif stdout:
        print(out_str, flush = True)
    else:
        eprint( out_str, flush = True )

    return start_time

def outro( start_time, log = False, stdout = True ):
    '''
    Inputs: start time string formatted YYYYmmdd, log path
    Outputs: prints execution time and exits with 0 status
    '''


    end_time = datetime.datetime.now()
    duration = end_time - start_time
    dur_min = duration.seconds/60
    out_str = '\nExecution finished: ' + str(end_time) + '\t' + \
            '\n\t{:.2}'.format(dur_min) + ' minutes\n'

    if log:
        zprint(out_str, log)
    elif not stdout:
        eprint(out_str, flush = True)
    else:
        print(out_str, flush = True)

    sys.exit(0)


def findExecs( deps, exit = set(), verbose = True ):
    '''
    Inputs list of dependencies, `dep`, to check path.
    If dependency is in exit and dependency is not in path,
    then exit.
    '''

    vprint('\nDependency check:', v = verbose, e = True, flush = True)
    checks = []
    if type(deps) is str:
        deps = [deps]
    for dep in deps:
        check = shutil.which( dep )
        vprint('{:<15}'.format(dep + ':', flush = True) + \
            str(check), v = verbose, e = True)
        if not check and dep in exit:
            eprint('\nERROR: ' + dep + ' not in PATH', flush = True)
            sys.exit(300)
        else:
            checks.append(check)

    return checks

def runWC(file_):
    with open(file_, 'r') as raw:
        return sum(1 for line in raw)
#    check_lines = subprocess.run([
 #       'wc', '-l', file_
  #      ], stdout = subprocess.PIPE
   #     )
    #return int(check_lines.stdout.decode('utf-8').rstrip().split(' ')[0])


def rmZeros(row_file, mtx_dir):

    zeros = {}
    with open(row_file + '.tmp', 'w') as out:
        with open(row_file, 'r') as raw:
            for line in raw:
                entries = line.rstrip().split('\t')
                if not entries[2:]:
                    init = int(line[:line.find('\t')])
                    zeros[init] = line
                else:
                    vals = [int(x.split(':')[0]) for x in entries[2:]]
                    for x in vals:
                        if x in zeros:
                            out.write(zeros[x])
                            del zeros[x]
                    out.write(line)

    os.rename(row_file + '.tmp', row_file)
    with open(mtx_dir + 'zeros.txt', 'w') as out:
        out.write('\n'.join([str(x) for x in list(zeros)]))

    return set(zeros)


def createSubgraphsAsym(row_file, mtx_dir, index):

    # must start from lowest index first and progress for this function to work
    graph_file = mtx_dir + 'sub.' + str(index) + '.mtx'
    hits, old_hits = set(), {index}
    with open(graph_file + '.tmp0', 'w') as out:
        with open(row_file, 'r') as raw:
            for line in raw:
                init = int(line[:line.find('\t')])
                if init == index:
                    entries = line.rstrip().split('\t')
                    for entry in entries[2:]:
                        info = [x for x in entry.split(':')]
                        out.write(str(init) + ' ' + info[0] + ' ' + info[1] + '\n')
                        hit = int(info[0])
#                        if hit not in zeros: # it wouldn't be a zero if it was in another
                        hits.add(int(info[0]))
                    break

        hits_file = open(mtx_dir + 'sub.' + str(index) + '.tmp_hits.txt', 'w')
        hits_file.write(str(index) + '\n')
        all_hits = hits.union(old_hits)
        cont, other_hits = True, set()
        while hits or cont:
            if other_hits == hits and hits: #either an error or the file was changed
#                print('\tERROR: value(s) without rows ' + str(hits), flush = True)
 #               sys.exit(17)
                old_hits = set()
                break
            other_hits = copy.deepcopy(hits)
            cont = False
            with open(row_file, 'r') as raw:
                for line in raw:
                    init = int(line[:line.find('\t')])
                    entries = line.rstrip().split('\t')
                    info = [x.split(':') for x in entries[2:]]
                    if init in hits or any(int(x[0]) in all_hits for x in info):
                        if init not in old_hits:
                            cont = True
                            for d in info:
                                hit = int(d[0])
                                if hit not in old_hits:
                                    out.write(str(init) + ' ' + d[0] + ' ' + d[1] + '\n')
#                                    if hit not in zeros:
                                    hits.add(hit)
                                    all_hits.add(hit)
                            old_hits.add(init)
                            hits_file.write(str(init) + '\n')
                            all_hits.add(init)
                            if init in hits:
                                hits.remove(init)

    hits_file.close()
    if len(old_hits) > 1:
        min_hit = min(list(old_hits))
        with open(mtx_dir + 'sub.' + str(min_hit) + '.old_hits.txt', 'w') as out:
            out.write('\n'.join([str(x) for x in old_hits]))
        os.rename(graph_file + '.tmp0', mtx_dir + 'sub.' + str(min_hit) + '.mtx.tmp1')
    else:
        os.remove(graph_file + '.tmp0')

    return old_hits 


def createSubgraphsSym(row_file, mtx_dir, index):

    graph_file = mtx_dir + 'sub.' + str(index) + '.mtx'
    # must start from lowest index first and progress for this function to work
    hits, old_hits = set(), {index}
    with open(graph_file + '.tmp0', 'w') as out:
        with open(row_file, 'r') as raw:
            for line in raw:
                init = int(line[:line.find('\t')])
                if init == index:
                    entries = line.rstrip().split('\t')
                    for entry in entries[2:]:
                        info = [x for x in entry.split(':')]
                        out.write(str(init) + ' ' + info[0] + ' ' + info[1] + '\n')
                        hits.add(int(info[0]))
                    break

        hits_file = open(mtx_dir + 'sub.' + str(index) + '.tmp_hits.txt', 'w')
        hits_file.write(str(index) + '\n')
        while hits:
            with open(row_file, 'r') as raw:
                for line in raw:
                    init = int(line[:line.find('\t')])
                    if init in hits:
                        entries = line.rstrip().split('\t')
                        for entry in entries[2:]:
                            info = [x for x in entry.split(':')]
                            hit = int(info[0])
                            if hit not in old_hits:
                                out.write(str(init) + ' ' + info[0] + ' ' + info[1] + '\n')
                                hits.add(hit)
                        old_hits.add(init)
                        hits_file.write(str(init) + '\n')
                        hits.remove(init)

    hits_file.close()
    if len(old_hits) > 1:
        min_hit = min(list(old_hits))
        with open(mtx_dir + 'sub.' + str(min_hit) + '.old_hits.txt', 'w') as out:
            out.write('\n'.join([str(x) for x in old_hits]))
        os.rename(graph_file + '.tmp0', mtx_dir + 'sub.' + str(min_hit) + '.mtx.tmp1')
    else:
        os.remove(graph_file + '.tmp0')

    return old_hits


def prep_mcl(graph_file, sym = True, output = subprocess.DEVNULL):

    prep_file = re.sub(r'\.tmp$', '', graph_file)
    if sym:
        conv_pipe = subprocess.call([
            'mcxload', '-abc', graph_file, '-o', prep_file,
            '--write-binary', '-write-tab',
            re.sub(r'\.mtx$', '.tsv', prep_file), '--stream-mirror'
            ], stdout = output, stderr = output #, stdin = subprocess.PIPE
            )
    else:
        conv_pipe = subprocess.call([
            'mcxload', '-abc', graph_file, '-o', prep_file,
            '--write-binary', '-write-tab',
            re.sub(r'\.mtx$', '.tsv', prep_file)
            ], stdout = output, stderr = output #, stdin = subprocess.PIPE
            )
    return prep_file


def conv_clus(clus_file, output = subprocess.DEVNULL):

    conv_cmd = subprocess.call([
        'mcxdump', '-icl', clus_file + '.tmp',
        '-o', clus_file, '--dump-pairs'
        ], stdout = output,
        stderr = subprocess.DEVNULL
        )
    os.remove(clus_file + '.tmp')


def run_mcl(
    graph_file, clus_file, inflation, 
    cpus = 1, sym = True, output = subprocess.DEVNULL
    ):

    vprint('\t\tRunning ' + os.path.basename(clus_file), flush = True, v = not output)
    prep_file = prep_mcl(graph_file, sym)
    os.remove(graph_file)
    mcl_cmd = subprocess.call([
        'mcl', prep_file, '-o', clus_file + '.tmp',
        '-I', str(inflation), '-te', str(cpus)],
        stdout = subprocess.DEVNULL, stderr = output
        )
    conv_clus(clus_file)


def reload_subgraph(mtx_dir, row_file, complete_file, zero_file):
    with open(complete_file, 'r') as raw:
        old_indices = set([int(x[:x.find('\t')]) for x in raw])
#        old_indices = set([int(x.rstrip()) for x in raw])
    if os.path.isfile(zero_file):
        with open(zero_file, 'r') as raw:
            zeros = set([int(x.rstrip()) for x in raw])
    else:
        zeros = set()
    with open(row_file + '.tmp', 'w') as out:
        with open(row_file, 'r') as raw:
            for line in raw:
                d = int(line[:line.find('\t')])
                if d in old_indices:
                    continue
                out.write(line)
    os.rename(row_file + '.tmp', row_file)

    return old_indices, zeros


def checkOverlappingRuns(procs, mtx_dir, verbose = False):

    tmp_hits = collect_files(mtx_dir, 'tmp_hits.txt')
    hit_sets = {}
    for f in tmp_hits:
        rows = re.sub(r'tmp_hits.txt$', 'mtx.tmp0', f)
        if not os.path.isfile(rows):
            os.remove(f)
        else:
            b = int(os.path.basename(f).replace('sub.','').replace('.tmp_hits.txt',''))
            with open(f, 'r') as raw:
                hits = set([int(x.rstrip()) for x in raw])
            hit_sets[b] = hits

    hit_keys, todel = list(hit_sets.keys()), {}
    for i0, key0 in enumerate(hit_keys): # could be improved to imply overlap
        hit0 = hit_sets[key0]
        for i1, key1 in enumerate(hit_keys[i0 + 1:]):
            hit1 = hit_sets[key1]
            if hit0.intersection(hit1):
                if len(hit0) > len(hit1):
                    if key1 not in todel:
                        todel[key1] = []
                    todel[key1].append(key0)
                else:
                    if key0 not in todel:
                        todel[key0] = []
                    todel[key0].append(key1)

    for del_key, del_hits in todel.items():
        if len(del_hits) > 1:
            del_hits = sorted(
                del_hits, key = lambda x: len(hit_sets[x]), reverse = True
                )
            for i, del_hit in enumerate(del_hits[1:]):
                if del_hit in procs:
                    procs[del_hit].terminate()
                    del_base = mtx_dir + 'sub.' + str(del_hit)
                    del_files = [
                        del_base + '.mtx.tmp0', del_base + '.tmp_hits.txt'
                        ]
                    for f in del_files:
                        if os.path.isfile(f):
                            os.remove(f)
                    del procs[del_hit]
                    vprint('\t\tOVERLAP REMOVED ' + str(del_hit), flush = True, v = verbose)
        if del_key in procs:
            procs[del_key].terminate()
            del_base = mtx_dir + 'sub.' + str(del_key)
            del_files = [
                del_base + '.mtx.tmp0', del_base + '.tmp_hits.txt'
                ]
            for f in del_files:
                if os.path.isfile(f):
                    os.remove(f)
            vprint('\t\tOVERLAP REMOVED ' + str(del_key), flush = True, v = verbose)
            del procs[del_key]

    return procs
           


def subgraphMngr(
    clusters, mtx_dir, row_file,
    old_indices = set(), sym = True, zeros = {}, cpus = 2,
    verbose = False
    ):

    cpus -= 1
    complete_file, procs, to_run = mtx_dir + 'complete.txt', {}, []
    # 0 is often the largest cluster, so let's start here
    if 0 not in zeros:
        if sym:
            procs[0] = (mp.Process(
                target = createSubgraphsSym,
                args=(row_file, mtx_dir, 0)
                ))
        else:
            procs[0] = (mp.Process(
                target=createSubgraphsAsym,
                args=(
                    row_file, mtx_dir, 0
                    )
                ))
        procs[0].start() 

    clus_range_prep = list(range(1, clusters))
    clus_range = list(set(clus_range_prep).difference(zeros))
    random.shuffle(clus_range)
    for i0 in clus_range:
        if i0 not in old_indices:
            while len(procs) == cpus:

                todel = []
                for i1, proc in procs.items():
                    if not proc.is_alive():
                        todel.append(i1)
                        proc.join()
                done_subgraphs = collect_files(mtx_dir, 'mtx.tmp1')
                for subgraph in done_subgraphs:
                    old_file = re.sub(r'mtx.tmp1$', 'old_hits.txt', subgraph)
                    with open(old_file, 'r') as raw:
                        rec_old_indices = set([int(x.rstrip()) for x in raw])
                    old_indices = old_indices.union(rec_old_indices)
                    with open(row_file + '.tmp', 'w') as row_out:
                        with open(row_file, 'r') as raw:
                            with open(complete_file, 'a') as comp_out: 
                                for line in raw:
                                    d = int(line[:line.find('\t')])
                                    if d in rec_old_indices:
                                        comp_out.write(line)
                                        continue
                                    row_out.write(line)
                    os.rename(row_file + '.tmp', row_file)
                    os.rename(subgraph, subgraph[:-1])

                procs = checkOverlappingRuns(procs, mtx_dir, verbose) # only worry when bottlenecked
                for i1 in reversed(todel):
                    del procs[i1]
                    
            if sym:
                procs[i0] = (mp.Process(
                    target = createSubgraphsSym,
                    args=(row_file, mtx_dir, i0)
                    ))
                procs[i0].start()
            else:
                procs[i0] = (mp.Process(
                    target=createSubgraphsAsym,
                    args=(
                        row_file, mtx_dir, i0
                        )
                    ))
                procs[i0].start() 


def mclMngr(
    subgraph_proc, processes, mtx_dir, inflation, 
    output = subprocess.DEVNULL
    ):

    complete_prep = collect_files(mtx_dir, 'clus')
    complete = set([re.sub(r'clus$', 'mtx.tmp', x) for x in complete_prep])

    procs = []
#    init_mtx = mtx_dir + 'sub.0.mtx.tmp'
 #   if os.path.isfile(init_mtx):
  #      clus = mtx_dir + 'sub.0.clus'
   #     init_proc = mp.Process(
    #        target=run_mcl,
     #       args=(
      #          init_mtx, clus,
       #         inflation, 2, sym, output
        #        )
         #   )
#        init_proc.start()
 #       init_proc.join()
  #      complete.add(init_mtx)
#    elif not os.path.isfile(init_mtx[:-4]):
 #       print('\t\tWARNING: No connections from index 0. Is this true?', flush = True)

    while subgraph_proc.is_alive():
        to_del = []
        for i, proc in enumerate(procs):
            if not proc.is_alive():
                to_del.append(i)
        for entry in reversed(to_del):
            procs[entry].join()
            del procs[entry]

        mtx_files = collect_files(mtx_dir, '[0-9]*.mtx.tmp')
        to_run = [x for x in mtx_files if x not in complete]
        while len(procs) < 1:
            try:
                mtx = to_run[0]
            except IndexError:
                break
            clus = re.sub(r'\.mtx.tmp$', '.clus', mtx)
            procs.append(mp.Process(
                target=run_mcl,
                args=(mtx, clus, inflation, 2, sym, output)
                ))
            complete.add(mtx)
            procs[-1].start()
            del to_run[0]
        time.sleep(1)

    subgraph_proc.join()
    mtx_files = collect_files(mtx_dir, '[0-9]*.mtx.tmp')
    to_run = [x for x in mtx_files if x not in complete]

    while to_run or procs:
        to_del = []
        for i, proc in enumerate(procs):
            if not proc.is_alive():
                to_del.append(i)
        for entry in reversed(to_del):
            procs[entry].join()
            del procs[entry]
        while len(procs) < processes and to_run:
            mtx = to_run[0]
            clus = re.sub(r'\.mtx.tmp$', '.clus', mtx)
            procs.append(mp.Process(
                target=run_mcl,
                args=(mtx, clus, inflation, 2, sym, output)
                ))
            procs[-1].start()
            complete.add(mtx)
            del to_run[0]
        time.sleep(1)


def clusteringMngr(
    cluster_len, row_file, mtx_dir, inflation, cpus, 
    sym = True, output = subprocess.DEVNULL
    ):

    zeros, complete_file = {}, mtx_dir + 'complete.txt'
    if os.path.isfile(complete_file):
        old_indices, zeros = reload_subgraph(
            mtx_dir, row_file, complete_file, mtx_dir + 'zeros.txt'
            )
    else:
        zeros, old_indices = set(), set()
#        if not sym:
        zeros = rmZeros(row_file, mtx_dir)
#            old_indices = createSubgraphsAsym(row_file, mtx_dir, 0)
 #           old_indices = old_indices.union(zeros)
                 
  #      with open(row_file + '.tmp', 'w') as out:
   #         with open(row_file, 'r') as raw:
    #            for line in raw:
     #               d = int(line[:line.find('\t')])
      #              if d in old_indices:
       #                 continue
        #            out.write(line)
       # os.rename(row_file + '.tmp', row_file)

    v = False
    if output is not subprocess.DEVNULL:
        v = True

    subgraph_proc = mp.Process(
        target = subgraphMngr, 
        args = (cluster_len, mtx_dir, row_file, old_indices, sym, zeros, cpus, v)
        )
    subgraph_proc.start()
    mclMngr(subgraph_proc, cpus - 1, mtx_dir, inflation, output)


def clusteringMngrSingle(cluster_len, row_file, mtx_dir, inflation, sym = True, output = subprocess.DEVNULL):

    zeros = rmZeros(row_file)
    if sym:
        old_indices = createSubgraphsSym(row_file, mtx_dir, 0)
        if os.path.isfile(mtx_dir + 'sub.0.mtx.tmp1'):
            os.rename(mtx_dir + 'sub.0.mtx.tmp1', mtx_dir + 'sub.0.mtx')
    else:
        old_indices = createSubgraphsAsym(row_file, mtx_dir, 0)
        old_indices = old_indices.union(zeros)
        if os.path.isfile(mtx_dir + 'sub.0.mtx.tmp1'):
            os.rename(mtx_dir + 'sub.0.mtx.tmp1', mtx_dir + 'sub.0.mtx')

    to_run = []
    for i in range(1, cluster_len):
        if i not in old_indices:
            mtx_file, clus_file = mtx_dir + str(i) + '.mtx', mtx_dir + str(i) + '.clus'
            old_indices = old_indices.union(
                createSubgraphsSym(row_file, mtx_dir, i)
                )
            if os.path.isfile(mtx_dir + 'sub.' + str(i) + '.mtx.tmp1'):
                os.rename(mtx_dir + 'sub.' + str(i) + '.mtx.tmp1', mtx_dir + 'sub.' + str(i) + '.mtx')
                to_run.append(mtx_file, clus_file)

    for files in to_run:
        run_mcl(files[0], files[1], inflation, 2, sym, output)


def readSubclusters(mtx_dir, out_dir, clusLen):

    master_file = mtx_dir + 'labels.tsv'
    clus_files = collect_files(mtx_dir, '[0-9]*.clus')

    master_conv = {}
    if os.path.isfile(master_file):
        with open(master_file, 'r') as raw:
            for line in raw:
                data = [int(x) for x in line.rstrip().split('\t')]
                master_conv[data[0]] = data[1]

    clusters = []
    for clus_file in clus_files:
        sub_file = re.sub(r'\.clus$', '.tsv', clus_file)
        t_clus = {}
        with open(clus_file, 'r') as raw:
            for line in raw:
                data = [int(x) for x in line.rstrip().split('\t')]
                if data[0] not in t_clus:
                    t_clus[data[0]] = []
                t_clus[data[0]].append(data[1])

        t_conv = {}
        with open(sub_file, 'r') as raw:
            for line in raw:
                data = [int(x) for x in line.rstrip().split('\t')]
                t_conv[data[0]] = data[1]

        init_conv = [
            [t_conv[y] for y in t_clus[x]] for x in t_clus
            ]
        if master_conv:
            conv_clus = [
                [master_conv[y] for y in x] for x in init_conv
                ]
            clusters.extend(conv_clus)
        else:
            clusters.extend(init_conv)

    if os.path.isfile(mtx_dir + 'zeros.txt'):
        with open(mtx_dir + 'zeros.txt', 'r') as zeros:
            init = [[int(y.rstrip())] for y in zeros]
            if master_conv:
                conv_clus = [[mast_conv[y[0]]] for y in init]
                clusters.extend(conv_clus)
            else:
                clusters.extend(init)

    clusIndices = set()
    with gzip.open(out_dir + 'mcl.res.gz', 'wt') as out:
        for i, clus in enumerate(clusters):
            for hit in clus:
                out.write(str(i) + '\t' + str(hit) + '\n')
                clusIndices.add(int(hit))

    missing, count = set(range(clusLen)).difference(clusIndices), len(clusters)
    with gzip.open(out_dir + 'mcl.res.gz', 'at') as out:
        for miss in missing:
            out.write(str(count) + '\t' + str(miss) + '\n')
            count += 1
    

    with tarfile.open(mtx_dir[:-1] + '.tar.gz', 'w:gz') as tar:
        tar.add(mtx_dir, arcname = os.path.basename(mtx_dir[:-1]))
    shutil.rmtree(mtx_dir)

    return tuple([tuple(x) for x in clusters])


def prep4subgraph(mcxdump, file_in, file_out, output = subprocess.DEVNULL):
    return subprocess.call([
        mcxdump, '-imx', file_in, 
        '--dump-vlines', '-o', file_out
        ], stdout = output,
        stderr = output
        )
       
def writeMCLformat(clusters, out_dir):

    clusters = sorted(clusters, key = lambda x: len(x), reverse = True)
    clusters = [list(x) for x in clusters]
    for v in clusters:
        v.sort()
    with open(out_dir + 'clus.mcl.txt', 'w') as out:
        out.write(
            '# cline: bigmcl\n(mclheader\nmcltype matrix\ndimensions ' + \
            str(sum([len(x) for x in clusters])) + 'x' + str(len(clusters)) + \
            '\n)\n(mclmatrix\nbegin\n'
            )
        for i, v in enumerate(clusters):
            out.write(str(i) + '       ')
            out.write(' '.join([str(x) for x in v[:10]]))
            for start in range(10, len(v), 10):
                out.write('\n         ' + ' '.join([str(x) for x in v[start:start+10]]))
            out.write(' $\n')
        out.write(')')



def main(graph_in, mcxdump, inflation, out_dir, mclOut = True, row_file = None, sym = False, cpus = 1, verbose = True):

    mtx_dir = out_dir + 'mtx/'
    if not os.path.isdir(mtx_dir):
        os.mkdir(mtx_dir)

    if verbose:
        output = None
    else:
        output = subprocess.DEVNULL

    if os.path.isfile(out_dir + 'mcl.res.gz') and mclOut:
        print('\nReloading clusters and converting to MCL format', flush = True)
        clus_dict = {}
        with gzip.open(out_dir + 'mcl.res.gz', 'rt') as raw:
            for line in raw:
                d = [int(x) for x in line.rstrip().split('\t')]
                if d[0] not in clus_dict:
                    clus_dict[d[0]] = []
                clus_dict[d[0]].append(d[1])
        clusters = []
        for i in clus_dict:
            clusters.append(clus_dict[i])
        writeMCLformat(clusters, out_dir)
        print('\nComplete\n', flush = True)
        sys.exit(0)

    print('\nI. Outputting parseable rows', flush = True)
    if not row_file:
        row_file = mtx_dir + 'rows.txt'
        prep4subgraph(mcxdump, graph_in, row_file, output)

    print('\tAcquiring number of inputs', flush = True)
    in_len = runWC(row_file)
    if os.path.isfile(mtx_dir + 'complete.txt'):
        in_len += runWC(mtx_dir + 'complete.txt')
    print('\t' + str(in_len), flush = True)
    
    print('\nII. Subgraphing and MCL', flush = True)
    if cpus > 1:
        clusteringMngr(
            in_len, row_file, mtx_dir, inflation, 
            cpus = cpus, sym = sym, output = output
            )
    else:
        clusteringMngrSingle(in_len, row_file, mtx_dir, inflation, sym = sym, output = output)

    print('\nIII. Parsing clusters', flush = True)
    clusters = readSubclusters(mtx_dir, out_dir, in_len)

    if mclOut:
        writeMCLformat(clusters, out_dir)
#    with open(out_dir + 'clusters.pickle', 'wb') as out:
 #       pickle.dump(clusters)

    return out_dir + 'clus.mcl.txt'


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description = \
        "Isolates disconnected graphs and runs MCL on the subgraphs. Input data must be numerical."
        )
    parser.add_argument('-i', '--input', help = 'MCL graph file in imx format', required = True)
    parser.add_argument('-I', '--inflation', required = True)
    parser.add_argument('-s', '--symmetric',
        help = 'Matrix is symmetric (throughput increase)', action = 'store_true', default = False)
    parser.add_argument('-r', '--row_file', help = 'Continue from finished row.txt')
    parser.add_argument('-m', '--mcl_format', action = 'store_true', help = 'Output clusters in MCL format')
    parser.add_argument('-o', '--output', help = 'Alternative output directory')
    parser.add_argument('-c', '--cores', default = 1, type = int)
    parser.add_argument('-v', '--verbose', action = 'store_true')
    args = parser.parse_args()

    deps = findExecs(['mcxdump', 'wc'], exit = {'mcxdump', 'wc'})
    mcxdump = deps[0]

    start_time = intro('Bigmcl.py - an MCL subgraphing procedure', {
        'Graph file': formatPath(args.input), 'Inflation': args.inflation,
        'Symmetric': args.symmetric, 'Row file': args.row_file, 'MCL format': args.mcl_format,
        'Output': args.output, 'Cores': args.cores
        })

    if not args.output:
        date = start_time.strftime('%Y%m%d')
        output = os.getcwd() + '/' + date + '_bigmcl/'
        if not os.path.isdir(output):
            os.mkdir(output)
        output = formatPath(output)
    else:
        if not os.path.isdir(args.output):
            os.mkdir(args.output)
        output = formatPath(args.output)

    main(
        formatPath(args.input), mcxdump, args.inflation, output, args.mcl_format,
        args.row_file, args.symmetric, args.cores, args.verbose
        )
    outro(start_time)

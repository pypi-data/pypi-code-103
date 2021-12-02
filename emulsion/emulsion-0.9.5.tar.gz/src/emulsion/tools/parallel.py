"""A Python implementation of the EMuLSion framework.
(Epidemiologic MUlti-Level SImulatiONs).

Tools for parallel computing.

"""
import multiprocessing           as     mp

from   emulsion.tools.simulation import MultiSimulation, SensitivitySimulation

def job_dist(total_task, workers):
    """ Return a distribution of each worker need to do.

    """
    nb = total_task // workers
    rest = total_task % workers
    return [nb+1 if i <= rest-1 else nb for i in range(workers)]

def job(target_simulation_class, proc, **others):
    """ Simple job for a simple processes

    """
    simu = target_simulation_class(proc=proc, **others)
    simu.run()
    simu.write_dot()
    # simu.counts_to_csv()

def parallel_multi(target_simulation_class=MultiSimulation, nb_simu=None,
                   nb_proc=1, **others):
    """ Parallel loop for distributing tasks in different processes

    """
    list_proc = []
    list_nb_simu = job_dist(nb_simu, nb_proc)

    for i in range(nb_proc):
        others['nb_simu'] = list_nb_simu[i]
        others['start_id'] = sum(list_nb_simu[:i])
        proc = mp.Process(target=job, args=(target_simulation_class, i),
                          kwargs=others)
        list_proc.append(proc)
        proc.start()

    for proc in list_proc:
        proc.join()

def parallel_sensi(target_simulation_class=SensitivitySimulation, nb_proc=1,
                   **others):
    """ Parallel loop for distributing sensitivity tasks in different processes

    """
    list_proc = []
    list_nb_simu = job_dist(len(others['df']), nb_proc)

    for i in range(nb_proc):
        others['nb_multi'] = list_nb_simu[i]
        others['start_id'] = sum(list_nb_simu[:i])
        proc = mp.Process(target=job, args=(target_simulation_class, i),
                          kwargs=others)
        list_proc.append(proc)
        proc.start()

    for proc in list_proc:
        proc.join()

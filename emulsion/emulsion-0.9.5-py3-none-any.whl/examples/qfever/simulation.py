"""Dairy cow QFever disease model.
IBM, stochastic model

Author: Yu-Lin Huang

This code contain the simulator of qfever model.
"""
import numpy                                      as np
import multiprocessing                            as mp
import pandas                                     as pd

from   pathlib                                    import Path
from   emulsion.tools.state                       import StateVarDict
from   emulsion.tools.wind                        import plume_ermak
from   emulsion.model                             import EmulsionModel
from   emulsion.examples.qfever.simplified_agents import QfeverHerd, Cow

def job_dist(total_nb, workers):
    """ Return a distribution of each worker need to do.

    """
    nb=int(total_nb/workers)
    rest=total_nb-nb*workers
    return [nb+1 if i<=rest-1 else nb for i in range(workers)]

def within_herd_job(param, n):
    """ Simple job for a simple processes 

    """
    simulation = WithinHerdSimulation(param)
    simulation.run()
    simulation.output(proc=n)

def parallel_run(nb_proc, param, job = within_herd_job):
    """ Parallel loop for distributing tasks in different processes

    """
    list_proc = []
    list_nb_simu = job_dist(param.nb_simu, nb_proc)

    for i in range(nb_proc):
        p = StateVarDict(param)
        p.nb_simu = list_nb_simu[i]
        proc = mp.Process(target=job, args=(p, i))
        list_proc.append(proc)
        proc.start()

    for proc in list_proc:
        proc.join()

class BetweenHerdTestSimulation(object):
    """BetweenHerd test class
    !!!!!!!!!TODO!!!!!!!!! Change structure (not passing by Simulation)
    Pass by a SetViewCompartiment?????
    """
    def __init__(self, param, path = 'config/qfever/qfever-yulin.yaml'):
        super(BetweenHerdTestSimulation, self).__init__()
        self.param = param
        self.path = path

    def get_infected_herd(self):
        """Return a infected herd in a steady regime (disease established).
        To do so, we choose a herd initially infected by an infected animal
        and in which the disease persist after 200 time setps.

        """
        p = StateVarDict(self.param)
        p.longitude = 0.
        p.latitude = 0.

        persistence = 0
        while persistence==0:
            h = Simulation(p, path=self.path)
            h.run(steps=200)
            persistence = h.herd['infection'].counts['Persistence'][-1]

        return h

    def get_healthy_herd(self, longitude, latitude):
        """Return a healthy herd (not infected) with given longitude
        and latitude. 

        """
        p = StateVarDict(self.param)
        p.longitude = longitude
        p.latitude = latitude
        return Simulation(p, path=self.path, infected=False)

    def construct_herd(self):
        """Construct a series of herd for testing the wind propagation.

        """
        self.d_simu = {'origin': self.get_infected_herd()}
        self.d_simu.update({str(x): self.get_healthy_herd(200.*x, 0.) for x in range(1, 26)})
        self.d_simu['out_of_range_x'] = self.get_healthy_herd(-200., 0.)
        self.d_simu['out_of_range_y1'] = self.get_healthy_herd(0., 200.)
        self.d_simu['out_of_range_y2'] = self.get_healthy_herd(0., -200.)

    def wind_propagation(self):
        origin_simu = self.d_simu['origin']
        quantity = origin_simu.herd.Eout
        for key, simu in self.d_simu.items():
            if key != 'origin':
                Eplume = plume_ermak(5, quantity, simu.param.longitude, simu.param.latitude)
                Eplume *= simu.param.init_pop*17
                simu.herd.Eplume = Eplume

    def evolve(self, steps = 52):
        for step in range(steps):
            for simu in self.d_simu.values():
                simu.herd.evolve()
            self.wind_propagation()

    def output(self, simu_id=0):
        results = []
        for key, simu in self.d_simu.items():
            l_prevalence = simu.herd['infection'].counts['Prevalence']
            l_seroprevalence = simu.herd['infection'].counts['Seroprevalence']
            list_ = [simu_id, key, simu.param.longitude, simu.param.latitude]
            list_.append(l_prevalence[-1])
            list_.append(l_seroprevalence[-1])
            list_.append(simu.herd['infection'].counts['Eexcr'][-1])
            list_.append(int(sum(l_prevalence)!=0))
            firt_case_time = np.nonzero(l_prevalence)[0][0] if list_[-1] else 0
            list_.append(firt_case_time)
            firt_sero_time = np.nonzero(l_seroprevalence)[0][0] if int(sum(l_seroprevalence)!=0) else 0
            list_.append(firt_sero_time)
            results.append(list_)
        return results

    def run(self):
        headers = [ 'simu_id', 'herd_id', 'Longitude', 'Latitude', 'Prevalence', 'Seroprevalence',\
                    'Eexcr', 'InfectedOnce', 'FirstCaseTime', 'FirstSeroTime']
        results = []
        for simu in range(self.param.nb_simu):
            print('-'*10, simu, '/', self.param.nb_simu,'-'*10)
            self.construct_herd()
            self.evolve()
            results += self.output(simu_id=simu)
        res = pd.DataFrame(results, columns=headers)
        res.to_csv(str(Path(self.param.output_dir, 'results.csv')), index=False)


class ParellalWithinHerdSimulation(object):
    """The ParellalWithinHerdSimulation class handles several 
    WithinHerdSimulations

    """
    def __init__(self, param, path = 'config/qfever/qfever-yulin.yaml'):
        super(ParellalWithinHerdSimulation, self).__init__()
        self.param = param
        self.path = path
        self.pool = mp.Pool()
        
    def function(self):
        param = self.param.copy()

class WithinHerdSimulation(object):
    """The WithinHerdSimulation class handles several simulation of qfever
    disease in a dairy herd
    """
    def __init__(self, param, path = 'config/qfever/qfever-yulin.yaml'):
        self.param = param
        self.path = path
        self.simulations = {id_: Simulation(self.param, id_=id_, path=self.path) for id_ in range(self.param.nb_simu)}

    def run(self):
        for simu in self.simulations.values():
            print('-'*10, simu.id, '-'*10)
            simu.run()

    def output(self, sep=' ', proc=None):
        """ Save dots for each state machine and the counts results in output firectory
        (TODO: change hard coded part for the process name when retrieving
        the counts and headers)
        """
        self.output_dot()
        filename = str(Path(self.param.output_dir, 'counts.csv')) if proc is None \
                    else str(Path(self.param.output_dir, 'counts_'+str(proc)+'.csv'))

        step_list = [x for x in range(self.param.steps+1)]*self.param.nb_simu
        id_list   = [x for x in range(self.param.nb_simu) for _ in range(self.param.steps+1)]

        infection_list, infection_headers = self.get_list('infection')
        lifecycle_list, lifecycle_headers = self.get_list('lifecycle')
        parity_list, parity_headers = self.get_list('parity_grouping')

        final_list = [id_list ,step_list] + infection_list + lifecycle_list + parity_list
        final_headers = 'step ' + infection_headers + lifecycle_headers + parity_headers

        np.savetxt(filename, np.array(final_list).T, header=final_headers, comments='id ')

    def get_list(self, name):
        """Get the counts and headers associated with a given process name
        """
        list_ = None
        for i in range(self.param.nb_simu):
            simu = self.simulations[i]
            counts = simu.herd[name].counts
            headers = ' '.join([name for name in counts.keys()]) +' '
            temp_list = [value for value in counts.values()]
            if list_ is None:
                list_ = temp_list
            else:
                for j in range(len(list_)):
                    list_[j] += (temp_list[j])
        return list_, headers

    def output_dot(self):
        """ Save the dots correspond to each state machine.
        (TODO: this method should be coded in the EmulsionModel class (generical conception))
        """
        model = EmulsionModel(filename=self.path)
        for name, statemachine in model.state_machines.items():
            name += '.dot'
            p = str(Path(self.param.output_dir, name))
            statemachine.write_dot(p)

class Simulation(object):
    """The Simulation class handles a whole simulation of qfever
    disease in a dairy herd
    """
    def __init__(self, param, id_=0, path='config/qfever/qfever-yulin.yaml', infected = True):
        # ID of the simulation
        self.id = id_
        # Path of config file
        self.path = path
        # Bool which indicate infected or healthy herd
        self.infected = infected
        # parameters for this simulation
        self.param = param
        self.init_herd()

        self.herd.add_atoms(self.init_cows(), init=True)

        # Reset cows _time_spend, will be automatic in the future
        for cow in self.l_cows:
            cow.statevars._time_spent_life_cycle = self.get_random_cycle(cow.statevars.life_cycle.name)
        if infected:
            cow = self.l_cows[-1]
            cow.statevars._time_spent_life_cycle = self.get_max_cycle(cow.statevars.life_cycle.name)

    def get_random_cycle(self, lc): 
        return np.random.randint(
            0, self.herd.lifecycle.get_value(self.herd.lifecycle._statedesc[lc]['duration'])
        )
            
    def get_max_cycle(self, lc): 
        return self.herd.lifecycle.get_value(self.herd.lifecycle._statedesc[lc]['duration'])


    def init_herd(self):
        """Return a initialized herd.
        """
        herd_param = StateVarDict(self.param)
        self.herd = QfeverHerd(model=EmulsionModel(filename=self.path),
                               **herd_param)

    def init_states(self):
        """Return an initial population dictionary.
        """
        states = self.herd.lifecycle.states
        proba = [self.get_max_cycle(lc.name) for lc in states]
        proba = [x/sum(proba) for x in proba]

        healthy_pop = self.param.init_pop-1 if self.infected else self.param.init_pop
        init_nb = np.random.multinomial(healthy_pop, proba)
        {states(i+1) : init_nb[i] for i in range(len(states))}
        return {states(i+1) : init_nb[i] for i in range(len(states))}

    def init_cows(self):
        """Return a initial cow list. i.e Healthy cows with uniform life state 
        distribution and one infected cow (not vaccinated) with perform calving 
        in the next step.
        """
        param = self.param
        proba = param.parity_proba
        cows = [Cow(health_state=self.herd.disease.states.S,
                    life_cycle=lc,
                    parity=np.random.choice(len(proba), p = proba),
                    _time_spent_life_cycle=self.get_random_cycle(lc.name),
                    vaccinated=param.global_vaccinated,
                    last_infection=-1)
                for lc, quantity in self.init_states().items()
                for _ in range(quantity)]

        if self.infected:
            lc_states = self.herd.lifecycle.states
            lc_infected = lc_states(len(lc_states))
            cows.append(Cow(health_state=self.herd.disease.states['I+'],
                            life_cycle=lc_infected,
                            parity=0,
                            _time_spent_life_cycle=self.get_max_cycle(lc_infected.name),
                            vaccinated=0,
                            last_infection=-1))

        self.l_cows = cows         
        return self.l_cows

    def run(self, steps=None):
        nb_evolve = steps if steps else self.param.steps
        for step in range(nb_evolve):
            self.herd.evolve()

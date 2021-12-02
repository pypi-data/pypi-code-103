"""A Python implementation of the EMuLSion framework.

(Epidemiologic MUlti-Level SImulatiONs).

Classes and functions defining agents involved in the QFever IBM
model.

"""

import json
import yaml
import time
import numpy                    as     np
import pandas                   as     pd

from   sortedcontainers         import SortedDict
from   collections              import defaultdict
from   utm                      import to_latlon, from_latlon

from   emulsion.tools.wind      import plume_ermak, plume_gaussian, referential_transform
from   emulsion.tools.misc      import select_random
from   emulsion.agent.atoms     import AtomAgent
from   emulsion.agent.views     import AdaptiveView, StructuredView
from   emulsion.agent.managers  import GroupManager, MultiProcessManager

from   emulsion.model           import EmulsionModel


##----------------------------------------------------------------
## INDIVIDUALS

class Cow(AtomAgent):
    """The Cow class represents individuals in the hybrid (IBM +
    compartments) model of the QFever disease.

    """
    def __init__(self, **others):
        super().__init__(**others)
        self.nb_abortion = 0
        self.last_infection = -1

    @property
    def life_machine(self):
        """Provide access to the state machine in charge of the
        management of the life cycle of the cow.

        """
        return self.get_host(key=(self.statevars.life_cycle,)).get_host().state_machine

    @property
    def host_id(self):
        """Return the herd ID in which animal belongs to.

        """
        return self.get_host(key='MASTER').get_host().get_information('herd_id')

    @property
    def abortable(self):
        """Condition testing if the cow is likely to abort. According
        to the QFever model, pregnant cows could abort at any time of
        the gestation but with condition of during the 3 weeks following
        infection or resumption of shedding.
        """
        last_infection = self.last_infection
        bool_ = last_infection >0 and last_infection <= 3
        return int(bool_ and self.pregnant) #and not(self.too_old))

    @property
    def shedder(self):
        """Return True if the cow sheds bacteria, False otherwise. In
        the current model this corresponds to all 'I***' states. ###
        TODO: in future versions, replace this by convenient state
        properties.

        """
        return 'I' in self.statevars.health_state.name

    @property
    def pregnant(self):
        """Return True if the cow is pregnant (i.e. in the 'P' state
        of the life cycle), False otherwise.

        """
        return int(self.statevars.life_cycle.name == 'P')

    @property
    def early_abortion(self):
        """Return True if the abortion occurs during the beginning of
        the pregnancy, False otherwise.

        """
        return int(self.statevars._time_spent_life_cycle <=\
                   self.life_machine.get_value('max_abort'))

    @property
    def Etemp(self):
        """Return the amount of bacteria present in the temporary
        environment. This value is retrieved from the self. ### TODO:
        in future, the place to retrieve this value could be specified
        in the YAML config file, and the corresponding property
        implemented automatically.

        """
        return self.get_host(key='MASTER').get_host().Etemp

    @Etemp.setter
    def Etemp(self, value):
        """Modify the amount of bacteria present in the temporary
        environment. This value is retrieved from the self. ### TODO:
        in future versions, the place to retrieve this value could be
        specified in the YAML config file, and the corresponding
        property implemented automatically.

        """
        self.get_host(key='MASTER').get_host().Etemp = value

    @property
    def herd_abortion(self):
        """Return the amount of abortions occured in the herd.
        This value is retrieved from the self.
        ### TODO: This attribute is set with heath_state for
        a short time concern. But it will need to be integrated
        in life_cycle.

        """
        return self.get_host(key='MASTER').get_host().herd_abortion

    @herd_abortion.setter
    def herd_abortion(self, value):
        """Modify the amount of abortions occured in the herd.
        This value is retrieved from the self. ### TODO: See above.

        """
        self.get_host(key='MASTER').get_host().herd_abortion = value

    @property
    def herd_recursion_abortion(self):
        """Return the amount of cows which abort twice or more in the herd.
        This value is retrieved from the self.
        ### TODO: This attribute is set with heath_state for
        a short time concern. But it will need to be integrated
        in life_cycle.

        """
        return self.get_host(key='MASTER').get_host().herd_recursion_abortion

    @herd_recursion_abortion.setter
    def herd_recursion_abortion(self, value):
        """Modify the amount of cows which abort twice or more in the herd.
        This value is retrieved from the self. ### TODO: See above

        """
        self.get_host(key='MASTER').get_host().herd_recursion_abortion = value

    ### ACTIONS
    def increase_parity(self, **kwargs):
        """Increase the parity (number of calvings) of the cow."""
        self.statevars.parity += 1

    def shift_life_cycle(self, duration, **kwargs):
        """Modifies the time to spend in the next state of the life
        cycle by the specified duration.

        """
        self.set_time_to_live_offset('life_cycle', duration)

    def abortion_shed(self, amount, **kwargs):
        """Shed the specified amount of bacteria in the environment
        (special action when abortion occurs). And update abortion
        number of herd.

        """
        self.Etemp += amount
        self.nb_abortion += 1
        self.herd_abortion += 1
        if self.nb_abortion >=2:
            self.herd_recursion_abortion += 1

    def calving_shed(self, amount, **kwargs):
        """Shed the specified amount of bacteria in the environment
        (special action when a I+ cow calving new heifer).

        """
        if 'I+' == self.statevars.health_state.name:
            self.Etemp += amount

    def reset_last_infection(self, **kwargs):
        """Set the residence time in the (new) life cycle state to the
        specified value.

        """
        self.last_infection = 0

    def update_incidence_shedder(self, **kwargs):
        """Update the incidence status of the herd when presence of
        shedder.

        """
        self.get_host(key='MASTER').get_host().update_incidence_shedder()
        if self.get_information('origin_herd_id') == self.host_id:
            self.get_host(key='MASTER').get_host().update_local_incidence_shedder()

    def update_incidence_sero(self, **kwargs):
        """Update the incidence status of the herd when presence of
        sero-positive animals.

        """
        self.get_host(key='MASTER').get_host().update_incidence_sero()
        if self.get_information('origin_herd_id') == self.host_id:
            self.get_host(key='MASTER').get_host().update_local_incidence_sero()

    def evolve(self, machine):
        super().evolve()
        if self.last_infection >=0:
            self.last_infection+=1


##----------------------------------------------------------------
## COMPARTMENTS

class ObserverHealthStateComp(AdaptiveView):
    """This compartment is aimed at containing individuals (Cows) and
    managing their health state. The observed variables are the health
    state, the 'is_PC' state and the vaccination state. ### TODO: in
    future versions, this class should be removed, since the only
    properties used here are in charge of retrieving variables in the
    self.

    """
    ### Keys: health_state, is_PC, vaccinated
    # PROPERTIES
    @property
    def Eplume(self):
        return self.get_host().Eplume

    @property
    def Eexcr(self):
        return self.get_host().Eexcr

    @property
    def Eaero(self):
        return self.get_host().Eaero

    @property
    def Etemp(self):
        return self.get_host().Etemp

    @Etemp.setter
    def Etemp(self, value):
        self.get_host().Etemp = value

    @property
    def herd_population(self):
        return self.get_host().herd_population


class HealthStateDictComp(GroupManager):
    """This compartment is in charge of managing Cows in several
    health states. ### TODO: in future versions, this compartment
    should be removed, since the only properties used here are in
    charge of retrieving variables in the self. Besides, the
    aggregated values could be defined elsewhere and then added to the
    compartment.

    """
    def __init__(self, **others):
        super().__init__(**others)
#        self.mu = 1. - self.state_machine._values['mu']

    @property
    def Eexcr(self):
        return self.get_host().Eexcr

    @property
    def Eaero(self):
        return self.get_host().Eaero

    @property
    def Etemp(self):
        return self.get_host().Etemp

    @Etemp.setter
    def Etemp(self, value):
        self.get_host().Etemp = value

    @property
    def Eplume(self):
        return self.get_host().Eplume

    @property
    def herd_abortion(self):
        return self.get_host().herd_abortion

    @property
    def herd_recursion_abortion(self):
        return self.get_host().herd_recursion_abortion

    @property
    def herd_population(self):
        return self.get_host()['MASTER'].population

    def init_counts(self, index=0):
        super().init_counts(index=index)
        self.counts['N'] = [] if self.keep_history else 0
        self.counts['Eexcr'] = [] if self.keep_history else 0
        self.counts['Eaero'] = [] if self.keep_history else 0
        self.counts['Prevalence'] = [] if self.keep_history else 0
        self.counts['Seroprevalence'] = [] if self.keep_history else 0
        self.counts['Vaccinated'] = [] if self.keep_history else 0
        self.counts['Persistence'] = [] if self.keep_history else 0
        self.counts['CumulatedAbortion'] = [] if self.keep_history else 0
        self.counts['CumulatedRecursionAbortion'] = [] if self.keep_history else 0

    def update_counts(self, index=0):
        super().update_counts(index=index)
        total = {}
        total['N'] = (self.get_host()['MASTER'].population)
        total['Eexcr'] = (self.Eexcr)
        total['Eaero'] = (self.Eaero)
        total_pop = sum([self.counts[state.name][-1] if self.keep_history else self.counts[state.name]
                         for state in self.state_machine.states])
        total['Prevalence'] = (0 if total_pop == 0 else\
                                         sum([self.counts[state.name][-1] if self.keep_history else self.counts[state.name]
                                              for state in self.state_machine.states
                                              if 'I' in state.name]) / total_pop )
        total['Seroprevalence'] = (0 if total_pop == 0 else\
                                             sum([self.counts[state.name][-1] if self.keep_history else self.counts[state.name]
                                                  for state in self.state_machine.states
                                                  if '+' in state.name]) / total_pop)
        total['Vaccinated'] = (0 if total_pop == 0 else\
                                             sum([comp.population
                                                  for comp in self
                                                  if comp.keys[-1]]) / total_pop)
        total['Persistence'] = (0 if total['Prevalence'] == 0 and\
                                               total['Seroprevalence'] == 0 and\
                                               self.counts['L'] == 0 else 1)
        total['CumulatedAbortion'] = (self.herd_abortion)
        total['CumulatedRecursionAbortion'] = (self.herd_recursion_abortion)

        if self.keep_history:
            for key, value in total.items():
                self.counts[key].append(value)
        else:
            self.counts.update(total)


class ObserverLifeStateComp(AdaptiveView):
    """This compartment is in charge of handling parity changes among
    Cows. ### TODO: in future versions, this class should be removed,
    since the residence time in each state will be made implicit.

    """
    @property
    def life_machine(self):
        return self.get_host().state_machine

    # @property
    # def max_duration(self):
    #     return self.life_machine.get_value(
    #         self.life_machine.stateprops[self.statevars.life_cycle.name]['max_duration'])


class ParityDictComp(StructuredView):
    """This class is in charge of managing several parity
    compartments. ### TODO: in future versions, this class should be
    removed, since the current 'parity' variable type will move from
    'int' to 'enum', hence with a state name like other states of
    state machines.

    """
    def __init__(self, **others):
        super().__init__(**others)
        self.init_counts()

    def __contains__(self, keys):
        return keys in self._content

    def init_counts(self, index=0):
        self.counts = {'Parity'+str(p): [] if self.keep_history else 0 for p in range(8)}

    def update_counts(self, index=0):
        if not self.keep_history:
            self.init_counts(index=index)
        total = {'Parity'+str(p): 0 for p in range(8)}
        for (key, unit) in self._content.items():
            if key[index] is not None:
                total['Parity'+str(key[index])] += unit.population
        if self.keep_history:
            for p in range(8):
                self.counts['Parity'+str(p)].append(total['Parity'+str(p)])
        else:
            self.counts.update(total)

    def evolve(self):
        super().evolve()
        self.update_counts()




##----------------------------------------------------------------
## HERD

class QfeverHerd(MultiProcessManager):
    def __init__(self, infected=True, herd_id = 0, init_infection=None, keep_history=False, **others):
        super().__init__(herd_id = herd_id, keep_history = keep_history, **others)
        # init variables
        self.init_infection = init_infection
        self.step = 0
        self.Eexcr = 0
        self.Eplume = 0
        self.Etemp = 0
        self.Eaero = 0
        self.Eout = 0
        self.herd_abortion = 0
        self.herd_recursion_abortion = 0

        # incidence data
        self.incidence_shedder = False
        self.incidence_shedder_at = 0
        self.incidence_shedder_by_trade = False
        self.incidence_shedder_Eexcr = 0
        self.incidence_shedder_Eplume = 0
        self.incidence_shedder_Eaero = 0
        self.incidence_sero = False
        self.incidence_sero_at = 0
        self.incidence_sero_by_trade = False
        self.incidence_sero_Eexcr = 0
        self.incidence_sero_Eplume = 0
        self.incidence_sero_Eaero = 0
        # local incidence data
        self.local_incidence_shedder = False
        self.local_incidence_shedder_at = 0
        self.local_incidence_shedder_Eexcr = 0
        self.local_incidence_shedder_Eplume = 0
        self.local_incidence_shedder_Eaero = 0
        self.local_incidence_sero = False
        self.local_incidence_sero_at = 0
        self.local_incidence_sero_Eexcr = 0
        self.local_incidence_sero_Eplume = 0
        self.local_incidence_sero_Eaero = 0
        self.exposed_at = -1
        # load the model
        self.disease   = self.model.state_machines['health_state']
        self.lifecycle = self.model.state_machines['life_cycle']
        # additional variable to simpify access to a model parameter
        self.dispersion = 1. - self.model.get_value('mu')
        self.mu = self.model.get_value('mu')
        self.kappa = self.model.get_value('kappa')

        self.infected = infected
        self.prevalent = infected
        self.init_herd(infected=infected)

    def init_herd(self, infected=True):
        """Initialize the herd

        """
        self._get_distribution()
        self._init_population(infected=infected)

    def compute_culling(self, parity):
        """Return the number of cows to cull for the specified
        parity.

        """
        return np.random.binomial(self['parity_grouping'][(parity,)].population,
                                  self.culling_proba[parity])

    def culling_process(self):
        """Cull cows if needed. When the herd is too large, cows are
        culled with a probability based on their parity. Old cows are
        removed anyway.

        """
        if self['MASTER'].population >\
          self.model.get_value('culling_threshold')*self.statevars.init_pop:
            for parity in range(len(self.culling_proba)):
                if (parity,) in self['parity_grouping']._content:
                    self.remove_atoms(select_random(self['parity_grouping'][(parity,)],
                                                    self.compute_culling(parity)))
        for parity in range(len(self.culling_proba), 8):
            if (parity,) in self['parity_grouping']._content:
                self.remove_atoms(self['parity_grouping'][(parity,)])

    def renewal_process(self):
        """Introduce new cows in the herd. In the intra-herd model,
        new Cows are built from scratch when the herd becomes too
        small.

        """
        # init_pop = self.model.get_value('init_pop')
        init_pop = self.statevars.init_pop
        if self['MASTER'].population <\
          self.model.get_value('renewal_threshold') * init_pop:
            nb = np.random.binomial(init_pop, self.model.get_value('renew_proba')(self))
            self.add_atoms([self.renew_cow() for _ in range(nb)])

    def renew_cow(self):
        """Return a instance of Cow for renewal process.
        TODO: With EmulsionModel, new feature with initializing animals
        Not passing by _description of model.

        """
        dict_ = self.model.prototypes['individuals']['renew_animal']
        #self.model._description['renew_animal']
        return Cow( health_state=self.disease.states[dict_['health_state']],
                    life_cycle=self.lifecycle.states[dict_['life_state']],
                    parity=int(dict_['parity']),
                    vaccinated=int(dict_['vaccinated']),
                    origin_herd_id = self.get_information('herd_id'))

    def vaccination_process(self):
        """Vaccination process. All cows are vaccinated at the same
        time.

        """
        for atom in self['MASTER']:
            atom.statevars.vaccinated = 1
        self.make_consistent(self['infection'])

    def bacterial_dispersion(self):
        """Bacterial dispersion or mortality in the environment
        (exponential decrease).

        """
        self.Eout   = (self.Eexcr+self.Eplume)*self.mu*self.kappa
        self.Eplume*= self.dispersion
        self.Eexcr *= self.dispersion
        self.Eexcr += self.Etemp
        self.Etemp  = 0
        if self.exposed_at == -1 and self.Eexcr + self.Eplume + self.Eaero > 0:
            self.exposed_at = self.step
        self.Eaero  = 0
        self.step += 1
        # self.Eplume = 0

    def get_random_cycle(self, lc):
        return np.random.randint(0, self.get_max_cycle(lc))

    def get_max_cycle(self, lc):
        return self.lifecycle.get_value(self.lifecycle._statedesc[lc]['duration'])

    def _get_distribution(self):
        self.culling_proba = [self.get_information('culling_proba_{}'.format(x)) for x in range(7)]
        self.dist_parity =  [self.get_information('dist_parity_{}'.format(x)) for x in range(6)]

    def _get_init_state(self):
        """Return an initial population dictionary.
        Homogeneous with duration of each state of lifecycle

        """
        states = self.lifecycle.states
        proba = [self.get_max_cycle(lc.name) for lc in states]
        proba = [x/sum(proba) for x in proba]

        init_nb = np.random.multinomial(self.statevars.init_pop, proba)
        # {states(i+1) : init_nb[i] for i in range(len(states))}
        return SortedDict({states(i+1) : init_nb[i] for i in range(len(states))})

    def _get_init_health_state(self):
        """Return a health state when intantiating a cow. It will always return susceptible state
        when the ```init_infection``` is not given. Otherwise it will chose with the given
        distribution for the health state.

        """
        init_animal_dict = self.model.prototypes['individuals'][
            'init_susceptible_animal']
        if self.init_infection is None:
            return self.disease.states[init_animal_dict['health_state']]
        else:
            list_proba = [self.init_infection[state.name] for state in self.disease.states]
            index = np.random.multinomial(1, list_proba).nonzero()[0][0] + 1
            return self.disease.states(index)

    def _init_population(self, infected=True):
        """Return population of the herd at the beginning.
        TODO: With EmulsionModel, new feature with initializing animals
        Not passing by _description of model.

        """
        init_animal_dict = self.model.prototypes['individuals'][
            'init_susceptible_animal']
        cows = [Cow(health_state=self._get_init_health_state(),
                    life_cycle=lc,
                    parity=np.random.choice(len(self.dist_parity), p = self.dist_parity),
                    # _time_spent_life_cycle=self.get_random_cycle(lc.name),
                    vaccinated=int(init_animal_dict['vaccinated']),
                    origin_herd_id = self.get_information('herd_id'))
                for lc, quantity in self._get_init_state().items()
                for _ in range(quantity)]
        # if infected:
        #     self.Eexcr = self.model.get_value('Q_calving') if self.init_infection is None else self.init_infection['Eexcr']

        self.add_atoms(cows, init=True)
        for cow in cows:
            cow.statevars._time_spent_life_cycle = self.get_random_cycle(cow.statevars.life_cycle.name)
        if infected:
            cow = cows[-1]
            # cow.statevars._time_spent_life_cycle = self.get_max_cycle(cow.statevars.life_cycle.name)
            infected_state = self.model.prototypes['individuals'][
                'init_infected_animal']['health_state']
            cow.statevars.health_state = self.disease.states[infected_state]

    def sell_cows(self, d_sell={}):
        """Select cows to sell based on a dictionary of movement sorted by parity.
        We choose firstly animals that corresponding to the asked parity. If there are
        not enough animals to sell, we try to select from the parity just less then asked.

        """
        list_sell = []
        rest = {}
        for parity, qty in d_sell.items():
            if qty > 0 :
                if parity == 'global':
                    comp = self['MASTER']
                    sold_animals = select_random(comp, min(qty, comp.population))
                    list_sell += sold_animals
                    if qty > comp.population:
                        print('Attention, missing {} animals in herd {} to sell cows'.format(qty - comp.population, self.statevars.herd_id))
                else:
                    parity = int(parity)
                    if (parity,) in self['parity_grouping']._content:
                        comp_parity = self['parity_grouping'][(parity, )]
                        qty_sell = qty if qty <= comp_parity.population else comp_parity.population
                        rest_qty = 0 if qty <= comp_parity.population else qty - comp_parity.population

                        sold_animals = select_random(comp_parity, qty_sell)
                        list_sell += sold_animals

                        rest_parity = parity -1 if parity >= 1 else 'global'
                        rest[rest_parity] = rest_qty
                    else:
                        rest_parity = parity -1 if parity >= 1 else 'global'
                        rest[rest_parity] = qty


        self.remove_atoms(list_sell)

        if rest:
            rest_sell, rest_rest = self.sell_cows(rest)
            list_sell += rest_sell

        return list_sell, rest

    def checkout_inbox(self):
        self.Eaero = 0
        for message in self._inbox:
            if 'animals' in message['content']:
                animals = message['content']['animals']
                self.add_atoms(animals)
                set_health = set(cow.statevars.health_state.name for cow in animals)
                if 'I-' in set_health or 'I+' in set_health:
                    self.update_incidence_shedder(trade=True)
                if 'I+' in set_health or 'C+' in set_health:
                    self.update_incidence_sero(trade=True)

            if 'Eplume' in message['content']:
                self.Eplume += message['content']['Eplume']

            if 'Eaero' in message['content']:
                self.Eaero += message['content']['Eaero']

    def update_incidence_shedder(self, trade=False):
        """Update the incidence status of the herd when having
        shedder.

        """
        if not self.infected and not self.incidence_shedder:
            # step = self.get_host().get_host().step
            self.incidence_shedder = True
            self.incidence_shedder_at = self.step
            self.incidence_shedder_by_trade = trade
            self.incidence_shedder_Eexcr = self.Eexcr
            self.incidence_shedder_Eplume = self.Eplume
            self.incidence_shedder_Eaero = self.Eaero

    def update_incidence_sero(self, trade=False):
        """Update the incidence status of the herd when having
        sero-positive animals.

        """
        if not self.infected and not self.incidence_sero:
            # step = self.get_host().get_host().step
            self.incidence_sero = True
            self.incidence_sero_at = self.step
            self.incidence_sero_by_trade = trade
            self.incidence_sero_Eexcr = self.Eexcr
            self.incidence_sero_Eplume = self.Eplume
            self.incidence_sero_Eaero = self.Eaero

    def update_local_incidence_shedder(self):
        """Update the local incidence status of the herd when having
        shedder.

        """
        if not self.infected and not self.local_incidence_shedder:
            # step = self.get_host().get_host().step
            self.local_incidence_shedder = True
            self.local_incidence_shedder_at = self.step
            self.local_incidence_shedder_Eexcr = self.Eexcr
            self.local_incidence_shedder_Eplume = self.Eplume
            self.local_incidence_shedder_Eaero = self.Eaero

    def update_local_incidence_sero(self):
        """Update the local incidence status of the herd when having
        sero-positive animals.

        """
        if not self.infected and not self.local_incidence_sero:
            # step = self.get_host().get_host().step
            self.local_incidence_sero = True
            self.local_incidence_sero_at = self.step
            self.local_incidence_sero_Eexcr = self.Eexcr
            self.local_incidence_sero_Eplume = self.Eplume
            self.local_incidence_sero_Eaero = self.Eaero

    def update_size(self, size):
        """Update herd size (init_pop) for culling and renewal threshold.

        """
        self.statevars.init_pop = size

    @property
    def counts(self):
        """Return a pandas DataFrame containing counts of each process if existing.
        TODO: column steps need to be with one of process

        """
        res = {}
        for comp in self:
            try:
                res.update(comp.counts)
            except AttributeError:
                pass
            except Exception as e:
                raise e
        if not self.keep_history:
            res.update({'steps': self.step})
        return pd.DataFrame(res, index=[0])

class QfeverMetaPop(MultiProcessManager):
    """QfeverMetaPop is in charge of handling multiple herds. In cluding
    aerosol dispersion and movement between herds.

    """
    def __init__(self,  keep_history=False,
                        **others):
        super().__init__(level='metapop', keep_history=keep_history, **others)
        self.step = 0

        self.zeta = self.model.get_value('zeta')
        self.aero = self.model.get_value('aero')
        self.depot = self.model.get_value('depot')
        self.metapop_risk = self.model.get_value('metapop_risk')
        self.breath_height = self.model.get_value('breath_height')
        self.surface_per_cow = self.model.get_value('surface_per_cow')

    def __contains__(self, keys):
        """Shortcut verification if herd_id in the metapopulation or not

        """
        return keys in self['MASTER']._content.keys()

    @property
    def health_composition(self):
        """Return a list of current population composition of the
        metapopulation based on health state.

        """
        dist = SortedDict({state: 0 for state in self.model.state_machines['health_state'].states})
        for herd in self['MASTER']:
            for state in dist.keys():
                dist[state] += herd['infection'].counts[state.name]
        return dist

    def read_meta_pop(self, path):
        """Read a meta population config file (csv) and instanciate
        herds corresponding.

        """
        d_herd = pd.read_csv(path).to_dict(orient='index')
        self.add_atoms([self.get_herd(**param) for param in d_herd.values()])

    def read_mvt_data(self, path):
        with open(path, 'r') as f:
            self.mvt = json.load(f)

    def read_stable_herd(self, path):
        with open(path, 'r') as f:
            self.stable_herd_stat = json.load(f)

    def read_wind_data(self, wind_u_path, wind_v_path):
        """Load wind datas.

        """
        df_u = pd.read_csv(wind_u_path, index_col=0)
        df_v = pd.read_csv(wind_v_path, index_col=0)
        dict_wind_data = {}

        max_step = min((df_u.columns.size-2)//7, (df_v.columns.size-2)//7)
        for index in range(1,len(df_u)+1):
            # rs = []
            # thetas = []
            speeds = []
            angles = []
            key = (df_u['x'][index], df_u['y'][index])
            for x in range(max_step):
                start = x*7+1
                end = (x+1)*7
                l_u = np.array([df_u['band{}'.format(i)][index] for i in range(start, end+1)])
                l_v = np.array([df_v['band{}'.format(i)][index] for i in range(start, end+1)])
                average_u = np.mean(l_u)
                average_v = np.mean(l_v)
                # l_r = np.sqrt(l_u**2+l_v**2)
                # l_theta = np.arctan2(l_v, l_u)
                speeds.append(np.sqrt(average_u**2+average_v**2))
                angles.append(np.arctan2(average_v, average_u))
                # rs.append(np.mean(l_r))
                # thetas.append(np.mean(l_theta))

            dict_wind_data[key] = {'speeds': speeds, 'angles': angles}
        self.dict_wind_data = dict_wind_data

    def random_position(self, filepath='data/qfever/holdingDataSimulatedCoords.csv'):
        """distribute random position pre-computed by Luyan's R code.
        Choice between 4 different coordinates."""
        df = pd.read_csv('data/qfever/holdingDataSimulatedCoords.csv', index_col='HoldingID')
        choice = int(self.model.get_value('random_position_choice'))
        for herd in self['MASTER']:
            herd_id = herd.statevars.herd_id
            lon, lat = df['Xcoord_{}'.format(choice)][herd_id], df['Ycoord_{}'.format(choice)][herd_id]
            lon, lat, _, _ = from_latlon(lat, lon)
            herd.statevars.longitude = lon
            herd.statevars.latitude = lat


    def find_neighbor(self, distance=10000):
        """Find and stock neighbor with given distance of each herd.

        """
        neighbors = SortedDict()
        # TODO: find in data
        min_lat, delta_lat = 47.25 , 0.75
        min_lon, delta_lon = 354.75, 0.75
        find_lon = lambda x: ((x-min_lon+delta_lon/2) //delta_lon) * delta_lon + min_lon
        find_lat = lambda x: ((x-min_lat+delta_lat/2) //delta_lat) * delta_lat + min_lat

        if self.model.get_value('random_position'):
            self.random_position()

        for herd_1 in self['MASTER']:
            neighbors[herd_1.statevars.herd_id] = []
            for herd_2 in self['MASTER']:
                x = herd_2.statevars.longitude - herd_1.statevars.longitude
                y = herd_2.statevars.latitude - herd_1.statevars.latitude
                if herd_2 != herd_1 and x**2 + y**2 <= distance**2:
                    neighbors[herd_1.statevars.herd_id].append(herd_2.statevars.herd_id)

            # Find geolocalisation keys
            lat, lon  = to_latlon(herd_1.statevars.longitude, herd_1.statevars.latitude, 30, 'T')
            lon = lon % 360
            herd_1.wind_data_key = (find_lon(lon), find_lat(lat))

        self.neighbors = neighbors

    def increase_step(self):
        self.step += 1

    def outbox_to_inbox(self):
        """Four actions are applicated:
        - Send messages from outboxes to inboxes.
        - Reset outboxes.
        - Checkout inbox for each herd
        - Clean non sticky message in the inbox

        """
        for herd in self['MASTER']:
            messages = herd.get_outbox()
            for message in messages:
                sms = { 'from': herd.statevars.herd_id,
                        'content': message['content']}
                if message['to'] in self:
                    self['MASTER'][message['to']].add_inbox([sms])
            herd.reset_outbox()

        for herd in self['MASTER']:
            herd.checkout_inbox()
            herd.clean_inbox()

    def exchange_animals(self):
        """Select sell animals and put them in the outboxes.
        For animals from outside of metapopulation, we instanciate
        new animals based on property of the metapopulation.

        """
        health_composition = self.health_composition
        health_distribution = np.array(health_composition.values())
        health_distribution = health_distribution / health_distribution.sum()
        for source, mvts_from_source in self.mvt[str(self.step+1)].items():
            source = int(source) if source != 'outside' else source
            for dest, mvt_to_dest in mvts_from_source.items():
                dest = int(dest) if dest != 'outside' else dest
                # If animals come from other herd of the meta pop
                if source in self:
                    pop_sold, _ = self['MASTER'][source].sell_cows(mvt_to_dest)
                    self['MASTER'][source].add_outbox({'to': dest, 'content': {'animals': pop_sold}})
                # If animals come from outside of the meta pop
                elif dest in self:
                    animals = []
                    # Use SortedDict to insure order for a given random seed
                    for parity, qty in SortedDict(mvt_to_dest).items():
                        parity = int(parity)
                        l_healths = np.random.multinomial(qty, health_distribution)
                        d_healths = SortedDict(zip(health_composition.keys(), l_healths))
                        for state, state_qty in d_healths.items():
                            state = state if self.metapop_risk else self.model.state_machines['health_state'].states['S']
                            animals += [Cow(health_state=state,
                                            life_cycle=self.model.state_machines['life_cycle'].states['NP'],
                                            parity=parity,
                                            vaccinated=0,
                                            origin_herd_id = 0)
                                        for _ in range(state_qty)]
                    sms = {'from': 'outside', 'content': {'animals': animals}}
                    # print([animal.statevars.health_state for animal in animals])
                    self['MASTER'][dest].add_inbox([sms])
                else:
                    pass
                    # print(dest, 'is not in metapop')


    def wind_propagation(self):
        """Bacteria's wind transmission.

        """
        step = self.step
        # wind_speed = self.wind_speed[step]
        # wind_angle = self.wind_angle[step]
        for herd in self['MASTER']:
            Eout = herd.Eout
            if Eout > 0:
                for id_neighbor in self.neighbors[herd.statevars.herd_id]:
                    wind_speed = self.dict_wind_data[herd.wind_data_key]['speeds'][step]
                    wind_angle = self.dict_wind_data[herd.wind_data_key]['angles'][step]
                    herd_neighbor = self['MASTER'][id_neighbor]
                    x = herd_neighbor.statevars.longitude - herd.statevars.longitude
                    y = herd_neighbor.statevars.latitude - herd.statevars.latitude
                    x_adjusted, y_adjusted = referential_transform(x, y, wind_angle)
                    if x_adjusted > 0:
                        if self.depot:
                            concent, Wdep = plume_ermak(wind_speed, Eout, x_adjusted, y_adjusted)
                            Eplume = self.surface_per_cow*herd_neighbor.statevars.init_pop*concent*Wdep
                            if Eplume < 0:
                                print('Attention: Eplume < 0', wind_speed, Eout, x_adjusted, y_adjusted)
                            sms = {'from': herd.statevars.herd_id, 'content': {'Eplume': Eplume}}
                            herd_neighbor.add_inbox([sms])
                            if self.aero:
                                qty = concent * self.surface_per_cow * herd_neighbor.statevars.init_pop * self.breath_height * self.zeta
                                sms = {'from': herd.statevars.herd_id, 'content': {'Eaero': qty}}
                                herd_neighbor.add_inbox([sms])

                        elif self.aero:
                            concent = plume_gaussian(wind_speed, Eout, x_adjusted, y_adjusted)
                            qty = concent * self.surface_per_cow * herd_neighbor.statevars.init_pop * self.breath_height * self.zeta

                            if qty < 0:
                                print(wind_speed, Eout, x_adjusted, y_adjusted)
                            sms = {'from': herd.statevars.herd_id, 'content': {'Eaero': qty}}
                            herd_neighbor.add_inbox([sms])


class QfeverFinister2012(QfeverMetaPop):
    """QfeverFinister2012 class is aimed to model Qfever propagation (trade/aero)
    in the department Finister in France (n° 29) within the year 2012.

    """
    def __init__(self,  mvt_path        = 'data/qfever/movement_2012_luyan.json',
                        wind_u_path     = 'data/qfever/space_2012_u.csv',
                        wind_v_path     = 'data/qfever/space_2012_v.csv',
                        metapop_path    = 'data/qfever/final_herd.csv',
                        stable_herd_path= 'data/qfever/stable_herd_stat.json',
                        extension_path  = 'data/qfever/extension_herd_29.csv',
                        **others):
        super().__init__(**others)
        self.read_mvt_data(mvt_path)
        self.read_wind_data(wind_u_path=wind_u_path, wind_v_path=wind_v_path)
        self.read_stable_herd(stable_herd_path)

        start = time.perf_counter()
        self.read_meta_pop(metapop_path)

        if self.model.get_value('herd_extension'):
            self.read_extension_data(extension_path)
        end = time.perf_counter()
        print('Initialization {} s'.format(end - start))
        self.find_neighbor(distance=self.model.get_value('neighborhood_distance'))

    def get_herd(self, **param):
        """Return a QfeverHerd instances with given parameter

        """
        prev_level = {
            # '+'  : 0.18, #[0.18, 0.29],
            # '++' : 0.40, #[0.40, 0.47],
            # '+++': 0.36, #[0.36, 0.44],
            '+'  : [0.18, 0.29],
            '++' : [0.40, 0.47],
            '+++': [0.36, 0.44],
        }
        infected = param['elisa_2012'] != '-'
        # infected = False
        param['infected'] = infected
        param['keep_history'] = self.keep_history
        # print(self.keep_history)

        if infected:
            pop = min(260, int((param['init_pop'] - 10)//30 * 30 + 20))
            init_infection = self.stable_herd_stat[str(pop)][param['elisa_2012']] if infected else None


            # table_stat = self.stable_herd_stat[str(pop)]

            # data_seroprevalence = np.array(table_stat['Seroprevalence'])
            # line, column = np.where((data_seroprevalence>prev_level[param['elisa_2012']][0]) & (data_seroprevalence>prev_level[param['elisa_2012']][1]))

            # # If at least an element in ```data_seroprevalence``` satisfied the condition, we choose
            # # randomly an element.
            # if line.any():
            #     # index = np.random.randint(len(line))
            #     line_ = np.random.choice(list(set(line)))
            #     index = np.where(line == line_)[0][0]
            #     line   = line[index]
            #     column = column[index]
            # else:
            #     line = np.random.randint(len(data_seroprevalence))
            #     column = -1

            # # Construct ```init_infection```
            # init_infection = {state.name: table_stat[state.name][line][column]/table_stat['N'][line][column] \
            #                     for state in self.model.state_machines['health_state'].states}
            # init_infection.update({'Eexcr': table_stat['Eexcr'][line][column]})

            # # Distribut random position when unknown (value set by 0)
            # if param['longitude'] == 0:
            #     print('before:', param)
            #     lon, lat = param['Xcoord'], param['Ycoord']
            #     lon, lat, _, _ = from_latlon(lat, lon)
            #     param['longitude'] = lon
            #     param['latitude']  = lat
            #     print('after', param)



            # INITIATE INFECTION BY NATURAL SELECTION

            # init_natural = True
            # if init_natural:
            #     init_times = 0
            #     sero_prev = 0
            #     step = 0
            #     while init_times<= 3 and sero_prev <= prev_level[param['elisa_2012']]:

            #         if step == 0:
            #             # print('init itmes', init_times)
            #             herd = QfeverHerd(model=self.model, host=self['MASTER'],
            #                           init_infection=None,
            #                           **param)
            #         herd.evolve()
            #         sero_prev = herd['infection'].counts['Seroprevalence']
            #         if step <= 299:
            #             step += 1
            #         else:
            #             step = 0
            #             init_times += 1

            #     print(sero_prev)
            #     return herd


            return QfeverHerd(model=self.model, host=self['MASTER'],
                              init_infection=init_infection,
                              **param)
        else:
            return QfeverHerd(model=self.model, host=self['MASTER'], **param)

    def read_extension_data(self, path):
        """Read a extension population config file (csv) and instanciate
        herds corresponding.

        """
        d_herd = pd.read_csv(path).to_dict(orient='index')
        # prevalence_dist = [herd['infection'].counts['Seroprevalence'] for herd in self['MASTER']]
        prevalence_dist = [herd.get_information('elisa_2012') for herd in self['MASTER']]
        self.add_atoms([self.get_extension_herd(prevalence_dist, **param) for param in d_herd.values()])

    def get_extension_herd(self, prevalence_dist, **param):
        """Return a QfeverHerd instances with given parameter. The sero-prevalence
        is generated by meta population distribution.
        """
        # select a prevalence level
        prevalence = np.random.choice(prevalence_dist)
        prev_level = {
            '+'  : 0.18, #[0.18, 0.29],
            '++' : 0.40, #[0.40, 0.47],
            '+++': 0.36, #[0.36, 0.44],
        }

        infected = prevalence != '-'
        # infected = False
        param['infected'] = infected
        param['keep_history'] = self.keep_history
        # print(self.keep_history)

        if infected:
            pop = min(260, int((param['init_pop'] - 10)//30 * 30 + 20))
            init_infection = self.stable_herd_stat[str(pop)][prevalence] if infected else None

            # table_stat = self.stable_herd_stat[str(pop)]

            # data_seroprevalence = np.array(table_stat['Seroprevalence'])
            # line, column = np.where((data_seroprevalence>prev_level[param['elisa_2012']][0]) & (data_seroprevalence>prev_level[param['elisa_2012']][1]))

            # # If at least an element in ```data_seroprevalence``` satisfied the condition, we choose
            # # randomly an element.
            # if line.any():
            #     # index = np.random.randint(len(line))
            #     line_ = np.random.choice(list(set(line)))
            #     index = np.where(line == line_)[0][0]
            #     line   = line[index]
            #     column = column[index]
            # else:
            #     line = np.random.randint(len(data_seroprevalence))
            #     column = -1

            # # Construct ```init_infection```
            # init_infection = {state.name: table_stat[state.name][line][column]/table_stat['N'][line][column] \
            #                     for state in self.model.state_machines['health_state'].states}
            # init_infection.update({'Eexcr': table_stat['Eexcr'][line][column]})

            # Distribut random position

            herd = QfeverHerd(model=self.model, host=self['MASTER'],
                              init_infection=init_infection,
                              **param)
        else:
            herd = QfeverHerd(model=self.model, host=self['MASTER'], **param)

        lon, lat = param['Xcoord'], param['Ycoord']
        lon, lat, _, _ = from_latlon(lat, lon)
        herd.statevars.longitude = lon
        herd.statevars.latitude = lat

        return herd

    @property
    def counts(self):
        dict_counts = defaultdict(list)
        for herd in self['MASTER']:
            if herd.get_information('elisa_2012') == '-':
                dict_counts['herd_id'].append(herd.statevars.herd_id)
                dict_counts['longitude'].append(herd.statevars.longitude)
                dict_counts['latitude'].append(herd.statevars.latitude)
                dict_counts['elisa_2012'].append(herd.statevars.elisa_2012)
                dict_counts['elisa_2013'].append(herd.statevars.elisa_2013)

                dict_counts['incidence_shedder'].append(herd.incidence_shedder)
                dict_counts['incidence_shedder_at'].append(herd.incidence_shedder_at)
                dict_counts['incidence_shedder_by_trade'].append(herd.incidence_shedder_by_trade)
                dict_counts['incidence_shedder_Eexcr'].append(herd.incidence_shedder_Eexcr)
                dict_counts['incidence_shedder_Eplume'].append(herd.incidence_shedder_Eplume)
                dict_counts['incidence_shedder_Eaero'].append(herd.incidence_shedder_Eaero)

                dict_counts['incidence_sero'].append(herd.incidence_sero)
                dict_counts['incidence_sero_at'].append(herd.incidence_sero_at)
                dict_counts['incidence_sero_by_trade'].append(herd.incidence_sero_by_trade)
                dict_counts['incidence_sero_Eexcr'].append(herd.incidence_sero_Eexcr)
                dict_counts['incidence_sero_Eplume'].append(herd.incidence_sero_Eplume)
                dict_counts['incidence_sero_Eaero'].append(herd.incidence_sero_Eaero)

                dict_counts['local_incidence_shedder'].append(herd.local_incidence_shedder)
                dict_counts['local_incidence_shedder_at'].append(herd.local_incidence_shedder_at)
                dict_counts['local_incidence_shedder_Eexcr'].append(herd.local_incidence_shedder_Eexcr)
                dict_counts['local_incidence_shedder_Eplume'].append(herd.local_incidence_shedder_Eplume)
                dict_counts['local_incidence_shedder_Eaero'].append(herd.local_incidence_shedder_Eaero)

                dict_counts['local_incidence_sero'].append(herd.local_incidence_sero)
                dict_counts['local_incidence_sero_at'].append(herd.local_incidence_sero_at)
                dict_counts['local_incidence_sero_Eexcr'].append(herd.local_incidence_sero_Eexcr)
                dict_counts['local_incidence_sero_Eplume'].append(herd.local_incidence_sero_Eplume)
                dict_counts['local_incidence_sero_Eaero'].append(herd.local_incidence_sero_Eaero)

                dict_counts['exposed_at'].append(herd.exposed_at)
                dict_counts['final_Eexcr'].append(herd.Eexcr)
                dict_counts['final_Eplume'].append(herd.Eplume)
                dict_counts['prevalence'].append(herd['infection'].counts['Prevalence'])
                dict_counts['seroprevalence'].append(herd['infection'].counts['Seroprevalence'])
                dict_counts['step'].append(self.step)

                for name in herd['infection'].counts.keys():
                    dict_counts[name].append(herd['infection'].counts[name])
                for name in herd['lifecycle'].counts.keys():
                    dict_counts[name].append(herd['lifecycle'].counts[name])
                for name in herd['parity_grouping'].counts.keys():
                    dict_counts[name].append(herd['parity_grouping'].counts[name])

        return pd.DataFrame(dict_counts)


class QfeverMetaPop1D(QfeverMetaPop):
    """QfeverMetaPop1D is aim to test the effect of aerosol dispersion.
    We place a herd infected at origin and only the bacteria in this
    herd can be transported to others.

    """
    def __init__(self,  keep_history=False, **others):
        super().__init__(**others)
        self.zeta = self.model.get_value('zeta')

        self.get_infected_herd(**others)
        self.add_atoms([QfeverHerd(herd_id=x*100, longitude=x*100, infected=not bool(x), host=self['MASTER'],
                                   keep_history=keep_history, **others) for x in range(1, 100)])


    def get_infected_herd(self, **others):
        """Add a stable infected herd in current metapopulation.

        """
        extinction = True
        while extinction:
            herd = QfeverHerd(herd_id=0, longitude=0, infected=True, host=self['MASTER'],
                      keep_history=self.keep_history, **others)

            for t in range(200):
                herd.evolve()
            prev = herd['infection'].counts['Seroprevalence']
            extinction = prev == 0

        self.add_atoms([herd])

    def wind_propagation(self):
        source = self['MASTER'][0]
        Eout = source.Eout
        for herd in self['MASTER']:
            if herd != source:
                if Eout > 0:
                    x = herd.statevars.longitude - source.statevars.longitude
                    if x > 0:
                        if self.depot:
                            concent, Wdep = plume_ermak(5, Eout, x, 0)
                            Eplume = 17*herd.statevars.init_pop*concent*Wdep
                            if Eplume < 0:
                                print(5, Eout, x, 0)
                            sms = {'from': 0, 'content': {'Eplume': Eplume}}
                            herd.add_inbox([sms])
                            if self.aero:
                                qty = concent * 17 * herd.statevars.init_pop * 4 * self.zeta
                                sms = {'from': 0, 'content': {'Eaero': qty}}
                                herd.add_inbox([sms])
                        elif self.aero:
                            concent = plume_gaussian(5, Eout, x, 0)
                            qty = 17*herd.statevars.init_pop*4*concent * self.zeta
                            if qty < 0:
                                print(5, Eout, x, 0)
                            sms = {'from': 0, 'content': {'Eaero': qty}}
                            herd.add_inbox([sms])
            herd.checkout_inbox()
            herd.clean_inbox()

    def exchange_animals(self, **dparams):
        pass

    def outbox_to_inbox(self):
        pass

    def increase_step(self):
        pass

    @property
    def counts(self):
        dict_counts = defaultdict(list)
        for herd in self['MASTER']:
            dict_counts['herd_id'].append(herd.statevars.herd_id)
            dict_counts['longitude'].append(herd.statevars.longitude)
            dict_counts['incidence_shedder'].append(herd.incidence_shedder)
            dict_counts['incidence_shedder_at'].append(herd.incidence_shedder_at)
            dict_counts['incidence_shedder_by_trade'].append(herd.incidence_shedder_by_trade)
            dict_counts['incidence_shedder_Eexcr'].append(herd.incidence_shedder_Eexcr)
            dict_counts['incidence_shedder_Eplume'].append(herd.incidence_shedder_Eplume)
            dict_counts['incidence_shedder_Eaero'].append(herd.incidence_shedder_Eaero)

            dict_counts['incidence_sero'].append(herd.incidence_sero)
            dict_counts['incidence_sero_at'].append(herd.incidence_sero_at)
            dict_counts['incidence_sero_by_trade'].append(herd.incidence_sero_by_trade)
            dict_counts['incidence_sero_Eexcr'].append(herd.incidence_sero_Eexcr)
            dict_counts['incidence_sero_Eplume'].append(herd.incidence_sero_Eplume)
            dict_counts['incidence_sero_Eaero'].append(herd.incidence_sero_Eaero)

            dict_counts['local_incidence_shedder'].append(herd.local_incidence_shedder)
            dict_counts['local_incidence_shedder_at'].append(herd.local_incidence_shedder_at)
            dict_counts['local_incidence_shedder_Eexcr'].append(herd.local_incidence_shedder_Eexcr)
            dict_counts['local_incidence_shedder_Eplume'].append(herd.local_incidence_shedder_Eplume)
            dict_counts['local_incidence_shedder_Eaero'].append(herd.local_incidence_shedder_Eaero)

            dict_counts['local_incidence_sero'].append(herd.local_incidence_sero)
            dict_counts['local_incidence_sero_at'].append(herd.local_incidence_sero_at)
            dict_counts['local_incidence_sero_Eexcr'].append(herd.local_incidence_sero_Eexcr)
            dict_counts['local_incidence_sero_Eplume'].append(herd.local_incidence_sero_Eplume)
            dict_counts['local_incidence_sero_Eaero'].append(herd.local_incidence_sero_Eaero)
            dict_counts['exposed_at'].append(herd.exposed_at)
            dict_counts['final_Eexcr'].append(herd.Eexcr)
            dict_counts['final_Eplume'].append(herd.Eplume)
            dict_counts['prevalence'].append(herd['infection'].counts['Prevalence'])
            dict_counts['seroprevalence'].append(herd['infection'].counts['Seroprevalence'])
        return pd.DataFrame(dict_counts)

class QfeverFinister2005(QfeverMetaPop):
    """QfeverFinister2005 is aimed to model Qfever propagation since 2005."""
    def __init__(self,  mvt_path           = 'data/qfever/movement_2005_2014.json',
                        wind_u_path        = 'data/qfever/finister_2005_now_u.csv',
                        wind_v_path        = 'data/qfever/finister_2005_now_v.csv',
                        metapop_path       = 'data/qfever/final_herd.csv',
                        holding_char_path  = 'data/qfever/holdingsCharForYuLin.csv',
                        stable_herd_path   = 'data/qfever/large/complete_stable_herd.json',
                        intra_distribution = 'data/qfever/FQ_prévalence des séropositifs intra-troupeau.xlsx',
                        dynamic_size       = True,
                        **others):
        super().__init__(**others)
        self.dynamic_size = dynamic_size
        self.read_mvt_data(mvt_path)
        self.read_wind_data(wind_u_path=wind_u_path, wind_v_path=wind_v_path)
        self.read_stable_herd(stable_herd_path)
        self.read_intra_distribution(intra_distribution)
        if dynamic_size:
            self.read_holding_char(holding_char_path)

        start = time.perf_counter()
        self.read_meta_pop(metapop_path)
        end = time.perf_counter()
        print('Initialization {} s'.format(end - start))
        self.find_neighbor(distance=self.model.get_value('neighborhood_distance'))

    def read_intra_distribution(self, path):
        """Read the intra herd's prevalence data file.

        """
        df = pd.read_excel(path)[:-3]
        self.intra_dist = df['prev_Vaches laitières'].values

    def get_intra_prevalence(self):
        """Return a prevalence intra-herd based on field data.

        """
        return np.random.choice(self.intra_dist)

    def read_holding_char(self, path):
        """Read the herd's size data file (2005-2013).

        """
        df = pd.read_csv(path, index_col = 0)
        self.holding_char = df

    def get_herd(self, **param):
        """Return a QfeverHerd instances with given parameter

        """
        infected_2012 = param['elisa_2012'] != '-'

        global_seroprevalence = 0.05

        # TODO: 2697/1900 is "Number of total herds/number of total seropositive herds in 2012"
        # is now hard coded, need to be automatically calculated in the future
        infected = infected_2012 and np.random.binomial(1, global_seroprevalence*2697/1900)
        # infected = False
        param['infected'] = infected
        param['keep_history'] = self.keep_history
        # print(self.keep_history)

        # Change herd size at each year
        if self.dynamic_size:
            herd_id = param['herd_id']
            if herd_id in self.holding_char['nbPresD05'].keys():
                pop = self.holding_char['nbPresD05'][herd_id]
                pop = 2 if pop <= 2 else pop
                param['init_pop'] = pop


        if infected:
            pop = int(min(260, (param['init_pop'] - 10)//30 * 30 + 20))
            pop = 20 if pop <=0 else pop
            table_stat = self.stable_herd_stat[str(pop)]

            data_seroprevalence = np.array(table_stat['Seroprevalence'])
            intra_prevalence = self.get_intra_prevalence()
            line, column = np.where(data_seroprevalence>intra_prevalence)

            # If at least an element in ```data_seroprevalence``` satisfied the condition, we choose
            # randomly an element.
            if line.any():
                index = np.random.randint(len(line))
                line   = line[index]
                column = column[index]
            else:
                line = np.random.randint(len(data_seroprevalence))
                column = -1

            # Construct ```init_infection```
            init_infection = {state.name: table_stat[state.name][line][column]/table_stat['N'][line][column] \
                                for state in self.model.state_machines['health_state'].states}
            init_infection.update({'Eexcr': table_stat['Eexcr'][line][column]})

            return QfeverHerd(model=self.model, host=self['MASTER'],
                              init_infection=init_infection,
                              **param)
        else:
            return QfeverHerd(model=self.model, host=self['MASTER'], **param)

    def evolve(self):
        if self.dynamic_size and self.step % 52 == 0:
            year = self.step // 52 + 5
            if year <= 13:
                key = 'nbPresD0{}'.format(year) if year < 10 else 'nbPresD{}'.format(year)
                dict_size = self.holding_char[key]
                for herd in self['MASTER']:
                    herd_id = herd.statevars.herd_id
                    if herd_id in dict_size.keys():
                        size = dict_size[herd_id]
                        herd.update_size(size)
        super().evolve()


    @property
    def counts(self):
        dict_counts = defaultdict(list)
        for herd in self['MASTER']:
            dict_counts['herd_id'].append(herd.statevars.herd_id)
            dict_counts['longitude'].append(herd.statevars.longitude)
            dict_counts['latitude'].append(herd.statevars.latitude)
            dict_counts['elisa_2012'].append(herd.statevars.elisa_2012)
            dict_counts['elisa_2013'].append(herd.statevars.elisa_2013)

            dict_counts['incidence_shedder'].append(herd.incidence_shedder)
            dict_counts['incidence_shedder_at'].append(herd.incidence_shedder_at)
            dict_counts['incidence_shedder_by_trade'].append(herd.incidence_shedder_by_trade)
            dict_counts['incidence_shedder_Eexcr'].append(herd.incidence_shedder_Eexcr)
            dict_counts['incidence_shedder_Eplume'].append(herd.incidence_shedder_Eplume)
            dict_counts['incidence_shedder_Eaero'].append(herd.incidence_shedder_Eaero)

            dict_counts['incidence_sero'].append(herd.incidence_sero)
            dict_counts['incidence_sero_at'].append(herd.incidence_sero_at)
            dict_counts['incidence_sero_by_trade'].append(herd.incidence_sero_by_trade)
            dict_counts['incidence_sero_Eexcr'].append(herd.incidence_sero_Eexcr)
            dict_counts['incidence_sero_Eplume'].append(herd.incidence_sero_Eplume)
            dict_counts['incidence_sero_Eaero'].append(herd.incidence_sero_Eaero)

            dict_counts['local_incidence_shedder'].append(herd.local_incidence_shedder)
            dict_counts['local_incidence_shedder_at'].append(herd.local_incidence_shedder_at)
            dict_counts['local_incidence_shedder_Eexcr'].append(herd.local_incidence_shedder_Eexcr)
            dict_counts['local_incidence_shedder_Eplume'].append(herd.local_incidence_shedder_Eplume)
            dict_counts['local_incidence_shedder_Eaero'].append(herd.local_incidence_shedder_Eaero)

            dict_counts['local_incidence_sero'].append(herd.local_incidence_sero)
            dict_counts['local_incidence_sero_at'].append(herd.local_incidence_sero_at)
            dict_counts['local_incidence_sero_Eexcr'].append(herd.local_incidence_sero_Eexcr)
            dict_counts['local_incidence_sero_Eplume'].append(herd.local_incidence_sero_Eplume)
            dict_counts['local_incidence_sero_Eaero'].append(herd.local_incidence_sero_Eaero)

            dict_counts['exposed_at'].append(herd.exposed_at)
            # dict_counts['prevalence'].append(herd['infection'].counts['Prevalence'])
            # dict_counts['seroprevalence'].append(herd['infection'].counts['Seroprevalence'])

            dict_counts['step'].append(self.step)

            for name in herd['infection'].counts.keys():
                dict_counts[name].append(herd['infection'].counts[name])
            for name in herd['lifecycle'].counts.keys():
                dict_counts[name].append(herd['lifecycle'].counts[name])
            for name in herd['parity_grouping'].counts.keys():
                dict_counts[name].append(herd['parity_grouping'].counts[name])

        return pd.DataFrame(dict_counts)

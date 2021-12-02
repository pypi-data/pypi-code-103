"""A Python implementation of the EMuLSion framework.

(Epidemiologic MUlti-Level SImulatiONs).

Classes and functions for entities management.

"""

import abc
from   collections               import OrderedDict, Counter

from   sortedcontainers          import SortedSet, SortedDict

import numpy                     as np
import pandas                    as pd

from   emulsion.agent.exceptions import LevelException
from   emulsion.agent.comparts   import Compartment
from   emulsion.agent.views      import StructuredView, AdaptiveView
from   emulsion.agent.process    import MethodProcess, StateMachineProcess
from   emulsion.tools.misc       import load_class, rates_to_probabilities,\
                                   count_population, aggregate_probabilities,\
                                   probabilities_to_rates, select_random




#   _____                       __  __
#  / ____|                     |  \/  |
# | |  __ _ __ ___  _   _ _ __ | \  / | __ _ _ __   __ _  __ _  ___ _ __
# | | |_ | '__/ _ \| | | | '_ \| |\/| |/ _` | '_ \ / _` |/ _` |/ _ \ '__|
# | |__| | | | (_) | |_| | |_) | |  | | (_| | | | | (_| | (_| |  __/ |
#  \_____|_|  \___/ \__,_| .__/|_|  |_|\__,_|_| |_|\__,_|\__, |\___|_|
#                        | |                              __/ |
#                        |_|                             |___/

class GroupManager(StructuredView):
    """An GroupManager is able to make its content
    evolve according to a specific state machine, the state of each
    subcompartment being stored in a specific state variable or
    attribute.

    """
    def __init__(self, state_machine=None, **others):
        """Create an GroupManager based on the
        specified state machine. The state of each subcompartment can
        be retrieved in the specified statevar name ('true' statevar
        or attribute)

        """
        ### WARNING: strange bug found sometimes when content={} not
        ### explicitly specified, another content (from another
        ### instance ???) may be used instead !!!!
        super().__init__(**others)
        self._content = SortedDict()
        self.state_machine = state_machine
        self.init_counts()

    def init_counts(self, index=0):
        """Initialize the counts."""
        self.counts = {}
        if self.state_machine is not None:
            self.counts = {state.name: [] if self.keep_history else 0
                           for state in self.state_machine.states}
            self.counts['step'] = [] if self.keep_history else 0
        else:
            super().init_counts()

    def update_counts(self, index=0):
        """Update the number of atoms for each state of the state
        machine (TODO: for each value of the key[index] enum).

        """
        if self.state_machine is not None:
            total = {state.name: 0 for state in self.state_machine.states}
            for (key, unit) in self._content.items():
                if key[index] is not None:
                    total[key[index].name] += unit.get_information('population')
            if self.keep_history:
                self.counts['step'].append(self.statevars.step)
                for state in self.state_machine.states:
                    self.counts[state.name].append(total[state.name])
            else:
                self.counts['step'] = self.statevars.step
                self.counts.update(total)
        else:
            super().update_counts()

    def apply_changes(self, changes):
        """Apply modifications to the compartments contained in the
        current StructuredView, according to the ``changes``
        dictionary.

        """
        for source, evolutions in changes.items():
            for target, population_or_agents in evolutions:
                self._content[source].move_to(
                    self.get_or_build(target, source=self[source]),
                    state_machine=self.state_machine,
                    **population_or_agents)

    def evolve(self, machine=None):
        super().evolve(machine=machine)
        self.evolve_states()
        self.update_counts()

    def evolve_states(self, machine=None):
        """Ask each compartment to make its content evolve according
        to its current state and the specified state_machine.

        """
        future = OrderedDict()
        for name, compart in self._content.items():
            # compute the current population of each source compartment
            current_pop = compart.get_information('population')
            # no action if current pop <= 0
            if current_pop <= 0:
                continue
            # compute all possible transitions from the current state
            current_state = compart.get_information(
                self.state_machine.machine_name)
            compart.do_state_actions('on_stay', self.state_machine,
                                     current_state.name,
                                     **compart.get_content())
            transitions = compart.next_states_from(current_state.name,
                                                   self.state_machine)
#            print('TRANSITIONS = ', name, '->', transitions)
            # nothing to do if no transitions
            if not transitions:
                continue
            # retrieve the list of states, the list of flux, the list
            # of values, the list of populations affected by each
            # possible transition
            states, flux, values, populations, actions = zip(*transitions)
            # print(name, '->\n\t', states, values, [ag._agid
            #                                        for u in populations
            #                                        for ag in u['agents']])

            # add the current state to the possible destination states...
            states = states + (current_state.name,)
            # ... with no action
            actions = actions + ([], )
            # CHECK WHETHER TRANSITIONS AFFECT THE SAME
            # (SUB)POPULATION OR NOT
            identical = True
            reference_pop = None
            for other_pop in populations:
                if reference_pop is not None:
                    if reference_pop != other_pop:
                        identical = False
                        break
                reference_pop = other_pop
            if identical:
                values, method = self._compute_values_for_unique_population(
                    values, flux, reference_pop, compart.stochastic)
                change_list = compart.next_states(states,
                                                  values,
                                                  [reference_pop],
                                                  actions, method=method)
                future[name] = _rewrite_keys(name, name.index(current_state), change_list)
            else:
                values, method = self._compute_values_for_multiple_populations(
                    values, flux, populations, compart.stochastic)
                change_list = compart.next_states(states,
                                                  values,
                                                  populations,
                                                  actions,
                                                  method=method)
 #               print(change_list)
                # if name not in future:
                #     future[name] = []
                future[name] = _rewrite_keys(name, name.index(current_state), change_list)
#        print('FUTURE:', future)
        self.apply_changes(future)

    def _compute_values_for_unique_population(self,
                                              values,
                                              flux,
                                              reference_pop,
                                              stochastic):
        """Restructure the values according to the situation, for
        edges concerning the same population.

        """
        # ALL TRANSITIONS AFFECT THE SAME POPULATION (reference_pop)
        # The `values` can represent : 1) amounts - in that case no
        # transformation occurs, 2) probabilities - in that case the
        # values must be converted to rates if the target compartment
        # is deterministic, otherwise the step duration must be taken
        # into account; 3) rates - in that case the values must be
        # converted to probabilities if the target compartment is
        # stochastic
        # print('IDENTICAL')
        available_flux = set(flux)
        # try:
        assert len(available_flux) == 1 or available_flux == set(['amount', 'amount-all-but'])
        # except:
        #     print(available_flux)

        method = None
        if 'amount' in available_flux or 'amount-all-but' in available_flux:
            # handle values as amounts
            method = 'amount'
            total_ref_pop = count_population(reference_pop)
            # check that values are between 0 and the population size,
            # if needed invert 'amount-all-but' values
            values = tuple([max(0, min(total_ref_pop-v, total_ref_pop))\
                              if f == 'amount-all-but'\
                              else max(0, min(v, total_ref_pop))
                            for (f, v) in zip(flux, values)])
            # when finished the length of values is the number of
            # outgoing edges
            # print('AMOUNT', values)
        elif 'proba' in available_flux:
            if not stochastic:
                # then if the target compartment is deterministic,
                # probabilities must be converted into rates
                # print('PROBA -> RATES', values)
                values = probabilities_to_rates(values + (1 - sum(values),))
                # when finished the length of values is the number of
                # outgoing edges
                # print(values)
            else:
                # aggregate probabilities wrt the time step duration
                values = aggregate_probabilities(values, self.model.delta_t)
                values = values + (1 - sum(values),)
                # when finished the length of values is the number of
                # outgoing edges + 1
                # print('PROBA', values)
        elif not stochastic:
            # print('RATES', values)
            pass
        else:
            # otherwise values are transformed from rates to
            # probabilities
            values = rates_to_probabilities(sum(values),
                                            values,
                                            delta_t=self.model.delta_t)
            # when finished the length of values is the number of
            # outgoing edges + 1
            # print("RATES -> PROBAS", values)
        return values, method

    def _compute_values_for_multiple_populations(self,
                                                 values,
                                                 flux,
                                                 populations,
                                                 stochastic):
        """Restructure the values according to the situation, for
        edges concerning distinct populations.

        """
        # IN THAT CASE, EACH POSSIBLE TRANSITION IS RELATED TO A
        # SPECIFIC SUBGROUP OF THE COMPART.
        ### IMPORTANT: we assume that all conditions are disjoint,
        ### i.e. there is no intersection between the populations. IF
        ### NOT THE CASE, this means that the model is not really
        ### consistent, and the calculation of probabilities should be
        ### done on each individual... thus why use a StructuredView
        ### instead of a set of EvolvingAtom ???
        # print('MULTIPLE')
        pop_sets = [SortedSet(pop['agents']) for pop in populations]
        # pop_sets must be disjoint
        assert(not any([pop_sets[i] & pop_sets[j]
                        for i in range(len(pop_sets)-1)
                        for j in range(i+1, len(pop_sets))]))
        # binomial values must be computed for each transition to
        # determine how many units among the candidates will cross the
        # transition, thus we need probabilities. If all values are
        # given as rates, they must be transformed
        method = None
        available_flux = set(flux)
        # try:
        assert len(available_flux) == 1 or available_flux == set(['amount', 'amount-all-but'])
        # except:
        #     print(available_flux)

        if available_flux == {'rate'} and stochastic:
            # values are transformed from rates to probabilities
            values = rates_to_probabilities(sum(values),
                                            values,
                                            delta_t=self.model.delta_t)
            # print('RATES -> PROBAS', values)
        elif 'amount' in available_flux or 'amount-all-but' in available_flux:
            method = 'amount'
            pops = [len(p) for p in pop_sets]
            values = tuple([max(0, min(pop-v, pop))\
                              if f == 'amount-all-but'\
                              else max(0, min(v, pop))
                            for (f, v, pop) in zip(flux, values, pops)])
            values = values #+ (1 - sum(values),)
            # print('AMOUNTS:', values)
        elif 'proba' in available_flux:
            if stochastic:
                # values must be aggregated wrt the times step duration
                values = aggregate_probabilities(values,
                                                 delta_t=self.model.delta_t)
                values = values + (1 - sum(values),)
                # print('PROBAS:', values)
            else:
                # values must be transformed from probabilities to rates
                # print('PROBABILITIES -> RATES', values)
                values = probabilities_to_rates(values + (1 - sum(values),))
                # print(values)
        else:
            print('ERROR - DETERMINISTIC COMPARTMENT MODEL MUST NOT'
                  ' TRY TO HANDLE SEPARATE SUBPOPULATIONS')
        return values, method



def _rewrite_keys(name, position, change_list):
    prefix = name[:position]
    suffix = name[position+1:]
    return [(prefix + (key,) + suffix, value)
            for key, value in change_list]


#           _         _                  _
#     /\   | |       | |                | |
#    /  \  | |__  ___| |_ _ __ __ _  ___| |_
#   / /\ \ | '_ \/ __| __| '__/ _` |/ __| __|
#  / ____ \| |_) \__ \ |_| | | (_| | (__| |_
# /_/    \_\_.__/|___/\__|_|  \__,_|\___|\__|
#  _____                             __  __
# |  __ \                           |  \/  |
# | |__) | __ ___   ___ ___  ___ ___| \  / | __ _ _ __   __ _  __ _  ___ _ __
# |  ___/ '__/ _ \ / __/ _ \/ __/ __| |\/| |/ _` | '_ \ / _` |/ _` |/ _ \ '__|
# | |   | | | (_) | (_|  __/\__ \__ \ |  | | (_| | | | | (_| | (_| |  __/ |
# |_|   |_|  \___/ \___\___||___/___/_|  |_|\__,_|_| |_|\__,_|\__, |\___|_|
#                                                              __/ |
#                                                             |___/

class AbstractProcessManager(StructuredView):
    """An AbstractProcessManager is aimed handling several independent
    StructuredViews at the same time, to represent several
    concerns. It can automatically build compartments for state
    machines associated with a specific state variable or attribute.

    """
    def __init__(self, model=None, master=None, level=None, stochastic=True,
                 keep_history=False, **others):
        super().__init__(recursive=False, **others)
        self.statevars.population = 0
        self.stochastic = stochastic
        self.model = model
        self.level = level
        self.keep_history = keep_history
        if master is not None:
            self._content['MASTER'] = master
            self.no_compart = SortedSet(['MASTER'])
        else:
            self.no_compart = SortedSet()
        # machine names that potentially require state initialization
        self.init_machines = SortedSet()
        self.init_processes()
        self.initialize_level()

    def initialize_level(self, **others):
        """User-defined operations when creating an instance of this level."""
        pass

    def init_processes(self):
        """Init the processes that the ProcessManager will undergo during each
        time step, in order. Processes may be either 'method'
        processes (based on the execution of the specified method
        name), or 'group-based' processes (defined by the evolution of
        a grouping (aggregation or compartment), possibly endowed with
        a state machine), or even a 'state-machine-driven' process,
        based on the direct execution of a state machine within the
        ProcessManager.

        """
        if self.level in self.model.processes:
            for process in self.model.processes[self.level]:
                if self.level not in self.model.compartments or\
                   process not in self.model.compartments[self.level]:
                    if process in self.model.state_machines:
                        self.add_statemachine_process(process)
                    else:
                        self.add_method_process(process)
                else:
                    compart_properties = dict(
                        self.model.compartments[self.level][process])
                    for keyword in ['compart_manager', 'compart_class']:
                        if keyword in compart_properties:
                            class_desc = compart_properties[keyword]
                            # print(keyword, class_desc)
                            compart_properties[keyword] = load_class(**class_desc)
                    self.add_compart_process(process, **compart_properties)

    def evolve(self, **others):
        """Make the ProcessManager evolve, i.e. all the registered processes
        in order, starting with the evolution of the sublevels, and
        followed by the evolution inherited from superclasses.

        """
#        self['MASTER'].evolve()
        for process in self:
            process.evolve()
        super().evolve(**others)

    def add_method_process(self, process_name, method=None):
        """Add a process based on a method name."""
        # print('process:', process_name)
        if method is None:
            method = getattr(self, process_name)
        self._content[process_name] = MethodProcess(process_name, method)
        self.no_compart.add(process_name)

    def add_statemachine_process(self, process_name):
        """Add a process based on the direct execution of a state machine."""
        self._content[process_name] = StateMachineProcess(
            process_name, self, self.model.state_machines[process_name]
        )
        self.no_compart.add(process_name)

    def add_compart_process(self,
                            process_name,
                            key_variables,
                            compart_manager=(GroupManager, {}),
                            machine_name=None,
                            allowed_values=None,
                            compart_class=(AdaptiveView, {})):
        """Add a process aimed at managing a 'Compartment Manager', i.e. an
        object aimed at managing a collection of compartments. This
        compartment manager is automatically initialized from the
        `compart_manager` class (which should be a subclass of
        StructuredView or GroupManager). The compartment manager may
        be associated with a specific state machine, and MUST BE
        identified by a tuple of state variables names. Additionally,
        since a first compartment is also instantiated, a specific
        class to do so can be also specified.

        """
        args = {'keys': tuple(key_variables), 'host': self,
                'keep_history': self.keep_history}
        if machine_name:
            args['state_machine'] = self.model.state_machines[machine_name]
            # print(machine_name)
            if machine_name in self.model.init_actions:
                self.init_machines.add(machine_name)
        if allowed_values:
            args['allowed_values'] = allowed_values
        compart_manager_cl, options = compart_manager
        args.update(options)
        dict_comp = compart_manager_cl(**args)
        # update the model of the compartment manager
        dict_comp.model = self.model
        init_key = tuple(None for _ in key_variables)
        compart_class_cl, options = compart_class
        dict_comp._content[init_key] = compart_class_cl(
            recursive=False,
            stochastic=self.stochastic,
            observables=key_variables,
            keys=init_key,
            values=init_key,
            host=dict_comp, **options)
        # update the model of views
        dict_comp._content[init_key].model = self.model
        self._content[process_name] = dict_comp

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
            except Exception as exc:
                raise exc
        if not self.keep_history:
            res.update({
                'level': self.level,
                'agent_id': self.agid,
                'population': self.population})
            if self.level in self.model.outputs and\
               'extra_vars' in self.model.outputs[self.level]:
                res.update({name: self.get_information(name)
                            for name in self.model.outputs[self.level]['extra_vars']})
        return pd.DataFrame(res, index=[0])

    @abc.abstractmethod
    def remove_randomly(self, proba=0):
        """Remove randomly chosen atoms or population from this
        ProcessManager.

        """
        pass

    @property
    def population(self):
        return self.statevars.population

#  __  __       _ _   _ _____
# |  \/  |     | | | (_)  __ \
# | \  / |_   _| | |_ _| |__) | __ ___   ___ ___  ___ ___
# | |\/| | | | | | __| |  ___/ '__/ _ \ / __/ _ \/ __/ __|
# | |  | | |_| | | |_| | |   | | | (_) | (_|  __/\__ \__ \
# |_|  |_|\__,_|_|\__|_|_|   |_|  \___/ \___\___||___/___/
#  __  __
# |  \/  |
# | \  / | __ _ _ __   __ _  __ _  ___ _ __
# | |\/| |/ _` | '_ \ / _` |/ _` |/ _ \ '__|
# | |  | | (_| | | | | (_| | (_| |  __/ |
# |_|  |_|\__,_|_| |_|\__,_|\__, |\___|_|
#                            __/ |
#                           |___/

class MultiProcessManager(AbstractProcessManager):
    """A MultiProcessManager is aimed handling several independent
    StructuredViews at the same time, together with a
    SimpleView containing all the atom units. It can
    automatically build compartments for:
    - state machines associated with a specific state variable or attribute
    - specific state variables or attributes with a limited number of
    values, such as booleans or enumerations

    """
    def __init__(self, model=None, level=None, **others):
        view_class, options = load_class(
            **model.levels[level]['super']['master']
        )
        master = view_class(keys='MASTER', host=self, recursive=True, **options)
        super().__init__(model=model, master=master, level=level, **others)

    def add_compart_process(self,
                            process_name,
                            key_variables,
                            compart_manager=(GroupManager, {}),
                            machine_name=None,
                            allowed_values=None,
                            compart_class=(AdaptiveView, {})):
        super().add_compart_process(process_name, key_variables,
                                    compart_manager=compart_manager,
                                    machine_name=machine_name,
                                    allowed_values=allowed_values,
                                    compart_class=compart_class)

    def select_atoms(self, variable, state=None, value=None, process=None):
        """Return a list of atoms having `variable` equal to the specified `state_name`.

        """
        if state is not None:
            value = self.model.get_value(state)
        if process is not None:
            if (value,) in self[process]._content:
                result = list(self[process][(value,)]._content)
        return [agent for agent in self['MASTER']
                if agent.get_information(variable) == value]

    def get_agent_class_for_sublevel(self, sublevel):
        """Return the agent class in charge of representing the specified
        sublevel.

        """
        if sublevel not in self.model.levels:
            raise LevelException('not found', sublevel)
        if 'contains' not in self.model.levels[self.level]:
            raise LevelException('not linked with %s' % (self.level), sublevel)
        cl, _ = self.model.get_agent_class_for_level(sublevel)
        return cl

    def new_atom(self, sublevel=None, prototype=None, **args):
        """Instantiate a new atom for the specified sublevel, with the
        specified arguments. If the sublevel is not specified, the
        first one from the `contains` list is taken. If the name of a
        prototype is provided, it is applied to the new agent.

        """
        if sublevel is None:
            if 'contains' not in self.model.levels[self.level]:
                raise LevelException('not specified for atom creation', '')
            sublevel = self.model.levels[self.level]['contains'][0]
        atom_class = self.get_agent_class_for_sublevel(sublevel)
        args.update(model=self.model)
        new_atom = atom_class(level=sublevel, **args)
        if prototype is not None:
            new_atom.apply_prototype(prototype)
        return new_atom

    def add_atoms(self, atom_set, init=False, level=None):

        """Add the specified set of atoms to the current
        MultiProcessManager. Atoms are especially added
        automatically to each of the compartment managers.  If `init`
        is True, the compartment managers counts the initial value of
        the populations in each compartment.

        """
        self['MASTER'].add(atom_set)
        self.statevars.population = len(self['MASTER']._content)
        # update the model of atoms
        if level is None:
            if 'contains' in self.model.levels[self.level]:
                level = self.model.levels[self.level]['contains'][0]
        for atom in atom_set:
            atom.model = self.model
            atom.level = level
        # check if any initialization action has to be performed
        for machine in self.init_machines:
            agents_to_init = OrderedDict()
            for atom in atom_set:
                state = atom.statevars[machine]
                if state in self.model.init_actions[machine]:
                    if state not in agents_to_init:
                        agents_to_init[state] = []
                    agents_to_init[state].append(atom)
            for state, atoms in agents_to_init.items():
                for action in self.model.init_actions[machine][state]:
                    action.execute_action(self['MASTER'], agents=atoms)

        # add atoms to appropriate compartments and make them
        # consistent
        for name, comp in self._content.items():
            if name not in self.no_compart:
                default_key = tuple(None for _ in comp.keys)
                comp[default_key].add(atom_set)
                self.make_consistent(comp)
                if init:
                    comp.update_counts()

    def make_consistent(self, compartment):
        """Make the specified dict compartment check and handle the
        consistency of its own sub-compartments.

        """
        for comp in compartment:
            comp.check_consistency()
        compartment.handle_notifications()

    def remove_atoms(self, atom_set):
        """Remove the specified atoms from the current
        MultiProcessManager. Atoms are removed from each of the
        compartment managers (including the 'MASTER' set).

        """
        for atom in list(atom_set):
            for host in list(atom._host.values()):
                host.remove([atom])
        self.statevars.population = len(self['MASTER']._content)

    def select_randomly(self, proba=0, amount=None, process=None):
        """Select randomly chosen atoms from this ProcessManager. `proba` can
        be either a probability or a dictionary. In that case, the
        `process` parameter indicates the name of the process grouping
        which drives the probabilities, and the keys must be those of
        the grouping. Selected atoms are removed and returned by the
        method.

        """
        if self.population <= 0:
            return []
        if process is None:
            if amount is None:
                amount = np.random.binomial(len(self['MASTER']), proba)
            selection = select_random(self['MASTER'], amount)
        else:
            selection = []
            if amount is None:
                for key, compart in self[process].items():
                    if key in proba:
                        selection += select_random(
                            compart, np.random.binomial(len(compart),
                                                        proba[key]))
            else:
                return []       #  inconsistent call
        return selection

    def remove_randomly(self, proba=0, amount=None, process=None):
        """Remove randomly chosen atoms from this ProcessManager. `proba` can
        be either a probability or a dictionary. In that case, the
        `process` parameter indicates the name of the process grouping
        which drives the probabilities, and the keys must be those of
        the grouping. Selected atoms are removed and returned by the
        method.

        """
        to_remove = self.select_randomly(amount=amount, proba=proba,
                                         process=process)
        self.remove_atoms(to_remove)
        # print(to_remove)
        return to_remove


#  __  __      _
# |  \/  |    | |
# | \  / | ___| |_ __ _ _ __   ___  _ __
# | |\/| |/ _ \ __/ _` | '_ \ / _ \| '_ \
# | |  | |  __/ || (_| | |_) | (_) | |_) |
# |_|  |_|\___|\__\__,_| .__/ \___/| .__/
#                      | |         | |
#                      |_|         |_|

class MetapopProcessManager(MultiProcessManager):
    """This class is in charge of handling multiple populations."""

    def get_populations(self):
        return OrderedDict(self['MASTER']._content)

    @property
    def counts(self):
        """Return a pandas DataFrame containing counts of each process if
        existing.

        """
        result = None
        for population in self['MASTER']:
            res = {}
            for comp in population:
                try:
                    res.update(comp.counts)
                except AttributeError:
                    pass
                except Exception as exc:
                    raise exc
            if not self.keep_history:
                res.update({
                    'level': population.level,
                    'agent_id': population.agid,
                    'population': population.population,
                    'population_id': population.statevars.population_id})
                if population.level in population.model.outputs and\
                   'extra_vars' in population.model.outputs[population.level]:
                    res.update({name: population.get_information(name)
                                for name in population.model.outputs[population.level]['extra_vars']})
            result = pd.DataFrame(res, index=[0]) if result is None\
                        else result.append(pd.DataFrame(res, index=[0]))
        return result



#   _____                                 _   _____
#  / ____|                               | | |  __ \
# | |     ___  _ __ ___  _ __   __ _ _ __| |_| |__) | __ ___   ___ ___  ___ ___
# | |    / _ \| '_ ` _ \| '_ \ / _` | '__| __|  ___/ '__/ _ \ / __/ _ \/ __/ __|
# | |___| (_) | | | | | | |_) | (_| | |  | |_| |   | | | (_) | (_|  __/\__ \__ \
#  \_____\___/|_| |_| |_| .__/ \__,_|_|   \__|_|   |_|  \___/ \___\___||___/___/
#                       | |
#                       |_|
#  __  __
# |  \/  |
# | \  / | __ _ _ __   __ _  __ _  ___ _ __
# | |\/| |/ _` | '_ \ / _` |/ _` |/ _ \ '__|
# | |  | | (_| | | | | (_| | (_| |  __/ |
# |_|  |_|\__,_|_| |_|\__,_|\__, |\___|_|
#                            __/ |
#                           |___/

class CompartProcessManager(AbstractProcessManager):
    """A CompartProcessManager is aimed handling several independent
    StructuredViews at the same time, for managing true compartments.
    It can automatically allocate compartments for state machines
    associated with a specific state variable or attribute.

    """


    def add_compart_process(self,
                            process_name,
                            key_variables,
                            compart_manager=(GroupManager, {}),
                            machine_name=None,
                            compart_class=(Compartment, {})):
        super().add_compart_process(process_name, key_variables,
                                    compart_manager=compart_manager,
                                    machine_name=machine_name,
                                    compart_class=compart_class)

    def add_population(self, population_spec, init=False):
        """Add the specified population specification to the current
        CompartProcessManager. `population_spec` is a dictionary with
        process names as keys, each one associated with a dictionary
        (tuple of statevars) -> population. If `init` is True, the compartment
        managers counts the initial value of the populations in each
        compartment.

        """
        # add populations to appropriate compartments for each process

        added = {}
        for process, spec in population_spec.items():
            if process not in self.no_compart:
                # retrieve the group manager associated to the process
                manager = self[process]
                # retrieve the machine name (always here in compartment models)
                machine_name = manager.state_machine.machine_name
                # locate the index of the statevar holding the state
                # of the state machine
                index = manager.keys.index(machine_name)\
                        if machine_name in manager.keys else None
                default_key = tuple(None for _ in manager.keys)
                added[process] = 0
                for key, qty in spec.items():
                    if key not in manager._content:
                        new_comp = manager[default_key].clone(population=qty)
                        if index is not None:
                            new_comp.statevars[machine_name] = key[index]
                        new_comp.keys = key
                        manager._content[key] = new_comp
                    else:
                        manager[key].add(qty)
                    added[process] += qty
                if init:
                    manager.update_counts()
        nb = set(added.values())
        assert(len(nb) <= 1)
        if nb:
            self.statevars.population += nb.pop()


    def remove_population(self, population_spec):
        """Remove the specified population spec from the current
        CompartProcessManager.

        """
        removed = {}
        for process, spec in population_spec.items():
            if process not in self.no_compart:
                # print(process, spec)
                manager = self[process]
                removed[process] = 0
                for key, qty in spec.items():
                    if key in manager._content:
                        manager[key].remove(qty)
                        removed[process] += qty
        nb = set(removed.values())
        assert(len(nb) <= 1)
        if nb:
            self.statevars.population -= nb.pop()

    def remove_randomly(self, proba=0, amount=None, process=None):
        """Remove random amounts of populations from this ProcessManager. If
        `amount` is not None, a multinomial sampling is performed for
        each process. Otherwise: `proba` can be either a probability
        or a dictionary. In that case, the `process` parameter
        indicates the name of the process grouping which drives the
        probabilities, and the keys must be those of the
        grouping. Selected quantities are removed and returned by the
        method.

        """
        to_remove = {}
        total = None
        if amount is not None:
            for name, proc in self._content.items():
                keys, probas = zip(*[(key, comp.population/self.population)
                                     for key, comp in proc.items()])
                amounts = np.random.multinomial(amount, probas)
                to_remove[name] = dict(zip(keys, amounts))
            self.remove_population(to_remove)
            return to_remove

        if process is not None:
            to_remove[process] = {}
            total = 0
            # print(self._content, process, name, self.no_compart)
            for key, comp in self[process].items():
                pop = comp.statevars.population
                if key in proba:
                    n = np.random.binomial(pop, proba[key])
                    to_remove[process][key] = n
                    total += n
        for name, proc in self._content.items():
            if name in self.no_compart or name == process:
                continue
            if total is None:
                to_remove[name] = {}
                total = 0
                for key, comp in proc._content.items():
                    pop = comp.statevars.population
                    n = np.random.binomial(pop, proba)
                    to_remove[name][key] = n
                    total += n
                continue
            keys, pops = zip(*[(key, comp.statevars.population)
                               for key, comp in self[name].items()])
            total_pop = sum(pops)
            probas = [ n / total_pop for n in pops]
            qties = np.random.multinomial(total, probas)
            to_remove[name] = dict(zip(keys, qties))
        # print(to_remove)
        self.remove_population(to_remove)
        return to_remove



#  _____ ____  __  __ _____
# |_   _|  _ \|  \/  |  __ \
#   | | | |_) | \  / | |__) | __ ___   ___ ___  ___ ___
#   | | |  _ <| |\/| |  ___/ '__/ _ \ / __/ _ \/ __/ __|
#  _| |_| |_) | |  | | |   | | | (_) | (_|  __/\__ \__ \
# |_____|____/|_|  |_|_|   |_|  \___/ \___\___||___/___/
#  __  __
# |  \/  |
# | \  / | __ _ _ __   __ _  __ _  ___ _ __
# | |\/| |/ _` | '_ \ / _` |/ _` |/ _ \ '__|
# | |  | | (_| | | | | (_| | (_| |  __/ |
# |_|  |_|\__,_|_| |_|\__,_|\__, |\___|_|
#                            __/ |
#                           |___/

class IBMProcessManager(MultiProcessManager):
    """An IBMProcessManager is a MultiProcessManager dedicated to the
    management of Individual-Based Models. This class is endowed with
    a `counters` attribute which is a dictionary {process -> counter of
    states in relation with the process}.

    """
    def __init__(self, **others):
        super().__init__(**others)
        self.statemachines = self.find_sublevel_statemachines()
        self.counters = {
            machine.machine_name: Counter(
                atom.statevars[machine.machine_name].name
                for atom in self['MASTER']
            )
            for machine in self.statemachines
        }
        for atom in self['MASTER']:
            atom.set_statemachines(self.statemachines)
            atom.init_level_processes()

    def add_atoms(self, atom_set, init=False, **others):
        super().add_atoms(atom_set, init=init, **others)
        if not init:
            for atom in self['MASTER']:
                atom.set_statemachines(self.statemachines)
                atom.init_level_processes()


    def find_sublevel_statemachines(self):
        """Retrieve state machines used as processes by agents from the
        sub-level.

        """
        if 'contains' not in self.model.levels[self.level]:
            return []
        return set([self.model.state_machines[process]
                    for sublevel in self.model.levels[self.level]['contains']
                    for process in self.model.processes[sublevel]
                    if process in self.model.state_machines])

    def evolve(self, **others):
        """Make the agent evolve and update counts based on sub-level
        agents.

        """
        super().evolve(**others)
        self.update_counts()

    def update_counts(self):
        """Update counters based on invdividual status."""

        for name, counter in self.counters.items():
            counter.clear()
            counter.update([atom.statevars[name].name
                            for atom in self['MASTER']])

    @property
    def counts(self):
        """Return a pandas DataFrame containing counts of each process if
        existing.

        """
        res = {state.name: self.counters[state_machine.machine_name][state.name]
               for state_machine in self.statemachines
               for state in state_machine.states}
        res.update({'step': self.statevars.step,
                    'level': self.level,
                    'agent_id': self.agid,
                    'population': self.population})
        if self.level in self.model.outputs and\
           'extra_vars' in self.model.outputs[self.level]:
            res.update({name: self.get_information(name)
                        for name in self.model.outputs[self.level]['extra_vars']})
        return pd.DataFrame(res, index=[0])

    def remove_randomly(self, proba=0, statevar=None):
        """Remove randomly chosen atoms from this ProcessManager. `proba` can
        be either a probability or a dictionary. In that case, the
        `statevar` parameter indicates the name of the state variable
        which drives the probabilities, and the keys must be valid
        values for this state variable. Selected atoms are removed and
        returned by the method.

        """
        if statevar is None:
            to_remove = select_random(self['MASTER'],
                                      np.random.binomial(len(self['MASTER']),
                                                         proba))
        else:
            to_remove = []
            for atom in self['MASTER']:
                val = atom.get_information(statevar)
                if val in proba:
                    if np.random.binomial(1, proba[val]):
                        to_remove.append(atom)
        self.remove_atoms(to_remove)
        # print(to_remove)
        return to_remove

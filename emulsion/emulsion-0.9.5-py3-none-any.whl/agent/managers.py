"""A Python implementation of the EMuLSion framework.

(Epidemiologic MUlti-Level SImulatiONs).

Classes and functions for entities management.

"""

from   collections               import OrderedDict

from   sortedcontainers          import SortedSet, SortedDict

from   emulsion.agent.views      import StructuredView, AdaptiveView
from   emulsion.agent.process    import MethodProcess
from   emulsion.tools.misc       import load_class, rates_to_probabilities,\
                                   count_population, aggregate_probabilities,\
                                   probabilities_to_rates




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
        self.counts = {state.name: [] if self.keep_history else 0
                       for state in self.state_machine.states}
        self.counts['step'] = [] if self.keep_history else 0

    def update_counts(self, index=0):
        """Update the number of atoms for each state of the state
        machine (TODO: for each value of the key[index] enum).

        """
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

    def apply_changes(self, changes):
        """Apply modifications to the compartments contained in the
        current StructuredView, according to the ``changes``
        dictionary.

        """
        for source, evolutions in changes.items():
            for target, population_or_agents in evolutions:
                self._content[source].move_to(
                    self.get_or_build(target, model=self[source]),
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

class MultiProcessManager(StructuredView):
    """A MultiProcessManager is aimed handling several independent
    StructuredViews at the same time, together with a
    SimpleView containing all the atom units. It can
    automatically build compartments for:
    - state machines associated with a specific state variable or attribute
    - specific state variables or attributes with a limited number of
    values, such as booleans or enumerations

    """
    def __init__(self, model=None, level='herd', keep_history=True, **others):
        super().__init__(recursive=False, **others)
#        self._content = OrderedDict()
        #        self.model = model.copy()
        self.model = model
        self.level = level
        self.keep_history = keep_history
        view_class, options = load_class(
            **model.levels[level]['super']['master']
        )
        self._content['MASTER'] = view_class(keys='MASTER',
                                             host=self,
                                             recursive=True,
                                             **options)
        self.no_compart = SortedSet(['MASTER'])
        # machine names that potentially require state initialization
        self.init_machines = SortedSet()
        self.init_processes()

    def init_processes(self):
        """Init the processes that the MultiProcessManager will
        undergo during each time step, in order. Processes may be either
        'method' processes (based on the execution of the specified
        method name), or 'compartiment-based' processes (defined by the
        evolution of a compartment, possibly endowed with a state
        machine).

        """
        for process in self.model.processes[self.level]:
            if process not in self.model.compartments[self.level]:
                self.add_method_process(process)
            else:
                compart_properties = dict(self.model.compartments[self.level][process])
                for keyword in ['compart_manager', 'compart_class']:
                    if keyword in compart_properties:
                        class_desc = compart_properties[keyword]
                        # print(keyword, class_desc)
                        compart_properties[keyword] = load_class(**class_desc)
                self.add_compart_process(process, **compart_properties)


    def evolve(self, **others):
        """Make the MultiProcessManager evolve, i.e. all the
        registered processes in order, starting with the evolution of
        the atoms, and followed by the evolution inherited from
        superclasses.

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


    def add_compart_process(self,
                            process_name,
                            key_variables,
                            compart_manager=(GroupManager, {}),
                            machine_name=None,
                            compart_class=(AdaptiveView, {})):
        """Add a process aimed at managing a 'Compartment Manager',
        i.e. an object aimed at managing a collection of
        compartments. This compartment manager is automatically
        initialized from the `compart_manager` class (which should be
        a subclass of StructuredView or GroupManager). The compartment
        manager may be associated with a specific state machine, and
        MUST BE identified by a tuple of state variables
        names. Additionally, since a first compartment is also
        instantiated, a specific class to do so can be also
        specified.

        """
        # print('compart:', process_name)
        # print([s for s in self._content])
        # print(compart_manager.__name__, compart_class.__name__)
        args = {'keys': tuple(key_variables), 'host': self, 'keep_history': self.keep_history}
        if machine_name:
            args['state_machine'] = self.model.state_machines[machine_name]
            # print(machine_name)
            if machine_name in self.model.init_actions:
                self.init_machines.add(machine_name)
        compart_manager, options = compart_manager
        args.update(options)
        dict_comp = compart_manager(**args)
        # update the model of the compartment manager
        dict_comp.model = self.model
        init_key = tuple(None for _ in key_variables)
        compart_class, options = compart_class
        dict_comp._content[init_key] = compart_class(recursive=False,
                                                     observables=key_variables,
                                                     keys=init_key,
                                                     values=init_key,
                                                     host=dict_comp, **options)
        # update the model of views
        dict_comp._content[init_key].model = self.model
        self._content[process_name] = dict_comp

    def add_atoms(self, atom_set, init=False):
        """Add the specified set of atoms to the current
        MultiProcessManager. Atoms are especially added
        automatically to each of the compartment managers.  If `init`
        is True, the compartment managers counts the initial value of
        the populations in each compartment.

        """
        self['MASTER'].add(atom_set)
        # update the model of atoms
        for atom in atom_set:
            atom.model = self.model
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

class CompartProcessManager(StructuredView):
    """A CompartProcessManager is aimed handling several independent
    StructuredViews at the same time. It can automatically build compartments
    for:
    - state machines associated with a specific state variable or attribute
    - specific state variables or attributes with a limited number of
    values, such as booleans or enumerations

    """
    def __init__(self, model=None, level='herd', keep_history=True, **others):
        super().__init__(recursive=False, **others)
#        self._content = OrderedDict()
        #        self.model = model.copy()
        self.model = model
        self.level = level
        self.keep_history = keep_history
        # ViewClass, options = load_class(**model.levels[level]['super']['master'])
        # self._content['MASTER'] = ViewClass(keys='MASTER',
        #                                      host=self,
        #                                      recursive=True,
        #                                      **options)
        # self.no_compart=SortedSet(['MASTER'])
        # machine names that potentially require state initialization
        self.init_machines = SortedSet()
        self.init_processes()

    def init_processes(self):
        """Init the processes that the MultiProcessManager will
        undergo during each time step, in order. Processes may be either
        'method' processes (based on the execution of the specified
        method name), or 'compartiment-based' processes (defined by the
        evolution of a compartment, possibly endowed with a state
        machine).

        """
        for process in self.model.processes[self.level]:
            if process not in self.model.compartments[self.level]:
                self.add_method_process(process)
            else:
                compart_properties = dict(self.model.compartments[self.level][process])
                for keyword in ['compart_manager', 'compart_class']:
                    if keyword in compart_properties:
                        class_desc = compart_properties[keyword]
                        # print(keyword, class_desc)
                        compart_properties[keyword] = load_class(**class_desc)
                self.add_compart_process(process, **compart_properties)


    def evolve(self, **others):
        """Make the MultiProcessManager evolve, i.e. all the
        registered processes in order, starting with the evolution of
        the atoms, and followed by the evolution inherited from
        superclasses.

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


    def add_compart_process(self,
                            process_name,
                            key_variables,
                            compart_manager=(GroupManager, {}),
                            machine_name=None,
                            compart_class=(AdaptiveView, {})):
        """Add a process aimed at managing a 'Compartment Manager',
        i.e. an object aimed at managing a collection of
        compartments. This compartment manager is automatically
        initialized from the `compart_manager` class (which should be
        a subclass of StructuredView or GroupManager). The compartment
        manager may be associated with a specific state machine, and
        MUST BE identified by a tuple of state variables
        names. Additionally, since a first compartment is also
        instantiated, a specific class to do so can be also
        specified.

        """
        # print('compart:', process_name)
        # print([s for s in self._content])
        # print(compart_manager.__name__, compart_class.__name__)
        args = {'keys': tuple(key_variables), 'host': self, 'keep_history': self.keep_history}
        if machine_name:
            args['state_machine'] = self.model.state_machines[machine_name]
            # print(machine_name)
            if machine_name in self.model.init_actions:
                self.init_machines.add(machine_name)
        compart_manager, options = compart_manager
        args.update(options)
        dict_comp = compart_manager(**args)
        # update the model of the compartment manager
        dict_comp.model = self.model
        init_key = tuple(None for _ in key_variables)
        compart_class, options = compart_class
        dict_comp._content[init_key] = compart_class(recursive=False,
                                                     observables=key_variables,
                                                     keys=init_key,
                                                     values=init_key,
                                                     host=dict_comp, **options)
        # update the model of views
        dict_comp._content[init_key].model = self.model
        self._content[process_name] = dict_comp

    def add_atoms(self, atom_set, init=False):
        """Add the specified set of atoms to the current
        MultiProcessManager. Atoms are especially added
        automatically to each of the compartment managers.  If `init`
        is True, the compartment managers counts the initial value of
        the populations in each compartment.

        """
        self['MASTER'].add(atom_set)
        # update the model of atoms
        for atom in atom_set:
            atom.model = self.model
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

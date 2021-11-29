"""
.. module:: emulsion.agent.managers.functions

.. moduleauthor:: Sébastien Picault <sebastien.picault@inra.fr>

"""


# EMULSION (Epidemiological Multi-Level Simulation framework)
# ===========================================================
# 
# Contributors and contact:
# -------------------------
# 
#     - Sébastien Picault (sebastien.picault@inrae.fr)
#     - Yu-Lin Huang
#     - Vianney Sicard
#     - Sandie Arnoux
#     - Gaël Beaunée
#     - Pauline Ezanno (pauline.ezanno@inrae.fr)
# 
#     INRAE, Oniris, BIOEPAR, 44300, Nantes, France
# 
# 
# How to cite:
# ------------
# 
#     S. Picault, Y.-L. Huang, V. Sicard, S. Arnoux, G. Beaunée,
#     P. Ezanno (2019). "EMULSION: Transparent and flexible multiscale
#     stochastic models in human, animal and plant epidemiology", PLoS
#     Computational Biology 15(9): e1007342. DOI:
#     10.1371/journal.pcbi.1007342
# 
# 
# License:
# --------
# 
#     Copyright 2016 INRAE and Univ. Lille
# 
#     Inter Deposit Digital Number: IDDN.FR.001.280043.000.R.P.2018.000.10000
# 
#     Agence pour la Protection des Programmes,
#     54 rue de Paradis, 75010 Paris, France
# 
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
# 
#         http://www.apache.org/licenses/LICENSE-2.0
# 
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

from   collections               import OrderedDict

from   sortedcontainers          import SortedDict

from   emulsion.agent.views      import StructuredView
from   emulsion.tools.misc       import count_population, rewrite_keys

from   emulsion.agent.managers.functions import group_and_split_populations

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
        self.process_name = None
        self.init_counts()

    def init_counts(self, index=0):
        """Initialize the counts."""
        ## DEBUG
        # print('STEP', self.statevars.step, '\nInit counts in GM', self)
        self.counts = {}
        if self.state_machine is not None:
            self.counts = {state.name: [] if self.keep_history else 0
                           for state in self.state_machine.states}
            self.counts['step'] = [] if self.keep_history else 0
        else:
            super().init_counts()
        ## DEBUG
        # print(self.counts)

    def update_counts(self, index=0):
        """Update the number of atoms for each state of the state
        machine (TODO: for each value of the key[index] enum).

        """
        if self.state_machine is not None:
            total = {state.name: 0 for state in self.state_machine.states}
            ## DEBUG
            # print('\t', self.statevars.step, sep='')
            for (key, unit) in self._content.items():
                if key[index] is not None and key[index].name in total:
                    total[key[index].name] += unit.get_information('population')
                    # total[key[index].name] += unit.population
                    ## DEBUG
                    # print(key, unit.population, sep=' + ')
            # print()
            # print(self, self.statevars.step)
            if self.keep_history:
                self.counts['step'].append(self.statevars.step)
                for state in self.state_machine.states:
                    self.counts[state.name].append(total[state.name])
            else:
                self.counts['step'] = self.statevars.step
                self.counts.update(total)
        else:
            super().update_counts()
        ## DEBUG
        # print('STEP', self.statevars.step, '\nUPDATE', self.counts)

    def apply_changes(self, transitions, productions):
        """Apply modifications to the compartments contained in the current
        StructuredView, according to `transitions` and
        `productions`. Dictionary `transitions` is keyed by a tuple of
        variables and associated with a list of dictionaries, either
        {'population': qty, 'actions': list} or {'agents': list,
        'actions': list}. List `productions` contains tuples (target,
        {'population': qty}, None) or (target, {'agents': list},
        prototype).

        """
        for source, evolutions in transitions.items():
            for target, population_or_agents in evolutions:
                target_comp = self.get_or_build(target, source=self[source])
                self._content[source].move_to(
                    target_comp,
                    state_machine=self.state_machine,
                    **population_or_agents)
        self.new_population = productions

    def evolve(self, machine=None):
        super().evolve(machine=machine)
        ## DEBUG
        # print(self.statevars.step, self.counts)
        if self.statevars._is_active:
            self.evolve_states()
            ## DEBUG
            # print(self.statevars.step, self.counts)
            for key, comp in self._content.items():
                if comp.autoremove:
                    agents_or_population = comp.get_content()
                    if agents_or_population[0] == 'population':
                        agents_or_population = (agents_or_population[0],
                                                {self.process_name: {
                                                    key: agents_or_population[1]
                                                }})
                    self._host.remove(agents_or_population)
            self.update_counts()
        ## DEBUG
        # print(self.statevars.step, self.counts)

    def evolve_states(self, machine=None):
        """Ask each compartment to make its content evolve according
        to its current state and the specified state_machine.

        """
        self.new_population = None
        transitions = self._evolve_transitions(machine=machine)
        productions = self._evolve_productions(machine=machine)
        self.apply_changes(transitions, productions)

    def _evolve_transitions(self, machine=None):
        # init empty dictionary for all changes to perform
        future = OrderedDict()
        # iterate over all compartments
        for name, compart in self._content.items():
            future[name] = []
            # compute the current population of each source compartment
            current_pop = compart.get_information('population')
            # no action if current pop <= 0
            if current_pop <= 0:
                continue
            # compute all possible transitions from the current state
            current_state = compart.get_information(
                self.state_machine.machine_name)
            # execute actions on stay for current state
            compart.do_state_actions('on_stay', self.state_machine,
                                     current_state.name,
                                     **dict([compart.get_content()]))
            # get the possible transitions from the current state
            # i.e. a list of tuples (state, flux, value, cond_result,
            # actions) where:
            # - state is a possible state reachable from the current state
            # - flux is either 'rate' or 'proba' or 'amount' or 'amount-all-but'
            # - value is the corresponding rate or probability or amount
            # - cond_result is a tuple (either ('population', qty) or
            # ('agents', list)) describing who fulfills the condition to cross
            # the transition
            # - actions is the list of actions on cross
            transitions = compart.next_states_from(current_state.name,
                                                   self.state_machine)
            # print('TRANSITIONS = ', name, '->', transitions)
            # nothing to do if no transitions
            if not transitions:
                continue

            ### REWRITE TRANSITIONS TO HAVE DISJOINT SUB-POPULATIONS
            transitions_by_pop = group_and_split_populations(transitions)
            # print(transitions_by_pop)
            for ref_pop, properties in transitions_by_pop:
                # retrieve the list of states, the list of flux, the
                # list of values, the list of populations affected by
                # each possible transition
                states, flux, values, actions = zip(*properties)
                # print(name, '->\n\t', states, values, [ag._agid
                #                                        for u in populations
                #                                        for ag in u['agents']])
                # add the current state to the possible destination states...
                states = states + (current_state.name,)
                # ... with no action
                actions = actions + ([], )
                #
                values, method = self._compute_values_for_unique_population(
                    values, flux, ref_pop, compart.stochastic)
                change_list = compart.next_states(states,
                                                  values,
                                                  [ref_pop],
                                                  actions, method=method)
                future[name] += rewrite_keys(name, name.index(current_state),
                                              change_list)
        # print('FUTURE:', future)
        return future


    def _evolve_productions(self, machine=None):
        # init empty list for all changes to perform
        future = []
        # iterate over all compartments
        for name, compart in self._content.items():
            # compute the current population of each source compartment
            current_pop = max(compart.get_information('population'), 0)
            # no action if "fake" compartment
            if set(name) == {None}:
                continue
            # if current pop == 0, productions are still possible (e.g. amounts)
            # compute all possible transitions from the current state
            current_state = compart.get_information(self.state_machine.machine_name)
            # get the possible productions from the current state
            # i.e. a list of tuples (state, flux, value, cond_result,
            # prototype) where:
            # - state is a possible state producible from the current state
            # - flux is either 'rate' or 'proba' or 'amount' or 'amount-all-but'
            # - value is the corresponding rate or probability or amount
            # - cond_result is a tuple (either ('population', qty) or
            # ('agents', list)) describing who fulfills the condition to cross
            # the transition
            # - prototype is the prototype for creating new agents
            productions = compart.production_from(current_state.name, self.state_machine)
            # print('PRODUCTIONS = ', productions)
            # nothing to do if no transitions
            if not productions:
                continue
            ### HERE WE ASSUME THAT AN AGENT CAN PRODUCE SEVERAL OTHER
            ### AGENTS SIMULTANEOUSLY (OTHERWISE USE CONDITIONS)
            ### REWRITE TRANSITIONS TO HAVE DISJOINT SUB-POPULATIONS
            for target_state, flux, values, ref_pop, proto in productions:
                pop_size = count_population(ref_pop)
                amount = self._compute_production(values, flux, pop_size, compart.stochastic)
                if amount > 0:
                    future.append((target_state, amount, proto))
        # print('FUTURE:', future)
        return future

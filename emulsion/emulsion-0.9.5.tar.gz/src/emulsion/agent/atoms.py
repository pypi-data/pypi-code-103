"""A Python implementation of the EMuLSion framework.

(Epidemiologic MUlti-Level SImulatiONs).

Classes and functions for entities management.

"""

from   collections               import OrderedDict

from   emulsion.agent.core       import EmulsionAgent
from   emulsion.agent.process    import StateMachineProcess, MethodProcess

#          _                                           _
#     /\  | |                    /\                   | |
#    /  \ | |_ ___  _ __ ___    /  \   __ _  ___ _ __ | |_
#   / /\ \| __/ _ \| '_ ` _ \  / /\ \ / _` |/ _ \ '_ \| __|
#  / ____ \ || (_) | | | | | |/ ____ \ (_| |  __/ | | | |_
# /_/    \_\__\___/|_| |_| |_/_/    \_\__, |\___|_| |_|\__|
#                                      __/ |
#                                     |___/

class AtomAgent(EmulsionAgent):
    """The AtomAgent is aimed at representing an 'individual', i.e. the
    smallest organization level to be modeled as an entity in the
    simulation. An AtomAgent may be situated in several hosts, each one
    associated with a specific tuple of state variables.

    """
    def __init__(self, **others):
        super().__init__(**others)
        self.statevars.population = 1
        self._host = OrderedDict()
        if 'host' in others:
            self.add_host(others['host'])
    def __len__(self):
        return 1

    def get_content(self):
        """Return the population (1) of the current unit.

        """
        return {'population': 1}

    def add_host(self, host):
        """Add the specified host to the current AtomAgent, associated
        with the specified key.

        """
        self._host[host.keys] = host
        self.simulation = host.simulation

    def remove_host(self, host, keys=None):
        """Remove the specified host from the current AtomAgent,
        associated with the specified key.

        """
        if keys is None:
            del self._host[host.keys]
        else:
            del self._host[keys]

    def get_host(self, key='MASTER'):
        """Retrieve the host of the current AtomAgent identified by the
        specific key.

        """
        return self._host[key]

    def clone(self, prototype=None, **others):
        """Make a copy of the current compartment with the specified
        observable/value settings. If a prototype is provided, it is
        applied to the new atom.

        """
        new_atom = self.__class__.from_dict(self.statevars)
        new_atom.model = self.model
        new_atom.level = self.level
        new_atom.statevars.update(**others)
        if prototype is not None:
            new_atom.apply_prototype(prototype)
        return new_atom


#  ______          _       _                     _
# |  ____|        | |     (_)               /\  | |
# | |____   _____ | |_   ___ _ __   __ _   /  \ | |_ ___  _ __ ___
# |  __\ \ / / _ \| \ \ / / | '_ \ / _` | / /\ \| __/ _ \| '_ ` _ \
# | |___\ V / (_) | |\ V /| | | | | (_| |/ ____ \ || (_) | | | | | |
# |______\_/ \___/|_| \_/ |_|_| |_|\__, /_/    \_\__\___/|_| |_| |_|
#                                   __/ |
#                                  |___/

class EvolvingAtom(AtomAgent):
    """An EvolvingAtom is able to change state according to its
    own statemachines.

    """
    def __init__(self, statemachines=[], **others):
        super().__init__(**others)
        self.processes = []
        self.statemachine_processes = {}
        self.method_processes = {}
        if statemachines:
            self.set_statemachines(statemachines)

    def set_statemachines(self, statemachines):
        """Define the state machines that this agent is able to execute."""
        self.statemachine_processes = {
            sm.machine_name: StateMachineProcess(sm.machine_name, self, sm)
            for sm in statemachines
        }

    def init_level_processes(self):
        """Initialize the level of the agent."""
        if self.level in self.model.processes:
            self.processes = self.model.processes[self.level]
            for process in self.processes:
                if process not in self.statemachine_processes:
                    self.add_method_process(process)

    def add_method_process(self, process_name, method=None):
        """Add a process based on a method name."""
        # print('process:', process_name)
        if method is None:
            method = getattr(self, process_name)
        self.method_processes[process_name] = MethodProcess(process_name, method)

    def get_machine(self, name):
        """Return the state machine with the specified name."""
        return self.statemachine_processes[name].state_machine

    def evolve(self, machine=None):
        super().evolve(machine=machine)
        self.evolve_states()

    def evolve_states(self, machine=None):
        """Change the state of the current unit according to the
        specified state machine name. If no special state machine is
        provided, executes all the machines.

        """
        # retrieve the iterable containing the processes to execute
        if machine is not None:
            self.statemachine_processes[machine].evolve()
        else:
            for process_name in self.processes:
                process = self.statemachine_processes[process_name]\
                            if process_name in self.statemachine_processes\
                            else self.method_processes[process_name]
                process.evolve()

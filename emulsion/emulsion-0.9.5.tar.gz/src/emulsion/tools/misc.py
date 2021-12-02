"""A Python implementation of the EMuLSion framework.
(Epidemiologic MUlti-Level SImulatiONs).

Various tools...

"""

from   importlib                 import import_module
import yaml

import numpy                     as np

from   sortedcontainers          import SortedSet

def load_class(module=None, class_name=None, options={}):
    """Dynamically load the class with the specified name from the given
    module.

    """
    mod = import_module(module)
    return getattr(mod, class_name), options

def load_module(module):
    """Dynamically load the module with the specified name and return
    it.

    """
    return import_module(module)

def rates_to_probabilities(total_value, values, delta_t=1):
    """Transform the specified list of values (interpreted as rates)
    into probabilities, according to the specified time step
    (`delta_t`).

    """
    base_proba = 1 - np.exp(- total_value * delta_t)
    # 2) normalize values proportionnally to the rate
    values = [base_proba * rate / total_value
              for rate in values]
    # 3) add the probability to stay in the current state
    values.append(1 - base_proba)
    return values

def aggregate_probabilities(values, delta_t):
    """From the specified probability values, intended to represent a
    probability per time unit, compute the probabilities for the
    specified time step.

    """
    return values if delta_t == 1 else tuple(1 - (1-p)**delta_t for p in values)

def probabilities_to_rates(values):
    """Transform a list of probabilities into a list of rates. The
    last value is expected to represent the probability of staying in
    the current state.

    """
    if values[-1] == 1:
        return [0] * (len(values) - 1)
    sum_of_rates = - np.log(values[-1])
    proba_change = 1 - values[-1]
    values = [v * sum_of_rates / proba_change for v in values]
    return values[:-1]


def count_population(agents_or_pop_dict):
    """Return the amount of atoms represented in the dictionary. This
    dictionary can contain a `population` key associated with a
    number, or a `agents` key associated with instances of agents.

    """
    return agents_or_pop_dict['population']\
      if 'population' in agents_or_pop_dict\
      else len(agents_or_pop_dict['agents'])


def select_random(origin, quantity, exclude=SortedSet()):
    """Return a random selection of ``quantity`` units from the
    origin group.

    """
    content = [unit for unit in origin if unit not in exclude]
    size = len(content)
    np.random.shuffle(content)
    return content[:min(quantity, size)]


def read_from_file(filename):
    """Read the specified YAML filename and return the corresponding
    python document.

    """
    with open(filename, 'r') as fil:
        description = yaml.load(fil)
    return description


def retrieve_value(value_or_function, agent):
    """Return a value either directly given by the specified parameter
    if it is a true value, or computed from this parameter seen as a
    function, with the specified agent as argument.
    """

    return value_or_function(agent)\
        if callable(value_or_function)\
        else value_or_function



def moving_average(values, window_size, mode='same'):
    """Compute a moving average of the specified values with respect to
    the window size on which the average is calculated.  The return
    moving average has the same size as the original values.  To avoid
    boundary effects, use `mode='valid'`, which produce a result of size
    `len(values) - window_size + 1`.
    """
    window = np.ones(int(window_size)) / float(window_size)
    return np.convolve(values, window, mode)

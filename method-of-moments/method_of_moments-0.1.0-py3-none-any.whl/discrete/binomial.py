"""
This module contains description of function for binomial distribution.

References
----------
https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binom.html

"""


from scipy.stats import binom


def get_binomial_distribution(
        successes: int,
        trials: int,
        success_probability: float,
) -> float:
    """
    Return probability of specified successes number
    in a sequence of specified number of independent experiments.

    Parameters
    ----------
    success_probability : float
        Probability of success in any experiment.
    successes : int
        Number of successes.
    trials : int
        Number of trials.

    Returns
    -------
    float
        Probability of specified successes number
        in a sequence of specified number of independent experiments.

    """
    return binom.pmf(
        k=successes,
        n=trials,
        p=success_probability,
    )

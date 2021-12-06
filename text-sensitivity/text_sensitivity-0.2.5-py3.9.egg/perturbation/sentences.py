"""Create sentence-level perturbations (`text_sensitivity.perturbation.base.Perturbation`)."""


from typing import Optional

from text_sensitivity.perturbation.base import OneToOnePerturbation


def to_upper() -> OneToOnePerturbation:
    return OneToOnePerturbation.from_function(str.upper, 'not_upper', 'upper')


def to_lower() -> OneToOnePerturbation:
    return OneToOnePerturbation.from_function(str.lower, 'not_lower', 'lower')


def repeat_k_times(k: int = 10, connector: Optional[str] = ' '):
    """Repeat a string k times."""
    if connector is None:
        connector = ''

    def repeat_k(string: str) -> str:
        return connector.join([string] * k)

    return OneToOnePerturbation.from_function(repeat_k, label_to='repeated')

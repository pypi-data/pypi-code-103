from typing import List, Tuple

import numpy as np
import scipy.stats as st


class CI(object):
    @property
    def value(self) -> float:
        return self.__value

    @property
    def ci(self) -> float:
        return self.__ci

    @property
    def p(self) -> float:
        return self.__p

    @property
    def alpha(self) -> float:
        return 1 - self.__p

    @property
    def min(self) -> float:
        return self.__value - self.__ci

    @property
    def max(self) -> float:
        return self.__value + self.__ci

    @property
    def interval(self) -> Tuple[float, float]:
        return self.__value - self.__ci, self.__value + self.__ci

    def __init__(self, value: float, ci, p: float = None) -> None:
        self.__value = value
        self.__ci = abs(ci)
        self.__p = p

    @staticmethod
    def confidence_score(values: List[float], alpha: float = 0.95) -> 'CI':
        """ Obtain the mean value and confidence interval for a list of measures for different metrics.

        :param values: A list of values.
        :param alpha: The alpha value of a coefficient interval in a value between 0 and 1.
        :return: A dictionary with the different metrics and a tuple with the mean value and the confidence interval.
        """
        interval = st.t.interval(alpha, len(values) - 1, loc=np.mean(values), scale=st.sem(values))
        return CI.from_interval(interval[0], interval[1], 1 - alpha)

    def is_significant(self, other: 'CI') -> bool:
        return self.value + self.ci < other.value - other.ci or self.value - self.ci > other.value + other.ci

    @staticmethod
    def from_interval(a: float, b: float, p: float = None) -> 'CI':
        return CI((b + a) / 2, (b - a) / 2, p)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f'{self.__value}±{self.__ci}'

    def __iter__(self):
        return iter((self.__value, self.__ci))

    def __eq__(self, other: 'CI') -> bool:
        return self.value == other.value

    def __ne__(self, other: 'CI') -> bool:
        return self.value != other.value

    def __gt__(self, other: 'CI') -> bool:
        return self.value > other.value

    def __lt__(self, other: 'CI') -> bool:
        return self.value < other.value

    def __ge__(self, other: 'CI') -> bool:
        return self.value > other.value

    def __le__(self, other: 'CI') -> bool:
        return self.value <= other.value

    def __bool__(self) -> bool:
        return bool(self.value) or bool(self.ci)

    def __float__(self) -> float:
        return self.value

    def __getitem__(self, item: int) -> float:
        return tuple(self)[item]

    def __cmp__(self, other: 'CI') -> float:
        return 0 if self.value == other.value else self.value - other.value

    def __hash__(self) -> int:
        return hash((self.value, self.ci))

    def __contains__(self, other: 'CI') -> bool:
        return other.min >= self.min and other.max <= self.max

    def __copy__(self) -> 'CI':
        return CI(self.value, self.ci, self.p)

    def __pow__(self, power, **kwargs) -> float:
        return None if self.p is None else self.p ** power

    def __complex__(self) -> complex:
        return complex(self.value, self.ci)

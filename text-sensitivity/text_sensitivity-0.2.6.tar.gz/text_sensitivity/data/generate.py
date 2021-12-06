"""Generate data from a pattern, e.g. `'{He|She} lives in {city}.'`"""

import itertools
from typing import List, Tuple

from instancelib.instances.text import MemoryTextInstance, TextInstanceProvider
from instancelib.labels.memory import MemoryLabelProvider
from text_explainability.utils import word_detokenizer, word_tokenizer

from text_sensitivity.data.random.entity import (RandomAddress, RandomCity,
                                                 RandomCountry,
                                                 RandomCryptoCurrency,
                                                 RandomCurrencySymbol,
                                                 RandomDay, RandomDayOfWeek,
                                                 RandomEmail, RandomFirstName,
                                                 RandomLastName,
                                                 RandomLicensePlate,
                                                 RandomMonth, RandomName,
                                                 RandomPhoneNumber,
                                                 RandomPriceTag, RandomYear)
from text_sensitivity.data.wordlist import WordList

DEFAULTS = {'address': RandomAddress,
            'city': RandomCity,
            'country': RandomCountry,
            'name': RandomName,
            'first_name': RandomFirstName,
            'last_name': RandomLastName,
            'email': RandomEmail,
            'phone_number': RandomPhoneNumber,
            'year': RandomYear,
            'month': RandomMonth,
            'day': RandomDay,
            'day_of_week': RandomDayOfWeek,
            'price_tag': RandomPriceTag,
            'currency_symbol': RandomCurrencySymbol,
            'crypto_currency': RandomCryptoCurrency,
            'license_plate': RandomLicensePlate}


def options_from_brackets(string: str,
                          n: int = 3,
                          seed: int = 0,
                          **kwargs):
    def from_pattern(token: str):
        if token.startswith('{') and token.endswith('}'):
            pattern = token[1:-1]
            if ':' not in pattern:
                pattern = ':' + pattern

            modifiers, pattern = pattern.split(':')
            modifiers = [str(token).strip().lower() for x in modifiers.split(',')]

            def modify(p):
                if 'upper' in modifiers:
                    return p.upper()
                elif 'lower' in modifiers:
                    return p.lower()
                elif 'sentence' in modifiers:
                    return p.sentence()
                elif 'title' in modifiers:
                    return p.title()
                return p.original()

            if '|' in pattern:
                pattern = pattern.split('|')
            elif pattern in kwargs:
                pattern = kwargs[pattern]
            elif pattern in DEFAULTS:
                pattern = DEFAULTS[pattern]
            else:
                raise ValueError(f'Unknown {pattern=}')

            if isinstance(pattern, list):
                return modify(WordList.from_list(pattern, seed=seed)).generate_list()
            return modify(pattern(seed=seed)).generate_list(n=n)
        else:
            return [token]

    return [from_pattern(s) for s in word_tokenizer(string, exclude_curly_brackets=True)]


def from_pattern(pattern: str,
                 n: int = 3,
                 seed: int = 0,
                 **kwargs) -> Tuple[TextInstanceProvider, MemoryLabelProvider]:
    """Generate data from a pattern.

    Examples:
        Generate a list ['This is his house', 'This was his house', 'This is his car', 'This was his car', ...]:

        >>> from_pattern('This {is|was} his {house|car|boat}')

        Generate a list ['His home town is Eindhoven.', 'Her home town is Eindhoven.', 
        'His home town is Meerssen.', ...]. By default uses `RandomCity()` to generate the city name.

        >>> from_pattern('{His|Her} home town is {city}.')

        Override the 'city' default with your own list ['Amsterdam', 'Rotterdam', 'Utrecht']:

        >>> from_pattern('{His|Her} home town is {city}.', city=['Amsterdam', 'Rotterdam', 'Utrecht'])

        Apply lower case to the first argument and uppercase to the last, getting 
        ['Vandaag, donderdag heeft Sanne COLIN gebeld!', ..., 'Vandaag, maandag heeft Nora SEPP gebeld!', ...] for
        five random elements of each:

        >>> from_pattern('Vandaag, {lower:day_of_week}, heeft {first_name} {upper:first_name} gebeld!', n=5)

    Args:
        pattern (str): String containing pattern.
        n (int, optional): Number of elements to generate for each element, when generator is random. Defaults to 3.
        seed (int, optional): Seed for reproducibility. Defaults to 0.

    Returns:
        Tuple[TextInstanceProvider, MemoryLabelProvider]: Generated instances and corresponding labels.
    """
    instances = list(map(list, itertools.product(*options_from_brackets(pattern, n=n, seed=seed, **kwargs))))
    ids = [i for i in range(len(instances))]

    instances = TextInstanceProvider([MemoryTextInstance(id, word_detokenizer(instance), None, tokenized=instance)
                                      for id, instance in zip(ids, instances)])

    # TODO: get labels from options_from_brackets
    labels = MemoryLabelProvider.from_tuples(list(zip(ids, [frozenset({'perturbed'})] * len(instances))))

    return instances, labels


def default_patterns() -> List[str]:
    return list(DEFAULTS.keys())

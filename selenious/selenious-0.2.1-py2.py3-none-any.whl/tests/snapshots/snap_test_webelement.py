# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots['test_all_find_el_are_wrapped 1'] = [
    GenericRepr('MockWebElement'),
    [
        GenericRepr('MockWebElement')
    ],
    GenericRepr('MockWebElement'),
    [
        GenericRepr('MockWebElement')
    ],
    GenericRepr('MockWebElement'),
    [
        GenericRepr('MockWebElement')
    ],
    GenericRepr('MockWebElement'),
    [
        GenericRepr('MockWebElement')
    ],
    GenericRepr('MockWebElement'),
    [
        GenericRepr('MockWebElement')
    ],
    GenericRepr('MockWebElement'),
    [
        GenericRepr('MockWebElement')
    ],
    GenericRepr('MockWebElement'),
    [
        GenericRepr('MockWebElement')
    ],
    GenericRepr('MockWebElement'),
    [
        GenericRepr('MockWebElement')
    ],
    GenericRepr('MockWebElement'),
    [
        GenericRepr('MockWebElement')
    ]
]

snapshots['test_all_find_el_are_wrapped 2'] = [
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': '__init__',
        'retval': 'self'
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'id',
            'value': 'ignored'
        },
        'name': 'find_element',
        'retval': GenericRepr('MockWebElement')
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'id',
            'value': 'ignored'
        },
        'name': 'find_elements',
        'retval': [
            GenericRepr('MockWebElement')
        ]
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'xpath',
            'value': 'ignored'
        },
        'name': 'find_element',
        'retval': GenericRepr('MockWebElement')
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'xpath',
            'value': 'ignored'
        },
        'name': 'find_elements',
        'retval': [
            GenericRepr('MockWebElement')
        ]
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'link text',
            'value': 'ignored'
        },
        'name': 'find_element',
        'retval': GenericRepr('MockWebElement')
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'link text',
            'value': 'ignored'
        },
        'name': 'find_elements',
        'retval': [
            GenericRepr('MockWebElement')
        ]
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'partial link text',
            'value': 'ignored'
        },
        'name': 'find_element',
        'retval': GenericRepr('MockWebElement')
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'partial link text',
            'value': 'ignored'
        },
        'name': 'find_elements',
        'retval': [
            GenericRepr('MockWebElement')
        ]
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'name',
            'value': 'ignored'
        },
        'name': 'find_element',
        'retval': GenericRepr('MockWebElement')
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'name',
            'value': 'ignored'
        },
        'name': 'find_elements',
        'retval': [
            GenericRepr('MockWebElement')
        ]
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'tag name',
            'value': 'ignored'
        },
        'name': 'find_element',
        'retval': GenericRepr('MockWebElement')
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'tag name',
            'value': 'ignored'
        },
        'name': 'find_elements',
        'retval': [
            GenericRepr('MockWebElement')
        ]
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'class name',
            'value': 'ignored'
        },
        'name': 'find_element',
        'retval': GenericRepr('MockWebElement')
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'class name',
            'value': 'ignored'
        },
        'name': 'find_elements',
        'retval': [
            GenericRepr('MockWebElement')
        ]
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'css selector',
            'value': 'ignored'
        },
        'name': 'find_element',
        'retval': GenericRepr('MockWebElement')
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'css selector',
            'value': 'ignored'
        },
        'name': 'find_elements',
        'retval': [
            GenericRepr('MockWebElement')
        ]
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'ignored',
            'value': 'twice'
        },
        'name': 'find_element',
        'retval': GenericRepr('MockWebElement')
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'ignored',
            'value': 'twice'
        },
        'name': 'find_elements',
        'retval': [
            GenericRepr('MockWebElement')
        ]
    }
]

snapshots['test_click_no_recover_excepts 1'] = [
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': '__init__',
        'retval': 'self'
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'click',
        'retval': GenericRepr("<class 'selenium.common.exceptions.NoSuchElementException'>")
    }
]

snapshots['test_click_recover_fails 1'] = [
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': '__init__',
        'retval': 'self'
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'click',
        'retval': GenericRepr("<class 'selenium.common.exceptions.NoSuchElementException'>")
    },
    {
        'args': (
            GenericRepr('<selenious.recover.RecoverData object at 0x100000000>')
        ,),
        'kwargs': {
        },
        'name': 'recover',
        'retval': None
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'click',
        'retval': GenericRepr("<class 'selenium.common.exceptions.NoSuchElementException'>")
    }
]

snapshots['test_click_recover_succeeds 1'] = [
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': '__init__',
        'retval': 'self'
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'click',
        'retval': GenericRepr("<class 'selenium.common.exceptions.NoSuchElementException'>")
    },
    {
        'args': (
            GenericRepr('<selenious.recover.RecoverData object at 0x100000000>')
        ,),
        'kwargs': {
        },
        'name': 'recover',
        'retval': None
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'click',
        'retval': None
    }
]

snapshots['test_find_element_decorator_raise 1'] = [
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': '__init__',
        'retval': 'self'
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'monotonic',
        'retval': 0
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'id',
            'value': '_'
        },
        'name': 'find_element',
        'retval': GenericRepr("<class 'selenium.common.exceptions.NoSuchElementException'>")
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'monotonic',
        'retval': 99
    },
    {
        'args': (
        ),
        'kwargs': {
            'poll_frequency': 0.5,
            'prev_state': None,
            'time_left': -99
        },
        'name': 'mock_next_state',
        'retval': (
            'raise',
            GenericRepr('MockWebElement')
        )
    }
]

snapshots['test_find_element_decorator_recover_or_raise_nonnull 1'] = [
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': '__init__',
        'retval': 'self'
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'monotonic',
        'retval': 0
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'id',
            'value': '_'
        },
        'name': 'find_element',
        'retval': GenericRepr("<class 'selenium.common.exceptions.NoSuchElementException'>")
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'monotonic',
        'retval': 99
    },
    {
        'args': (
        ),
        'kwargs': {
            'poll_frequency': 0.5,
            'prev_state': None,
            'time_left': 101
        },
        'name': 'mock_next_state',
        'retval': (
            'recover_or_raise',
            GenericRepr('MockWebElement')
        )
    },
    {
        'args': (
            GenericRepr('MockWebElement')
        ,),
        'kwargs': {
        },
        'name': 'mock_sleep',
        'retval': None
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'id',
            'value': '_'
        },
        'name': 'find_element',
        'retval': GenericRepr('MockWebElement')
    }
]

snapshots['test_find_element_decorator_recover_or_raise_null 1'] = [
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': '__init__',
        'retval': 'self'
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'monotonic',
        'retval': 0
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'id',
            'value': '_'
        },
        'name': 'find_element',
        'retval': GenericRepr("<class 'selenium.common.exceptions.NoSuchElementException'>")
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'monotonic',
        'retval': 99
    },
    {
        'args': (
        ),
        'kwargs': {
            'poll_frequency': 0.5,
            'prev_state': None,
            'time_left': 101
        },
        'name': 'mock_next_state',
        'retval': (
            'recover_or_raise',
            GenericRepr('MockWebElement')
        )
    }
]

snapshots['test_find_elements_decorator_debounce 1'] = [
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': '__init__',
        'retval': 'self'
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'monotonic',
        'retval': 0
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'id',
            'value': '_'
        },
        'name': 'find_elements',
        'retval': [
        ]
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'monotonic',
        'retval': 1
    },
    {
        'args': (
        ),
        'kwargs': {
            'debounce': 0.1,
            'ismin': False,
            'poll_frequency': 0.5,
            'prev_state': None,
            'stable_time': 1,
            'time_left': 199
        },
        'name': 'mock_next_state',
        'retval': (
            'debounce',
            GenericRepr('MockWebElement')
        )
    },
    {
        'args': (
            GenericRepr('MockWebElement')
        ,),
        'kwargs': {
        },
        'name': 'mock_sleep',
        'retval': None
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'id',
            'value': '_'
        },
        'name': 'find_elements',
        'retval': [
            GenericRepr('MockWebElement'),
            GenericRepr('MockWebElement'),
            GenericRepr('MockWebElement')
        ]
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'monotonic',
        'retval': 99
    },
    {
        'args': (
        ),
        'kwargs': {
            'debounce': 0.1,
            'ismin': True,
            'poll_frequency': 0.5,
            'prev_state': 'debounce',
            'stable_time': 0,
            'time_left': 101
        },
        'name': 'mock_next_state',
        'retval': (
            'success',
            GenericRepr('MockWebElement')
        )
    }
]

snapshots['test_find_elements_decorator_raise 1'] = [
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': '__init__',
        'retval': 'self'
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'monotonic',
        'retval': 0
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'id',
            'value': '_'
        },
        'name': 'find_elements',
        'retval': [
        ]
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'monotonic',
        'retval': 1
    },
    {
        'args': (
        ),
        'kwargs': {
            'debounce': 0.1,
            'ismin': False,
            'poll_frequency': 0.5,
            'prev_state': None,
            'stable_time': 1,
            'time_left': 199
        },
        'name': 'mock_next_state',
        'retval': (
            'raise',
            GenericRepr('MockWebElement')
        )
    }
]

snapshots['test_find_elements_decorator_recover_and_retry_no_recover 1'] = [
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': '__init__',
        'retval': 'self'
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'monotonic',
        'retval': 0
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'id',
            'value': '_'
        },
        'name': 'find_elements',
        'retval': [
        ]
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'monotonic',
        'retval': 1
    },
    {
        'args': (
        ),
        'kwargs': {
            'debounce': 0.1,
            'ismin': False,
            'poll_frequency': 0.5,
            'prev_state': None,
            'stable_time': 1,
            'time_left': 199
        },
        'name': 'mock_next_state',
        'retval': (
            'recover_and_retry',
            GenericRepr('MockWebElement')
        )
    },
    {
        'args': (
            GenericRepr('MockWebElement')
        ,),
        'kwargs': {
        },
        'name': 'mock_sleep',
        'retval': None
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'id',
            'value': '_'
        },
        'name': 'find_elements',
        'retval': [
            GenericRepr('MockWebElement'),
            GenericRepr('MockWebElement'),
            GenericRepr('MockWebElement')
        ]
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'monotonic',
        'retval': 99
    },
    {
        'args': (
        ),
        'kwargs': {
            'debounce': 0.1,
            'ismin': True,
            'poll_frequency': 0.5,
            'prev_state': 'recover_and_retry',
            'stable_time': 0,
            'time_left': 101
        },
        'name': 'mock_next_state',
        'retval': (
            'success',
            GenericRepr('MockWebElement')
        )
    }
]

snapshots['test_find_elements_decorator_recover_and_retry_recover 1'] = [
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': '__init__',
        'retval': 'self'
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'monotonic',
        'retval': 0
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'id',
            'value': '_'
        },
        'name': 'find_elements',
        'retval': [
        ]
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'monotonic',
        'retval': 1
    },
    {
        'args': (
        ),
        'kwargs': {
            'debounce': 0.1,
            'ismin': False,
            'poll_frequency': 0.5,
            'prev_state': None,
            'stable_time': 1,
            'time_left': 199
        },
        'name': 'mock_next_state',
        'retval': (
            'recover_and_retry',
            GenericRepr('MockWebElement')
        )
    },
    {
        'args': (
            GenericRepr('MockWebElement')
        ,),
        'kwargs': {
        },
        'name': 'mock_sleep',
        'retval': None
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'id',
            'value': '_'
        },
        'name': 'find_elements',
        'retval': [
            GenericRepr('MockWebElement'),
            GenericRepr('MockWebElement'),
            GenericRepr('MockWebElement')
        ]
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'monotonic',
        'retval': 99
    },
    {
        'args': (
        ),
        'kwargs': {
            'debounce': 0.1,
            'ismin': True,
            'poll_frequency': 0.5,
            'prev_state': 'recover_and_retry',
            'stable_time': 0,
            'time_left': 101
        },
        'name': 'mock_next_state',
        'retval': (
            'success',
            GenericRepr('MockWebElement')
        )
    }
]

snapshots['test_find_elements_decorator_recover_or_raise_no_recover 1'] = [
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': '__init__',
        'retval': 'self'
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'monotonic',
        'retval': 0
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'id',
            'value': '_'
        },
        'name': 'find_elements',
        'retval': [
        ]
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'monotonic',
        'retval': 1
    },
    {
        'args': (
        ),
        'kwargs': {
            'debounce': 0.1,
            'ismin': False,
            'poll_frequency': 0.5,
            'prev_state': None,
            'stable_time': 1,
            'time_left': 199
        },
        'name': 'mock_next_state',
        'retval': (
            'recover_or_raise',
            GenericRepr('MockWebElement')
        )
    }
]

snapshots['test_find_elements_decorator_recover_or_raise_recover 1'] = [
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': '__init__',
        'retval': 'self'
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'monotonic',
        'retval': 0
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'id',
            'value': '_'
        },
        'name': 'find_elements',
        'retval': [
        ]
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'monotonic',
        'retval': 1
    },
    {
        'args': (
        ),
        'kwargs': {
            'debounce': 0.1,
            'ismin': False,
            'poll_frequency': 0.5,
            'prev_state': None,
            'stable_time': 1,
            'time_left': 199
        },
        'name': 'mock_next_state',
        'retval': (
            'recover_or_raise',
            GenericRepr('MockWebElement')
        )
    },
    {
        'args': (
            GenericRepr('MockWebElement')
        ,),
        'kwargs': {
        },
        'name': 'mock_sleep',
        'retval': None
    },
    {
        'args': (
        ),
        'kwargs': {
            'by': 'id',
            'value': '_'
        },
        'name': 'find_elements',
        'retval': [
            GenericRepr('MockWebElement'),
            GenericRepr('MockWebElement'),
            GenericRepr('MockWebElement')
        ]
    },
    {
        'args': (
        ),
        'kwargs': {
        },
        'name': 'monotonic',
        'retval': 99
    },
    {
        'args': (
        ),
        'kwargs': {
            'debounce': 0.1,
            'ismin': True,
            'poll_frequency': 0.5,
            'prev_state': 'recover_or_raise',
            'stable_time': 0,
            'time_left': 101
        },
        'name': 'mock_next_state',
        'retval': (
            'success',
            GenericRepr('MockWebElement')
        )
    }
]

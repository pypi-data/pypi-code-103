EXPECTED = {'Parameterization': {'extensibility-implied': False,
                      'imports': {'Parameterization2': ['B2',
                                                        'D2',
                                                        'E2',
                                                        'F2']},
                      'object-classes': {},
                      'object-sets': {},
                      'tags': 'AUTOMATIC',
                      'types': {'A': {'members': [{'name': 'a', 'type': 'B'}],
                                      'parameters': ['B'],
                                      'type': 'SEQUENCE'},
                                'A-Boolean': {'actual-parameters': [{'type': 'BOOLEAN'}],
                                              'type': 'A'},
                                'A-Integer': {'actual-parameters': [{'type': 'INTEGER'}],
                                              'type': 'A'},
                                'A2': {'type': 'BOOLEAN'},
                                'B': {'members': [{'name': 'a', 'type': 'A'},
                                                  {'name': 'b',
                                                   'optional': True,
                                                   'type': 'B'}],
                                      'parameters': ['A', 'B'],
                                      'type': 'SEQUENCE'},
                                'B-BooleanInteger': {'actual-parameters': [{'type': 'BOOLEAN'},
                                                                           {'type': 'INTEGER'}],
                                                     'type': 'B'},
                                'C': {'members': [{'name': 'a', 'type': 'A'},
                                                  {'actual-parameters': [{'type': 'A'},
                                                                         {'type': 'INTEGER'}],
                                                   'name': 'b',
                                                   'type': 'B'}],
                                      'parameters': ['A'],
                                      'type': 'CHOICE'},
                                'D': {'members': [{'actual-parameters': [{'type': 'B-BooleanInteger'}],
                                                   'name': 'a',
                                                   'type': 'C'},
                                                  {'members': [{'actual-parameters': [{'actual-parameters': [{'type': 'NULL'},
                                                                                                             {'type': 'INTEGER'}],
                                                                                       'type': 'B'}],
                                                                'name': 'c',
                                                                'type': 'A'},
                                                               {'actual-parameters': [{'type': 'NULL'},
                                                                                      {'type': 'INTEGER'}],
                                                                'name': 'd',
                                                                'type': 'B'}],
                                                   'name': 'b',
                                                   'type': 'CHOICE'}],
                                      'type': 'SEQUENCE'},
                                'E': {'element': {'members': [{'name': 'a',
                                                               'type': 'A'},
                                                              {'members': [{'element': {'actual-parameters': [{'type': 'A'},
                                                                                                              {'type': 'BOOLEAN'}],
                                                                                        'type': 'B'},
                                                                            'name': 'c',
                                                                            'type': 'SEQUENCE '
                                                                                    'OF'}],
                                                               'name': 'b',
                                                               'type': 'SEQUENCE'}],
                                                  'type': 'CHOICE'},
                                      'parameters': ['A'],
                                      'size': [(0, 5)],
                                      'type': 'SEQUENCE OF'},
                                'F': {'actual-parameters': [{'type': 'INTEGER'}],
                                      'type': 'E'},
                                'G': {'element': {'type': 'BOOLEAN'},
                                      'parameters': ['a'],
                                      'size': [(0, 'a')],
                                      'type': 'SEQUENCE OF'},
                                'H': {'actual-parameters': [5], 'type': 'G'},
                                'I': {'actual-parameters': ['i'], 'type': 'G'},
                                'J': {'element': {'type': 'BOOLEAN'},
                                      'parameters': ['b'],
                                      'size': ['b'],
                                      'type': 'SEQUENCE OF'},
                                'K': {'actual-parameters': [3], 'type': 'J'},
                                'L': {'parameters': ['a', 'b'],
                                      'restricted-to': [('a', 'b')],
                                      'type': 'INTEGER'},
                                'M': {'actual-parameters': [3, 9], 'type': 'L'},
                                'N': {'parameters': ['a', 'B'],
                                      'restricted-to': [(-5, 'a')],
                                      'type': 'B'},
                                'O': {'actual-parameters': [-2,
                                                            {'type': 'INTEGER'}],
                                      'type': 'N'},
                                'P': {'members': [{'name': 'a', 'type': 'A'}],
                                      'parameters': ['A'],
                                      'type': 'SEQUENCE'},
                                'Q': {'actual-parameters': [{'type': 'A'}],
                                      'parameters': ['A'],
                                      'type': 'P'},
                                'R': {'actual-parameters': [{'type': 'INTEGER'}],
                                      'type': 'Q'},
                                'S': {'actual-parameters': [{'type': 'BOOLEAN'}],
                                      'type': 'B2'},
                                'T': {'actual-parameters': [{'type': 'OCTET '
                                                                     'STRING'}],
                                      'type': 'D2'},
                                'U': {'actual-parameters': [{'type': 'INTEGER'}],
                                      'type': 'E2'},
                                'V': {'actual-parameters': [{'type': 'INTEGER'}],
                                      'type': 'F2'}},
                      'values': {'i': {'type': 'INTEGER', 'value': 1}}},
 'Parameterization2': {'extensibility-implied': False,
                       'imports': {'Parameterization3': ['B3', 'D3']},
                       'object-classes': {},
                       'object-sets': {},
                       'tags': 'AUTOMATIC',
                       'types': {'A2': {'type': 'INTEGER'},
                                 'B2': {'members': [{'name': 'a', 'type': 'A'},
                                                    {'name': 'b',
                                                     'type': 'A2'}],
                                        'parameters': ['A'],
                                        'type': 'SEQUENCE'},
                                 'C2': {'type': 'INTEGER'},
                                 'D2': {'members': [{'name': 'a', 'type': 'A'},
                                                    {'name': 'b',
                                                     'type': 'C2'}],
                                        'parameters': ['A'],
                                        'type': 'SEQUENCE'},
                                 'E2': {'members': [{'name': 'a', 'type': 'A'},
                                                    {'actual-parameters': [{'type': 'A'}],
                                                     'name': 'b',
                                                     'type': 'B3'}],
                                        'parameters': ['A'],
                                        'type': 'SEQUENCE'},
                                 'F2': {'actual-parameters': [{'type': 'A'}],
                                        'parameters': ['A'],
                                        'type': 'D3'}},
                       'values': {}},
 'Parameterization3': {'extensibility-implied': False,
                       'imports': {},
                       'object-classes': {},
                       'object-sets': {},
                       'tags': 'AUTOMATIC',
                       'types': {'A3': {'type': 'INTEGER'},
                                 'B3': {'members': [{'name': 'a', 'type': 'A'},
                                                    {'name': 'b',
                                                     'type': 'A3'}],
                                        'parameters': ['A'],
                                        'type': 'SEQUENCE'},
                                 'C3': {'type': 'OCTET STRING'},
                                 'D3': {'parameters': ['A'], 'type': 'C3'}},
                       'values': {}}}
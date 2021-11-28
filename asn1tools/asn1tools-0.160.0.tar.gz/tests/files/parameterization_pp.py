EXPECTED = {'Parameterization': {'extensibility-implied': False,
                      'imports': {'Parameterization2': ['B2',
                                                        'D2',
                                                        'E2',
                                                        'F2']},
                      'object-classes': {},
                      'object-sets': {},
                      'tags': 'AUTOMATIC',
                      'types': {'A-Boolean': {'members': [{'name': 'a',
                                                           'tag': {'kind': 'EXPLICIT',
                                                                   'number': 0},
                                                           'type': 'BOOLEAN'}],
                                              'type': 'SEQUENCE'},
                                'A-Integer': {'members': [{'name': 'a',
                                                           'tag': {'kind': 'EXPLICIT',
                                                                   'number': 0},
                                                           'type': 'INTEGER'}],
                                              'type': 'SEQUENCE'},
                                'A2': {'type': 'BOOLEAN'},
                                'B-BooleanInteger': {'members': [{'name': 'a',
                                                                  'tag': {'kind': 'EXPLICIT',
                                                                          'number': 0},
                                                                  'type': 'BOOLEAN'},
                                                                 {'name': 'b',
                                                                  'optional': True,
                                                                  'tag': {'kind': 'EXPLICIT',
                                                                          'number': 1},
                                                                  'type': 'INTEGER'}],
                                                     'type': 'SEQUENCE'},
                                'D': {'members': [{'members': [{'name': 'a',
                                                                'tag': {'kind': 'EXPLICIT',
                                                                        'number': 0},
                                                                'type': 'B-BooleanInteger'},
                                                               {'members': [{'name': 'a',
                                                                             'tag': {'kind': 'EXPLICIT',
                                                                                     'number': 0},
                                                                             'type': 'B-BooleanInteger'},
                                                                            {'name': 'b',
                                                                             'optional': True,
                                                                             'tag': {'kind': 'EXPLICIT',
                                                                                     'number': 1},
                                                                             'type': 'INTEGER'}],
                                                                'name': 'b',
                                                                'tag': {'kind': 'IMPLICIT',
                                                                        'number': 1},
                                                                'type': 'SEQUENCE'}],
                                                   'name': 'a',
                                                   'tag': {'kind': 'EXPLICIT',
                                                           'number': 0},
                                                   'type': 'CHOICE'},
                                                  {'members': [{'members': [{'members': [{'name': 'a',
                                                                                          'tag': {'kind': 'EXPLICIT',
                                                                                                  'number': 0},
                                                                                          'type': 'NULL'},
                                                                                         {'name': 'b',
                                                                                          'optional': True,
                                                                                          'tag': {'kind': 'EXPLICIT',
                                                                                                  'number': 1},
                                                                                          'type': 'INTEGER'}],
                                                                             'name': 'a',
                                                                             'tag': {'kind': 'EXPLICIT',
                                                                                     'number': 0},
                                                                             'type': 'SEQUENCE'}],
                                                                'name': 'c',
                                                                'tag': {'kind': 'IMPLICIT',
                                                                        'number': 0},
                                                                'type': 'SEQUENCE'},
                                                               {'members': [{'name': 'a',
                                                                             'tag': {'kind': 'EXPLICIT',
                                                                                     'number': 0},
                                                                             'type': 'NULL'},
                                                                            {'name': 'b',
                                                                             'optional': True,
                                                                             'tag': {'kind': 'EXPLICIT',
                                                                                     'number': 1},
                                                                             'type': 'INTEGER'}],
                                                                'name': 'd',
                                                                'tag': {'kind': 'IMPLICIT',
                                                                        'number': 1},
                                                                'type': 'SEQUENCE'}],
                                                   'name': 'b',
                                                   'tag': {'kind': 'EXPLICIT',
                                                           'number': 1},
                                                   'type': 'CHOICE'}],
                                      'type': 'SEQUENCE'},
                                'F': {'element': {'members': [{'name': 'a',
                                                               'tag': {'kind': 'EXPLICIT',
                                                                       'number': 0},
                                                               'type': 'INTEGER'},
                                                              {'members': [{'element': {'members': [{'name': 'a',
                                                                                                     'tag': {'kind': 'EXPLICIT',
                                                                                                             'number': 0},
                                                                                                     'type': 'INTEGER'},
                                                                                                    {'name': 'b',
                                                                                                     'optional': True,
                                                                                                     'tag': {'kind': 'EXPLICIT',
                                                                                                             'number': 1},
                                                                                                     'type': 'BOOLEAN'}],
                                                                                        'type': 'SEQUENCE'},
                                                                            'name': 'c',
                                                                            'tag': {'kind': 'IMPLICIT',
                                                                                    'number': 0},
                                                                            'type': 'SEQUENCE '
                                                                                    'OF'}],
                                                               'name': 'b',
                                                               'tag': {'kind': 'IMPLICIT',
                                                                       'number': 1},
                                                               'type': 'SEQUENCE'}],
                                                  'type': 'CHOICE'},
                                      'size': [(0, 5)],
                                      'type': 'SEQUENCE OF'},
                                'H': {'element': {'type': 'BOOLEAN'},
                                      'size': [(0, 5)],
                                      'type': 'SEQUENCE OF'},
                                'I': {'element': {'type': 'BOOLEAN'},
                                      'size': [(0, 'i')],
                                      'type': 'SEQUENCE OF'},
                                'K': {'element': {'type': 'BOOLEAN'},
                                      'size': [3],
                                      'type': 'SEQUENCE OF'},
                                'M': {'restricted-to': [(3, 9)],
                                      'type': 'INTEGER'},
                                'O': {'restricted-to': [(-5, -2)],
                                      'type': 'INTEGER'},
                                'R': {'members': [{'name': 'a',
                                                   'tag': {'kind': 'EXPLICIT',
                                                           'number': 0},
                                                   'type': 'INTEGER'}],
                                      'type': 'SEQUENCE'},
                                'S': {'members': [{'name': 'a',
                                                   'tag': {'kind': 'EXPLICIT',
                                                           'number': 0},
                                                   'type': 'BOOLEAN'},
                                                  {'name': 'b',
                                                   'tag': {'kind': 'IMPLICIT',
                                                           'number': 1},
                                                   'type': 'A2'}],
                                      'module-name': 'Parameterization2',
                                      'type': 'SEQUENCE'},
                                'T': {'members': [{'name': 'a',
                                                   'tag': {'kind': 'EXPLICIT',
                                                           'number': 0},
                                                   'type': 'OCTET STRING'},
                                                  {'name': 'b',
                                                   'tag': {'kind': 'IMPLICIT',
                                                           'number': 1},
                                                   'type': 'C2'}],
                                      'module-name': 'Parameterization2',
                                      'type': 'SEQUENCE'},
                                'U': {'members': [{'name': 'a',
                                                   'tag': {'kind': 'EXPLICIT',
                                                           'number': 0},
                                                   'type': 'INTEGER'},
                                                  {'members': [{'name': 'a',
                                                                'tag': {'kind': 'EXPLICIT',
                                                                        'number': 0},
                                                                'type': 'INTEGER'},
                                                               {'name': 'b',
                                                                'tag': {'kind': 'IMPLICIT',
                                                                        'number': 1},
                                                                'type': 'A3'}],
                                                   'module-name': 'Parameterization3',
                                                   'name': 'b',
                                                   'tag': {'kind': 'IMPLICIT',
                                                           'number': 1},
                                                   'type': 'SEQUENCE'}],
                                      'module-name': 'Parameterization2',
                                      'type': 'SEQUENCE'},
                                'V': {'module-name': 'Parameterization3',
                                      'type': 'C3'}},
                      'values': {'i': {'type': 'INTEGER', 'value': 1}}},
 'Parameterization2': {'extensibility-implied': False,
                       'imports': {'Parameterization3': ['B3', 'D3']},
                       'object-classes': {},
                       'object-sets': {},
                       'tags': 'AUTOMATIC',
                       'types': {'A2': {'type': 'INTEGER'},
                                 'C2': {'type': 'INTEGER'}},
                       'values': {}},
 'Parameterization3': {'extensibility-implied': False,
                       'imports': {},
                       'object-classes': {},
                       'object-sets': {},
                       'tags': 'AUTOMATIC',
                       'types': {'A3': {'type': 'INTEGER'},
                                 'C3': {'type': 'OCTET STRING'}},
                       'values': {}}}

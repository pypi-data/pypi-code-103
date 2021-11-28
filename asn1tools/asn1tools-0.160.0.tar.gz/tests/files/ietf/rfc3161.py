EXPECTED = {'PKIXTSP': {'extensibility-implied': False,
             'imports': {'CryptographicMessageSyntax': ['ContentInfo'],
                         'PKIX1Explicit88': ['AlgorithmIdentifier',
                                             'Extensions'],
                         'PKIX1Implicit88': ['GeneralName'],
                         'PKIXCMP': ['PKIFreeText']},
             'object-classes': {},
             'object-sets': {},
             'tags': 'IMPLICIT',
             'types': {'Accuracy': {'members': [{'name': 'seconds',
                                                 'optional': True,
                                                 'type': 'INTEGER'},
                                                {'name': 'millis',
                                                 'optional': True,
                                                 'restricted-to': [(1, 999)],
                                                 'tag': {'number': 0},
                                                 'type': 'INTEGER'},
                                                {'name': 'micros',
                                                 'optional': True,
                                                 'restricted-to': [(1, 999)],
                                                 'tag': {'number': 1},
                                                 'type': 'INTEGER'}],
                                    'type': 'SEQUENCE'},
                       'MessageImprint': {'members': [{'name': 'hashAlgorithm',
                                                       'type': 'AlgorithmIdentifier'},
                                                      {'name': 'hashedMessage',
                                                       'type': 'OCTET STRING'}],
                                          'type': 'SEQUENCE'},
                       'PKIFailureInfo': {'named-bits': [('badAlg', '0'),
                                                         ('badRequest', '2'),
                                                         ('badDataFormat', '5'),
                                                         ('timeNotAvailable',
                                                          '14'),
                                                         ('unacceptedPolicy',
                                                          '15'),
                                                         ('unacceptedExtension',
                                                          '16'),
                                                         ('addInfoNotAvailable',
                                                          '17'),
                                                         ('systemFailure',
                                                          '25')],
                                          'type': 'BIT STRING'},
                       'PKIStatus': {'named-numbers': {'granted': 0,
                                                       'grantedWithMods': 1,
                                                       'rejection': 2,
                                                       'revocationNotification': 5,
                                                       'revocationWarning': 4,
                                                       'waiting': 3},
                                     'type': 'INTEGER'},
                       'PKIStatusInfo': {'members': [{'name': 'status',
                                                      'type': 'PKIStatus'},
                                                     {'name': 'statusString',
                                                      'optional': True,
                                                      'type': 'PKIFreeText'},
                                                     {'name': 'failInfo',
                                                      'optional': True,
                                                      'type': 'PKIFailureInfo'}],
                                         'type': 'SEQUENCE'},
                       'TSAPolicyId': {'type': 'OBJECT IDENTIFIER'},
                       'TSTInfo': {'members': [{'name': 'version',
                                                'named-numbers': {'v1': 1},
                                                'type': 'INTEGER'},
                                               {'name': 'policy',
                                                'type': 'TSAPolicyId'},
                                               {'name': 'messageImprint',
                                                'type': 'MessageImprint'},
                                               {'name': 'serialNumber',
                                                'type': 'INTEGER'},
                                               {'name': 'genTime',
                                                'type': 'GeneralizedTime'},
                                               {'name': 'accuracy',
                                                'optional': True,
                                                'type': 'Accuracy'},
                                               {'default': False,
                                                'name': 'ordering',
                                                'type': 'BOOLEAN'},
                                               {'name': 'nonce',
                                                'optional': True,
                                                'type': 'INTEGER'},
                                               {'name': 'tsa',
                                                'optional': True,
                                                'tag': {'number': 0},
                                                'type': 'GeneralName'},
                                               {'name': 'extensions',
                                                'optional': True,
                                                'tag': {'kind': 'IMPLICIT',
                                                        'number': 1},
                                                'type': 'Extensions'}],
                                   'type': 'SEQUENCE'},
                       'TimeStampReq': {'members': [{'name': 'version',
                                                     'named-numbers': {'v1': 1},
                                                     'type': 'INTEGER'},
                                                    {'name': 'messageImprint',
                                                     'type': 'MessageImprint'},
                                                    {'name': 'reqPolicy',
                                                     'optional': True,
                                                     'type': 'TSAPolicyId'},
                                                    {'name': 'nonce',
                                                     'optional': True,
                                                     'type': 'INTEGER'},
                                                    {'default': False,
                                                     'name': 'certReq',
                                                     'type': 'BOOLEAN'},
                                                    {'name': 'extensions',
                                                     'optional': True,
                                                     'tag': {'kind': 'IMPLICIT',
                                                             'number': 0},
                                                     'type': 'Extensions'}],
                                        'type': 'SEQUENCE'},
                       'TimeStampResp': {'members': [{'name': 'status',
                                                      'type': 'PKIStatusInfo'},
                                                     {'name': 'timeStampToken',
                                                      'optional': True,
                                                      'type': 'TimeStampToken'}],
                                         'type': 'SEQUENCE'},
                       'TimeStampToken': {'type': 'ContentInfo'}},
             'values': {'id-ct-TSTInfo': {'type': 'OBJECT IDENTIFIER',
                                          'value': [('iso', 1),
                                                    ('member-body', 2),
                                                    ('us', 840),
                                                    ('rsadsi', 113549),
                                                    ('pkcs', 1),
                                                    ('pkcs-9', 9),
                                                    ('smime', 16),
                                                    ('ct', 1),
                                                    4]}}}}
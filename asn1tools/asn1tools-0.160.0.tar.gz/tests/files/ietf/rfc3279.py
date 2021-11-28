EXPECTED = {'PKIX1Algorithms88': {'extensibility-implied': False,
                       'imports': {},
                       'object-classes': {},
                       'object-sets': {},
                       'tags': 'EXPLICIT',
                       'types': {'Characteristic-two': {'members': [{'name': 'm',
                                                                     'type': 'INTEGER'},
                                                                    {'name': 'basis',
                                                                     'type': 'OBJECT '
                                                                             'IDENTIFIER'},
                                                                    {'choices': {},
                                                                     'name': 'parameters',
                                                                     'type': 'ANY '
                                                                             'DEFINED '
                                                                             'BY',
                                                                     'value': 'basis'}],
                                                        'type': 'SEQUENCE'},
                                 'Curve': {'members': [{'name': 'a',
                                                        'type': 'FieldElement'},
                                                       {'name': 'b',
                                                        'type': 'FieldElement'},
                                                       {'name': 'seed',
                                                        'optional': True,
                                                        'type': 'BIT STRING'}],
                                           'type': 'SEQUENCE'},
                                 'DHPublicKey': {'type': 'INTEGER'},
                                 'DSAPublicKey': {'type': 'INTEGER'},
                                 'DomainParameters': {'members': [{'name': 'p',
                                                                   'type': 'INTEGER'},
                                                                  {'name': 'g',
                                                                   'type': 'INTEGER'},
                                                                  {'name': 'q',
                                                                   'type': 'INTEGER'},
                                                                  {'name': 'j',
                                                                   'optional': True,
                                                                   'type': 'INTEGER'},
                                                                  {'name': 'validationParms',
                                                                   'optional': True,
                                                                   'type': 'ValidationParms'}],
                                                      'type': 'SEQUENCE'},
                                 'Dss-Parms': {'members': [{'name': 'p',
                                                            'type': 'INTEGER'},
                                                           {'name': 'q',
                                                            'type': 'INTEGER'},
                                                           {'name': 'g',
                                                            'type': 'INTEGER'}],
                                               'type': 'SEQUENCE'},
                                 'Dss-Sig-Value': {'members': [{'name': 'r',
                                                                'type': 'INTEGER'},
                                                               {'name': 's',
                                                                'type': 'INTEGER'}],
                                                   'type': 'SEQUENCE'},
                                 'ECDSA-Sig-Value': {'members': [{'name': 'r',
                                                                  'type': 'INTEGER'},
                                                                 {'name': 's',
                                                                  'type': 'INTEGER'}],
                                                     'type': 'SEQUENCE'},
                                 'ECPVer': {'named-numbers': {'ecpVer1': 1},
                                            'type': 'INTEGER'},
                                 'ECParameters': {'members': [{'name': 'version',
                                                               'type': 'ECPVer'},
                                                              {'name': 'fieldID',
                                                               'type': 'FieldID'},
                                                              {'name': 'curve',
                                                               'type': 'Curve'},
                                                              {'name': 'base',
                                                               'type': 'ECPoint'},
                                                              {'name': 'order',
                                                               'type': 'INTEGER'},
                                                              {'name': 'cofactor',
                                                               'optional': True,
                                                               'type': 'INTEGER'}],
                                                  'type': 'SEQUENCE'},
                                 'ECPoint': {'type': 'OCTET STRING'},
                                 'EcpkParameters': {'members': [{'name': 'ecParameters',
                                                                 'type': 'ECParameters'},
                                                                {'name': 'namedCurve',
                                                                 'type': 'OBJECT '
                                                                         'IDENTIFIER'},
                                                                {'name': 'implicitlyCA',
                                                                 'type': 'NULL'}],
                                                    'type': 'CHOICE'},
                                 'FieldElement': {'type': 'OCTET STRING'},
                                 'FieldID': {'members': [{'name': 'fieldType',
                                                          'type': 'OBJECT '
                                                                  'IDENTIFIER'},
                                                         {'choices': {},
                                                          'name': 'parameters',
                                                          'type': 'ANY DEFINED '
                                                                  'BY',
                                                          'value': 'fieldType'}],
                                             'type': 'SEQUENCE'},
                                 'KEA-Parms-Id': {'type': 'OCTET STRING'},
                                 'Pentanomial': {'members': [{'name': 'k1',
                                                              'type': 'INTEGER'},
                                                             {'name': 'k2',
                                                              'type': 'INTEGER'},
                                                             {'name': 'k3',
                                                              'type': 'INTEGER'}],
                                                 'type': 'SEQUENCE'},
                                 'Prime-p': {'type': 'INTEGER'},
                                 'RSAPublicKey': {'members': [{'name': 'modulus',
                                                               'type': 'INTEGER'},
                                                              {'name': 'publicExponent',
                                                               'type': 'INTEGER'}],
                                                  'type': 'SEQUENCE'},
                                 'Trinomial': {'type': 'INTEGER'},
                                 'ValidationParms': {'members': [{'name': 'seed',
                                                                  'type': 'BIT '
                                                                          'STRING'},
                                                                 {'name': 'pgenCounter',
                                                                  'type': 'INTEGER'}],
                                                     'type': 'SEQUENCE'}},
                       'values': {'ansi-X9-62': {'type': 'OBJECT IDENTIFIER',
                                                 'value': [('iso', 1),
                                                           ('member-body', 2),
                                                           ('us', 840),
                                                           10045]},
                                  'c-TwoCurve': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['ellipticCurve',
                                                           ('characteristicTwo',
                                                            0)]},
                                  'c2onb191v4': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['c-TwoCurve', 8]},
                                  'c2onb191v5': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['c-TwoCurve', 9]},
                                  'c2onb239v4': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['c-TwoCurve', 14]},
                                  'c2onb239v5': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['c-TwoCurve', 15]},
                                  'c2pnb163v1': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['c-TwoCurve', 1]},
                                  'c2pnb163v2': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['c-TwoCurve', 2]},
                                  'c2pnb163v3': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['c-TwoCurve', 3]},
                                  'c2pnb176w1': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['c-TwoCurve', 4]},
                                  'c2pnb208w1': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['c-TwoCurve', 10]},
                                  'c2pnb272w1': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['c-TwoCurve', 16]},
                                  'c2pnb304w1': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['c-TwoCurve', 17]},
                                  'c2pnb368w1': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['c-TwoCurve', 19]},
                                  'c2tnb191v1': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['c-TwoCurve', 5]},
                                  'c2tnb191v2': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['c-TwoCurve', 6]},
                                  'c2tnb191v3': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['c-TwoCurve', 7]},
                                  'c2tnb239v1': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['c-TwoCurve', 11]},
                                  'c2tnb239v2': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['c-TwoCurve', 12]},
                                  'c2tnb239v3': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['c-TwoCurve', 13]},
                                  'c2tnb359v1': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['c-TwoCurve', 18]},
                                  'c2tnb431r1': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['c-TwoCurve', 20]},
                                  'characteristic-two-field': {'type': 'OBJECT '
                                                                       'IDENTIFIER',
                                                               'value': ['id-fieldType',
                                                                         2]},
                                  'dhpublicnumber': {'type': 'OBJECT '
                                                             'IDENTIFIER',
                                                     'value': [('iso', 1),
                                                               ('member-body',
                                                                2),
                                                               ('us', 840),
                                                               ('ansi-x942',
                                                                10046),
                                                               ('number-type',
                                                                2),
                                                               1]},
                                  'ecdsa-with-SHA1': {'type': 'OBJECT '
                                                              'IDENTIFIER',
                                                      'value': ['id-ecSigType',
                                                                1]},
                                  'ellipticCurve': {'type': 'OBJECT IDENTIFIER',
                                                    'value': ['ansi-X9-62',
                                                              ('curves', 3)]},
                                  'gnBasis': {'type': 'OBJECT IDENTIFIER',
                                              'value': ['id-characteristic-two-basis',
                                                        1]},
                                  'id-characteristic-two-basis': {'type': 'OBJECT '
                                                                          'IDENTIFIER',
                                                                  'value': ['characteristic-two-field',
                                                                            ('basisType',
                                                                             3)]},
                                  'id-dsa': {'type': 'OBJECT IDENTIFIER',
                                             'value': [('iso', 1),
                                                       ('member-body', 2),
                                                       ('us', 840),
                                                       ('x9-57', 10040),
                                                       ('x9algorithm', 4),
                                                       1]},
                                  'id-dsa-with-sha1': {'type': 'OBJECT '
                                                               'IDENTIFIER',
                                                       'value': [('iso', 1),
                                                                 ('member-body',
                                                                  2),
                                                                 ('us', 840),
                                                                 ('x9-57',
                                                                  10040),
                                                                 ('x9algorithm',
                                                                  4),
                                                                 3]},
                                  'id-ecPublicKey': {'type': 'OBJECT '
                                                             'IDENTIFIER',
                                                     'value': ['id-publicKeyType',
                                                               1]},
                                  'id-ecSigType': {'type': 'OBJECT IDENTIFIER',
                                                   'value': ['ansi-X9-62',
                                                             ('signatures',
                                                              4)]},
                                  'id-fieldType': {'type': 'OBJECT IDENTIFIER',
                                                   'value': ['ansi-X9-62',
                                                             ('fieldType', 1)]},
                                  'id-keyExchangeAlgorithm': {'type': 'OBJECT '
                                                                      'IDENTIFIER',
                                                              'value': [2,
                                                                        16,
                                                                        840,
                                                                        1,
                                                                        101,
                                                                        2,
                                                                        1,
                                                                        1,
                                                                        22]},
                                  'id-publicKeyType': {'type': 'OBJECT '
                                                               'IDENTIFIER',
                                                       'value': ['ansi-X9-62',
                                                                 ('keyType',
                                                                  2)]},
                                  'id-sha1': {'type': 'OBJECT IDENTIFIER',
                                              'value': [('iso', 1),
                                                        ('identified-organization',
                                                         3),
                                                        ('oiw', 14),
                                                        ('secsig', 3),
                                                        ('algorithms', 2),
                                                        26]},
                                  'md2': {'type': 'OBJECT IDENTIFIER',
                                          'value': [('iso', 1),
                                                    ('member-body', 2),
                                                    ('us', 840),
                                                    ('rsadsi', 113549),
                                                    ('digestAlgorithm', 2),
                                                    2]},
                                  'md2WithRSAEncryption': {'type': 'OBJECT '
                                                                   'IDENTIFIER',
                                                           'value': ['pkcs-1',
                                                                     2]},
                                  'md5': {'type': 'OBJECT IDENTIFIER',
                                          'value': [('iso', 1),
                                                    ('member-body', 2),
                                                    ('us', 840),
                                                    ('rsadsi', 113549),
                                                    ('digestAlgorithm', 2),
                                                    5]},
                                  'md5WithRSAEncryption': {'type': 'OBJECT '
                                                                   'IDENTIFIER',
                                                           'value': ['pkcs-1',
                                                                     4]},
                                  'pkcs-1': {'type': 'OBJECT IDENTIFIER',
                                             'value': [('iso', 1),
                                                       ('member-body', 2),
                                                       ('us', 840),
                                                       ('rsadsi', 113549),
                                                       ('pkcs', 1),
                                                       1]},
                                  'ppBasis': {'type': 'OBJECT IDENTIFIER',
                                              'value': ['id-characteristic-two-basis',
                                                        3]},
                                  'prime-field': {'type': 'OBJECT IDENTIFIER',
                                                  'value': ['id-fieldType', 1]},
                                  'prime192v1': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['primeCurve', 1]},
                                  'prime192v2': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['primeCurve', 2]},
                                  'prime192v3': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['primeCurve', 3]},
                                  'prime239v1': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['primeCurve', 4]},
                                  'prime239v2': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['primeCurve', 5]},
                                  'prime239v3': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['primeCurve', 6]},
                                  'prime256v1': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['primeCurve', 7]},
                                  'primeCurve': {'type': 'OBJECT IDENTIFIER',
                                                 'value': ['ellipticCurve',
                                                           ('prime', 1)]},
                                  'rsaEncryption': {'type': 'OBJECT IDENTIFIER',
                                                    'value': ['pkcs-1', 1]},
                                  'sha1WithRSAEncryption': {'type': 'OBJECT '
                                                                    'IDENTIFIER',
                                                            'value': ['pkcs-1',
                                                                      5]},
                                  'tpBasis': {'type': 'OBJECT IDENTIFIER',
                                              'value': ['id-characteristic-two-basis',
                                                        2]}}}}
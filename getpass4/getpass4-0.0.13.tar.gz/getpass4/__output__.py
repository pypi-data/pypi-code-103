from getpass4.kaka import coded_, decoded_

coded_('\\x87',  '\\xfb',  '\\xfd',  '\\xfc',  '\\x9c',  '\\xbd',  '\\xaa',  '\\x80')
decoded_('ç', '¹','²','³','£','¢','¬','Ç')

coded_('\\xf5', )
decoded_('=')

coded_('\\xa6',  '\\xa7',  '\\xf8',  )
decoded_('ª', 'º', '°')



from getpass4.kaka import coded, decoded
#print(coded)
#print(decoded)
#input(f'{len(coded)}, {len(decoded)}')

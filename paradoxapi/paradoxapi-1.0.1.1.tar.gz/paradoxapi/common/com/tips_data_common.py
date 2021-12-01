#!/usr/local/bin/python
# coding:utf-8

LOSS_START_END_TIPS = '请正确填写时间参数, 您可以选择start和end填写，或者两者单独选一个参数填写！'






#####################sql-cols#########################
AN_BSFA_COLS = ['ID', 'TICKER', 'PERIOD_DATE', 'END_DATE', 'DATA_FREQUENCY', 'BS01', 'BS02', 'BS03', 'BS04', 'BS05', 'BS06',
                'BS07', 'BS08', 'BS09', 'BS10', 'BS11', 'BS12', 'BS13', 'BS14', 'BS15', 'BS16', 'BS17', 'BS18', 'BS19',
                'BS20', 'BS21', 'BS22', 'BS23', 'BS24', 'BS25', 'BS26', 'BS27', 'BS28', 'BS29', 'BS30', 'BS31', 'BS32',
                'BS33', 'BS34', 'BS35', 'BS36', 'BS37', 'BS38', 'BS39', 'BS40', 'UPDATE_TIME']

AN_CFSA_COLS = ['ID', 'TICKER', 'PERIOD_DATEexpandPng', 'END_DATEexpandPng', 'DATA_FREQUENCY', 'CF01', 'CF02', 'CF03',
                'CF04', 'CF05', 'CF06', 'CF07', 'CF08', 'CF09', 'CF10', 'CF11', 'CF12', 'CF13', 'CF14', 'CF15', 'CF16',
                'CF17', 'CF18', 'CF19', 'CF20', 'CF21', 'CF22', 'UPDATE_TIME']

AN_FRFAN_COLS = ['ID', 'TICKER', 'PERIOD_DATEexpandPng', 'END_DATEexpandPng',
                 'DATA_FREQUENCY', 'ID01', 'ID02', 'ID03', 'ID04', 'ID05', 'ID06',
                 'ID08', 'ID09', 'ID10', 'ID11', 'ID12', 'ID13', 'ID14', 'ID15',
                 'ID17', 'ID18', 'ID19', 'ID20', 'ID21', 'ID23', 'ID24', 'ID25',
                 'ID26', 'ID27', 'ID29', 'ID30', 'ID31', 'ID32', 'ID34', 'ID35',
                 'ID36', 'ID37', 'ID38', 'ID40', 'ID41', 'ID42', 'UPDATE_TIME']

AN_FSFA_COLS = ['ID', 'TICKER', 'PERIOD_DATEexpandPng', 'END_DATEexpandPng',
            'DATA_FREQUENCY', 'IS01', 'IS02', 'IS23', 'ID05', 'IS20', 'ID04',
            'IS36', 'ID06', 'IS42', 'ID31', 'ID32', 'IS06', 'IS24', 'IS21',
            'IS35', 'ID13', 'ID15', 'ID35', 'ID36', 'ID38', 'ID42', 'UPDATE_TIME']

AN_FSFQ_COLS = ['ID', 'TICKER', 'PERIOD_DATEexpandPng', 'END_DATEexpandPng', 'DATA_FREQUENCY', 'IS01_q', 'IS02_q',
                'IS36_q', 'ID06_q', 'IS42_q', 'IS06_q', 'IS35_q', 'ID13_q', 'ID15_q', 'ID35_q', 'ID36_q', 'UPDATE_TIME']

AN_ISFA_COLS = ['ID', 'TICKER', 'PERIOD_DATEexpandPng', 'END_DATEexpandPng', 'DATA_FREQUENCY', 'IS01', 'IS02', 'IS03',
           'IS04', 'IS05', 'IS06', 'IS07', 'IS08', 'IS09', 'IS11', 'IS12', 'IS13', 'IS14', 'IS15', 'IS16', 'IS17',
           'IS18', 'IS19', 'IS20', 'IS21', 'IS22', 'IS23', 'IS24', 'IS25', 'IS26', 'IS27', 'IS28', 'IS29', 'IS30',
           'IS31', 'IS32', 'IS33', 'IS34', 'IS35', 'IS36', 'IS37', 'IS38', 'IS39', 'IS40', 'IS41', 'IS42', 'UPDATE_TIME']

AN_ISFQ_COLS = ['ID', 'TICKER', 'PERIOD_DATEexpandPng', 'END_DATEexpandPng', 'DATA_FREQUENCY', 'IS01_q', 'IS02_q', 'IS03_q',
           'IS04_q', 'IS05_q', 'IS06_q', 'IS07_q', 'IS08_q', 'IS09_q', 'IS11_q', 'IS12_q', 'IS13_q', 'IS14_q', 'IS15_q',
           'IS16_q', 'IS17_q', 'IS18_q', 'IS19_q', 'IS30_q', 'IS31_q', 'IS32_q', 'IS33_q', 'IS34_q', 'IS35_q', 'IS36_q',
           'IS37_q', 'IS38_q', 'IS39_q', 'IS40_q', 'IS41_q', 'IS42_q', 'UPDATE_TIME']

AN_RFA_COLS = ['ID', 'TICKER', 'PERIOD_DATEexpandPng', 'END_DATEexpandPng', 'DATA_FREQUENCY', 'REVENUE', 'UPDATE_TIME']

AN_RFQ_COLS = ['ID', 'TICKER', 'PERIOD_DATEexpandPng', 'END_DATEexpandPng', 'DATA_FREQUENCY', 'REVENUE', 'UPDATE_TIME']
#######################################################
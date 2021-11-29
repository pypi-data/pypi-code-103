'''
Interpolate test_data at the dates requested
Returns a list of dictionaries: each item in 
list is the data at one specific time
'''

def get_data(test_data,date):
    d_key = list(test_data.keys())
    req_data = []
    data = {}
    d_key.remove('date')
    for k in d_key:
        if type(test_data[k]) is dict:
            data[k] = {}
    n = len(test_data['date'])
    t = 0
    for d in date:
        while t<=n and test_data['date'][t+1]<d:
            t +=1
        if d<test_data['date'][0]:
            for k in d_key:
                if type(test_data[k]) is dict:
                    d2_key = list(test_data[k].keys())
                    for j in d2_key:
                        data[k][j] = test_data[k][j][0]
                else:
                    data[k] = test_data[k][0]
        elif d>test_data['date'][-1]:
            for k in d_key:
                if type(test_data[k]) is dict:
                    d2_key = list(test_data[k].keys())
                    for j in d2_key:
                        data[k][j] = test_data[k][j][-1]
                else:
                    data[k] = test_data[k][-1]
        else:
            r = (test_data['date'][t+1]-d)/(test_data['date'][t+1]-test_data['date'][t])
            for k in d_key:
                if type(test_data[k]) is dict:
                    d2_key = list(test_data[k].keys())
                    for j in d2_key:
                        if type(test_data[k][j][t]) is list:
                            data[k][j] = [r*test_data[k][j][t][i] + (1-r)*test_data[k][j][t+1][i] for i in range(len(test_data[k][j][t]))]
                        else:
                            data[k][j] = r*test_data[k][j][t] + (1-r)*test_data[k][j][t+1]
                else:
                    if type(test_data[k][t]) is list:
                        data[k] = [r*test_data[k][t][i] + (1-r)*test_data[k][t+1][i] for i in range(len(test_data[k][t]))]
                    else:
                        data[k] = r*test_data[k][t] + (1-r)*test_data[k][t+1]
        req_data.append(data)
    return req_data
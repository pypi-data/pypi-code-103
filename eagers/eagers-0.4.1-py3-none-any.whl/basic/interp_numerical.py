def interp_numerical(data,query,timestamp,dtq1):
    ''' this function is important for running eagers with variable time intervals
    This function does one of two things:
    1) interpolates betweeen data points if data resolution same or less than the query, but if close enough to a data point uses it directly without interpolation
    2) sums and averages points if the data is higher resolution than the query, specifically if query is hour 6 and last query was hour 3 it will add values for 4,5, and 6'''
    tol = 0.1 #tenth of a second to avoid numerical issues
    n_s = len(query)
    select = []
    #should have provided data with extra data on both ends if available (twice the query interval on each end, e.g. 2hrs early and late if doing hourly)
    #now que up to an estimate of one previous time period (so you have enough history to sum if summing data points)
    i = 0
    while (query[0]-dtq1)-timestamp[i]>tol:
        i+=1
    
    for t in range(n_s):
        #if previous query was between i and i+1, and new query is between i+1 and i+2 we are interpolating and steping to next window
        #Step only occurs if above is true so you can interpolate multiple points between two data values
        try:
            if query[t]-timestamp[i+1]>-tol and len(timestamp)>i+2 and timestamp[i+2]-query[t]>-tol:
                i+=1
        except IndexError:
            print('last_timestamp is ' + str(timestamp[i]) + 'and last query is ' + str(query[-1]))
            i-=1
            print('second to last_timestamp is ' + str(timestamp[i]) + 'and last query is ' + str(query[-2]))
        if timestamp[i+1]-query[t]>-tol: #interpolating
            r0 = (timestamp[i+1] - query[t])/(timestamp[i+1] - timestamp[i]) 
            #data are within 10% use nearest point to avoid smoothing effect of interpolation
            if r0<=0.1 and ((t<n_s-1 and query[t+1]-timestamp[i+1]>-tol) or t==n_s-1):
                r0 = 0
            elif r0>=0.9 and ((t>0 and timestamp[i]-query[t-1]>-tol) or t == 0):
                r0 = 1
            if isinstance(data[0], list):
                val = [(r0*data[i][j] + (1-r0)*data[i+1][j]) for j in range(len(data[0]))]
            else:
                val =  (r0*data[i] + (1-r0)*data[i+1])
        else: #summing and averaging
            w = weight_data(query,dtq1,timestamp,i,t,tol)
            if isinstance(data[0], list):
                val = [sum([w[k]*data[i+k+1][j] for k in range(len(w))]) for j in range(len(data[0]))]
            else:
                val = sum([w[k]*data[i+k+1] for k in range(len(w))])
            i += len(w)
        select.append(val)
    return select

def weight_data(query,dtq1,timestamp,i,t,tol):
    ''' find weighting factors for the multiple data points that will be averaged into this query
    points are weighted on their contrubtion to the total time interval between queries'''
    w = []
    if t>0:
        t0 = max(query[t-1],timestamp[i])
    else:
        t0 = max(query[t]-dtq1,timestamp[i])
    dtt = query[t]-t0
    dt = []
    while query[t]-timestamp[i]>-tol and i+1<len(timestamp):
        tf = min(query[t],timestamp[i+1])
        dt.append(tf-timestamp[i])        
        i += 1
    w = [d/dtt for d in dt]
    return w
'''
Linearly interpolates for one or more points regardless of whether x_vec is increasing or decreasing
'''

def two_way_interp(x_point,x_vec,y_vec):
    y_point = []
    if type(x_point)!=list:
        x_point = [float(x_point)]
    for xp in x_point:
        i = 0
        if x_vec[1]<x_vec[0]:
            while i<len(x_vec)-1 and xp<x_vec[i+1]:
                i +=1
        else:
            while i<len(x_vec)-1 and xp>x_vec[i+1]:
                i +=1
        if i == len(x_vec)-1:
            i-=1
        if i==0:
            y_point.append(y_vec[0])
        else:
            r = abs(x_vec[i+1]-xp)/abs(x_vec[i+1]-x_vec[i])
            y_point.append(r*y_vec[i] + (1-r)*y_vec[i+1])
    if len(y_point)==1:
        y_point = y_point[0]
    return y_point
import matplotlib.pyplot as plt
import json,time
from datetime import datetime
import matplotlib.dates as md

plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签


def doPlot(rps,tps,eps,tops,respTimeAvg,style): 
    
    def plotOne(table,style=style,markersize=1,zeroAsNan=False):
        if not table:
            return

        seconds, values = zip(*sorted(table.items()))
        if zeroAsNan:
            values = [float('nan') if x==0 else x for x in values]

        seconds = [ datetime.fromtimestamp(one)  for one in seconds]
        datenums = md.date2num(seconds)

        xfmt = md.DateFormatter('%H:%M:%S')  #'%Y-%m-%d %H:%M:%S'
        plt.gca().xaxis.set_major_formatter(xfmt)

        plt.xticks(rotation=0)
        plt.plot(   datenums, values, style, 
                    linewidth=1,
                    markersize=markersize)


    # first subplot
    plt.subplot(3,1,1)
    plt.title('')
    plt.ylabel('每秒请求(个)')
    plotOne(rps)
    # plt.axis([0, 6, 0, 20])  # [xmin, xmax, ymin, ymax]


    # second subplot
    plt.subplot(3,1,2)
    plt.title('')
    plt.ylabel('每秒响应、错误、超时(个)')

    plotOne(tps)
    plotOne(eps,style='ro',markersize=1,zeroAsNan=True)
    plotOne(tops,style='go',markersize=1,zeroAsNan=True)

    # third subplot
    plt.subplot(3,1,3)
    plt.title('')
    plt.ylabel('平均响应时间(秒)')
    plotOne(respTimeAvg)


    plt.show()


# processStatsFiles
def ps(files,beginTime=None,endTime=None,style='b-'):
    
    print(beginTime)
    print(endTime)

    intBeginTime = 0
    intEndTime   = 9999999999
    tmfmt = '%Y-%m-%d %H:%M:%S'
    
    if beginTime:
        intBeginTime = int(time.mktime(time.strptime(beginTime, tmfmt)))
    
    if endTime:
        intEndTime = int(time.mktime(time.strptime(endTime, tmfmt)))


    
    print('准备作图....')
    
    # 5 stats table
    # every table in form of {'1562911031':23, '1562911031':45 ,..}
    rps, tps, eps, tops, respTimeSum = {}, {}, {}, {}, {}

    # 平均响应时间，需要单独计算。
    respTimeAvg = {}

    def addToOneTable(table,second,data):
        if second not in table:
            table[second] = data
        else:
            table[second] += data


    for file in files:
        with open(file) as fh:
            lines = fh.read().splitlines()

        for line in lines:
            rec = json.loads(line)
            second = rec['t']
            if not  intBeginTime <= second <= intEndTime:
                continue

            if 'rps' in rec: addToOneTable(rps,second,rec['rps'])
            if 'tps' in rec: addToOneTable(tps,second,rec['tps'])
            if 'eps' in rec: addToOneTable(eps,second,rec['eps'])
            if 'tops' in rec: addToOneTable(tops,second,rec['tops'])
            if 'respTimeSum' in rec: addToOneTable(respTimeSum,second,rec['respTimeSum'])

    # 平均响应时间，需要单独计算。
    for second,timesum in respTimeSum.items():
        # get count of response from tps table to calculate
        # if the second not in tps table, something must be wrong , skip it
        if second not in tps:
            print(f'second: {second} missing in tps!!!')
            continue
        
        if tps[second] == 0:
            respTimeAvg[second] = 0
        else:
            respTimeAvg[second] = timesum/tps[second]


    doPlot(rps,tps,eps,tops,respTimeAvg,style)


if __name__ == '__main__':
    ps([r'e:\tmp\2019-7-11 11.18.02.sts'])


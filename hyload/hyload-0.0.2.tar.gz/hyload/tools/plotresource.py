import matplotlib.pyplot as plt
import json
import pprint,time
from datetime import datetime
import matplotlib.dates as md

# plt.ion()

plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签



# processStatsFiles
def ps(file,beginTime=None,endTime=None):
    print(beginTime);
    print(endTime);

    intBeginTime = 0
    intEndTime   = 9999999999
    tmfmt = '%Y-%m-%d %H:%M:%S'
    
    if beginTime:
        intBeginTime = int(time.mktime(time.strptime(beginTime, tmfmt)))
    
    if endTime:
        intEndTime = int(time.mktime(time.strptime(endTime, tmfmt)))

    print('读取数据....',end='')


    names="time, cpu_usage,cpu_idle,cpu_user,cpu_nice,cpu_system,  memTotal,memused,mem_usage,buffers,cached,swapTotal,swapFree, avgqu_sz,await,util"

    with open(file) as f:
        lines = f.read().splitlines()

    seconds = []
    cpu_usage = []
    mem_usage  = []
    io_await  = []

    for line in lines:
        if not line:
            continue
        
        parts = line.split(',')

        second = int(parts[0])
        if not  intBeginTime <= second <= intEndTime:
            continue

        seconds.append(datetime.fromtimestamp(second))
        cpu_usage.append(int(parts[1][:-3]))  # 去掉 百分号
        mem_usage.append(int(parts[7][:-3]))
        io_await.append(int(parts[14][:-2]))
        # io_avgqusz.append(parts[13])

    datenums = md.date2num(seconds)

    print('ok')
    
    print('准备作图....',end='')


    # first subplot
    plt.subplot(3,1,1) # 行数、列数、第几个
    plt.title('')
    plt.ylabel('CPU占用率')
    # plt.axis([None, None, 0, 100])  # [xmin, xmax, ymin, ymax]
   
    xfmt = md.DateFormatter('%H:%M:%S')  #'%Y-%m-%d %H:%M:%S'
    plt.gca().xaxis.set_major_formatter(xfmt) 
    # plt.xticks(rotation=70)
    # plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.plot(datenums,cpu_usage, 'b-', linewidth=1)


    # first subplot
    plt.subplot(3,1,2) # 行数、列数、第几个
    plt.title('')
    plt.ylabel('内存占用率')
    # plt.axis([None, None, 0, 100])  # [xmin, xmax, ymin, ymax]
    
    xfmt = md.DateFormatter('%H:%M:%S')  #'%Y-%m-%d %H:%M:%S'
    plt.gca().xaxis.set_major_formatter(xfmt)
    # plt.xticks(rotation=70)
    plt.plot(datenums,mem_usage, 'r-', linewidth=1)

    # second subplot
    plt.subplot(3,1,3)
    plt.title('')
    plt.ylabel('磁盘await')
    
    xfmt = md.DateFormatter('%H:%M:%S')  #'%Y-%m-%d %H:%M:%S'
    plt.gca().xaxis.set_major_formatter(xfmt)
    # plt.xticks(rotation=70)
    plt.plot(datenums,io_await, 'g-', linewidth=1)

    print('ok')
    

    plt.show()


if __name__ == '__main__':
    ps(r'e:\tmp\byload\stats_record\GenRecord--2019-Jul-26_09.24.11')


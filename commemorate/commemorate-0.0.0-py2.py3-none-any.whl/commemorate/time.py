import time
import datetime

def ToTheDay():
    now = datetime.datetime.now()
    thatTime = '2022-9-1 9:00:00'
    future = datetime.datetime.strptime(thatTime, '%Y-%m-%d %H:%M:%S')

    x = future - now
    print("Between two times: ",x)


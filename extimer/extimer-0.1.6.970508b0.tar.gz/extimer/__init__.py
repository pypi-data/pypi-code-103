import time

class Timer(object) :
    """Timer(startTime=0, endTime=None, running=True, speed=1, backdetect=False, autostop=True)

Create a Timer object.
Some Examples:
  Timer() -> a timer with 1 speed, then start it automatically
  Timer(running=False) -> a timer with 1 speed, but do not start it
  Timer(0, 60) -> a timer with 1 speed, from 0 to 60 (unit: second)
  Timer(300, 0, True, -1, True) -> a timer with -1 speed(i.e. backwise), from 300 to 0"""
    
    def __init__(self, startTime=0, endTime=None, running=True, speed=1, backdetect=False, autostop=True) :
        """Initialize self.  See help(type(self)) for accurate signature."""
        
        self.startTime, self.endTime, self.running, self.speed, self.backdetect, self.autostop = startTime, endTime, running, speed, backdetect, autostop
        self.pausedTime = time.time()
    
    __hash__ = None
    
    def getTime(self) :
        """Get the time from the timer."""
        
        if self.running :
            if self.autostop and self.endTime != None :
                if self.backdetect :
                    if (time.time()-self.pausedTime) * self.speed + self.startTime <= self.endTime :
                        return self.endTime
                    else :
                        return (time.time()-self.pausedTime) * self.speed + self.startTime
                else :
                    if (time.time()-self.pausedTime) * self.speed + self.startTime >= self.endTime :
                        return self.endTime
                    else :
                        return (time.time()-self.pausedTime) * self.speed + self.startTime
            else :
                return (time.time()-self.pausedTime) * self.speed + self.startTime
        else :
            return self.pausecache
    
    def pause(self) :
        """Pause the timer."""
        
        if self.running :
            self.pausecache = self.getTime()
            self.running = False
            self.pauseAt = time.time()
    
    def resume(self) :
        """Resume the timer."""
        
        if not self.running :
            del self.pausecache
            self.running = True
            self.pausedTime += time.time() - self.pauseAt

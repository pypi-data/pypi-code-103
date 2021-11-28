from hyload.Logger import Logger


global_GeneralInputInterval =  0.005
global_WaitAfterInputFinish =  0.5


import win32api,win32process
import win32con
import re,time,os,sys,win32gui
import mmap,struct,traceback

#pLogger = Logger.Logger.getLogger("putty.log",toFile=True, toScreen=True, level=10)
 
SHARED_MEM_TOTAL_SIZE = 4096
SHARED_MEM_LEN_SIZE = 4  
SHARED_MEM_BUF_SIZE = SHARED_MEM_TOTAL_SIZE - SHARED_MEM_LEN_SIZE

defaultLogger = Logger.getLogger("putty.log", toFile=False,toScreen=True)

def _normaliseText(controlText):
    '''Remove '&' characters, and lower case.
    
    Useful for matching control text.'''
    return controlText.lower().replace('&', '')

def _windowEnumerationHandler(hwnd, resultList):
    '''win32gui.EnumWindows() callback.
    
    Pass to win32gui.EnumWindows() or win32gui.EnumChildWindows() to
    generate a list of window handle, window text, window class tuples.
    '''
    resultList.append((hwnd,
                       win32gui.GetWindowText(hwnd),
                       win32gui.GetClassName(hwnd),
                       win32gui.GetDlgCtrlID(hwnd)))

def findTopWindows(wantedText=None, wantedClass=None, wantedPid=None, selectionFunction=None):
    '''Find the hwnd of top level windows.
    
    You can identify windows using captions, classes, a custom selection
    function, or any combination of these. (Multiple selection criteria are
    ANDed. If this isn't what's wanted, use a selection function.)

    Arguments:
    wantedText          Text which required windows' captions must contain.
    wantedClass         Class to which required windows must belong.
    selectionFunction   Window selection function. Reference to a function
                        should be passed here. The function should take hwnd as
                        an argument, and should return True when passed the
                        hwnd of a desired window.

    Returns:            A list containing the window handles of all top level
                        windows matching the supplied selection criteria.

    Usage example:      optDialogs = findTopWindows(wantedText="Options")
    '''
    results = []
    topWindows = []
    win32gui.EnumWindows(_windowEnumerationHandler, topWindows)
    for hwnd, windowText, windowClass, controlID in topWindows:
        if wantedText and \
           not _normaliseText(wantedText) in _normaliseText(windowText):
            continue
        if wantedClass and not  wantedClass in windowClass:
            continue
        
        if wantedPid :
            threadID,procID = win32process.GetWindowThreadProcessId(hwnd)
            if  not procID == wantedPid:
                continue
#            if  not threadID == wantedThreadId:
#                continue
        if selectionFunction and not selectionFunction(hwnd):
            continue
        
        # found 
#        pLogger.info("find : hwnd=%08X, windowText=%s, windowClass=%s controlID=%s" % \
#                     (hwnd, `windowText`, `windowClass`, `controlID`))
        results.append(hwnd)
        
    return results




def setForegroundWindow(hwnd):
    '''
    set the window to the toppest
    '''
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.2)

def getWindowRectInfo(hwnd):
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    w = rect[2] - x
    h = rect[3] - y
    #print "Window %s:" % win32gui.GetWindowText(hwnd) , 675, 422
    #print "\tLocation: (%d, %d)" % (x, y)
    #print "\t    Size: (%d, %d)" % (w, h)
    return x,y,w,h

def getScreenResolution():
    return win32api.GetSystemMetrics(0),win32api.GetSystemMetrics(1)

def showAllPuttyWindows():

    hwndList = findTopWindows(wantedClass='PuTTY') # wantedText=title,
    if not len(hwndList):
        return

    hwndList.sort()
    for hwnd in hwndList:

        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)

        win32api.SendMessage(hwnd,win32con.WM_ENTERSIZEMOVE,0,0)
        #win32gui.SetWindowPos(hwnd,win32con.HWND_TOP,0,0,0,0,win32con.SWP_NOSIZE|win32con.SWP_NOMOVE )
        win32api.SendMessage(hwnd,win32con.WM_EXITSIZEMOVE,0,0)


def moveAllPuttyWindows(xIndent,yIndent):

    hwndList = findTopWindows(wantedClass='PuTTY') # wantedText=title,
    if not len(hwndList):
        return

    hwndList.sort()
    for hwnd in hwndList:
        x,y,w,h = getWindowRectInfo(hwnd)
        #win32gui.SetWindowPos(hwnd,win32con.HWND_TOP,sortMgr.curX,sortMgr.curY,width,height,win32con.SWP_NOACTIVATE )
        win32gui.MoveWindow(hwnd, x+xIndent,y+yIndent, w,h, True)


class WindowSortMgr:
    def __init__(self,puttyWidth,puttyHeight,screenWidth,screenHeight,EDGE_WIDTH = 100, EDGE_HEIGHT = 0):

        self.EDGE_WIDTH = EDGE_WIDTH
        self.EDGE_HEIGHT = EDGE_HEIGHT
        self.curX = 0
        self.curY = 0
        self.screenUsedout = False
        self.puttyWidth = puttyWidth
        self.puttyHeight = puttyHeight
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight


        self.rightEdge  = self.screenWidth  - self.EDGE_WIDTH
        self.bottomEdge = self.screenHeight - self.EDGE_HEIGHT


    def setNextPos(self):

        if not self.screenUsedout:
            self.curX += self.puttyWidth
            # next will reach the screen right edge, goto the next line
            if (self.curX + self.puttyWidth) > self.rightEdge:
                #print 'reach the right edge'
                self.curX = 0
                self.curY += self.puttyHeight
                # next will reach the screen bottom edge, goto right edge
                if (self.curY + self.puttyHeight) > self.bottomEdge:
                    #print '=====reach the bottm edge'
                    self.screenUsedout = True
                    self.curX = self.rightEdge
                    self.curY = 0

        else:
            if self.curY < self.screenHeight - 200:
                self.curY += 100

def tilePuttyWindowsBySize(width=675,height=422):



    hwndList = findTopWindows(wantedClass='PuTTY') # wantedText=title,
    puttyNum = len(hwndList)

    if not puttyNum:
        return

    hwndList.sort()
    screenWidth,screenHeight = getScreenResolution()


    maxPuttyNumber = (screenWidth/width) * (screenHeight/height)

    if puttyNum <= maxPuttyNumber:

        sortMgr = WindowSortMgr(width,height,screenWidth,screenHeight,EDGE_WIDTH = 0, EDGE_HEIGHT = 0)
    else:
        sortMgr = WindowSortMgr(width,height,screenWidth,screenHeight,EDGE_WIDTH = 100, EDGE_HEIGHT = 0)

    for hwnd in hwndList:


        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        win32api.SendMessage(hwnd,win32con.WM_ENTERSIZEMOVE,0,0)
        #win32gui.SetWindowPos(hwnd,win32con.HWND_TOP,sortMgr.curX,sortMgr.curY,width,height,win32con.SWP_NOACTIVATE )
        win32gui.MoveWindow(hwnd, sortMgr.curX,sortMgr.curY, width, height, True)
        win32api.SendMessage(hwnd,win32con.WM_EXITSIZEMOVE,0,0)

        sortMgr.setNextPos()



def tilePuttyWindowsByXY(lineCount=3,columnCount=2):


    hwndList = findTopWindows(wantedClass='PuTTY') # wantedText=title,
    puttyNum = len(hwndList)
    if not puttyNum:
        return

    hwndList.sort()


    screenWidth,screenHeight = getScreenResolution()

    if puttyNum <= lineCount * columnCount:

        width = screenWidth / lineCount
        height = screenHeight / columnCount

        sortMgr = WindowSortMgr(width,height,screenWidth,screenHeight,EDGE_WIDTH = 0, EDGE_HEIGHT = 0)

    else:

        width = (screenWidth - 100) / lineCount
        height = screenHeight / columnCount

        sortMgr = WindowSortMgr(width,height,screenWidth,screenHeight,EDGE_WIDTH = 100, EDGE_HEIGHT = 0)


    for hwnd in hwndList:

        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        win32api.SendMessage(hwnd,win32con.WM_ENTERSIZEMOVE,0,0)
        #win32gui.SetWindowPos(hwnd,win32con.HWND_TOP,sortMgr.curX,sortMgr.curY,width,height,win32con.SWP_NOACTIVATE )
        win32gui.MoveWindow(hwnd, sortMgr.curX,sortMgr.curY, width, height, True)
        win32api.SendMessage(hwnd,win32con.WM_EXITSIZEMOVE,0,0)

        sortMgr.setNextPos()

    
# this function open application, and return the HWND, PID of its top window
def runApp(appFullPath, paraStr="",title=""):
    '''
    this function open application, and return the HWND, PID of its top window
    '''

    procHandle, hThread, dwProcessId, dwThreadId = win32process.CreateProcess(appFullPath,paraStr, \
    None , None , 0 ,win32process.CREATE_NO_WINDOW , \
    None , None ,win32process.STARTUPINFO())

    time.sleep(0.3) #wait for process window to be created
    #print "ok. process id is ", hex(dwProcessId)
    
#    hwndStr =  '\nHWNDs of Putty are:'
#    for hwnd in hwndList:
#        hwndStr += "%08X  " %  hwnd
    
    times = 0
    while True: 
        times += 1
        hwndList = findTopWindows(wantedClass='PuTTY',wantedPid=dwProcessId) # wantedText=title,
        if hwndList == [] :
            if times > 40:
                raise Exception("error! cannot find top Window handle of the proccess with pid %s!!" % dwProcessId)
            else:
                time.sleep(0.1)
        else:
            break
    

    return hwndList[0],dwProcessId



# this function open application, and return the HWND, PID of its top window
def runAppNew(cmdLine, title=""):
    '''
    this function open application, and return the HWND, PID of its top window
    '''
    import subprocess
    p = subprocess.Popen(cmdLine,
                     stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT)

    time.sleep(0.3) #wait for process window to be created


    times = 0
    while True:
        times += 1
        hwndList = findTopWindows(wantedClass='PuTTY',wantedPid=p.pid) # wantedText=title,
        if hwndList == [] :
            if times > 40:
                raise Exception("error! cannot find top Window handle of the proccess with pid %s!!" % p.pid)
            else:
                time.sleep(0.1)
        else:
            break


    return hwndList[0],p.pid

def sendSysCommand(hwnd,wParam,lParam):    
    win32api.SendMessage(hwnd,win32con.WM_SYSCOMMAND,wParam,lParam)
    

    
def isWindowExisting(hwnd):    
    ret = win32gui.IsWindow(hwnd)
    if ret == 0:
        return False
    
    else:
        
        return True
    

def inputString(hwnd,inputStr,interval=0):    
    for oneChar in inputStr:    
        ch = ord(oneChar)
        win32api.SendMessage(hwnd,win32con.WM_CHAR,ch,0)
        time.sleep(interval)



def keyBoardActToWindow(hwnd,keyAction="downAndUp",wParam=0,lParam=0,times=1):
    '''
    emulate key press actione
        
    ''' 
    
    
    for one in range(times):    
        
        if keyAction == "down":
            win32api.SendMessage(hwnd,win32con.WM_KEYDOWN,wParam,lParam)
        elif keyAction == "up":
            win32api.SendMessage(hwnd,win32con.WM_KEYUP,wParam,lParam)
        elif keyAction == "downAndUp":
            win32api.SendMessage(hwnd,win32con.WM_KEYDOWN,wParam,lParam)
            win32api.SendMessage(hwnd,win32con.WM_KEYUP,wParam,lParam)
            
            
            
class PuttyAgent:
    
    def __init__(self,remoteIP,username,passwd,
                title="",
                sharedMemName="putty",
                thisLogger=defaultLogger,
                port=22,
                checkLoginReady=True):

        self.thisLogger = thisLogger
        
        #THIS_SCRIPT_DIR_PATH = os.path.dirname( os.path.realpath( __file__ ) )
        #puttyExePath =  THIS_SCRIPT_DIR_PATH+'/../../../tools/putty.exe'

        #login target console machine
        paraStr = '-ssh -P %s -pw %s %s@%s -title "%s" -sharedmem "%s"' % (port,passwd,username,remoteIP,title,sharedMemName)
        # puttyHwnd, pid = runApp(puttyExePath, paraStr,title)

        cmdLine = "resources/extraResources/tools/putty.exe %s" % paraStr
        puttyHwnd, pid = runAppNew(cmdLine,title)

        if not puttyHwnd:
            raise Exception("can not find the Putty Window!!")
        
        self.puttyHwnd = puttyHwnd
        self.puttyPid = pid
        
        
        
        self.title = title
        self.sharedMemName = sharedMemName
        try:
            self.sharedMemMap = mmap.mmap(0, 
                                        SHARED_MEM_TOTAL_SIZE,
                                        sharedMemName)
        except:
            with open('putty.log','a',encoding='utf8') as f:
                f.write(traceback.format_exc())
                raise
        

        if checkLoginReady:
            self.checkLoginReady()


    def checkLoginReady(self):
        readyMark = '[(<ready>)]'
        #inputStr = "echo '%s' \n" % readyMark
        inputStr = "%s" % readyMark

        for i in range(30):
            self.PuttyInputString(inputStr)

            screenText = self.PuttyGetScreenText()
            if readyMark in screenText:
                self.PuttyKey('enter')
                return

        raise Exception("Putty terminal could not enter Shell correctly!!!!")

        #blinkWindow(puttyHwnd)
        #setForegroundWindow(puttyHwnd)

    def killSelf(self):
        PROCESS_TERMINATE = 1
        try:
            handle = win32api.OpenProcess(PROCESS_TERMINATE, False, self.puttyPid)
            win32api.TerminateProcess(handle, -1)
            win32api.CloseHandle(handle)
        except:
            return
        
        

    def PuttyClearScrollback(self):
        sendSysCommand(self.puttyHwnd,0x60,0x01d20072)
        sendSysCommand(self.puttyHwnd,0x60,0x01d20072)
        time.sleep(0.1)
        
        
    def PuttyClearTerminal(self):
        sendSysCommand(self.puttyHwnd,0x70,0x01d20072)
        sendSysCommand(self.puttyHwnd,0x70,0x01d20072)
        
        self.PuttyClearScrollback()
        time.sleep(0.5)
        self.PuttyKey('enter')
        
        
        
    def PuttyInputCmd(self,cmdStr,interval=global_GeneralInputInterval,waitAfterFinish=global_WaitAfterInputFinish):
        #cmdStr += '\n'
        print (">>>" + cmdStr)
        self.PuttyInputString(cmdStr,interval,waitAfterFinish)
        self.PuttyKey('enter')
        
    def PuttyInputString(self,theString,interval=global_GeneralInputInterval,waitAfterFinish=global_WaitAfterInputFinish):
        inputString(self.puttyHwnd,theString,interval)
        time.sleep(waitAfterFinish)
        
        
    def PuttyCtrlShiftDel(self):        
        keyBoardActToWindow(self.puttyHwnd,keyAction="down",wParam=0x11,lParam=0x01d0001)    #Ctrl  
        keyBoardActToWindow(self.puttyHwnd,keyAction="down",wParam=0x12,lParam=0x20380001)   #Alt  
        keyBoardActToWindow(self.puttyHwnd,keyAction="down",wParam=0x2e,lParam=0x01530001)   #Del
        
    def PuttyKey(self,key,times=1,interval=0):
        for i in range(times):
            if key=="arrow_down":
                #print 'simulate arrow_down'
                keyBoardActToWindow(self.puttyHwnd,keyAction="down",wParam=0x28,lParam=0x1500001)
                
            elif key=="arrow_up":
                #print 'simulate arrow_up'
                keyBoardActToWindow(self.puttyHwnd,keyAction="down",wParam=0x26,lParam=0x1500001)
                
            elif key=="enter":
                #print 'simulate enter'
                keyBoardActToWindow(self.puttyHwnd,keyAction="down",wParam=0x0d,lParam=0x1500001)
                
            elif key=="delete":
                #print 'simulate delete'
                keyBoardActToWindow(self.puttyHwnd,keyAction="down",wParam=0x2e,lParam=0x1500001)
                
                
            elif key=="tab":
                keyBoardActToWindow(self.puttyHwnd,keyAction="down",wParam=9,lParam=0x1500001)
                
            elif key=="F12":
                keyBoardActToWindow(self.puttyHwnd,keyAction="down",wParam=123,lParam=0x1500001)
                
            elif key=="pageUp":
                keyBoardActToWindow(self.puttyHwnd,keyAction="down",wParam=33,lParam=0x1500001)
                
            elif key=="pageDown":
                keyBoardActToWindow(self.puttyHwnd,keyAction="down",wParam=34,lParam=0x1500001)
                
            elif key=="ESC":
                #print 'simulate esc'
                keyBoardActToWindow(self.puttyHwnd,keyAction="down",wParam=0x1B,lParam=0x10001)
                keyBoardActToWindow(self.puttyHwnd,keyAction="up",wParam=0x1B,lParam=0xc0010001)
#                time.sleep(0.3)
#                #print 'simulate shift down'
#                keyBoardActToWindow(self.puttyHwnd,keyAction="down",wParam=0x10,lParam=0x360001)
                
#                keyBoardActToWindow(self.puttyHwnd,keyAction="down",wParam=0x39,lParam=0xa0001)
#                keyBoardActToWindow(self.puttyHwnd,keyAction="up",wParam=0x39,lParam=0xc00a0001)
#                
#                
#                keyBoardActToWindow(self.puttyHwnd,keyAction="up",wParam=0x10,lParam=0xc0360001)
                
            
            time.sleep(interval)
        
    def getSharedMemText(self):        
        
        self.sharedMemMap.seek(0)
        sizeBytes = self.sharedMemMap.read(SHARED_MEM_LEN_SIZE)
        len =  struct.unpack("@i", sizeBytes)[0]
        
        #print '%s bytes in shared memory' %len
        
        return self.sharedMemMap.read(len)
        
            
        
    def PuttyGetScreenText(self,charcoding='utf8'):  
        if not isWindowExisting(self.puttyHwnd) :
            raise Exception('putty window closed !!')
             
        sendSysCommand(self.puttyHwnd,0x210,0x0166009e)
        time.sleep(0.2)
        screenText = self.getSharedMemText().decode(charcoding)
        return screenText
    
    
    def PuttyClose(self):     
        if not isWindowExisting(self.puttyHwnd) :
            self.thisLogger.info("ask putty to close it self, but its window hwnd %s does not exist!!" % self.puttyHwnd)
            self.killSelf()
            return
        
        sendSysCommand(self.puttyHwnd,0xf060,0x01e80172)
        time.sleep(1)
        self.killSelf()
        
        
    def _hexDump(self,info, raw):
        
        
        s = info + ':\n'
        for i in range(0,len(raw),16):
            l = "%04x " % i
            for j in range(i,i+16):
                if (j % 4)==0:
                    l += " "
                if j<len(raw):
                    l += "%02x" % ord(raw[j])
                else:
                    l += '  '
            l += "     "
            for j in range(i,min(i+16,len(raw))):
                b = ord(raw[j])
                if b>=32 and b<127:
                    l += raw[j]
                else:
                    l += '.'
            s += l + '\n'
        
        fh = open("tmpDebug",'a')
        fh.write(s)
        fh.close()
        
    def displayTimeOut(self,elapsedTime):               
        sys.stdout.write (chr(13))
        sys.stdout.write ("%d seconds elapsed." % elapsedTime)    
        
    
    def logCurrentPuttyScreen(self):
                    
        self.thisLogger.info('\n\n################################  The Putty Screen ################################ \n%s\n#################################################################################### \n\n' % self.PuttyGetScreenText())
    
       
    def PuttyWaitForOutputInCurrentScreenEx(self,expectedStr,timeout=60,isRegularExpress=False):
        
        self.thisLogger.info('\n\n--->wait for the following string come out on screen in %s seconds... \n\n%s\n' %(timeout,expectedStr))
        entryTime = time.time()
        while True:
            bufferText = self.PuttyGetScreenText()
            if os.path.exists('debug'):
                self._hexDump('----------- bufferText ----------',bufferText)
                self._hexDump('----------- expectedStr ----------',expectedStr)
            
            if isRegularExpress:
                ret = re.search(expectedStr,bufferText)
                if ret != None: #found
                    self.thisLogger.info("<---get it.\n")   
                    return True
            else:        
                if expectedStr in bufferText:
                    self.thisLogger.info("<---get it.\n")   
                    return True
                
            curTime = time.time()
            elapsedTime = curTime-entryTime
            if elapsedTime >= timeout:
                print ("<---no `%s`"    % expectedStr)
                
                self.logCurrentPuttyScreen()
                raise Exception("in %s seconds, no `%s`"    % (timeout,expectedStr))
            else:                
                self.displayTimeOut(elapsedTime)
            
            #self.PuttyClearScrollback()
            time.sleep(0.5)             
            
    def PuttyWaitForOutputInCurrentScreen(self,expectedStr,timeout=60,isRegularExpress=False,needPressEnterKey=False):
        
        self.thisLogger.info('\n\n--->wait for the following string come out on screen in %s seconds... \n\n%s\n' %(timeout,expectedStr))
        entryTime = time.time()
        while True:
            bufferText = self.PuttyGetScreenText()
            if os.path.exists('debug'):
                self._hexDump('----------- bufferText ----------',bufferText)
                self._hexDump('----------- expectedStr ----------',expectedStr)
            
            if isRegularExpress:
                ret = re.search(expectedStr,bufferText)
                if ret != None: #found
                    self.thisLogger.info("<---get it.\n")   
                    return True
            else:        
                if expectedStr in bufferText:
                    self.thisLogger.info("<---get it.\n")   
                    return True
                
            curTime = time.time()
            elapsedTime = curTime-entryTime
            if elapsedTime >= timeout:
                print ("<---no `%s`"    % expectedStr)
                
                #self.logCurrentPuttyScreen()
                return False
            else:                
                self.displayTimeOut(elapsedTime)
            
            #self.PuttyClearScrollback()
            time.sleep(0.5) 
            if needPressEnterKey:
                #press enter every 5 seconds
                if int(elapsedTime) % 5 == 0:
                    self.PuttyKey("enter")
            

            
    def PuttyWaitForListedOutputInCurrentScreenEx(self,expectedStrList,timeout=60,isRegularExpress=False):
        
        self.thisLogger.info('\n\n--->wait for any of the following string come out on screen in %s seconds... \n\n%s\n' %(timeout,expectedStrList))
        entryTime = time.time()
        while True:
            bufferText = self.PuttyGetScreenText()
            
            if isRegularExpress:
                for expectedStr in expectedStrList:
                    ret = re.search(expectedStr,bufferText)
                    if ret != None: #found
                        self.thisLogger.info("<---get `%s`.\n" % expectedStr)   
                        return expectedStr
            else:        
                for expectedStr in expectedStrList:
                    if expectedStr in bufferText:
                        self.thisLogger.info("<---get `%s`.\n" % expectedStr)   
                        return expectedStr
                
            curTime = time.time()
            elapsedTime = curTime-entryTime
            if elapsedTime >= timeout:
                print ("<---no `%s`"    % expectedStr)
                
                self.logCurrentPuttyScreen()
                raise Exception("in %s seconds, no `%s`"    % (timeout,expectedStrList))
            else:                
                self.displayTimeOut(elapsedTime)
            
            #self.PuttyClearScrollback()
            time.sleep(0.5) 
            
    def PuttyWaitForListedOutputInCurrentScreen(self,expectedStrList,timeout=60,isRegularExpress=False):
        
        self.thisLogger.info('\n\n--->wait for any of the following string come out on screen in %s seconds... \n\n%s\n' %(timeout,expectedStrList))
        entryTime = time.time()
        while True:
            bufferText = self.PuttyGetScreenText()
            
            if isRegularExpress:
                for expectedStr in expectedStrList:
                    ret = re.search(expectedStr,bufferText)
                    if ret != None: #found
                        self.thisLogger.info("<---get `%s`.\n" % expectedStr)    
                        return True,expectedStr
            else:        
                for expectedStr in expectedStrList:
                    if expectedStr in bufferText:
                        self.thisLogger.info("<---get `%s`.\n" % expectedStr)   
                        return True,expectedStr
                
            curTime = time.time()
            elapsedTime = curTime-entryTime
            if elapsedTime >= timeout:
                print ("<---no `%s`"    % expectedStr)
                
                #self.logCurrentPuttyScreen()
                return False,''
            else:                
                self.displayTimeOut(elapsedTime)
            
            #self.PuttyClearScrollback()
            time.sleep(0.5) 
    
    def _specialStripRight(self,srcStr):
        totalLen = len(srcStr)
        idx = totalLen - 1
        while idx >= 0:
            if ord(srcStr[idx]) <= 0x20: # it is a invisible char
                idx -= 1
            else:
                break
        
        return srcStr[:idx+1]
   
    def PuttyWaitForOutputInCurrentScreenEndwithEx(self,expectedStr,timeout=60,isRegularExpress=False):
        self.thisLogger.info( '\n\n--->wait for the following come out at end of screen in %s seconds... \n\n%s\n' %(timeout,expectedStr))
        entryTime = time.time()
        
        #expectedStr += "\n" #putty alway has \x0d\x0a\x00 at end of clipboard
        
        while True:     
            
            curTime = time.time()
            elapsedTime = curTime-entryTime
            if elapsedTime >= timeout:
                print ("<---no `%s` at the end of screen\n"    % expectedStr)
                self.logCurrentPuttyScreen()
                raise Exception("in %s seconds, no `%s`"    % (timeout,expectedStr))
            else:                
                self.displayTimeOut(elapsedTime)
                
                
                
            
            bufferText = self.PuttyGetScreenText()
            bufferText = self._specialStripRight(bufferText)
            
            
            if os.path.exists('debug'):
                self._hexDump('----------- bufferText ----------',bufferText)
                self._hexDump('----------- expectedStr ----------',expectedStr)
                
            if isRegularExpress:
                ret = re.search(expectedStr,bufferText)
                if ret != None: #found
                    self.thisLogger.info("<---get it.\n")  
                    return True
                
            
            else:     
                
                if  bufferText.endswith(expectedStr):
                    self.thisLogger.info("<---get it.\n")   
                    return True
            
            #self.PuttyClearScrollback()
            time.sleep(0.5)              
            
    def PuttyWaitForOutputInCurrentScreenEndwith(self,expectedStr,timeout=60,isRegularExpress=False):
        self.thisLogger.info( '\n\n--->wait for the following come out at end of screen in %s seconds... \n\n%s\n' %(timeout,expectedStr))
        entryTime = time.time()
        
        #expectedStr += "\n" #putty alway has \x0d\x0a\x00 at end of clipboard
        
        while True:     
            
            curTime = time.time()
            elapsedTime = curTime-entryTime
            if elapsedTime >= timeout:
                print ("<---no `%s` at the end of screen\n"    % expectedStr)
                #self.logCurrentPuttyScreen()
                return False
            else:                
                self.displayTimeOut(elapsedTime)
                
                
                
            
            bufferText = self.PuttyGetScreenText()
            bufferText = self._specialStripRight(bufferText)
            
            
            if os.path.exists('debug'):
                self._hexDump('----------- bufferText ----------',bufferText)
                self._hexDump('----------- expectedStr ----------',expectedStr)
                
            if isRegularExpress:
                ret = re.search(expectedStr,bufferText)
                if ret != None: #found
                    self.thisLogger.info("<---get it.\n")  
                    return True
                
            
            else:     
                
                if  bufferText.endswith(expectedStr):
                    self.thisLogger.info("<---get it.\n")   
                    return True
            
            #self.PuttyClearScrollback()
            time.sleep(0.5)     
    
            
            
    
            
    def PuttyIsCurrentScreenEndwith(self,expectedStr):
        self.thisLogger.info( '\n\n--->check is the following string at end of screen ... \n\n%s\n' %expectedStr)
        
        #expectedStr += "\n" #putty alway has \x0d\x0a\x00 at end 
#        expectedStr += '\x0d\x0a\x00'
        
        bufferText = self.PuttyGetScreenText()
        bufferText = self._specialStripRight(bufferText)
        
        
        if os.path.exists('debug'):
            self._hexDump('----------- bufferText ----------',bufferText)
            self._hexDump('----------- expectedStr ----------',expectedStr)
                
        
        if bufferText.endswith(expectedStr):
            self.thisLogger.info("<---get it.\n")   
            return True
        else:
            print ("<---no that!\n")                      
            #self.thisLogger.info('\n\n################################  The Putty Screen ################################ \n\n%s\n\n######################################################################################### \n\n' % self.PuttyGetScreenText())
            return False         
            
            
    def PuttyWaitForOutputInCurrentScreenEndwith_old(self,expectedStr,timeout=60,isRegularExpress=False):
        print ('\n--->wait for the following come out at end of screen in %s seconds... \n\n%s\n' %(timeout,expectedStr))
        entryTime = time.time()
        
        #expectedStr += "\n" #putty alway has \n at end of clipboard
        lenOfExpectedStr = len(expectedStr)+5
        while True:            
            curTime = time.time()
            if curTime-entryTime >= timeout:
                print ("<---no `%s`\n"    % expectedStr)
                return False
            
            bufferText = self.PuttyGetScreenText()
                
            if len(bufferText) < lenOfExpectedStr:
                time.sleep(0.5)        
                continue
            
            bufferText = bufferText[0-lenOfExpectedStr:]
            
            if os.path.exists('debug'):
                self._hexDump('----------- bufferText ----------',bufferText)
                self._hexDump('----------- expectedStr ----------',expectedStr)
                
#            print expectedStr
#            print bufferText
#            print '--------------\n'
            if isRegularExpress:
                ret = re.search(expectedStr,bufferText)
                if ret != None: #found
                    return True
            else:       
                if expectedStr in bufferText:
                    print ("<---get it.\n")   
                    return True
            
            #self.PuttyClearScrollback()
            time.sleep(0.5)
            
            

            
    def PuttyIsCurrentScreenEndwith_old(self,expectedStr):
        print ('\n--->check is the following string at end of screen ... \n\n%s\n' %expectedStr)
        entryTime = time.time()
        
        #expectedStr += "\n" #putty alway has \n at end of clipboard
        lenOfExpectedStr = len(expectedStr)+5
        
        bufferText = self.PuttyGetScreenText()
        
        
        if os.path.exists('debug'):
            self._hexDump('----------- bufferText ----------',bufferText)
            self._hexDump('----------- expectedStr ----------',expectedStr)
                
        if len(bufferText) < lenOfExpectedStr:
            print ("<---no that!\n")
            return False
        
        bufferText = bufferText[0-lenOfExpectedStr:]
        if expectedStr in bufferText:
            print ("<---get it.\n")   
            return True
        else:
            print ("<---no that!\n")
            return False
                  
 

            
    def PuttyWaitForOutputInCurrentScreenEndwith_old2(self,expectedStr,timeout=60,isRegularExpress=False):
        self.thisLogger.info( '\n\n--->wait for the following come out at end of screen in %s seconds... \n\n%s\n' %(timeout,expectedStr))
        entryTime = time.time()
        
        #expectedStr += "\n" #putty alway has \x0d\x0a\x00 at end of clipboard
        expectedStr += '\x0d\x0a\x00'
#        lenOfExpectedStr = len(expectedStr)
        while True:     
            
            curTime = time.time()
            elapsedTime = curTime-entryTime
            if elapsedTime >= timeout:
                print ("<---no `%s` at the end of screen\n"    % expectedStr)
                #self.logCurrentPuttyScreen()
                return False
            else:                
                self.displayTimeOut(elapsedTime)
                
                
                
            
            bufferText = self.PuttyGetScreenText()
            
            
            if os.path.exists('debug'):
                self._hexDump('----------- bufferText ----------',bufferText)
                self._hexDump('----------- expectedStr ----------',expectedStr)
                
            if isRegularExpress:
                ret = re.search(expectedStr,bufferText)
                if ret != None: #found
                    print ("<---get it.\n")   
                    return True
                
            
            else:     
                
                if  bufferText.endswith(expectedStr):
                    print ("<---get it.\n")   
                    return True
            
            self.PuttyClearScrollback()
            time.sleep(0.5)       




    def bringPuttyWndToToppest(self):
        '''
        set the window to the toppest
        '''
        win32gui.SetForegroundWindow(self.puttyHwnd)



    def flashPuttyWnd(self):
        '''
        set the window to the toppest
        '''
#         self.bringPuttyWndToToppest()
        win32gui.FlashWindowEx(self.puttyHwnd,
                               win32con.FLASHW_ALL|win32con.FLASHW_TIMERNOFG,
                               20,
                               200)


class EnhancedPuttyAgent(PuttyAgent):


    def __init__(self,machine,title=None,checkLoginReady=True):
        if title == None:
            title = machine.ip+" - 白月黑羽定制"

        remoteIP = machine.ip
        username = machine.user
        passwd   = machine.passwd
        port     = machine.port
        sharedMemName="putty"+str(time.time())

        thisLogger = Logger.getLogger("putty.log", toFile=False,toScreen=True)
        PuttyAgent.__init__(self, remoteIP, username, passwd, 
        title, sharedMemName, thisLogger,port,
        checkLoginReady=checkLoginReady)

        # readyMark = '[(<ready>)]'
        # #inputStr = "echo '%s' \n" % readyMark
        # inputStr = "%s" % readyMark
        #
        # for i in range(30):
        #     self.PuttyInputString(inputStr)
        #
        #     screenText = self.PuttyGetScreenText()
        #     if readyMark in screenText:
        #         self.PuttyKey('enter')
        #         self.checkNeedAutoSwitch(machine)
        #         return
        #
        # raise Exception("Putty terminal could not enter Shell correctly!!!!")

        self.checkNeedAutoSwitch(machine)

    def checkNeedAutoSwitch(self,machine):
        if machine.isAutoSwitchToRoot:
            self.PuttyClearTerminal()
            self.PuttyInputString("su -\n")
            self.PuttyWaitForOutputInCurrentScreenEx("Password:",2)
            self.PuttyInputString("%s\n" % machine.rootPassword)
            time.sleep(1)


    # def initOld(self,machine,title=None,successPrompt='->'):
    #     if title == None:
    #         title = machine.ip
    #
    #     remoteIP = machine.ip
    #     username = machine.user
    #     passwd   = machine.passwd
    #     sharedMemName="putty"+str(time.time())
    #
    #     thisLogger = Logger.getLogger("putty.log", toFile=False,toScreen=True)
    #     PuttyAgent.__init__(self, remoteIP, username, passwd, title, sharedMemName, thisLogger)
    #
    #     isGet = False
    #     for i in range(60):
    #         ret = self.PuttyIsCurrentScreenEndwith(successPrompt)
    #         if not ret:
    #             self.PuttyKey( 'enter')
    #             time.sleep(2)
    #         else:
    #             isGet = True
    #             break
    #
    #
    #     if not isGet:
    #         self.logCurrentPuttyScreen()
    #         raise Exception('screen text not end with `%s` !!' % successPrompt)



class LinuxPuttyAgent(EnhancedPuttyAgent):
    
    def __init__(self,machine,title=None,checkLoginReady=True):
        EnhancedPuttyAgent.__init__(self,machine,title,
                        checkLoginReady=checkLoginReady)


    def PuttyLinuxExecCmd(self,intent='',cmdStr ='',timeout=60,checkResult=False):
        
        print ("\n*** %s " % intent)
        
        self.PuttyClearTerminal()
        self.PuttyInputCmd("\n")
        cmdStr = cmdStr +''' ;echo "<Operation result=$?>"'''
        self.PuttyInputCmd(cmdStr)
        
        self.PuttyWaitForOutputInCurrentScreenEx("<Operation result=\d+>",timeout=timeout,isRegularExpress=True)
        
        
        if checkResult:
            screenText = self.PuttyGetScreenText()
            if "<Operation result=0>" not in screenText:
                raise Exception("Execute Linux command return error!!")
       
            
        #self.logCurrentPuttyScreen()
        
        
        

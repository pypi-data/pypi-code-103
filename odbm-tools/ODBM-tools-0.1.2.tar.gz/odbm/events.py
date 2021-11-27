import roadrunner as rr

def addEvent(label, event, trigger, regenerate = False):
    '''
    User passes in, for example:
    'at (time > 10): X = sin(t)'
    trigger is left of ':': t = 10
    event is right of ':': X = sin(t)


    Examples from Tellurium:
        at sin(2*pi*time/period) >  0, t0=false: UpDown = 1
        at sin(2*pi*time/period) <= 0, t0=false: UpDown = 0
        at (x>5): y=3, x=r+2;
        E1: at(x>=5): y=3, x=r+2;

    event can be a list of events 
    '''

    #To-do:
        # check uniqueness of event label
    rr.addEvent(eid = label, False, trigger, regenerate)
    rr.

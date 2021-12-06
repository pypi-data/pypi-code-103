from device import Device
    

class Glove(Device):
    """A class for Cyberglove recordings. This is a base class, since the 
    Cybergloves have different numbers of sensors/sensor layouts this will only
    hold functions common to both. 

    Arguments:
        Device {[type]} -- [description]
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def record(self):
        pass
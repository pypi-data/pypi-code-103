from math import sqrt
import matplotlib as mpl


class square:
    def __init__(self, adl):
        self.s = f"""// Geom
        ad := rect(ad_size,ad_size)
        ring := rect(ad_size + ring_size * 2,ad_size + ring_size * 2)
        """


class diamond:
    def __init__(self, adl):
        self.s = f"""// Geom
        ad := rect(ad_size,ad_size).RotZ(pi/4)
        ring := rect(ad_size + ring_size * 2,ad_size + ring_size * 2).RotZ(pi/4)
        """


class circle:
    def __init__(self, adl):
        self.s = f"""// Geom
        ad := circle(ad_size)
        ring := circle(ad_size + ring_size * 2)
        """


class triangle:
    def __init__(self, adl):
        self.s = f"""// Geom
        ad := triangle(ad_size)
        ring := triangle(ad_size + ring_size * 2)
        """

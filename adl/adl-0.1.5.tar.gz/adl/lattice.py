import math


def add_coordinates(trs):
    for i, tr in enumerate(trs):
        if i == 0:
            rings = f"rings := ring.{tr}"
            ads = f"ads := ad.{tr}"
            vortex = f"m.setInShape(ring.{tr},vortex(1, 1).{tr})"
        else:
            rings += f".add(ring.{tr})"
            ads += f".add(ad.{tr})"
            vortex += f"\n\tm.setInShape(ring.{tr},vortex(1, 1).{tr})"
    s = f"""{rings}
        {ads}
        {vortex}
    """
    return s


class square_lattice:
    def __init__(self, parms):
        self.coordinates = [(0, 0)]
        self.xsize = parms.lattice_param
        self.ysize = parms.lattice_param
        self.s = f"""
        rings := ring
        ads := ad
        m.setinshape(ring,vortex(1,1))
        """


class rectangular_lattice:
    def __init__(self, parms):
        if parms.lattice_param2 == 0:
            raise ValueError("lattice_param2 is missing for the rectangular lattice.")
        self.coordinates = [(0, 0)]
        self.xsize = parms.lattice_param
        self.ysize = parms.lattice_param2
        self.s = f"""
        rings := ring
        ads := ad
        m.setinshape(ring,vortex(1,1))
        """


class hexagonal_lattice:
    def __init__(self, parms):
        self.xsize = parms.lattice_param
        self.ysize = 2 * parms.lattice_param * math.sin(60 * math.pi / 180)
        self.s = f"""
        a1 := lattice_param/4
        a2 := lattice_param * sqrt(3)/4
        """
        trs = [
            "transl(a1,a2,0)",
            "transl(-a1,-a2,0)",
            "transl(3*a1,-a2,0)",
            "transl(-3*a1,a2,0)",
        ]
        self.s += add_coordinates(trs)


class honeycomb_lattice:
    def __init__(self, parms):
        self.xsize = 3 * parms.lattice_param
        self.ysize = 2 * parms.lattice_param * math.sin(60 * math.pi / 180)
        self.s = f"""
        a1 := lattice_param
        a2 := lattice_param * sqrt(3)/2
        """
        trs = [
            "transl(-a1/2,-a2,0)",
            "transl(a1/2,-a2,0)",
            "transl(-a1,0,0)",
            "transl(a1,0,0)",
            "transl(-a1/2,a2,0)",
            "transl(a1/2,a2,0)",
        ]
        self.s += add_coordinates(trs)


class octagonal_lattice:
    def __init__(self, parms):
        self.xsize = parms.lattice_param * (1 + math.sqrt(2))
        self.ysize = parms.lattice_param * (1 + math.sqrt(2))
        self.s = f"""
        // Lattice
        a1 := lattice_param / 2 + lattice_param / sqrt(2)
        a2 := lattice_param / 2
        """
        trs = [
            "transl(a1,a2,0)",
            "transl(-a1,a2,0)",
            "transl(-a1,-a2,0)",
            "transl(a1,-a2,0)",
            "transl(a2,a1,0)",
            "transl(-a2,a1,0)",
            "transl(-a2,-a1,0)",
            "transl(a2,-a1,0)",
        ]
        self.s += add_coordinates(trs)

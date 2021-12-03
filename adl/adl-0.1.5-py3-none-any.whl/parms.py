from dataclasses import dataclass


@dataclass
class parms:
    # Needed
    lattice: str
    antidot: str
    lattice_param: int
    ad_size: int
    ring: int
    lattice_param2: int = 0
    ad_size2: int = 0
    # Mesh
    dx: int = 0.75
    dy: int = 0.75
    dz: int = 13.2
    PBC: int = 32
    edgesmooth: int = 3
    # Material
    msat: str = "810e3"
    aex: str = "13e-12"
    ku1: str = "453195"
    anisu: str = "vector(0,0,1)"
    alpha: str = "1e-7"
    gammall: str = "187e9"
    # Static
    m: str = "uniform(1e-5, 1e-5, 1)"
    angle: str = "0.0001"
    B0: str = "0.223"
    maxerr_s: str = "4e-5"
    minimizerstop: str = "1e-7"
    relaxtorquethreshold: str = "1e-5"
    # Dynamics
    mindt: str = "1e-14"
    maxdt: str = "1.42e-12"
    maxerr_d: str = "1e-7"
    solver: int = 5
    amps: str = "5e-3"
    f_cut: str = "20e9"
    t0: str = "t + 10/f_cut"
    t_sampl: str = "0.5 / (f_cut * 1.5)"
    Bmask: str = ""
    autosave: str = "autosave(m,t_sampl)"
    trun: str = "500"
    # Overrides
    mesh: str = ""
    material: str = ""
    static: str = ""
    dynamics: str = ""

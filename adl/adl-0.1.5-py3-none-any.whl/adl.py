import inspect
import os

from matplotlib import pyplot as plt
import matplotlib as mpl
import numpy as np

from . import antidot, lattice, parms

antidots = {
    "square": antidot.square,
    "circle": antidot.circle,
    "triangle": antidot.triangle,
    "diamond": antidot.diamond,
    "squ": antidot.square,
    "cir": antidot.circle,
    "tri": antidot.triangle,
    "dia": antidot.diamond,
}
lattices = {
    "square": lattice.square_lattice,
    "hexagonal": lattice.hexagonal_lattice,
    "rectangular": lattice.rectangular_lattice,
    "honeycomb": lattice.honeycomb_lattice,
    "octagonal": lattice.octagonal_lattice,
    "squ": lattice.square_lattice,
    "hex": lattice.hexagonal_lattice,
    "rec": lattice.rectangular_lattice,
    "hon": lattice.honeycomb_lattice,
    "oct": lattice.octagonal_lattice,
}


class adl:
    def __init__(self, parms: parms):
        self._lattice = lattices[parms.lattice](parms)
        self._s = ""
        parms = self.add_dimensions(parms)
        self._antidot = antidots[parms.antidot](parms)
        self.add_mesh(parms)
        self.add_material(parms)
        self.add_geom(parms)
        self.add_static(parms)
        self.add_dynamics(parms)

    def add_dimensions(self, parms):
        parms.Nx = int(self._lattice.xsize / parms.dx)
        parms.Ny = int(self._lattice.ysize / parms.dy)
        parms.Nz = 1
        new_nx = parms.Nx - parms.Nx % 10
        parms.dx = parms.Nx / new_nx * parms.dx
        parms.Nx = new_nx
        new_ny = parms.Ny - parms.Ny % 10
        parms.dy = parms.Ny / new_ny * parms.dy
        parms.Ny = new_ny
        return parms

    def add_mesh(self, parms):
        if parms.mesh == "":
            self._s += f"""
        lattice_param := {parms.lattice_param}e-9
        ring_size := {parms.ring}e-9
        ad_size := {parms.ad_size}e-9"""
            if parms.lattice == "rectangular":
                self._s += f"""
        lattice_param2 := {parms.lattice_param2}e-9"""
            if parms.antidot == "diamond":
                self._s += f"""
        ad_size2 := {parms.ad_size2}e-9"""

            self._s += f"""
        PBC := {parms.PBC}
        Tx := {parms.Nx*parms.dx:.5f}e-9
        Ty := {parms.Ny*parms.dy:.5f}e-9
        Tz := {parms.Nz*parms.dz:.5f}e-9
        Nx := {parms.Nx}
        Ny := {parms.Ny}
        Nz := {parms.Nz}
        setgridsize(Nx,Ny,Nz)
        setcellsize(Tx/Nx,Ty/dy,Tz/dz)
        setpbc(PBC,PBC,0)
        edgesmooth={parms.edgesmooth}
            """
        else:
            self._s += parms.mesh

    def add_material(self, parms):
        if parms.material == "":
            self._s += f"""
        // CoPd film
        msat = {parms.msat}
        aex = {parms.aex}
        ku1 = {parms.ku1}
        anisu = {parms.anisu}
        alpha = {parms.alpha}
        gammall = {parms.gammall}

        """
        else:
            self._s += parms.material

    def add_geom(self, parms):
        self._s += self._antidot.s
        self._s += self._lattice.s
        self._s += f"""
        bulk := universe().sub(rings).sub(ads)
        m.setInShape(bulk,uniform(0,0,1))
        defregion(201,rings)
        defregion(202,ads)
        defregion(203,bulk)
        ku1.setregion(201,0)
        setgeom(bulk.add(rings).sub(ads))
        """

    def add_static(self, parms):
        if parms.static == "":
            self._s += f"""
        // Static
        angle := {parms.angle} * pi / 180
        B0 := {parms.B0}
        B_ext = vector(B0*sin(angle), 0, B0*cos(angle))

        // Relaxation
        maxerr = {parms.maxerr_s}
        minimizerstop = {parms.minimizerstop}
        relaxtorquethreshold = {parms.relaxtorquethreshold}
        minimize()
        saveas(m,"stable")
        snapshotas(m,"stable.png")
        """
        else:
            self._s += parms.static

    def add_dynamics(self, parms):
        if parms.dynamics == "":
            self._s += f"""
        // Dynamics
        setsolver({parms.solver})
        maxdt = {parms.maxdt}
        mindt = {parms.mindt}
        maxerr = {parms.maxerr_d}
        amps:= {parms.amps}
        f_cut := {parms.f_cut}
        t_sampl := {parms.t_sampl}
        t0 := {parms.t0}
        """
            if parms.Bmask == "":
                self._s += """
        // Bmask
        grainSize  := 20e-9  // m
        randomSeed := 1234567
        maxRegion  := 30
        ext_makegrains(grainSize, maxRegion, randomSeed)
        for i:=4; i<maxRegion+4; i++{
            b:=0.1*randnorm()*1/f_cut
            B_ext.setregion(i, vector(B0*sin(angle)+amps*sinc(2*pi*f_cut*(t-t0+b)),amps*sinc(2*pi*f_cut*(t-t0+b)),B0*cos(angle)))
        }
        defregion(201,rings)
        ku1.setregion(201,0)
        """
            else:
                self._s += """
        // Bmask"""
                self._s += parms.Bmask
            self._s += f"""
        // Saving
        run(20/f_cut)
        B_ext.RemoveExtraTerms( )
        B_ext = vector(B0*sin(angle), 0, B0*cos(angle))
        run(5/f_cut)
        t = 0
        tableadd(B_ext)
        tableautosave(t_sampl)
        {parms.autosave}
        run({parms.trun} * t_sampl)
        """
        else:
            self._s += parms.dynamics

    def save(self, path):
        import time

        self._s = inspect.cleandoc(self._s)  # removes padding
        if path[-4:] == ".mx3":
            with open(path, "w") as f:
                f.writelines(self._s)
        else:
            i = 0
            while True:
                mx3_path = f"{path}/adl_{i}.mx3"
                if not os.path.exists(mx3_path):
                    print(f"Saved as '{mx3_path}'")
                    with open(mx3_path, "w") as f:
                        f.writelines(self._s)
                    break
                i += 1

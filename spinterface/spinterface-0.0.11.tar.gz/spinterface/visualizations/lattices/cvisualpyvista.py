# -*- coding: utf-8 -*-
r"""
Module contains implementation of pyvista visualizations for spin lattices.
"""
from pathlib import Path
from spinterface.visualizations.lattices.utilities import get_colormap
import pyvista as pv
import numpy as np
from spinterface.visualizations.lattices.ivisualizer import IVisualizer
from spinterface.inputs.lattice.ILattice import ILattice
from typing import List, Tuple, Union
from spinterface.visualizations.const import SPINDEFAULT_SETTINGS, EVECDEFAULT_SETTINGS
from spinterface.inputs.lattice.const import LATT_TYPE_EVEC, LATT_TYPE_SPIN


class CVisualPyVista(IVisualizer):
    r"""
    Class for visualizing spin lattices with py vista library
    """

    def __init__(self, lattice: ILattice, tiplength: Union[float, None] = None, tipradius: Union[float, None] = None,
                 arrowscale: Union[float, None] = None, draw_background: Union[bool, None] = None,
                 cam: Union[List[Tuple[float, float, float]], None] = None,
                 cmap: str = 'hsv_spind') -> None:
        r"""
        Initializes the visualization

        Args:
            tiplength(float): geometry of arrow: tiplength
            tipradius(float): geometry of arrow: tipradius
            arrowscale(float): geometry of arrow: arrowscale
            draw_background(bool): shall i draw the background of the lattice
            camera: camera position
            cmap: string for the choice of the colormap. Defined in utilities module
        """
        super().__init__(lattice)
        self.tiplength, self.tipradius, self.arrowscale, self.drawbackground = self._load_settings(tiplength, tipradius,
                                                                                                   arrowscale,
                                                                                                   draw_background)
        self._geom = pv.Arrow(start=np.array([-self.arrowscale / 2.0, 0, 0]), tip_length=self.tiplength,
                              tip_radius=self.tipradius, scale=self.arrowscale)
        self.cam = cam
        self.cmap = get_colormap(cmap)
        self._make_plotter()

    def _load_settings(self, tl: Union[float, None], tr: Union[float, None],
                       asc: Union[float, None], dbg: Union[bool, None]) -> Tuple[float, float, float, bool]:
        r"""
        Returns:
            loads the tiplength, tipradius and arrowscale depending on the inputs and the lattice type
        """
        # Decide on loading settings
        if self.lattice.source == LATT_TYPE_SPIN:
            print(f'loading defaults for type: {LATT_TYPE_SPIN}')
            tiplength = SPINDEFAULT_SETTINGS['tiplength']
            tipradius = SPINDEFAULT_SETTINGS['tipradius']
            arrowscale = SPINDEFAULT_SETTINGS['arrowscale']
            drawbackground = SPINDEFAULT_SETTINGS['drawbackground']
        elif self.lattice.source == LATT_TYPE_EVEC:
            print(f'loading defaults for type: {LATT_TYPE_SPIN}')
            tiplength = EVECDEFAULT_SETTINGS['tiplength']
            tipradius = EVECDEFAULT_SETTINGS['tipradius']
            arrowscale = EVECDEFAULT_SETTINGS['arrowscale']
            drawbackground = EVECDEFAULT_SETTINGS['drawbackground']
        else:
            raise ValueError('Not a valid lattice source!')
        if tl is not None:
            print('Overwriting tiplength setting with user input')
            tiplength = tl
        if tr is not None:
            print('Overwriting tiplradius setting with user input')
            tiplength = tr
        if asc is not None:
            print('Overwriting arrowscale setting with user input')
            tiplength = asc
        if dbg is not None:
            print('Overwriting drawbackground setting with user input')
            drawbackground = dbg
        return tiplength, tipradius, arrowscale, drawbackground

    def _make_plotter(self, offscreen: bool = False):
        r"""
        Creates the plotter. The plotter will be recreated when saving the image
        """
        self.plotter = pv.Plotter(off_screen=offscreen, lighting='three lights')
        self._configureplotter()
        self.plotter.camera_position = self.cam
        plotpoints, plotspins, plotsz = self._make_plot_points()
        self.PolyData = pv.PolyData(plotpoints)
        self.PolyData.vectors = plotspins
        self.PolyData['oop'] = plotsz
        if self.lattice.source == LATT_TYPE_SPIN:
            self.Glyphs = self.PolyData.glyph(orient=True, scale=True, geom=self._geom)
        elif self.lattice.source == LATT_TYPE_EVEC:
            self.Glyphs = self.PolyData.glyph(orient=True, scale=True, geom=self._geom)
        self.plotter.add_mesh(self.Glyphs, show_scalar_bar=False, cmap=self.cmap)
        if self.drawbackground:
            self._draw_background()

    def _draw_background(self) -> None:
        r"""
        Draws the background of the lattice
        """
        for layer in range(self.lattice.nlayer):
            magstruct = self.lattice.getlayer_by_idx(layer)
            points = magstruct[:, :3]
            points_poly = pv.PolyData(points)
            surface = points_poly.delaunay_2d()
            self.plotter.add_mesh(surface, show_edges=True, opacity=0.5)

    def _make_plot_points(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        r"""
        We always want to norm the colormap in the interval -1, 1 even we have a lattice which spins have only SZ comp.
        in the interval e.g. (1,0.5). There is now easy way to do this with pyvista since there is no interface for nor-
        malizing. Therefore, we add an invisible point in the center of the lattice here.

        Returns:
            the points, the spins and the sz components
        """
        plotpoints = np.append(self.lattice.points, np.array([self.lattice.midpoint, self.lattice.midpoint]), axis=0)
        plotspins = np.append(self.lattice.spins, np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]), axis=0)
        if self.lattice.source == LATT_TYPE_SPIN:
            plotsz = np.append(self.lattice.SZ, np.array([1.0, -1.0]))
        elif self.lattice.source == LATT_TYPE_EVEC:
            ez = np.array([0.0, 0.0, 1.0])
            plotsz = [np.dot(spin / np.linalg.norm(spin), ez) for spin in self.lattice.spins]
            plotsz = np.append(plotsz, np.array([1.0, -1.0]))
        else:
            raise ValueError('Lattice type not supported.')
        return plotpoints, plotspins, plotsz

    def _configureplotter(self) -> None:
        r"""
        Configures the plotter object
        """
        pv.set_plot_theme("ParaView")
        pv.rcParams['transparent_background'] = True
        self.plotter.set_background('white')

        def cam() -> None:
            print('Camera postion: ', self.plotter.camera_position)

        self.plotter.add_key_event('c', cam)

    def show(self) -> None:
        r"""
        Shows the plotter
        """
        print('Look what you have done.......')
        print('to get current cam-position press key c')
        self.plotter.show()

    def __call__(self, outpath: Path = Path.cwd() / 'spin.png') -> None:
        r"""
        Saves the image to a file

        Args:
            outpath(Path): output path for the png image created.
        """
        self._make_plotter(offscreen=True)
        self.plotter.window_size = [4000, 4000]
        self.plotter.screenshot(str(outpath.stem))

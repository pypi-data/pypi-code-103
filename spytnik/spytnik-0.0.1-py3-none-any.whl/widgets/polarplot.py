import numpy as np
import pyqtgraph as pg


class PolarPlotWidget:
    def __init__(self, parent=None):
        self.plot = self._create(parent)
        self.pen = pg.mkPen("b", width=5)
        self.curves = []

    def add_curve(self, az, el):
        theta = (90 - az) * 2 * np.pi / 360
        radius = 90 - el

        # Transform to cartesian and plot
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)

        p = self.plot.plot(x, y, pen=self.pen)

        self.curves.append(p)

    def clean(self):
        for c in self.curves:
            self.plot.removeItem(c)
        self.curves = []

    def _create(self, parent):
        p = pg.PlotWidget(parent)
        p.setMouseEnabled(x=False, y=False)
        p.setMinimumSize(240, 240)
        p.setAspectLocked()
        p.setLimits(xMin=-90, xMax=90)
        p.getPlotItem().hideAxis("bottom")
        p.getPlotItem().hideAxis("left")

        p.addLine(x=0, pen=0.2)
        p.addLine(y=0, pen=0.2)

        for r in [30, 60, 90]:
            circle = pg.QtGui.QGraphicsEllipseItem(-r, -r, r * 2, r * 2)
            circle.setPen(pg.mkPen(0.2))
            p.addItem(circle)

        return p

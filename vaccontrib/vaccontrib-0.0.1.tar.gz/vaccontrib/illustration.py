"""
Helper classes and functions do illustrate contribution matrices
as segments of circles.
"""
# coding: utf-8


import matplotlib.pyplot as pl

from shapely.geometry import Point, LineString, Polygon, MultiPolygon
from shapely.affinity import translate

import numpy as np
from scipy.optimize import root

import bfmplot as bp
import matplotlib.pyplot as pl

from shapely.geometry import CAP_STYLE, JOIN_STYLE

_BASE_CIRCLE_RESOLUTION = 64

class CircleCaps():

    def __init__(self,r,h,w=1/10,circle_resolution=_BASE_CIRCLE_RESOLUTION):
        #self.y = sorted([amount0, amount1],key=lambda x:-x)
        self.r = r
        self.w = w
        self.h = h
        self.circle_resolution = circle_resolution
        self.compute()

    def compute(self):
        point = Point(0,0)
        self.circle = point.buffer(self.r,resolution=self.circle_resolution)
        r = self.r
        h = self.h
        w = self.w
        box0 = Polygon([(-2*r,h+w), (2*r,h+w), (2*r,h+w+2*r),(-2*r,h+w+2*r)])
        box1 = Polygon([(-2*r,h), (2*r,h), (2*r,h-2*r),(-2*r,h-2*r)])
        self.cap0 = self.circle.intersection(box0)
        self.cap1 = self.circle.intersection(box1)

        filtered_polygons = list(filter(lambda x: x.area > 0,  [self.cap0,self.cap1]))
        self.all = MultiPolygon(filtered_polygons)

    def get_areas(self):
        return (self.cap0.area, self.cap1.area)

    def area(self):
        return self.all.area

class CircleCapSegments():

    def __init__(self,r,h,x_hi,x_lo,w=1/10,circle_resolution=_BASE_CIRCLE_RESOLUTION):
        #self.y = sorted([amount0, amount1],key=lambda x:-x)
        self.r = r
        self.w = w
        self.h = h
        self.x_lo = x_lo
        self.x_hi = x_hi
        self.circle_resolution = circle_resolution
        self.compute()

    def compute(self):
        point = Point(0,0)
        self.circle = point.buffer(self.r,resolution=self.circle_resolution)
        r = self.r
        h = self.h
        w = self.w
        x_lo = self.x_lo
        x_hi = self.x_hi
        box0 = Polygon([(-2*r,h+w), (2*r,h+w), (2*r,h+w+2*r),(-2*r,h+w+2*r)])
        box1 = Polygon([(-2*r,h), (2*r,h), (2*r,h-2*r),(-2*r,h-2*r)])
        self.cap0 = self.circle.intersection(box0)
        self.cap1 = self.circle.intersection(box1)

        box_lo_left  = Polygon([(-2*r,h+w/2), (x_lo,h+w/2), (x_lo,h-2*r),(-2*r,h-2*r)])
        box_lo_right = Polygon([(x_lo + w,h+w/2), (2*r,h+w/2), (2*r,h-2*r),(x_lo+w,h-2*r)])

        box_hi_left  = Polygon([(-2*r,h+w/2), (x_hi,h+w/2), (x_hi,h+2*r),(-2*r,h+2*r)])
        box_hi_right = Polygon([(x_hi+w,h+w/2), (2*r,h+w/2), (2*r,h+2*r),(x_hi+w,h+2*r)])

        self.seg00 = self.cap0.intersection(box_hi_left)
        self.seg01 = self.cap0.intersection(box_hi_right)
        self.seg10 = self.cap1.intersection(box_lo_left)
        self.seg11 = self.cap1.intersection(box_lo_right)

        filtered_polygons = list(filter(lambda x: x.area > 0, [self.seg00, self.seg01, self.seg10, self.seg11]))
        self.all = MultiPolygon(filtered_polygons)

    def get_areas(self):
        return [ [self.seg00.area, self.seg01.area], [self.seg10.area, self.seg11.area] ]

    def area(self):
        return self.all.area


class CircleCapPresentation():

    def __init__(self,y,r=1,w=1/10,area=None,circle_resolution=_BASE_CIRCLE_RESOLUTION):

        if area is not None:
            self.initial_r = r = np.sqrt(area/np.pi)
            self.target_area = area
        else:
            self.initial_r = r
            self.target_area = np.pi * r**2

        self.y = np.array(y)
        assert(self.y.shape == (2,))
        self.relative_y = self.y/self.y.sum()
        self.target_areas = self.target_area * self.relative_y
        self.w = w
        self.circle_resolution = circle_resolution

    def get_caps(self,r,h,w):
        caps = CircleCaps(r,h,w,circle_resolution=self.circle_resolution)
        return caps

    def get_areas(self,r,h,w):
        caps = self.get_caps(r,h,w)
        return np.array(caps.get_areas())

    def compute(self,tol=1e-3):
        r0 = self.initial_r
        h0 = (self.relative_y[0] - self.relative_y[1])
        #print(r0,h0)
        func = lambda param: self.get_areas(param[0], param[1], self.w) - self.target_areas
        solution = root(func,[r0,h0],tol=tol)
        self.caps = self.get_caps(solution.x[0],solution.x[1],self.w)
        self.r = solution.x[0]

        return self
        #print(solution)

class CircleCapPresentationConstR():

    def __init__(self,y,r=1,w=1/10,circle_resolution=_BASE_CIRCLE_RESOLUTION):

        self.r = r
        self.target_area = np.pi * r**2

        self.y = np.array(y)
        assert(self.y.shape == (2,))
        self.relative_y = self.y/self.y.sum()
        self.rel_target_areas = self.relative_y
        self.w = w
        self.circle_resolution = circle_resolution


    def get_caps(self,r,h,w):
        caps = CircleCaps(r,h,w,circle_resolution=self.circle_resolution)
        return caps

    def get_relative_areas(self,r,h,w):
        caps = self.get_caps(r,h,w)
        areas = np.array(caps.get_areas())
        return areas / areas.sum()

    def compute(self,tol=1e-3):
        h0 = 0

        def func(param):
            rel = self.get_relative_areas(self.r, param[0], self.w)
            trg = self.rel_target_areas
            return [ rel[0] - trg[0] ]

        solution = root(func,[h0],tol=tol)
        self.caps = self.get_caps(self.r,solution.x[0],self.w)
        return self

class CircleCapSegmentPresentation():

    def __init__(self,C,r=1,w=1/10,area=None,circle_resolution=_BASE_CIRCLE_RESOLUTION):

        if area is not None:
            self.initial_r = r = np.sqrt(area/np.pi)
            self.target_area = area
        else:
            self.initial_r = r
            self.target_area = np.pi * r**2

        self.C = np.array(C)
        assert(self.C.shape == (2,2))
        self.relative_C = self.C/self.C.sum()
        self.target_areas = (self.target_area * self.relative_C)
        self.w = w
        self.circle_resolution = circle_resolution


    def get_segs(self,r,h,xhi,xlo,w):
        segs = CircleCapSegments(r,h,xhi,xlo,w,circle_resolution=self.circle_resolution)
        return segs

    def get_areas(self,r,h,xhi,xlo,w):
        segs = self.get_segs(r,h,xhi,xlo,w)
        return np.array(segs.get_areas())

    def compute(self,tol=1e-3):
        r0 = self.initial_r

        h0 = 0
        xhi0 = 0
        xlo0 = 0

        func = lambda p: self.get_areas(p[0], p[1], p[2], p[3], self.w).ravel() - self.target_areas.ravel()
        solution = root(func,[r0,h0,xhi0,xlo0],tol=tol)
        p = solution.x.tolist() + [self.w]
        self.r = p[0]
        self.segs = self.get_segs(*p)

        return self

    def plot(self,
             ax=None,
             upper_color=None,
             lower_color=None,
             brighter_base=2,
             ec='w',
             linewidth=0.5,
             figsize=(6,6),
             ):

        if upper_color is None:
            self.upper_color = bp.epipack[1]
        else:
            self.upper_color = upper_color
        if lower_color is None:
            self.lower_color = bp.epipack[2]
        else:
            self.upper_color = upper_color
        self.upper_brighter = bp.brighter(self.upper_color, brighter_base)
        self.lower_brighter = bp.brighter(self.lower_color, brighter_base)

        if ax is None:
            fig, ax = pl.subplots(1,1,figsize=figsize)

        def _plot(geom, color, ec=None, linewidth=None):
            xs, ys = geom.exterior.xy
            ax.fill(xs, ys, fc=color, ec=ec, linewidth=linewidth)

        for geom, color in [
                (self.segs.seg00, self.upper_color),
                (self.segs.seg01, self.upper_brighter),
                (self.segs.seg10, self.lower_color),
                (self.segs.seg11, self.lower_brighter),
            ]:
            if geom.area > 0:
                _plot(geom, color, ec=ec, linewidth=linewidth)

        return ax


class CircleCapSegmentPresentationConstR(CircleCapSegmentPresentation):

    def __init__(self,C,r=1,w=1/10,circle_resolution=_BASE_CIRCLE_RESOLUTION):

        self.r = r
        self.target_area = np.pi * r**2

        self.C = np.array(C)
        assert(self.C.shape == (2,2))
        self.relative_C = self.C/self.C.sum()
        self.rel_target_areas = self.relative_C
        self.w = w
        self.circle_resolution = circle_resolution

    def get_segs(self,r,h,xhi,xlo,w):
        segs = CircleCapSegments(r,h,xhi,xlo,w,circle_resolution=self.circle_resolution)
        return segs

    def get_relative_areas(self,r,h,xhi,xlo,w):
        segs = self.get_segs(r,h,xhi,xlo,w)
        areas = np.array(segs.get_areas())
        return areas / areas.sum()

    def compute(self,tol=1e-3):
        r0 = self.r

        h0 = 0
        xhi0 = 0
        xlo0 = 0

        def func(p):
            areas = self.get_relative_areas(self.r, p[0], p[1], p[2], self.w).ravel()
            targets = self.rel_target_areas.ravel()
            return areas[1:] - targets[1:]

        solution = root(func,[h0,xhi0,xlo0],tol=tol)

        p = [self.r] + solution.x.tolist() + [self.w]
        self.segs = self.get_segs(*p)

        return self

class JoinedVectorAndMatrixPresentation():

    def __init__(self,
                 vector_presentation,
                 matrix_presentation,
                 xoff=0.0,
                 yoff=0.0,
                ):

        caps = vector_presentation.caps
        segs = matrix_presentation.segs

        cap_width = 2 * vector_presentation.r
        seg_r = matrix_presentation.r

        #if xoff is None:
        #    xoff = cap_width + seg_r
        if yoff == 0.0 and xoff == 0.0:
            yoff = -1.5*cap_width - seg_r

        self.cap0 = caps.cap0
        self.cap1 = caps.cap1
        self.w = vector_presentation.w

        self.r_caps = vector_presentation.r
        self.r_segs = matrix_presentation.r

        self.seg00 = translate(segs.seg00, xoff=xoff, yoff=yoff)
        self.seg01 = translate(segs.seg01, xoff=xoff, yoff=yoff)
        self.seg10 = translate(segs.seg10, xoff=xoff, yoff=yoff)
        self.seg11 = translate(segs.seg11, xoff=xoff, yoff=yoff)

        self.caps = [self.cap0, self.cap1]
        self.segs = [self.seg00, self.seg01, self.seg10, self.seg11]
        self.seg_matrix = [ [self.seg00, self.seg01], [self.seg10, self.seg11] ]

        filtered_polygons = list(filter(lambda x: x.area > 0, self.caps+self.segs))
        self.all = MultiPolygon(filtered_polygons)

    def plot(self,ax=None,upper_color=None,lower_color=None,brighter_base=2,ec='w',linewidth=0.5,figsize=(6,6)):
        if upper_color is None:
            self.upper_color = bp.epipack[1]
        else:
            self.upper_color = upper_color
        if lower_color is None:
            self.lower_color = bp.epipack[2]
        else:
            self.upper_color = upper_color
        self.upper_brighter = bp.brighter(self.upper_color, brighter_base)
        self.lower_brighter = bp.brighter(self.lower_color, brighter_base)

        if ax is None:
            fig, ax = pl.subplots(1,1,figsize=figsize)

        def _plot(geom, color, ec=None, linewidth=None):
            xs, ys = geom.exterior.xy
            ax.fill(xs, ys, fc=color, ec=ec, linewidth=linewidth)

        for geom, color in [
                (self.cap0, self.upper_color),
                (self.cap1, self.lower_color),
                (self.seg00, self.upper_color),
                (self.seg01, self.upper_brighter),
                (self.seg10, self.lower_color),
                (self.seg11, self.lower_brighter),
            ]:
            if geom.area > 0:
                _plot(geom, color, ec=ec, linewidth=linewidth)

        ax.axis('equal')

        self.ax = ax

        return ax

    def add_arrows_to_plot(self, lw=1.5, symmetrical_arrows=True):

        d = self.w
        arrowwidth = self.w*1.5
        if not symmetrical_arrows:
            left_max = right_max - 2*self.w
            right_max = max(self.r_caps, self.r_segs) + 4*self.w
        else:
            left_max = -max(self.r_caps, self.r_segs) - 2*self.w
            right_max = max(self.r_caps, self.r_segs) + 2*self.w

        first_set = { 'cap': self.cap0, 'seg0': self.seg00, 'seg1': self.seg10, 'max': left_max, 'color': self.upper_brighter }
        second_set = { 'cap': self.cap1, 'seg0': self.seg01, 'seg1': self.seg11, 'max': right_max, 'color': self.lower_brighter }
        capfactors = [+1,-1]
        segfactors = [4,1]
        zorders = [0,0]

        distance_between_circles = 2*self.r_caps

        for cfac, sfac, _set, zorder in zip(capfactors, segfactors, [first_set, second_set], zorders):

            # deal with left arrow#
            _x0, _x1, _y = _find_focused_edge_x(_set['cap'])
            xdist = _x1
            xcap, ycap = _find_mean_x_and_y_of_focused_edge_x(_set['cap'])
            ycap += cfac*d
            xseg0, yseg0 = _find_mean_x_and_y_of_focused_edge_x(_set['seg0'])
            yseg0 += sfac*d
            xseg1, yseg1 = _find_mean_x_and_y_of_focused_edge_x(_set['seg1'])
            yseg1 -= sfac*d

            if symmetrical_arrows:
                xseg0, yseg0 = _set['seg0'].centroid.coords[0]
                xseg1, yseg1 = _set['seg1'].centroid.coords[0]

            xstart0 = xcap-cfac*d

            base_coords = [
                            #(xcap-cfac*xdist*0.85, ycap),
                           # (_set['max'], ycap+0.5*(yseg0-ycap)),
                            (xstart0, ycap),
                            (xstart0, -0.5*distance_between_circles-self.r_caps),
                            (_set['max'], -1.25*distance_between_circles-self.r_caps),
                          ]
            up_coords = [
                            (_set['max'], yseg0),
                            (xseg0, yseg0),
                        ]
            low_coords = [
                            (_set['max'], yseg1),
                            (xseg1, yseg1),
                        ]
            x, y = zip(*(base_coords+up_coords))
            self.ax.plot(x, y, zorder=zorder, color=_set['color'], lw=lw)
            x, y = zip(*(base_coords+low_coords))
            self.ax.plot(x, y, zorder=zorder, color=_set['color'], lw=lw)

            if not symmetrical_arrows and cfac == 1:
                arr_fac = -cfac
            else:
                arr_fac = cfac

            arrow_one = [
                            (_set['max'], yseg1),
                            (_set['max']+arr_fac*arrowwidth*1.5, yseg1),
                            (_set['max'], yseg1+0.5*arrowwidth),
                        ]
            arrow_two = [
                            #(_set['max'], yseg0), #half arrow
                            (_set['max'], yseg0 - 0.5*arrowwidth), #full arrow
                            (_set['max']+arr_fac*arrowwidth*1.5, yseg0),
                            (_set['max'], yseg0+0.5*arrowwidth),
                        ]
            offset = -cfac*arrowwidth*.5 #set this to 0 for full arrow, not half arrow
            arrow_three = [
                            (xstart0+cfac*arrowwidth*.5, ycap,),
                            (xstart0+cfac*arrowwidth*.5, -1.1*self.r_caps),
                            (xstart0, -1.1*self.r_caps-2*arrowwidth),
                            (xstart0+offset, -1.1*self.r_caps),
                            (xstart0+offset, ycap),
                    ]
            for arrow in [arrow_one, arrow_two, arrow_three]:
                xs, ys = zip(*arrow)
                self.ax.fill(xs, ys, fc=_set['color'], ec='None',zorder=-1)

    def add_text_to_plot(self):

        d = self.w
        arrowwidth = self.w*1.5
        right_max = max(self.r_caps, self.r_segs) + 4*self.w

        first_set = { 'cap': self.cap0, 'seg0': self.seg00, 'seg1': self.seg10, 'color': self.upper_brighter }
        second_set = { 'cap': self.cap1, 'seg0': self.seg01, 'seg1': self.seg11, 'color': self.lower_brighter }
        capfactors = [+1,-1]
        segfactors = [4,1]
        zorders = [0,0]

        distance_between_circles = 2*self.r_caps
        labels = {'cap': ['(u)nvacc','(v)acc']}
        labels = {'cap': ['u','v']}

        vas = ['bottom', 'top']

        for i, (cfac, sfac, _set, zorder, va) in enumerate(zip(capfactors, segfactors, [first_set, second_set], zorders, vas)):

            # deal with left arrow#
            _x0, _x1, _y = _find_focused_edge_x(_set['cap'])
            xdist = _x1
            xcap, ycap = _find_mean_x_and_y_of_focused_edge_x(_set['cap'])
            ycap += cfac*d
            xseg0, yseg0 = _find_mean_x_and_y_of_focused_edge_x(_set['seg0'])
            yseg0 += sfac*d
            xseg1, yseg1 = _find_mean_x_and_y_of_focused_edge_x(_set['seg1'])
            yseg1 -= sfac*d

            self.ax.text(xcap, ycap, labels['cap'][i], transform=self.ax.transData, color='w', ha='center',va=va, fontstyle='italic')

def get_circular_vector_and_matrix_presentation(y, C, r=1, w=0.1):

    ypres = CircleCapPresentationConstR(y,r=r,w=w).compute()
    Cpres = CircleCapSegmentPresentation(C, area=ypres.caps.area()*C.sum(), w=w).compute()
    joined = JoinedVectorAndMatrixPresentation(ypres, Cpres)

    return joined

def _get_envelope_xy(geom,which):
    x, y = geom.envelope.exterior.xy
    if not which.lower() in [
                'lower left',
                'upper right',
                'upper left',
                'lower right',
            ]:
        if which == 'lower left':
            return min(x), min(y)
        if which == 'upper left':
            return min(x), max(y)
        if which == 'upper right':
            return max(x), max(y)
        if which == 'lower right':
            return max(x), min(y)
    else:
        raise ValueError(f"Don't know how to interpret {which=}")

def _find_focused_edge_x(geom):
    x, y = geom.exterior.xy
    ndx = np.where(np.diff(y) == 0.)[0][0]
    _x = sorted([ x[ndx], x[ndx+1] ])
    _y = [y[ndx]] * 2
    return _x + [_y[0]]

def _find_focused_edge_y(geom):
    x, y = geom.exterior.xy
    ndx = np.where(np.diff(x) == 0.)[0][0]
    _y = sorted([ y[ndx], y[ndx+1] ])
    _x = [x[ndx]] * 2
    return [_x[0] ] + _y

def _find_mean_x_and_y_of_focused_edge_x(geom):
    x0, x1, y = _find_focused_edge_x(geom)
    return np.mean([x0,x1]), y

def _find_mean_x_and_y_of_focused_edge_y(geom):
    x, y0, y1, = _find_focused_edge_y(geom)
    return x, np.mean([y0,y1]), y


def add_text_to_plot(joined_pres, c):
    pass

if __name__ == "__main__":

    import vaccontrib as vc

    C = vc.covid.get_reduced_vaccinated_susceptible_contribution_matrix_covid([1.,4,4,4,4],variant='alpha')
    K = vc.covid.get_next_generation_matrix_covid([1.,4,4,4,4],variant='alpha')

    C = vc.covid.get_reduced_vaccinated_susceptible_contribution_matrix_covid([1.,1,1,1,1],variant='delta')
    K = vc.covid.get_next_generation_matrix_covid([1.,1,1,1,1],variant='delta')

    C = vc.covid.get_reduced_vaccinated_susceptible_contribution_matrix_covid([6.,6,6,6,6],variant='delta')
    K = vc.covid.get_next_generation_matrix_covid([6.,6,6,6,6],variant='delta')

    C = np.random.rand(2,2)

    y = vc.get_eigenvector(K)
    y = y.sum(axis=0)
    y = np.array([y[0],y[1:].sum()])

    y = np.random.rand(2)
    pres = get_circular_vector_and_matrix_presentation(y, C)

    ax = pres.plot(figsize=(6,6))
    ax.axis('off')
    pres.add_arrows_to_plot()
    pres.add_text_to_plot()
    ax.get_figure().savefig('a.pdf')


    segsonly = CircleCapSegmentPresentation(C,area=C.sum())
    segsonly.compute()
    ax = segsonly.plot()

    pl.show()

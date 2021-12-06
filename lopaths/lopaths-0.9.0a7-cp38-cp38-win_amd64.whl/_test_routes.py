'''
Created on 20.03.2020

@author: Samuel
'''
import os
import sys
from itertools import cycle

import numpy as np
import matplotlib as mpl
if os.name == 'posix':
    # if executed on a Windows server. Comment out this line, if you are working
    # on a desktop computer that is not Windows.
    mpl.use('Agg')

from vemomoto_core.tools.tee import Tee

if __name__ == '__main__':
    if len(sys.argv) > 1:
        teeObject = Tee(sys.argv[1])

try:
    from .test_routes import *
except ImportError:
    from test_routes import *

if __name__ == '__main__':
    
    restart = True
    restart = False
    show = False
    
    """
    fileNameVertices = "LakeNetworkExample_full_vertices.csv"
    fileNameEdges = "LakeNetworkExample_full.csv"
    fileNameSave = "testRouteTester2"
    fileNameSave = "testRouteTester"
    fileNameData= "testRCData.csv"
    additionalStations = [b'14', b'22']
    """
    fileNameVertices = "ExportVertices.csv"
    fileNameEdges = "ExportEdges.csv"
    fileNameSave = "BCRouteTester"
    fileNameData= "ExportOriginDestinationStation.csv"
    additionalStations = [b'18']
    
    
    
    #"""
    
    
    
    tester = RouteTester.new(fileNameSave, fileNameEdges, fileNameVertices, restart)
    
    restart = False
    
    cmap = mpl.cm.get_cmap('viridis')
    colorCycler = cycle([cmap(i) for i in np.linspace(0, 1, 4)[::-1]])
    
    plt.figure(**FIGARGS)
    plt.plot([0, 1], [0, 1], "--", color='k')
    for level in [0.1, 1, 2, 3, 4]:
        adjust_ticks(TICKS, TICKS)
        tester.test_empirical_validity(fileNameData, additionalStations, 
                                       level=level, stretchConstant=1.3,
                                       restart=restart, show=show,
                                       colorCycler=colorCycler)
        tester.test_empirical_validity(fileNameData, additionalStations, 
                                       level=level, stretchConstant=1.5,
                                       restart=restart, show=show,
                                       colorCycler=colorCycler)
        tester.test_empirical_validity(fileNameData, additionalStations, 
                                       level=level, stretchConstant=2,
                                       restart=restart, show=show,
                                       colorCycler=colorCycler)
        tester.test_empirical_validity(fileNameData, additionalStations, 
                                       level=level, stretchConstant=3,
                                       restart=restart, show=show,
                                       colorCycler=colorCycler)
        plt.figure(**FIGARGS)
        plt.plot([0, 1], [0, 1], "--", color='k')
    
    
    
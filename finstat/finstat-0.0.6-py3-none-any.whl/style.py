import numpy as np
import pandas as pd
from collections import UserString

class ColorStr(UserString):
    @property
    def nohash(self):
        return self.data[1:]
    
    def hex_to_rgb(self): 
        return tuple(int(self.nohash[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_bgrhex(self, rgb):
        '''
        win32 uses bgr in hex
        '''
        bgr = (rgb[2], rgb[1], rgb[0])
        strValue = '%02x%02x%02x' % bgr
        iValue = int(strValue, 16)

        return iValue

    @property
    def bgrhex(self):
        if not hasattr(self, '_bgrhex'):
            self._bgrhex = self.rgb_to_bgrhex(self.hex_to_rgb())
        
        return self._bgrhex

class grc:
    blue = ColorStr('#253765')
    green = ColorStr('#6dbc45')
    lblue = ColorStr('#2765b0')
    drkgreen = ColorStr('#335B20')
    vlblue = ColorStr('#c5d9f3')
    lgreen = ColorStr('#95CF77')

    # vlblue = ColorStr('#eef4fb')

    @classmethod
    def colors(cls, nohash=False):
        colors = [cls.blue, cls.green, cls.lblue, cls.drkgreen, cls.vlblue, cls.lgreen]

        if nohash:
            return [c.nohash for c in colors]
        else:
            return colors

class tabs:
    @classmethod
    @property
    def inputs(cls):
        return np.array([        
            'Assumptions',
            'Pipeline',
            'Headcount - Plan',
            'Headcount - Existing',
            'Opex',
            'Capex',
            'Capital'
        ])
    
    @classmethod
    @property
    def spacers(cls):
        return np.array(['Inputs --->', 'Forecast --->', 'Annual --->', 'Quarterly --->', 'Supporting --->'])
    
    @classmethod
    @property
    def order(cls):
        return np.concatenate((cls.inputs, cls.spacers))
    
    @classmethod
    @property
    def before_after(cls):
        return pd.concat((
            pd.Series(cls.order), 
            pd.Series(cls.order).shift(-1), 
            pd.Series(cls.order).shift(1)
            ), 
            axis=1
        ).set_index(0).rename(columns={1: 'before', 2: 'after'})
    
    @classmethod
    def set_color(cls, sheet):
        if sheet.name in tabs.spacers:
            color = grc.blue
        elif sheet.name in tabs.inputs:
            color = grc.green
        else:
            color = grc.vlblue
        
        sheet.api.Tab.Color = color.bgrhex

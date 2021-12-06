# -*- coding: utf-8 -*-
"""
Created on Sun Sep 26 13:17:48 2021

@author: mumuz
"""

import clr
from System.Collections.Generic import List

import muswmm.lib

from Mumu.SWMM.SwmmObjects import Point as Pnt
from Mumu.SWMM.SwmmObjects import UnnamedObjs

class Point():
    
    def __init__(self, x = 0.0, y = 0.0):
        self._x = x
        self._y = y
        
    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self, value):
        self._y = value
        
    @property
    def swmm_point(self):
        return Pnt(self._x, self._y)
    
    @swmm_point.setter
    def swmm_point(self, value):
        self._x = value.X
        self._y = value.Y


class Points():
    
    def __init__(self):
        self._points = []
        self._cur_index = 0
    
    def __len__(self):
        return len(self._points)
    
    def __getitem__(self, index):
        try:
            return self._points[index]
        except Exception as e:
            raise Exception(e.args[0])
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self._cur_index < self.__len__():
            obj = self._points[self._cur_index]
            self._cur_index += 1
            return obj
        else:
            raise StopIteration()
    
    @property
    def swmm_points(self):
        if self._points.count == 0:
            return
        list_point = [Pnt(self._points[i].x, self._points[i].y)
                  for i in range(0, len(self._points))]
        net_list = List[Pnt]()
        for point in list_point:
            net_list.Add(point)
        return net_list        
        
    @swmm_points.setter
    def swmm_points(self, value):
        list_point= value.ToList()
        self._points = [Point(list_point[i].X, list_point[i].Y)
                        for i in range(0, int(len(list_point)))]
    
    def add(self, point):
        self._points.append(point)
        
    def remove(self, point):
        self._points.remove(point)
        
    def clear(self):
        self._points.clear()
        
    def count(self):
        return len(self._points)    


import math
import random
import numpy as np


from .utils import min_fast, max_fast


class Mutations:

    @staticmethod
    def uniform_by_x():
        
        def func(x: float, left: float, right: float):
            alp = min_fast(x - left, right - x)
            return np.random.uniform(x - alp, x + alp)
        return func

    @staticmethod
    def uniform_by_center():
        
        def func(x: float, left: float, right: float):
            return np.random.uniform(left, right)
        
        return func

    @staticmethod
    def gauss_by_x(sd: float = 0.3):
        """
        gauss mutation with x as center and sd*length_of_zone as std
        """
        def func(x: float, left: float, right: float):
            std = sd * (right - left)
            return max_fast(left, min_fast(right, np.random.normal(loc = x, scale = std)))
        
        return func

    @staticmethod
    def gauss_by_center(sd: float = 0.3):
        """
        gauss mutation with (left+right)/2 as center and sd*length_of_zone as std
        """
        def func(x: float, left: float, right: float):
            std = sd * (right - left)
            return max_fast(left, min_fast(right, np.random.normal(loc = (left+right)*0.5, scale = std)))
        
        return func
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 19 16:24:25 2021

@author: Umt
"""

import time

# Sleep between print and tqdm displays
def safe_print(text, stop_dur=0.3):
    print(text)
    time.sleep(stop_dur)
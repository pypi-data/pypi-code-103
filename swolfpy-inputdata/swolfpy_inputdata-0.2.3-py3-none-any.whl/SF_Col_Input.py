# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 22:52:32 2019

@author: msmsa
"""
from .InputData import InputData
from .CommonData import CommonData
from pathlib import Path
import pandas as pd


class SF_Col_Input(InputData):
    def __init__(self, input_data_path=None, process_data_path=None,
                 process_name='SF_Col', CommonDataObjct=None):
        if input_data_path:
            self.input_data_path = input_data_path
        else:
            self.input_data_path = Path(__file__).parent / 'Data/SF_Col_Input.csv'

        # Initialize the superclass
        super().__init__(self.input_data_path, process_name)

        if not CommonDataObjct:
            CommonDataObjct = CommonData()

        if process_data_path is None:
            process_data_path = Path(__file__).parent / "Data/SF_Col_Input_MaterialDependent.csv"
        self.add_process_data(process_data_path=process_data_path,
                              index=CommonDataObjct.Index)

        ### Read input data
        self.col = pd.read_csv(Path(__file__).parent / 'Data/SF_Col_Input_process.csv',
                               index_col='Name',
                               usecols=['Name', 'RWC', 'SSR', 'DSR', 'MSR', 'LV', 'SSYW', 'SSO', 'ORG', 'DryRes', 'REC',
                                        'WetRes', 'MRDO', 'SSYWDO', 'MSRDO']).astype(float)
        self.col = self.col.transpose()

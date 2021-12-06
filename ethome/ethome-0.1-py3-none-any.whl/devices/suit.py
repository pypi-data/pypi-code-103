import os
import pickle
import itertools
import subprocess
import numpy as np
import transforms3d
import pandas as pd
import xml.etree.ElementTree as ET

from device import Device
from mvnx.mvnx import MVNX


class Suit(Device):
    attrs = [
        'HipsPos_Pos_X', 
        'HipsPos_Pos_Y', 
        'HipsPos_Pos_Z', 
        'Hips_Rot_Z',
        'Hips_Rot_X',
        'Hips_Rot_Y',
        'LeftUpLeg_Rot_Z',
        'LeftUpLeg_Rot_X',
        'LeftUpLeg_Rot_Y',
        'LeftLeg_Rot_Z',
        'LeftLeg_Rot_X',
        'LeftLeg_Rot_Y',
        'LeftFoot_Rot_Z',
        'LeftFoot_Rot_X',
        'LeftFoot_Rot_Y',
        'LeftFootHeel_Rot_Z',
        'LeftFootHeel_Rot_X',
        'LeftFootHeel_Rot_Y',
        'RightUpLeg_Rot_Z',
        'RightUpLeg_Rot_X',
        'RightUpLeg_Rot_Y',
        'RightLeg_Rot_Z',
        'RightLeg_Rot_X',
        'RightLeg_Rot_Y',
        'RightFoot_Rot_Z',
        'RightFoot_Rot_X',
        'RightFoot_Rot_Y',
        'RightFootHeel_Rot_Z',
        'RightFootHeel_Rot_X',
        'RightFootHeel_Rot_Y',
        'Spine_Rot_Z',
        'Spine_Rot_X',
        'Spine_Rot_Y',
        'Spine1_Rot_Z',
        'Spine1_Rot_X',
        'Spine1_Rot_Y',
        'LeftShoulder_Rot_Z',
        'LeftShoulder_Rot_X',
        'LeftShoulder_Rot_Y',
        'LeftArm_Rot_Z',
        'LeftArm_Rot_X',
        'LeftArm_Rot_Y',
        'LeftForeArm_Rot_Z',
        'LeftForeArm_Rot_X',
        'LeftForeArm_Rot_Y',
        'LeftHand_Rot_Z',
        'LeftHand_Rot_X',
        'LeftHand_Rot_Y',
        'RightShoulder_Rot_Z',
        'RightShoulder_Rot_X',
        'RightShoulder_Rot_Y',
        'RightArm_Rot_Z',
        'RightArm_Rot_X',
        'RightArm_Rot_Y',
        'RightForeArm_Rot_Z',
        'RightForeArm_Rot_X',
        'RightForeArm_Rot_Y',
        'RightHand_Rot_Z',
        'RightHand_Rot_X',
        'RightHand_Rot_Y',
        'Neck_Rot_Z',
        'Neck_Rot_X',
        'Neck_Rot_Y',
        'Head_Rot_Z',
        'Head_Rot_X',
        'Head_Rot_Y',
    ]

    def __init__(self, **kwargs):
        kwargs.update({"labels": self.attrs})
        super().__init__(**kwargs)

    def load_MVNX(self, filename):
        """
        Arguments:
            filename {[type]} -- [description]
        """
        assert isinstance(filename, str)
        mvnx = MVNX(filename)
        # self.data = {key: value for key, value in mvnx.items() if isinstance(value, np.ndarray)}
        # self.labels = list(self.data.keys())
        self.joints = mvnx.joints
        self.jointAngle = mvnx.jointAngle
        self.angularVelocity = mvnx.angularVelocity
        self.segments = mvnx.segments
        self.time = mvnx.time
        self.timecode = mvnx.timecode
        self.ms = mvnx.ms
        # return self.data

    # def data_to_HDF5(self):
    #     create_dataset(self.jointAngle)

    def read_BVH(self, BVHfile):
        self.BVHobject = npybvh.Bvh()
        with open(BVHfile, 'r') as f:
            _file = f.read()
        return self.BVHobject.parse_string(_file)

    def convert_BVH_to_CSV(self, filename):
        subprocess.call(f'bvh2csv --position {filename}')

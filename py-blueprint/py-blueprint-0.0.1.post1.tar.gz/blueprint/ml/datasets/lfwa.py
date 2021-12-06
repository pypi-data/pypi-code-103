# MIT License

# Copyright (c) 2021 Hao Yang (yanghao.alexis@foxmail.com)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import numpy as np
import cv2
import functools
import torch
from typing import Dict, List

from . import data_path
from ..dataset import Dataset, Split


@functools.lru_cache()
def _cached_imread(fname, flags=None):
    return cv2.imread(fname, flags=flags)


class LFWA(Dataset):
    """ The LFWA dataset used by 

        Liu, Ziwei, Ping Luo, Xiaogang Wang, and Xiaoou Tang. 
        "Deep learning face attributes in the wild." In Proceedings 
        of the IEEE international conference on computer vision, 
        pp. 3730-3738. 2015.

    It can be downloaded from https://mmlab.ie.cuhk.edu.hk/projects/CelebA.html.

    """

    def __init__(self, split=Split.TRAIN, root=None, aligned=False):
        if root is None:
            root = data_path.get('LFWA')

        self.images_root = os.path.join(root, 'lfw')

        attr_data = torch.load(os.path.join(root, 'lfw_att_40.pth'))
        self.names = attr_data['name']
        self.labels = attr_data['label']

        index_data = torch.load(os.path.join(root, 'indices_train_test.pth'))
        if split == Split.TRAIN:
            self.indices = index_data["indices_img_train"].astype(np.long)-1
        elif split == Split.TEST:
            self.indices = index_data["indices_img_test"].astype(np.long)-1

        self.landmarks = torch.load(os.path.join(root, 'lfw_landmarks.pth'))

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, index):
        index = self.indices[index]
        image = cv2.cvtColor(_cached_imread(os.path.join(
            self.images_root, *self.names[index].split('\\'))), cv2.COLOR_BGR2RGB)
        labels = self.labels[index]
        landmarks = self.landmarks[index]
        return {
            'image': image,
            'attrs': labels,
            'face_5_pts': landmarks
        }

    def sample_name(self, index) -> str:
        index = self.indices[index]
        return self.names[index].replace('\\', '.')

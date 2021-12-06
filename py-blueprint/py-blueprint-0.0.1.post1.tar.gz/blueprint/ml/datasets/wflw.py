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

from . import data_path
from ..dataset import Dataset, Split


class WFLW(Dataset):
    """ The WFLW dataset proposed by 

        Wu, Wayne, Chen Qian, Shuo Yang, Quan Wang, Yici Cai, and Qiang Zhou. 
        "Look at boundary: A boundary-aware face alignment algorithm." 
        In Proceedings of the IEEE conference on computer vision and 
        pattern recognition, pp. 2129-2138. 2018.

    It can be downloaded from https://wywu.github.io/projects/LAB/WFLW.html.

    """

    def __init__(self, root=None, split=Split.ALL, subset=None):
        if root is None:
            root = data_path.get('WFLW')

        self.root = root

        anno_file = None
        if split == Split.TRAIN:
            anno_file = 'list_98pt_rect_attr_train_test/list_98pt_rect_attr_train.txt'
        elif split == Split.TEST:
            if subset is None:
                anno_file = 'list_98pt_test/list_98pt_test.txt'
            else:
                anno_file = f'list_98pt_test/list_98pt_test_{subset}.txt'

        self.info_list = []
        with open(os.path.join(root, 'WFLW_annotations', anno_file), 'r') as f:
            for line_id, line in enumerate(f):
                line = line.strip()
                if len(line) == 0:
                    continue
                components = line.split()
                landmarks = np.reshape(
                    np.array([float(v) for v in components[:2*98]]), [98, 2])
                cx, cy = np.mean(landmarks, axis=0)
                image_file = components[-1]
                self.info_list.append({
                    'im_path': os.path.join(root, 'WFLW_images', image_file),
                    'sample_name': image_file.replace('/', '.') + ('_%.3f_%.3f' % (cx, cy)),
                    'landmarks': landmarks})

    def __len__(self):
        return len(self.info_list)

    def __getitem__(self, index):
        info = self.info_list[index]
        image = cv2.cvtColor(cv2.imread(info['im_path']), cv2.COLOR_BGR2RGB)
        x1, y1 = np.min(info['landmarks'], axis=0)
        x2, y2 = np.max(info['landmarks'], axis=0)
        box_y1x1y2x2 = np.array([y1, x1, y2, x2], dtype=np.float32)
        return {
            'image': image,
            'box': box_y1x1y2x2,
            'landmarks': info['landmarks']
        }

    def sample_name(self, index):
        return self.info_list[index]['sample_name']

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
import scipy.io

from . import data_path
from ..dataset import Dataset, Split


class AFLW_19(Dataset):
    """ The AFLW-19 dataset used by [1], which has 19 landmark points in each image. 
    Note that it is NOT the original AFLW [2] dataset which has 21 landmark points per image.

    AFLW-19 data can be downloaded from http://mmlab.ie.cuhk.edu.hk/projects/compositional.html.

    Citations:

        [1] Zhu, Shizhan, Cheng Li, Chen-Change Loy, and Xiaoou Tang. 
            "Unconstrained face alignment via cascaded compositional learning." 
            In Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition, 
            pp. 3409-3417. 2016.
        
        [2] Koestinger, Martin, Paul Wohlhart, Peter M. Roth, and Horst Bischof. 
            "Annotated facial landmarks in the wild: A large-scale, real-world database for facial 
            landmark localization." In 2011 IEEE international conference on computer vision workshops 
            (ICCV workshops), pp. 2144-2151. IEEE, 2011.
    """

    def __init__(self, root=None, split=Split.ALL, subset: str = 'full'):
        if root is None:
            root = data_path.get('AFLW')
        self.images_root = os.path.join(root, 'aflw-21', 'data', 'flickr')
        info = scipy.io.loadmat(os.path.join(
            root, 'aflw-19', 'AFLWinfo_release.mat'))
        self.bbox = info['bbox']  # 24386x4 left, right, top bottom
        self.data = info['data']  # 24386x38 x1,x2...,xn,y1,y2...,yn
        self.mask = info['mask_new']  # 24386x19
        self.name_list = [s[0][0] for s in info['nameList']]

        ra = np.reshape(info['ra'].astype(np.int32), [-1])-1
        assert ra.min() == 0
        assert ra.max() == self.bbox.shape[0] - 1
        if split == Split.ALL:
            self.indices = ra
        elif split == Split.TRAIN:
            self.indices = ra[:20000]
        elif split == Split.TEST:
            if subset == 'full':
                self.indices = ra[20000:]
            elif subset == 'frontal':
                all_visible = np.all(self.mask == 1, axis=1)  # 24386
                self.indices = np.array(
                    [ind for ind in ra[20000:] if all_visible[ind]])

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, index):
        ind = self.indices[index]
        image = cv2.cvtColor(cv2.imread(os.path.join(
            self.images_root, self.name_list[ind])), cv2.COLOR_BGR2RGB)
        landmarks = np.reshape(self.data[ind], [2, 19]).transpose()

        left, right, top, bottom = self.bbox[ind]
        box_y1x1y2x2 = np.array([top, left, bottom, right], dtype=np.float32)

        visibility = self.mask[ind]
        return {
            'image': image,
            'box': box_y1x1y2x2,
            'landmarks': landmarks,
            'visibility': visibility
        }

    def sample_name(self, index):
        return str(index)

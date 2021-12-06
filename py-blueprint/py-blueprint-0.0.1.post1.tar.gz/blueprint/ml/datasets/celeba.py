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
from typing import Dict, List

from . import data_path
from ..dataset import Dataset, Split


@functools.lru_cache()
def _cached_imread(fname, flags=None):
    return cv2.imread(fname, flags=flags)


class CelebA(Dataset):
    """ The CelebA dataset proposed by 

        Liu, Ziwei, Ping Luo, Xiaogang Wang, and Xiaoou Tang. 
        "Deep learning face attributes in the wild." In Proceedings 
        of the IEEE international conference on computer vision, 
        pp. 3730-3738. 2015.

    It can be downloaded from https://mmlab.ie.cuhk.edu.hk/projects/CelebA.html.

    """

    def __init__(self, split=Split.ALL, root=None, aligned=False):
        if root is None:
            root = data_path.get('CelebA')
        if aligned:
            self.images_root = os.path.join(root, 'Img', 'img_align_celeba')
            self.anno_landmark_file = os.path.join(
                root, 'Anno', 'list_landmarks_align_celeba.txt')
        else:
            self.images_root = os.path.join(root, 'Img', 'img_celeba')
            self.anno_landmark_file = os.path.join(
                root, 'Anno', 'list_landmarks_celeba.txt')

        self.info_dict = dict()
        self.image_names = []
        with open(os.path.join(root, 'Eval', 'list_eval_partition.txt'), 'r') as f:
            for line in f:
                line = line.strip()
                if len(line) == 0:
                    continue
                image_name, eval_status = line.split()
                assert image_name.endswith('.jpg')
                eval_status = int(eval_status)
                if split == Split.TRAIN and eval_status == 0 or split == Split.VAL and eval_status == 1 \
                        or split == Split.TEST and eval_status == 2 or split == Split.ALL:
                    self.info_dict[image_name] = dict()
                    self.image_names.append(image_name)

        with open(os.path.join(root, 'Anno', 'identity_CelebA.txt'), 'r') as f:
            for line in f:
                line = line.strip()
                if len(line) == 0:
                    continue
                image_name, identity = line.split()
                if image_name in self.info_dict:
                    self.info_dict[image_name]['identity'] = int(identity)

        with open(os.path.join(root, 'Anno', 'list_attr_celeba.txt'), 'r') as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if idx < 2 or len(line) == 0:
                    continue
                image_name, *attrs = line.split()
                if image_name in self.info_dict:
                    attrs = np.array(
                        [int(a) == 1 for a in attrs], dtype=np.uint8)
                    self.info_dict[image_name]['attrs'] = attrs

        if not aligned:
            with open(os.path.join(root, 'Anno', 'list_bbox_celeba.txt'), 'r') as f:
                for idx, line in enumerate(f):
                    line = line.strip()
                    if idx < 2 or len(line) == 0:
                        continue
                    image_name, *xywh = line.split()
                    if image_name in self.info_dict:
                        x, y, w, h = [int(v) for v in xywh]
                        y1x1y2x2 = np.array([y, x, y+h, x+w], dtype=np.float32)
                        self.info_dict[image_name]['box'] = y1x1y2x2

        with open(self.anno_landmark_file, 'r') as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if idx < 2 or len(line) == 0:
                    continue
                image_name, *face_5_pts = line.split()
                if image_name in self.info_dict:
                    face_5_pts = np.reshape(
                        np.array([float(v) for v in face_5_pts], dtype=np.float32), [5, 2])
                    self.info_dict[image_name]['face_5_pts'] = face_5_pts

        # check all
        for image_name, info in self.info_dict.items():
            assert 'identity' in info
            assert 'attrs' in info
            if not aligned:
                assert 'box' in info
            assert 'face_5_pts' in info

    def __len__(self):
        return len(self.image_names)

    def __getitem__(self, index):
        image_name = self.image_names[index]
        image = cv2.cvtColor(_cached_imread(os.path.join(
            self.images_root, image_name)), cv2.COLOR_BGR2RGB)
        info = self.info_dict[image_name]
        data = {
            'image': image,
            'identity': info['identity'],
            'attrs': info['attrs'],
            'face_5_pts': info['face_5_pts']
        }
        if 'box' in info:
            data['box'] = info['box']
        return data

    def sample_name(self, index) -> str:
        return self.image_names[index][:-4]


class CelebAMaskHQ(Dataset):
    """ The CelebAMask-HQ dataset proposed by 

        Lee, Cheng-Han, Ziwei Liu, Lingyun Wu, and Ping Luo. 
        "Maskgan: Towards diverse and interactive facial image manipulation." 
        In Proceedings of the IEEE/CVF Conference on Computer Vision and 
        Pattern Recognition, pp. 5549-5558. 2020.

    It can be downloaded from https://github.com/switchablenorms/CelebAMask-HQ.
    """

    def __init__(self, split=Split.ALL, root=None, label_type='all'):
        if root is None:
            root = data_path.get('CelebAMask-HQ')
        assert os.path.exists(root)
        self.root = root
        self.split = split
        self.names = []

        if split != Split.ALL:
            hq_to_orig_mapping = dict()
            orig_to_hq_mapping = dict()
            mapping_file = os.path.join(
                root, 'CelebA-HQ-to-CelebA-mapping.txt')
            assert os.path.exists(mapping_file)
            for s in open(mapping_file, 'r'):
                if '.jpg' not in s:
                    continue
                idx, _, orig_file = s.split()
                hq_to_orig_mapping[int(idx)] = orig_file
                orig_to_hq_mapping[orig_file] = int(idx)

            # load partition
            partition_file = os.path.join(root, 'list_eval_partition.txt')
            assert os.path.exists(partition_file)
            for s in open(partition_file, 'r'):
                if '.jpg' not in s:
                    continue
                orig_file, group = s.split()
                group = int(group)
                if orig_file not in orig_to_hq_mapping:
                    continue
                hq_id = orig_to_hq_mapping[orig_file]
                if split == Split.TRAIN and group == 0:
                    self.names.append(str(hq_id))
                elif split == Split.VAL and group == 1:
                    self.names.append(str(hq_id))
                elif split == Split.TEST and group == 2:
                    self.names.append(str(hq_id))
                elif split == Split.TOY:
                    self.names.append(str(hq_id))
                    if len(self.names) >= 10:
                        break
        else:
            self.names = [
                n[:-(len('.jpg'))]
                for n in os.listdir(os.path.join(self.root, 'CelebA-HQ-img'))
                if n.endswith('.jpg')
            ]

        self.label_setting = {
            'human': {
                'suffix': [
                    'neck', 'skin', 'cloth', 'l_ear', 'r_ear', 'l_brow', 'r_brow',
                    'l_eye', 'r_eye', 'nose', 'mouth', 'l_lip', 'u_lip', 'hair'
                ],
                'names': [
                    'bg', 'neck', 'face', 'cloth', 'rr', 'lr', 'rb', 'lb', 're',
                    'le', 'nose', 'imouth', 'llip', 'ulip', 'hair'
                ]
            },
            'aux': {
                'suffix': [
                    'eye_g', 'hat', 'ear_r', 'neck_l',
                ],
                'names': [
                    'normal', 'glass', 'hat', 'earr', 'neckl'
                ]
            },
            'all': {
                'suffix': [
                    'neck', 'skin', 'cloth', 'l_ear', 'r_ear', 'l_brow', 'r_brow',
                    'l_eye', 'r_eye', 'nose', 'mouth', 'l_lip', 'u_lip', 'hair',
                    'eye_g', 'hat', 'ear_r', 'neck_l',
                ],
                'names': [
                    'bg', 'neck', 'face', 'cloth', 'rr', 'lr', 'rb', 'lb', 're',
                    'le', 'nose', 'imouth', 'llip', 'ulip', 'hair',
                    'glass', 'hat', 'earr', 'neckl'
                ]
            }
        }[label_type]

    def make_label(self, index, ordered_label_suffix):
        label = np.zeros((512, 512), np.uint8)
        name = self.names[index]
        name_id = int(name)
        name5 = '%05d' % name_id
        p = os.path.join(self.root, 'CelebAMask-HQ-mask-anno',
                         str(name_id // 2000), name5)
        for i, label_suffix in enumerate(ordered_label_suffix):
            label_value = i + 1
            label_fname = os.path.join(p + '_' + label_suffix + '.png')
            if os.path.exists(label_fname):
                mask = _cached_imread(label_fname, cv2.IMREAD_GRAYSCALE)
                label = np.where(mask > 0,
                                 np.ones_like(label) * label_value, label)
        return label

    def __getitem__(self, index):
        name = self.names[index]
        image = cv2.resize(
            cv2.imread(os.path.join(self.root, 'CelebA-HQ-img',
                                    name + '.jpg'))[:, :, ::-1],
            (512, 512),
            interpolation=cv2.INTER_LINEAR)

        data = {'image': image}
        label = self.make_label(index, self.label_setting['suffix'])
        data[f'label'] = label

        return data

    def __len__(self):
        return len(self.names)

    def sample_name(self, index):
        return self.names[index]

    @property
    def label_names(self) -> List[str]:
        return self.label_setting['names']

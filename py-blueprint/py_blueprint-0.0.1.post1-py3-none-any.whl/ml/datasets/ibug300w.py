import os
import numpy as np
import cv2
import re

import xmltodict

from . import data_path
from ..dataset import Dataset, Split


class IBUG300W(Dataset):
    """The IBUG-300W face alignment dataset.
    """

    def __init__(self, root=None, split=Split.ALL, subset='Fullset'):
        if root is None:
            root = data_path.get('300W', 'Splitted')

        self.root = root

        self.anno = []

        if split == Split.ALL:
            pattern = '.*'
        elif split == Split.TRAIN:
            pattern = '(afw/.*)|(helen/trainset/.*)|(lfpw/trainset/.*)'
        elif split == Split.TEST:
            pattern = {
                'Common': '(helen/testset/.*)|(lfpw/testset/.*)',
                'Challenging': 'ibug/.*',
                'Fullset': '(helen/testset/.*)|(lfpw/testset/.*)|(ibug/.*)',
            }[subset]
        else:
            raise RuntimeError(f'unsupported split {split} for IBUG300W')
        pattern = re.compile(pattern)

        with open(os.path.join(self.root, 'labels_ibug_300W.xml'), 'r') as fd:
            anno = xmltodict.parse(fd.read())

        self.info_list = []
        for info in anno['dataset']['images']['image']:
            if '_mirror' in info['@file']:
                continue
            if not pattern.match(info['@file']):
                continue

            im_path = os.path.join(self.root, info['@file'])

            sample_name = info['@file'].replace('/', '.')
            box_info = info['box']

            landmarks = np.zeros([68, 2], dtype=np.float32)
            for point in box_info['part']:
                index = int(point['@name'])
                landmarks[index, 0] = float(point['@x'])
                landmarks[index, 1] = float(point['@y'])
            self.info_list.append({
                'sample_name': sample_name,
                'im_path': im_path,
                'landmarks': landmarks
            })

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

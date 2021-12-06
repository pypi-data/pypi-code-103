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
from typing import Union, Tuple
import cv2

from ..dataset import Dataset


class Wild(Dataset):
    """ Dataset based on wild images.
    """

    def __init__(self, root: str, suffix: Union[str, Tuple[str, ...]] = ('.jpg', '.png', '.jpeg')):
        self.root = root
        self.paths = []
        for r, _, files in os.walk(self.root):
            for name in files:
                if name.lower().endswith(suffix):
                    self.paths.append(os.path.join(r, name))

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, index):
        p = self.paths[index]
        image = cv2.imread(p)[:, :, ::-1]
        return {'image': image}

    def sample_name(self, index):
        return self.paths[index].replace('\\', '.').replace('//', '.')

# -*- coding: utf-8 -*-
###############################################################################
#   Copyright (c) 2021 Gaston Alberto Bertolani
#   License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
###############################################################################

import numpy as np
import cv2
from PIL import Image
from operator import xor
import os
import re
from glob import glob


class BackgroundEliminator(object):

    def __init__(self, image_path, save_path=False,
                 no_origin=False, with_groups=False):
        self.image_path = image_path
        self.save_path = save_path
        self.isfile = os.path.isfile(self.image_path)
        self.no_origin = no_origin
        self.with_groups = with_groups

    def _get_img_save_path(self, image_path):
        res = re.search('.*\.(\w{3,4})$', image_path)
        ft = res.group(1)
        if not self.save_path:
            save_path = image_path[:-len(ft)] + 'png'
        elif os.path.isdir(self.save_path):
            # If it is with a group, we create the group
            # of the image in the destination
            dir_to_save = self.save_path
            if self.with_groups:
                base_path = os.path.dirname(image_path)
                category_name = os.path.basename(base_path)
                dir_to_save = os.path.join(self.save_path, category_name)
                try:
                    os.mkdir(dir_to_save)
                except FileExistsError:
                    pass
            image_name = os.path.basename(image_path)[:-len(ft)] + 'png'
            save_path = os.path.join(dir_to_save, image_name)
        else:
            save_path = self.save_path
        return save_path

    def _navigate(self, folder):
        folders = glob(folder + '/*/')
        # Folder is last folder
        if not folders:
            image_path_lst = []
            image_formats = ('*.png', '*.jpg', '*.jpeg', '*.bmp')
            for format in image_formats:
                image_path_lst.extend(glob(folder + '/' + format))
            for i, image_path in enumerate(image_path_lst):
                click.echo("Removing background %s of %s"
                      % (i+1, len(image_path_lst)))
                self._remove_background(image_path)
        else:
            for folder in folders:
                self._navigate(folder)

    def _remove_background(self, image_path):
        img = cv2.imread(image_path)
        # convert to graky
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # threshold input image as mask
        mask = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)[1]

        # negate mask
        mask = 255 - mask

        # apply morphology to remove isolated extraneous noise
        # use borderconstant of black since foreground touches the edges
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # anti-alias the mask -- blur then stretch
        # blur alpha channel
        mask = cv2.GaussianBlur(mask, (0, 0), sigmaX=2, sigmaY=2,
                                borderType=cv2.BORDER_DEFAULT)

        # linear stretch so that 127.5 goes to 0, but 255 stays 255
        mask = (2*(mask.astype(np.float32))-255.0).clip(0, 255).astype(np.uint8)

        # put mask into alpha channel
        result = img.copy()
        result = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
        result[:, :, 3] = mask

        save_path = self._get_img_save_path(image_path)

        cv2.imwrite(save_path, result)

        img = np.array(Image.open(save_path))
        idx = np.where(img[:, :, 3] > 0)
        x0, y0, x1, y1 = idx[1].min(), idx[0].min(), idx[1].max(), idx[0].max()
        out = Image.fromarray(img[y0:y1+1, x0:x1+1, :])
        out.save(save_path)
        if self.no_origin:
            os.remove(image_path)
        return True

    def remove_background(self):
        if self.isfile:
            self._remove_background(self.image_path)
        else:
            self._navigate(self.image_path)
        return True

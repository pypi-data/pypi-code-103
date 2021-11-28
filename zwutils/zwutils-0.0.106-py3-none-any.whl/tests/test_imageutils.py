# -*- coding: utf-8 -*-
import pytest
from PIL import Image

from zwutils import imageutils

def test_image_base64():
    img = Image.open('data/yew.png')
    img_str = imageutils.image_to_base64(img)
    new_img = imageutils.base64_to_image(img_str)
    new_img.show()


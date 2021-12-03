#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:
#   https://pillow.readthedocs.io/en/5.2.x/reference/Image.html#open-rotate-and-display-an-image-using-the-default-viewer

#  from PIL import Image as I
#  import io
#  import requests

#  class Image():

    #  def __init__(self, *args, **kwargs):
        #  self.path = args[0]
        #  if self.path.startswith('http'):
            #  self.is_network = True
            #  res = requests.get(self.path)
            #  self.data = res.content
            #  self.image = I.open(io.BytesIO(self.data))
        #  else:
            #  self.is_local = True
            #  self.image = I.open(self.path)

        #  self.format = self.image.format.lower()
        #  self.size = self.image.size

    #  def save(self, path, size):
        #  self.image.thumbnail(size)
        #  self.image.save(path, self.format)

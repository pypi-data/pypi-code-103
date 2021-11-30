""" Full assembly of the parts to form the complete network """

from .unet_parts import *

import torch
import torch.nn as nn
import torch.nn.functional as F

class Unet(nn.Module):
    def __init__(self, n_channels, n_classes):
        super(Unet, self).__init__()
        self.n_channels = n_channels
        self.n_classes = n_classes

        self.input_image_tile =  Block(self.n_channels,64)  
        self.cont_1 = DownBlock(64,128)
        self.cont_2 = DownBlock(128,256)
        self.cont_3 = DownBlock(256,512)
        self.cont_4 = DownBlock(512,512)
        self.exp_1 =  UpBlock(1024, 256)
        self.exp_2 =  UpBlock(512, 128)
        self.exp_3 =  UpBlock(256, 64)
        self.exp_4 =  UpBlock(128, 64)
        self.output = nn.Conv2d(self.n_channels, self.n_classes, kernel_size=1)
    def forward(self, x):
        x_1 = self.input_image_tile(x)
        x_2 = self.cont_1(x_1)
        x_3 = self.cont_2(x_2)
        x_4 = self.cont_3(x_3)
        x_5 = self.cont_1(x_4)
        x = self.exp_1(x_5,x_4)
        x = self.exp_1(x,x_3)
        x = self.exp_1(x,x_2)
        x = self.exp_1(x,x_1)
        return self.output(x)
             
        
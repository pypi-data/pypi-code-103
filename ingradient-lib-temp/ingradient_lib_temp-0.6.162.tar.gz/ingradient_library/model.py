import torch
import torch.nn as nn
import numpy as np
import torch.nn.functional as F
from torch.autograd import Variable
import math
from functools import partial


class ConvDropoutNormNonlin(nn.Module):
    def __init__(self, input_channels = 4, output_channels = 1,
                 conv_op=nn.Conv3d, conv_kwargs=None,
                 norm_op=nn.InstanceNorm3d, norm_op_kwargs=None,
                 dropout_op=nn.Dropout3d, dropout_op_kwargs=None,
                 nonlin=nn.LeakyReLU, nonlin_kwargs=None):
        super().__init__()
        if nonlin_kwargs is None:
            nonlin_kwargs = {'negative_slope': 1e-2, 'inplace': True}
        if dropout_op_kwargs is None:
            dropout_op_kwargs = {'p': 0.5, 'inplace': True}
        if norm_op_kwargs is None:
            norm_op_kwargs = {'eps': 1e-5, 'affine': True, 'momentum': 0.1}
        if conv_kwargs is None:
            conv_kwargs = {'kernel_size': 3, 'stride': 1, 'padding': 1, 'dilation': 1, 'bias': True}

        self.nonlin_kwargs = nonlin_kwargs
        self.nonlin = nonlin
        self.dropout_op = dropout_op
        self.dropout_op_kwargs = dropout_op_kwargs
        self.norm_op_kwargs = norm_op_kwargs
        self.conv_kwargs = conv_kwargs
        self.conv_op = conv_op
        self.norm_op = norm_op

        self.conv = self.conv_op(input_channels, output_channels, **self.conv_kwargs)
        if self.dropout_op is not None and self.dropout_op_kwargs['p'] is not None and self.dropout_op_kwargs[
            'p'] > 0:
            self.dropout = self.dropout_op(**self.dropout_op_kwargs)
        else:
            self.dropout = None
        self.instnorm = self.norm_op(output_channels, **self.norm_op_kwargs)
        self.lrelu = self.nonlin(**self.nonlin_kwargs)

    def forward(self, x):
        x = self.conv(x)
        if self.dropout is not None:
            x = self.dropout(x)
        return self.lrelu(self.instnorm(x))


class DeepLabV3_CT(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.deeplab = torch.hub.load('pytorch/vision:v0.10.0', 'deeplabv3_resnet50', pretrained=True)
        self.deeplab.backbone.conv1 = nn.Conv2d(in_channels, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), bias=False)
        self.deeplab.aux_classifier[-1] = nn.Conv2d(512, out_channels, kernel_size=(1,1), stride=(1,1))
        

    def forward(self, input, hidden):
        
        input = self.deeplab.backbone(input)
        input = self.deeplab.classifier(input)



class DeepSuperVisionUNet2dot5(nn.Module):
    def __init__(self, n_modalities = 1, depth = 256, fianl_output_channels = 2, patch_size = (256,512,512)):
        conv_kwargs1 = {'kernel_size' : 3, 'padding' : 1, 'stride' : 1}
        encoder_channel1 = 64
        encoder_channel2 = encoder_channel1 * 2
        encoder_channel3 = encoder_channel2 * 2
        encoder_channel4 = encoder_channel3 * 2
        encoder_channel5 = encoder_channel4 * 2

        self.encoder1 = nn.Sequential(
            ConvDropoutNormNonlin(n_modalities * depth, encoder_channel1, conv_kwargs= conv_kwargs1, conv_op = nn.Conv2d, norm_op = nn.InstanceNorm2d, dropout_op = nn.Dropout2d),
            ConvDropoutNormNonlin(encoder_channel1, encoder_channel1, conv_kwargs = conv_kwargs1, conv_op = nn.Conv2d, norm_op = nn.InstanceNorm2d, dropout_op = nn.Dropout2d)
        )
        conv_kwargs1 = {'kernel_size' : 3, 'padding' : 1, 'stride' : 2}
        conv_kwargs2 = {'kernel_size' : 3, 'padding' : 1, 'stride' : 1}
        self.encoder2 = nn.Sequential(
            ConvDropoutNormNonlin(encoder_channel1, encoder_channel2, conv_kwargs= conv_kwargs1, conv_op = nn.Conv2d, norm_op = nn.InstanceNorm2d, dropout_op = nn.Dropout2d),
            ConvDropoutNormNonlin(encoder_channel2, encoder_channel2, conv_kwargs= conv_kwargs2, conv_op = nn.Conv2d, norm_op = nn.InstanceNorm2d, dropout_op = nn.Dropout2d)
        )
        self.encoder3 = nn.Sequential(
            ConvDropoutNormNonlin(encoder_channel2, encoder_channel3, conv_kwargs= conv_kwargs1, conv_op = nn.Conv2d, norm_op = nn.InstanceNorm2d, dropout_op = nn.Dropout2d),
            ConvDropoutNormNonlin(encoder_channel3, encoder_channel3, conv_kwargs= conv_kwargs2, conv_op = nn.Conv2d, norm_op = nn.InstanceNorm2d, dropout_op = nn.Dropout2d)
        )
        self.encoder4 = nn.Sequential(
            ConvDropoutNormNonlin(encoder_channel3, encoder_channel4, conv_kwargs= conv_kwargs1, conv_op = nn.Conv2d, norm_op = nn.InstanceNorm2d, dropout_op = nn.Dropout2d),
            ConvDropoutNormNonlin(encoder_channel4, encoder_channel4, conv_kwargs= conv_kwargs2, conv_op = nn.Conv2d, norm_op = nn.InstanceNorm2d, dropout_op = nn.Dropout2d)
        )
        self.encoder5 = nn.Sequential(
            ConvDropoutNormNonlin(encoder_channel4, encoder_channel5, conv_kwargs= conv_kwargs1, conv_op = nn.Conv2d, norm_op = nn.InstanceNorm2d, dropout_op = nn.Dropout2d),
            ConvDropoutNormNonlin(encoder_channel5, encoder_channel5, conv_kwargs= conv_kwargs2, conv_op = nn.Conv2d, norm_op = nn.InstanceNorm2d, dropout_op = nn.Dropout2d)
        )
    


class Deep_Supervision_UNet3d_Narrow(nn.Module):
    def __init__(self, n_modalities = 4, final_output_channels = 5, patch_size = (128, 128, 128), is_binary = False):
        super().__init__()
        self.patch_size = np.array(patch_size)
        self.networks_depth = self.get_networks_depth()
        self.encoder_blocks = []
        self.decoder_blocks = []
        self.upsample_operations = []
        self.final_output_channels = final_output_channels
        self.is_binary = is_binary
        
        conv_kwargs1 = {'kernel_size' : 3, 'padding' : 1, 'stride' : 1}
        self.encoder1 = nn.Sequential(
            ConvDropoutNormNonlin(n_modalities, 32, conv_kwargs= conv_kwargs1, conv_op = nn.Conv3d),
            ConvDropoutNormNonlin(32, 32, conv_kwargs = conv_kwargs1, conv_op = nn.Conv3d)
        )
        conv_kwargs1 = {'kernel_size' : 3, 'padding' : 1, 'stride' : 2}
        conv_kwargs2 = {'kernel_size' : 3, 'padding' : 1, 'stride' : 1}
        self.encoder2 = nn.Sequential(
            ConvDropoutNormNonlin(32, 64, conv_kwargs= conv_kwargs1, conv_op = nn.Conv3d),
            ConvDropoutNormNonlin(64, 64, conv_kwargs= conv_kwargs2, conv_op = nn.Conv3d)
        )
        self.encoder3 = nn.Sequential(
            ConvDropoutNormNonlin(64, 128, conv_kwargs= conv_kwargs1, conv_op = nn.Conv3d),
            ConvDropoutNormNonlin(128, 128, conv_kwargs= conv_kwargs2, conv_op = nn.Conv3d)
        )
        self.encoder4 = nn.Sequential(
            ConvDropoutNormNonlin(128, 256, conv_kwargs= conv_kwargs1, conv_op = nn.Conv3d),
            ConvDropoutNormNonlin(256, 256, conv_kwargs= conv_kwargs2, conv_op = nn.Conv3d)
        )
        self.encoder5 = nn.Sequential(
            ConvDropoutNormNonlin(256, 320, conv_kwargs= conv_kwargs2, conv_op = nn.Conv3d),
            ConvDropoutNormNonlin(320, 320, conv_kwargs= conv_kwargs2, conv_op = nn.Conv3d)
        )

        conv_kwargs1 = {'kernel_size' : 3, 'padding' : 1,  'stride' : 1}
        conv_kwargs2 = {'kernel_size' : 3, 'stride' : 1, 'padding':1}
        transp_kwargs = {'kernel_size' : 2, 'stride' : 1, 'stride' : 2}


        self.decoder1_trans = ConvDropoutNormNonlin(320, 256, conv_kwargs= conv_kwargs1, conv_op = nn.Conv3d)
        self.decoder1_conv = nn.Sequential(
            ConvDropoutNormNonlin(256*2, 256, conv_kwargs= conv_kwargs1, conv_op = nn.Conv3d),
            ConvDropoutNormNonlin(256, 256, conv_kwargs = conv_kwargs2, conv_op = nn.Conv3d)
        )
        self.decoder2_trans = ConvDropoutNormNonlin(256, 128, conv_kwargs= transp_kwargs, conv_op = nn.ConvTranspose3d)
        self.decoder2_conv = nn.Sequential(
            ConvDropoutNormNonlin(128*2, 128 , conv_kwargs= conv_kwargs1, conv_op = nn.Conv3d),
            ConvDropoutNormNonlin(128, 128, conv_kwargs= conv_kwargs2, conv_op = nn.Conv3d)
        )
        self.decoder3_trans = ConvDropoutNormNonlin(128, 64, conv_kwargs= transp_kwargs, conv_op = nn.ConvTranspose3d)
        self.decoder3_conv = nn.Sequential(
            ConvDropoutNormNonlin(64*2, 64, conv_kwargs= conv_kwargs1, conv_op = nn.Conv3d),
            ConvDropoutNormNonlin(64, 64, conv_kwargs= conv_kwargs2, conv_op = nn.Conv3d)
        )
        self.decoder4_trans = ConvDropoutNormNonlin(64, 32, conv_kwargs= transp_kwargs, conv_op = nn.ConvTranspose3d)
        self.decoder4_conv = nn.Sequential(
            ConvDropoutNormNonlin(32*2, 32, conv_kwargs= conv_kwargs1, conv_op = nn.Conv3d),
            ConvDropoutNormNonlin(32, 32, conv_kwargs= conv_kwargs2, conv_op = nn.Conv3d)
        )


        self.final_layer1 = nn.Sequential(
            nn.Conv3d(32, final_output_channels, 3, 1, 1)
            )
        self.final_layer2 = nn.Sequential(
            nn.Conv3d(64, final_output_channels, 3, 1, 1)
            )
        self.final_layer3 = nn.Sequential(
            nn.Conv3d(128, final_output_channels, 3, 1, 1)
            )
        self.final_layer4 = nn.Sequential(
            nn.Conv3d(256, final_output_channels, 3, 1, 1)
            )

        self.upsample4 = nn.Upsample(scale_factor=8, mode = 'trilinear')
        self.upsample3 = nn.Upsample(scale_factor=4, mode = 'trilinear')
        self.upsample2 = nn.Upsample(scale_factor=2, mode = 'trilinear')
        
    
    def forward(self, x):
        bs, nc, nx, ny, nz  = x.shape
        x1 = self.encoder1(x)
        x2 = self.encoder2(x1)
        x3 = self.encoder3(x2)
        x4 = self.encoder4(x3)
        x5 = self.encoder5(x4)
        x4_ = self.decoder1_conv(torch.cat((x4, self.decoder1_trans(x5)), dim = 1))
        x3_ = self.decoder2_conv(torch.cat((x3, self.decoder2_trans(x4_)), dim = 1))
        x2_ = self.decoder3_conv(torch.cat((x2, self.decoder3_trans(x3_)), dim = 1))
        x1_ = self.decoder4_conv(torch.cat((x1, self.decoder4_trans(x2_)), dim = 1))

        if not self.is_binary:
            x1_ = F.softmax(self.final_layer1(x1_).view(bs, self.final_output_channels, -1), dim = 1).view(bs, self.final_output_channels, nx, ny, nz)
            x2_ = F.softmax(self.upsample2(self.final_layer2(x2_)).view(bs, self.final_output_channels, -1), dim = 1).view(bs, self.final_output_channels, nx, ny, nz)
            x3_ = F.softmax(self.upsample3(self.final_layer3(x3_)).view(bs, self.final_output_channels, -1), dim = 1).view(bs, self.final_output_channels, nx, ny, nz)
            x4_ = F.softmax(self.upsample4(self.final_layer4(x4_)).view(bs, self.final_output_channels, -1), dim = 1).view(bs, self.final_output_channels, nx, ny, nz)
        else:
            x1_ = torch.sigmoid(self.final_layer1(x1_).view(bs, self.final_output_channels, -1)).view(bs, self.final_output_channels, nx, ny, nz)
            x2_ = torch.sigmoid(self.upsample2(self.final_layer2(x2_)).view(bs, self.final_output_channels, -1)).view(bs, self.final_output_channels, nx, ny, nz)
            x3_ = torch.sigmoid(self.upsample3(self.final_layer3(x3_)).view(bs, self.final_output_channels, -1)).view(bs, self.final_output_channels, nx, ny, nz)
            x4_ = torch.sigmoid(self.upsample4(self.final_layer4(x4_)).view(bs, self.final_output_channels, -1)).view(bs, self.final_output_channels, nx, ny, nz)
        
        result = torch.stack([x1_, x2_, x3_, x4_]).permute(1,0,2,3,4,5)
        
        return result.contiguous()
                
    def get_networks_depth(self):
        min_patch_axis = np.min(self.patch_size)
        return np.clip(np.log2(min_patch_axis), 0, 6).astype(int)
    

class Deep_Supervision_UNet3d(nn.Module):
    def __init__(self, in_channels = 1, out_channels = 2, patch_size = (128, 128, 128), is_binary = False):
        super().__init__()
        self.patch_size = np.array(patch_size)
        self.networks_depth = self.get_networks_depth()
        self.encoder_blocks = []
        self.decoder_blocks = []
        self.upsample_operations = []
        self.final_output_channels = out_channels
        self.is_binary = is_binary
        
        conv_kwargs1 = {'kernel_size' : 3, 'padding' : 1, 'stride' : 1}
        self.encoder1 = nn.Sequential(
            ConvDropoutNormNonlin(in_channels, 32, conv_kwargs= conv_kwargs1, conv_op = nn.Conv3d),
            ConvDropoutNormNonlin(32, 32, conv_kwargs = conv_kwargs1, conv_op = nn.Conv3d)
        )
        conv_kwargs1 = {'kernel_size' : 3, 'padding' : 1, 'stride' : 2}
        conv_kwargs2 = {'kernel_size' : 3, 'padding' : 1, 'stride' : 1}
        self.encoder2 = nn.Sequential(
            ConvDropoutNormNonlin(32, 64, conv_kwargs= conv_kwargs1, conv_op = nn.Conv3d),
            ConvDropoutNormNonlin(64, 64, conv_kwargs= conv_kwargs2, conv_op = nn.Conv3d)
        )
        self.encoder3 = nn.Sequential(
            ConvDropoutNormNonlin(64, 128, conv_kwargs= conv_kwargs1, conv_op = nn.Conv3d),
            ConvDropoutNormNonlin(128, 128, conv_kwargs= conv_kwargs2, conv_op = nn.Conv3d)
        )
        self.encoder4 = nn.Sequential(
            ConvDropoutNormNonlin(128, 256, conv_kwargs= conv_kwargs1, conv_op = nn.Conv3d),
            ConvDropoutNormNonlin(256, 256, conv_kwargs= conv_kwargs2, conv_op = nn.Conv3d)
        )
        self.encoder5 = nn.Sequential(
            ConvDropoutNormNonlin(256, 320, conv_kwargs= conv_kwargs1, conv_op = nn.Conv3d),
            ConvDropoutNormNonlin(320, 320, conv_kwargs= conv_kwargs2, conv_op = nn.Conv3d)
        )

        conv_kwargs1 = {'kernel_size' : 3, 'padding' : 1,  'stride' : 1}
        conv_kwargs2 = {'kernel_size' : 3, 'stride' : 1, 'padding':1}
        transp_kwargs = {'kernel_size' : 2, 'stride' : 1, 'stride' : 2}


        self.decoder1_trans = ConvDropoutNormNonlin(320, 256, conv_kwargs= transp_kwargs, conv_op = nn.ConvTranspose3d)
        self.decoder1_conv = nn.Sequential(
            ConvDropoutNormNonlin(256*2, 256, conv_kwargs= conv_kwargs1, conv_op = nn.Conv3d),
            ConvDropoutNormNonlin(256, 256, conv_kwargs = conv_kwargs2, conv_op = nn.Conv3d)
        )
        self.decoder2_trans = ConvDropoutNormNonlin(256, 128, conv_kwargs= transp_kwargs, conv_op = nn.ConvTranspose3d)
        self.decoder2_conv = nn.Sequential(
            ConvDropoutNormNonlin(128*2, 128 , conv_kwargs= conv_kwargs1, conv_op = nn.Conv3d),
            ConvDropoutNormNonlin(128, 128, conv_kwargs= conv_kwargs2, conv_op = nn.Conv3d)
        )
        self.decoder3_trans = ConvDropoutNormNonlin(128, 64, conv_kwargs= transp_kwargs, conv_op = nn.ConvTranspose3d)
        self.decoder3_conv = nn.Sequential(
            ConvDropoutNormNonlin(64*2, 64, conv_kwargs= conv_kwargs1, conv_op = nn.Conv3d),
            ConvDropoutNormNonlin(64, 64, conv_kwargs= conv_kwargs2, conv_op = nn.Conv3d)
        )
        self.decoder4_trans = ConvDropoutNormNonlin(64, 32, conv_kwargs= transp_kwargs, conv_op = nn.ConvTranspose3d)
        self.decoder4_conv = nn.Sequential(
            ConvDropoutNormNonlin(32*2, 32, conv_kwargs= conv_kwargs1, conv_op = nn.Conv3d),
            ConvDropoutNormNonlin(32, 32, conv_kwargs= conv_kwargs2, conv_op = nn.Conv3d)
        )

        self.final_layer1 = nn.Sequential(
            nn.Conv3d(32, out_channels, kernel_size = 1, stride = 1, padding = 0)
            )
        self.final_layer2 = nn.Sequential(
            nn.Conv3d(64, out_channels, kernel_size = 1, stride = 1, padding = 0)
            )
        self.final_layer3 = nn.Sequential(
            nn.Conv3d(128, out_channels, kernel_size = 1, stride = 1, padding = 0)
            )
        self.final_layer4 = nn.Sequential(
            nn.Conv3d(256, out_channels, kernel_size = 1, stride = 1, padding = 0)
            )

        self.upsample4 = nn.Upsample(scale_factor=8, mode = 'trilinear')
        self.upsample3 = nn.Upsample(scale_factor=4, mode = 'trilinear')
        self.upsample2 = nn.Upsample(scale_factor=2, mode = 'trilinear')
        
    
    def forward(self, x):
        bs, nc, nx, ny, nz  = x.shape
        x1 = self.encoder1(x)
        x2 = self.encoder2(x1)
        x3 = self.encoder3(x2)
        x4 = self.encoder4(x3)
        x5 = self.encoder5(x4)

        x4_ = self.decoder1_conv(torch.cat((x4, self.decoder1_trans(x5)), dim = 1))
        x3_ = self.decoder2_conv(torch.cat((x3, self.decoder2_trans(x4_)), dim = 1))
        x2_ = self.decoder3_conv(torch.cat((x2, self.decoder3_trans(x3_)), dim = 1))
        x1_ = self.decoder4_conv(torch.cat((x1, self.decoder4_trans(x2_)), dim = 1))

        if not self.is_binary:
            x1_ = F.softmax(self.final_layer1(x1_).view(bs, self.final_output_channels, -1), dim = 1).view(bs, self.final_output_channels, nx, ny, nz)
            x2_ = F.softmax(self.upsample2(self.final_layer2(x2_)).view(bs, self.final_output_channels, -1), dim = 1).view(bs, self.final_output_channels, nx, ny, nz)
            x3_ = F.softmax(self.upsample3(self.final_layer3(x3_)).view(bs, self.final_output_channels, -1), dim = 1).view(bs, self.final_output_channels, nx, ny, nz)
            x4_ = F.softmax(self.upsample4(self.final_layer4(x4_)).view(bs, self.final_output_channels, -1), dim = 1).view(bs, self.final_output_channels, nx, ny, nz)
        

        else:
            x1_ = torch.sigmoid(self.final_layer1(x1_).view(bs, self.final_output_channels, -1)).view(bs, self.final_output_channels, nx, ny, nz)
            x2_ = torch.sigmoid(self.upsample2(self.final_layer2(x2_)).view(bs, self.final_output_channels, -1)).view(bs, self.final_output_channels, nx, ny, nz)
            x3_ = torch.sigmoid(self.upsample3(self.final_layer3(x3_)).view(bs, self.final_output_channels, -1)).view(bs, self.final_output_channels, nx, ny, nz)
            x4_ = torch.sigmoid(self.upsample4(self.final_layer4(x4_)).view(bs, self.final_output_channels, -1)).view(bs, self.final_output_channels, nx, ny, nz)
        
        result = torch.stack([x1_, x2_, x3_, x4_]).permute(1,0,2,3,4,5)
        
        return result.contiguous()
                
    def get_networks_depth(self):
        min_patch_axis = np.min(self.patch_size)
        return np.clip(np.log2(min_patch_axis), 0, 6).astype(int)
    


class Interactive_Model(nn.Module):
    def __init__(self, n_modalities = 1, point_channel = 2, patch_size = (320,256,256), final_output_channels = 1):
        super().__init__()
        kwargs = {'sample_input_D':patch_size[0], 'sample_input_H':patch_size[1], 'sample_input_W':patch_size[2],'num_seg_classes':1}
        self.model = resnet10(**kwargs)
        input = n_modalities + final_output_channels + point_channel

        self.point_layers = nn.Sequential(
            nn.Conv3d(1, point_channel, 1, 1, 0),
            nn.InstanceNorm3d(point_channel),
            nn.LeakyReLU(),
            nn.Conv3d(point_channel, point_channel, 3, 1, 1),
            nn.InstanceNorm3d(point_channel),
            nn.LeakyReLU(),
            
        )
        self.initial_layer = nn.Sequential(
            nn.Conv3d(input, 3, 3, 1, 1),
            nn.InstanceNorm3d(32),
            nn.LeakyReLU(),
            nn.Conv3d(3, 1, 3, 1, 1),
            nn.InstanceNorm3d(final_output_channels),
            nn.LeakyReLU(),
            )
        self.final_upsample = nn.Upsample(scale_factor=4, mode = 'trilinear')
        
        
    
    def forward(self, x, positive_points, negative_points, prev_seg = None):
        bs, nc, nx, ny, nz  = x.shape
        if prev_seg == None:
            prev_seg = torch.zeros((bs, 1, nx, ny, nz)).to(x.device.index)
        point = self.point_layers((positive_points - negative_points).unsqueeze(1))
        
        x = torch.cat((x, point), dim = 1)
        x = torch.cat((x, prev_seg), dim = 1)
        x = self.initial_layer(x)
        x = self.model(x)
        x = self.final_upsample(x)

        return torch.sigmoid(x)




class Daegu_Model10(nn.Module):
    def __init__(self, patch_size, resnet_output = 4):
        super().__init__()
        resnet_output = resnet_output
        out_tconv1 = resnet_output//2
        out_tconv2 = out_tconv1//2
        kwargs = {'sample_input_D':patch_size[0], 'sample_input_H':patch_size[1], 'sample_input_W':patch_size[2],'num_seg_classes':resnet_output}
        self.model = resnet10(**kwargs)

        self.upsample1 = nn.Sequential(nn.ConvTranspose3d(in_channels = resnet_output, out_channels= out_tconv1, kernel_size =3 , stride = 2, padding = 1, output_padding =1),
                                       nn.InstanceNorm3d(out_tconv1),
                                       nn.LeakyReLU())
        
        self.upsample2 = nn.Sequential(nn.ConvTranspose3d(in_channels = out_tconv1, out_channels= out_tconv2, kernel_size =3 , stride = 2, padding = 1, output_padding =1),
                                       nn.InstanceNorm3d(out_tconv2),
                                       nn.LeakyReLU())
        
        self.final_layer = nn.Sequential(nn.Conv3d(in_channels = out_tconv2, out_channels = 2, kernel_size = 3, stride = 1, padding = 1),
                                   nn.InstanceNorm3d(2),
                                   nn.LeakyReLU())

    def forward(self, X):
        X = self.model(X)
        X = self.upsample1(X)
        X = self.upsample2(X)
        X = self.final_layer(X)
        return torch.softmax(X, dim = -1)

class Daegu_Model34(nn.Module):
    def __init__(self, patch_size, input_channel = 1, output_channel= 2):
        super().__init__()
        out_channel1 = 1
        out_channel2 = out_channel1 * 4

        self.a_conv1 = nn.Sequential(nn.Conv3d(in_channels = input_channel, out_channels = out_channel1, kernel_size = 3, stride = 1, padding = 6, dilation = 6),
                                   nn.InstanceNorm3d(out_channel1),
                                   nn.LeakyReLU())
        self.a_conv2 = nn.Sequential(nn.Conv3d(in_channels = input_channel, out_channels = out_channel1, kernel_size = 3, stride = 1, padding = 12, dilation = 12),
                                   nn.InstanceNorm3d(out_channel1),
                                   nn.LeakyReLU())
        self.a_conv3 = nn.Sequential(nn.Conv3d(in_channels = input_channel, out_channels = out_channel1, kernel_size = 3, stride = 1, padding = 18, dilation = 18),
                                   nn.InstanceNorm3d(out_channel1),
                                   nn.LeakyReLU())
        self.a_conv4 = nn.Sequential(nn.Conv3d(in_channels = input_channel, out_channels = out_channel1, kernel_size = 1, stride = 1, padding = 0, dilation = 1),
                                   nn.InstanceNorm3d(out_channel1),
                                   nn.LeakyReLU())

        self.a_conv2_1 = nn.Sequential(nn.Conv3d(in_channels = out_channel2, out_channels = out_channel2, kernel_size = 1, stride = 1, padding = 0, dilation = 1),
                                   nn.InstanceNorm3d(out_channel2),
                                   nn.LeakyReLU())

        self.last_layer = nn.Sequential(nn.Conv3d(in_channels = out_channel2, out_channels = output_channel, kernel_size = 1, stride = 1, padding = 0, dilation = 1),
                                   nn.InstanceNorm3d(output_channel),
                                   nn.LeakyReLU())


    def forward(self, X):
        X1 = self.a_conv1(X)
        X2 = self.a_conv2(X)
        X3 = self.a_conv3(X)
        X4 = self.a_conv4(X)

        X = torch.cat((X1,X2,X3,X4), dim = 1)
        X = self.a_conv2_1(X)
        X = self.last_layer(X)
        return torch.softmax(X, dim = -1)




def conv3x3x3(in_planes, out_planes, stride=1, dilation=1):
    # 3x3x3 convolution with padding
    return nn.Conv3d(
        in_planes,
        out_planes,
        kernel_size=3,
        dilation=dilation,
        stride=stride,
        padding=dilation,
        bias=False)


def downsample_basic_block(x, planes, stride, no_cuda=False):
    out = F.avg_pool3d(x, kernel_size=1, stride=stride)
    zero_pads = torch.Tensor(
        out.size(0), planes - out.size(1), out.size(2), out.size(3),
        out.size(4)).zero_()
    if not no_cuda:
        if isinstance(out.data, torch.cuda.FloatTensor):
            zero_pads = zero_pads.cuda()

    out = Variable(torch.cat([out.data, zero_pads], dim=1))

    return out


class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, inplanes, planes, stride=1, dilation=1, downsample=None):
        super(BasicBlock, self).__init__()
        self.conv1 = conv3x3x3(inplanes, planes, stride=stride, dilation=dilation)
        self.bn1 = nn.BatchNorm3d(planes)
        self.relu = nn.LeakyReLU(inplace = True)
        self.conv2 = conv3x3x3(planes, planes, dilation=dilation)
        self.bn2 = nn.BatchNorm3d(planes)
        self.downsample = downsample
        self.stride = stride
        self.dilation = dilation

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.conv2(out)
        out = self.bn2(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual
        out = self.relu(out)

        return out


class Bottleneck(nn.Module):
    expansion = 4

    def __init__(self, inplanes, planes, stride=1, dilation=1, downsample=None):
        super(Bottleneck, self).__init__()
        self.conv1 = nn.Conv3d(inplanes, planes, kernel_size=1, bias=False)
        self.bn1 = nn.BatchNorm3d(planes)
        self.conv2 = nn.Conv3d(
            planes, planes, kernel_size=3, stride=stride, dilation=dilation, padding=dilation, bias=False)
        self.bn2 = nn.BatchNorm3d(planes)
        self.conv3 = nn.Conv3d(planes, planes * 4, kernel_size=1, bias=False)
        self.bn3 = nn.BatchNorm3d(planes * 4)
        self.relu = nn.LeakyReLU(inplace=True)
        self.downsample = downsample
        self.stride = stride
        self.dilation = dilation

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)

        out = self.conv3(out)
        out = self.bn3(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual
        out = self.relu(out)

        return out


class ResNet(nn.Module):

    def __init__(self,
                 block,
                 layers,
                 sample_input_D,
                 sample_input_H,
                 sample_input_W,
                 num_seg_classes,
                 shortcut_type='B',
                 no_cuda = False):
        self.inplanes = 64
        self.no_cuda = no_cuda
        super(ResNet, self).__init__()
        self.conv1 = nn.Conv3d(
            1,
            64,
            kernel_size=7,
            stride=(2, 2, 2),
            padding=(3, 3, 3),
            bias=False)
            
        self.bn1 = nn.BatchNorm3d(64)
        self.relu = nn.LeakyReLU(inplace=True)
        self.maxpool = nn.MaxPool3d(kernel_size=(3, 3, 3), stride=2, padding=1)
        self.layer1 = self._make_layer(block, 64, layers[0], shortcut_type)
        self.layer2 = self._make_layer(
            block, 128, layers[1], shortcut_type, stride=2)
        self.layer3 = self._make_layer(
            block, 256, layers[2], shortcut_type, stride=1, dilation=2)
        self.layer4 = self._make_layer(
            block, 512, layers[3], shortcut_type, stride=1, dilation=4)

        self.conv_seg = nn.Sequential(
                                        nn.ConvTranspose3d(
                                        512 * block.expansion,
                                        32,
                                        2,
                                        stride=2
                                        ),
                                        nn.BatchNorm3d(32),
                                        nn.LeakyReLU(inplace=True),
                                        nn.Conv3d(
                                        32,
                                        32,
                                        kernel_size=3,
                                        stride=(1, 1, 1),
                                        padding=(1, 1, 1),
                                        bias=False), 
                                        nn.BatchNorm3d(32),
                                        nn.LeakyReLU(inplace=True),
                                        nn.Conv3d(
                                        32,
                                        num_seg_classes,
                                        kernel_size=1,
                                        stride=(1, 1, 1),
                                        bias=False) 
                                        )

        for m in self.modules():
            if isinstance(m, nn.Conv3d):
                m.weight = nn.init.kaiming_normal(m.weight, mode='fan_out')

    def _make_layer(self, block, planes, blocks, shortcut_type, stride=1, dilation=1):
        downsample = None
        if stride != 1 or self.inplanes != planes * block.expansion:
            if shortcut_type == 'A':
                downsample = partial(
                    downsample_basic_block,
                    planes=planes * block.expansion,
                    stride=stride,
                    no_cuda=self.no_cuda)
            else:
                downsample = nn.Sequential(
                    nn.Conv3d(
                        self.inplanes,
                        planes * block.expansion,
                        kernel_size=1,
                        stride=stride,
                        bias=False), nn.BatchNorm3d(planes * block.expansion))

        layers = []
        layers.append(block(self.inplanes, planes, stride=stride, dilation=dilation, downsample=downsample))
        self.inplanes = planes * block.expansion
        for i in range(1, blocks):
            layers.append(block(self.inplanes, planes, dilation=dilation))

        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.conv_seg(x)

        return x


def resnet10(**kwargs):
    """Constructs a ResNet-10 model.
    """
    model = ResNet(BasicBlock, [1, 1, 1, 1], **kwargs)
    return model


def resnet18(**kwargs):
    """Constructs a ResNet-18 model.
    """
    model = ResNet(BasicBlock, [2, 2, 2, 2], **kwargs)
    return model


def resnet34(**kwargs):
    """Constructs a ResNet-34 model.
    """
    model = ResNet(BasicBlock, [3, 4, 6, 3], **kwargs)
    return model


def resnet50(**kwargs):
    """Constructs a ResNet-50 model.
    """
    model = ResNet(Bottleneck, [3, 4, 6, 3], **kwargs)
    return model


def resnet101(**kwargs):
    """Constructs a ResNet-101 model.
    """
    model = ResNet(Bottleneck, [3, 4, 23, 3], **kwargs)
    return model


def resnet152(**kwargs):
    """Constructs a ResNet-101 model.
    """
    model = ResNet(Bottleneck, [3, 8, 36, 3], **kwargs)
    return model


def resnet200(**kwargs):
    """Constructs a ResNet-101 model.
    """
    model = ResNet(Bottleneck, [3, 24, 36, 3], **kwargs)
    return model
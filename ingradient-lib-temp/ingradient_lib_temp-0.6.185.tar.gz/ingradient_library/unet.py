import torch.nn as nn
import torch
import torch.nn.functional as F
from torch.utils.checkpoint import checkpoint_sequential
from ingradient_library.block import *


class CheckPointNet(nn.Module):
    def __init__(self, in_channels = 1, out_channels = 2, n_channels = 32, segment = 8):
        super().__init__()
        self.model = nn.Sequential(nn.Conv3d(in_channels, n_channels, kernel_size = 3, stride = 1, padding = 1, dilation = 1),
                        nn.Dropout3d(),
                        nn.InstanceNorm3d(n_channels),
                        nn.LeakyReLU(),
                        nn.Conv3d(n_channels, n_channels, kernel_size = 3, stride = 1, padding = 24, dilation = 24),
                        nn.Dropout3d(),
                        nn.InstanceNorm3d(n_channels),
                        nn.LeakyReLU(),
                        nn.Conv3d(n_channels, n_channels, kernel_size = 3, stride = 1, padding = 18, dilation = 18),
                        nn.Dropout3d(),
                        nn.InstanceNorm3d(n_channels),
                        nn.LeakyReLU(),
                        nn.Conv3d(n_channels, n_channels, kernel_size = 3, stride = 1, padding = 12, dilation = 12),
                        nn.Dropout3d(),
                        nn.InstanceNorm3d(n_channels),
                        nn.LeakyReLU(),
                        nn.Conv3d(n_channels, n_channels, kernel_size = 3, stride = 1, padding = 6, dilation = 6),
                        nn.Dropout3d(),
                        nn.InstanceNorm3d(n_channels),
                        nn.LeakyReLU(),
                        nn.Conv3d(n_channels, n_channels, kernel_size = 3, stride = 1, padding = 1, dilation = 1),
                        nn.Dropout3d(),
                        nn.InstanceNorm3d(n_channels),
                        nn.LeakyReLU(),
                        nn.Conv3d(n_channels, n_channels, kernel_size = 1, stride = 1, padding = 0, dilation = 1),
                        nn.Dropout3d(),
                        nn.InstanceNorm3d(n_channels),
                        nn.LeakyReLU(),
                        nn.Conv3d(n_channels, out_channels, kernel_size = 1, stride = 1, padding = 0, dilation = 1)
                        )
        self.segment = segment

    def forward(self, X):
        if self.segment != 0:
            X = checkpoint_sequential(self.model, self.segment, X)
        
        else:
            X = self.model(X)

        return X

class UNet3d_Plus(nn.Module):
    def __init__(self, in_channels = 1, out_channels = 2, n_channels = 32, channel_bound = 320, vectorization = True):
        super().__init__()
        self.expand_channels = encoder_block(in_channels, n_channels, stride = 1)
        self.conv_downsample1 = encoder_block(n_channels, n_channels * 2)
        self.conv_downsample2 = encoder_block(n_channels * 2, n_channels * 4)
        self.conv_downsample3 = encoder_block(n_channels * 4, n_channels * 8)
        self.conv_downsample4 = encoder_block(n_channels * 8, channel_bound)

        self.conv_upsample1 = nn.ConvTranspose3d(channel_bound, n_channels * 8, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)
        self.conv_upsample2= nn.ConvTranspose3d(n_channels * 8, n_channels * 4, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)
        self.conv_upsample3= nn.ConvTranspose3d(n_channels * 4, n_channels * 2, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)
        self.conv_upsample4= nn.ConvTranspose3d(n_channels * 2, n_channels, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)

        self.decoder1 = encoder_block(n_channels * 1 * 2, n_channels, stride = 1)
        self.decoder2 = encoder_block(n_channels * 2 * 2, n_channels * 2, stride = 1)
        self.decoder3 = encoder_block(n_channels * 4 * 2, n_channels * 4, stride = 1)
        self.decoder4 = encoder_block(n_channels * 8 * 2, n_channels * 8, stride = 1)
        
        self.classifier1 = nn.Conv3d(n_channels, out_channels, kernel_size = 1)
        self.classifier2 = nn.Conv3d(n_channels * 2, out_channels, kernel_size = 1)
        self.classifier3 = nn.Conv3d(n_channels * 4, out_channels, kernel_size = 1)
        self.classifier4 = nn.Conv3d(n_channels * 8, out_channels, kernel_size = 1)

        self.upsample4 = nn.Upsample(scale_factor=8)
        self.upsample3 = nn.Upsample(scale_factor=4)
        self.upsample2 = nn.Upsample(scale_factor=2)
        self.vectorization = vectorization

    
    def forward(self, x):
        x = self.expand_channels(x)
        x_downsample1 = self.conv_downsample1(x)
        x_downsample2 = self.conv_downsample2(x_downsample1)
        x_downsample3 = self.conv_downsample3(x_downsample2)
        x_downsample4 = self.conv_downsample4(x_downsample3)

        x_downsample4_up = self.conv_upsample1(x_downsample4)
        l4_output = self.decoder4(torch.cat((x_downsample4_up, x_downsample3), dim = 1))
        x_downsample3_up = self.conv_upsample2(l4_output)
        l3_output = self.decoder3(torch.cat((x_downsample3_up, x_downsample2), dim = 1))
        x_downsample2_up = self.conv_upsample3(l3_output)
        l2_output = self.decoder2(torch.cat((x_downsample2_up, x_downsample1), dim = 1))
        x_downsample1_up = self.conv_upsample4(l2_output)
        l1_output = self.decoder1(torch.cat((x_downsample1_up, x), dim = 1))

        l1_output = self.classifier1(l1_output)
        l2_output = self.upsample2(self.classifier2(l2_output))
        l3_output = self.upsample3(self.classifier3(l3_output))
        l4_output = self.upsample4(self.classifier4(l4_output))

        if self.vectorization:
            l1_output = torch.softmax(l1_output , dim = 1)
            l2_output = torch.softmax(l2_output , dim = 1)
            l3_output = torch.softmax(l3_output , dim = 1)
            l4_output = torch.softmax(l4_output , dim = 1)
            result = torch.stack([l1_output, l2_output, l3_output, l4_output]).permute(1,0,2,3,4,5)
            
            return result.contiguous()

        
        return [l1_output, l2_output, l3_output, l4_output]



class UNet3d_MultiModal(nn.Module):
    def __init__(self, in_channels = 1, out_channels = 2, n_channels = 32, channel_bound = 320):
        super().__init__()
        channel_bound = min(n_channels * 16, channel_bound)
        self.expand_channels_CT = encoder_block(in_channels, n_channels, stride = 1)
        self.conv_downsample1_CT = encoder_block(n_channels, n_channels * 2)
        self.conv_downsample2_CT = encoder_block(n_channels * 2, n_channels * 4)
        self.conv_downsample3_CT = encoder_block(n_channels * 4, n_channels * 8)
        self.conv_downsample4_CT = encoder_block(n_channels * 8, channel_bound)

        self.conv_upsample1_CT = nn.ConvTranspose3d(channel_bound, n_channels * 8, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)
        self.conv_upsample2_CT= nn.ConvTranspose3d(n_channels * 8, n_channels * 4, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)
        self.conv_upsample3_CT= nn.ConvTranspose3d(n_channels * 4, n_channels * 2, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)
        self.conv_upsample4_CT= nn.ConvTranspose3d(n_channels * 2, n_channels, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)

        self.decoder1_CT = encoder_block(n_channels * 1 * 2, n_channels, stride = 1)
        self.decoder2_CT = encoder_block(n_channels * 2 * 2, n_channels * 2, stride = 1)
        self.decoder3_CT = encoder_block(n_channels * 4 * 2, n_channels * 4, stride = 1)
        self.decoder4_CT = encoder_block(n_channels * 8 * 2, n_channels * 8, stride = 1)

        self.expand_channels_PET = encoder_block(in_channels, n_channels, stride = 1)
        self.conv_downsample1_PET = encoder_block(n_channels, n_channels * 2)
        self.conv_downsample2_PET = encoder_block(n_channels * 2, n_channels * 4)
        self.conv_downsample3_PET = encoder_block(n_channels * 4, n_channels * 8)
        self.conv_downsample4_PET = encoder_block(n_channels * 8, channel_bound)

        self.conv_upsample1_PET = nn.ConvTranspose3d(channel_bound, n_channels * 8, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)
        self.conv_upsample2_PET= nn.ConvTranspose3d(n_channels * 8, n_channels * 4, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)
        self.conv_upsample3_PET= nn.ConvTranspose3d(n_channels * 4, n_channels * 2, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)
        self.conv_upsample4_PET= nn.ConvTranspose3d(n_channels * 2, n_channels, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)

        self.decoder1_PET = encoder_block(n_channels * 1 * 2, n_channels, stride = 1)
        self.decoder2_PET = encoder_block(n_channels * 2 * 2, n_channels * 2, stride = 1)
        self.decoder3_PET = encoder_block(n_channels * 4 * 2, n_channels * 4, stride = 1)
        self.decoder4_PET = encoder_block(n_channels * 8 * 2, n_channels * 8, stride = 1)
        
        self.classifier1 = nn.Conv3d(n_channels, out_channels, kernel_size = 1)
        self.classifier2 = nn.Conv3d(n_channels * 2, out_channels, kernel_size = 1)
        self.classifier3 = nn.Conv3d(n_channels * 4, out_channels, kernel_size = 1)
        self.classifier4 = nn.Conv3d(n_channels * 8, out_channels, kernel_size = 1)

        self.classifier_PET = nn.Conv3d(n_channels, 1, kernel_size = 1)

        self.upsample4 = nn.Upsample(scale_factor=8)
        self.upsample3 = nn.Upsample(scale_factor=4)
        self.upsample2 = nn.Upsample(scale_factor=2)


    def forward(self, CT, PET):
        PET = self.expand_channels_PET(PET)
        PET_downsample1 = self.conv_downsample1_PET(PET)
        PET_downsample2 = self.conv_downsample2_PET(PET_downsample1)
        PET_downsample3 = self.conv_downsample3_PET(PET_downsample2)
        PET_downsample4 = self.conv_downsample4_PET(PET_downsample3)

        PET_downsample4_up = self.conv_upsample1_PET(PET_downsample4)
        l4_output_PET = self.decoder4_PET(torch.cat((PET_downsample4_up, PET_downsample3), dim = 1))
        PET_downsample3_up = self.conv_upsample2_PET(l4_output_PET)
        l3_output_PET = self.decoder3_PET(torch.cat((PET_downsample3_up, PET_downsample2), dim = 1))
        PET_downsample2_up = self.conv_upsample3_PET(l3_output_PET)
        l2_output_PET = self.decoder2_PET(torch.cat((PET_downsample2_up, PET_downsample1), dim = 1))
        PET_downsample1_up = self.conv_upsample4_PET(l2_output_PET)
        l1_output_PET = self.decoder1_PET(torch.cat((PET_downsample1_up, PET), dim = 1))
        spatial_attention_map = self.classifier_PET(l1_output_PET)

        spatial_attention_map_div2 = F.interpolate(spatial_attention_map, scale_factor = 0.5, mode ='trilinear')
        spatial_attention_map_div4 = F.interpolate(spatial_attention_map, scale_factor = 0.25, mode ='trilinear')
        spatial_attention_map_div8 = F.interpolate(spatial_attention_map, scale_factor = 0.125, mode ='trilinear')

        CT = self.expand_channels_CT(CT)
        CT_downsample1 = self.conv_downsample1_CT(CT)
        CT_downsample2 = self.conv_downsample2_CT(CT_downsample1)
        CT_downsample3 = self.conv_downsample3_CT(CT_downsample2)
        CT_downsample4 = self.conv_downsample4_CT(CT_downsample3)

        CT_downsample4_up = self.conv_upsample1_CT(CT_downsample4)
        l4_output_CT = self.decoder4_CT(torch.cat((CT_downsample4_up, CT_downsample3*spatial_attention_map_div8), dim = 1))
        CT_downsample3_up = self.conv_upsample2_CT(l4_output_CT)
        l3_output_CT = self.decoder3_CT(torch.cat((CT_downsample3_up, CT_downsample2*spatial_attention_map_div4), dim = 1))
        CT_downsample2_up = self.conv_upsample3_CT(l3_output_CT)
        l2_output_CT = self.decoder2_CT(torch.cat((CT_downsample2_up, CT_downsample1*spatial_attention_map_div2), dim = 1))
        CT_downsample1_up = self.conv_upsample4_CT(l2_output_CT)
        l1_output_CT = self.decoder1_CT(torch.cat((CT_downsample1_up, CT*spatial_attention_map), dim = 1))

        l1_output = self.classifier1(l1_output_CT)
        l2_output = self.upsample2(self.classifier2(l2_output_CT))
        l3_output = self.upsample3(self.classifier3(l3_output_CT))
        l4_output = self.upsample4(self.classifier4(l4_output_CT))
        
        return [l1_output, l2_output, l3_output, l4_output]

    
class UNet3d_MultiModalV2(nn.Module):
    def __init__(self, in_channels = 1, out_channels = 2, n_channels = 32, channel_bound = 320, vectorization = True):
        super().__init__()
        self.vectorization = vectorization
        channel_bound = min(n_channels * 16, channel_bound)
        self.expand_channels_CT = aspp_encoder(in_channels, n_channels, stride = 1)
        self.conv_downsample1_CT = encoder_block(n_channels, n_channels * 2)
        self.conv_downsample2_CT = encoder_block(n_channels * 2, n_channels * 4)
        self.conv_downsample3_CT = encoder_block(n_channels * 4, n_channels * 8)
        self.conv_downsample4_CT = encoder_block(n_channels * 8, channel_bound)

        self.conv_upsample1_CT = nn.ConvTranspose3d(channel_bound, n_channels * 8, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)
        self.conv_upsample2_CT= nn.ConvTranspose3d(n_channels * 8, n_channels * 4, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)
        self.conv_upsample3_CT= nn.ConvTranspose3d(n_channels * 4, n_channels * 2, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)
        self.conv_upsample4_CT= nn.ConvTranspose3d(n_channels * 2, n_channels, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)

        self.decoder1_CT = encoder_block(n_channels * 1 * 2, n_channels, stride = 1)
        self.decoder2_CT = encoder_block(n_channels * 2 * 2, n_channels * 2, stride = 1)
        self.decoder3_CT = encoder_block(n_channels * 4 * 2, n_channels * 4, stride = 1)
        self.decoder4_CT = encoder_block(n_channels * 8 * 2, n_channels * 8, stride = 1)

        self.expand_channels_PET = aspp_encoder(in_channels, n_channels, stride = 1)
        self.conv_downsample1_PET = encoder_block(n_channels, n_channels * 2)
        self.conv_downsample2_PET = encoder_block(n_channels * 2, n_channels * 4)
        self.conv_downsample3_PET = encoder_block(n_channels * 4, n_channels * 8)
        self.conv_downsample4_PET = encoder_block(n_channels * 8, channel_bound)

        self.conv_upsample1_PET = nn.ConvTranspose3d(channel_bound, n_channels * 8, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)
        self.conv_upsample2_PET= nn.ConvTranspose3d(n_channels * 8, n_channels * 4, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)
        self.conv_upsample3_PET= nn.ConvTranspose3d(n_channels * 4, n_channels * 2, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)
        self.conv_upsample4_PET= nn.ConvTranspose3d(n_channels * 2, n_channels, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)

        self.decoder1_PET = encoder_block(n_channels * 1 * 2, n_channels, stride = 1)
        self.decoder2_PET = encoder_block(n_channels * 2 * 2, n_channels * 2, stride = 1)
        self.decoder3_PET = encoder_block(n_channels * 4 * 2, n_channels * 4, stride = 1)
        self.decoder4_PET = encoder_block(n_channels * 8 * 2, n_channels * 8, stride = 1)
        
        self.classifier1 = nn.Conv3d(n_channels * 2, out_channels, kernel_size = 1)
        self.classifier2 = nn.Conv3d(n_channels * 2 * 2, out_channels, kernel_size = 1)
        self.classifier3 = nn.Conv3d(n_channels * 4 * 2, out_channels, kernel_size = 1)
        self.classifier4 = nn.Conv3d(n_channels * 8 * 2, out_channels, kernel_size = 1)


        self.upsample4 = nn.Upsample(scale_factor=8)
        self.upsample3 = nn.Upsample(scale_factor=4)
        self.upsample2 = nn.Upsample(scale_factor=2)


    def forward(self, CT, PET):
        PET = self.expand_channels_PET(PET)
        PET_downsample1 = self.conv_downsample1_PET(PET)
        PET_downsample2 = self.conv_downsample2_PET(PET_downsample1)
        PET_downsample3 = self.conv_downsample3_PET(PET_downsample2)
        PET_downsample4 = self.conv_downsample4_PET(PET_downsample3)

        PET_downsample4_up = self.conv_upsample1_PET(PET_downsample4)
        l4_output_PET = self.decoder4_PET(torch.cat((PET_downsample4_up, PET_downsample3), dim = 1))
        PET_downsample3_up = self.conv_upsample2_PET(l4_output_PET)
        l3_output_PET = self.decoder3_PET(torch.cat((PET_downsample3_up, PET_downsample2), dim = 1))
        PET_downsample2_up = self.conv_upsample3_PET(l3_output_PET)
        l2_output_PET = self.decoder2_PET(torch.cat((PET_downsample2_up, PET_downsample1), dim = 1))
        PET_downsample1_up = self.conv_upsample4_PET(l2_output_PET)
        l1_output_PET = self.decoder1_PET(torch.cat((PET_downsample1_up, PET), dim = 1))
        CT = self.expand_channels_CT(CT)
        CT_downsample1 = self.conv_downsample1_CT(CT)
        CT_downsample2 = self.conv_downsample2_CT(CT_downsample1)
        CT_downsample3 = self.conv_downsample3_CT(CT_downsample2)
        CT_downsample4 = self.conv_downsample4_CT(CT_downsample3)

        CT_downsample4_up = self.conv_upsample1_CT(CT_downsample4)
        l4_output_CT = self.decoder4_CT(torch.cat((CT_downsample4_up, CT_downsample3), dim = 1))
        CT_downsample3_up = self.conv_upsample2_CT(l4_output_CT)
        l3_output_CT = self.decoder3_CT(torch.cat((CT_downsample3_up, CT_downsample2), dim = 1))
        CT_downsample2_up = self.conv_upsample3_CT(l3_output_CT)
        l2_output_CT = self.decoder2_CT(torch.cat((CT_downsample2_up, CT_downsample1), dim = 1))
        CT_downsample1_up = self.conv_upsample4_CT(l2_output_CT)
        l1_output_CT = self.decoder1_CT(torch.cat((CT_downsample1_up, CT), dim = 1))

        l1_output = self.classifier1(torch.cat((l1_output_CT, l1_output_PET), dim = 1))
        l2_output = self.upsample2(self.classifier2(torch.cat((l2_output_CT, l2_output_PET), dim = 1)))
        l3_output = self.upsample3(self.classifier3(torch.cat((l3_output_CT, l3_output_PET), dim = 1)))
        l4_output = self.upsample4(self.classifier4(torch.cat((l4_output_CT, l4_output_PET), dim = 1)))

        if self.vectorization:
            l1_output = torch.softmax(l1_output , dim = 1)
            l2_output = torch.softmax(l2_output , dim = 1)
            l3_output = torch.softmax(l3_output , dim = 1)
            l4_output = torch.softmax(l4_output , dim = 1)
            result = torch.stack([l1_output, l2_output, l3_output, l4_output]).permute(1,0,2,3,4,5)

            return result.contiguous()

        
        return [l1_output, l2_output, l3_output, l4_output]


class UNet3d_Plus_ASPP(nn.Module):
    def __init__(self, in_channels = 1, out_channels = 2, n_channels = 32, channel_bound = 320):
        super().__init__()
        self.expand_channels = aspp_encoder(in_channels, n_channels, stride = 1)
        self.conv_downsample1 = aspp_encoder(n_channels, n_channels * 2)
        self.conv_downsample2 = encoder_block(n_channels * 2, n_channels * 4)
        self.conv_downsample3 = encoder_block(n_channels * 4, n_channels * 8)
        self.conv_downsample4 = encoder_block(n_channels * 8, channel_bound)

        self.conv_upsample1 = nn.ConvTranspose3d(channel_bound, n_channels * 8, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)
        self.conv_upsample2= nn.ConvTranspose3d(n_channels * 8, n_channels * 4, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)
        self.conv_upsample3= nn.ConvTranspose3d(n_channels * 4, n_channels * 2, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)
        self.conv_upsample4= nn.ConvTranspose3d(n_channels * 2, n_channels, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)

        self.decoder1 = aspp_encoder(n_channels * 1 * 2, n_channels, stride = 1)
        self.decoder2 = aspp_encoder(n_channels * 2 * 2, n_channels * 2, stride = 1)
        self.decoder3 = encoder_block(n_channels * 4 * 2, n_channels * 4, stride = 1)
        self.decoder4 = encoder_block(n_channels * 8 * 2, n_channels * 8, stride = 1)
        
        self.classifier1 = nn.Conv3d(n_channels, out_channels, kernel_size = 1)
        self.classifier2 = nn.Conv3d(n_channels * 2, out_channels, kernel_size = 1)
        self.classifier3 = nn.Conv3d(n_channels * 4, out_channels, kernel_size = 1)
        self.classifier4 = nn.Conv3d(n_channels * 8, out_channels, kernel_size = 1)

        self.upsample4 = nn.Upsample(scale_factor=8)
        self.upsample3 = nn.Upsample(scale_factor=4)
        self.upsample2 = nn.Upsample(scale_factor=2)

    
    def forward(self, x):
        x = self.expand_channels(x)
        x_downsample1 = self.conv_downsample1(x)
        x_downsample2 = self.conv_downsample2(x_downsample1)
        x_downsample3 = self.conv_downsample3(x_downsample2)
        x_downsample4 = self.conv_downsample4(x_downsample3)

        x_downsample4_up = self.conv_upsample1(x_downsample4)
        l4_output = self.decoder4(torch.cat((x_downsample4_up, x_downsample3), dim = 1))
        x_downsample3_up = self.conv_upsample2(l4_output)
        l3_output = self.decoder3(torch.cat((x_downsample3_up, x_downsample2), dim = 1))
        x_downsample2_up = self.conv_upsample3(l3_output)
        l2_output = self.decoder2(torch.cat((x_downsample2_up, x_downsample1), dim = 1))
        x_downsample1_up = self.conv_upsample4(l2_output)
        l1_output = self.decoder1(torch.cat((x_downsample1_up, x), dim = 1))

        l1_output = self.classifier1(l1_output)
        l2_output = self.upsample2(self.classifier2(l2_output))
        l3_output = self.upsample3(self.classifier3(l3_output))
        l4_output = self.upsample4(self.classifier4(l4_output))

        
        return [l1_output, l2_output, l3_output, l4_output]



class UNet2d_Plus(nn.Module):
    def __init__(self, in_channels = 1, out_channels = 2, n_channels = 64, channel_bound = 1024):
        super().__init__()
        self.expand_channels = encoder_block_2d(in_channels, n_channels, stride = 1)
        self.conv_downsample1 = encoder_block_2d(n_channels, n_channels * 2)
        self.conv_downsample2 = encoder_block_2d(n_channels * 2, n_channels * 4)
        self.conv_downsample3 = encoder_block_2d(n_channels * 4, n_channels * 8)
        self.conv_downsample4 = encoder_block_2d(n_channels * 8, channel_bound)

        self.conv_upsample1 = nn.ConvTranspose2d(channel_bound, n_channels * 8, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)
        self.conv_upsample2= nn.ConvTranspose2d(n_channels * 8, n_channels * 4, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)
        self.conv_upsample3= nn.ConvTranspose2d(n_channels * 4, n_channels * 2, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)
        self.conv_upsample4= nn.ConvTranspose2d(n_channels * 2, n_channels, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)

        self.decoder1 = encoder_block_2d(n_channels * 1 * 2, n_channels, stride = 1)
        self.decoder2 = encoder_block_2d(n_channels * 2 * 2, n_channels * 2, stride = 1)
        self.decoder3 = encoder_block_2d(n_channels * 4 * 2, n_channels * 4, stride = 1)
        self.decoder4 = encoder_block_2d(n_channels * 8 * 2, n_channels * 8, stride = 1)
        
        self.classifier1 = nn.Conv2d(n_channels, out_channels, kernel_size = 1)
        self.classifier2 = nn.Conv2d(n_channels * 2, out_channels, kernel_size = 1)
        self.classifier3 = nn.Conv2d(n_channels * 4, out_channels, kernel_size = 1)
        self.classifier4 = nn.Conv2d(n_channels * 8, out_channels, kernel_size = 1)

        self.upsample4 = nn.Upsample(scale_factor=8)
        self.upsample3 = nn.Upsample(scale_factor=4)
        self.upsample2 = nn.Upsample(scale_factor=2)

    
    def forward(self, x):
        x = self.expand_channels(x)
        x_downsample1 = self.conv_downsample1(x)
        x_downsample2 = self.conv_downsample2(x_downsample1)
        x_downsample3 = self.conv_downsample3(x_downsample2)
        x_downsample4 = self.conv_downsample4(x_downsample3)

        x_downsample4_up = self.conv_upsample1(x_downsample4)
        l4_output = self.decoder4(torch.cat((x_downsample4_up, x_downsample3), dim = 1))
        x_downsample3_up = self.conv_upsample2(l4_output)
        l3_output = self.decoder3(torch.cat((x_downsample3_up, x_downsample2), dim = 1))
        x_downsample2_up = self.conv_upsample3(l3_output)
        l2_output = self.decoder2(torch.cat((x_downsample2_up, x_downsample1), dim = 1))
        x_downsample1_up = self.conv_upsample4(l2_output)
        l1_output = self.decoder1(torch.cat((x_downsample1_up, x), dim = 1))

        l1_output = self.classifier1(l1_output)
        l2_output = self.upsample2(self.classifier2(l2_output))
        l3_output = self.upsample3(self.classifier3(l3_output))
        l4_output = self.upsample4(self.classifier4(l4_output))

        
        return [l1_output, l2_output, l3_output, l4_output]




class UNet2d_GRU(nn.Module):
    def __init__(self, in_channels = 1, out_channels = 2, n_channels = 64, channel_bound = 1024, input_size = (48, 48), device = 0):
        super().__init__()
        input_size = np.array(input_size)
        self.device = device
        self.expand_channels = encoder_block_2d(in_channels, n_channels, stride = 1)
        self.conv_downsample1 = encoder_block_2d(n_channels, n_channels * 2)
        self.conv_downsample2 = encoder_block_2d(n_channels * 2, n_channels * 4)
        self.conv_downsample3 = encoder_block_2d(n_channels * 4, n_channels * 8)
        self.conv_downsample4 = encoder_block_2d(n_channels * 8, channel_bound)

        self.conv_upsample1 = nn.ConvTranspose2d(channel_bound, n_channels * 8, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)
        self.conv_upsample2= nn.ConvTranspose2d(n_channels * 8, n_channels * 4, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)
        self.conv_upsample3= nn.ConvTranspose2d(n_channels * 4, n_channels * 2, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)
        self.conv_upsample4= nn.ConvTranspose2d(n_channels * 2, n_channels, kernel_size = 3, stride = 2, padding = 1, output_padding = 1)

        self.decoder1 = encoder_block_2d(n_channels * 1 * 2, n_channels, stride = 1)
        self.decoder2 = encoder_block_2d(n_channels * 2 * 2, n_channels * 2, stride = 1)
        self.decoder3 = encoder_block_2d(n_channels * 4 * 2, n_channels * 4, stride = 1)
        self.decoder4 = encoder_block_2d(n_channels * 8 * 2, n_channels * 8, stride = 1)
        
        self.classifier1 = nn.Conv2d(n_channels, out_channels, kernel_size = 1)
        self.classifier2 = nn.Conv2d(n_channels * 2, out_channels, kernel_size = 1)
        self.classifier3 = nn.Conv2d(n_channels * 4, out_channels, kernel_size = 1)
        self.classifier4 = nn.Conv2d(n_channels * 8, out_channels, kernel_size = 1)

        self.upsample4 = nn.Upsample(scale_factor=8)
        self.upsample3 = nn.Upsample(scale_factor=4)
        self.upsample2 = nn.Upsample(scale_factor=2)

        self.gru1 = ConvGRUCell(input_size = input_size, input_dim = n_channels, hidden_dim = n_channels, kernel_size = [3, 3])
        self.gru2 = ConvGRUCell(input_size = input_size //2, input_dim = n_channels*2, hidden_dim = n_channels*2, kernel_size = [3, 3])
        self.gru3 = ConvGRUCell(input_size = input_size //4, input_dim = n_channels*4, hidden_dim = n_channels*4, kernel_size = [3, 3])
        self.gru4 = ConvGRUCell(input_size = input_size //8, input_dim = n_channels*8, hidden_dim = n_channels*8, kernel_size = [3, 3])
        self.gru5 = ConvGRUCell(input_size = input_size //16, input_dim = n_channels*16, hidden_dim = n_channels*16, kernel_size = [3, 3])

    
    def forward(self, x, hidden_state = None):
        x = self.expand_channels(x)
        x_downsample1 = self.conv_downsample1(x)
        x_downsample2 = self.conv_downsample2(x_downsample1)
        x_downsample3 = self.conv_downsample3(x_downsample2)
        x_downsample4 = self.conv_downsample4(x_downsample3)

        if hidden_state != None:
            x = self.gru1(x, hidden_state[0])
            x_downsample1 = self.gru2(x_downsample1, hidden_state[1])
            x_downsample2 = self.gru3(x_downsample2, hidden_state[2])
            x_downsample3 = self.gru4(x_downsample3, hidden_state[3])
            x_downsample4 = self.gru5(x_downsample4, hidden_state[4])
        else:
            x = self.gru1(x, torch.zeros(x.shape).float().to(self.device))
            x_downsample1 = self.gru2(x_downsample1, torch.zeros(x_downsample1.shape).float().to(self.device))
            x_downsample2 = self.gru3(x_downsample2, torch.zeros(x_downsample2.shape).float().to(self.device))
            x_downsample3 = self.gru4(x_downsample3, torch.zeros(x_downsample3.shape).float().to(self.device))
            x_downsample4 = self.gru5(x_downsample4, torch.zeros(x_downsample4.shape).float().to(self.device))

        x_downsample4_up = self.conv_upsample1(x_downsample4)
        l4_output = self.decoder4(torch.cat((x_downsample4_up, x_downsample3), dim = 1))
        x_downsample3_up = self.conv_upsample2(l4_output)
        l3_output = self.decoder3(torch.cat((x_downsample3_up, x_downsample2), dim = 1))
        x_downsample2_up = self.conv_upsample3(l3_output)
        l2_output = self.decoder2(torch.cat((x_downsample2_up, x_downsample1), dim = 1))
        x_downsample1_up = self.conv_upsample4(l2_output)
        l1_output = self.decoder1(torch.cat((x_downsample1_up, x), dim = 1))

        l1_output = self.classifier1(l1_output)
        l2_output = self.upsample2(self.classifier2(l2_output))
        l3_output = self.upsample3(self.classifier3(l3_output))
        l4_output = self.upsample4(self.classifier4(l4_output))

        
        return [l1_output, l2_output, l3_output, l4_output], [x.detach().clone(), x_downsample1.detach().clone(), x_downsample2.detach().clone(), x_downsample3.detach().clone(), x_downsample4.detach().clone()]



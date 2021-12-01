import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
import torch
import numpy as np

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

def conv_block(in_channels, out_channels, kernel_size, stride, padding, dilation):
    return nn.Sequential(nn.Conv3d(in_channels, out_channels, kernel_size, stride, padding, dilation),
                         nn.Dropout3d(),
                         nn.InstanceNorm3d(out_channels),
                         nn.LeakyReLU())
    
def encoder_block(in_channels, out_channels, kernel_size = 3, stride = 2, padding = 1, dilation = 1):
    return nn.Sequential(conv_block(in_channels, out_channels, kernel_size, stride, padding = padding, dilation = dilation),
                         conv_block(out_channels, out_channels, kernel_size, stride = 1, padding = padding, dilation = dilation))


def conv_block_2d(in_channels, out_channels, kernel_size, stride, padding, dilation):
    return nn.Sequential(nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding, dilation),
                         nn.Dropout2d(),
                         nn.InstanceNorm2d(out_channels),
                         nn.LeakyReLU())

def encoder_block_2d(in_channels, out_channels, kernel_size = 3, stride = 2, padding = 1, dilation = 1):
    return nn.Sequential(conv_block_2d(in_channels, out_channels, kernel_size, stride, padding = padding, dilation = dilation),
                         conv_block_2d(out_channels, out_channels, kernel_size, stride = 1, padding = padding, dilation = dilation))

def aspp_block(in_channels, out_channels):
    return nn.Sequential(ASPP_Block(in_channels, out_channels),
                         nn.Dropout3d(),
                         nn.InstanceNorm3d(out_channels),
                         nn.LeakyReLU())
                    
    
def aspp_encoder(in_channels, out_channels, kernel_size = 3, stride = 2, padding = 1, dilation = 1):
    return nn.Sequential(conv_block(in_channels, out_channels, kernel_size, stride, padding = padding, dilation = dilation),
                         aspp_block(out_channels, out_channels))


class ASPP(nn.Module):
    def __init__(self, in_channels, out_channels, num_classes):
        super(ASPP, self).__init__()
        
        # 1번 branch = 1x1 convolution → BatchNorm → ReLu
        self.conv_1x1_1 = nn.Conv3d(in_channels, out_channels, kernel_size=1)
        self.bn_conv_1x1_1 = nn.BatchNorm3d(out_channels)

        # 2번 branch = 3x3 convolution w/ rate=6 (or 12) → BatchNorm → ReLu
        self.conv_3x3_1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=1, padding=6, dilation=6)
        self.bn_conv_3x3_1 = nn.BatchNorm3d(out_channels)

        # 3번 branch = 3x3 convolution w/ rate=12 (or 24) → BatchNorm → ReLu
        self.conv_3x3_2 = nn.Conv3d(in_channels, out_channels, kernel_size=3, stride=1, padding=12, dilation=12)
        self.bn_conv_3x3_2 = nn.BatchNorm3d(out_channels)
    
        # 4번 branch = 3x3 convolution w/ rate=18 (or 36) → BatchNorm → ReLu
        self.conv_3x3_3 = nn.Conv3d(in_channels, out_channels, kernel_size=3, stride=1, padding=18, dilation=18)
        self.bn_conv_3x3_3 = nn.BatchNorm3d(out_channels)

        # 5번 branch = AdaptiveAvgPool2d → 1x1 convolution → BatchNorm → ReLu
        self.avg_pool = nn.AdaptiveAvgPool3d(1)
        self.conv_1x1_2 = nn.Conv3d(in_channels, out_channels, kernel_size=1)
        self.bn_conv_1x1_2 = nn.BatchNorm2d(out_channels)
        
        self.conv_1x1_3 = nn.Conv2d(out_channels * 5, out_channels, kernel_size=1) # (1280 = 5*256)
        self.bn_conv_1x1_3 = nn.BatchNorm2d(out_channels)

        self.conv_1x1_4 = nn.Conv2d(out_channels, num_classes, kernel_size=1)

    def forward(self, feature_map):
        # feature map의 shape은 (batch_size, in_channels, height/output_stride, width/output_stride)

        feature_map_h = feature_map.size()[2] # (== h/16)
        feature_map_w = feature_map.size()[3] # (== w/16)

        # 1번 branch = 1x1 convolution → BatchNorm → ReLu
        # shape: (batch_size, out_channels, height/output_stride, width/output_stride)
        out_1x1 = F.relu(self.bn_conv_1x1_1(self.conv_1x1_1(feature_map)))
        # 2번 branch = 3x3 convolution w/ rate=6 (or 12) → BatchNorm → ReLu
        # shape: (batch_size, out_channels, height/output_stride, width/output_stride)
        out_3x3_1 = F.relu(self.bn_conv_3x3_1(self.conv_3x3_1(feature_map)))
        # 3번 branch = 3x3 convolution w/ rate=12 (or 24) → BatchNorm → ReLu
        # shape: (batch_size, out_channels, height/output_stride, width/output_stride)
        out_3x3_2 = F.relu(self.bn_conv_3x3_2(self.conv_3x3_2(feature_map)))
        # 4번 branch = 3x3 convolution w/ rate=18 (or 36) → BatchNorm → ReLu
        # shape: (batch_size, out_channels, height/output_stride, width/output_stride)
        out_3x3_3 = F.relu(self.bn_conv_3x3_3(self.conv_3x3_3(feature_map)))

        # 5번 branch = AdaptiveAvgPool2d → 1x1 convolution → BatchNorm → ReLu
        # shape: (batch_size, in_channels, 1, 1)
        out_img = self.avg_pool(feature_map) 
        # shape: (batch_size, out_channels, 1, 1)
        out_img = F.relu(self.bn_conv_1x1_2(self.conv_1x1_2(out_img)))
        # shape: (batch_size, out_channels, height/output_stride, width/output_stride)
        out_img = F.upsample(out_img, size=(feature_map_h, feature_map_w), mode="bilinear")

        # shape: (batch_size, out_channels * 5, height/output_stride, width/output_stride)
        out = torch.cat([out_1x1, out_3x3_1, out_3x3_2, out_3x3_3, out_img], 1) 
        # shape: (batch_size, out_channels, height/output_stride, width/output_stride)
        out = F.relu(self.bn_conv_1x1_3(self.conv_1x1_3(out))) 
        # shape: (batch_size, num_classes, height/output_stride, width/output_stride)
        out = self.conv_1x1_4(out) 

        return out

class ASPP_Block(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.conv1x1 = conv_block(in_channels, out_channels, kernel_size = 1, stride = 1, padding = 0, dilation = 1)
        self.conv3x3_1 = conv_block(in_channels, out_channels, kernel_size = 3, stride = 1, padding = 6, dilation = 6)
        self.conv3x3_2 = conv_block(in_channels, out_channels, kernel_size = 3, stride = 1, padding = 12, dilation = 12)
        self.conv3x3_3 = conv_block(in_channels, out_channels, kernel_size = 3, stride = 1, padding = 18, dilation = 18)
        self.avg_pool = nn.Sequential(nn.AdaptiveAvgPool3d(1),
                        conv_block(in_channels, out_channels, kernel_size = 1, stride = 1, padding = 0, dilation = 1))

        self.concat_conv = conv_block(out_channels*5, out_channels, kernel_size = 1, stride = 1, padding = 0, dilation = 1)

    
    def forward(self, X):
        _, _, w, h, d = X.size()
        X_1x1 = self.conv1x1(X)
        X_3x3_6 = self.conv3x3_1(X)
        X_3x3_12 = self.conv3x3_2(X)
        X_3x3_18 = self.conv3x3_3(X)
        X_avg_pool = self.avg_pool(X)
        X_avg_pool = F.upsample(X_avg_pool, size=(w, h, d), mode="trilinear")
        out = torch.cat([X_1x1, X_3x3_6, X_3x3_12, X_3x3_18, X_avg_pool], 1)
        out = self.concat_conv(out)

        return out
        

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



class ASPP_Block(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.conv1x1 = conv_block(in_channels, out_channels, kernel_size = 1, stride = 1, padding = 0, dilation = 1)
        self.conv3x3_1 = conv_block(in_channels, out_channels, kernel_size = 3, stride = 1, padding = 6, dilation = 6)
        self.conv3x3_2 = conv_block(in_channels, out_channels, kernel_size = 3, stride = 1, padding = 12, dilation = 12)
        self.conv3x3_3 = conv_block(in_channels, out_channels, kernel_size = 3, stride = 1, padding = 18, dilation = 18)
        self.avg_pool = nn.Sequential(nn.AvgPool3d(1),
                        conv_block(in_channels, out_channels, kernel_size = 1, stride = 1, padding = 0, dilation = 1))

        self.concat_conv = conv_block(out_channels*5, out_channels, kernel_size = 1, stride = 1, padding = 0, dilation = 1)

    
    def forward(self, X):
        _, _, w, h, d = X.size()
        X_1x1 = self.conv1x1(X)
        X_3x3_6 = self.conv3x3_1(X)
        X_3x3_12 = self.conv3x3_2(X)
        X_3x3_18 = self.conv3x3_3(X)
        X_avg_pool = self.avg_pool(X)
        X_avg_pool = F.upsample(X_avg_pool, size=(w, h, d), mode="trilinear")
        out = torch.cat([X_1x1, X_3x3_6, X_3x3_12, X_3x3_18, X_avg_pool], 1)
        out = self.concat_conv(out)

        return out


class My_ASPP(nn.Module):
    def __init__(self, in_channels, out_channels, stride = 1):
        super().__init__()
        self.conv1x1 = conv_block(in_channels//5, out_channels//5, kernel_size = 1, stride = 1, padding = 0, dilation = 1)
        self.conv3x3_0 = conv_block(in_channels//5, out_channels//5, kernel_size = 3, stride = 1, padding = 1, dilation = 1)
        self.conv3x3_1 = conv_block(in_channels//5, out_channels//5, kernel_size = 3, stride = 1, padding = 6, dilation = 6)
        self.conv3x3_2 = conv_block(in_channels//5, out_channels//5, kernel_size = 3, stride = 1, padding = 12, dilation = 12)
        self.conv3x3_3 = conv_block(in_channels//5, out_channels//5, kernel_size = 3, stride = 1, padding = 18, dilation = 18)
        self.conv3x3_4 = conv_block(in_channels, out_channels, kernel_size = 3, stride = stride, padding = 1, dilation = 1)

        

    
    def forward(self, X):
        _, _, w, h, d = X.size()
        X_1x1 = self.conv1x1(X)
        X_3x3_1 = self.conv3x3_0(X)
        X_3x3_6 = self.conv3x3_1(X)
        X_3x3_12 = self.conv3x3_2(X)
        X_3x3_18 = self.conv3x3_3(X)
        return self.conv3x3_4(torch.cat((X_1x1, X_3x3_1, X_3x3_6, X_3x3_12, X_3x3_18), 1))



def myaspp_block(in_channels, out_channels):
    return nn.Sequential(My_ASPP(in_channels, out_channels),
                         nn.Dropout3d(),
                         nn.InstanceNorm3d(out_channels),
                         nn.LeakyReLU())
def myaspp_encoder(in_channels, out_channels, stride):
    return nn.Sequential(myaspp_block(in_channels, out_channels, stride = 1),
                         myaspp_block(in_channels, out_channels, stride = stride))


class ConvGRUCell(nn.Module):
    def __init__(self, input_size, input_dim, hidden_dim, kernel_size, bias = 0, dtype = float):
        """
        Initialize the ConvLSTM cell
        :param input_size: (int, int)
            Height and width of input tensor as (height, width).
        :param input_dim: int
            Number of channels of input tensor.
        :param hidden_dim: int
            Number of channels of hidden state.
        :param kernel_size: (int, int)
            Size of the convolutional kernel.
        :param bias: bool
            Whether or not to add the bias.
        :param dtype: torch.cuda.FloatTensor or torch.FloatTensor
            Whether or not to use cuda.
        """
        super(ConvGRUCell, self).__init__()
        self.height, self.width = input_size
        self.padding = kernel_size[0] // 2, kernel_size[1] // 2
        self.hidden_dim = hidden_dim
        self.bias = bias
        self.dtype = dtype

        self.conv_gates = nn.Conv2d(in_channels=input_dim + hidden_dim,
                                    out_channels=2*self.hidden_dim,  # for update_gate,reset_gate respectively
                                    kernel_size=kernel_size,
                                    padding=self.padding,
                                    bias=self.bias)

        self.conv_can = nn.Conv2d(in_channels=input_dim+hidden_dim,
                              out_channels=self.hidden_dim, # for candidate neural memory
                              kernel_size=kernel_size,
                              padding=self.padding,
                              bias=self.bias)


    def forward(self, input_tensor, h_cur):
        """
        :param self:
        :param input_tensor: (b, c, h, w)
            input is actually the target_model
        :param h_cur: (b, c_hidden, h, w)
            current hidden and cell states respectively
        :return: h_next,
            next hidden state
        """
        combined = torch.cat([input_tensor, h_cur], dim=1)
        combined_conv = self.conv_gates(combined)

        gamma, beta = torch.split(combined_conv, self.hidden_dim, dim=1)
        reset_gate = torch.sigmoid(gamma)
        update_gate = torch.sigmoid(beta)

        combined = torch.cat([input_tensor, reset_gate*h_cur], dim=1)
        cc_cnm = self.conv_can(combined)
        cnm = torch.tanh(cc_cnm)

        h_next = (1 - update_gate) * h_cur + update_gate * cnm
        return h_next
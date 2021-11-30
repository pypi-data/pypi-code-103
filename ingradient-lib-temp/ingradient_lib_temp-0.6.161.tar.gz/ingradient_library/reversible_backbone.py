import revlib
import torch.nn as nn
import torch

# UNet의 경우 병렬적인 구조가 너무 많음. DeepLabV3 의 3D 모델 구현으로 가는 방안이 나아보임.
# Active Contour Loss를 Reversible 하게 설계하는 것도 좋은 방법. 현재는 마지막 Volume에 *3을 하게 됨.
# 해당 아이디어는 다음과 같은데 결국 Active Contour Loss는 F를 Sobel_Filter_x(X), Sobel_FIlter_y(X), Soble_Filter_z(X) 하는거고
# 이 결과를 각각 Sx, Sy, Sz라고 하면 Sx**2 + Sy**2 + Sz**2 를 구해서 Length로 사용하는데, 위의 Sobel Filter를 각기 구하는 과정에서
# 이를 G3(G2(G1(X))) = Sx**2 + Sy**2 + Sz**2로 수렴하게 하면 됨. => random 변수로 형성 후, Neural Network 학습 이후 뽑아내면 됨.
# 장점 No patch Needed 그냥 한번에 돌리면 됨.

def conv_block(in_channels, out_channels, kernel_size = 3, padding = 1, stride = 1, dilation = 1):
    return nn.Sequential([nn.Conv3d(in_channels, out_channels, kernel_size = kernel_size, padding = padding, stride = stride, dilation = dilation),
                        nn.InstanceNorm3d(out_channels),
                        nn.Dropout3d(0.2),
                        nn.LeakyReLU()])

def block(in_channels, kernel_size = 3, padding = 1, stride = 1, dilation = 1):
    return nn.Sequential([conv_block(in_channels, in_channels*2, kernel_size = kernel_size, padding = padding, stride = stride, dilation = dilation),
                        conv_block(in_channels*2, in_channels, kernel_size = 3, padding = 1, stride = 1)])

def classifier(in_channels, out_channels):
    return nn.Sequential(conv_block(in_channels, in_channels),
                         nn.Conv3d(in_channels, out_channels, 1, 1, 0))

def backbone(in_channels, depth = 5, variation = 6):
    return nn.Sequential(nn.Sequential([block(in_channels, dilation = 1, padding = 1)] +
            [block(in_channels, dilation= i*variation, padding = i*variation) for i in range(depth, 0, -1)]))

def model(in_channels, out_channels, depth, variation):
    return revlib.ReversibleSequential([backbone(in_channels, depth, variation), classifier(in_channels, out_channels)])

import torch
import torch.nn.functional as F
import torch.nn as nn

class Binary_Dice_Loss(nn.Module):
    def __init__(self, smooth = 1.0):
        super(Binary_Dice_Loss, self).__init__()
        self.smooth = smooth
    
    def forward(self, output, target):
        # output shape => (n_bs, 1, -1)
        # target shape => (n_bs, -1)
        n_bs = output.shape[0]
        output = output.view(n_bs, -1)
        target = target.view(n_bs, -1)
        intersection = (output * target).sum(-1)  # (n_bs, n_ds)
        union = output.sum(-1) + target.sum(-1)
        dice = 2.0 * (intersection + self.smooth) / (union + self.smooth)
        dice = dice.mean()
        return 1 - dice


class Multi_Dice_Loss(nn.Module):
    def __init__(self, num_classes, smooth = 0.0, epsilon = 1e-8, background_index = 0):
        super(Multi_Dice_Loss, self).__init__()
        self.smooth = smooth
        self.background_index = background_index
        self.num_classes = num_classes
        self.mask = (torch.arange(0, num_classes) != self.background_index)
        self.reduction = 'none'
        self.epsilon = epsilon

    def forward(self, output, target):
        #output shape => (n_bs, n_classes, -1)
        #target shape => (n_bs, -1)
        self.mask.to(output.device.index)
        n_bs = output.shape[0]
        output = output.view(n_bs, self.num_classes, -1)
        target = target.view(n_bs, -1)
        output = output[:, self.mask].permute(0, 2, 1) # (n_bs,  -1, n_cls)
        target = F.one_hot(target, num_classes = self.num_classes)
        target = target[:,:, self.mask]
        intersection = (output * target).sum((-1,-2)) #각 class 별 intersection score를 합함.
        union = output.sum((-1,-2)) + target.sum((-1,-2)) #각 class 별 union score를 합함.

        dice = 2.0 * (intersection + self.smooth) / (union + self.smooth + self.epsilon)
        dice = dice.mean()
        return 1 - dice


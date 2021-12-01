import torch
import torch.nn.functional as F
import torch.nn as nn

class Deep_Supervision_Loss(nn.Module):
    """
    1. 모든 Loss Funtion은 Reduction이어야한다.
    2. Target (Batch Size, x, y, z) 의 형태이며 element는 class number이다.
    3. Input은 (Batch Size, n_class, x, y, z) 형태이다.

    """
    def __init__(self, n_deepsupervision, loss1, loss2 = None, regularizer = 1.0, deep_supervision_weight = 0.5):
        super(Deep_Supervision_Loss, self).__init__()
        self.n_deepsupervision = n_deepsupervision
        loss1.reduction = 'none'
        if loss2 != None:
            loss1.reduction = 'none'
        self.loss1 = loss1
        self.loss2 = loss2
        self.regularizer = regularizer
        self.deep_supervision_weight = deep_supervision_weight
        self.writer = SummaryWriter()
        
    
    def forward(self, output, target):
        batch_size, deep_supervision_size, channel_size, size_x, size_y, size_y = output.shape
        output = output.reshape(batch_size * deep_supervision_size, channel_size, -1)
        target = target.reshape(batch_size, 1, -1).repeat(1, deep_supervision_size,1).reshape(batch_size * deep_supervision_size, -1)

        result = self.loss1(output, target)
        if isinstance(self.loss1, nn.CrossEntropyLoss):
            result = result.mean(-1)
        self.writer.add_scalar('Iteration_Loss/loss1', result.mean())
        if self.loss2 != None:
            loss2 = self.loss2(output, target)
            if isinstance(self.loss2, nn.CrossEntropyLoss):
                loss2 = loss2.mean(-1)
                self.writer.add_scalar('Iteration_Loss/loss2', loss2.mean())
            result += loss2 * self.regularizer

        result = result.view(batch_size, deep_supervision_size, -1)
    
        weight = torch.ones(deep_supervision_size).to(output.device.index)
        acc_value = self.deep_supervision_weight
        for i in range(deep_supervision_size):
            weight[i] = acc_value ** i
    
        weight = weight / weight.sum()
        weight = weight.view(1,deep_supervision_size ,1)
        result = result * weight

        return result.mean()
        


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
        
        return 1 - dice



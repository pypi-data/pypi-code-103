"""
* Sourse of SuperLoss, LabelSmoothingCrossEntropy, and 
    LabelSmoothingCrossEntropyWithSuperLoss):
    https://github.com/Rodger-Huang/SYSU-HCP-at-ImageCLEF-VQA-Med-2021/blob/main/utils.py
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from scipy.special import lambertw

__all__ = [
    'SuperLoss', 
    'LabelSmoothingCE',
    'LabelSmoothingCEWithSuperLoss'
]

class SuperLoss(nn.Module):
    def __init__(self, C=330, lam=0.25, device=None):
        super(SuperLoss, self).__init__()
        self.tau = torch.log(torch.FloatTensor([C]).to(device))
        self.lam = lam  # set to 1 for CIFAR10 and 0.25 for CIFAR100
        self.device = device

    def forward(self, l_i):
        l_i_detach = l_i.detach()
        # self.tau = 0.9 * self.tau + 0.1 * l_i_detach
        sigma = self.sigma(l_i_detach)
        loss = (l_i - self.tau) * sigma + self.lam * torch.log(sigma)**2
        loss = loss.mean()
        return loss

    def sigma(self, l_i):
        x = -2 / torch.exp(torch.ones_like(l_i)).to(self.device)
        y = 0.5 * torch.max(x, (l_i - self.tau) / self.lam)
        y = y.cpu().numpy()
        sigma = np.exp(-lambertw(y))
        sigma = sigma.real.astype(np.float32)
        sigma = torch.from_numpy(sigma).to(self.device)
        return sigma

class LabelSmoothingCE(nn.Module):
    def __init__(self, eps=0.1, reduction='mean', classes=330):
        super(LabelSmoothingCE, self).__init__()
        self.eps = eps
        self.reduction = reduction

    def forward(self, output, target):
        B, c = output.size()
        log_preds = F.log_softmax(output, dim=-1)
        if self.reduction == 'sum':
            loss = -log_preds.sum()
        else:
            loss = -log_preds.sum(dim=-1)
            if self.reduction == 'mean':
                loss = loss.mean()
        return loss * self.eps / c + (1 - self.eps) * F.nll_loss(log_preds, target, reduction=self.reduction)
        

class LabelSmoothingCEWithSuperLoss(nn.Module):
    def __init__(self, eps=0.1, reduction='mean', classes=330, device=None):
        super(LabelSmoothingCEWithSuperLoss, self).__init__()
        self.eps = eps
        self.reduction = reduction
        self.super_loss = SuperLoss(C=classes, device=device)
        self.device = device

    def forward(self, output, target):
        B, c = output.size()
        log_preds = F.log_softmax(output, dim=-1)
        if self.reduction == 'sum':
            loss = -log_preds.sum()
        else:
            loss = -log_preds.sum(dim=-1)
            if self.reduction == 'mean':
                loss = loss.mean()

        # l_i = (-log_preds.sum(dim=-1)) * self.eps / c + (1 - self.eps) * F.nll_loss(log_preds, target, reduction='none')
        # return self.super_loss(l_i)
        loss_cls = loss * self.eps / c + (1 - self.eps) * self.super_loss(F.nll_loss(log_preds, target, reduction='none'))
        return loss_cls
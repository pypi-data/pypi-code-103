from .losses import AUCMLoss
from .losses import APLoss_SH
from .losses import CrossEntropyLoss
from .losses import FocalLoss
from .losses import AUCM_MultiLabel



# alias name
AUROC = AUCMLoss
AUPRC = APLoss_SH
AUCM = AUCMLoss
SOAPLoss = APLoss_SH
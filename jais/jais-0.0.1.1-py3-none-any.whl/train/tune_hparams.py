import os
import torch
import torch.nn as nn
from typing import Tuple, Optional
from jais.train.trainer import Trainer
from jais.utils import get_logger, load_config

CNF = load_config(os.getenv('JAIS_CNF_PATH'))
LOG = get_logger(CNF, os.getenv('JAIS_LOG_PATH'))

class TuneHP:
    def __init__(self, dataloader, net, loss_fn, optm_fn, device) -> None:
        self.dataloader = dataloader
        self.net = net.to(device)
        self.loss_fn = loss_fn
        self.optm_fn = optm_fn
        self.device = device

    def tune(self, 
             lr_range: Tuple[float, float] = (1., 1e-6),
             wd_range: Tuple[float, float] = (1e-3, 1e-8),
             mom_range: Tuple[float, float] = (0.9, 0.99),
             optm_fn: Optional[nn.Module] = None,
             max_iters: int = 100):

        # set new optimizer, if given
        if optm_fn:
            self.optm_fn = optm_fn
            LOG.info(f"Optimizer changed to {optm_fn}")
        # Find best learning rate range
        # Train on one batch and validate on next
        #TODO ADD LEARNING RATE FINDER CODE HERE
        dl = iter(self.dataloader)
        for i in range(0, max_iters, 2):
            # Train on one batch
            self.net.train()
            self.train_one_batch(next(dl))
            # Validate on next batch
            self.net.eval()
            with torch.no_grad():
                self.val_one_batch(next(dl))
        

    def train_one_batch(self, batch):
        return Trainer.train_one_batch(batch)
    
    def val_one_batch(self, batch):
        return Trainer.val_one_batch(batch)

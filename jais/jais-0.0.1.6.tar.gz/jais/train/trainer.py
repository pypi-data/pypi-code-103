import os
import math
import time
import torch
from pathlib import Path
from typing import Dict, Optional, Any, Union
from collections import OrderedDict
from torchmetrics import Metric
from jais.train.log import TrainingLogger, RichProgress
from jais.utils import manage_log_files
from jais.__main__ import CNF0, LOG


__all__ = ['Trainer']


class Trainer:
    def __init__(self,
                 dls: Dict[str, torch.utils.data.DataLoader],
                 net: torch.nn.Module,
                 loss_fn: torch.nn.Module,
                 optm_fn: torch.nn.Module,
                 device: torch.device,
                 metrics: Optional[Dict[str, Metric]] = None,
                 training_logger_name: Optional[str] = None,
                 training_logs_dir: Optional[Union[str, Path]] = None,
                 training_logs_filename: Optional[Union[str, Path]] = None,
                 keep_n_recent_logs: int = 5,
                 wandb_init_kwargs: Optional[dict] = None) -> None:
        """Training and validation handler class

        Args:
            dls: dict of dataloaders
            net: Network / model to train and validate
            loss_fn: criterion instance
            optm_fn: optimizer instance
            device: device to train on.
            metrics: dict of metrics such as accuracy, precision, recall, etc.
            training_logger_name: Name of the logger to use out of ('wb', 'tb'). 
                e.g. 'wb' for wandb or 'tb' for tensorboard.
            training_logs_dir: path to the folder to save training logs.
            training_logs_filename: Name of the training logs file.
                This file will save per epoch metrics. 
                This is same as the displayed metrics table.
                [Default is `CNF0.log.training_log_filename_prefix@<current time>.csv`]
            wandb_init_kwargs: `wandb.init` function arguments. 
                e.g. {
                    'config': <wandb configurations>
                    'project': <project name>, 
                    'entity': <enitity>,
                }
        """
        self.dls, self.net = dls, net.to(device)
        self.loss_fn, self.optm_fn = loss_fn, optm_fn
        self.device, self.metrics = device, metrics
        self.logger = TrainingLogger(logger_name=training_logger_name,
                                     logs_dir=training_logs_dir,
                                     wandb_init_kwargs=wandb_init_kwargs
                                     ) if training_logger_name else None

        if training_logs_dir is None:
            self.training_logs_dir = Path(CNF0.paths.logs_dir)
        else:
            self.training_logs_dir = Path(training_logs_dir)

        self.training_logs_filename = training_logs_filename
        if self.training_logs_filename is None:
            self.training_logs_filename = f"{CNF0.log.training_log_filename_prefix}@{time.time()}.csv"
        self.keep_n_recent_logs = keep_n_recent_logs

        # Put weights tensor on same device
        if hasattr(self.loss_fn, 'weight') and \
                (self.loss_fn.weight is not None):
            self.loss_fn.weight = self.loss_fn.weight.to(self.device)

    def train_one_batch(self, batch):
        # return loss, outputs, targets
        """
        Either inherit this class to implement new routine
            OR
            def my_train_one_batch_func(self, batch):
                # Routine here
            Trainer.train_one_batch = my_train_one_batch_func
        """
        # DATA
        inputs = batch['inputs'].to(self.device)
        targets = batch['targets'].to(self.device)
        # PREDICT
        outputs = self.net(inputs)
        # LOSS
        loss = self.loss_fn(outputs, targets)
        # BACKWARD
        self.optm_fn.zero_grad()
        loss.backward()
        self.optm_fn.step()
        return loss, outputs, targets

    def val_one_batch(self, batch):
        """
        Either inherit this class to implement new routine
            OR
            def my_val_one_batch_func(self, batch):
                # Routine here
            Trainer.val_one_batch = my_val_one_batch_func
        """
        # DATA
        inputs = batch['inputs'].to(self.device)
        targets = batch['targets'].to(self.device)
        # PREDICT
        outputs = self.net(inputs)
        # LOSS
        loss = self.loss_fn(outputs, targets)
        return loss, outputs, targets

    def train_and_val_one_epoch(self,
                                epoch_num: int,
                                rp: RichProgress = None,
                                max_train_iters: int = None,
                                max_val_iters: int = None) -> Dict[str, Any]:
        """Train and validate one epoch"""
        # Put network in training mode and device
        self.net.train()
        # Train one epoch
        epoch_loss, epoch_outputs, epoch_targets = [], [], []
        for i, batch in enumerate(self.dls['train'], start=1):
            loss, outputs, targets = self.train_one_batch(batch)
            epoch_loss.append(loss)
            epoch_outputs.append(outputs)
            epoch_targets.append(targets)
            rp.update_train_bar()
            if i >= max_train_iters:
                break
        # Compute training metrics
        avg_epoch_loss = torch.tensor(epoch_loss).mean().item()
        # epoch_outputs = torch.cat(epoch_outputs, dim=0).to(self.device)
        # epoch_targets = torch.cat(epoch_targets, dim=0).to(self.device)

        # Validate
        with torch.no_grad():
            self.net.eval()
            val_loss, val_outputs, val_targets = [], [], []
            for i, batch in enumerate(self.dls['val'], start=1):
                loss, outputs, targets = self.val_one_batch(batch)
                val_loss.append(loss)
                val_outputs.append(outputs)
                val_targets.append(targets)
                rp.update_val_bar()
                if i >= max_val_iters:
                    break
            # Compute validation metrics
            avg_val_loss = torch.tensor(val_loss).mean().item()
            val_outputs = torch.cat(val_outputs, dim=0).cpu()
            val_targets = torch.cat(val_targets, dim=0).cpu()
            if self.metrics:
                val_metrics_dict = self.metrics(val_outputs, val_targets)
                val_metrics_dict = {
                    k: v.item() for k, v in val_metrics_dict.items()
                }

        # Update metrics table and logger
        epoch_logs = OrderedDict({
            'epoch_num': epoch_num,
            'train_loss': avg_epoch_loss,
            'val_loss': avg_val_loss,
        })
        if self.metrics:
            epoch_logs.update(val_metrics_dict)
        return epoch_logs

    def train(self,
              n_epochs: int,
              max_train_iters: int = None,
              max_val_iters: int = None,
              optm_fn=None):
        if optm_fn:  # change optimizer
            self.optm_fn = optm_fn
        self.table_columns = ['Epoch', 'TrainLoss']
        if max_train_iters is None:
            max_train_iters = math.ceil(
                len(self.dls['train'].dataset) / self.dls['train'].batch_size
            )
        if (max_val_iters is None) and ('val' in self.dls.keys()):
            max_val_iters = math.ceil(
                len(self.dls['val'].dataset) / self.dls['val'].batch_size
            )
        if 'val' in self.dls.keys():
            self.table_columns.append('ValLoss')
        # Add metrics names as table columns
        self.table_columns += [
            f"Val{k.capitalize()}" for k in self.metrics.keys()
        ]

        with RichProgress(columns=self.table_columns,
                          n_epochs=n_epochs,
                          n_train_iters=max_train_iters,
                          n_val_iters=max_val_iters) as rp:
            for epoch_num in range(1, n_epochs + 1):

                epoch_logs = self.train_and_val_one_epoch(
                    epoch_num=epoch_num,
                    rp=rp,
                    max_train_iters=max_train_iters,
                    max_val_iters=max_val_iters
                )
                if self.logger:
                    self.logger.log(epoch_logs)
                rp.update_epoch(list(epoch_logs.values()))

        # Save logs
        manage_log_files(logs_dir=self.training_logs_dir,
                         keep_n_recent_logs=self.keep_n_recent_logs,
                         file_ext='.csv')
        rp.to_csv(self.training_logs_dir/self.training_logs_filename)

from optparse import Option
import os
import math
import time
import torch
from pathlib import Path
from typing import Dict, Optional, Any, Union
from collections import OrderedDict
from torchmetrics import Metric
from wandb import wandb
from jais.train.log import TrainingLogger, RichProgress
from jais.utils import manage_log_files
from jais.__main__ import CNF, LOG


__all__ = ['Trainer']


class Trainer:
    def __init__(self,
                 dls: Dict[str, torch.utils.data.DataLoader],
                 net: torch.nn.Module,
                 loss_fn: torch.nn.Module,
                 optm_fn: torch.nn.Module,
                 device: torch.device,
                 metrics: Optional[Dict[str, Metric]] = None,
                 chkpts_dir: Optional[Union[str, Path]] = None,
                 chkpt_of: Optional[list[Dict[str, str]]] = [{'val_loss': 'min'}],
                 chkpt_prefix: str = "",
                 training_logger_name: Optional[str] = None,
                 training_logs_dir: Optional[Union[str, Path]] = None,
                 training_logs_filename: Optional[Union[str, Path]] = None,
                 keep_n_recent_logs: Optional[int] = 5,
                 wandb_init_kwargs: Optional[dict] = None,
                 wandb_model_versioning: bool = True) -> None:
        """Training and validation handler class

        Args:
            dls: dict of dataloaders
            net: Network / model to train and validate
            loss_fn: criterion instance
            optm_fn: optimizer instance
            device: device to train on.
            metrics: dict of metrics such as accuracy, precision, recall, etc.
            chkpts_dir: folder path to save trained model and checkpoints.
            chkpt_of: List of names and mode pair 
                (`{<metric name>: <min or max>}`) of the metrics to create 
                a checkpoint on best value. e.g. save model weights when 
                val loss converges from best value. 
                The weights will be saved as `baseline_best_val_loss_wts.pt`.
            chkpt_prefix: Name for model weight's save file. e.g. 
                `chkpt_prefix='baseline'` will save the weights with filename
                `baseline_best_val_loss_wts.pt` or 
                `baseline_best_accuracy_wts.pt` (as per `chkpt_of` names).
            training_logger_name: Name of the logger to use out of ('wb', 'tb'). 
                e.g. 'wb' for wandb or 'tb' for tensorboard.
            training_logs_dir: path to the folder to save training logs.
            training_logs_filename: Name of the training logs file.
                This file will save per epoch metrics. 
                This is same as the displayed metrics table.
                [Default is `CNF.log.training_log_filename_prefix@<current time>.csv`]
            wandb_init_kwargs: `wandb.init` function arguments. 
                e.g. {
                    'config': <wandb configurations>
                    'project': <project name>, 
                    'entity': <enitity>,
                }
            wandb_model_versioning: If True, log model weights to wandb.
        """
        self.dls, self.net = dls, net.to(device)
        self.loss_fn, self.optm_fn = loss_fn, optm_fn
        self.device, self.metrics = device, metrics

        # Checkpoints settings
        if chkpts_dir is None:
            self.chkpts_dir = Path.cwd()/'checkpoints'
        else:
            self.chkpts_dir = Path(chkpts_dir)
        self.chkpts_dir.mkdir(exist_ok=True)
        # Save model weights on given metrics
        self.chkpts_handler = {}
        self.chkpt_of = chkpt_of
        for _met_dict in chkpt_of:
            _met_name, _met_mode = list(_met_dict.items())[0]
            if _met_mode == 'min':
                self.chkpts_handler[_met_name] = float('inf')
            elif _met_mode == 'max':
                self.chkpts_handler[_met_name] = 0.
            else:
                _errmsg = "Either pass `min` to save weights when converge "
                _errmsg += "(for losses) or pass `max` to save weights when "
                _errmsg += "metric improves (such as accuracy)"
                raise ValueError(_errmsg)
        self.chkpt_prefix = f"{chkpt_prefix}_" if chkpt_prefix else ''

        # Training logger and settings
        self.training_logger_name = training_logger_name
        self.wandb_model_versioning = wandb_model_versioning
        self.logger = TrainingLogger(logger_name=training_logger_name,
                                     logs_dir=training_logs_dir,
                                     wandb_init_kwargs=wandb_init_kwargs
                                     ) if training_logger_name else None
        if training_logs_dir is None:
            self.training_logs_dir = Path(CNF.paths.logs_dir)
        else:
            self.training_logs_dir = Path(training_logs_dir)
        self.training_logs_filename = training_logs_filename
        if self.training_logs_filename is None:
            _path = f"{CNF.log.training_log_filename_prefix}@{time.time()}.csv"
            self.training_logs_filename = _path
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

        # Save checkpoints when metric improves
        self._create_checkpoint(epoch_logs)
        return epoch_logs

    def _create_checkpoint(self, epoch_logs) -> None:
        """Save checkpoints when metric improves"""
        for _met_dict in self.chkpt_of:
            _met_name, _met_mode = list(_met_dict.items())[0]
            if _met_name not in epoch_logs.keys():
                _errmsg = f"Metric `{_met_name}` must match names in given" 
                _errmsg += "metrics. Available metrics are "
                _errmsg += f"{self.metrics.keys()}."
                raise KeyError(_errmsg)
            savename = f"{self.chkpt_prefix}best_{_met_name}_wts.pt"
            savepath = self.chkpts_dir/ savename
            _msg  = f"`{_met_name}` improved from "
            _msg += f"{self.chkpts_handler[_met_name]:.5f} to "
            _msg += f"{epoch_logs[_met_name]:.5f}. "
            _msg += f"Checkpoint saved @ `{savepath}`."
            if _met_mode == 'min':
                if epoch_logs[_met_name] < self.chkpts_handler[_met_name]:
                    torch.save(self.net.state_dict(), savepath)
                    self.chkpts_handler[_met_name] = epoch_logs[_met_name]
                    LOG.info(_msg)
            else:
                if epoch_logs[_met_name] > self.chkpts_handler[_met_name]:
                    torch.save(self.net.state_dict(), savepath)
                    self.chkpts_handler[_met_name] = epoch_logs[_met_name]
                    LOG.info(_msg)
        
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

        # Save last epoch model weights
        savepath = self.chkpts_dir/f'{self.chkpt_prefix}last_epoch_wts.pt'
        torch.save(self.net.state_dict(), savepath)

        # Log model to wandb, if given
        if (self.training_logger_name in ['wb', 'wandb']) and \
            (self.wandb_model_versioning):
            trained_model_artifact = wandb.Artifact(
                f'TrainedModel-{self.net.__class__.__name__}',
                type='model')
            trained_model_artifact.add_dir(self.chkpts_dir)
            wandb.log_artifact(trained_model_artifact)

        # Save logs
        manage_log_files(logs_dir=self.training_logs_dir,
                         keep_n_recent_logs=self.keep_n_recent_logs,
                         file_ext='.csv')
        rp.to_csv(self.training_logs_dir/self.training_logs_filename)

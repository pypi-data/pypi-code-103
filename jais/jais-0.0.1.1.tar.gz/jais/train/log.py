import os
from pathlib import Path
from typing import Dict, Union
from torch import Tensor
from numpy import ndarray
from pandas import DataFrame
from rich import print
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table
from jais.utils import load_default_configs


__all__ = ['TrainingLogger', 'RichProgress']


CNF, LOG = load_default_configs()


class TrainingLogger:
    def __init__(self, 
                 logger_name: str = None, 
                 log_dir: Union[Path, str] = CNF.paths.logs_dir) -> None:
        """
        Metrics logs handling class for training and validation per 
            epoch or batch

        Args:
            logger_name: name of the logger to use. 
                [wandb (wb), tensorboard (tb), locallogger (ll)]
        """
        self.logger_name = logger_name
        self.log_dir = log_dir
        if self.logger_name:
            if self.logger_name in ['wb', 'wandb']:
                import wandb
                wandb.init(project=CNF.project_name, 
                        dir=self.log_dir, 
                        save_code=True)
                self.logger = wandb.log
            elif self.logger_name in ['tb', 'tensorboard']:
                from torch.utils.tensorboard import SummaryWriter

                self.writer = SummaryWriter(log_dir=f"{self.log_dir}/tensorboard")
            else:
                raise ValueError("Only `wandb` and `tensorboard` is supported.")

    def log(self, logs: Dict[str, Union[Tensor, ndarray, float]]) -> None:
        """Add the metrics to the metrics list

        Args:
            logs: dict of values to add in the history
        """        
        # Log to the particular logger
        if self.logger_name:
            if self.logger_name in ['tb', 'tensorboard']:
                for k, v in logs.items():
                    if k.endswith('_loss'):
                        self.writer.add_scalar(
                            f"Loss/{k.split('_')[0]}", 
                            v, 
                            global_step=logs['epoch_num'])
                    else:
                        self.writer.add_scalar(k, v, global_step=logs['epoch_num'])
            elif self.logger_name in ['wb', 'wandb']:
                self.logger(logs)
            else:
                _errmsg = "Only `wandb` and `tensorboard` is supported."
                raise NotImplementedError(_errmsg)


class RichProgress:
    def __init__(self, 
                 columns: list, 
                 n_epochs: int, 
                 n_train_iters: int, 
                 n_val_iters: int, 
                 refresh_rate: int = 10) -> None:
        self.columns, self.n_epochs, self.epoch_num = columns, n_epochs, 1
        self.n_train_iters, self.n_val_iters = n_train_iters, n_val_iters

        self.progress_bar = Progress(
            "{task.description}",
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            transient=True
        )
        self.epoch_bar = self.progress_bar.add_task(
            f"[cyan]Overall", total=self.n_epochs
        )
        self.train_bar = self.progress_bar.add_task(
            f"Epoch [1/{self.n_epochs}]", 
            total=self.n_train_iters, 
            visible=False
        )
        self.val_bar = self.progress_bar.add_task(
            f"Validate", total=self.n_val_iters, visible=False
        )

        # Make Table and Bars
        progress_table = Table.grid(expand=True)
        self.metrics_table = Table()
        for col in self.columns:
            self.metrics_table.add_column(col, justify='center')
        progress_table.add_row(self.metrics_table)
        progress_table.add_row(self.progress_bar)

        self.live = Live(progress_table, 
                         refresh_per_second=refresh_rate, 
                         vertical_overflow=None)
                         
    def __enter__(self) -> None:
        self.live.start()
        return self

    def update_epoch(self, row: list) -> None:
        """Update metrics table and progress"""

        typecast = lambda x: f"{x:.4f}" if isinstance(x, float) else str(x)

        self.reset_progress_bars()
        self.metrics_table.add_row(*map(typecast, row))
        self.progress_bar.update(self.epoch_bar, advance=1)
        self.epoch_num += 1 # For self.train_bar value
        
    def update_train_bar(self) -> None:
        """Update the training progress bar visualizations"""
        description = f"Epoch [{self.epoch_num}/{self.n_epochs}]"
        self.progress_bar.update(self.train_bar,
                                 description=description,
                                 advance=1, visible=True)
        self.progress_bar.update(self.val_bar, visible=False)
        
    def update_val_bar(self) -> None:
        """Update the validation progress bar visualizations"""
        self.progress_bar.update(self.train_bar, visible=False)
        self.progress_bar.update(self.val_bar, advance=1, visible=True)

    def reset_progress_bars(self) -> None:
        """Reset progress bars for next epoch"""
        self.progress_bar.reset(self.train_bar)
        self.progress_bar.reset(self.val_bar)

    def __exit__(self, *args) -> None:
        """Clear per epoch bars and stop live display"""
        self.progress_bar.disable = True
        self.progress_bar.update(self.train_bar, visible=False)
        self.progress_bar.update(self.val_bar, visible=False)
        self.live.stop()

    def to_csv(self, savepath: str) -> None:
        df = {
            col.header: col._cells 
            for col in self.metrics_table.__dict__['columns']
        }
        DataFrame.from_dict(df).to_csv(savepath, index=False)
        print(f"Training logs saved @ `{savepath}`")
        

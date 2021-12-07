import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple


__all__ = [
    # Functions
    'minmaxscaler',

    # Classes
    'OptmWithLRSWrapper',
]

# ============================= FUNCTIONS ==============================
def minmaxscaler(x: list, axis=0, min=0, max=1):
        x_std = (x - x.min(axis=axis)) / (x.max(axis=axis) - x.min(axis=axis))
        x_scaled  = x_std * (max - min) + min
        return x_scaled

def jais_lr_scheduler_values(num_epochs: int,
                             num_iters_per_epochs: int,
                             warmup_pct: float = 0.20,
                             lr_range: Tuple[float, float] = (0.01, 1e-6),
                             verbose: bool = False) -> list:
    # Number of iterations / batches in one epoch
    max_lr, min_lr = lr_range
    num_iters = num_iters_per_epochs
    n_steps = num_epochs * num_iters  # Total steps 
    n_warmup_steps = int(n_steps * warmup_pct)  # Number of warmup steps
    n_rem_steps = n_steps - n_warmup_steps  # Number of StepLR steps
    # Warmup lr values list
    warmup_lr = minmaxscaler(
        np.sqrt(np.linspace(min_lr, max_lr, num=n_warmup_steps)),
        min=min_lr, max=max_lr
    )
    n_steplr_epochs = int(n_rem_steps / num_iters) # Number of epochs for StepLR 
    # Remaining steps after warmup and StepLR
    n_rem_steps = n_steps - (n_warmup_steps + (n_steplr_epochs * num_iters))
    # StepLR values per epoch
    if n_rem_steps != 0: # Keep `min_lr` away for further adjustment
        steplr_epochs_lr = np.linspace(max_lr, min_lr * 10, num=n_steplr_epochs)
    else:
        # Do adjustments till `min_lr`
        steplr_epochs_lr = np.linspace(max_lr, min_lr, num=n_steplr_epochs)
    steplr_lr = np.repeat(steplr_epochs_lr, num_iters)  # StepLR values per 
    if n_rem_steps != 0:
        rem_lr = list(np.linspace(min_lr*10, min_lr, num=n_rem_steps))
        total_lr = list(warmup_lr) + list(steplr_lr) + rem_lr
    else:
        total_lr = list(warmup_lr) + list(steplr_lr)
    assert len(total_lr) == n_steps, f"total_lr = {len(total_lr)} but n_steps = {n_steps}."
    if verbose:
        plt.figure(figsize=(10,5))
        plt.title("JAIS Custom Learning Rate Scheduler")
        plt.plot(range(len(total_lr)), total_lr)
    return total_lr


# ============================= CLASSES ==============================
class OptmWithLRSWrapper:
    def __init__(self,
                 optm_fn,
                 num_epochs: int,
                 num_iters_per_epochs: int,
                 warmup_pct: float = 0.20,
                 lr_range: Tuple[float, float] = (0.01, 1e-6)) -> None:
        """Learning Rate Scheduler Wrapper"""
        self.optm_fn = optm_fn
        self.step_num = 0
        self.lr_list = jais_lr_scheduler_values(
            num_epochs=num_epochs,
            num_iters_per_epochs=num_iters_per_epochs,
            warmup_pct=warmup_pct,
            lr_range=lr_range)

    def step(self) -> None:
        "Step with the inner optimizer"
        self.update_lr()
        self.optm_fn.step()

    def zero_grad(self):
        "Zero out the gradients with the inner optimizer"
        self.optm_fn.zero_grad()
    
    def update_lr(self) -> None:
        try:
            self.current_lr = self.lr_list[self.step_num]
        except IndexError:
            # When last batch has less samples than others
            self.current_lr = self.lr_list[-1]
        for param_group in self.optm_fn.param_groups:
            param_group['lr'] = self.current_lr
        self.step_num += 1

    def get_lr(self) -> float:
        return self.current_lr
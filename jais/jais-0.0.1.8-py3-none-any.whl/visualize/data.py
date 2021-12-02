"""Data Visualization Module"""
from rich import print
from typing import Union, List
from numpy import ndarray
from torch import Tensor
import matplotlib.pyplot as plt

def show_batch(inputs: Union[ndarray, Tensor, List[ndarray]],
               targets: Union[ndarray, Tensor, List[ndarray]],
               outputs: Union[None, ndarray, Tensor, List[ndarray]] = None,
               n_cols: int = None, 
               title_fontsize: int = 20) -> None:
    """Display images in a grid

    Args:
        inputs: sample images
        targets: ground truth
        outputs: predictions
        n_cols: Number of columns to plot in the figure
        title_fontsize: font size of the main plot's title
    """
    n_inputs_dims = len(inputs.shape)

    if n_inputs_dims == 3:
        batch_size, height, width = inputs.shape
        n_channels = 1
    elif n_inputs_dims == 4:
        batch_size, n_channels, height, width = inputs.shape
    else:
        raise NotImplementedError("3D or 4D inputs supported only.")

    if n_cols is None:
        if batch_size <= 8:
            n_cols, n_rows = batch_size, 1
        else:
            n_cols = 8
            n_rows = batch_size // n_cols
    else:
        if batch_size % n_cols != 0:
            n_rows = batch_size // n_cols
            msg = f"Displaying {n_rows * n_cols} images out of {batch_size} "
            msg += f"because full grid matrix is not possible with n_cols={n_cols}."
            print(msg)
        else:
            n_rows = batch_size // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols*2, (n_rows*2)+1))
    for i, ax in enumerate(axes.flat):
        sample_image = inputs[i]
        ax.imshow(sample_image, cmap='gray' if n_channels == 1 else None)
        true_label = targets[i]
        pred_label = true_label if outputs is None else outputs[i]
        color = "green" if true_label == pred_label else "red"
        if outputs is None:
            ax.set_title(pred_label, color=color, fontdict={
                'fontsize': title_fontsize})
        else:
            ax.text(0.40, 1.1, pred_label, fontsize=20, color=color, ha='right',
                    verticalalignment='center', transform=ax.transAxes)
            ax.text(0.55, 1.1, " |", fontsize=20, color='white', ha='right',
                    verticalalignment='center', transform=ax.transAxes)
            ax.text(0.60, 1.1, true_label, fontsize=20, color='g', ha='left',
                    verticalalignment='center', transform=ax.transAxes)
        ax.axis('off')
    plt.show()

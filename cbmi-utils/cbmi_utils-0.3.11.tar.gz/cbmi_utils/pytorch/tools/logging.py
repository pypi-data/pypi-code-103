import logging
from typing import Any, Iterable, List, Mapping, Optional, Sequence, Union

import torch
from torchinfo import summary


def get_model_summary(model: torch.nn.Module,
                      input_size: Optional[Sequence[Union[int, Sequence[Any], torch.Size]]] = None,
                      input_data: Optional[Union[torch.Tensor, Sequence[Any], Mapping[str, Any]]] = None,
                      batch_dim: Optional[int] = None,
                      cache_forward_pass: Optional[bool] = None,
                      col_names: Optional[Iterable[str]] = None,
                      col_width: int = 25,
                      depth: int = 3,
                      device: Optional[Union[torch.device, str]] = None,
                      dtypes: Optional[List[torch.dtype]] = None,
                      row_settings: Optional[Iterable[str]] = None,
                      verbose: Optional[int] = None,
                      **kwargs: Any,):
    """
    See torchinfo's summary function for further information on parameters
    """
    model_stats = summary(model=model,
                          input_size=input_size,
                          input_data=input_data,
                          batch_dim=batch_dim,
                          cache_forward_pass=cache_forward_pass,
                          col_names=col_names,
                          col_width=col_width,
                          depth=depth,
                          device=device,
                          dtypes=dtypes,
                          row_settings=row_settings,
                          verbose=verbose,
                          **kwargs)
    return str(model_stats)


def print_learnable_params(model, freezed_too=True):
    """ Print (learnable) parameters in a given network model

    Args:
        model: Model you want to print the learned parameters
        freezed_too: Print the freezed parameters as well
    """
    logger = logging.getLogger()
    updated = []
    freezed = []

    for name, param in model.named_parameters():
        if param.requires_grad:
            updated.append(name)
        else:
            freezed.append(name)

    logger.info("-- Following parameters will be updated:")

    for para in updated:
        logger.info(f"  -- {para}")
    if freezed_too is True:
        logger.info("-- Following parameters are freezed:")
        for para in freezed:
            logger.info(f"  -- {para}")

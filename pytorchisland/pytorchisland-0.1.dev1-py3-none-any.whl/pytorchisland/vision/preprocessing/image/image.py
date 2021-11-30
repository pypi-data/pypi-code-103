import torch
import torch.nn as nn
import numpy as np


def image_to_tensor(image)-> torch.Tensor:
    """Convert image into tensor"""
    
    image_shape = image.shape
    image_dim = len(image_shape)
    if(image_dim<2 or image_dim>3):
        raise ValueError("Invalid image shape")

    tensor = torch.from_numpy(image) 

    if(image_dim==2):
        tensor = tensor.unsqueeze(0)
    elif(image_dim==3):
        tensor = tensor.permute(2,0,1)
    else:
        raise ValueError("Invalid image shape")

    return tensor 

def tensor_to_image(tensor) -> "np.ndarray":
    """Convert tensor into image"""
    if not isinstance(tensor,torch.Tensor):
        raise ValueError("Input type is invalid")
    input_shape = tensor.shape
    input_dim = len(input_shape)
    if(input_dim<2 or input_dim>3):
        raise ValueError("Invalid tensor shape")
    image = tensor.cpu().detach().numpy()
    if (input_dim==2):
        pass
    elif (input_dim==3):
        if (input_shape[0]==1):
            # gray scale image
            image = image.squeeze()
        else:
            image = image.transpose(1,2,0)
    else:        
        raise ValueError("Invalid tensor shape")
    return image    
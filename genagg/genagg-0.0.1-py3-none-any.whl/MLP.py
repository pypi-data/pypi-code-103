import torch.nn as nn
import numpy as np

class MLP(nn.Module):

	def __init__(self, input_dim, output_dim, layer_sizes, batchnorm=True):
		super(MLP, self).__init__()
		self.input_dim = input_dim
		self.output_dim = output_dim
		self.batchnorm = batchnorm
		layer_sizes_full = [input_dim] + layer_sizes + [output_dim]
		layers = []
		for i in range(len(layer_sizes_full)-1):
			layers.append(nn.Linear(layer_sizes_full[i], layer_sizes_full[i+1]))
			if i != len(layer_sizes_full)-2:
				if batchnorm:
					layers.append(BatchNorm(layer_sizes_full[i+1]))
				layers.append(nn.ReLU())
		self.net = nn.Sequential(*layers)


	def forward(self, X):
		return self.net(X)



class BatchNorm(nn.Module):

	def __init__(self, *args, **kwargs):
		super().__init__()
		self.bn = nn.BatchNorm1d(*args, **kwargs)

	def forward(self, x):
		shape = x.shape
		x_r = x.reshape(np.prod(shape[:-1]), shape[-1])
		y_r = self.bn(x_r)
		y = y_r.reshape(shape)
		return y


def layergen(input_dim, output_dim, nlayers=1, midmult=1.):
	midlayersize = midmult * (input_dim + output_dim)//2
	midlayersize = max(midlayersize, 1)
	nlayers += 2
	layers1 = np.around(np.logspace(np.log10(input_dim), np.log10(midlayersize), num=(nlayers)//2)).astype(int)
	layers2 = np.around(np.logspace(np.log10(midlayersize), np.log10(output_dim), num=(nlayers+1)//2)).astype(int)[1:]
	return list(np.concatenate([layers1, layers2])[1:-1])
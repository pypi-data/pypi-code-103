from typing import Callable
from typing import Optional
from torch_geometric.typing import Adj
from torch import Tensor

from functools import partial

import torch
from torch_geometric.nn import MessagePassing, GraphConv

from genagg import GenAggSparse
from genagg.MLP import MLP, layergen


def patch_conv_with_aggr(cls, aggr_cls, *aggr_args, **aggr_kwargs):
	"""Patch a general pytorch_geometric conv layer to
	use a custom aggregation function"""
	class PatchedConv(cls):
		def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)
			# Build aggr at init so we can create
			# multiple gnn layers with differing weights
			self.aggr = aggr_cls(*aggr_args, **aggr_kwargs)

		def aggregate(self, 
			inputs: Tensor, index: Tensor, 
			ptr: Optional[torch.Tensor] = None, 
			dim_size: Optional[int] = None
		) -> Tensor:
			return self.aggr(inputs, index) 

	return PatchedConv

class AggGNN(MessagePassing):
	def __init__(self, 
			fupdate : Callable = lambda x_i, x_j_agg: x_i + x_j_agg,
			fcom : Callable = lambda x_i, x_j: x_j,
		):
		super().__init__()
		self.aggr = GenAggSparse(p=1., a=0., shift=True, learnable=True)
		self.fcom = fcom
		self.fupdate = fupdate

	def forward(self, x: Tensor, edge_index: Adj) -> Tensor:
		neighbour_agg = self.propagate(edge_index=edge_index, x=x)
		y = self.fupdate(x, neighbour_agg)
		return y

	def aggregate(self, inputs: Tensor, index: Tensor,  ptr: Optional[torch.Tensor] = None, dim_size: Optional[int] = None) -> Tensor:
		return self.aggr(inputs, index) 

	def message(self, x_i: Tensor, x_j: Tensor) -> Tensor:
		return self.fcom(x_i, x_j)


def create_agg_gnn(in_dim, out_dim, nlayers=3, batchnorm=True, midmult=1.):
	# Creates a GNN with the given parameters
	# nlayers: the number of layers for both MLPs (3 layers means [input_dim, hidden1, hidden2, output_dim])
	# batchnorm: whether or not to include batchnorm in both MLPs
	# midmult: the middle layer of each MLP will be of size [midmult * (input_dim + output_dim) / 2]
	def compose(*inputs, f=None):
		return f(torch.cat(inputs, dim=-1))

	fcom_net = MLP(input_dim=in_dim*2, output_dim=in_dim, batchnorm=batchnorm,
				layer_sizes=layergen(input_dim=in_dim, output_dim=in_dim, nlayers=nlayers, midmult=midmult))
	fupdate_net = MLP(input_dim=in_dim*2, output_dim=out_dim, batchnorm=batchnorm,
				layer_sizes=layergen(input_dim=in_dim, output_dim=out_dim, nlayers=nlayers, midmult=midmult))
	fcom = partial(compose, f=fcom_net)
	fupdate = partial(compose, f=fupdate_net)
	gnn = AggGNN(fupdate=fupdate, fcom=fcom)
	return gnn


if __name__ == '__main__':
	from torch_geometric.data import Data
	aggr = GenAggSparse(p=1., a=0., shift=True, learnable=True)
	GraphConvGenAgg = patch_conv_with_aggr(GraphConv, aggr)
	gnn = GraphConvGenAgg(1, 1) 
	#gnn = create_agg_gnn(in_dim=1, out_dim=1)


	edge_index = torch.tensor([[0, 1, 1, 2],
								[1, 0, 2, 1]], dtype=torch.long)
	x = torch.tensor([[-1], [0], [1]], dtype=torch.float)
	data = Data(x=x, edge_index=edge_index)

	out = gnn(x=data.x, edge_index=data.edge_index)

	print(out)



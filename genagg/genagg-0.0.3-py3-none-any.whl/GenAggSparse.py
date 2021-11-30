import torch
import math
from typing import Callable, Tuple
from torch_scatter import scatter



class GenAggSparse(torch.nn.Module):
	"""Generalized aggregation operator"""
	def __init__(self,
			# p term in generalized mean
			p: float = 1.0, 
			# premultiply gen-mean by N^a 
			# so we can normalize wrt to num neighbors
			a: float = 0.0, 
			# Whether to shift x into positive real to avoid
			# complex numbers
			shift: bool = True, 
			# Whether a,p should be learnable or fixed
			learnable: bool = True, 
			# Mapping function from parameter p' => actual p
			# use this if we don't want p to change linearly
			# (e.g. we want to approach p=inf faster, so map 
			# p = tan(p'))
			map_fn: Callable = lambda p: torch.tan(p * math.pi / 4),
			# Bounds the domain of p to prevent over/underflow
			# for the default map_fn, this should be betwee -1.99.. and 1.99..
			p_domain: Tuple[float, float] = [-1.98, 1.98]
	):
		super().__init__()
		self.p = torch.nn.Parameter(torch.tensor([p]).float()) if learnable else torch.tensor([p]).float()
		self.a = torch.nn.Parameter(torch.tensor([a]).float()) if learnable else torch.tensor([a]).float()
		self.shift = shift
		self.learnable = learnable
		self.p_domain = p_domain
		self.map_fn = map_fn

	def forward(self, x, index, **kwargs):
		# Clamp p parameter to prevent over/underflows
		if self.learnable:
			self.p.data = self.p.data.clamp(*self.p_domain)
		if self.map_fn:
			p = self.map_fn(self.p)

		y = gen_agg_sparse(x, index, p=p, a=self.a, shift=self.shift, special=(not self.learnable), **kwargs)
		if torch.is_complex(y):
			y = y.real
		return y



def gen_agg_sparse(x, index, p=1, a=0, shift=True, special=False, agg_dim=0, dim_size=None):
	"""Generalized mean aggregation. If shift is true,
	then apply transformations to ensure well-behaved outputs."""

	if x.numel() == 0:
		shape = list(x.shape)
		shape[agg_dim] = dim_size
		return torch.zeros(shape, device=x.device, dtype=x.dtype)

	# special cases
	if special:
		if p == math.inf:
			if torch.is_complex(x):
				x = x.real
			return scatter(x, index, dim=agg_dim, dim_size=dim_size, reduce="max")
		elif p == -math.inf:
			if torch.is_complex(x):
				x = x.real
			return scatter(x, index, dim=agg_dim, dim_size=dim_size, reduce="min")
		elif p == 0:
			dtype = x.dtype
			if torch.is_complex(x):
				x = x.real
			N = scatter(torch.ones(x.shape[agg_dim], device=x.device), index, dim=agg_dim, dim_size=dim_size, reduce="sum")
			prod = scatter(x, index, dim=agg_dim, dim_size=dim_size, reduce="mul")
			Y = torch.pow(prod.cfloat(), 1/N)
			return Y.type(dtype)

	# number of neighbours
	N = scatter(torch.ones(x.shape[agg_dim], device=x.device), index, dim=agg_dim, dim_size=dim_size, reduce="sum")
	# Can't have divide by zero error, this should not affect final results
	N[N==0] = 1

	# when shift is True, p=0 is min, p=1 is avg, p=inf is max
	if shift:
		if torch.is_complex(x):
			x = x.real
		# TODO: handle empty x
		shifts, _ = x.min(dim=agg_dim)
		shifts -= 1e-3
		x = x - shifts
		Y = torch.exp(1 / p * (-torch.log(N)[:,None] + logsumexp_sparse(p * torch.log(x), index=index, agg_dim=agg_dim, dim_size=dim_size)))
		return (N[:,None] ** a) * (Y + shifts)
	# when shift is False, p=-inf is min, p=0 is prod, p=1 is avg, p=inf is max
	else:
		return torch.exp((a * torch.log(N)[:,None]) + 1 / p * (-torch.log(N)[:,None] + logsumexp_sparse(p * torch.log(x), index=index, agg_dim=agg_dim, dim_size=dim_size)))



def logsumexp_sparse(x, index, agg_dim=0, dim_size=None):
	"""log-sum-exp that works for both real and complex
	torch tensors"""
	dtype = x.dtype
	if torch.is_complex(x):
		c_max, _ = x.real.max(dim=agg_dim)
		c_min, _ = x.real.min(dim=agg_dim)
		x = x.cdouble()
	else:
		c_max, _ = x.max(dim=agg_dim)
		c_min, _ = x.min(dim=agg_dim)
		x = x.double()
	c = (c_max + c_min) / 2
	c.unsqueeze(agg_dim)
	shifted = torch.exp(x - c)
	summed = scatter(shifted, index, dim=agg_dim, dim_size=dim_size, reduce="sum")
	res = c + torch.log(summed).type(dtype)
	return res



### Test ###



if __name__ == '__main__':
	in_size = 5
	out_size = 1
	# Shape [nodes, node_feats]
	x = torch.randn(in_size,2).cfloat() * 100
	index = torch.randint(low=0, high=out_size, size=(in_size,))
	p = 1.99
	#res = gen_agg_sparse(x=x, p=p, index=index, shift=False)
	g = GenAggSparse(p=p, shift=False)
	res = g(x, index)

	# Shifted version
	g = GenAggSparse(p=p, shift=True)
	shifted = g(x, index)


	# Verify
	p = 100
	true_sum = (1 / x.shape[0] * ((x.cfloat() ** p).sum(dim=0))) ** (1 / p)

	print("x:", x)
	print("genagg:", res)
	print("genagg (shifted):", shifted)
	print("true sum:", true_sum)

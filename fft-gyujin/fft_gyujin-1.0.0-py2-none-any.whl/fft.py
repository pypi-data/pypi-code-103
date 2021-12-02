#!/usr/bin/python3

import math

def fftg(data):
	rearrange(data)
	output = compute(data)
	return output

def rearrange(data):
	j = 0
	k = 0
	N = len(data)
	for i in range(0, N):
		if j > i:
			data[i], data[j] = data[j], data[i]
		k = N / 2
		while(k >= 2 and j >= k):
			j -= k
			k = k/2
			j += k;
		j = int(j)


def compute(data_re):
	output = []
	PI = -3.141592
	step = 1
	N = len(data_re)
	data_im = [0] * N
	result = [0] * N
	output = [0] * N
	while step < N:
		jump = step << 1
		n_re = 1
		n_im = 0
		group = 0
		while group < step:    
			pair = group
			while pair < N:
				match = pair + step
				result_re = n_re * data_re[match] - n_im * data_im[match]
				result_im = n_im * data_re[match] + n_re * data_im[match]
				data_re[match] = data_re[pair] - result_re
				data_im[match] = data_im[pair] - result_im
				data_re[pair] = data_re[pair] + result_re
				data_im[pair] = data_im[pair] + result_im
				pair += jump
			angle = PI * (group + 1) / step
			n_re = math.cos(angle)
			n_im = math.sin(angle)
			group = group + 1
		step = step << 1
	for i in range(0, N):
		result[i] = math.sqrt(math.pow(data_re[i], 2) + math.pow(data_im[i], 2))
		output[i] = 10 * math.log10(math.exp(-20) + result[i])
	return output




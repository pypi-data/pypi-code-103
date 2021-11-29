"""Genetic Algorith approach to optimizing input model parameters.

Uses method described in "Using genetic algorithms to optimise model parameters, Q.J.Wang(1997).
"""

# %%
from matplotlib import pyplot as plt
import numpy
import random

example_param_base = {
    "foo": 10,
    "bar": 100,
}

ga_config = {
    "foo": {
        "key": "foo",
        "type": "number",
        "min": 3,
        "max": 8,
    }
}

data = [1, 2, 3, 3]


def encode_parameters(param):
    return list(param.items())


def decode_parameters(param):
    return {k: v for k, v in param}


def combine_param_state(param_a, param_b):
    encoded_param_a = encode_parameters(param_a)
    encoded_param_b = encode_parameters(param_b)
    number_of_params = len(encoded_param_a)
    k1 = random.randint(0, number_of_params-1)
    k2 = random.randint(0, number_of_params-1)

    pa = encoded_param_a[0:k1] if k1 < k2 else encoded_param_b[0:k2]
    pb = encoded_param_a[k1:k2] if k1 < k2 else encoded_param_b[k2: k1]
    pc = encoded_param_a[k2:] if k1 < k2 else encoded_param_b[k1:]

    new_encoded_param = pa + pb + pc
    new_param = decode_parameters(new_encoded_param)
    return new_param


def generate_param_state(param_base, gaconf):
    new_param = {**param_base, 'foo': random.randint(0, 10)}
    return new_param


def mutate_param_state(param, gaconf):
    new_foo = param['foo'] + random.randint(-9, 9)
    new_param = {**param, 'foo': new_foo}
    return new_param


def example_ga(param_base, gaconf, func, optfunc, input_data, population=10, tolerance=0.1, max_iterations=1000):
    initial_parameters = [generate_param_state(param_base, gaconf) for i in range(population)]

    parameters = initial_parameters
    best_parameters = parameters[0]
    loss = 9999999
    lowest_loss = 999999
    iterations = 0
    loss_values = []

    while loss > tolerance and iterations < max_iterations:
        # Run and get losses
        outputs = [func(params, input_data) for params in parameters]
        losses = [optfunc(o, p) for p, o in zip(parameters, outputs)]
        loss = min(losses)
        loss_values.append(loss)
        lowest_loss = loss if loss < lowest_loss else lowest_loss
        total_loss = sum(losses)

        # Sort parameters
        parameters_index_sorted = list(
            map(lambda x: x[0], sorted(enumerate(losses), key=lambda si: si[1])))

        # Set new best parameters if loss is lowest
        best_parameters = parameters[parameters_index_sorted[0]
                                     ] if loss < lowest_loss else best_parameters

        # Choose next parameter pairs based on
        loss_ratios = [((total_loss - loss)/total_loss)/(population-1) for loss in losses]
        choices_population = [numpy.random.choice(
            population, 2, p=loss_ratios) for i in range(population)]
        new_parameters = [combine_param_state(*[parameters[i] for i in choices])
                          for choices in choices_population]

        mutated_new_parameters = [mutate_param_state(param, gaconf) for param in new_parameters]

        parameters = mutated_new_parameters

        iterations += 1
    last_output = outputs[parameters_index_sorted[0]]
    return best_parameters, iterations, last_output, loss_values


def model(config, data):
    # return config['foo']
    return sum(data) * config['foo']


def loss_function(output, params):
    """The lower the return value the closer it is to optimum."""
    return abs(params['bar'] - output)


example_ga(
    example_param_base, ga_config, model, loss_function, data, max_iterations=5)
# %%
out = model(example_param_base, data)
loss_function(out, example_param_base)


# %%
best_parameters, iterations, last_output, loss_values = example_ga(
    example_param_base, ga_config, model, loss_function, data, max_iterations=5000, tolerance=0.1)
plt.plot(loss_values)
# %%
best_parameters, iterations, last_output

# %%

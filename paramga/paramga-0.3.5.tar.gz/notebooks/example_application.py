"""Example of using the library."""
# %%

from paramga.run import run_iterator
from matplotlib import pyplot as plt
from math import exp
import numpy as np
# %%


def demo_state():
    return {
        "foo": 800,
        "bar": 360,
        "zoo": 400
    }

def demo_conf():
    return {
        "foo": {
            "type": "number",
            "min": 1,
            "max": 1000,
            "step": 10,
        },
        "zoo": {
            "type": "number",
            "min": 80,
            "max": 500,
            "step": 10,
        }
    }

def demo_model():
    def model(params, data):
        return sum(data) * params['foo']
    return model

def demo_loss_function():
    def loss_function(output, params):
        x = params['bar'] - output
        return abs((x / (1 + exp(x))))
        # return abs(params['bar'] - output)
    return loss_function

def demo_data():
    return [1, 2, 3, 3]

def demo_best_params():
    return {
        "foo": 40,
        "bar": 360,
        "zoo": 10,
    }


fg, axs = plt.subplots(nrows=3, figsize=(20,5))
def demo_model_b(params, data):
    return (params['foo'] - params['zoo'])** 2 if params['foo'] < 100 else params['foo']**2 #sum([v for v in params.values()])
for i in range(10):
    model_iterator = run_iterator(
        demo_state(),
        demo_conf(),
        demo_model_b,
        demo_loss_function(),
        demo_data(),
        max_iterations=100,
        tolerance=None,
        verbose=False,
        population=(i + 1) * 3,
    )

    states = list(model_iterator)
    states

    loss = [s.loss for s in states]
    axs[0].plot(loss, label=i)

    param_foo = [s.parameters[0]['foo'] for s in states]
    axs[1].plot(param_foo, label=i)


    param_bar = [s.parameters[0]['zoo'] for s in states]
    axs[2].plot(param_bar, label=i)
    print(states[0].best_parameters)
for ax in axs:
    ax.legend()
# %%
states[-1].best_parameters

# %%
# Plot
for i in range(5):
    model_iterator = run_iterator(
        demo_state(),
        demo_conf(),
        demo_model_b,
        demo_loss_function(),
        demo_data(),
        max_iterations=200,
        tolerance=0.1,
        verbose=False,
        population=(i + 1) * 3,
    )

    states = list(model_iterator)
    states

    loss = [s.loss for s in states]
    axs[0].plot(loss, label=i)

    param_foo = [s.parameters[0]['foo'] for s in states]
    axs[1].plot(param_foo, label=i)


    param_bar = [s.parameters[0]['zoo'] for s in states]
    axs[2].plot(param_bar, label=i)
    print(states[0].best_parameters)
    x = [s.best_parameters['foo'] for s in states]
    y = [s.best_parameters['zoo'] for s in states]
    losses = np.array([s.loss for s in states])
    plt.scatter(x, y, c=1/losses, s=1/losses)
    # plt.plot(x, y)
plt.colorbar()
# %%


# %%

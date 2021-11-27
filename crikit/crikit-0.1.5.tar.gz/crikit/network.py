#!/usr/bin/python3
import numpy as np
from scipy.special import expit
import sys

ACTIVATIONS = {}
ACTIVATIONS["linear"] = lambda x: x
# ACTIVATIONS['softmax'] = lambda x: np.exp(x-np.max(x, axis=1)[:, None])/np.sum(np.exp(x-np.max(x, axis=1)[:, None]), axis=1)[:, None]
ACTIVATIONS["sigmoid"] = lambda x: expit(x)
ACTIVATIONS["tanh"] = lambda x: np.tanh(x)
ACTIVATIONS["relu"] = lambda x: x * (x > 0)
ACTIVATIONS["softplus"] = lambda x: np.log(np.exp(x) + 1)

ACT_DERIVATIVES = {}
ACT_DERIVATIVES["linear"] = lambda x, z: np.ones(z.shape)
# ACT_DERIVATIVES['softmax'] = lambda x, z: z*(1-z)
ACT_DERIVATIVES["sigmoid"] = lambda x, z: z * (1 - z)
ACT_DERIVATIVES["tanh"] = lambda x, z: 1 - z * z
ACT_DERIVATIVES["relu"] = lambda x, z: 1 * (x > 0)
ACT_DERIVATIVES["softplus"] = lambda x, z: 1 / (np.exp(-x) + 1)

ERRORS = {}
ERRORS["squared_error"] = lambda y_true, y_pred: np.mean((y_true - y_pred) ** 2)


def cross_entropy(y_true, y_pred):
    y_pred = y_pred.clip(0.00001, 1 - 0.00001)
    return -np.sum(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))


def cross_entropy_der(y_true, y_pred):
    y_pred = y_pred.clip(0.00001, 1 - 0.00001)
    return -y_true / y_pred + (1 - y_true) / (1 - y_pred)


ERRORS["cross_entropy"] = cross_entropy

ERR_DERIVATIVES = {}
ERR_DERIVATIVES["squared_error"] = lambda y_true, y_pred: -(y_true - y_pred) / len(
    y_true.flatten()
)
ERR_DERIVATIVES["cross_entropy"] = cross_entropy_der


class Layer(object):
    def __init__(self, num_outputs, input_shape, activation="sigmoid", weights=None):
        self.input_shape = input_shape
        self.num_outputs = num_outputs
        self.activation = activation

        self.output = np.zeros((self.num_outputs))
        if len(input_shape) > 1:
            print(
                "Layer() error: input_shape must be one-dimensional for this layer type"
            )
            sys.exit(1)

        if weights is None:
            # Generate weights between -0.3 and 0.3
            weights = np.random.random_sample(
                (self.input_shape[0] + 1, self.num_outputs)
            )
            weights = weights * 0.6 - 0.3
        self.weights = weights
        self.deltaw = np.zeros_like(self.weights)

    def create_copy(self, weights=None):
        if weights is None:
            weights = self.weights.copy()
        elif isinstance(weights, str) and weights == "random":
            weights = None
        else:
            weights = weights.copy()
            assert weights.shape == self.weights.shape

        return Layer(self.num_outputs, self.input_shape, self.activation, weights)

    def forward_pass(self, data):
        self.input = np.append(data, np.ones(data.shape[0])[:, None], axis=1)
        self.act = np.dot(self.input, self.weights)
        self.output = ACTIVATIONS[self.activation](self.act)

    def compute_jacobian(self):
        # I removed the bottom row from the weights, because they correspond to the bias terms.
        act_der = ACT_DERIVATIVES[self.activation](self.act, self.output)
        my_jacobian = act_der[:, :, None] * np.transpose(self.weights[:-1, :])
        return my_jacobian

    def backward_pass(self, next_layer, err_der=None):
        if err_der is None:
            err_der = np.dot(next_layer.err, np.transpose(next_layer.weights))[:, :-1]
        act_der = ACT_DERIVATIVES[self.activation](self.act, self.output)
        self.err = err_der * act_der
        self.weight_gradient = np.dot(self.input.transpose(), self.err)

    def update_weights(self, learning_rate, momentum):
        self.deltaw = momentum * self.deltaw - learning_rate * self.weight_gradient
        self.weights += self.deltaw


class Network(object):
    def __init__(self, layers=None, filename=None):
        self.error = "squared_error"
        if filename is None:
            self.layers = layers
        else:
            self.load(filename)
        if len(self.layers) == 0:
            print("Network() error: len(layers) must be > 0")
            sys.exit(1)
        self.num_inputs = self.layers[0].input_shape[0]
        self.num_outputs = self.layers[-1].num_outputs

    @staticmethod
    def create_layers(
        num_inputs,
        num_outputs,
        output_activation,
        layer_sizes,
        layer_activation,
        seed=None,
    ):
        layers = []
        prev_output_shape = (num_inputs,)
        np.random.seed(seed)
        for n in layer_sizes:
            l = Layer(
                num_outputs=n,
                input_shape=prev_output_shape,
                activation=layer_activation,
            )
            layers.append(l)
            prev_output_shape = (l.num_outputs,)
        layers.append(
            Layer(
                num_outputs=num_outputs,
                input_shape=prev_output_shape,
                activation=output_activation,
            )
        )
        return layers

    def create_copy(self, weights=None):
        layers = []
        if weights == "random":
            for l in self.layers:
                l = l.create_copy(weights=weights)
                layers.append(l)
            return Network(layers)

        if weights is None:
            weights = self.get_weights(copy=False)

        assert len(weights) == len(self.layers)
        for l, w in zip(self.layers, weights):
            l = l.create_copy(weights=w)
            layers.append(l)
        return Network(layers)

    def get_weights(self, copy=True):
        weights = []
        for l in self.layers:
            weights.append(l.weights if not copy else l.weights.copy())
        return weights

    def set_weights(self, weights):
        assert len(weights) == len(self.layers)
        for l, w in zip(self.layers, weights):
            l.weights = w

    def train(self, x, y, learning_rate=0.001, momentum=0, debug=False):
        # Forward pass
        self.predict(x, debug=debug)

        # Backward Pass
        self.derivative_calculations(
            ERR_DERIVATIVES[self.error](y, self.layers[-1].output), debug=debug
        )

        # Update weights
        self.update_weights(learning_rate=learning_rate, momentum=momentum, debug=debug)

        return self.layers[-1].output, ERRORS[self.error](y, self.layers[-1].output)

    def derivative_calculations(self, err_der, debug=False):
        if debug:
            print("Backward Pass (err)")

        l = self.layers[-1]
        l.backward_pass(None, err_der)
        if debug:
            print("Layer %d: %s" % (len(self.layers) - 1, l.err.shape))
        for i in range(len(self.layers) - 2, -1, -1):
            l = self.layers[i]
            l.backward_pass(self.layers[i + 1])
            if debug:
                print("Layer %d: %s" % (i, l.err.shape))

        l = self.layers[0]
        self.input_err = np.dot(l.err, np.transpose(l.weights))[:, :-1]
        self.param_err = []
        for l in self.layers:
            self.param_err.append(l.weight_gradient)

        if debug:
            print("Input: %s" % (self.input_err.shape,))
            print()

    def update_weights(self, learning_rate=0.001, momentum=0, debug=False):
        if debug:
            print("Updating weights (deltaw)")
        for l in self.layers:
            l.update_weights(learning_rate=learning_rate, momentum=momentum)
        if debug:
            print("Successfully updated weights. Quitting now...")
            sys.exit(1)

    def predict(self, x, debug=False):
        self.layers[0].forward_pass(x)
        if debug:
            print("Forward Pass (input -> output)")
            print(
                "Layer %d: %s -> %s"
                % (0, self.layers[0].input.shape, self.layers[0].output.shape)
            )
        for i in range(1, len(self.layers)):
            l = self.layers[i]
            l.forward_pass(self.layers[i - 1].output)
            if debug:
                print("Layer %d: %s -> %s" % (i, l.input.shape, l.output.shape))
        if debug:
            print()
        return self.layers[-1].output

    def jacobian_calculations(self):
        jac = self.layers[0].compute_jacobian()
        for i in range(1, len(self.layers)):
            l = self.layers[i]
            ljac = l.compute_jacobian()
            jac = np.matmul(ljac, jac)
        self.jacobian = jac
        self.p_jacobian = None

    def summary(self):
        s = "============================\n"
        s += "    Network Summary\n\n"
        s += "(input_size) -> output_size\n\n"
        for i, l in enumerate(self.layers):
            s += "Layer %d: %s -> %s\n" % (i, l.input_shape, l.num_outputs)
        s += "===========================\n"
        return s

    def save(self, filename):
        import pickle

        with open(filename, "wb") as outputFile:
            pickle.dump(self.layers, outputFile, pickle.HIGHEST_PROTOCOL)

    def load(self, filename):
        import pickle

        with open(filename, "rb") as inputFile:
            self.layers = pickle.load(inputFile)


class PlapNetwork(object):
    def __init__(self, p=2, dims=2, input_just_vector=False, output_vector=False):
        self.p = p
        self.dims = dims
        self.deltap = 0
        self.output_vector = output_vector
        self.input_just_vector = input_just_vector
        self.num_inputs = self.dims if self.input_just_vector else 1 + self.dims
        self.num_outputs = self.dims if self.output_vector else 1

    @staticmethod
    def create_layers(
        num_inputs, num_outputs, output_activation, layer_sizes, layer_activation, seed
    ):
        raise NotImplementedError("PlapNetwork doesn't have this functionality")

    def train(self, x, y, learning_rate=0.001, momentum=0, debug=False):
        # Forward pass
        self.predict(x, debug=debug)

        # Backward Pass
        self.derivative_calculations(
            ERR_DERIVATIVES[self.error](y, l.output), debug=debug
        )

        # Update weights
        self.update_weights(debug=debug, learning_rate=learning_rate, momentum=momentum)

        return self.output, ERRORS[self.error](y, self.output)

    def create_copy(self, p=None, plap_network=None):
        layers = []

        if plap_network is not None:
            if p is not None:
                raise ValueError("It's invalid to define both p and plap_network")

            return PlapNetwork(
                obj.p,
                dims=plap_network.dims,
                input_just_vector=plap_network.input_just_vector,
                output_vector=plap_network.output_vector,
            )

        if p == "random":
            return PlapNetwork(
                2 + np.random.rand(),
                dims=self.dims,
                input_just_vector=self.input_just_vector,
                output_vector=self.output_vector,
            )

        if p is None:
            p = self.p
        return PlapNetwork(
            p=p,
            dims=self.dims,
            input_just_vector=self.input_just_vector,
            output_vector=self.output_vector,
        )

    def derivative_calculations(self, err_der, debug=False):
        self.jacobian_calculations()
        self.err_der = err_der
        if self.output_vector:
            self.input_err = np.matmul(self.err_der[:, None, :], self.jacobian)
        else:
            self.input_err = self.err_der * self.jacobian[:, 0, :]

        axes = np.arange(len(self.err_der.shape))
        self.param_err = np.tensordot(self.err_der, self.p_jacobian, (axes, axes))[0]
        if self.param_err.size == 1:
            self.param_err = self.param_err.flat[0]

        if not self.input_just_vector:
            # Add a column of zeros to input_err to take the place of the function value, which has a gradient of 0.
            zeros = np.zeros((self.input_err.shape[0], self.input_err.shape[1] + 1))
            zeros[:, 1:] = self.input_err
            self.input_err = zeros

    def update_weights(self, learning_rate=0.001, momentum=0, debug=False):
        self.deltap = momentum * self.deltap - learning_rate * np.dot(
            self.err_der.transpose(), self.p_jacobian
        )
        self.p += self.deltap

    def predict(self, x, debug=False):

        if self.input_just_vector:
            self.input = x[:, :]
        else:
            # The first column of x is the function value, and the other columns are the gradient.
            self.input = x[:, 1:]

        self.activation = np.sum(self.input * self.input, axis=1) + 1e-12
        self.activation = self.activation[:, None]

        self.output = self.activation ** ((self.p - 2) / 2)

        if self.output_vector:
            # Multiply the output magnitudes by gradu.
            self.output = self.output * self.input
        return self.output

    def jacobian_calculations(self):
        a = self.activation
        g = self.input
        q = self.p - 2

        if self.output_vector:

            self.jacobian = np.matmul(
                (q * (a ** (q / 2 - 1)) * g)[:, :, None], g[:, None, :]
            )

            # Then add to diagonal
            diag = np.arange(self.dims)
            self.jacobian[:, diag, diag] += a ** (q / 2)

            if not self.input_just_vector:
                # Add a column of zeros at the beginning to represent the function value, which has a gradient of 0.
                jac = np.zeros((self.jacobian.shape[0], self.jacobian.shape[1] + 1))
                jac[:, 1:] = self.jacobian
                self.jacobian = jac

        else:
            self.jacobian = a ** (q / 2 - 1) * q * g
            self.jacobian = self.jacobian[:, None, :]

        # self.p_jacobian = self.output*np.log(self.activation)[:, None]
        self.p_jacobian = self.output * 0.5 * np.log(a)
        self.p_jacobian = np.expand_dims(self.p_jacobian, axis=-1)

    def summary(self):
        s = "============================\n"
        s += "    PlapNetwork Summary\n\n"
        s += "        p = %g\n" % self.p
        s += "     dims = %d\n" % self.dims
        s += "===========================\n"
        return s

    def save(self, filename):
        raise NotImplementedError("PlapNetwork doesn't have this functionality")

    def load(self, filename):
        raise NotImplementedError("PlapNetwork doesn't have this functionality")

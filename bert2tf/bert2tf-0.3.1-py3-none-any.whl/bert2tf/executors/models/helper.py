import numpy as np
import tensorflow as tf


def gelu(x):
    """ Gaussian Error Linear Unit.
    Original Implementation of the gelu activation function in Google Bert repo when initially created.
        For information: OpenAI GPT's gelu is slightly different (and gives slightly different results):
        0.5 * x * (1 + torch.tanh(math.sqrt(2 / math.pi) * (x + 0.044715 * torch.pow(x, 3))))
        Also see https://arxiv.org/abs/1606.08415
    """
    cdf = 0.5 * (1.0 + tf.math.erf(x / tf.math.sqrt(2.0)))
    return x * cdf


def gelu_new(x):
    """Gaussian Error Linear Unit.
    This is a smoother version of the RELU.
    Original paper: https://arxiv.org/abs/1606.08415
    Args:
        x: float Tensor to perform activation.
    Returns:
        `x` with the GELU activation applied.
    """
    cdf = 0.5 * (1.0 + tf.tanh((np.sqrt(2 / np.pi) * (x + 0.044715 * tf.pow(x, 3)))))
    return x * cdf


def swish(x):
    return x * tf.sigmoid(x)


ACT2FN = {
    'gelu': tf.keras.activations.gelu,
    'relu': tf.keras.activations.relu,
    'swish': tf.keras.activations.swish,
    'gelu_new': tf.keras.layers.Activation(gelu_new),
}


def get_initializer(initializer_range=0.02):
    """Creates a `tf.initializers.truncated_normal` with the given range.
    Args:
        initializer_range: float, initializer range for stddev.
    Returns:
        TruncatedNormal initializer with stddev = `initializer_range`.
    """
    return tf.keras.initializers.TruncatedNormal(stddev=initializer_range)


def shape_list(x):
    """Deal with dynamic shape in tensorflow cleanly."""
    static = x.shape.as_list()
    dynamic = tf.shape(x)
    return [dynamic[i] if s is None else s for i, s in enumerate(static)]


def get_weights_dict_from_h5(file_path):
    """Get weights from h5 file
    it will return a dict, key is weight's name, value is weight's value
    """
    import h5py
    from tensorflow.python.keras.saving.hdf5_format import load_attributes_from_hdf5_group
    import numpy as np
    with h5py.File(file_path) as f:
        weights_dict = {}
        for name, group in f.items():
            weight_names = load_attributes_from_hdf5_group(group, 'weight_names')
            weights = {weight_name[:-2]: np.asarray(group[weight_name]) for weight_name in weight_names}
            if weights is not None:
                weights_dict.update(weights)

        return weights_dict

# def load_weights(model, resolved_archive_file: str, _prefix: str = None):
#     # Read the H5 file
#     with h5py.File(resolved_archive_file, "r") as f:
#         # Retrieve the name of each layer from the H5 file
#         saved_h5_model_layers_name = set(hdf5_format.load_attributes_from_hdf5_group(f, "layer_names"))
#
#         # Find the missing layers from the high level list of layers
#         missing_layers = list(set([layer.name for layer in model.layers]) - saved_h5_model_layers_name)
#
#         # Find the unexpected layers from the high level list of layers
#         unexpected_layers = list(saved_h5_model_layers_name - set([layer.name for layer in model.layers]))
#         saved_weight_names_set = set()
#         symbolic_weights_names = set()
#         weight_value_tuples = []
#
#         # Compute missing and unexpected sub layers
#         # Store the weights in list of tuples that looks like [(weight_object, value_of_weight),...]
#         for layer in model.layers:
#             # if layer_name from the H5 file belongs to the layers from the instantiated model
#             if layer.name in saved_h5_model_layers_name:
#                 # Get the H5 layer object from its name
#                 h5_layer_object = f[layer.name]
#                 # Get all the weights as a list from the layer object
#                 symbolic_weights = layer.trainable_weights + layer.non_trainable_weights
#                 saved_weights = {}
#
#                 # Create a dict from the H5 saved model that looks like {"weight_name": weight_value}
#                 # And a set with only the names
#                 for weight_name in hdf5_format.load_attributes_from_hdf5_group(h5_layer_object, "weight_names"):
#                     # TF names always start with the model name so we ignore it
#                     name = "/".join(weight_name.split("/")[1:])
#
#                     if _prefix is not None:
#                         name = _prefix + "/" + name
#
#                     saved_weights[name] = np.asarray(h5_layer_object[weight_name])
#
#                     # Add the updated name to the final list for computing missing/unexpected values
#                     saved_weight_names_set.add(name)
#
#                 # Loop over each weights from the instantiated model and compare with the weights from the H5 file
#                 for symbolic_weight in symbolic_weights:
#                     # TF names always start with the model name so we ignore it
#                     if _prefix is not None:
#                         delimeter = len(_prefix.split("/"))
#                         symbolic_weight_name = "/".join(
#                             symbolic_weight.name.split("/")[:delimeter]
#                             + symbolic_weight.name.split("/")[delimeter + 1:]
#                         )
#                     else:
#                         symbolic_weight_name = "/".join(symbolic_weight.name.split("/")[1:])
#
#                     # here we check if the current weight is among the weights from the H5 file
#                     # If yes, get the weight_value of the corresponding weight from the H5 file
#                     # If not, make the value to None
#                     saved_weight_value = saved_weights.get(symbolic_weight_name, None)
#
#                     # Add the updated name to the final list for computing missing/unexpected values
#                     symbolic_weights_names.add(symbolic_weight_name)
#
#                     # If the current weight is found
#                     if saved_weight_value is not None:
#                         # Check if the shape of the current weight and the one from the H5 file are different
#                         if K.int_shape(symbolic_weight) != saved_weight_value.shape:
#                             # If yes we reshape the weight from the H5 file accordingly to the current weight
#                             # If the two shapes are not compatible we raise an issue
#                             try:
#                                 array = np.reshape(saved_weight_value, K.int_shape(symbolic_weight))
#                             except AssertionError as e:
#                                 e.args += (K.int_shape(symbolic_weight), saved_weight_value.shape)
#                                 raise e
#                         else:
#                             array = saved_weight_value
#
#                         # We create the tuple that will be loaded and add it to the final list
#                         weight_value_tuples.append((symbolic_weight, array))
#
#     # Load all the weights
#     K.batch_set_value(weight_value_tuples)
#
#     # Compute the missing and unexpected layers
#     missing_layers.extend(list(symbolic_weights_names - saved_weight_names_set))
#     unexpected_layers.extend(list(saved_weight_names_set - symbolic_weights_names))
#
#     return missing_layers, unexpected_layers

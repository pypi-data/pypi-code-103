# coding=utf-8
import os

from tf_geometric import SparseAdj
from tf_geometric.nn import gcn_norm_adj, gcn_build_cache_for_graph
from tf_sparse import SparseMatrix

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
from tf_geometric.utils import tf_utils
import tensorflow as tf
import tf_geometric as tfg
from tqdm import tqdm
import time
import tf_sparse as tfs
import warnings
# tf.config.run_functions_eagerly(True)





def gcn(x, edge_index, edge_weight, kernel, bias=None, activation=None,
        renorm=True, improved=False, cache=None):
    """
    Functional API for Graph Convolutional Networks.

    :param x: Tensor, shape: [num_nodes, num_features], node features
    :param edge_index: Tensor, shape: [2, num_edges], edge information
    :param edge_weight: Tensor or None, shape: [num_edges]
    :param kernel: Tensor, shape: [num_features, num_output_features], weight
    :param bias: Tensor, shape: [num_output_features], bias
    :param activation: Activation function to use.
    :param renorm: Whether use renormalization trick (https://arxiv.org/pdf/1609.02907.pdf).
    :param improved: Whether use improved GCN or not.
    :param cache: A dict for caching A' for GCN. Different graph should not share the same cache dict.
        To use @tf_utils.function with gcn, you should cache the noremd edge information before the first call of the gcn.

        - (1) If you're using OOP APIs tfg.layers.GCN:

              gcn_layer.build_cache_for_graph(graph)

        - (2) If you're using functional API tfg.nn.gcn:

              from tf_geometric.nn.conv.gcn import gcn_build_cache_for_graph
              gcn_build_cache_for_graph(graph)

    :return: Updated node features (x), shape: [num_nodes, num_output_features]
    """

    num_nodes = tfs.shape(x)[0]

    sparse_adj = SparseAdj(edge_index, edge_weight, [num_nodes, num_nodes])
    normed_sparse_adj = gcn_norm_adj(sparse_adj, renorm, improved, cache)

    # SparseTensor is usually used for one-hot node features (For example, feature-less nodes.)
    if isinstance(x, tf.sparse.SparseTensor):
        h = tf.sparse.sparse_dense_matmul(x, kernel)
    else:
        h = x @ kernel

    h = normed_sparse_adj @ h

    if bias is not None:
        h += bias

    if activation is not None:
        h = activation(h)

    return h



class GCN(tf.keras.Model):
    """
    Graph Convolutional Layer
    """

    def build(self, input_shapes):
        x_shape = input_shapes[0]
        num_features = x_shape[-1]

        self.kernel = self.add_weight("kernel", shape=[num_features, self.units],
                                      initializer="glorot_uniform", regularizer=self.kernel_regularizer)
        if self.use_bias:
            self.bias = self.add_weight("bias", shape=[self.units],
                                        initializer="zeros", regularizer=self.bias_regularizer)

    def __init__(self, units, activation=None,
                 use_bias=True,
                 renorm=True, improved=False,
                 kernel_regularizer=None, bias_regularizer=None, *args, **kwargs):
        """

        :param units: Positive integer, dimensionality of the output space.
        :param activation: Activation function to use.
        :param use_bias: Boolean, whether the layer uses a bias vector.
        :param renorm: Whether use renormalization trick (https://arxiv.org/pdf/1609.02907.pdf).
        :param improved: Whether use improved GCN or not.
        :param kernel_regularizer: Regularizer function applied to the `kernel` weights matrix.
        :param bias_regularizer: Regularizer function applied to the bias vector.
        """
        super().__init__(*args, **kwargs)
        self.units = units

        self.activation = activation
        self.use_bias = use_bias

        self.kernel = None
        self.bias = None

        self.renorm = renorm
        self.improved = improved

        self.kernel_regularizer = kernel_regularizer
        self.bias_regularizer = bias_regularizer

    def build_cache_for_graph(self, graph, override=False):
        """
        Manually compute the normed edge based on this layer's GCN normalization configuration (self.renorm and self.improved) and put it in graph.cache.
        If the normed edge already exists in graph.cache and the override parameter is False, this method will do nothing.

        :param graph: tfg.Graph, the input graph.
        :param override: Whether to override existing cached normed edge.
        :return: None
        """
        gcn_build_cache_for_graph(graph, self.renorm, self.improved, override=override)

    def cache_normed_edge(self, graph, override=False):
        """
        Manually compute the normed edge based on this layer's GCN normalization configuration (self.renorm and self.improved) and put it in graph.cache.
        If the normed edge already exists in graph.cache and the override parameter is False, this method will do nothing.

        :param graph: tfg.Graph, the input graph.
        :param override: Whether to override existing cached normed edge.
        :return: None

        .. deprecated:: 0.0.56
            Use ``build_cache_for_graph`` instead.
        """
        warnings.warn("'GCN.cache_normed_edge(graph, override)' is deprecated, use 'GCN.build_cache_for_graph(graph, override)' instead", DeprecationWarning)
        return self.build_cache_for_graph(graph, override=override)

    def call(self, inputs, cache=None, training=None, mask=None):
        """

        :param inputs: List of graph info: [x, edge_index, edge_weight]
        :param cache: A dict for caching A' for GCN. Different graph should not share the same cache dict.
        :return: Updated node features (x), shape: [num_nodes, units]
        """

        if len(inputs) == 3:
            x, edge_index, edge_weight = inputs
        else:
            x, edge_index = inputs
            edge_weight = None

        return gcn(x, edge_index, edge_weight, self.kernel, self.bias,
                   activation=self.activation, renorm=self.renorm, improved=self.improved, cache=cache)















dataset = "ogbn-arxiv"
graph, (train_index, valid_index, test_index) = tfg.datasets.OGBNodePropPredDataset(dataset).load_data()
# graph: tfg.Graph

num_classes = graph.y.max() + 1
# graph.convert_data_to_tensor()

drop_rate = 0.5
learning_rate = 1e-2


# Multi-layer GCN Model
class GCNModel(tf.keras.Model):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gcn0 = GCN(256, activation=tf.nn.relu)
        self.gcn1 = GCN(256, activation=tf.nn.relu)
        self.gcn2 = GCN(num_classes)
        self.dropout = tf.keras.layers.Dropout(drop_rate)

    def call(self, inputs, training=None, mask=None, cache=None):
        # start = tf.timestamp()

        x, edge_index, edge_weight = inputs
        # h = self.dropout(x, training=training)
        h = self.gcn0([x, edge_index, edge_weight], cache=cache)
        h = self.dropout(h, training=training)

        h = self.gcn1([h, edge_index, edge_weight], cache=cache)
        h = self.dropout(h, training=training)
        h = self.gcn2([h, edge_index, edge_weight], cache=cache)

        # tf.print("forward time: ", tf.timestamp() - start)

        return h

# Multi-layer GCN Model
# class GCNModel1(tf.keras.Model):
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.gcn0 = tfg.layers.GCN(256, activation=tf.nn.relu)
#         self.gcn1 = tf.keras.layers.Dense(256, activation=tf.nn.relu)
#         self.gcn2 = tf.keras.layers.Dense(num_classes)
#         self.dropout = tf.keras.layers.Dropout(drop_rate)
#
#     def call(self, inputs, training=None, mask=None, cache=None):
#         start = tf.timestamp()
#
#         x, edge_index, edge_weight = inputs
#
#         h = self.gcn1(x, training=training)
#
#         adj: SparseAdj = cache["gcn_normed_adj_True_False"]
#         h = adj @ h
#
#         h = self.gcn2(h, training=training)
#
#
#
#         tf.print("forward time: ", tf.timestamp() - start)
#
#         return h

model = GCNModel()


# @tf_utils.function can speed up functions for TensorFlow 2.x.
# @tf_utils.function is not compatible with TensorFlow 1.x and dynamic graph.cache.
# @tf_utils.function
def forward(graph, training=False):
    return model([graph.x, graph.edge_index, graph.edge_weight], training=training, cache=graph.cache)




# The following line is only necessary for using GCN with @tf_utils.function
# For usage without @tf_utils.function, you can commont the following line and GCN layers can automatically manager the cache
model.gcn0.build_cache_for_graph(graph)



# edge_index, edge_weight, shape = graph.cache[list(graph.cache.keys())[0]]
# print(edge_index.shape)
# adsfafsd

# print(tf.constant(adj))
# asdfasdf

# adj.index = adj.edge_index.numpy()
# adj.value = adj.edge_weight.numpy()

# adj.index = tf.constant(adj.edge_index)
# adj.value = tf.constant(adj.edge_weight)



# @tf_utils.function
def compute_loss(logits, mask_index, vars):
    # start = tf.timestamp()

    masked_logits = tf.gather(logits, mask_index)
    masked_labels = tf.gather(graph.y, mask_index)
    # losses = tf.nn.softmax_cross_entropy_with_logits(
    #     logits=masked_logits,
    #     labels=tf.one_hot(masked_labels, depth=num_classes)
    # )

    losses = tf.nn.sparse_softmax_cross_entropy_with_logits(
        logits=masked_logits,
        labels=masked_labels
    )



    kernel_vars = [var for var in vars if "kernel" in var.name]
    l2_losses = [tf.nn.l2_loss(kernel_var) for kernel_var in kernel_vars]

    loss = tf.reduce_mean(losses) + tf.add_n(l2_losses) * 1e-4

    # tf.print("loss time: ", tf.timestamp() - start)

    return loss


optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)


@tf_utils.function
# @tf_utils.function(experimental_compile=True)
def train_step():

    print("retracing ......")

    # logits = forward(graph, training=True)
    # loss = logits[0][0]#compute_loss(logits, train_index, model.trainable_variables)




    with tf.GradientTape() as tape:
        logits = forward(graph, training=True)
        loss = compute_loss(logits, train_index, tape.watched_variables())

    vars = tape.watched_variables()
    grads = tape.gradient(loss, vars)
    optimizer.apply_gradients(zip(grads, vars))


    return loss


# func = train_step.get_concrete_function()
# graph = func.graph
# for node in graph.as_graph_def().node:
#   print(f'{node.input} -> {node.name}')
#
#
# print("========")

@tf_utils.function
# @tf_utils.function(experimental_compile=True)
def evaluate():
    logits = forward(graph)
    masked_logits = tf.gather(logits, test_index)
    masked_labels = tf.gather(graph.y, test_index)

    y_pred = tf.argmax(masked_logits, axis=-1, output_type=tf.int32)

    corrects = tf.equal(y_pred, masked_labels)
    accuracy = tf.reduce_mean(tf.cast(corrects, tf.float32))
    return accuracy


loss = train_step()

# train_step_ = train_step.get_concrete_function()
# graph = train_step_.graph
# # for node in graph.as_graph_def().node:
# #   print(f'{node.input} -> {node.name}')
# #
# # print("======")
# # print(graph.as_graph_def())
#
# with open("numpy.txt", "w", encoding="utf-8") as f:
#     f.write(str(graph.as_graph_def()))
# exit(0)

accuracy = evaluate()

start_time = time.time()

print(train_step.pretty_printed_concrete_signatures())

for step in range(1, 20001):
    loss = train_step()
    if step % 20 == 0:
        accuracy = evaluate()
        # accuracy = 0.0
        print("step = {}\tloss = {}\taccuracy = {}\tavg_time = {}".format(step, loss, accuracy, (time.time() - start_time) / step))




print("\nstart speed test...")
num_test_iterations = 1000
start_time = time.time()
for _ in tqdm(range(num_test_iterations)):
    logits = forward(graph)
end_time = time.time()
print("mean forward time: {} seconds".format((end_time - start_time) / num_test_iterations))

if tf.__version__[0] == "1":
    print("** @tf_utils.function is disabled in TensorFlow 1.x. "
          "Upgrade to TensorFlow 2.x for 10X faster speed. **")
import tensorflow as tf
from tensorflow.python.keras import backend as K

from .helper import get_initializer, shape_list


class BaseEmbedding(tf.keras.layers.Layer):
    """
    Base embedding layer, it is used to convinced custom
    """

    def __init__(self, vocab_size, embed_size, initializer_range=None, word_embedding_name='word_embeddings', **kwargs):
        super().__init__(**kwargs)
        self.vocab_size = vocab_size
        self.hidden_size = embed_size
        self.word_embeddings_name = word_embedding_name
        self.initializer_range = embed_size ** -0.5 if initializer_range is None else initializer_range

    def build(self, input_shape):
        # Create and initialize weights. The random normal initializer was chosen
        # arbitrarily, and works well.
        self.word_embeddings = self.add_weight(
            self.word_embeddings_name,
            shape=[self.vocab_size, self.hidden_size],
            initializer=get_initializer(self.initializer_range)
        )

        super().build(input_shape)

    def get_config(self):
        config = {
            'vocab_size': self.vocab_size,
            'hidden_size': self.hidden_size,
            'initializer_range': self.initializer_range,
        }
        base_config = super().get_config()

        return dict(list(base_config.items()) + list(config.items()))

    def call(self, inputs, mode='embedding', **kwargs):
        embeds = getattr(self, mode, None)(inputs)

        return embeds

    def embedding(self, inputs):
        """
        Word embedding
        """
        input_ids = inputs

        dtype = K.dtype(input_ids)
        if dtype != 'int32' and dtype != 'int64':
            input_ids = tf.cast(input_ids, 'int32')
        word_embeddings = tf.gather(self.word_embeddings, input_ids)

        return word_embeddings

    def linear(self, inputs):
        """
        Map to hidden state to vocab
        """
        batch_size = shape_list(inputs)[0]
        length = shape_list(inputs)[1]

        x = tf.reshape(inputs, [-1, self.hidden_size])
        logits = tf.matmul(x, self.word_embeddings, transpose_b=True)

        return tf.reshape(logits, [batch_size, length, self.vocab_size])


class RelativePositionEmbedding(tf.keras.layers.Layer):
    """Relative position embedding for self attention"""

    def __init__(self, max_position_embeddings, embed_size, initializer_range=None, **kwargs):
        super().__init__(**kwargs)

        self.max_position_embeddings = max_position_embeddings
        self.embed_size = embed_size
        self.initializer_range = initializer_range

        # self.ln = tf.keras.layers.LayerNormalization(name='LayerNorm')
        self.dense = tf.keras.layers.Dense(embed_size, kernel_initializer=get_initializer(initializer_range),
                                           use_bias=False)

    def build(self, input_shape):
        self.position_embeddings = self.add_weight('position_embedding',
                                                   shape=[2 * self.max_position_embeddings - 1, self.embed_size],
                                                   initializer=get_initializer(self.initializer_range))

        super().build(input_shape)

    def call(self, inputs, **kwargs):
        query_layer = inputs
        # todo need find why it has to add ln
        # self.position_embeddings = self.ln(self.position_embeddings)
        batch_size, num_attention_heads, seq_length, size_per_head = shape_list(query_layer)

        # fetch embedding
        # assuming L = 2 * to_seq_length - 1, shape = [L, embedding_size]
        # convert 2 * max_position_embeddings - 1 -> 2 * seq_length -1
        embedding = self._gather_positional_embedding(seq_length)

        embedding = self.dense(embedding)
        # multi-head attention
        embedding = tf.reshape(embedding, [-1, num_attention_heads, size_per_head])
        # shape = [num_attention_heads, 2*seq_length - 1, size_per_head]
        embedding = tf.transpose(embedding, [1, 0, 2])

        # flatten 1,2, shape = [num_attention_heads, batch_size * seq_length, size_per_head]
        query = tf.reshape(query_layer, [num_attention_heads, -1, size_per_head])
        # calculate attention score, shape = [num_attention_heads, batch_size * seq_length, 2*seq_length - 1]
        attention_score = tf.matmul(query, embedding, transpose_b=True)

        # create index for fetching relative position
        rel_index = tf.range(start=seq_length - 1, limit=2 * seq_length - 1)
        rel_index = tf.expand_dims(rel_index, axis=0)
        # [seq_length * seq_length]
        rel_index = tf.tile(rel_index, [seq_length, 1])

        # offset
        row_index = tf.range(start=0, limit=seq_length)
        row_index = tf.expand_dims(row_index, axis=-1)

        rel_index = rel_index - row_index

        row_offset = row_index * (2 * seq_length - 1)

        rel_index += row_offset
        rel_index = tf.reshape(rel_index, [-1])

        # fetch score
        # shape = [num_attention_heads, batch_size, seq_length * (2 * seq_length - 1)]
        attention_score = tf.reshape(attention_score, [num_attention_heads, batch_size, -1])

        # gather, shape = [num_attention_heads, batch_size, seq_length * seq_length]
        attention_score = tf.gather(params=attention_score, indices=rel_index, axis=2)

        return tf.reshape(attention_score, [batch_size, num_attention_heads, seq_length, seq_length])

    def _gather_positional_embedding(self, seq_length):
        embedding_index = tf.range(
            start=self.max_position_embeddings - seq_length,
            limit=self.max_position_embeddings + seq_length - 1)

        # negative part
        negative_mask = tf.sign(tf.sign(embedding_index) + 1)

        # reset all negative index to ZERO
        embedding_index = embedding_index * negative_mask

        # upper bound part
        max_id = 2 * self.max_position_embeddings - 2
        positive_mask = tf.sign(tf.sign(max_id - embedding_index) + 1)

        # reset upper bound part to ZERO
        embedding_index = embedding_index * positive_mask

        # set ZERO to max_id
        positive_mask_id = (1 - positive_mask) * max_id
        embedding_index += positive_mask_id

        # cast
        embedding_index = tf.cast(embedding_index, tf.int32)

        return tf.gather(params=self.position_embeddings, indices=embedding_index, axis=0)

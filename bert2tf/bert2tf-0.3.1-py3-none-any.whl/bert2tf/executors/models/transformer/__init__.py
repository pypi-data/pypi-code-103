from typing import List, Tuple

import tensorflow as tf

from .. import BaseModel
from ..embedding import BaseEmbedding
from ..helper import get_initializer, ACT2FN, shape_list


class Transformer(BaseModel):
    """
    Transformer models
    """

    def __init__(self, seq_len, vocab_size, hidden_size, intermediate_size, num_attention_heads, initializer_range,
                 hidden_dropout_prob, attention_probs_dropout_prob, max_position_embeddings, hidden_act,
                 num_encoder_layers=1, num_decoder_layers=1, **kwargs):
        super().__init__(**kwargs)

        self.seq_len = seq_len

        self.embedding = TransformerEmbedding(hidden_size, hidden_dropout_prob,
                                              max_position_embeddings=max_position_embeddings, vocab_size=vocab_size,
                                              initializer_range=initializer_range, name='embedding')
        self.encoder = TransformerEncoder(hidden_size, num_attention_heads, num_encoder_layers,
                                          attention_probs_dropout_prob, initializer_range, hidden_dropout_prob,
                                          hidden_act, intermediate_size)

        self.decoder = TransformerDecoder(hidden_size, initializer_range, hidden_dropout_prob, num_attention_heads,
                                          attention_probs_dropout_prob, num_layers=num_decoder_layers,
                                          embedding=self.embedding, hidden_act=hidden_act)

    def get_dummy_inputs(self):
        encoder_input_ids = tf.keras.Input(shape=(self.seq_len,), name='encoder_input_ids')
        decoder_input_ids = tf.keras.Input(shape=(None,), name='decoder_input_ids')

        return [encoder_input_ids, decoder_input_ids]

    def call(self, inputs, decoder_input_ids=None, encoder_position_ids=None, decoder_position_ids=None,
             encoder_attention_mask=None, **kwargs):
        if isinstance(inputs, (List, Tuple)):
            encoder_input_ids = inputs[0]
            decoder_input_ids = inputs[1] if len(inputs) > 1 else decoder_input_ids
            encoder_position_ids = inputs[2] if len(inputs) > 2 else encoder_position_ids
            decoder_position_ids = inputs[3] if len(inputs) > 3 else decoder_position_ids
            encoder_attention_mask = inputs[4] if len(inputs) > 4 else encoder_attention_mask

        else:
            raise ValueError(f'{inputs} is not support type')

        encoder_embeddings = self.embedding([encoder_input_ids, encoder_position_ids])
        decoder_embeddings = self.embedding([decoder_input_ids, decoder_position_ids])
        encoder_outputs = self.encoder(encoder_embeddings, encoder_attention_mask)
        decoder_outputs = self.decoder(decoder_embeddings, encoder_outputs, encoder_attention_mask)

        model_outputs = self.embedding(decoder_outputs, mode='linear')

        return model_outputs


class TransformerEmbedding(BaseEmbedding):
    """Transformer Embedding"""

    def __init__(self, embed_size, hidden_dropout_prob, max_position_embeddings=None, **kwargs):
        super().__init__(embed_size=embed_size, **kwargs)

        if max_position_embeddings:
            self.position_embeddings = tf.keras.layers.Embedding(
                max_position_embeddings,
                embed_size,
                embeddings_initializer=get_initializer(self.initializer_range),
                name='position_embeddings'
            )

        self.ln = tf.keras.layers.LayerNormalization(name='LayerNorm', epsilon=1e-12)
        self.dropout = tf.keras.layers.Dropout(hidden_dropout_prob)

    def call(self, inputs, mode='embedding', do_ln=True, training=False, **kwargs):
        embeds = super().call(inputs, mode=mode, **kwargs)

        if mode == 'embedding' and do_ln:
            embeds = self.ln(embeds)

        embeds = self.dropout(embeds, training)
        return embeds

    def embedding(self, inputs):
        input_ids, position_ids = inputs
        input_shape = shape_list(input_ids)
        seq_length = input_shape[1]

        word_embeddings = super().embedding(input_ids)

        if hasattr(self, 'position_embeddings'):
            if position_ids is None:
                position_ids = tf.range(seq_length, dtype=tf.int32)[tf.newaxis, :]

            position_embeddings = self.position_embeddings(position_ids)
            embeddings = word_embeddings + position_embeddings
        else:
            embeddings = word_embeddings

        return embeddings


class TransformerEncoder(tf.keras.layers.Layer):
    """
    Transformer Encoder
    """

    def __init__(self, hidden_size, num_attention_heads, num_hidden_layers, attention_probs_dropout_prob,
                 initializer_range, hidden_dropout_prob, hidden_act, intermediate_size, **kwargs):
        super(TransformerEncoder, self).__init__(**kwargs)
        self.layers = [
            TransformerEncoderLayer(hidden_size, num_attention_heads, attention_probs_dropout_prob, initializer_range,
                                    hidden_dropout_prob, hidden_act, intermediate_size, name=f'layer_{i}')
            for i in range(num_hidden_layers)]

    def call(self, hidden_states, attention_mask=None, **kwargs):
        all_hidden_states = ()

        for layer in self.layers:
            hidden_states = layer(hidden_states=hidden_states, attention_mask=attention_mask)
            all_hidden_states = all_hidden_states + (hidden_states,)

        return all_hidden_states


class TransformerEncoderLayer(tf.keras.layers.Layer):
    """
    Transformer layer
    """

    def __init__(self, hidden_size, num_attention_heads, attention_probs_dropout_prob, initializer_range,
                 hidden_dropout_prob, hidden_act, intermediate_size, **kwargs):
        super().__init__(**kwargs)
        self.attention = TransformerAttention(hidden_size, num_attention_heads, attention_probs_dropout_prob,
                                              hidden_dropout_prob, initializer_range, name='attention')
        self.intermediate = TransformerIntermediate(intermediate_size, initializer_range, hidden_act,
                                                    name='intermediate')
        self.self_output = TransformerOutput(hidden_size, initializer_range, hidden_dropout_prob, name='output')

    def call(self, hidden_states, key=None, value=None, attention_mask=None, **kwargs):
        attention_output = self.attention(hidden_states, key, value, attention_mask=attention_mask)
        intermediate_output = self.intermediate(attention_output)
        layer_output = self.self_output(intermediate_output, attention_output)
        return layer_output


class TransformerDecoderLayer(TransformerEncoderLayer):
    """
    Transformer Decoder Layer
    """

    def __init__(self, hidden_size, num_attention_heads, attention_probs_dropout_prob, initializer_range,
                 hidden_dropout_prob, hidden_act, intermediate_size, **kwargs):
        super(TransformerDecoderLayer, self).__init__(hidden_size, num_attention_heads, attention_probs_dropout_prob,
                                                      initializer_range, hidden_dropout_prob, hidden_act,
                                                      intermediate_size, **kwargs)

        self.masked_attention = TransformerAttention(hidden_size, num_attention_heads, attention_probs_dropout_prob,
                                                     hidden_dropout_prob, initializer_range, masked=True)

    def call(self, hidden_states, encoder_hidden_states=None, encoder_attention_mask=None, decoder_attention_mask=None,
             **kwargs):
        masked_attention_output = self.masked_attention(hidden_states,
                                                        attention_mask=decoder_attention_mask)

        layer_output = super(TransformerDecoderLayer, self).call(hidden_states=masked_attention_output,
                                                                 key=encoder_hidden_states,
                                                                 value=encoder_hidden_states,
                                                                 attention_mask=encoder_attention_mask)

        return layer_output


class TransformerDecoder(tf.keras.layers.Layer):
    """
    Transformer Decoder
    """

    def __init__(self, hidden_size, num_attention_heads, num_hidden_layers, attention_probs_dropout_prob,
                 initializer_range, hidden_dropout_prob, hidden_act, intermediate_size, **kwargs):
        super(TransformerDecoder, self).__init__(**kwargs)
        self.layers = [
            TransformerDecoderLayer(hidden_size, num_attention_heads, attention_probs_dropout_prob, initializer_range,
                                    hidden_dropout_prob, hidden_act, intermediate_size, name=f'layer_{i}')
            for i in range(num_hidden_layers)]

    def call(self, embeddings, encoder_hidden_states=None, **kwargs):
        assert encoder_hidden_states is not None

        all_hidden_states = ()

        hidden_states = embeddings
        for layer in self.layers:
            hidden_states = layer(hidden_states, encoder_hidden_states=encoder_hidden_states, **kwargs)
            all_hidden_states = all_hidden_states + (hidden_states,)

        return all_hidden_states


class TransformerAttention(tf.keras.layers.Layer):
    """
    Transformer attention
    """

    def __init__(self, hidden_size, num_attention_heads, attention_probs_dropout_prob, hidden_dropout_prob,
                 initializer_range, masked=False, **kwargs):
        super(TransformerAttention, self).__init__(**kwargs)
        if masked:
            self.self_attention = MaskedMultiHeadSelfAttention(hidden_size, num_attention_heads, initializer_range,
                                                               attention_probs_dropout_prob, name='self')
        else:
            self.self_attention = MultiHeadSelfAttention(hidden_size, num_attention_heads, initializer_range,
                                                         attention_probs_dropout_prob, name='self')

        self.dense_output = TransformerOutput(hidden_size, initializer_range, hidden_dropout_prob, name='output')

    def call(self, query, key=None, value=None, attention_mask=None, **kwargs):
        attention_outputs, _ = self.self_attention(query, key, value, attention_mask=attention_mask)
        attention_outputs = self.dense_output(attention_outputs, query)
        return attention_outputs


class TransformerIntermediate(tf.keras.layers.Layer):
    """
    Transformer intermediate layer
    """

    def __init__(self, intermediate_size, initializer_range, hidden_act, **kwargs):
        super().__init__(**kwargs)
        self.dense = tf.keras.layers.Dense(
            intermediate_size, kernel_initializer=get_initializer(initializer_range), name='dense'
        )
        if isinstance(hidden_act, str):
            self.intermediate_act_fn = ACT2FN[hidden_act]
        else:
            self.intermediate_act_fn = hidden_act

    def call(self, attention_output, **kwargs):
        hidden_states = self.dense(attention_output)
        hidden_states = self.intermediate_act_fn(hidden_states)

        return hidden_states


class TransformerOutput(tf.keras.layers.Layer):
    """
    Transformer Add&Norm layer
    """

    def __init__(self, hidden_size, initializer_range, hidden_dropout_prob, **kwargs):
        super(TransformerOutput, self).__init__(**kwargs)
        self.dense = tf.keras.layers.Dense(
            hidden_size, kernel_initializer=get_initializer(initializer_range), name='dense')
        self.dropout = tf.keras.layers.Dropout(hidden_dropout_prob)
        self.LayerNorm = tf.keras.layers.LayerNormalization(name='LayerNorm', epsilon=1e-12)

    def call(self, hidden_states, input_tensor=None, training=False, **kwargs):
        assert input_tensor is not None

        hidden_states = self.dense(hidden_states)
        hidden_states = self.dropout(hidden_states, training)
        outputs = self.LayerNorm(hidden_states + input_tensor)

        return outputs


class MultiHeadSelfAttention(tf.keras.layers.Layer):
    """Transformer Self Attention"""

    def __init__(self, hidden_size, num_attention_heads, initializer_range, attention_probs_dropout_prob, **kwargs):
        """

        :param hidden_size: hidden states size
        :param num_attention_heads: number of multi attention heads
        :param initializer_range: weights initial range
        :param attention_probs_dropout_prob: dropout rate after get attention probability
        """
        super(MultiHeadSelfAttention, self).__init__(**kwargs)
        if hidden_size % num_attention_heads != 0:
            raise ValueError(
                'The hidden size (%d) is not a multiple of the number of attention '
                'heads (%d)' % (hidden_size, num_attention_heads)
            )

        self.num_attention_heads = num_attention_heads
        self.attention_head_size = int(hidden_size / num_attention_heads)

        self.all_head_size = hidden_size
        self.initializer_range = initializer_range

        self.dropout = tf.keras.layers.Dropout(attention_probs_dropout_prob)

        self.query, self.key, self.value = self.create_denses()

    def create_denses(self):
        """create query key value linear transformation"""
        query = tf.keras.layers.Dense(
            self.all_head_size, kernel_initializer=get_initializer(self.initializer_range), name='query'
        )
        key = tf.keras.layers.Dense(
            self.all_head_size, kernel_initializer=get_initializer(self.initializer_range), name='key'
        )
        value = tf.keras.layers.Dense(
            self.all_head_size, kernel_initializer=get_initializer(self.initializer_range), name='value'
        )

        return query, key, value

    def call(self, query, key=None, value=None, attention_mask=None, training=False, **kwargs):
        if key is None:
            key = query
            value = query

        batch_size = shape_list(query)[0]
        mixed_query_layer = self.query(query) if self.query else query
        mixed_key_layer = self.key(key) if self.key else key
        value_layer = split_heads(self.value(value), self.num_attention_heads)

        attention_scores = multi_head_attention(mixed_query_layer, mixed_key_layer, self.num_attention_heads,
                                                attention_mask)

        attention_probs = tf.nn.softmax(attention_scores, axis=-1)
        # This is actually dropping out entire tokens to attend to, which might
        # seem a bit unusual, but is taken from the original Transformer paper.
        attention_probs = self.dropout(attention_probs, training)

        # [b, head, seq, seq] * [b, head, seq, head_size] = [b, head, seq, head_size]
        context_outputs = tf.matmul(attention_probs, value_layer)

        context_outputs = tf.transpose(context_outputs, perm=[0, 2, 1, 3])
        context_outputs = tf.reshape(context_outputs, (batch_size, -1, self.all_head_size))  # [b, seq, hidden_size]

        return context_outputs, attention_probs

    def expand_context_mask(self, context_mask):
        """Expand 2D tensor to 3D tensor [B, Q, hidden_size]"""
        if len(shape_list(context_mask)) == 2:
            context_mask = tf.tile(tf.expand_dims(context_mask, axis=-1), multiples=[1, 1, self.all_head_size])
        return context_mask


class MaskedMultiHeadSelfAttention(MultiHeadSelfAttention):
    """
    Transformer Masked multi head self attention
    """

    def call(self, query, key=None, value=None, attention_mask=None, **kwargs):
        q_input_shape = shape_list(query)
        batch_size = q_input_shape[0]
        q_shape = q_input_shape[1]
        k_shape = shape_list(key)[1] if key is not None else q_shape

        if q_shape != k_shape:
            raise ValueError(
                f'in masked self attention, the query shape must equal to key shape, got {q_shape} != {k_shape}')

        attention_mask = tf.expand_dims(attention_mask, axis=1)
        attention_mask = tf.tile(attention_mask, [1, q_shape, 1])

        tril_attention_mask = tf.linalg.LinearOperatorLowerTriangular(
            tf.ones([batch_size, q_shape, k_shape])).to_dense()

        attention_mask = attention_mask * tril_attention_mask  # [b, q, k]

        context_outputs, attention_probs = super().call(query=query, key=key, value=value,
                                                        attention_mask=attention_mask, **kwargs)

        return context_outputs, attention_probs


def expand_attention_mask(attention_mask, to_shape, scale=True):
    """
    Expand 2D/3D tensor to 4D tensor
    :param attention_mask: 2D/3D tensor
    :param to_shape: the target shape, which you want to expand, always like [B, H, Q, K]
    :param scale: should we scale the mask position, if True, it will set the masked position to -1e-4
    """
    if len(shape_list(attention_mask)) == 2:
        attention_mask = tf.expand_dims(attention_mask, axis=1)
        attention_mask = tf.tile(attention_mask, [1, to_shape[2], 1])  # [B, Q, K] to_shape[2] is q length

    if len(shape_list(attention_mask)) < 4:
        attention_mask = tf.expand_dims(attention_mask, axis=1)
        attention_mask = tf.tile(attention_mask, [1, to_shape[1], 1, 1])  # [B, head, Q, K]

    if scale:
        attention_mask = tf.cast(attention_mask, tf.float32)
        attention_mask = (1.0 - attention_mask) * -1e4  # scale to min

    return attention_mask


def split_heads(x: tf.Tensor, num_heads: int) -> tf.Tensor:
    batch_size, _, hidden_size = shape_list(x)
    head_size = hidden_size / num_heads
    head_size = tf.cast(head_size, tf.int32)
    x = tf.reshape(x, [batch_size, -1, num_heads, head_size])
    return tf.transpose(x, perm=[0, 2, 1, 3])


def multi_head_attention(query: tf.Tensor, key: tf.Tensor, num_heads: int, attention_mask: tf.Tensor) -> tf.Tensor:
    query_layer = split_heads(query, num_heads)
    key_layer = split_heads(key, num_heads)
    attention_scores = tf.matmul(query_layer, key_layer, transpose_b=True)
    dk = tf.cast(shape_list(key_layer)[-1], tf.float32)  # scale attention_scores
    attention_scores = tf.divide(attention_scores, tf.math.sqrt(dk))

    if attention_mask is not None:
        to_shape = shape_list(attention_scores)
        attention_mask = expand_attention_mask(attention_mask, to_shape, scale=True)
        attention_scores = attention_scores + attention_mask

    return attention_scores

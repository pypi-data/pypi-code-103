import tensorflow as tf

from ..bert import Bert, BertEmbedding, BertAttention, BertEncoder, BertLayer
from ..embedding import RelativePositionEmbedding
from ..helper import shape_list
from ..transformer import MultiHeadSelfAttention, multi_head_attention, split_heads


class PlmBert(Bert):
    """
    PLM Bert, it use relative position embedding to replace absolute position embedding
    """

    def create_embedding_layer(self, config):
        embeddings = PlmBertEmbedding(vocab_size=config.vocab_size,
                                      embed_size=config.hidden_size,
                                      initializer_range=config.initializer_range,
                                      hidden_dropout_prob=config.hidden_dropout_prob,
                                      type_vocab_size=config.type_vocab_size,
                                      name='embeddings')
        return embeddings

    def create_encoder_layer(self, config):
        encoder = PlmBertEncoder(hidden_size=config.hidden_size,
                                 num_attention_heads=config.num_attention_heads,
                                 num_hidden_layers=config.num_hidden_layers,
                                 attention_probs_dropout_prob=config.attention_probs_dropout_prob,
                                 initializer_range=config.initializer_range,
                                 hidden_dropout_prob=config.hidden_dropout_prob,
                                 hidden_act=config.hidden_act,
                                 intermediate_size=config.intermediate_size,
                                 max_position_embeddings=config.max_position_embeddings,
                                 name='encoder')

        return encoder


class PlmBertEmbedding(BertEmbedding):
    """Plm bert embedding"""

    def __init__(self, **kwargs):
        super(PlmBertEmbedding, self).__init__(max_position_embeddings=None, **kwargs)


class PlmBertEncoder(BertEncoder):
    """
    Encoder for Plm Bert
    """

    def __init__(self, max_position_embeddings, num_hidden_layers, **kwargs):
        super().__init__(num_hidden_layers=num_hidden_layers, **kwargs)

        kwargs.pop('name')
        self.layers = [PlmBertLayer(max_position_embeddings, name=f'layer_{i}', **kwargs)
                       for i in range(num_hidden_layers)]


class PlmBertLayer(BertLayer):
    """
    Plm Bert layer
    """

    def __init__(self, max_position_embeddings, **kwargs):
        super().__init__(**kwargs)

        kwargs.pop('hidden_act')
        kwargs.pop('intermediate_size')
        self.attention = PlmBertAttention(max_position_embeddings, **kwargs)


class PlmAttention(MultiHeadSelfAttention):
    """Plm bert attention, it contain self attention and relative position embedding"""

    def __init__(self, hidden_size, initializer_range, max_position_embeddings, **kwargs):
        super().__init__(hidden_size=hidden_size, initializer_range=initializer_range, **kwargs)

        self.relative_position = RelativePositionEmbedding(max_position_embeddings, hidden_size, initializer_range)

    def call(self, query, key=None, value=None, attention_mask=None, **kwargs):
        key = query if not key else key
        value = query if not value else value

        batch_size = shape_list(query)[0]
        mixed_query_layer = self.query(query) if self.query else query
        mixed_key_layer = self.key(key) if self.key else key
        value_layer = split_heads(self.value(value) if self.value else value, self.num_attention_heads)

        attention_scores = multi_head_attention(mixed_query_layer, mixed_key_layer, self.num_attention_heads,
                                                attention_mask)
        rel_pos_attention_scores = self.relative_position(split_heads(mixed_query_layer, self.num_attention_heads))

        attention_scores = attention_scores + rel_pos_attention_scores
        attention_probs = tf.nn.softmax(attention_scores, axis=-1)

        # [b, head, seq, seq] * [b, head, seq, head_size] = [b, head, seq, head_size]
        context_outputs = tf.matmul(attention_probs, value_layer)

        context_outputs = tf.transpose(context_outputs, perm=[0, 2, 1, 3])
        context_outputs = tf.reshape(context_outputs, (batch_size, -1, self.all_head_size))

        return context_outputs, attention_probs


class PlmBertAttention(BertAttention):
    """Plm bert attention"""

    def __init__(self, max_position_embeddings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.self_attention = PlmAttention(max_position_embeddings=max_position_embeddings, *args, **kwargs)

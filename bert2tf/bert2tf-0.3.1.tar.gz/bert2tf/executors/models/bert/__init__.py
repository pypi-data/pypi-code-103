import tensorflow as tf
from tensorflow.python.keras import backend as K

from .. import PreTrainModel
from ..configs import BertConfig
from ..helper import get_initializer, shape_list, get_weights_dict_from_h5, ACT2FN
from ..losses import MRCLoss
from ..transformer import TransformerAttention, TransformerEncoder, TransformerEmbedding, TransformerEncoderLayer


class Bert(PreTrainModel):
    """Bert models"""

    config_cls = BertConfig

    def __init__(self, with_pooler=True, seq_length=4, name='bert', **kwargs):
        """

        :param config: instance of bert configs or configs path
        :param with_pooler: whether create pooler layer
        :param seq_length: sequence length
        """
        super().__init__(name=name, **kwargs)

        self.seq_length = seq_length
        self.embeddings = self.create_embedding_layer(self.config)
        self.encoder = self.create_encoder_layer(self.config)
        if with_pooler:
            self.pooler = BertPooler(self.config.hidden_size, self.config.hidden_size, name='pooler')

    def create_embedding_layer(self, config):
        embeddings = BertEmbedding(config.hidden_size,
                                   config.type_vocab_size,
                                   vocab_size=config.vocab_size,
                                   initializer_range=config.initializer_range,
                                   hidden_dropout_prob=config.hidden_dropout_prob,
                                   max_position_embeddings=config.max_position_embeddings,
                                   name='embeddings')
        return embeddings

    def create_encoder_layer(self, config):
        encoder = BertEncoder(config.hidden_size, config.num_attention_heads, config.num_hidden_layers,
                              config.attention_probs_dropout_prob, config.initializer_range,
                              config.hidden_dropout_prob, config.hidden_act, config.intermediate_size, name='encoder')
        return encoder

    def get_pooler_outputs(self, inputs=None, num_layer_hidden=-1, hidden_states=None):
        """
        Get [CLS] output
        :param inputs: inputs
        :param num_layer_hidden: which layers to pool
        :param hidden_states: encoder layer hidden states
        """
        if hidden_states is None:
            all_hidden_states = self.call(inputs)
            hidden_states = all_hidden_states[num_layer_hidden]
        pooler_outputs = self.pooler(hidden_states)

        return pooler_outputs

    def get_dummy_inputs(self):
        input_ids = tf.keras.Input(shape=(self.seq_length,), name='input_ids')
        input_mask = tf.keras.Input(shape=(self.seq_length,), name='input_mask')
        segment_ids = tf.keras.Input(shape=(self.seq_length,), name='segment_ids')
        return [input_ids, input_mask, segment_ids]

    def call(self,
             inputs,
             attention_mask=None,
             segment_ids=None,
             position_ids=None,
             num_layer_hidden=-1,
             **kwargs):
        if isinstance(inputs, (list, tuple)):
            input_ids = inputs[0]
            attention_mask = inputs[1] if len(inputs) > 1 else attention_mask
            segment_ids = inputs[2] if len(inputs) > 2 else segment_ids
            position_ids = inputs[3] if len(inputs) > 3 else position_ids
        else:
            input_ids = inputs

        embedds = self.embeddings([input_ids, position_ids, segment_ids])
        all_hidden_states = self.encoder(embedds, attention_mask)
        hidden_states = all_hidden_states[num_layer_hidden]

        if hasattr(self, 'pooler'):
            pooler_outputs = self.pooler(hidden_states)
            return hidden_states, pooler_outputs

        return hidden_states

    def mapping(self, pretrained_model_path: str):
        name_to_variable = self.get_name_to_variable()
        if pretrained_model_path.endswith('.ckpt'):
            init_variables = tf.train.list_variables(pretrained_model_path)
            weight_value_tuples = self.ckpt_mapping(name_to_variable, init_variables,
                                                    pretrained_model_path)
        elif pretrained_model_path.endswith('.h5'):
            init_variables = get_weights_dict_from_h5(pretrained_model_path)
            weight_value_tuples = self.h5_mapping(name_to_variable, init_variables)
        else:
            self.logger.warning(f'{pretrained_model_path} does not have file extension, '
                                f'it will default as checkpoint file.')
            init_variables = tf.train.list_variables(pretrained_model_path)
            weight_value_tuples = self.ckpt_mapping(name_to_variable, init_variables,
                                                    pretrained_model_path)

        matched_weight_names = [var.name[:-2] for var, _ in weight_value_tuples]
        missed_weights = {name: var for name, var in name_to_variable.items() if name not in matched_weight_names}

        for name, _ in missed_weights.items():
            self.logger.warning(f'{name} missed from checkpoint weights')

        return weight_value_tuples

    def ckpt_mapping(self, name_to_variable, init_variables, pretrained_ckpt_path):
        """Get mapping from checkpoint file"""
        weight_value_tuples = []

        for name, _ in init_variables:
            resource_variable = None
            if name in name_to_variable:
                resource_variable = name_to_variable[name]
            elif f'{self.name}/{name}' in name_to_variable:
                resource_variable = name_to_variable[f'{self.name}/{name}']
            elif f'{name}/embeddings' in name_to_variable:
                resource_variable = name_to_variable[f'{name}/embeddings']

            if resource_variable is not None:
                value = tf.train.load_variable(pretrained_ckpt_path, name)
                weight_value_tuples.append((resource_variable, value))

        return weight_value_tuples

    def h5_mapping(self, name_to_variable, init_variables):
        """Get mapping from .h5 file"""
        weight_value_tuples = []
        for name, value in init_variables.items():
            if 'layer' in name:
                name = name.replace('layer_._', 'layer_')
            sub_names = list(name.split('/'))
            name = '/'.join(sub_names[1:])
            if name in name_to_variable:
                weight_value_tuples.append([name_to_variable[name], value])
            elif sub_names[-1] == 'weight' and f'{"/".join(sub_names[1:-1])}' in name_to_variable:
                weight_value_tuples.append([name_to_variable[f'{"/".join(sub_names[1:-1])}'], value])

        return weight_value_tuples


class BertEmbedding(TransformerEmbedding):
    """Bert word embedding"""

    def __init__(self, embed_size, type_vocab_size=None, use_token_type_embedd=True, share_word_embedding=False,
                 **kwargs):
        if use_token_type_embedd:
            if share_word_embedding:
                raise ValueError('can not set use_token_type_embedding and share_word_embedding both True. '
                                 f'either use token type embedding or use share word embedding as token type embedding')
            if not type_vocab_size:
                raise ValueError('if you want to use token type embedding, please set the length of token type vocab')

        super().__init__(embed_size=embed_size, **kwargs)

        self.share_word_embedding = share_word_embedding
        if use_token_type_embedd and not share_word_embedding:
            self.token_type_embeddings = tf.keras.layers.Embedding(
                type_vocab_size,
                embed_size,
                embeddings_initializer=get_initializer(self.initializer_range),
                name='token_type_embeddings'
            )
        else:
            self.token_type_embeddings = None

    def embedding(self, inputs):
        input_ids, position_ids, segment_ids = inputs
        embeds = super().embedding([input_ids, position_ids])
        input_shape = shape_list(input_ids)

        if self.token_type_embeddings:
            if segment_ids is None:
                segment_ids = tf.fill(input_shape, 0)
            token_type_embeddings = self.token_type_embeddings(segment_ids)
        elif self.share_word_embedding:
            if segment_ids is None:
                raise ValueError(
                    'if you want to share word embedding as token type embedding, you must input segment ids.')
            dtype = K.dtype(segment_ids)
            if dtype != 'int32' and dtype != 'int64':
                segment_ids = tf.cast(segment_ids, 'int32')
            token_type_embeddings = tf.gather(self.word_embeddings, segment_ids)
        else:
            token_type_embeddings = tf.zeros_like(embeds)

        embeds = embeds + token_type_embeddings

        return embeds


class BertEncoder(TransformerEncoder):
    """
    Bert Encoder
    """


class BertLayer(TransformerEncoderLayer):
    """
    Bert Layer
    """


class BertAttention(TransformerAttention):
    """
    Bert attention
    """


class BertPooler(tf.keras.layers.Layer):
    """
    Bert pool layer
    """

    def __init__(self, hidden_size, initializer_range, **kwargs):
        super().__init__(**kwargs)
        self.dense = tf.keras.layers.Dense(
            hidden_size,
            kernel_initializer=get_initializer(initializer_range),
            activation='tanh',
            name='dense',
        )

    def call(self, inputs, **kwargs):
        # We "pool" the models by simply taking the hidden state corresponding
        # to the first token.
        first_token_tensor = inputs[:, 0]
        pooled_output = self.dense(first_token_tensor)
        return pooled_output


class BertPredictionHeadTransform(tf.keras.layers.Layer):
    """
    Bert transformer layer
    it does 3 things
        1. dense inputs
        2. use activation function to activate hidden states
        3. layer normalization
    """

    def __init__(self, hidden_size, initializer_range, hidden_act, **kwargs):
        super().__init__(**kwargs)
        self.dense = tf.keras.layers.Dense(
            hidden_size, kernel_initializer=get_initializer(initializer_range), name='dense'
        )
        if isinstance(hidden_act, str):
            self.transform_act_fn = ACT2FN[hidden_act]
        else:
            self.transform_act_fn = hidden_act
        self.LayerNorm = tf.keras.layers.LayerNormalization(name='LayerNorm', epsilon=1e-12)

    def call(self, hidden_states, **kwargs):
        hidden_states = self.dense(hidden_states)
        hidden_states = self.transform_act_fn(hidden_states)
        hidden_states = self.LayerNorm(hidden_states)
        return hidden_states


class BertMRC(Bert):
    """Bert for machine reading comprehension, it bases on version which was provided by Google"""

    def __init__(self, custom_loss_fn=None, label_smoothing=None, **kwargs):
        """

        :param custom_loss_fn: custom loss function, if None, it will use categorical cross entropy loss function
        :param label_smoothing: label smoothing value
        """
        super().__init__(with_pooler=False, **kwargs)
        self.output_layer = BertMRCOutputs(self.config.hidden_size, self.config.initializer_range)
        self.loss_layer = MRCLoss(self.seq_length, custom_loss_fn=custom_loss_fn, label_smoothing=label_smoothing)

    def call(self, inputs, start_positions=None, end_positions=None, **kwargs):
        if isinstance(inputs, list) or isinstance(inputs, tuple):
            start_positions = inputs[3] if len(inputs) > 3 else start_positions
            end_positions = inputs[4] if len(inputs) > 4 else end_positions
            inputs = inputs[:3]
        elif isinstance(inputs, dict):
            if 'start_positions' in inputs.keys():
                start_positions = inputs.pop('start_positions')
            if 'end_positions' in inputs.keys():
                end_positions = inputs.pop('end_positions')

        hidden_states = super().call(inputs=inputs, **kwargs)
        start_logits, end_logits = self.output_layer(hidden_states)
        if start_positions and end_positions:
            loss = self.loss_layer([start_positions, end_positions], [start_logits, end_logits])
            self.add_loss(loss)

        return start_logits, end_logits

    def get_dummy_inputs(self):
        inputs = super().get_dummy_inputs()
        start_positions = tf.keras.Input(shape=(), name='start_positions')
        end_positions = tf.keras.Input(shape=(), name='end_positions')
        inputs.append(start_positions)
        inputs.append(end_positions)
        return inputs


class BertMRCOutputs(tf.keras.layers.Layer):
    """Bert mrc output layer"""

    def __init__(self, hidden_size, initializer_range, **kwargs):
        super().__init__(**kwargs)
        self.hidden_size = hidden_size
        self.initializer_range = initializer_range

    def build(self, input_shape):
        self.output_weights = self.add_weight(
            'cls/squad/output_weights',
            shape=[2, self.hidden_size],
            initializer=get_initializer(self.initializer_range),
        )

        self.output_bias = self.add_weight(
            'cls/squad/output_bias',
            shape=[2],
            initializer='zeros',
        )
        super().build(input_shape)

    def call(self, inputs, **kwargs):
        final_hidden_shape = shape_list(inputs)
        batch_size = final_hidden_shape[0]
        seq_length = final_hidden_shape[1]
        hidden_size = final_hidden_shape[2]

        final_hidden_matrix = tf.reshape(inputs, [batch_size * seq_length, hidden_size])

        logits = tf.matmul(final_hidden_matrix, self.output_weights, transpose_b=True)
        logits = tf.nn.bias_add(logits, self.output_bias)

        logits = tf.reshape(logits, [batch_size, seq_length, 2])
        logits = tf.transpose(logits, [2, 0, 1])

        start_logits, end_logits = tf.unstack(logits, axis=0)

        return start_logits, end_logits


class BertPreTrainingModel(Bert):
    """Bert models for pre training"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.nsp = BertNSP(self.config.hidden_size, self.config.initializer_range, name='cls/seq_relationship')
        self.mlm = BertMLMHead(self.config.vocab_size, self.config.hidden_size, self.config.initializer_range,
                               self.config.hidden_act, self.embeddings, name='cls')

    def call(self, inputs, **kwargs):
        hidden_states, pooler_outputs = super().call(inputs, **kwargs)
        prediction_scores = self.mlm(hidden_states)
        seq_relationship_score = self.nsp(pooler_outputs)

        return prediction_scores, seq_relationship_score


class BertNSP(tf.keras.layers.Layer):
    """
    Bert next sentence prediction layer
    """

    def __init__(self, hidden_size, initializer_range, **kwargs):
        super().__init__(**kwargs)
        self.hidden_size = hidden_size
        self.initializer_range = initializer_range

    def build(self, input_shape):
        self.output_weights = self.add_weight(
            'output_weights',
            shape=[2, self.hidden_size],
            initializer=get_initializer(self.initializer_range),
        )

        self.output_bias = self.add_weight(
            'output_bias',
            shape=[2],
            initializer='zeros',
        )
        super().build(input_shape)

    def call(self, pooled_output, **kwargs):
        seq_relationship_score = tf.matmul(pooled_output, self.output_weights, transpose_b=True)
        seq_relationship_score = seq_relationship_score + self.output_bias
        return seq_relationship_score


class BertMLMHead(tf.keras.layers.Layer):
    def __init__(self, vocab_size, hidden_size, initializer_range, hidden_act, input_embeddings, **kwargs):
        super().__init__(**kwargs)
        self.predictions = BertLMPredictionHead(vocab_size, hidden_size, initializer_range, hidden_act,
                                                input_embeddings, name='predictions')

    def call(self, sequence_output, **kwargs):
        prediction_scores = self.predictions(sequence_output)
        return prediction_scores


class BertLMPredictionHead(tf.keras.layers.Layer):
    def __init__(self, vocab_size, hidden_size, initializer_range, hidden_act, input_embeddings, **kwargs):
        super().__init__(**kwargs)
        self.vocab_size = vocab_size
        self.transform = BertPredictionHeadTransform(hidden_size, initializer_range, hidden_act, name='transform')

        # The output weights are the same as the input embeddings, but there is
        # an output-only bias for each token.
        self.input_embeddings = input_embeddings

    def build(self, input_shape):
        self.bias = self.add_weight(shape=(self.vocab_size,), initializer='zeros', name='output_bias')
        super().build(input_shape)

    def call(self, hidden_states, **kwargs):
        hidden_states = self.transform(hidden_states)
        # hidden_states = tf.matmul(hidden_states, self.input_embeddings.word_embeddings, transpose_b=True)
        hidden_states = self.input_embeddings(hidden_states, mode='linear')
        hidden_states = tf.nn.bias_add(hidden_states, self.bias)
        return hidden_states

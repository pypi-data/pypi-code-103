from typing import List, Tuple, Union

import numpy as np
import tensorflow as tf

from .. import PreTrainModel
from ..bert import Bert, BertLMPredictionHead
from ..helper import get_weights_dict_from_h5, shape_list, get_initializer
from ..configs import SoftMaskedBertConfig


class SoftMaskedBert(PreTrainModel):
    """
    Soft Masked Bert
    """
    config_cls = SoftMaskedBertConfig

    def __init__(self, name: str = 'soft_masked_bert', **kwargs):
        super(SoftMaskedBert, self).__init__(name=name, **kwargs)

        self.detector = SoftMaskedBertDetector(self.config, name='detector')
        self.corrector = SoftMaskedBertCorrector(self.config, name='corrector')
        self.intermediate = SoftMaskedBertIntermediate(self.config.masked_id, self.corrector.embeddings)

    def call(self,
             inputs: Union[np.ndarray, List, Tuple],
             segment_ids: np.ndarray = None,
             attention_mask: np.ndarray = None,
             num_layer_hidden: int = -1,
             **kwargs):
        if isinstance(inputs, (List, Tuple)):
            input_ids = inputs[0]
            segment_ids = inputs[1] if len(inputs) > 1 else segment_ids
            attention_mask = inputs[2] if len(inputs) > 2 else attention_mask

        else:
            input_ids = inputs

        embeddings = self.corrector.embeddings([input_ids, None, segment_ids])

        detector_scores = self.detector(embeddings)
        hidden_states, detector_scores = self.intermediate([detector_scores, embeddings])
        corrector_logits = self.corrector(hidden_states, attention_mask, embeddings)

        return detector_scores, corrector_logits

    def get_dummy_inputs(self):
        input_ids = tf.keras.Input(shape=(8,), name='input_ids')
        input_mask = tf.keras.Input(shape=(8,), name='input_mask')
        segment_ids = tf.keras.Input(shape=(8,), name='segment_ids')
        return [input_ids, input_mask, segment_ids]

    def mapping(self, pretrained_model_path: str):
        name_to_variable = self.get_name_to_variable()

        if pretrained_model_path.endswith('.h5'):
            init_variables = get_weights_dict_from_h5(pretrained_model_path)
            variable_names = init_variables.keys()
        else:
            init_variables = tf.train.list_variables(pretrained_model_path)
            variable_names = [name for name, _ in init_variables]

        weight_value_tuples = []

        for name in variable_names:
            resource_variable = None
            if name in name_to_variable:
                resource_variable = name_to_variable[name]
            elif name.replace('bert', self.name) in name_to_variable:
                resource_variable = name_to_variable[name.replace('bert', self.name)]
            elif f'{name.replace("bert", self.name)}/embeddings' in name_to_variable:
                resource_variable = name_to_variable[f'{name.replace("bert", self.name)}/embeddings']
            elif name.replace('bert', f'{self.name}/corrector') in name_to_variable:
                resource_variable = name_to_variable[name.replace('bert', f'{self.name}/corrector')]
            elif f'{self.name}/corrector/{name}' in name_to_variable:
                resource_variable = name_to_variable[f'{self.name}/corrector/{name}']

            if resource_variable is not None:
                if pretrained_model_path.endswith('.h5'):
                    value = init_variables[name]
                else:
                    value = tf.train.load_variable(pretrained_model_path, name)
                weight_value_tuples.append((resource_variable, value))

        matched_weight_names = [var.name[:-2] for var, _ in weight_value_tuples]
        missed_weights = {name: var for name, var in name_to_variable.items() if
                          name not in matched_weight_names and 'gru' not in name and 'pointer' not in name}

        for name, _ in missed_weights.items():
            self.logger.warning(f'{name} missed from checkpoint weights')

        return weight_value_tuples


class SoftMaskedBertIntermediate(tf.keras.layers.Layer):
    def __init__(self, masked_id: int, embeddings: tf.keras.layers.Layer, **kwargs):
        super(SoftMaskedBertIntermediate, self).__init__(**kwargs)

        self.masked_id = masked_id
        self.embeddings = embeddings

    def get_masked_embedding(self, batch_size: int, seq_len: int) -> tf.Tensor:
        """
        Get masked embedding with shape [batch_size, seq_len, hidden_size] by adding word embedding with token type embedding
        :param batch_size: batch size of this batch
        :param seq_len: sequence length of this batch size
        :return: masked embedding
        """
        masked_word_ids = tf.ones([batch_size, seq_len], dtype=tf.int32)
        masked_word_ids = masked_word_ids * self.masked_id

        masked_word_embedding = self.embeddings([masked_word_ids, None, None])

        return masked_word_embedding

    def call(self, inputs, **kwargs):
        detector_scores, embeddings = inputs
        true_scores = 1 - detector_scores
        batch_size, seq_len, _ = shape_list(detector_scores)
        masked_embeddings = self.get_masked_embedding(batch_size, seq_len)

        hidden_states = true_scores * embeddings + detector_scores * masked_embeddings

        scores = tf.concat([true_scores, detector_scores], axis=-1)

        return hidden_states, scores


class SoftMaskedBertCorrector(Bert):
    """
    Soft Masked Bert Corrector
    """
    config_cls = SoftMaskedBertConfig

    def __init__(self, config: SoftMaskedBertConfig, name: str = 'corrector', *args, **kwargs):
        super(SoftMaskedBertCorrector, self).__init__(config=config, name=name, with_pooler=False, *args, **kwargs)
        self.predictions = SoftMaskedBertCorrectorLMPredictionHead(config.vocab_size,
                                                                   config.hidden_size,
                                                                   config.initializer_range,
                                                                   config.hidden_act,
                                                                   self.embeddings,
                                                                   name='cls/predictions')

    def call(self,
             inputs: tf.Tensor,
             context_mask: np.ndarray = None,
             embeddings: tf.Tensor = None,
             num_layer_hidden: int = -1,
             **kwargs):
        hidden_states = self.encoder(inputs, context_mask)[num_layer_hidden]
        prediction_scores = self.predictions(hidden_states, embeddings)

        return prediction_scores


class SoftMaskedBertCorrectorLMPredictionHead(BertLMPredictionHead):

    def call(self, hidden_states, embeddings=None, **kwargs):
        hidden_states = self.transform(hidden_states)
        hidden_states += embeddings
        prediction_scores = self.input_embeddings(hidden_states, mode='linear')
        prediction_scores = prediction_scores + self.bias

        return prediction_scores


class SoftMaskedBertDetector(tf.keras.layers.Layer):
    """
    Soft-Masked Bert Detector
    """

    def __init__(self, config: SoftMaskedBertConfig, name: str = 'detector', **kwargs):
        super(SoftMaskedBertDetector, self).__init__(name=name, **kwargs)

        self.bi_gru = tf.keras.layers.Bidirectional(
            tf.keras.layers.GRU(units=int(config.hidden_size / 2),
                                dropout=config.hidden_dropout_prob,
                                return_sequences=True,
                                kernel_initializer=get_initializer(config.initializer_range)))

        self.pointer = tf.keras.layers.Dense(1, activation=tf.nn.sigmoid, name='pointer')

    def call(self, embeddings: np.ndarray, **kwargs):
        hidden_states = self.bi_gru(embeddings)
        scores = self.pointer(hidden_states)

        return scores

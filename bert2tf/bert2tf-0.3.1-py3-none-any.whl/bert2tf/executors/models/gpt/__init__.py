import numpy as np

from ..auto_regressive import AutoRegressive
from ..bert import BertMLMHead, Bert, BertEmbedding, BertEncoder
from ..configs import GPTConfig, HuaweiGPTConfig
from ..transformer import TransformerAttention, TransformerEncoderLayer


class OpenAIGPT(Bert):
    config_cls = GPTConfig

    def __init__(self, name='gpt', **kwargs):
        super().__init__(with_pooler=False, name=name, **kwargs)

    def create_embedding_layer(self, config):
        embeddings = OpenAIGPTEmbedding(vocab_size=config.vocab_size, embed_size=config.hidden_size,
                                        initializer_range=config.initializer_range,
                                        hidden_dropout_prob=config.hidden_dropout_prob,
                                        max_position_embeddings=config.max_position_embeddings,
                                        name='embeddings')
        return embeddings

    def create_encoder_layer(self, config):
        encoder = OpenAIGPTEncoder(hidden_size=config.hidden_size, num_attention_heads=config.num_attention_heads,
                                   num_hidden_layers=config.num_hidden_layers,
                                   attention_probs_dropout_prob=config.attention_probs_dropout_prob,
                                   initializer_range=config.initializer_range,
                                   hidden_dropout_prob=config.hidden_dropout_prob, hidden_act=config.hidden_act,
                                   intermediate_size=config.intermediate_size,
                                   name='transformer')
        return encoder


class OpenAIGPTPretraing(OpenAIGPT):
    def call(self, inputs, **kwargs):
        hidden_states = super().call(inputs, **kwargs)
        prediction_scores = self.embeddings(hidden_states, mode='linear')

        return prediction_scores


class OpenAIGPTAutoRegressive(OpenAIGPTPretraing, AutoRegressive):
    """OpenAI GPT auto regressive models"""

    def __init__(self, end_id, start_id=None, top_k=4, top_p=None, num_samples=1, min_ends=1, min_len=16, max_len=128,
                 **kwargs):
        """

        :param end_id: full stop or exclamation point id etc in vocab
        :param start_id:  first token of whole generate sentences
        :param top_k: generate from top k probability
        :param top_p: sample from over top probability and sum of probability
        :param num_samples: how many samples should we sample, used for beam search
        :param min_ends: related to end id, should the models stops at how many end id were generated
        :param min_len: the minimum length of generate sentence
        :param max_len: max length of sample sentence
        """
        super().__init__(**kwargs)
        self.end_id = end_id
        self.start_id = start_id
        self.top_k = top_k
        self.min_ends = min_ends
        self.min_len = min_len
        self.max_len = max_len
        self.top_p = top_p
        self.num_samples = num_samples

    def next_token_scores(self, inputs, output_ids, **kwargs):
        input_ids, segment_ids = inputs
        curr_segment_ids = np.zeros_like(output_ids) + input_ids[0, -1]
        input_ids = np.concatenate([input_ids, output_ids], 1)
        segment_ids = np.concatenate([segment_ids, curr_segment_ids], 1)
        scores = self.call([input_ids, None, segment_ids], **kwargs)[:, -1]

        return scores


class HuaweiGPT(Bert):
    """Huawei GPT models"""
    config_cls = HuaweiGPTConfig

    def __init__(self, **kwargs):
        super().__init__(with_pooler=False, **kwargs)

    def create_embedding_layer(self, config):
        embeddings = HuaweiGPTEmbedding(vocab_size=config.vocab_size, embed_size=config.hidden_size,
                                        initializer_range=config.initializer_range,
                                        hidden_dropout_prob=config.hidden_dropout_prob,
                                        max_position_embeddings=config.max_position_embeddings, name='embeddings')
        return embeddings

    def create_encoder_layer(self, config):
        encoder = HuaweiGPTEncoder(config.hidden_size, config.num_attention_heads, config.num_hidden_layers,
                                   config.attention_probs_dropout_prob, config.initializer_range,
                                   config.hidden_dropout_prob, config.hidden_act, config.intermediate_size,
                                   name='encoder')
        return encoder

    def get_dummy_inputs(self):
        return super(HuaweiGPT, self).get_dummy_inputs()[:1]


class HuaweiGPTPreTraining(HuaweiGPT):
    """
    GPT pre training models from huawei, it has same structure with bert, but it uses masked self attention as self attention.
    it is used for pre training
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mlm = BertMLMHead(self.config.vocab_size, self.config.hidden_size, self.config.initializer_range,
                               self.config.hidden_act, self.embeddings, name='cls')

    def call(self, inputs, **kwargs):
        hidden_states = super().call(inputs, **kwargs)
        prediction_scores = self.mlm(hidden_states)
        return prediction_scores


class HuaweiGPTAutoRegressive(HuaweiGPTPreTraining, AutoRegressive):
    """
    GPT auto regressive models from huawei, it has same structure with bert, but it uses masked self attention as self attention.
    it is used for generate text
    """

    def __init__(self, end_id, start_id=None, top_k=4, top_p=None, num_samples=1, min_ends=1, min_len=16, max_len=128,
                 **kwargs):
        """

        :param end_id: full stop or exclamation point id etc in vocab
        :param start_id:  first token of whole generate sentences
        :param top_k: generate from top k probability
        :param top_p: sample from over top probability and sum of probability
        :param num_samples: how many samples should we sample, used for beam search
        :param min_ends: related to end id, should the models stops at how many end id were generated
        :param min_len: the minimum length of generate sentence
        :param max_len: max length of sample sentence
        """
        super().__init__(**kwargs)
        self.end_id = end_id
        self.start_id = start_id
        self.top_k = top_k
        self.min_ends = min_ends
        self.min_len = min_len
        self.max_len = max_len
        self.top_p = top_p
        self.num_samples = num_samples

    def next_token_scores(self, inputs, output_ids):
        inputs = np.concatenate([inputs[0], output_ids], 1)
        return self.call(inputs)[:, -1]


class OpenAIGPTEmbedding(BertEmbedding):
    """OpenAI GPT Embedding"""

    def __init__(self, *args, **kwargs):
        super().__init__(use_token_type_embedd=False, share_word_embedding=True, *args, **kwargs)

    def call(self, inputs, **kwargs):
        return super().call(inputs, do_ln=False, **kwargs)


class HuaweiGPTEmbedding(BertEmbedding):
    """Huawei GPT Embedding"""

    def __init__(self, *args, **kwargs):
        super().__init__(use_token_type_embedd=False, *args, **kwargs)


class HuaweiGPTEncoder(BertEncoder):
    """
    Encoder for Huawei GPT
    """

    def __init__(self, hidden_size, num_attention_heads, num_hidden_layers, attention_probs_dropout_prob,
                 initializer_range, hidden_dropout_prob, hidden_act, intermediate_size, **kwargs):
        super(HuaweiGPTEncoder, self).__init__(hidden_size, num_attention_heads, num_hidden_layers,
                                               attention_probs_dropout_prob, initializer_range, hidden_dropout_prob,
                                               hidden_act, intermediate_size, **kwargs)
        self.layers = [
            HuaweiGPTEncoderLayer(hidden_size, num_attention_heads, attention_probs_dropout_prob, initializer_range,
                                  hidden_dropout_prob, hidden_act, intermediate_size, name=f'layer_{i}')
            for i in range(num_hidden_layers)]


class HuaweiGPTEncoderLayer(TransformerEncoderLayer):
    def __init__(self, hidden_size, num_attention_heads, attention_probs_dropout_prob, initializer_range,
                 hidden_dropout_prob, *args, **kwargs):
        super(HuaweiGPTEncoderLayer, self).__init__(hidden_size, num_attention_heads, attention_probs_dropout_prob,
                                                    initializer_range, hidden_dropout_prob, *args, **kwargs)
        self.attention = TransformerAttention(hidden_size, num_attention_heads, attention_probs_dropout_prob,
                                              hidden_dropout_prob, initializer_range, name='attention', masked=True)


class OpenAIGPTEncoder(HuaweiGPTEncoder):
    """
        Encoder for OpenAI GPT
        """

import tensorflow as tf

from ..bert import Bert, BertEmbedding
from ..configs import ElectraConfig


class ElectraDiscriminator(Bert):
    """Electra discriminator models from google"""
    config_cls = ElectraConfig

    def __init__(self, name='electra', **kwargs):
        super().__init__(with_pooler=False, name=name, **kwargs)

    def create_embedding_layer(self, config):
        embeddings = ElectraEmbedding(config.embedding_size,
                                      config.hidden_size,
                                      vocab_size=config.vocab_size,
                                      initializer_range=config.initializer_range,
                                      type_vocab_size=config.type_vocab_size,
                                      max_position_embeddings=config.max_position_embeddings,
                                      hidden_dropout_prob=config.hidden_dropout_prob,
                                      name='embeddings')

        return embeddings

    def ckpt_mapping(self, name_to_variable, init_variables, pretrained_ckpt_path):
        weight_value_tuples = super().ckpt_mapping(name_to_variable, init_variables, pretrained_ckpt_path)
        extras = {
            f'{self.name}/embeddings_project/kernel': f'{self.name}/embeddings/embeddings_project/kernel',
            f'{self.name}/embeddings_project/bias': f'{self.name}/embeddings/embeddings_project/bias'
        }
        for init_name, trainable_name in extras.items():
            value = tf.train.load_variable(pretrained_ckpt_path, init_name)
            weight_value_tuples.append((name_to_variable[trainable_name], value))

        return weight_value_tuples


class ElectraEmbedding(BertEmbedding):
    """Electra Embedding for google"""

    def __init__(self, embed_size, hidden_size, **kwargs):
        super().__init__(embed_size=embed_size, use_token_type_embedd=True, share_word_embedding=False, **kwargs)
        if embed_size != hidden_size:
            self.embeddings_project = tf.keras.layers.Dense(hidden_size, name='embeddings_project')

    def call(self, inputs, mode='embedding', **kwargs):
        embedds = super().call(inputs, mode=mode, **kwargs)
        if mode == 'embedding' and hasattr(self, 'embeddings_project'):
            embedds = self.embeddings_project(embedds)
        return embedds

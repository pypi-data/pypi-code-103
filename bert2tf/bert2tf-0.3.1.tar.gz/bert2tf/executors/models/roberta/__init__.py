from ..bert import Bert, BertMLMHead


class Roberta(Bert):
    """
    Roberta, it has same structure with bert
    """


class RobertaPreTraining(Roberta):
    """
    Roberta Pre Training Model, it exclude nsp task
    """

    def __init__(self, **kwargs):
        super(RobertaPreTraining, self).__init__(with_pooler=False, **kwargs)
        self.mlm = BertMLMHead(self.config.vocab_size, self.config.hidden_size, self.config.initializer_range,
                               self.config.hidden_act, self.embeddings, name='cls')

    def call(self, inputs, **kwargs):
        hidden_states = super(RobertaPreTraining, self).call(inputs)
        prediction_scores = self.mlm(hidden_states)

        return prediction_scores

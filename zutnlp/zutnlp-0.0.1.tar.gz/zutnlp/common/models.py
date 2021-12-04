from typing import Tuple, Union

import torch

from . import BaseModel
import torch.nn as nn


class Model(BaseModel):

    def __init__(self, encoder):
        super(Model, self).__init__()

        pass

    def predict(self, *args, **kwargs):
        pass


# TODO 未构建完成
class RNNSeq2SeqEncoder(nn.Module):
    def __init__(self, embed: nn.Module, hidden_dim=300, dropout=0.3, num_layers=2, bidirectional=True,
                 rnn_type="lstm", pad_value=0):
        super(RNNSeq2SeqEncoder, self).__init__()
        assert rnn_type in ["lstm", "gru"]
        self.embed = embed
        self.num_layers = num_layers
        self.dropout = dropout
        self.hidden_dim = hidden_dim
        self.bidirectional = bidirectional
        self.pad_value = pad_value
        self.rnn_type = rnn_type

        hidden_dim = hidden_dim // 2 if bidirectional else hidden_dim

        if rnn_type == "lstm":
            self.rnn = nn.LSTM(input_size=embed.embedding_dim, hidden_size=hidden_dim, bidirectional=bidirectional,
                               batch_first=True, dropout=dropout if num_layers > 1 else 0, num_layers=num_layers)
        elif rnn_type == "gru":
            self.rnn = nn.GRU(input_size=embed.embedding_dim, hidden_size=hidden_dim, bidirectional=bidirectional,
                              batch_first=True, dropout=dropout if num_layers > 1 else 0, num_layers=num_layers)

    def forward(self, tokens):
        x = self.embed(tokens)
        encoder_mask = torch.ne(tokens, self.pad_value)
        if self.rnn_type == "lstm":
            x, (final_hidden, final_cell) = self.rnn(x)
            if self.bidirectional:
                final_hidden = self.concat_bidir(final_hidden)  # 将双向的hidden state拼接起来，用于接下来的decoder的input
                final_cell = self.concat_bidir(final_cell)
        elif self.rnn_type == "gru":
            x, hidden = self.rnn(x)

        return (x, (final_hidden[-1], final_cell[-1])), encoder_mask

    def concat_bidir(self, input):
        output = input.view(self.num_layers, 2, input.size(1), -1).transpose(1, 2)
        return output.reshape(self.num_layers, input.size(1), -1)

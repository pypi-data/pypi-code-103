import collections
import operator
from typing import Dict, Any, Tuple

import numpy as np
import tqdm

from kolibri.indexers.base_indexer import BaseIndexer


class LabelIndexer(BaseIndexer):

    def to_dict(self) -> Dict[str, Any]:
        data = super(LabelIndexer, self).to_dict()
        data['config']['multi_label'] = self.multi_label
        data['config']['index'] = self.index
        return data

    def __init__(self, multi_label=False, index=None, **kwargs):
        from sklearn.preprocessing import MultiLabelBinarizer
        super(LabelIndexer, self).__init__(**kwargs)
        self.multi_label = multi_label
        self.multi_label_binarizer = MultiLabelBinarizer()
#        self.multi_label_binarizer.fit_transform(self.token2id)
        self.index = index

    def build_vocab(self, x_data, y_data):
        from sklearn.preprocessing import MultiLabelBinarizer
        if self.token2id:
            return

        if y_data is None:
            raise ValueError

        token2id: Dict[str, int] = {}
        token2count: Dict[str, int] = {}
        if self.multi_label:
            for label in tqdm.tqdm(y_data, desc="Preparing classification label vocab dict"):
                if self.index is not None:
                    label = label[self.index]
                for token in label:
                    count = token2count.get(token, 0)
                    token2count[token] = count + 1
        else:
            for label in tqdm.tqdm(y_data, desc="Preparing classification label vocab dict"):
                if self.index is not None:
                    label = label[self.index]

                count = token2count.get(label, 0)
                token2count[label] = count + 1

        sorted_token2count = sorted(token2count.items(),
                                    key=operator.itemgetter(1),
                                    reverse=True)
        token2count = collections.OrderedDict(sorted_token2count)

        for token, token_count in token2count.items():
            if token not in token2id:
                token2id[token] = len(token2id)
        self.token2id = token2id
        self.id2token = dict([(v, k) for k, v in self.token2id.items()])
        self.multi_label_binarizer = MultiLabelBinarizer()
        self.multi_label_binarizer.fit(self.token2id)

    def get_tensor_shape(self, batch_size: int, seq_length: int) -> Tuple:
        if self.multi_label:
            return batch_size, len(self.token2id)
        else:
            return (batch_size,)

    def transform(self, samples, **kwargs):
        if self.multi_label:
            sample_tensor = self.multi_label_binarizer.transform(samples)
            return sample_tensor
        if self.index is not None:
            sample_tensor = [self.token2id[sample[self.index]] for sample in samples]
        else:
            sample_tensor = [self.token2id[sample] for sample in samples]
        return np.array(sample_tensor)

    def inverse_transform(self,
                          labels,
                          *,
                          lengths=None,
                          **kwargs):
        if self.multi_label:
            return self.multi_label_binarizer.inverse_transform(labels)
        else:
            return [self.id2token[i] for i in labels]


if __name__ == "__main__":
    pass

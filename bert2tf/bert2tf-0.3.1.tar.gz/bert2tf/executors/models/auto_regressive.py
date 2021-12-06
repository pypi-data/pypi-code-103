from typing import List

import numpy as np
import tensorflow as tf


class AutoRegressive:
    """Auto regressive, it is used to generate text"""

    def beam_search(self, inputs: List[np.ndarray], **kwargs):
        """
        Beam search
        :param inputs: a list contain input ids or input masks or segment ids for 1 sample
        :return: 1 axis list, each elements is vocab id
        """
        top_k = self.top_k
        output_ids = np.empty((1, 0), dtype=int) if self.start_id is None else np.array([[self.start_id]])
        output_scores = np.zeros(1)

        for step in range(self.max_len):
            scores = self.next_token_scores(inputs, output_ids).numpy()

            if step == 0:
                inputs = [np.repeat(_input, top_k, axis=0) for _input in inputs]

            scores = output_scores.reshape((-1, 1)) + scores
            indices = scores.argpartition(-top_k, axis=None)[-top_k:]
            indices_1 = indices // scores.shape[1]
            indices_2 = (indices % scores.shape[1]).reshape((-1, 1))

            output_ids = np.concatenate([output_ids[indices_1], indices_2], 1)
            output_scores = np.take_along_axis(scores, indices, axis=None)

            end_counts = (output_ids == self.end_id).sum(1)

            if output_ids.shape[1] >= self.min_len:
                best_one = output_scores.argmax()
                if end_counts[best_one] == self.min_ends:  # 如果已经终止
                    return output_ids[best_one][:-1]
                else:  # 否则，只保留未完成部分, 未完成部分还没有结束标志
                    flag = (end_counts < self.min_ends)  # 标记未完成序列
                    if not flag.all():  # 如果有已完成的
                        inputs = [_input[flag] for _input in inputs]  # 扔掉已完成序列
                        output_ids = output_ids[flag]  # 扔掉已完成序列
                        output_scores = output_scores[flag]  # 扔掉已完成序列
                        top_k = flag.sum()  # top_k相应变化

            # 达到长度直接输出
        return output_ids[output_scores.argmax()]

    def random_sample(self, inputs: List[np.ndarray], **kwargs):
        """
        Random sample
        :param inputs: a list contain input ids or input masks or segment ids for 1 sample
        :return: 2 axis list, each list contains all token ids of each sentence
        """
        output_ids = np.empty((1, 0), dtype=int) if self.start_id is None else np.array([[self.start_id]])

        results = []
        for step in range(self.max_len):
            probas = self.next_token_probas(inputs, output_ids).numpy()
            p_indices = None
            k_indices = None
            probas /= probas.sum(axis=1, keepdims=True)  # normalization
            if step == 0:
                probas = np.repeat(probas, self.num_samples, axis=0)  # repeat for n times
                inputs = [np.repeat(_input, self.num_samples, axis=0) for _input in inputs]
                output_ids = np.repeat(output_ids, self.num_samples, axis=0)

            if self.top_k is not None:
                k_indices = probas.argpartition(-self.top_k, axis=1)[:, -self.top_k:]
                probas = np.take_along_axis(probas, k_indices, axis=1)
                probas /= probas.sum(axis=1, keepdims=True)  # normalization again

            if self.top_p is not None:
                p_indices = probas.argsort(axis=1)[:, ::-1]
                probas = np.take_along_axis(probas, p_indices, axis=1)
                cumsum_probas = np.cumsum(probas, axis=1)
                flag = np.roll(cumsum_probas >= self.top_p, 1, axis=1)  # target the position which over top_p
                flag[:, 0] = False  # combine with np.roll, we shift one position
                probas[flag] = 0  # put the prob to zero which the position's flag is True
                probas /= probas.sum(axis=1, keepdims=True)  # normalization again

            # sample
            sample_ids = np.apply_along_axis(func1d=lambda p: np.random.choice(len(p), p=p), axis=1, arr=probas)
            sample_ids = sample_ids.reshape((-1, 1))

            if self.top_p is not None:
                sample_ids = np.take_along_axis(p_indices, sample_ids, axis=1)

            if self.top_k is not None:
                sample_ids = np.take_along_axis(k_indices, sample_ids, axis=1)

            output_ids = np.concatenate([output_ids, sample_ids], 1)  # update output ids
            end_counts = (output_ids == self.end_id).sum(1)

            if output_ids.shape[1] >= self.min_len:
                flag = (end_counts == self.min_ends)
                if flag.any():
                    for ids in output_ids[flag]:
                        results.append(ids[:-1])

                    flag = (flag == False)
                    inputs = [_input[flag] for _input in inputs]
                    output_ids = output_ids[flag]
                    if len(output_ids) == 0:
                        break

        for ids in output_ids:
            results.append(ids)

        return results

    def next_token_scores(self, inputs, output_ids):
        """Return a tensor which is the vocab score of next token"""
        raise NotImplementedError

    def next_token_probas(self, inputs, output_ids):
        """Return a tensor which is the vocab probability of next token"""
        scores = self.next_token_scores(inputs, output_ids)
        probas = tf.nn.softmax(scores)
        return probas

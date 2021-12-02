import spacy
from spacytextblob.spacytextblob import SpacyTextBlob

class BasePredictor(object):

    def process(self, task):
        pass


class SpacyPredictor(BasePredictor):

    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.nlp.add_pipe('spacytextblob')

    def process_many(self, tasks):
        return list(map(self.process, tasks))

    def process(self, task):
        text = task['data']['text']
        doc = self.nlp(text)
        predictions = []

        # Extract tokens
        prev_pred = None
        curr_id = None
        for tok in doc:
            new_pred = {
                'id': tok.i,
                'from_name': 'token',
                'to_name': 'text',
                'type': 'labels',
                'value': {
                    'start': tok.idx,
                    'end': tok.idx + len(tok.text),
                    'labels': [tok.text],
                    'text': tok.text
                }
            }
            predictions.append(new_pred)
            if prev_pred:
                predictions.append({
                    'type': 'relation',
                    'from_id': prev_pred['id'],
                    'to_id': predictions[-1]['id'],
                    'direction': 'right'
                })
            prev_pred = new_pred
            curr_id = tok.i

        # Extract Named Entities
        curr_id += 1
        for ent in doc.ents:
            predictions.append({
                'id': curr_id,
                'from_name': 'ner',
                'to_name': 'text',
                'type': 'labels',
                'value': {
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'labels': [f'<{ent.label_}>'],
                    'text': ent.text
                }
            })
            prev_token_idx = ent.start - 1
            if prev_token_idx > 0:
                predictions.append({
                    'type': 'relation',
                    'from_id': prev_token_idx,
                    'to_id': curr_id,
                    'direction': 'right'
                })
            curr_id += 1

        # Extract Sentiment
        # predictions.append({
        #     'from_name': 'sentiment',
        #     'to_name': 'text',
        #     'type': 'choices',
        #     'value': {
        #         'choices': ['positive' if doc._.polarity > 0 else 'negative']
        #     }
        # })

        return {
            'result': predictions,
            'task': task['id']
        }

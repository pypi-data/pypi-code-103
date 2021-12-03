import csv
from pkg_resources import resource_filename


class UdTagger:
    UNK_TAG = 'UNK'

    def __init__(self, language):
        self.language = language
        data = self.get_data(language)
        self.model = self.create_model(data)

    @staticmethod
    def read_data(filename):
        with open(filename, "r") as f:
            reader = csv.DictReader(f, delimiter='\t')
            data = list(reader)
        return data

    @classmethod
    def get_data(cls, language, data_path='data/'):
        fname = '%s/%s-ud_lemmas.tsv' %(data_path, language)
        fpath = resource_filename('ud2pos', fname)
        # import ipdb; ipdb.set_trace()
        return cls.read_data(fpath)

    @staticmethod
    def create_model(data):
        model = {}
        for item in data:
            model[item['form']] = item['pos']

        return model

    def __call__(self, word):
        return self.model.get(word.lower(), self.UNK_TAG)

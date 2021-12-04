from fastNLP import DataSet as Ds


class BaseDataSet(Ds):
    def __init__(self, data=None):
        super(BaseDataSet, self).__init__(data=data)

from ._utils import del_na_mask, del_sd_mask, del_corr_mask
from ._utils import raise_dataobject as rd

class Delete(object):
    
    def __init__(self):
        pass

    def transform(self, dataobject):
        rd(dataobject)
        dataobject.X = dataobject.X[:, self.mask]
        dataobject.Xnames = dataobject.Xnames[self.mask]
        return dataobject

    def fit_transform(self, dataobject):
        rd(dataobject)
        self.fit(dataobject)
        return self.transform(dataobject)

class DeleteNan(Delete):

    def __init__(self):
        super(DeleteNan, self).__init__()

    def fit(self, dataobject):
        rd(dataobject)
        self.mask = del_na_mask(dataobject.X)

class DeleteSd(Delete):

    def __init__(self, criterion=0.00001):
        super(DeleteSd, self).__init__()
        self.criterion = criterion

    def fit(self, dataobject):
        rd(dataobject)
        self.mask = del_sd_mask(dataobject.X, self.criterion)

class DeleteCorr(Delete):

    def __init__(self, criterion=0.99):
        super(DeleteCorr, self).__init__()
        self.criterion = criterion

    def fit(self, dataobject):
        rd(dataobject)
        self.mask = del_corr_mask(dataobject.X, self.criterion)

class Preprocessing(object):

    def __init__(self, sd=True, corr=True, sd_criterion=0.00001, corr_criterion=0.99):
        self.sd = sd
        self.corr = corr
        self.sd_criterion = sd_criterion
        self.corr_criterion = corr_criterion

    def fit_transform(self, dataobject):
        rd(dataobject)
        dataobject = DeleteNan().fit_transform(dataobject)
        if self.sd:
            dataobject = DeleteSd(self.sd_criterion).fit_transform(dataobject)
        if self.corr:
            dataobject = DeleteCorr(self.corr_criterion).fit_transform(dataobject)
        return dataobject


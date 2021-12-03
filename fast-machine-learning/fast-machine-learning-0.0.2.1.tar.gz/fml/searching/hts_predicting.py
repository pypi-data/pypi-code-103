
from ..descriptors import HOIP
from ..utils.base_func import linspace
from itertools import product, combinations
import numpy as np
from ..data import DataObject
import pandas as pd

class HOIPHTSWithVotingRegressor(object):

    def __init__(self, verbose=False):

        self.verbose = verbose
        self.hoip = HOIP()

    def fit_with_full_range(self, votingmodel, formular_info, site_counts=[2, 2, 1], steps=[0.1, 0.1, 0.1], starts=[0, 0, 0], ends=[1, 1, 3]):

        """
        formular_info = [
            ["FA", "MA", ...] # atoms in A site
            ["Pb", "Sn", ...] # atoms in B site
            ["Cl", "Br", "I"] # atoms in C site
        ]
        site_counts = [2, 2, 1]
        """
        columns_set = []
        for trainobj in votingmodel.trainobjects:
            columns_set += trainobj.Xnames.tolist()
        columns_set = list(set(columns_set))
        
        ratio_info = []
        for index, site_count in enumerate(site_counts):
            if index == 2:
                ratio_range = linspace(starts[index], ends[index], steps[index], decimal=5)
            else:
                ratio_range = linspace(starts[index], ends[index], steps[index], decimal=5)
            ratio_ranges = [ ratio_range for i in range(site_count) ]
            ratio_info.append(ratio_ranges)
        formulars = []
        lengths = []
        for formular_info_, ratio_info_, site_count, sum_ in zip(formular_info, ratio_info, site_counts, [1, 1, 3]):
            ratio_product = np.array(list(product(*ratio_info_)))
            ratio_product = ratio_product[ratio_product.sum(axis=1) == sum_].tolist()
            element_combination = list(combinations(formular_info_, site_count))
            site_product = list(product(element_combination, ratio_product))
            formulars.append(site_product)
            lengths.append(len(site_product))
        lengths = lengths[0]*lengths[1]*lengths[2]
        formulars = product(*formulars)
        formular_data = []
        formular_names = []
        formular_details = []
        descriptors = []
        predictions = []
        for index, site_info in enumerate(formulars):
            tmp_formular_list = []
            formular_name = ""
            formular_detail = []
            for site in site_info:
                tmp_site_dict = {}
                for element, ratio in zip(*site):
                    tmp_site_dict[element] = ratio
                    if float(ratio) != 0:
                        formular_name += element
                        if float(ratio) != 1:
                            if ratio in [1, 2, 3]:
                                ratio = int(ratio)
                            formular_name += str(ratio)
                    formular_detail += [element, ratio]
                tmp_formular_list.append(tmp_site_dict)
            formular_names.append(formular_name)
            formular_data.append(tmp_formular_list)
            formular_details.append(formular_detail)
            descriptor = self.hoip.describe_formular(tmp_formular_list, onehot=True)
            descriptor = descriptor.loc[columns_set]
            descriptors.append(descriptor)
            data = DataObject(X=descriptor.values.reshape(1, -1), Y=[0], 
                              Xnames=descriptor.index.values, Yname=votingmodel.trainobjects[0].Yname[0])
            pred = votingmodel.predict(data)[0]
            predictions.append(pred)
            if self.verbose:
                print(f" {index+1}/{lengths} {formular_name}: {round(pred, 3)}")
        
        self.predictions = pd.Series(predictions, index=formular_names, name=votingmodel.trainobjects[0].Yname[0])
        
        columns = []
        for i, j in enumerate(["A", "B", "C"]):
            for k in range(site_counts[i]):
                columns += [f"{j}{k+1}", f"r{j}{k+1}"]
        
        
        formular_details = pd.DataFrame(formular_details, index=formular_names,
                                        columns=columns)
        self.predictions_2 = pd.concat([pd.DataFrame(self.predictions), formular_details], axis=1)
        
        # self.descriptors = pd.concat(descriptors, axis=1).T
        self.descriptors = descriptors
        
        return self



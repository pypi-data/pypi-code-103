
import numpy as np
import math
import copy

class DealMultipleTarget:
    
    def __init__(self, deal="prone_mean", prone_criterion=0.01):
        self.deal = deal
        self.prone_criterion = prone_criterion
    
    def _counters(self, target):

        """
        
        counts
        
        ndarray
    
        index0: number or identification
    
        index1: target
    
        """
        from collections import Counter
        number_counter = Counter(target[:, 0])
        
        index_counter = {}
        
        for key, value in number_counter.items():
            value_indexes = np.where(target[:, 0] == key)[0].tolist()
            
            index_counter[key] = value_indexes
        
        value_counter = {}
        
        for key, indexes in index_counter.items():
            
            values = target[indexes, 1]
            
            values = values.astype("float")
            
            values = values.tolist()
            
            value_counter[key] = values
        
        return index_counter, value_counter
    
    def _get_gap(self, _list):
    
        gap_list = []
        
        for i, j in zip(_list[1:], _list[:-1]):
            
            gap_list.append(float(i) - float(j))
        
        return gap_list
    def _prone_list_target_mean(self, target_list, criterion):
        """
        target_list: list
        """
        
        target_list.sort()
        while np.std(target_list) > criterion and len(target_list) > 2:
            
            gap_list = self._get_gap(target_list)
            
            popindex = gap_list.index(max(gap_list))
            
            if popindex >= math.floor(len(target_list) / 2):
                popindex += 1
            
            target_list.pop(popindex)
        
        
        return np.mean(target_list)
    
    def deal_with_multiple_data(self, target):
        """
        
        transfer
        
        ndarray
    
        index0: number or identification
    
        index1: target
    
        deal: mean, max, min, prone_mean
    
        """
        
        index_counter, value_counter = self._counters(target)
        
        counters = dict(
            index_counter=index_counter,
            value_counter=value_counter
            )
        
        data = []
        
        for key, values in value_counter.items():
            
            if self.deal == "mean":
                value = np.mean(values)
            elif self.deal == "max":
                value = np.max(values)
            elif self.deal == "min":
                value = np.min(values)
            elif self.deal == "prone_mean":
                value = self._prone_list_target_mean(values, self.prone_criterion)
            
            data.append([key, value])
        
        data = np.array(data)
        
        counters.update({
            "raw_counter": self._counters(target)[1]
            })
        
        return data, counters

    def stdforsmallsamples(self, target, sample_number=2, criterion=0.1):
        
        index_counter, value_counter = self._counters(target)
        
        stds = {}
        for i, j in value_counter.items():
            if len(j) <= sample_number:
                if np.std(j) > criterion:
                    stds[i] = j
        return stds

def reg2cls(Y, class_number=2, deal="median"):
    
    try:
        Y = Y.reshape(-1, )
        Y = Y.astype(float)
    except Exception as err:
        return err
    
    try:
        class_number = int(class_number)
    except Exception as err:
        return err
    
    if class_number == 2:
        if deal == "median":
            deal = np.median(Y)
        elif deal == "mean":
            deal = np.mean(Y)
        for i, value in enumerate(Y):
            if value >= deal:
                Y[i] = 1
            else:
                Y[i] = 0
    elif class_number != 2:
        #ignore deal
        #split part
        step = 100 / class_number
        bins = [ [np.percentile(Y, i*step), np.percentile(Y, (i+1)*step)] for i in range(class_number) ]
        for i, value in enumerate(Y):
            for j, _bin in enumerate(bins):
                if _bin[0] <= value <= _bin[1]:
                    Y[i] = j
    return Y
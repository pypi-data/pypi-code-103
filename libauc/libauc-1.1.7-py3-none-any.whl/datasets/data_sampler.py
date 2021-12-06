import numpy as np
from torch.utils.data.sampler import Sampler
import random

class ImbalanceSampler(Sampler):
    

    def __init__(self, labels, batch_size, pos_num=1):
        # positive class: minority class
        # negative class: majority class
        self.labels = labels
        self.posNum = pos_num
        self.batchSize = batch_size

        self.clsLabelList = np.unique(labels)
        self.dataDict = {}

        for label in self.clsLabelList:
            self.dataDict[str(label)] = []

        for i in range(len(self.labels)):
            self.dataDict[str(self.labels[i])].append(i)

        self.ret = []
        
    def __iter__(self):
        minority_data_list = self.dataDict[str(1)]
        majority_data_list = self.dataDict[str(0)]

        # print(len(minority_data_list), len(majority_data_list))
        random.shuffle(minority_data_list)
        random.shuffle(majority_data_list)

        # In every iteration : sample 1(posNum) positive sample(s), and sample batchSize - 1(posNum) negative samples
        if len(minority_data_list) // self.posNum  >= len(majority_data_list)//(self.batchSize - self.posNum): # At this case, we go over the all positive samples in every epoch.
            majority_data_list.extend(np.random.choice(majority_data_list, len(minority_data_list) // self.posNum * (self.batchSize - self.posNum) - len(majority_data_list), replace=True).tolist())

            for i in range(len(minority_data_list) // self.posNum):
                if self.posNum == 1:
                    self.ret.append(minority_data_list[i])
                else:
                    self.ret.extend(minority_data_list[i*self.posNum:(i+1)*self.posNum])

                startIndex = i*(self.batchSize - self.posNum)
                endIndex = (i+1)*(self.batchSize - self.posNum)
                self.ret.extend(majority_data_list[startIndex:endIndex])

        else: # At this case, we go over the all negative samples in every epoch.
            # extend the length of minority_data_list from len(minority_data_list) to len(majority_data_list)//(batchSize-posNum) + 1

            minority_data_list.extend(np.random.choice(minority_data_list, len(majority_data_list) // (self.batchSize - self.posNum) + 1 - len(minority_data_list)//self.posNum, replace=True).tolist())
            for i in range(0, len(majority_data_list), self.batchSize - self.posNum):

                if self.posNum == 1:
                    self.ret.append(minority_data_list[i//(self.batchSize - self.posNum)])
                else:
                    self.ret.extend(minority_data_list[i//(self.batchSize- self.posNum)* self.posNum: (i//(self.batchSize-self.posNum) + 1)*self.posNum])

                self.ret.extend(majority_data_list[i:i + self.batchSize - self.posNum])

        return iter(self.ret)


    def __len__ (self):
        return len(self.ret)
    
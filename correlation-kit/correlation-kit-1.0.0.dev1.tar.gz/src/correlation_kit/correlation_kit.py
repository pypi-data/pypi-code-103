import csv
from scipy.stats import *

class CorrelationKit:

    def __init__(self,df):
        self.df=df

    def get_ds(self,field):
        list=self.df[field].values
        return list

    def get_pearson(self,xlabel, ylabel):
        x=self.get_ds(xlabel)
        y=self.get_ds(ylabel)
        stat, p = pearsonr(x, y)
        '''
        print('pearson stat=%.3f, p=%.3f' % (stat, p))
        if p > 0.05:
            print('Probably independent')
        else:
            print('Probably dependent')
        '''
        return round(stat,4), round(p,4)

    def get_spearman(self,xlabel, ylabel):
        x = self.get_ds(xlabel)
        y = self.get_ds(ylabel)
        stat, p = spearmanr(x, y)
        '''
        print('spearman stat=%.3f, p=%.3f' % (stat, p))
        if p > 0.05:
            print('Probably independent')
        else:
            print('Probably dependent')
        '''
        return round(stat,4), round(p,4)

    def get_kendalltau(self,xlabel, ylabel):
        x = self.get_ds(xlabel)
        y = self.get_ds(ylabel)
        stat, p = kendalltau(x, y)

        '''
        print('stat=%.3f, p=%.3f' % (stat, p))
        if p > 0.05:
            print('Probably independent')
        else:
            print('Probably dependent')
        '''
        return round(stat,4), round(p,4)

    def get_corr_between_category_and_continual(self,c_field, c_field_int, v_field):
        fields = [c_field, v_field]

        df2 = self.df[fields]

        # print(df[fields])

        # Since Categorical variable 'Type' has only 2 values we will convert it into numeric (0 and 1) datatype.

        df2['TypeInt'] = (df2[c_field] == c_field_int).astype(int)

        # print(df2)
        r1 = df2.corr(method="pearson")
        r2 = df2.corr(method="spearman")
        r3 = df2.corr(method="kendall")
        # print(r['TypeInt'][v_field])
        return round(r1['TypeInt'][v_field], 4), round(r2['TypeInt'][v_field], 4), round(r3['TypeInt'][v_field], 4)

    def get_f_oneway(self,c_field, c_field_values, v_field):
        list_args = []
        for c in c_field_values:
            list_args.append(self.df[self.df[c_field] == c][v_field])
        F, p = stats.f_oneway(*list_args)
        return round(F, 4), round(p, 4)



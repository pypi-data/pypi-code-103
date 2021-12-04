from kolibri.core.component import Component
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import MaxAbsScaler
from sklearn.preprocessing import QuantileTransformer
import pandas as pd



class Normalizer(Component):
    defaults = {
        "fixed":{
            "normalization-method": "zscore",
            "random-state-quantile":42,
            "ignore-columns":[],
            "normalize-group": None,
            "table-index": [],
            "columns":[]
        }
    }

    def __init__(self, configs={}):

        super().__init__(configs)
        self.normalizer_funct = self.get_parameter("normalization-method")
        self.random_state_quantile = self.get_parameter("random-state-quantile")


    def fit(self, data, y=None):

        # we only want to apply if there are numeric columns
        self.numeric_features = (
            data.select_dtypes(include=["float32", "int64", "float64", "int32"]).columns
        )
        self.numeric_features=[col for col in self.numeric_features if col not in  [self.target]+self.get_parameter("ignore-columns")]

        if len(self.numeric_features) > 0:
            if self.normalizer_funct == "zscore":
                self.scaler = StandardScaler()
                self.scaler.fit(data[self.numeric_features])
            elif self.normalizer_funct == "minmax":
                self.scaler = MinMaxScaler()
                self.scaler.fit(data[self.numeric_features])
            elif self.normalizer_funct == "quantile":
                self.scaler = QuantileTransformer(
                    random_state=self.random_state_quantile,
                    output_distribution="normal"
                )
                self.scaler.fit(data[self.numeric_features])
            elif self.normalizer_funct == "maxabs":
                self.scaler = MaxAbsScaler()
                self.scaler.fit(data[self.numeric_features])

        return self

    def _normalize_per_group(self, data, group, value):
        index_columns=self.get_parameter("table-index")
        data.groupby(index_columns).size().reset_index().rename(columns={0: 'count'})
        data_pivoted_var_id = pd.DataFrame(pd.pivot_table(data, values=value,
                                                          columns=[group],
                                                          index=self.get_parameter("table-index"),
                                                          aggfunc='sum').to_records())

        data_pivoted_var_id.fillna(0, inplace=True)

        data_pivoted_var_id = data_pivoted_var_id.set_index(
            ['Employee_Id', 'Run_Id']
        ).unstack(
            fill_value=0).stack().sort_index(level=1).reset_index()

        data_pivoted_var_id = data_pivoted_var_id.set_index(
            ['Employee_Id', 'Run_Id'])

        data_pivoted_var_id.head()

    def transform(self, data, y=None):

        if len(self.numeric_features) > 0:
            self.data_t = pd.DataFrame(
                self.scaler.transform(data[self.numeric_features])
            )
            # we need to set the same index as original data
            self.data_t.index = data.index
            self.data_t.columns = self.numeric_features
            for i in self.numeric_features:
                data[i] = self.data_t[i]
            return data

        else:
            return data

    def fit_transform(self, data, y=None):
        self.fit(data)

        return self.transform(data)

from kolibri.registry import ModulesRegistry
ModulesRegistry.add_module(Normalizer.name, Normalizer)
from sklearn.base import TransformerMixin

class FeatureLagger(TransformerMixin):
    '''
        Adds a lagged version of "feature_name", using "keys" to join to the original data
    '''
    def __init__(self, feature_name, date_id="date_block_num", keys=["shop_id", "item_id"],
                 period_lookback = 1,
                 use_last:bool = False,
                 min_items:int = 0,
                 use_test_data:bool=False,
                 fill_test_data_value:float=None,
                 verbose:bool=False # refactor: use a logger
                ):
        self.feature_name = feature_name
        self.date_id = date_id
        self.keys = keys
        self.period_lookback = period_lookback # aka lag
        self.use_last = use_last
        self.use_test_data = use_test_data
        self.fill_test_data_value = fill_test_data_value
        self.train_data = None
        self.lagged_name = f"{self.feature_name}_lag_{period_lookback}"
        self.verbose = verbose
    def fit(self, X, y=None):
        self.train_data = X[[self.date_id, self.feature_name] + self.keys]
        id_max_train = int(self.train_data[self.date_id].max())
        
        self.train_data.loc[:, self.date_id] = self.train_data.loc[:, self.date_id] + self.period_lookback
        self.train_data.rename(columns={self.feature_name: self.lagged_name}, inplace=True)

        return self
    
    def transform(self, X):
        x_len = X.shape[0]
        merge_keys = [self.date_id] + self.keys
        
        if self.verbose:
            print(f"Merge keys: {merge_keys}")
        X = X.merge(self.train_data, on=merge_keys, how="left")
        

        if self.fill_test_data_value is not None:
            X[self.lagged_name] = X[self.lagged_name].fillna(self.fill_test_data_value)
        
        assert x_len == X.shape[0], print(f"initial len: {x_len}, final len: {X.shape[0]}")
        
        return X
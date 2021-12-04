from rainiee_lib.dataframe import pandas_df
from rainiee_lib.constants import data_consts
from rainiee_lib.objects import objects_utils
import pandas as pd
import json
from typing import List

class PortfolioEntries(object):
    def construct(self, symbol : str, weights : float, est_ret : float, ext = {}):
        self.symbol = symbol
        self.weights = round(float(weights), 6)
        self.est_ret = round(float(est_ret), 6)
        self.ext = ext

    def to_json(self):
        return objects_utils.get_fields_json(self, objects_utils.portfolio_defualt_fields)

    def from_json(self, json_input):
        self.construct(json_input['symbol'],json_input['weights'],json_input['est_ret'],json_input['ext'])
    def to_json_str(self):
        return json.dumps(self.to_json())
    def from_json_str(self, json_str):
        self.from_json(json.loads(json_str))

class PortfolioParams(object):
    def construct(self, mean_returns : pd.DataFrame, cov_matrix : pd.DataFrame, ext={}):
        self.mean_returns = mean_returns
        self.cov_matrix = cov_matrix
        self.ext = ext

    def to_json(self):
        return {
            "mean_returns" : pandas_df.json_write_dataframe(self.mean_returns),
            "cov_matrix" : pandas_df.json_write_dataframe(self.cov_matrix),
            "ext" : self.ext
                }
    def from_json(self,json_input):
        self.construct(pandas_df.json_read_dataframe(json_input['mean_returns']),
                       pandas_df.json_read_dataframe(json_input['cov_matrix']),
                       json_input['ext'])
    def to_json_str(self):
        return json.dumps(self.to_json())
    def from_json_str(self, json_str):
        self.from_json(json.loads(json_str))


class Portfolio(object):
    def construct(self,
                  portf_allocation : List[PortfolioEntries],
                  est_portf_return : float,
                  est_portf_var : float,
                  solver_info : dict,
                  portf_param : PortfolioParams,
                  portf_model : str,
                  ext = {}):
        self.portf_allocation = portf_allocation
        self.est_portf_return = round(float(est_portf_return),6)
        self.est_portf_var = round(float(est_portf_var),6)
        self.solver_info = solver_info
        self.portf_param = portf_param
        self.portf_model = portf_model
        self.ext = ext

    def est_portf_sharpe(self):
        return round(self.est_portf_return / self.est_portf_var ,6)

    def get_portf_df(self):
        return pandas_df.get_df_obj_list(self.portf_allocation).sort_values(by=[data_consts.WEIGHTS], ascending=False)

    def get_portf_list(self):
        return list(self.get_portf_df().T.to_dict().values())

    def get_top_k_list(self, k):
        res_df = self.get_portf_df().sort_values(by=[data_consts.WEIGHTS], ascending=False)[:int(k)]
        res_df[data_consts.WEIGHTS] = res_df[data_consts.WEIGHTS] / res_df[data_consts.WEIGHTS].sum()
        res_list = list(res_df.T.to_dict().values())
        return res_list

    def to_json(self):
        return {"portf_allocation": [o.to_json() for o in self.portf_allocation],
                "est_portf_return": self.est_portf_return, "est_portf_var": self.est_portf_var,
                "solver_info": self.solver_info, "portf_param": self.portf_param.to_json(),
                "portf_model":self.portf_model, "ext": self.ext}
    def from_json(self, json_input):
        self.construct(objects_utils.from_json_object_list("PortfolioEntries", json_input['portf_allocation']),
                       json_input['est_portf_return'],
                       json_input['est_portf_var'],
                       json_input['solver_info'],
                       objects_utils.from_json_object("PortfolioParams", json_input['portf_param']),
                       json_input['portf_model'],
                       json_input['ext'])
    def to_json_str(self):
        return json.dumps(self.to_json())
    def from_json_str(self, json_str):
        self.from_json(json.loads(json_str))



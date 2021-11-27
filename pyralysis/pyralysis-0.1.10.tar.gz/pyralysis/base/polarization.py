import logging
import xarray as xr

pol_dict = {
    0: None,
    1: "I_s",
    2: "Q_s",
    3: "U_s",
    4: "V_s",
    5: "RR",
    6: "RL",
    7: "LR",
    8: "LL",
    9: "XX",
    10: "XY",
    11: "YX",
    12: "YY",
    13: "RX",
    14: "RY",
    15: "LX",
    16: "LY",
    17: "XR",
    18: "XL",
    19: "YR",
    20: "YL",
    21: "PP",
    22: "PQ",
    23: "QP",
    24: "QQ",
    25: "RCircular",
    26: "LCircular",
    27: "Linear",
    28: "Ptotal",
    29: "Plinear",
    30: "PFtotal",
    31: "PFlinear",
    32: "Pangle"
}


class Polarization:
    def __init__(self, _id: int = None, dataset: xr.Dataset = None):
        """
        Class that represents the polarization table of the partitioned Measurement Set

        Parameters
        ----------
        _id : int
              ID of the object
        dataset : xarray.Dataset
                  xarray Dataset with the polarization table
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        self._id = _id
        self.dataset = dataset

        self.corrs = []
        self.ncorrs = 0
        self.feed_kind = None
        if dataset is not None and _id is not None:
            self.corrs = dataset.CORR_TYPE.data.squeeze().compute()
            corr_string_list = [pol_dict[corr] for corr in self.corrs] # TODO: self.corr_names can be a string list -
            # no need to be a dictionary
            self.corrs_names = {i: corr_string_list[i] for i in range(0, len(corr_string_list))}
            linear_feed = ["XX", "XY", "YX", "YY"]
            if any(i in linear_feed for i in [*self.corrs_names.values()]):
                self.feed_kind = "linear"
            else:
                self.feed_kind = "circular"
            self.ncorrs = dataset.NUM_CORR.data.squeeze().compute()

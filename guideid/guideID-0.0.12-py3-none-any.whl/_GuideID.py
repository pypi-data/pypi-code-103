
# _GuideID.py

__module_name__ = "_GuideID.py"
__author__ = ", ".join(["Michael E. Vinyard"])
__email__ = ", ".join(["vinyard@g.harvard.edu",])


# local imports #
# ------------- #
from ._supporting_functions._return_guides_in_regions import _return_guides_in_regions


class _GuideID:
    
    def __init__(self, df):
        
        """"""
        
        self.df = df
        
        
    def scan(self,
             sequence,
             region_column,
             region_specification,
             df=False,
             PAM="NGG",
             region_extension=0,
             return_guides=False,
            ):
        
        """
        Parameters:
        -----------
        df


        sequence


        region_column


        region_specification


        Returns:
        --------

        Notes:
        ------
        df.loc[df[region_column] == region_specification]
        """
        
        if df:
            self.df = df
        
        self.guide_df = _return_guides_in_regions(sequence,
                                                  self.df,
                                                  region_column,
                                                  region_specification,
                                                  PAM,
                                                  region_extension,
                                                 ):

        if return_guides:
            return self.guide_df
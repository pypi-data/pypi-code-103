from hdsr_wis_config_reader.idmappings.columns import IdMapColumnChoices
from typing import List

import logging
import pandas as pd  # noqa pandas comes with geopandas


logger = logging.getLogger(__name__)


class IdMappingDataframe(pd.DataFrame):
    """A dataframe class for IdMappings with some custom filter methods"""

    @property
    def _constructor(self):
        """Pandas routinely returns new dataframes when performing operations on dataframes.
        So to preserve this dataframe class, we need to have pandas return this class when performing operations
        on an instance of this class."""
        return IdMappingDataframe

    @classmethod
    def __get_query(cls, **kwargs) -> str:
        dynamic_query = " & ".join([f"{key}=='{value}'" for key, value in kwargs.items() if value])
        return dynamic_query

    def get_filtered_df(
        self, ex_loc: str = None, ex_par: str = None, int_loc: str = None, int_par: str = None,
    ) -> pd.DataFrame:
        """Filter dataframe rows based on ex_loc, ex_par, int_loc, int_par."""
        dynamic_query = self.__get_query(
            **{
                IdMapColumnChoices.ex_loc.value: ex_loc,
                IdMapColumnChoices.ex_par.value: ex_par,
                IdMapColumnChoices.int_loc.value: int_loc,
                IdMapColumnChoices.int_par.value: int_par,
            }
        )
        if not dynamic_query:
            logger.warning("empty dynamic query returns unfiltered idmap dataframe")
            return self
        filter_df = self.query(expr=dynamic_query, inplace=False)
        return filter_df

    def get_filtered_column_values(
        self,
        make_result_unique: bool,
        target_column: IdMapColumnChoices,
        ex_loc: str = None,
        ex_par: str = None,
        int_loc: str = None,
        int_par: str = None,
    ) -> List[str]:
        assert isinstance(target_column, IdMapColumnChoices)
        filtered_df = self.get_filtered_df(ex_loc=ex_loc, ex_par=ex_par, int_loc=int_loc, int_par=int_par)
        assert target_column.value in filtered_df.columns
        if filtered_df.empty:
            return []
        column_values = filtered_df[target_column.value].to_list()
        column_values = list(set(column_values)) if make_result_unique else column_values
        return sorted(column_values)

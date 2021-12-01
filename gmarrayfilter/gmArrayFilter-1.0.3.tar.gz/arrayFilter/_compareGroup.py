import pandas as pd
from typing import Dict, List, Mapping, Optional
from functools import partial
from collections import Counter

from ._var import HybridStrategy
from ._allele import equalNA
from ._allele import isHybrid
from ._allele import uniAllele
from ._allele import twiAllele
from ._allele import naAlleleTransform
from ._utils import remove_web_name_prefix


def group2dict(
    group_name: str, group_samples: Optional[List[str]], web: bool = False
) -> Dict[str, str]:
    if group_samples:
        if web:
            group_samples = remove_web_name_prefix(group_samples)
        return {sample_i: group_name for sample_i in group_samples}
    return {}


def group_allele(
    allele_series: pd.Series, max_na: float = 0, keep_na: bool = False
) -> Optional[str]:
    allele_list = [naAlleleTransform(allele) for allele in allele_series.values]
    allele_count_num = len(set(allele_list))
    if allele_count_num == 1:
        return uniAllele(allele_list, keep_na=keep_na)
    elif allele_count_num > 2:
        return None
    else:
        allele_count = Counter(allele_list)
        return twiAllele(allele_count, max_na, keep_na)


def group_sample_allele_df(
    array_df: pd.DataFrame,
    grp_dict: Dict[str, str],
    max_na: float,
    keep_na: bool = False,
) -> pd.DataFrame:
    group_df = array_df[list(grp_dict.keys())].copy()
    group_df.rename(columns=grp_dict, inplace=True)  # type: ignore
    melt_df = group_df.melt(
        var_name="group_name", value_name="allele", ignore_index=False
    )
    grp_allele_func = partial(group_allele, max_na=max_na, keep_na=keep_na)

    grp_allele = melt_df.groupby(["probe_id", "group_name"]).allele.apply(
        grp_allele_func
    )

    grp_allele_df = grp_allele.unstack(level=1)
    grp_allele_df.columns.name = ""
    return grp_allele_df.copy()


def consist_with_parent(
    df: pd.DataFrame, child_col: str, parent_col: str
) -> pd.DataFrame:
    if child_col in df.columns and parent_col in df.columns:
        pa_is_na = df[parent_col].map(equalNA)
        child_eq_pa = df[child_col] == df[parent_col]
        return df[pa_is_na | child_eq_pa]  # type: ignore
    return df.copy()


def ne_other(df: pd.DataFrame, mut_col: str, wild_col: str) -> pd.DataFrame:
    if mut_col in df.columns and wild_col in df.columns:
        mut_is_na = df[mut_col].map(equalNA)
        wild_is_na = df[wild_col].map(equalNA)
        ne_mask = df[mut_col] != df[wild_col]
        return df[mut_is_na | wild_is_na | ne_mask]
    return df


def filter_by_gt(df: pd.DataFrame, col_name: str, gt: str) -> pd.DataFrame:
    if gt == HybridStrategy.both:
        return df
    elif col_name in df.columns:
        print(df)
        mask1 = df[col_name].map(equalNA)
        mask2 = df[col_name].map(isHybrid)
        if gt == HybridStrategy.het:
            return df[mask1 | mask2]
        else:
            return df[~mask2]  # type: ignore
    else:
        return df

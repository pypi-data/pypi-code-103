import typer
import delegator
import pandas as pd
from typing import Iterable, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from dataclasses import asdict
from functools import reduce

from ._allele import isHybrid
from ._allele import isATGCorNA
from ._compareGroup import group2dict
from ._compareGroup import group_sample_allele_df
from ._compareGroup import consist_with_parent
from ._compareGroup import ne_other
from ._compareGroup import filter_by_gt


from ._utils import var_density_stats
from ._utils import var_density_file_suffix
from ._utils import remove_web_name_prefix
from ._utils import params_cfg
from ._utils import merge_array_anno_dfs

from ._var import SnpDensityStatsTable
from ._var import FILE_SEP_MAP
from ._var import DENSITY_PLOT_R
from ._var import EchoPrefix
from ._var import LABEL_NAMES
from ._var import GT_COL
from ._var import LOCATION_COL
from ._var import ID_NAME
from ._var import DataType
from ._var import HybridStrategy

from ._exception import ArrayFormatError
from ._exception import ArrayInputError
from ._exception import ArrayNotFound


@dataclass
class ArrayFilerParams:
    mutant: List[str]
    wild: List[str]
    mutant_parent: Optional[List[str]]
    wild_parent: Optional[List[str]]
    child_max_na: float
    parent_max_na: float
    mutant_name: str
    wild_name: str
    mutant_pa_name: str
    wild_pa_name: str
    mutant_gt: str
    wild_gt: str
    mutant_parent_gt: str
    wild_parent_gt: str
    array: str
    genomes: List[str]
    density_window: int
    density_step: int
    strict: bool
    web: bool


class ArrayFilter:
    def __init__(
        self,
        array_df: pd.DataFrame,
        array_annotation_dir: Path,
        params: ArrayFilerParams,
    ) -> None:
        self.array_df = array_df
        self.array_annotation_dir = array_annotation_dir
        self.mutant = params.mutant
        self.wild = params.wild
        self.mutant_parent = params.mutant_parent
        self.wild_parent = params.wild_parent
        self.child_max_na = params.child_max_na
        self.parent_max_na = params.parent_max_na
        self.mutant_name = params.mutant_name
        self.wild_name = params.wild_name
        self.mutant_pa_name = params.mutant_pa_name
        self.wild_pa_name = params.wild_pa_name
        self.array = params.array
        self.genomes = params.genomes
        self.web = params.web
        self.mutant_gt = params.mutant_gt
        self.wild_gt = params.wild_gt
        self.mutant_parent_gt = params.mutant_parent_gt
        self.wild_parent_gt = params.wild_parent_gt
        self.strict = params.strict
        self.filter_df = pd.DataFrame([])

    @property
    def keep_na(self):
        return not self.strict

    @property
    def child_grp_dict(self):
        child_grp_dict = group2dict(self.mutant_name, self.mutant, web=self.web)
        child_grp_dict.update(group2dict(self.wild_name, self.wild, web=self.web))
        return child_grp_dict

    @property
    def parent_grp_dict(self):
        parent_grp_dict = group2dict(
            self.mutant_pa_name, self.mutant_parent, web=self.web
        )
        parent_grp_dict.update(
            group2dict(self.wild_pa_name, self.wild_parent, web=self.web)
        )
        return parent_grp_dict

    @property
    def child_allele_df(
        self,
    ) -> pd.DataFrame:
        return group_sample_allele_df(
            self.array_df, self.child_grp_dict, self.child_max_na
        )

    @property
    def parent_allele_df(self) -> pd.DataFrame:
        return group_sample_allele_df(
            self.array_df,
            self.parent_grp_dict,
            self.parent_max_na,
            keep_na=self.keep_na,
        )

    @property
    def array_ann_df(self) -> pd.DataFrame:
        array_ann_files = [
            self.array_annotation_dir / f"{genome}_{self.array}.annotation.csv.gz"
            for genome in self.genomes
        ]
        array_ann_df_list = [
            pd.read_csv(array_ann_file, comment="#", index_col=0)
            for array_ann_file in array_ann_files
        ]
        return merge_array_anno_dfs(array_ann_df_list, self.genomes)

    def filter_homo(self, df: pd.DataFrame) -> pd.DataFrame:
        homo_df = df[df[GT_COL] == DataType.homo].copy()
        filter_by_mut = consist_with_parent(
            homo_df, self.mutant_name, self.mutant_pa_name
        )
        filter_by_wild = consist_with_parent(
            filter_by_mut, self.wild_name, self.wild_pa_name
        )
        return filter_by_wild

    def filter_mut_het(self, df: pd.DataFrame) -> pd.DataFrame:
        mut_het_df = df[df[GT_COL] == DataType.mut_het].copy()
        wild_eq_pa = consist_with_parent(mut_het_df, self.wild_name, self.wild_pa_name)
        pa_ne_df = ne_other(wild_eq_pa, self.mutant_pa_name, self.wild_pa_name)
        return pa_ne_df

    def filter_wild_het(self, df: pd.DataFrame) -> pd.DataFrame:
        wild_het_df = df[df[GT_COL] == DataType.wild_het].copy()
        mut_eq_pa = consist_with_parent(
            wild_het_df, self.mutant_name, self.mutant_pa_name
        )
        pa_ne_df = ne_other(mut_eq_pa, self.mutant_pa_name, self.wild_pa_name)
        return pa_ne_df

    def filter_mutant_ne_wild(self) -> None:
        rm_na_df = self.child_allele_df.dropna()
        mask = rm_na_df[self.mutant_name] != rm_na_df[self.wild_name]
        self.filter_df = rm_na_df[mask].copy()

    def add_parent(self) -> None:
        if self.parent_grp_dict:
            self.filter_df = self.filter_df.merge(
                self.parent_allele_df, left_index=True, right_index=True
            )
            self.filter_df.dropna(inplace=True)

    def add_genoType(self):
        self.add_parent()
        if self.filter_df.empty:
            return False
        self.filter_df.loc[:, GT_COL] = DataType.homo  # type: ignore
        mut_het_mask = [isHybrid(allele) for allele in self.filter_df[self.mutant_name]]
        self.filter_df.loc[mut_het_mask, GT_COL] = DataType.mut_het  # type: ignore
        wild_het_mask = [isHybrid(allele) for allele in self.filter_df[self.wild_name]]
        self.filter_df.loc[wild_het_mask, GT_COL] = DataType.wild_het  # type: ignore
        return True

    def filter_by_genoType(self):
        if self.add_genoType():
            filter_pa_df_list = []
            if (self.mutant_gt in HybridStrategy.homo_like) & (
                self.wild_gt in HybridStrategy.homo_like
            ):
                filter_pa_df_list.append(self.filter_homo(self.filter_df))
            if self.mutant_gt in HybridStrategy.het_like:
                filter_pa_df_list.append(self.filter_mut_het(self.filter_df))
            if self.wild_gt in HybridStrategy.het_like:
                filter_pa_df_list.append(self.filter_wild_het(self.filter_df))
            filter_pa_df = pd.DataFrame(pd.concat(filter_pa_df_list))  # type: ignore
            filter_mut_pa_gt_df = filter_by_gt(
                filter_pa_df, self.mutant_pa_name, self.mutant_parent_gt
            )
            filter_wild_pa_gt_df = filter_by_gt(
                filter_mut_pa_gt_df, self.wild_pa_name, self.wild_parent_gt
            )
            self.filter_df = filter_wild_pa_gt_df.copy()

    def add_annotation(self) -> None:
        self.filter_df = self.filter_df.merge(
            self.array_ann_df, left_index=True, right_index=True, how="left"
        )
        self.filter_df.index.name = ID_NAME
        # self.filter_df.sort_values(LOCATION_COL, inplace=True)

    def filter_pipe(self) -> None:
        self.filter_mutant_ne_wild()
        self.filter_by_genoType()
        self.add_annotation()


def loadArrayFromFile(array_file: str) -> pd.DataFrame:
    array_file_path = Path(array_file)
    array_file_sep = FILE_SEP_MAP.get(array_file_path.suffix)
    if not array_file_sep:
        typer.secho(
            f"{EchoPrefix.error}: Wrong file format, [txt, csv] is supported.",
            fg=typer.colors.RED,
        )
        raise ArrayFormatError()
    return pd.read_csv(
        array_file_path, sep=array_file_sep, index_col=0, na_filter=False
    )


def loadArrayFromDir(sample_list: Iterable[str], array_dir: List[str]) -> pd.DataFrame:
    df_list = []
    array_paths = [Path(array_path) for array_path in array_dir]
    for sample_i in sample_list:
        sample_paths = [array_path / f"{sample_i}.csv.gz" for array_path in array_paths]
        path_filter = filter(lambda sample_path: sample_path.is_file(), sample_paths)
        sample_i_path = next(path_filter, None)
        if sample_i_path is None:
            typer.secho(
                f"{EchoPrefix.error}: File for Sample [{sample_i}] not found.",
                fg=typer.colors.RED,
            )
            raise ArrayNotFound()
        else:
            df_list.append(pd.read_csv(sample_i_path, index_col=0, na_filter=False))
    return reduce(
        lambda x, y: pd.merge(x, y, left_index=True, right_index=True),
        df_list,
    )


def loadArray(
    array_file: Optional[str], array_dir: Optional[List[str]], sample_iter: Iterable
) -> pd.DataFrame:
    if array_file:
        array_df = loadArrayFromFile(array_file)
    elif array_dir:
        array_df = loadArrayFromDir(sample_iter, array_dir)
    else:
        typer.secho(
            f"{EchoPrefix.error}: At least one of --array_file/--array_dir is required.",
            fg=typer.colors.RED,
        )
        raise ArrayInputError()
    array_df.index.name = "probe_id"
    return array_df


def filter_array(
    array_df: pd.DataFrame,
    arrayParams: ArrayFilerParams,
    out_dir: Path,
    array_annotation_dir: Path,
) -> Tuple[pd.DataFrame, Path]:
    array_filter_obj = ArrayFilter(
        array_df=array_df, params=arrayParams, array_annotation_dir=array_annotation_dir
    )
    array_filter_obj.filter_pipe()
    out_dir.mkdir(parents=True, exist_ok=True)
    array_filter_file = out_dir / "array.filter.csv"
    array_filter_obj.filter_df.to_csv(array_filter_file)
    return array_filter_obj.filter_df, array_filter_file


def array_density(
    array_df: pd.DataFrame,
    array_file: Path,
    density_window: int,
    density_step: int,
    genomes: List[str],
    genome_dir: Path,
) -> None:
    filter_density_file = array_file.with_suffix(".density.csv")
    if len(genomes) == 1:
        genome = genomes[0]
        filter_density_df = var_density_stats(
            chr_size_file=genome_dir / genome / "chr.size",
            array_df=array_df,
            window=density_window,
            step=density_step,
        )
    else:
        filter_density_dfs = [
            var_density_stats(
                chr_size_file=genome_dir / genome / "chr.size",
                array_df=array_df,
                window=density_window,
                step=density_step,
                genome=genome,
            )
            for genome in genomes
        ]
        filter_density_df = reduce(
            lambda x, y: pd.merge(
                x,
                y,
                on=[
                    SnpDensityStatsTable.CHROM,
                    SnpDensityStatsTable.START,
                    SnpDensityStatsTable.END,
                ],
                how="outer",
            ),
            filter_density_dfs,
        )
        # filter_density_df.fillna(0, inplace=True)
        filter_density_df.sort_values(
            [SnpDensityStatsTable.CHROM, SnpDensityStatsTable.START], inplace=True
        )
    filter_density_df.to_csv(filter_density_file, index=False, na_rep="NA")

    filter_density_plot = array_file.with_suffix(".plot")
    var_filter_density_suffix = var_density_file_suffix(density_window, density_step)
    plot_cmd = (
        f"Rscript {DENSITY_PLOT_R} -i {filter_density_file} "
        f"--output {filter_density_plot} --title {var_filter_density_suffix}"
    )
    delegator.run(plot_cmd)


def write_params(arrayParams: ArrayFilerParams, out_dir: Path) -> None:
    params_cfg_file = out_dir / "parameters.txt"
    out_params = {**asdict(arrayParams)}
    for label in LABEL_NAMES:
        out_params[label] = ", ".join(remove_web_name_prefix(out_params[label]))
    params_cfg(
        params_cfg_file,
        out_params,
    )


def pack_result(result_dir: Path) -> None:
    zip_cmd = f"cd {result_dir.parent}; zip -r Array-filter.zip {result_dir.name}"
    delegator.run(zip_cmd)


def split_array_by_sample(
    array_file: Path, split_dir: Path, prefix: Optional[str] = None
) -> List[str]:
    split_dir.mkdir(exist_ok=True, parents=True)
    array_file_sep = FILE_SEP_MAP.get(array_file.suffix)
    if not array_file_sep:
        typer.secho(
            f"{EchoPrefix.error}: Wrong file format, [txt, csv] is supported.",
            fg=typer.colors.RED,
        )
        raise ArrayFormatError()
    array_df = pd.read_csv(array_file, sep=array_file_sep, index_col=0, na_filter=False)
    test_array_df = array_df.applymap(isATGCorNA)
    sample_list = []
    for col_i in array_df:
        if all(test_array_df[col_i]):
            out_name = f"{col_i}.csv.gz"
            if prefix:
                out_name = f"{prefix}-{col_i}.csv.gz"
            sample_list.append(col_i)
            out_path = split_dir / out_name
            array_df[col_i].to_csv(out_path, compression="gzip")
    return sample_list
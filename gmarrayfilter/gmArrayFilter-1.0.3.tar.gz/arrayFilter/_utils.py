import typer
import jinja2
import pandas as pd


from pathlib import Path
from typing import Iterable, List, Optional, Tuple
from itertools import chain
from functools import reduce

from ._var import SCRIPT_DIR
from ._var import LOCATION_COL
from ._var import KEEP_COLS
from ._var import MERGE_COLS
from ._var import SnpDensityStatsTable
from ._var import EchoPrefix
from ._exception import ArrayNotFound


def remove_web_name_prefix(name_list: List[str]) -> List[str]:
    return [
        "-".join(each.split("-")[1:]) if ("-" in each) else each for each in name_list
    ]


def params_cfg(cfg_file: Path, cfg_value: dict) -> None:
    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(searchpath=f"{SCRIPT_DIR}")
    )
    template_name = "params.cfg"
    cfg_temp = jinja_env.get_template(template_name)
    cfg_obj = cfg_temp.render(cfg_value)
    with open(str(cfg_file), "w") as file_inf:
        file_inf.write(cfg_obj)


def window_number_format(number):
    megabase = 1000 * 1000
    kilobase = 1000
    if number >= megabase:
        return f"{number / megabase}M"
    elif number >= kilobase:
        return f"{int(number / kilobase)}K"
    else:
        return str(number)


def chrom_bin_snp_number_df(
    start: int, window: int, chr_len: int, chrom: str, df: pd.DataFrame, genome=""
) -> pd.DataFrame:
    cut_range = range(start, chr_len + window, window)
    position_col = LOCATION_COL[1]
    if genome:
        position_col = f"{genome}-{position_col}"
    range_count_df = pd.DataFrame(
        pd.cut(df[position_col].astype("int"), cut_range).value_counts().sort_index()
    )
    count_col = SnpDensityStatsTable.COUNT
    if genome:
        count_col = genome
    range_count_df.columns = [count_col]
    range_count_df.loc[:, SnpDensityStatsTable.CHROM] = chrom  # type: ignore
    range_count_df.loc[:, SnpDensityStatsTable.START] = [  # type: ignore
        each.left for each in range_count_df.index
    ]
    range_count_df.loc[:, SnpDensityStatsTable.END] = [  # type: ignore
        each.right for each in range_count_df.index
    ]
    out_df = range_count_df[
        [
            SnpDensityStatsTable.CHROM,
            SnpDensityStatsTable.START,
            SnpDensityStatsTable.END,
            count_col,
        ]
    ].reset_index(drop=True)
    out_df.loc[:, SnpDensityStatsTable.CHROM] = [each.replace("chr", "") for each in out_df[SnpDensityStatsTable.CHROM]]  # type: ignore
    return out_df


def var_density_stats(
    chr_size_file: Path,
    array_df: pd.DataFrame,
    window: int = 1000 * 1000,
    step: Optional[int] = None,
    genome: str = "",
) -> pd.DataFrame:
    chr_size_df = pd.read_csv(chr_size_file, sep="\t", index_col=0, names=["chr_len"])
    stats_df_list = []
    for chrom in chr_size_df.index:
        chr_len = int(chr_size_df.loc[chrom, "chr_len"])
        chrom_col = LOCATION_COL[0]
        if genome:
            chrom_col = f"{genome}-{chrom_col}"
        chrom_df = array_df[array_df[chrom_col] == chrom].copy()
        if step is None:
            step = window
        for start in range(0, window, step):
            stats_df_i = chrom_bin_snp_number_df(
                start=start,
                chr_len=chr_len,
                window=window,
                chrom=str(chrom),
                df=chrom_df,  # type: ignore
                genome=genome,
            )
            stats_df_list.append(stats_df_i)
    return pd.concat(stats_df_list)  # type: ignore


def var_density_file_suffix(window: int, step: Optional[int]):
    window_str = window_number_format(window)
    if step:
        step_str = window_number_format(step)
        return f"Window_{window_str}-Step_{step_str}"
    else:
        return f"Window_{window_str}"


def flatten_sample(*sampleSource) -> Iterable:
    return chain(*[samples for samples in sampleSource if samples])


def prefix2file(originalPrefix) -> Path:
    extensions = [".csv", ".csv.gz"]
    for ext in extensions:
        oriFile = Path(f"{originalPrefix}{ext}")
        if oriFile.is_file():
            return oriFile
    typer.secho(
        f"{EchoPrefix.error}: Can not find csv file with prefix {originalPrefix}."
    )
    raise ArrayNotFound()


def merge_array_anno_dfs(dfs: List[pd.DataFrame], genomes: List[str]) -> pd.DataFrame:
    if len(dfs) == 1:
        return dfs[0]
    new_dfs = []
    for i, df in enumerate(dfs):
        df = df[KEEP_COLS[1:]].copy()

        genome = genomes[i]
        new_dfs.append(
            df.rename(
                columns={
                    LOCATION_COL[0]: f"{genome}-{LOCATION_COL[0]}",
                    LOCATION_COL[1]: f"{genome}-{LOCATION_COL[1]}",
                }
            )
        )
    return reduce(lambda x, y: pd.merge(x, y, on=MERGE_COLS), new_dfs)

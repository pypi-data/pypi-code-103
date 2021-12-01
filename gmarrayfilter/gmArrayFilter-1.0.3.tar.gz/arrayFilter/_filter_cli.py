import json
import typer

from typing import List
from typing import Optional
from pathlib import Path


from ._var import HybridStrategy
from ._utils import flatten_sample
from ._core import ArrayFilerParams
from ._core import loadArray
from ._core import array_density
from ._core import filter_array
from ._core import write_params
from ._core import pack_result
from ._core import split_array_by_sample

array_filter_app = typer.Typer()


def array_filter(
    out_dir: Path,
    mutant: List[str],
    wild: List[str],
    array_annotation_dir: Path,
    genome_dir: Path,
    array_dir: Optional[List[str]] = typer.Option(None),
    array_file: Optional[str] = "",
    web: bool = False,
    mutant_parent: Optional[List[str]] = [],
    wild_parent: Optional[List[str]] = [],
    child_max_na: float = 0,
    parent_max_na: float = 1,
    mutant_name: str = "mutant",
    wild_name: str = "wild",
    mutant_pa_name: str = "mutant_parent",
    wild_pa_name: str = "wild_parent",
    mutant_gt: str = HybridStrategy.homo,
    wild_gt: str = HybridStrategy.homo,
    mutant_parent_gt: str = HybridStrategy.homo,
    wild_parent_gt: str = HybridStrategy.homo,
    array: str = "660K",
    genomes: List[str] = ["CSv1.0"],
    density_window: int = 1000_000,
    density_step: int = 500_000,
    strict: bool = False,
) -> None:
    sample_iter = flatten_sample(mutant, wild, mutant_parent, wild_parent)
    array_df = loadArray(array_file, array_dir, sample_iter)

    arrayParams = ArrayFilerParams(
        web=web,
        mutant=mutant,
        wild=wild,
        mutant_parent=mutant_parent,
        wild_parent=wild_parent,
        child_max_na=child_max_na,
        parent_max_na=parent_max_na,
        mutant_name=mutant_name,
        wild_name=wild_name,
        mutant_pa_name=mutant_pa_name,
        wild_pa_name=wild_pa_name,
        mutant_gt=mutant_gt,
        wild_gt=wild_gt,
        mutant_parent_gt=mutant_parent_gt,
        wild_parent_gt=wild_parent_gt,
        array=array,
        genomes=genomes,
        strict=strict,
        density_window=density_window,
        density_step=density_step,
    )

    result_dir = out_dir / "array-filter-results"

    array_filter_df, array_filter_file = filter_array(
        array_df, arrayParams, result_dir, array_annotation_dir
    )
    array_density(
        array_filter_df,
        array_filter_file,
        density_window,
        density_step,
        genomes,
        genome_dir,
    )
    write_params(arrayParams, result_dir)
    pack_result(result_dir)


@array_filter_app.command()
def array_filer_web(
    out_dir: Path = typer.Option(...),
    array_dir: List[str] = typer.Option(...),
    array_annotation_dir: Path = typer.Option(...),
    genome_dir: Path = typer.Option(...),
    options: str = typer.Option(...),
    prefix: bool = typer.Option(
        True, help="array file with prefix or not, default is true."
    ),
) -> None:
    optionsObj = json.loads(options)
    return array_filter(
        out_dir=out_dir,
        array_dir=array_dir,
        array_annotation_dir=array_annotation_dir,
        genome_dir=genome_dir,
        web=prefix,
        **optionsObj,
    )


@array_filter_app.command()
def array_split(
    array_file: Path,
    split_dir: Path,
    prefix: Optional[str] = None,
) -> None:
    sample_list = split_array_by_sample(array_file, split_dir, prefix)
    print(json.dumps(sample_list))
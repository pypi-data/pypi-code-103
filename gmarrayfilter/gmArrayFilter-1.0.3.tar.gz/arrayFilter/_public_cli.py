import typer
import pandas as pd

from pathlib import Path
from functools import reduce

from ._utils import prefix2file
from ._exception import ArrayNotFound

array_public_app = typer.Typer()


@array_public_app.command()
def public_array(original_prefix: str, out_prefix: Path) -> None:
    outPath = Path(f"{out_prefix}.csv.gz")
    if not outPath.is_file():
        gmId = out_prefix.name
        originalFile = prefix2file(original_prefix)
        df = pd.read_csv(originalFile, index_col=0)
        df.columns = [gmId]
        df.to_csv(outPath, compression="gzip")


@array_public_app.command()
def merge_array(pub_dir: Path, gm_ids: str, out_file: Path) -> None:
    df_list = []
    for gmId in gm_ids.split(","):
        pubFile_i = pub_dir / f"{gmId}.csv.gz"
        if not pubFile_i.is_file():
            typer.secho("Array File not Found: {pubFile_i}", fg=typer.colors.RED)
            raise ArrayNotFound
        df_list.append(pd.read_csv(pubFile_i, index_col=0))
    merge_df = reduce(
        lambda x, y: pd.merge(x, y, left_index=True, right_index=True), df_list
    )
    merge_df.to_csv(out_file, compression="gzip")
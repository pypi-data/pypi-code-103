import logging
from typing import List

from curvenote.latex.utils.index import LocalMarker
from curvenote.latex.utils.links import version_id_to_local_path, version_id_to_oxa_path

from ...client import Session
from ...models import BlockFormat, BlockVersion
from .get_fast_hash import get_fast_hash
from .get_image_block import get_image_block

VERSION_ID = "___VERSION_ID___"
CAPTION = "___CAPTION___"
LABEL = "___LABEL___"
IMAGE_LATEX_SNIPPET = rf"""\begin{{figure}}[ht]
  \centering
  \includegraphics[width=1.0\linewidth]{{{VERSION_ID}}}
  \caption{{{CAPTION}}}
  \label{{{LABEL}}}
\end{{figure}}
"""


def localize_image_from_top_level_block(
    session: Session,
    assets_folder: str,
    figure_list: List[LocalMarker],
    version: BlockVersion,
):
    """
    - get the image block
    - download the image to the assets_folder using teh local_path as name
    - build the LaTeX content snippet and return it
    """
    try:
        oxa_path = version_id_to_oxa_path(version.id)
        local_path = version_id_to_local_path(version.id)

        image_block, local_path_with_extension = get_image_block(
            session, assets_folder, oxa_path, local_path, BlockFormat.tex
        )

        figure = LocalMarker(
            marker=get_fast_hash(),
            local_path=local_path,
            remote_path=oxa_path,
            content="",
        )
        figure_list.append(figure)

        content = (
            IMAGE_LATEX_SNIPPET.replace(VERSION_ID, local_path_with_extension)
            .replace(CAPTION, image_block.caption)
            .replace(LABEL, figure.marker)
        )

        return f"\n\n{content}\n"
    except ValueError as err:
        logging.error(
            "Caught error trying to localize top level image %s, skipping",
            str(version.id),
        )
        logging.error(err)

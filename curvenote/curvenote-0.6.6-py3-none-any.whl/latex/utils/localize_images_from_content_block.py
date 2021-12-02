from typing import List

from curvenote.latex.utils.get_fast_hash import get_fast_hash
from curvenote.models import BlockFormat

from ...client import Session
from .get_image_block import get_image_block
from .index import LocalMarker
from .patch_local_images_from_tex_block import patch_local_images_from_tex_block
from .regex import INLINE_IMAGE_BLOCK_REGEX, INLINE_IMAGE_OXA_REGEX


def localize_images_from_content_block(
    session: Session, assets_folder: str, figure_list: List[LocalMarker], content: str
):
    """Process image blocks and their respective referencing data including:
    - captions
    - labels
    """
    patch = patch_local_images_from_tex_block(
        [INLINE_IMAGE_BLOCK_REGEX, INLINE_IMAGE_OXA_REGEX], content
    )
    content_with_extensions = patch.content

    for remote_path, local_path in zip(patch.remote_paths, patch.local_paths):
        # get block
        image_block, local_path_with_extension = get_image_block(
            session, assets_folder, remote_path, local_path, BlockFormat.tex
        )

        # now patch the image captions which will be marked have placeholders like
        # f"{local_path}.caption"
        content_with_extensions = content_with_extensions.replace(
            f"{local_path}.caption", image_block.caption
        )

        # now patch the image labels which will have local_path based placeholders
        # like r"\label{local_path}" with a unique local marker
        figure = LocalMarker(
            marker=get_fast_hash(),
            local_path=local_path,
            remote_path=remote_path,
            content="",
        )
        figure_list.append(figure)

        content_with_extensions = content_with_extensions.replace(
            f"\\label{{{figure.local_path}}}", f"\\label{{{figure.marker}}}"
        )

        # patch the remaining image block references
        content_with_extensions = content_with_extensions.replace(
            local_path, local_path_with_extension
        )

    return content_with_extensions
